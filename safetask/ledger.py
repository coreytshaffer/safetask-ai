import hashlib
import json
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Union, List, Iterator

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
    previous_hash: str = "GENESIS"
    record_hash: str = ""

    def __post_init__(self):
        try:
            if not isinstance(self.action_type, ActionType):
                self.action_type = ActionType(self.action_type)
        except ValueError as e:
            raise ValueError(f"Unknown action type: {self.action_type}") from e

    def compute_hash(self) -> str:
        d = asdict(self)
        d.pop('record_hash', None)
        d['timestamp'] = self.timestamp.isoformat()
        canonical_json = json.dumps(d, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    def to_json(self) -> str:
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return json.dumps(d)

    @classmethod
    def from_json(cls, json_str: str) -> 'LedgerRecord':
        try:
            d = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError("Malformed JSONL record") from e

        try:
            d['timestamp'] = datetime.fromisoformat(d['timestamp'])
        except (KeyError, ValueError) as e:
            raise ValueError("Malformed record data") from e

        return cls(**d)

@dataclass
class EventReviewState:
    event_id: str
    latest_review_status: str = "pending"
    latest_retention_policy: str = "default"
    notes: List[str] = field(default_factory=list)
    created_record_id: Union[str, None] = None
    updated_at: Union[datetime, None] = None

class EvidenceLedger:
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def append_record(self, event_id: str, action_type: Union[ActionType, str], payload: Dict[str, Any]) -> LedgerRecord:
        previous_hash = "GENESIS"
        if self.file_path.exists():
            records = self.read_records()
            if records:
                previous_hash = records[-1].record_hash

        record = LedgerRecord(
            timestamp=datetime.now(),
            record_id=str(uuid.uuid4()),
            event_id=event_id,
            action_type=ActionType(action_type),
            payload=payload,
            previous_hash=previous_hash
        )
        record.record_hash = record.compute_hash()

        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(record.to_json() + "\n")

        return record

    def iter_records(self) -> Iterator[LedgerRecord]:
        if not self.file_path.exists():
            return

        with self.file_path.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield LedgerRecord.from_json(line)
                except Exception as e:
                    raise ValueError(f"Malformed record at line {line_number}: {str(e)}") from e

    def read_records(self) -> List[LedgerRecord]:
        return list(self.iter_records())

    def records_for_event(self, event_id: str) -> List[LedgerRecord]:
        return [record for record in self.iter_records() if record.event_id == event_id]

    def reconstruct_event_state(self, event_id: str) -> EventReviewState:
        records = self.records_for_event(event_id)
        state = EventReviewState(event_id=event_id)

        for record in records:
            if record.action_type == ActionType.EVENT_CREATED:
                state.created_record_id = record.record_id
            elif record.action_type == ActionType.REVIEW_STATUS_CHANGED:
                if "status" in record.payload:
                    state.latest_review_status = record.payload["status"]
            elif record.action_type == ActionType.RETENTION_POLICY_CHANGED:
                if "policy" in record.payload:
                    state.latest_retention_policy = record.payload["policy"]
            elif record.action_type == ActionType.NOTE_ADDED:
                if "text" in record.payload:
                    state.notes.append(record.payload["text"])

            state.updated_at = record.timestamp

        return state

    def verify_integrity(self) -> bool:
        records = self.read_records()
        if not records:
            return True

        expected_previous_hash = "GENESIS"

        for i, record in enumerate(records, start=1):
            if not record.previous_hash or not record.record_hash:
                raise ValueError(f"Missing hash fields at record {i}")

            if record.previous_hash != expected_previous_hash:
                raise ValueError(f"Hash chain broken at record {i}: previous_hash mismatch")

            computed_hash = record.compute_hash()
            if record.record_hash != computed_hash:
                raise ValueError(f"Payload tampered at record {i}: record_hash mismatch")

            expected_previous_hash = record.record_hash

        return True
