# Flame/Smoke Module Design Assessment

## Overview

The Flame/Smoke detection module acts as the first candidate visual hazard detector for SafeTask. This document assesses its boundaries and formalizes its operational design under the Hazard-First Doctrine.

## Goal and Scope

* **Goal**: Detect early signs of outdoor or large-volume combustion (flame or smoke) that present an objective hazard to physical safety.
* **Scope Limits**: The module must only identify regions of the frame containing fire or smoke. It will not attempt to identify the cause of the fire if that cause involves human identity or vehicle recognition.

## Privacy-Preserving Constraints

1. **Static-Image Initial Scope**: To bypass the complexities of identity tracking and temporal blob masking in video footage, the initial implementation of the module will **only permit still-image exports**. If a hazard is detected, a single representative frame is extracted, redacted, and exported. Video clip export is deferred until stateless video redaction is mature.
2. **Fail-Closed Export**: If the system detects a human figure, face, or license plate in the frame, but the redaction engine fails to confidently apply a solid privacy mask, the export is **blocked**. The original evidence remains locally retained for internal review but cannot be shared.
3. **Internal Retention Horizon**: Unredacted source evidence captured by this module will be stored locally for initial operator review, but it will be automatically purged **7 days** after capture to prevent the buildup of a surveillance archive.

## Conceptual Input / Output Schemas

*Note: Formal JSON schemas for these payloads are located in the `schemas/` directory (`flame_smoke_claim.schema.json`).*

### Input Payload (from Drop Folder or VMS)
```json
{
  "source_event_id": "cam01-20260625-101422",
  "camera_id": "cam01-north-drive",
  "timestamp": "2026-06-25T17:14:22Z",
  "media_path": "/safezone/incoming/cam01-20260625-101422.jpg"
}
```

### Output Claim (Detection Engine to Ledger)
```json
{
  "event_type": "possible_flame_review_required",
  "source_event_id": "cam01-20260625-101422",
  "confidence": 0.89,
  "hazard_regions": [
    {"bbox": [150, 300, 250, 450], "label": "flame"}
  ],
  "review_status": "pending"
}
```
