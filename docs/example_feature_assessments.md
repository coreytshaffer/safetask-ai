# Example Feature Assessments

The following examples demonstrate how to apply the Future Feature Evaluation Rubric to proposed additions.

## Rejected Features

These features violate the core doctrine by prioritizing identity or behavior over objective safety conditions.

* **ALPR (Automated License Plate Recognition)** → `reject`
* **Face recognition** → `reject`
* **Suspicious person detection** → `reject`
* **Loitering detection** → `reject`
* **Public live wildlife/hazard map from private cameras** → `reject` or `defer` (High risk of public broadcast of private data)

## Approved Features (Review-Gated)

These features align with the Hazard-First Doctrine because they detect objective physical safety conditions and route them to human review.

* **Hazardous object in roadway lane** → `allow_review_gated_pilot`
* **Flame/smoke detection** → `allow_review_gated_pilot`
* **Bear or mountain lion hazard detection** → `allow_review_gated_pilot`

## Strict Scrutiny Features

* **Person down in roadway or configured hazard zone** → `maybe allow strict review_gated_pilot` (Requires careful design to ensure it detects the *hazard* of being prone in a dangerous zone, without evolving into general behavior or posture tracking.)

## Export Redaction Scenarios

When a review-gated feature generates footage for export, the following redaction rules apply based on the "Export the hazard, not the bystander" doctrine:

* **Wildfire smoke with person in frame** → Export the smoke region; mask the person.
* **Roadway hazard with pedestrian nearby** → Mask the pedestrian unless their exact position is essential to understanding the immediate safety context of the hazard.
* **Bear near driveway with person in background** → Mask the person.
* **Person down in roadway** → Strict case; do not casually expose identity. Preserve enough visual context for emergency review, but avoid unnecessary face/identity details. Mask unrelated bystanders entirely.
