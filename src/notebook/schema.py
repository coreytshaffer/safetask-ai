import uuid
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FieldNote:
    site_id: str
    timestamp: str
    notes: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    observer: Optional[str] = None
    coordinates: Optional[str] = None
    confidence_level: Optional[str] = None
    evidence_type: Optional[str] = None
