# Starter Event Taxonomy

This taxonomy outlines the standard event types that SafeTask processes. These events describe safety-condition claims, not identity judgments.

## Core Categories

* **Fire/Smoke Hazard**: Indications of combustion, thermal events, or obscuring smoke.
* **Roadway Obstruction Hazard**: Objects, debris, or vehicles blocking active traffic lanes.
* **Flood/Water Hazard**: Rapid water accumulation, standing water in safe zones, or burst pipes.
* **Access Obstruction Hazard**: Blocked emergency exits, driveways, or critical pathways (e.g., fallen trees).
* **Wildlife Hazard**: Large or dangerous animals entering safety-critical zones.
* **Human Safety Hazard**: High-risk physical conditions affecting individuals (e.g., person prone for an extended period).
* **Ambiguous Hazard Requiring Review**: Anomalies that cannot be clearly classified but indicate physical disruption.
* **System Integrity Hazard**: Internal system events indicating tampering, failure, or data loss.

## Example Event Names

* `possible_flame_review_required`
* `possible_smoke_review_required`
* `hazardous_object_in_roadway_review_required`
* `large_wildlife_hazard_review_required`
* `possible_person_down_in_hazard_zone_review_required`
* `ambiguous_hazard_review_required`
* `source_payload_tampering_detected`

## Export and Redaction Metadata

* `redacted_export_created`
* `human_masked_nonessential`
* `identity_details_removed`
* `hazard_region_preserved`

### Redaction Pipeline States
* `redaction_target_detected`
* `redaction_applied`
* `redaction_review_required`
* `redaction_failed_export_blocked`
