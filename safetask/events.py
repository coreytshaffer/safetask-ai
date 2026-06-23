import json
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Optional

class HumanReviewStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    RETAINED = "retained"

class RetentionPolicy(str, Enum):
    TEMPORARY = "temporary"
    RETAIN = "retain"
    DELETE_AFTER_REVIEW = "delete_after_review"

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
    human_review_status: HumanReviewStatus
    retention_policy: RetentionPolicy
    end_time: Optional[datetime] = None
    clip_uri: Optional[str] = None
    snapshot_uri: Optional[str] = None
    confidence: Optional[float] = None

    def __post_init__(self):
        # Enforce enum types
        if not isinstance(self.human_review_status, HumanReviewStatus):
            self.human_review_status = HumanReviewStatus(self.human_review_status)

        if not isinstance(self.retention_policy, RetentionPolicy):
            self.retention_policy = RetentionPolicy(self.retention_policy)

        # Validate temporal integrity
        if self.end_time is not None and self.end_time < self.start_time:
            raise ValueError("end_time cannot be earlier than start_time")

        # Validate confidence scores
        if self.confidence is not None:
            if not (0.0 <= self.confidence <= 1.0):
                raise ValueError("confidence must be between 0.0 and 1.0")

    def to_json(self) -> str:
        d = asdict(self)
        d['start_time'] = self.start_time.isoformat()
        if self.end_time:
            d['end_time'] = self.end_time.isoformat()
        return json.dumps(d)

    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        d = json.loads(json_str)
        d['start_time'] = datetime.fromisoformat(d['start_time'])
        if d.get('end_time'):
            d['end_time'] = datetime.fromisoformat(d['end_time'])
        return cls(**d)
