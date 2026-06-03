from dataclasses import dataclass
from typing import Optional


@dataclass
class DocumentMetadata:
    id: str
    title: str
    topic: str
    source: str
    jurisdiction: str
    freshness_date: str
    authority_level: str


@dataclass
class SourceCard:
    metadata: DocumentMetadata
    content: str
    relevance_score: Optional[float] = None
