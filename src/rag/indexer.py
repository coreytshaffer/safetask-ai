import os
from pathlib import Path

import chromadb
import yaml
from chromadb.utils import embedding_functions

from logger import logger


class DocumentIndexer:
    def __init__(
        self, db_dir: str = "data/chroma_db", collection_name: str = "field_docs"
    ):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.db_dir))

        # We use a standard lightweight embedding model for MVP semantic search
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.embedding_fn
        )

    def parse_markdown_with_frontmatter(self, filepath: Path):
        """Parses a markdown file with YAML frontmatter."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                metadata = yaml.safe_load(parts[1])
                text_content = parts[2].strip()
                return metadata, text_content
        return {}, content

    def parse_pdf(self, filepath: Path):
        """Parses a PDF file and returns a list of chunks (by page)."""
        try:
            import pypdf
        except ImportError:
            logger.warning("pypdf not installed. Skipping PDF indexing.")
            return []

        chunks = []
        try:
            with open(filepath, "rb") as f:
                reader = pypdf.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        chunks.append(
                            {
                                "id": f"{filepath.stem}_page_{i+1}",
                                "text": text.strip(),
                                "metadata": {
                                    "source": filepath.name,
                                    "page": str(i + 1),
                                    "type": "pdf",
                                },
                            }
                        )
        except Exception as e:
            logger.error(f"Error parsing PDF {filepath}: {e}")

        return chunks

    def index_directory(self, docs_dir: str = "data/documents"):
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            logger.warning(f"Directory {docs_dir} not found.")
            return

        documents = []
        metadatas = []
        ids = []

        # Index Markdown files
        for filepath in docs_path.glob("*.md"):
            metadata, text_content = self.parse_markdown_with_frontmatter(filepath)
            doc_id = metadata.get("id", filepath.stem)
            documents.append(text_content)
            clean_metadata = {k: str(v) for k, v in metadata.items()}
            clean_metadata["source"] = filepath.name
            clean_metadata["type"] = "markdown"
            metadatas.append(clean_metadata)
            ids.append(doc_id)

        # Index PDF files
        for filepath in docs_path.glob("*.pdf"):
            chunks = self.parse_pdf(filepath)
            for chunk in chunks:
                documents.append(chunk["text"])
                metadatas.append(chunk["metadata"])
                ids.append(chunk["id"])

        if ids:
            self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
            logger.info(f"Successfully indexed {len(ids)} documents/chunks.")
        else:
            logger.info("No documents found to index.")
