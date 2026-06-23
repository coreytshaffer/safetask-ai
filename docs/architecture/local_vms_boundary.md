# Local VMS Architecture Boundary

SafeTask is designed to sit **above** the local Video Management System (VMS) or Network Video Recorder (NVR) layer. SafeTask does not directly connect to cameras or stream RTSP feeds; instead, it relies on a local VMS to handle raw video ingestion, recording, and basic event detection.

SafeTask focuses on the **evidence ledger**: human review, notes, tags, retention policies, and situational awareness.

## Architecture Diagram

```text
Cameras
  ↓
Local VMS / NVR
  Frigate / ZoneMinder / Shinobi / Synology / future adapter
  ↓
SafeTask Adapter Layer
  normalized events, clips, metadata
  ↓
SafeTask Evidence Ledger
  human review, notes, tags, retention policy
  ↓
Household Dashboard
  “what happened?”, “what needs review?”, “what can be deleted?”
```

## Possible Future VMS Substrates

| Option                            | Best Use | Notes |
| --------------------------------- | ---: | --- |
| **Frigate**                       | Best likely future fit | Local AI object detection, MQTT, Home Assistant ecosystem, hardware accelerator support. |
| **ZoneMinder**                    | Mature, traditional CCTV/NVR | Full-featured open-source surveillance system, but should be kept private/VPN-only if used. |
| **Shinobi**                       | Lightweight/dev-friendly NVR | Open-source, Node.js-based, performance-oriented NVR. |
| **Synology Surveillance Station** | NAS-native option | Less open, but practical if you use a Synology NAS. |

**Note on VicoHome / VisionWell:**
Existing VicoHome cameras may or may not be usable locally. Treat them as an uncertain future compatibility investigation, not as a current dependency. We will not attempt to bypass vendor camera restrictions or reverse engineer cloud services.

## Adapter Design Note: Future Event Ingestion

To prepare for future VMS integration, SafeTask will ingest a normalized event object with the following schema:
- `source_system`: The origin VMS (e.g., "frigate", "zoneminder")
- `camera_id`: Identifier for the camera
- `event_id`: Unique identifier from the VMS
- `event_type`: The classification (e.g., "person", "motion")
- `start_time`: Timestamp of the event start
- `end_time`: Timestamp of the event end
- `clip_uri` / `clip_path`: Local path or URI to the video clip
- `snapshot_uri` / `snapshot_path`: Local path or URI to the snapshot image
- `confidence`: Optional confidence score (e.g., 0.85)
- `human_review_status`: State of review (e.g., "pending", "reviewed")
- `retention_policy`: Assigned retention rule (e.g., "default", "keep_indefinitely")
