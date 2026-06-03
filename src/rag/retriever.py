from pathlib import Path
from typing import List

import chromadb
from chromadb.utils import embedding_functions

from logger import logger

from .schema import DocumentMetadata, SourceCard


class DocumentRetriever:
    def __init__(
        self, db_dir: str = "data/chroma_db", collection_name: str = "field_docs"
    ):
        self.db_dir = Path(db_dir)

        self.client = chromadb.PersistentClient(path=str(self.db_dir))
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        try:
            self.collection = self.client.get_collection(
                name=collection_name, embedding_function=self.embedding_fn
            )
        except Exception:
            self.collection = None

    def search(self, query: str, n_results: int = 3) -> List[SourceCard]:
        if not self.collection:
            logger.warning("Collection not found. Please run indexer first.")
            return []

        results = self.collection.query(query_texts=[query], n_results=n_results)

        source_cards = []
        if results["documents"] and len(results["documents"]) > 0:
            for i in range(len(results["documents"][0])):
                doc_text = results["documents"][0][i]
                meta = results["metadatas"][0][i]
                distance = (
                    results["distances"][0][i]
                    if "distances" in results and results["distances"]
                    else None
                )

                metadata = DocumentMetadata(
                    id=meta.get("id", "unknown"),
                    title=meta.get("title", "Unknown Title"),
                    topic=meta.get("topic", "Unknown"),
                    source=meta.get("source", "Unknown Source"),
                    jurisdiction=meta.get("jurisdiction", "Unknown"),
                    freshness_date=meta.get("freshness_date", "Unknown"),
                    authority_level=meta.get("authority_level", "Unknown"),
                )

                card = SourceCard(
                    metadata=metadata, content=doc_text, relevance_score=distance
                )
                source_cards.append(card)

        return source_cards
