from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from safetask.events import Event

class AdapterValidationError(Exception):
    pass

PROHIBITED_CAPABILITIES = {
    "face_recognition",
    "alpr",
    "license_plate_recognition",
    "biometric_identification",
    "weapon_detection",
    "law_enforcement_workflow",
    "automated_escalation",
    "cloud_processing_required",
    "public_surveillance"
}

@dataclass
class AdapterPayload:
    adapter_name: str
    adapter_version: str
    source_system: str
    source_event_id: str
    camera_id: str
    event_type: str
    start_time: str
    evidence_references: Dict[str, str]
    local_processing_required: bool
    end_time: Optional[str] = None
    confidence: Optional[float] = None
    prohibited_capability_flags: List[str] = field(default_factory=list)
    capability_claims: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.adapter_name:
            raise AdapterValidationError("adapter_name is required")
        if not self.adapter_version:
            raise AdapterValidationError("adapter_version is required")
        if not self.source_system:
            raise AdapterValidationError("source_system is required")
        if not self.source_event_id:
            raise AdapterValidationError("source_event_id is required")
        if not self.camera_id:
            raise AdapterValidationError("camera_id is required")
        if not self.event_type:
            raise AdapterValidationError("event_type is required")
        if not self.start_time:
            raise AdapterValidationError("start_time is required")

        try:
            start_dt = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
        except ValueError:
            raise AdapterValidationError("start_time must be ISO 8601")

        if self.end_time:
            try:
                end_dt = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
            except ValueError:
                raise AdapterValidationError("end_time must be ISO 8601")

            if end_dt < start_dt:
                raise AdapterValidationError("end_time cannot be earlier than start_time")

        if not self.evidence_references:
            raise AdapterValidationError("At least one evidence reference is required")

        if self.confidence is not None:
            if self.confidence < 0.0 or self.confidence > 1.0:
                raise AdapterValidationError("confidence must be between 0.0 and 1.0")

        if not self.local_processing_required:
            raise AdapterValidationError("local_processing_required must be true")

        for claim in self.capability_claims:
            if claim.lower() in PROHIBITED_CAPABILITIES:
                raise AdapterValidationError(f"Adapter claims prohibited capability: {claim}")

    def to_event(self) -> Event:
        self.validate()
        
        start_dt = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(self.end_time.replace("Z", "+00:00")) if self.end_time else None
        
        clip_uri = self.evidence_references.get("clip_uri") or self.evidence_references.get("clip_path")
        snapshot_uri = self.evidence_references.get("snapshot_uri") or self.evidence_references.get("snapshot_path")

        from safetask.events import HumanReviewStatus, RetentionPolicy

        return Event(
            source_system=self.source_system,
            camera_id=self.camera_id,
            event_id=self.source_event_id,
            event_type=self.event_type,
            start_time=start_dt,
            end_time=end_dt,
            human_review_status=HumanReviewStatus.PENDING,
            retention_policy=RetentionPolicy.TEMPORARY,
            clip_uri=clip_uri,
            snapshot_uri=snapshot_uri,
            confidence=self.confidence
        )
