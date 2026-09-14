import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from safetask.core.provenance import ProvenanceError, eligible_for_review, resolve_provenance


@pytest.fixture
def source_env(tmp_path):
    source = tmp_path / "documents/example.md"
    source.parent.mkdir()
    source.write_text("Neutral source for boundary testing.", encoding="utf-8")
    catalog = tmp_path / "reviewed_sources.json"
    catalog.write_text('{"schema_version":1,"sources":[]}', encoding="utf-8")
    return source, catalog, tmp_path


def register(source, catalog, root, **overrides):
    record = dict(path=source.relative_to(root).as_posix(), review_id="test-review-1",
                  content_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  source_kind="external_source", source_locator="https://example.org/source",
                  issuer="Test issuer", scope="Test jurisdiction", source_version="test-v1",
                  reviewed_at="2026-09-11T00:00:00Z", official_source_domains=["example.org"])
    record.update(overrides)
    catalog.write_text(json.dumps(dict(schema_version=1, sources=[record])), encoding="utf-8")
    return record


@pytest.mark.parametrize("kind", ["synthetic", "external_source", "facility_policy", "unknown", "official_regulation"])
def test_metadata_never_approves(source_env, kind):
    source, catalog, root = source_env
    p = resolve_provenance(source, source.read_bytes(), {"source_kind": kind, "review_status": "reviewed",
        "authority_level": "official_regulation", "review_id": "invented"}, catalog_path=catalog, repository_root=root)
    assert not eligible_for_review(p)
    assert p.review_status == "unreviewed"


@pytest.mark.parametrize("kind", ["external_source", "facility_policy"])
def test_exact_match_modified_removed_and_revoked_review(source_env, kind):
    source, catalog, root = source_env
    register(source, catalog, root, source_kind=kind)
    resolve = lambda: resolve_provenance(source, source.read_bytes(), catalog_path=catalog, repository_root=root)
    assert eligible_for_review(resolve())
    source.write_text("Changed", encoding="utf-8")
    assert not eligible_for_review(resolve())
    register(source, catalog, root, source_kind=kind)
    assert eligible_for_review(resolve())
    catalog.write_text('{"schema_version":1,"sources":[]}', encoding="utf-8")
    assert not eligible_for_review(resolve())


def test_renamed_fixture_with_stronger_metadata_cannot_be_reviewed(source_env):
    source, catalog, root = source_env
    source.write_bytes((ROOT / "tests/fixtures/synthetic/water_policy.md").read_bytes().replace(
        b"source_kind: synthetic", b"source_kind: external_source"))
    register(source, catalog, root)
    p = resolve_provenance(source, source.read_bytes(), {"source_kind": "external_source", "review_status": "reviewed"},
                           catalog_path=catalog, repository_root=root)
    assert p.source_kind == "synthetic"
    assert not eligible_for_review(p)


def test_invalid_catalog_fails_closed(source_env):
    source, catalog, root = source_env
    catalog.write_text('{"schema_version":99,"sources":[]}', encoding="utf-8")
    with pytest.raises(ProvenanceError):
        resolve_provenance(source, source.read_bytes(), catalog_path=catalog, repository_root=root)


def test_duplicate_review_fails_closed(source_env):
    source, catalog, root = source_env
    record = register(source, catalog, root)
    catalog.write_text(json.dumps(dict(schema_version=1, sources=[record, record])), encoding="utf-8")
    with pytest.raises(ProvenanceError):
        resolve_provenance(source, source.read_bytes(), catalog_path=catalog, repository_root=root)
