import json
import pytest
from rag.indexer import COLLECTION_NAME, DocumentIndexer
from rag.retriever import DocumentRetriever, IndexRequired, RetrievalUnavailable
from test_provenance import register


class LocalEmbedding:
    def __call__(self, input):
        return [[float(len(text) % 13), 1.0, 0.5] for text in input]
    def name(self):
        return "deterministic-test-only"
    def embed_query(self, input):
        return self(input)
    def is_legacy(self):
        return True


@pytest.fixture
def rig(tmp_path, no_network):
    docs = tmp_path / "documents"
    docs.mkdir()
    source = docs / "source.md"
    source.write_text("Neutral source for testing.")
    catalog = tmp_path / "catalog.json"
    catalog.write_text('{"schema_version":1,"sources":[]}')
    kwargs = dict(db_dir=tmp_path / "index", docs_dir=docs, catalog_path=catalog,
                  repository_root=tmp_path, embedding_function=LocalEmbedding())
    return source, catalog, DocumentIndexer(**kwargs), DocumentRetriever(**kwargs)


def test_missing_legacy_only_and_valid_empty(rig):
    source, catalog, indexer, retriever = rig
    indexer.client.create_collection("field_docs", embedding_function=LocalEmbedding()).add(
        ids=["obsolete-water"], documents=["Obsolete authority"], metadatas=[{"authority_level": "official_regulation"}])
    with pytest.raises(IndexRequired):
        retriever.search("water")
    source.unlink()
    assert indexer.index_directory()["indexed_units"] == 0
    assert retriever.search("water") == []
    assert indexer.client.get_collection("field_docs").count() == 1


def test_provenance_round_trip_uses_current_bytes_not_cached_text(rig):
    source, catalog, indexer, retriever = rig
    register(source, catalog, source.parent.parent)
    indexer.index_directory()
    col = indexer.client.get_collection(COLLECTION_NAME, embedding_function=LocalEmbedding())
    col.update(ids=["source.md#page=0"], documents=["FORGED STORED AUTHORITY"])
    card, = retriever.search("neutral", reviewed_only=True)
    assert card.content == source.read_text()
    serialized = card.to_dict()
    assert serialized["metadata"]["provenance"]["review_status"] == "reviewed"
    assert "applicability requires human review" in serialized["metadata"]["provenance_label"]
    assert serialized["metadata"]["provenance"]["content_sha256"] == json.loads(catalog.read_text())["sources"][0]["content_sha256"]


@pytest.mark.parametrize("mutation", ["removed", "modified", "renamed", "revoked", "review_changed", "unit", "path", "hash", "metadata", "traversal"])
def test_stale_candidates_never_return(rig, mutation):
    source, catalog, indexer, retriever = rig
    register(source, catalog, source.parent.parent)
    indexer.index_directory()
    col = indexer.client.get_collection(COLLECTION_NAME, embedding_function=LocalEmbedding())
    if mutation == "removed":
        source.unlink()
    elif mutation == "modified":
        source.write_text("Changed source")
    elif mutation == "renamed":
        source.rename(source.with_name("other.md"))
    elif mutation == "revoked":
        catalog.write_text('{"schema_version":1,"sources":[]}')
    elif mutation == "review_changed":
        register(source, catalog, source.parent.parent, review_id="replacement-review")
    elif mutation == "unit":
        data = col.get(include=["metadatas"])
        col.delete(ids=["source.md#page=0"])
        col.add(ids=["source.md#page=9"], documents=["stale"], metadatas=data["metadatas"])
    else:
        field, value = {
            "path": ("relative_path", "missing.md"), "hash": ("content_sha256", "0" * 64),
            "metadata": ("provenance", "{}"), "traversal": ("relative_path", "../source.md")
        }[mutation]
        col.update(ids=["source.md#page=0"], metadatas=[{field: value}])
    assert retriever.search("neutral") == []


def test_replacement_rebuild_removes_units_and_usable_from_existing_retriever(rig):
    source, catalog, indexer, retriever = rig
    indexer.index_directory()
    assert len(retriever.search("neutral")) == 1
    source.unlink()
    indexer.index_directory()
    assert retriever.search("neutral") == []
    assert indexer.client.get_collection(COLLECTION_NAME).count() == 0


def test_partial_or_failed_build_and_catalog_failure_are_unavailable(rig):
    source, catalog, indexer, retriever = rig
    source.write_text("---\ninvalid: [\n---\nbody")
    with pytest.raises(Exception):
        indexer.index_directory()
    with pytest.raises(RetrievalUnavailable, match="incomplete"):
        retriever.search("neutral")
    source.write_text("Neutral")
    indexer.index_directory()
    catalog.write_text("invalid")
    with pytest.raises(RetrievalUnavailable):
        retriever.search("neutral")


def test_unreviewed_lookup_is_labelled_and_excluded_from_review(rig):
    source, catalog, indexer, retriever = rig
    source.write_text("---\nsource_kind: external_source\nreview_status: reviewed\nauthority_level: official_regulation\n---\nNeutral")
    indexer.index_directory()
    card, = retriever.search("neutral")
    assert card.metadata.provenance.review_status == "unreviewed"
    assert retriever.search("neutral", reviewed_only=True) == []
    with pytest.raises(RetrievalUnavailable):
        retriever.validate_card(card)
