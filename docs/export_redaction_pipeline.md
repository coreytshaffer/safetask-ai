# Export Redaction Pipeline Architecture

## The Fail-Closed Redaction Flow

SafeTask relies on a strict pipeline for exporting evidence safely. This pipeline operates as a state machine where privacy preservation is a hard gate.

### 1. The Redaction Target Detection Phase
Before an approved hazard claim is exported, the source frame is passed through the redaction engine.
* The engine scans for `human`, `face`, and `license_plate` bounding boxes.
* If targets are found, a `redaction_target_detected` event is logged to the ledger.

### 2. The Masking Phase
The redaction engine attempts to apply a solid, opaque mask over every detected target box.
* The engine must ensure the bounding box expands slightly to encompass all identifying details (e.g., clothing, hair).
* If masking succeeds and does not obscure the primary hazard region, a `redaction_applied` event is logged.

### 3. The Validation and Review Phase
If the redaction engine detects a conflict (e.g., a person is standing *inside* the smoke bounding box) or reports low confidence in the boundaries of the mask, the pipeline halts.
* A `redaction_review_required` event is issued.
* A human operator must manually verify or redraw the mask before the system generates the export file.

### 4. The Fail-Closed Gate
If the engine completely fails to process the image, crashes, or is unable to apply masks due to system errors, the export is strictly blocked.
* A `redaction_failed_export_blocked` event is recorded.
* The image will not be moved to the export directory.
* The system fails closed: **Safety evidence may be useful, but privacy failure blocks sharing.**

## Retention Lifecycle

1. **T=0**: Unredacted source image is stored in local, access-controlled vault.
2. **T+Review**: Operator reviews hazard. If valid, export pipeline initiates. Redacted copy is generated and placed in the shareable export volume.
3. **T+7 Days**: The original, unredacted source image is permanently deleted. Only the redacted export and the ledger metadata remain.

*Note: The explicit JSON schemas for redaction requests, successful export records, and failure events are defined in the `schemas/` directory.*
