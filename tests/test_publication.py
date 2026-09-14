"""A03a: exercise staged publication, including adversarial archive contents."""
import hashlib
import io
from pathlib import Path
import stat
import subprocess
import sys
import zipfile

import pytest

from scripts import check_publication as gate

ROOT = Path(__file__).resolve().parents[1]
EXPORT = "data/exports/clear_lake_context_20260602_064501_bundle.zip"
EXPORT_SHA256 = "f8aed49776e99ea889887a843b062563f344a44b3acaf7d33f57779d90b63230"


def zip_bytes(members):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, raw in members:
            archive.writestr(name, raw)
    return output.getvalue()


def git(repo, *args, input=None):
    return gate.git(repo, *args, input=input)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "core.hooksPath", str(tmp_path / "no-hooks"))
    return tmp_path


def stage(repo, path, raw=b""):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    git(repo, "add", "-f", "--", path)


@pytest.mark.parametrize("path", [
    "data/field_notes.db", "src/data/field_notes.db", "pitlens-table-games/pitlens.db",
    "test.DB-WAL", "test.db-shm", "test.db-journal", "test.SQLITE3", "test.sqlite-wal",
    "module.pyc", "module.PYO", "__pycache__/renamed.dat", "DATA/LOGS/trace.txt",
    "nested/runtime.log", "data/notes/note.md", "data/clear-lake-watch-repo/shore.json",
])
def test_forced_tracking_rejects_residue_even_when_empty_or_ignored(repo, path):
    (repo / ".gitignore").write_text("*\n")
    stage(repo, path)
    assert gate.check_index(repo), path


def test_archive_gate_uses_index_bytes_and_does_not_follow_working_copy(repo):
    bad = zip_bytes([("private/.GiT/config", b"synthetic test marker")])
    clean = zip_bytes([("synthetic-example.md", b"Explicit synthetic example")])
    stage(repo, "distribution.zip", bad)
    (repo / "distribution.zip").write_bytes(clean)
    assert "embedded Git" in "\n".join(gate.check_index(repo))
    git(repo, "add", "distribution.zip")
    (repo / "distribution.zip").write_bytes(bad)
    assert gate.check_index(repo) == []  # Unstaged bytes are not this commit's distribution.
    (repo / "distribution.zip").unlink()
    assert gate.check_index(repo) == []


@pytest.mark.parametrize("member", [
    "bundle\\.GiT\\objects\\pack\\sample.pack", "bundle/.git", "./bundle/DATA/LOGS/trace.txt",
    "bundle/cache.SQLite3-shm", "bundle/__PYCACHE__/renamed", "bundle/module.PyC",
    "bundle/.git./config", "../outside.md", "/absolute.md", "C:\\machine\\file.md",
])
def test_nested_renamed_archives_normalize_paths_and_reject_residue(member):
    raw = zip_bytes([("inner.bin", zip_bytes([(member, b"synthetic")]))])
    with pytest.raises(gate.PublicationError):
        gate.inspect_payload("renamed.bin", raw, gate.Budget())


def test_clean_nested_archive_remains_publishable():
    raw = zip_bytes([("inner.zip", zip_bytes([("examples/synthetic.md", b"Synthetic example")]))])
    gate.inspect_payload("distribution.zip", raw, gate.Budget())


