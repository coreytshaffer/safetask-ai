from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Event:
    """
    A normalized safety event, independent of any specific camera system.
    This serves as the ingestion boundary for any local VMS/NVR.
    """
    source_system: str
    camera_id: str
    event_id: str
    event_type: str
    start_time: datetime
    human_review_status: str
    retention_policy: str
    end_time: Optional[datetime] = None
    clip_uri: Optional[str] = None
    snapshot_uri: Optional[str] = None
    confidence: Optional[float] = None
