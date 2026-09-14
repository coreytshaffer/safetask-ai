"""Read-only publication gate over the Git index, including nested ZIP bytes.

No archive extraction, code execution, network access, or history scan. Unknown
archive formats fail closed for explicit review instead of being silently skipped.
"""
import argparse
from dataclasses import dataclass
import io
from pathlib import Path
import re
import stat
import subprocess
import zipfile
import zlib


MAX_INDEX_BYTES = 128_000_000
MAX_EXPANDED_BYTES = 50_000_000
MAX_MEMBERS = 10_000
MAX_DEPTH = 5
ZIP_SUFFIXES = (".zip", ".whl", ".jar", ".docx", ".xlsx", ".pptx")
OTHER_ARCHIVES = (".tar", ".gz", ".tgz", ".bz2", ".tbz2", ".xz", ".txz", ".7z", ".rar")


class PublicationError(ValueError):
    pass


def normalized_path(path):
    parts = path.replace("\\", "/").casefold().split("/")
    if (parts[0] == "" or any(p == ".." or ":" in p or "\0" in p
                              or p.endswith((" ", ".")) and p != "." for p in parts)):
        raise PublicationError("unsafe or ambiguous path")
    return "/".join(p for p in parts if p not in ("", "."))


def residue_reason(path, mode="100644"):
    path = normalized_path(path)
    parts = path.split("/")
    name = parts[-1]
    if ".git" in parts:
        return "embedded Git metadata"
    if "__pycache__" in parts or name.endswith((".pyc", ".pyo")):
        return "Python bytecode"
    if re.search(r"\.db(?:-(?:journal|wal|shm))?$|\.sqlite[^/]*$", name):
        return "runtime database or sidecar (no fixture exceptions configured)"
    if name.endswith(".log") or any(parts[i:i + 2] == ["data", "logs"] for i in range(len(parts))):
        return "runtime log"
    if "chroma_db" in parts:
        return "stored index"
    if any(parts[i:i + 2] in (["data", "notes"], ["data", "clear-lake-watch-repo"])
           for i in range(len(parts))):
        return "local runtime checkout"
    if mode == "160000" and "data" in parts:
        return "runtime-data Git link"
    return None


@dataclass
class Budget:
    expanded: int = 0
    members: int = 0

    def consume(self, size):
        self.members += 1
        self.expanded += size
        if self.members > MAX_MEMBERS or self.expanded > MAX_EXPANDED_BYTES:
            raise PublicationError("archive member/expanded-byte limit exceeded")


def inspect_payload(path, raw, budget, depth=0):
    """Inspect bytes, even when a ZIP has been renamed; never follow member links."""
    reason = residue_reason(path)
    if reason:
        raise PublicationError(f"{path}: {reason}")
    if raw.startswith(b"SQLite format 3\0"):
        raise PublicationError(f"{path}: SQLite content under a different filename")
    is_zip = zipfile.is_zipfile(io.BytesIO(raw))
    lower = path.casefold()
    if not is_zip:
        unsupported_magic = (raw.startswith((b"\x1f\x8b", b"BZh", b"\xfd7zXZ\0", b"7z\xbc\xaf\x27\x1c", b"Rar!"))
                             or raw[257:262] == b"ustar")
        if lower.endswith(ZIP_SUFFIXES + OTHER_ARCHIVES) or unsupported_magic or raw.startswith(b"PK\x03\x04"):
            raise PublicationError(f"{path}: unreadable or unsupported archive; explicit review required")
        return
    if depth >= MAX_DEPTH:
        raise PublicationError(f"{path}: archive nesting limit exceeded")
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            seen = set()
            for info in archive.infolist():
                # orig_filename retains NULs that ZipInfo.filename otherwise truncates.
                name = normalized_path(info.orig_filename)
                if not name or name in seen:
                    raise PublicationError("empty or duplicate normalized archive member")
                seen.add(name)
                budget.consume(info.file_size)
                reason = residue_reason(name)
                if reason:
                    raise PublicationError(f"{name}: {reason}")
                file_type = stat.S_IFMT(info.external_attr >> 16)
                if file_type not in (0, stat.S_IFREG, stat.S_IFDIR) or info.flag_bits & 1:
                    raise PublicationError(f"{name}: linked, special or encrypted archive member")
                if info.is_dir() and info.file_size:
                    raise PublicationError(f"{name}: archive directory carries hidden payload")
                if not info.is_dir():
                    inspect_payload(name, archive.read(info), budget, depth + 1)
    except (PublicationError, zipfile.BadZipFile, zlib.error, RuntimeError, NotImplementedError, OSError, EOFError) as exc:
        raise PublicationError(f"{path}!/{exc}") from exc


def git(root, *args, input=None):
    return subprocess.check_output(["git", "-C", str(root), *args], input=input)


def staged_entries(root):
    entries = []
    for record in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        header, path = record.split(b"\t", 1)
        mode, oid, stage = header.decode("ascii").split()
        if stage != "0":
            raise PublicationError("unmerged index entries require resolution")
        entries.append((path.decode("utf-8", errors="strict"), mode, oid))
    return entries


def staged_blobs(root, entries):
    """Bound the complete index read before asking Git for any blob contents."""
    oids = sorted({oid for _, mode, oid in entries if mode != "160000"})
    if not oids:
        return {}
    request = ("\n".join(oids) + "\n").encode("ascii")
    sizes = git(root, "cat-file", "--batch-check", input=request).splitlines()
    total = 0
    for line in sizes:
        oid, kind, size = line.split()
        if kind != b"blob":
            raise PublicationError("missing or non-blob index object")
        total += int(size)
    if total > MAX_INDEX_BYTES:
        raise PublicationError("index byte limit exceeded; explicit review required")
    stream = io.BytesIO(git(root, "cat-file", "--batch", input=request))
    blobs = {}
    for expected in oids:
        oid, kind, size = stream.readline().split()
        if oid.decode() != expected or kind != b"blob":
            raise PublicationError("unexpected Git object response")
        size = int(size)
        raw = stream.read(size)
        if len(raw) != size or stream.read(1) != b"\n":
            raise PublicationError("truncated Git object response")
        blobs[expected] = raw
    return blobs


def check_index(root):
    errors = []
    try:
        entries = staged_entries(root)
        blobs = staged_blobs(root, entries)
        budget = Budget()  # One expansion budget across all distributed archives.
        for path, mode, oid in entries:
            try:
                reason = residue_reason(path, mode)
                if reason:
                    raise PublicationError(reason)
                if mode == "160000":
                    continue  # Unrelated, intentional source subprojects are outside A03a.
                if mode == "120000" and path.casefold().endswith(ZIP_SUFFIXES + OTHER_ARCHIVES):
                    raise PublicationError("archive symlink cannot be inspected")
                inspect_payload(path, blobs[oid], budget)
            except PublicationError as exc:
                errors.append(f"{path}: {exc}")
    except (PublicationError, subprocess.CalledProcessError, UnicodeError, ValueError) as exc:
        errors.append(str(exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check_index(args.root)
    if errors:
        print("Publication check FAILED:\n" + "\n".join(errors))
        return 1
    print("Publication check passed: staged runtime residue and supported archive contents inspected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
