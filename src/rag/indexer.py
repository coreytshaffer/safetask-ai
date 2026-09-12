"""Disposable ranking index; current source bytes and the review catalog own provenance."""
import io
import json
from pathlib import Path
import threading
import uuid

import chromadb
from chromadb.config import Settings
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions
import yaml

from safetask.core.provenance import CATALOG_PATH, REPOSITORY_ROOT, read_catalog, resolve_provenance
from .schema import DocumentMetadata, SourceCard

COLLECTION_NAME = "field_docs_provenance_v1"
INDEX_LOCK = threading.RLock()


def source_path(root, relative):
    root = Path(root).resolve()
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts or ":" in str(relative):
        raise ValueError("Invalid source path")
    path = (root / relative).resolve()
    path.relative_to(root)  # Includes symlink containment.
    return path


def read_source_units(path, docs_root, *, catalog_path=CATALOG_PATH, repository_root=REPOSITORY_ROOT):
    path = Path(path).resolve()
    relative = path.relative_to(Path(docs_root).resolve()).as_posix()
    raw = path.read_bytes()
    declared = {}
    if path.suffix.lower() == ".md":
        text = raw.decode("utf-8-sig")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) != 3:
                raise ValueError("Invalid frontmatter")
            declared = yaml.safe_load(parts[1]) or {}
            if not isinstance(declared, dict):
                raise ValueError("Frontmatter must be an object")
            text = parts[2].strip()
        units = [(None, text)]
    elif path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        units = [(i + 1, page.extract_text() or "") for i, page in enumerate(PdfReader(io.BytesIO(raw)).pages)]
    else:
        return []
    provenance = resolve_provenance(path, raw, declared, catalog_path=catalog_path, repository_root=repository_root)
    return [
        SourceCard(DocumentMetadata(
            id=f"{relative}#page={page or 0}",
            title=str(declared.get("title", path.stem)),
            topic=str(declared.get("topic", "Unknown")),
            source=path.name,
            jurisdiction=provenance.scope or "Unverified",
            freshness_date=str(declared.get("freshness_date", "Unknown (source-declared)")),
            authority_level="draft",  # Legacy compatibility only; never an authority badge.
            provenance=provenance, relative_path=relative, page=page,
        ), text.strip())
        for page, text in units if text.strip()
    ]


class DocumentIndexer:
    def __init__(self, db_dir=None, collection_name=COLLECTION_NAME, *,
                 docs_dir=None, catalog_path=CATALOG_PATH, repository_root=REPOSITORY_ROOT,
                 embedding_function=None):
        if collection_name != COLLECTION_NAME:
            raise ValueError("Legacy/alternate collections are not supported")
        self.docs_dir = Path(docs_dir or REPOSITORY_ROOT / "data/documents").resolve()
        self.catalog_path, self.repository_root = catalog_path, repository_root
        self.client = chromadb.PersistentClient(
            path=str(db_dir or REPOSITORY_ROOT / "data/chroma_db"),
            settings=Settings(anonymized_telemetry=False),
        )
        self.embedding_fn = embedding_function or embedding_functions.DefaultEmbeddingFunction()

    def index_directory(self, docs_dir=None):
        if docs_dir is not None:
            self.docs_dir = Path(docs_dir).resolve()
        with INDEX_LOCK:
            # Failures leave no readable partial build. Only our new collection is replaced.
            try:
                self.client.delete_collection(COLLECTION_NAME)
            except NotFoundError:
                pass
            generation = uuid.uuid4().hex
            metadata = {"provenance_version": 1, "build_state": "building", "generation": generation}
            collection = self.client.create_collection(
                COLLECTION_NAME, metadata=metadata, embedding_function=self.embedding_fn)
            read_catalog(self.catalog_path)
            if not self.docs_dir.is_dir():
                raise ValueError("Source directory unavailable")
            cards = []
            for path in sorted(self.docs_dir.iterdir()):
                if path.is_file() and path.suffix.lower() in {".md", ".pdf"}:
                    cards.extend(read_source_units(
                        path, self.docs_dir, catalog_path=self.catalog_path,
                        repository_root=self.repository_root))
            if cards:
                collection.add(
                    ids=[c.metadata.id for c in cards],
                    documents=[c.content for c in cards],
                    metadatas=[{
                        "relative_path": c.metadata.relative_path,
                        "content_sha256": c.metadata.provenance.content_sha256,
                        "provenance": json.dumps(c.metadata.provenance.to_dict(), sort_keys=True),
                    } for c in cards],
                )
            collection.modify(metadata={**metadata, "build_state": "ready"})
            return {"status": "ready", "indexed_units": len(cards), "collection": COLLECTION_NAME}
