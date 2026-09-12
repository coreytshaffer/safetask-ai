import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RETIRED = {
    "field_aware_mvp.zip",
    "data/documents/state_water_reg_402.md",
    "safetask/domains/gaming/regulations.json",
    "archive/scratch/epic9.js",
    "src/rag/__pycache__/indexer.cpython-314.pyc",
    "src/rag/__pycache__/retriever.cpython-314.pyc",
    "src/rag/__pycache__/schema.cpython-314.pyc",
    "src/web/__pycache__/app.cpython-314.pyc",
    "safetask/api/__pycache__/router.cpython-314.pyc",
    "tests/__pycache__/test_rag.cpython-314-pytest-9.0.3.pyc",
}


def tracked_files():
    return subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().strip("\0").split("\0")


def test_retired_artifacts_absent_from_current_tracked_tree():
    tracked = tracked_files()
    assert not RETIRED.intersection(tracked)
    assert not any("/chroma_db/" in "/" + p for p in tracked)
    assert all(not (ROOT / p).exists() for p in RETIRED)


def archive_members(raw, prefix="", depth=0):
    assert depth < 5, "Unexpected nested archive requires manual review"
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        assert sum(info.file_size for info in archive.infolist()) < 50_000_000
        for info in archive.infolist():
            name = info.filename.replace("\\", "/")
            yield prefix + name
            if name.lower().endswith(".zip"):
                yield from archive_members(archive.read(info), prefix + name + "!/", depth + 1)


def test_current_archives_do_not_redistribute_retired_source_or_index():
    for filename in tracked_files():
        if filename.lower().endswith(".zip"):
            for member in archive_members((ROOT / filename).read_bytes()):
                assert "chroma_db/" not in member
                assert PurePosixPath(member).name not in {"state_water_reg_402.md", "field_aware_mvp.zip"}
                assert "gaming/regulations.json" not in member
                assert not any(member.endswith(retired) for retired in RETIRED)


def test_no_real_world_reviews_and_only_neutral_marked_fixtures():
    assert json.loads((ROOT / "policy/reviewed_sources.json").read_text()) == {"schema_version": 1, "sources": []}
    water = (ROOT / "tests/fixtures/synthetic/water_policy.md").read_text()
    gaming = (ROOT / "tests/fixtures/synthetic/gaming_policies.json").read_text()
    assert "SAFETASK_SYNTHETIC_FIXTURE" in water and "source_kind: synthetic" in water
    assert "SAFETASK_SYNTHETIC_FIXTURE" in gaming
    for entry in json.loads(gaming):
        assert entry["source_kind"] == "synthetic"
        assert entry["review_status"] == "unreviewed"


def test_duplicate_authority_cards_and_static_compliance_anchor_are_absent():
    page = (ROOT / "safetask/apps/legacy_scc/index.html").read_text(encoding="utf-8")
    for retired in ["Pre-Loaded Regulatory Reference Subparts", "SICS Section", "TICS Section",
                    "NIGC MICS COMPLIANT", "MICS Violation", "MICS/TICS Anti-Hallucination"]:
        assert retired not in page
    assert 'src="provenance-migration.js"' in page
    assert page.index('src="provenance-migration.js"') < page.index('src="app.js"')
