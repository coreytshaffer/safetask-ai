from dataclasses import dataclass
from typing import Optional
from dataclasses import asdict
from safetask.core.provenance import Provenance


@dataclass
class DocumentMetadata:
    id: str
    title: str
    topic: str
    source: str
    jurisdiction: str
    freshness_date: str
    authority_level: str
    provenance: Provenance
    relative_path: str
    page: Optional[int] = None


@dataclass
class SourceCard:
    metadata: DocumentMetadata
    content: str
    relevance_score: Optional[float] = None

    def to_dict(self):
        result = asdict(self)
        result["metadata"]["provenance_label"] = self.metadata.provenance.label
        return result
