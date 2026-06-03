import pytest
from pathlib import Path
import sys

# Ensure src is in the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag.indexer import DocumentIndexer
from rag.retriever import DocumentRetriever

def test_rag_flow(tmp_path):
    # Use tmp_path for ChromaDB so tests don't mess up the actual DB
    db_path = tmp_path / "chromadb"
    
    # 1. Indexing
    indexer = DocumentIndexer(db_dir=str(db_path))
    docs_dir = Path(__file__).parent.parent / "data" / "documents"
    indexer.index_directory(str(docs_dir))
    
    # Check that collection has documents
    assert indexer.collection.count() > 0
    
    # 2. Retrieval
    retriever = DocumentRetriever(db_dir=str(db_path))
    cards = retriever.search("cyanobacteria bloom PPE", n_results=2)
    
    assert len(cards) > 0
    
    # The clear_lake protocol has cyanobacteria and PPE
    assert any("protocol" in card.metadata.id.lower() or "protocol" in card.metadata.title.lower() for card in cards)
