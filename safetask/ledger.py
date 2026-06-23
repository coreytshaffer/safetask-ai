import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Union

class ActionType(str, Enum):
    EVENT_CREATED = "event_created"
    REVIEW_STATUS_CHANGED = "review_status_changed"
    RETENTION_POLICY_CHANGED = "retention_policy_changed"
    NOTE_ADDED = "note_added"

@dataclass
class LedgerRecord:
    timestamp: datetime
    record_id: str
    event_id: str
    action_type: ActionType
    payload: Dict[str, Any]

    def __post_init__(self):
        if not isinstance(self.action_type, ActionType):
            self.action_type = ActionType(self.action_type)

    def to_json(self) -> str:
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return json.dumps(d)

    @classmethod
    def from_json(cls, json_str: str) -> 'LedgerRecord':
        d = json.loads(json_str)
        d['timestamp'] = datetime.fromisoformat(d['timestamp'])
        return cls(**d)

class EvidenceLedger:
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def append_record(self, event_id: str, action_type: Union[ActionType, str], payload: Dict[str, Any]) -> LedgerRecord:
        record = LedgerRecord(
            timestamp=datetime.now(),
            record_id=str(uuid.uuid4()),
            event_id=event_id,
            action_type=ActionType(action_type),
            payload=payload
        )
        
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(record.to_json() + "\n")
            
        return record
