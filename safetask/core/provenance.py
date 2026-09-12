"""Content-bound source review. Source metadata can describe, never approve.

The catalog is repository-controlled configuration, not a reviewer identity service.
Runtime callers must not accept its path or repository_root from an HTTP request.
"""
from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPOSITORY_ROOT / "policy/reviewed_sources.json"
VERSION = 1
KINDS = {"synthetic", "external_source", "facility_policy", "unknown"}
FIXTURE_MARKER = b"SAFETASK_SYNTHETIC_FIXTURE"


class ProvenanceError(ValueError):
    pass


@dataclass(frozen=True)
class Provenance:
    provenance_version: int
    source_id: str
    source_kind: str
    review_status: str
    content_sha256: str
    review_id: str | None = None
    source_locator: str | None = None
    issuer: str | None = None
    scope: str | None = None
    source_version: str | None = None
    reviewed_at: str | None = None

    def to_dict(self):
        return asdict(self)

    @property
    def label(self):
        if self.source_kind == "synthetic":
            return "Synthetic test material - not reviewed authority"
        if eligible_for_review(self):
            kind = "facility policy" if self.source_kind == "facility_policy" else "external source"
            return f"Reviewed {kind} record - applicability requires human review"
        return "Unreviewed reference - not reviewed authority"


def eligible_for_review(provenance):
    return (
        isinstance(provenance, Provenance)
        and provenance.provenance_version == VERSION
        and provenance.source_kind in {"external_source", "facility_policy"}
        and provenance.review_status == "reviewed"
        and bool(provenance.review_id)
    )


def read_catalog(path=CATALOG_PATH):
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schema_version") != VERSION:
            raise ValueError("unsupported catalog")
        records = payload["sources"]
        if not isinstance(records, list):
            raise ValueError("sources must be a list")
        seen_paths, seen_reviews = set(), set()
        for record in records:
            required = ("path", "review_id", "content_sha256", "source_kind", "source_locator",
                        "issuer", "scope", "source_version", "reviewed_at")
            if not isinstance(record, dict) or any(
                not isinstance(record.get(k), str) or not record[k].strip() for k in required
            ):
                raise ValueError("incomplete review record")
            relative = PurePosixPath(record["path"])
            if relative.is_absolute() or ".." in relative.parts or "\\" in record["path"] or ":" in record["path"]:
                raise ValueError("review path must be repository-relative")
            if record["path"] in seen_paths or record["review_id"] in seen_reviews:
                raise ValueError("duplicate review record")
            seen_paths.add(record["path"])
            seen_reviews.add(record["review_id"])
            if record["source_kind"] not in {"external_source", "facility_policy"}:
                raise ValueError("synthetic/unknown sources cannot be approved")
            if not re.fullmatch(r"[0-9a-f]{64}", record["content_sha256"]):
                raise ValueError("invalid source hash")
            datetime.fromisoformat(record["reviewed_at"].replace("Z", "+00:00"))
        return records
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ProvenanceError("Review catalog unavailable or invalid") from exc


def resolve_provenance(path, raw, declared=None, *, catalog_path=CATALOG_PATH,
                       repository_root=REPOSITORY_ROOT):
    path, root = Path(path).resolve(), Path(repository_root).resolve()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        source_id = path.relative_to(root).as_posix()
    except ValueError:
        # Unregistered local reference files remain usable, without publishing local paths.
        source_id = "local:" + hashlib.sha256(str(path).encode()).hexdigest()
    declared = declared if isinstance(declared, dict) else {}
    kind = declared.get("source_kind", "unknown")
    if kind not in KINDS:
        kind = "unknown"
    synthetic = (
        kind == "synthetic" or FIXTURE_MARKER in raw
        or {"tests", "fixtures"}.issubset(set(path.parts))
    )
    records = read_catalog(catalog_path)
    if synthetic:
        kind = "synthetic"
    else:
        for record in records:
            if record["path"] == source_id and record["content_sha256"] == digest:
                return Provenance(
                    VERSION, source_id, record["source_kind"], "reviewed", digest,
                    **{key: record[key] for key in ("review_id", "source_locator", "issuer",
                       "scope", "source_version", "reviewed_at")},
                )
    return Provenance(VERSION, source_id, kind, "unreviewed", digest,
                      source_locator=path.name)
