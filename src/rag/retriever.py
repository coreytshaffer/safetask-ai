"""Chroma ranks candidates. Never return its stored document or authority claims."""
import json

from safetask.core.provenance import eligible_for_review, read_catalog
from chromadb.errors import NotFoundError
from .indexer import COLLECTION_NAME, INDEX_LOCK, DocumentIndexer, read_source_units, source_path
from .schema import SourceCard


class RetrievalUnavailable(RuntimeError):
    status = "retrieval_unavailable"


class IndexRequired(RetrievalUnavailable):
    status = "index_required"


class DocumentRetriever(DocumentIndexer):
    def _collection(self):
        try:
            collection = self.client.get_collection(COLLECTION_NAME, embedding_function=self.embedding_fn)
        except NotFoundError as exc:
            raise IndexRequired("Build the provenance index first") from exc
        meta = collection.metadata or {}
        if meta.get("provenance_version") != 1 or meta.get("build_state") != "ready" or not meta.get("generation"):
            raise RetrievalUnavailable("Index build is incomplete or incompatible")
        return collection

    def _current_card(self, relative, unit_id):
        path = source_path(self.docs_dir, relative)
        for card in read_source_units(path, self.docs_dir, catalog_path=self.catalog_path,
                                      repository_root=self.repository_root):
            if card.metadata.id == unit_id:
                return card
        return None

    def validate_card(self, card, *, reviewed_only=True):
        """Revalidate adapter input; never accept a dict's self-declared review."""
        if not isinstance(card, SourceCard):
            raise RetrievalUnavailable("Invalid source card")
        current = self._current_card(card.metadata.relative_path, card.metadata.id)
        if (current is None or current.metadata != card.metadata or current.content != card.content
                or (reviewed_only and not eligible_for_review(current.metadata.provenance))):
            raise RetrievalUnavailable("Source changed or is not reviewed")
        current.relevance_score = card.relevance_score
        return current

    def search(self, query, n_results=3, *, reviewed_only=False):
        try:
            with INDEX_LOCK:
                read_catalog(self.catalog_path)
                collection = self._collection()
                generation = collection.metadata["generation"]
                count = collection.count()
                cards = []
                if count and n_results > 0:
                    results = collection.query(
                        query_texts=[query], n_results=min(n_results, count),
                        include=["metadatas", "distances"],
                    )
                    for index, unit_id in enumerate(results["ids"][0]):
                        meta = results["metadatas"][0][index]
                        try:
                            card = self._current_card(meta["relative_path"], unit_id)
                            if card is None:
                                continue
                            provenance = card.metadata.provenance
                            if (provenance.content_sha256 != meta["content_sha256"]
                                    or provenance.to_dict() != json.loads(meta["provenance"])):
                                continue
                            if reviewed_only and not eligible_for_review(provenance):
                                continue
                            card.relevance_score = results["distances"][0][index]
                            cards.append(card)
                        except (OSError, ValueError, KeyError, TypeError):
                            # Stale, missing, malformed, moved and mismatched candidates are unusable.
                            continue
                if self._collection().metadata["generation"] != generation:
                    raise RetrievalUnavailable("Index changed during retrieval")
                read_catalog(self.catalog_path)
                # Catch source/catalog changes during this request before returning any result.
                return [self.validate_card(c, reviewed_only=reviewed_only) for c in cards]
        except RetrievalUnavailable:
            raise
        except Exception as exc:
            raise RetrievalUnavailable("Source retrieval unavailable") from exc