def test_links_duplicate_names_encryption_and_unknown_archives_fail_closed():
    link = zipfile.ZipInfo("link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    duplicate = zip_bytes([("Example.md", b"one"), ("example.md", b"two")])
    encrypted = bytearray(zip_bytes([("example.md", b"content")]))
    # Set the encrypted flag in the local and central headers; no decryption attempted.
    encrypted[6] |= 1
    encrypted[encrypted.index(b"PK\x01\x02") + 8] |= 1
    cases = [
        ("links.zip", zip_bytes([(link, b"outside")])), ("duplicates.zip", duplicate),
        ("encrypted.zip", bytes(encrypted)), ("bad.zip", b"not a zip"),
        ("hidden.zip", zip_bytes([("directory/", zip_bytes([(".git/config", b"synthetic")]))])),
        ("unknown.7z", b"uninspected"), ("renamed.bin", b"\x1f\x8b\x08unknown"),
        ("renamed.db.txt", b"SQLite format 3\0synthetic"),
    ]
    for name, raw in cases:
        with pytest.raises(gate.PublicationError):
            gate.inspect_payload(name, raw, gate.Budget())


def test_shared_archive_limits_and_depth_are_enforced(monkeypatch):
    raw = zip_bytes([("example.md", b"1234")])
    monkeypatch.setattr(gate, "MAX_EXPANDED_BYTES", 7)
    budget = gate.Budget()
    gate.inspect_payload("one.zip", raw, budget)
    with pytest.raises(gate.PublicationError, match="limit"):
        gate.inspect_payload("two.zip", raw, budget)
    monkeypatch.setattr(gate, "MAX_EXPANDED_BYTES", 100_000)
    monkeypatch.setattr(gate, "MAX_MEMBERS", 1)
    with pytest.raises(gate.PublicationError, match="limit"):
        gate.inspect_payload("two.zip", zip_bytes([("a", b""), ("b", b"")]), gate.Budget())
    monkeypatch.setattr(gate, "MAX_MEMBERS", 100)
    monkeypatch.setattr(gate, "MAX_DEPTH", 1)
    with pytest.raises(gate.PublicationError, match="nesting"):
        gate.inspect_payload("outer.zip", zip_bytes([("inner.zip", raw)]), gate.Budget())


def test_gitlinks_and_conflicted_index_fail_closed(repo):
    stage(repo, "source.md", b"Synthetic example")
    git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "-qm", "Synthetic baseline")
    oid = git(repo, "rev-parse", "HEAD").decode().strip()
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{oid},data/notes")
    assert "runtime checkout" in "\n".join(gate.check_index(repo))
    git(repo, "update-index", "--force-remove", "data/notes")
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{oid},data/other-runtime")
    assert "runtime-data Git link" in "\n".join(gate.check_index(repo))
    git(repo, "update-index", "--force-remove", "data/other-runtime")
    assert gate.check_index(repo) == []
    blob = git(repo, "rev-parse", ":source.md").decode().strip()
    git(repo, "update-index", "--index-info", input=f"100644 {blob} 1\tconflict.md\n".encode())
    assert "unmerged" in "\n".join(gate.check_index(repo))


def test_index_size_limit_and_cli_failure(repo, monkeypatch):
    stage(repo, "source.md", b"Synthetic example")
    monkeypatch.setattr(gate, "MAX_INDEX_BYTES", 1)
    assert "index byte limit" in "\n".join(gate.check_index(repo))
    stage(repo, "empty.db")
    result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/check_publication.py"),
                             "--root", str(repo)], capture_output=True, text=True)
    assert result.returncode == 1 and "empty.db" in result.stdout


def test_current_index_and_reviewed_export_are_preserved():
    assert gate.check_index(ROOT) == []
    raw = git(ROOT, "show", f":{EXPORT}")
    assert hashlib.sha256(raw).hexdigest() == EXPORT_SHA256
    assert (ROOT / EXPORT).read_bytes() == raw


def test_runtime_ignore_rules_are_narrow(repo):
    (repo / ".gitignore").write_bytes((ROOT / ".gitignore").read_bytes())
    ignored = ["data/field_notes.db", "src/data/field_notes.db", "pitlens-table-games/pitlens.db",
               "local.db-journal", "local.db-wal", "local.db-shm", "local.sqlite3-shm",
               "local.pyo", "any/__pycache__/local.pyc", "data/logs/local.log",
               "data/notes/local.md", "data/clear-lake-watch-repo/data/shore.json"]
    result = git(repo, "check-ignore", "--no-index", "--stdin", input=("\n".join(ignored) + "\n").encode())
    assert set(result.decode().splitlines()) == set(ignored)
    source = "tests/fixtures/synthetic/example.md"
    result = subprocess.run(["git", "-C", str(repo), "check-ignore", "--no-index", source], capture_output=True)
    assert result.returncode == 1
    stage(repo, source, b"Explicit synthetic example")
    assert gate.check_index(repo) == []
