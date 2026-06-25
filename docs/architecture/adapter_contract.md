# Adapter Contract Design

To protect SafeTask's ethical boundaries and local-first architecture, any future Video Management System (VMS) or Network Video Recorder (NVR) adapter must strictly adhere to this Adapter Contract. Adapters that violate these invariants will be rejected by the SafeTask normalization layer.

## The Adapter Boundary Payload

Before SafeTask accepts an event into its ledger, the adapter must provide a normalized payload matching this schema:

- `adapter_name`: String (e.g., "safetask-frigate-adapter")
- `adapter_version`: String (e.g., "1.0.0")
- `source_system`: String (e.g., "frigate", "zoneminder", "drop_folder")
- `source_event_id`: String (The original ID from the VMS)
- `camera_id`: String
- `event_type`: String (e.g., "person", "motion")
- `start_time`: ISO 8601 Timestamp
- `end_time`: ISO 8601 Timestamp (optional if event is ongoing)
- `evidence_references`: Dictionary of local paths or URIs (e.g., `clip_path`, `clip_uri`, `snapshot_path`, `snapshot_uri`)
- `confidence`: Float (optional, e.g., 0.85)
- `local_processing_required`: Boolean (Must be `True` to confirm the event was processed locally)
- `prohibited_capability_flags`: List of strings explicitly enumerating what the event does *not* contain (must match invariants below).

## Adapter Invariants

SafeTask requires active attestation that adapters are not performing prohibited actions.
- Adapters **must not claim** face recognition.
- Adapters **must not claim** ALPR (Automated License Plate Recognition).
- Adapters **must not claim** biometric identification.
- Adapters **must not claim** weapon detection.
- Adapters **must not trigger** law-enforcement workflows.
- Adapters **must not auto-escalate** events.
- Adapters **must not require** cloud processing.
- Adapters **must not create** deletion actions (retention is handled exclusively by SafeTask).
- Adapters **must produce** human-reviewable events only.

## Compatibility Expectations

SafeTask is designed to eventually accept normalized payloads from:
- **Local event sources**: MQTT or webhook-based local AI detection.
- **Traditional event sources**: CCTV event logs.
- **Generic file/drop-folder sources**: Scripts watching a local folder for MP4s/JPGs.

## Synthetic Adapter Payload Example

Below is a valid example of what an adapter would submit to SafeTask for normalization:

```json
{
  "adapter_name": "safetask-drop-folder-adapter",
  "adapter_version": "0.1.0",
  "source_system": "drop_folder",
  "source_event_id": "file_12345",
  "camera_id": "driveway_local",
  "event_type": "motion",
  "start_time": "2026-06-23T12:00:00Z",
  "end_time": "2026-06-23T12:01:00Z",
  "evidence_references": {
    "clip_path": "/local/storage/driveway_12345.mp4",
    "snapshot_path": "/local/storage/driveway_12345.jpg"
  },
  "confidence": 0.95,
  "local_processing_required": true,
  "prohibited_capability_flags": [
    "no_face_recognition",
    "no_alpr",
    "no_biometrics",
    "no_weapon_detection",
    "no_law_enforcement_workflow",
    "no_auto_escalation",
    "no_cloud"
  ]
}
```

## Mapping to the SafeTask Event Schema

Once the adapter contract validates the incoming payload, the SafeTask normalization layer will map it directly to the internal `safetask.events.Event` envelope:

| Adapter Payload | SafeTask `Event` Envelope |
|---|---|
| `source_event_id` | `source_id` |
| `source_system` | `source_system` |
| `camera_id` | `camera_id` |
| `event_type` | `event_type` |
| `start_time` | `timestamp` |
| `end_time` | (Parsed into `metadata` or used for duration logic) |
| `confidence` | `confidence` |
| `evidence_references` | Extracted or linked locally (future `metadata` integration) |
| (Derived) | `human_review_status` defaults to `"pending"` |
| (Derived) | `retention_policy` defaults to `"default"` |
