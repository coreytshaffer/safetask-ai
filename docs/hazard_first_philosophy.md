# Hazard-First Safety Doctrine

## Core Doctrine

> SafeTask detects dangerous conditions, not suspicious people.

## Expanded Doctrine

Protect people, their autonomy, and their privacy. Detect hazards and threats to public safety without becoming a behavioral nanny.

This doctrine guides all future work, including flame/smoke detection, roadway obstruction detection, large-wildlife hazard review, and person-down-in-hazard-zone detection.

## Why a Hazard-First Philosophy?

Safety systems often drift into behavior policing due to the nature of surveillance. SafeTask must explicitly counteract this drift.

1. **Autonomy and Privacy are Safety Requirements**: True safety protects individuals from both physical harm and systemic overreach.
2. **Hazards vs. Identities**: SafeTask focuses on the physical state of the environment (e.g., a fire, a flooded walkway, a blocked exit) rather than identifying *who* is in the environment.
3. **Unsafe Conditions vs. Nonconforming Behavior**: SafeTask evaluates the environment for objective threats, not subjective behavioral compliance or social conformity.
4. **Detections are Claims, Not Conclusions**: AI and sensors make probabilistic claims. They do not dictate ground truth.
5. **Human Review is Central**: Because detections are claims, human operators must review and validate them before any escalation occurs.

## Foundational Principles

1. **Detect hazards, not identities.**
2. **Detect unsafe conditions, not nonconforming behavior.**
3. **Treat detections as claims, not conclusions.**
4. **Require human review before escalation.**
5. **Keep sensing local-first where possible.**
6. **Minimize retention by default.**
7. **Make non-goals explicit before adding capability.**

## Building the Successor Pattern

SafeTask is not an attack on existing security systems. It is an attempt to build a different pattern. Many legacy systems grew around real safety needs, but accumulated identity tracking, behavioral control, and escalation habits that can undermine autonomy and trust. SafeTask starts from another premise: protect people by detecting dangerous conditions, preserving evidence integrity, and supporting human review — while refusing to turn ordinary people into surveillance subjects.

## Privacy-Preserving Export Redaction

SafeTask should distinguish between internal review evidence and exported evidence.

When footage or images are exported from a hazard event, any human figure, license plate, interior space, or private identifying detail that is not essential to understanding the hazard should be redacted by default.

For human figures, SafeTask should prefer an opaque mask or solid privacy blob over ordinary blur when feasible. The goal is not cosmetic anonymization; the goal is to prevent unnecessary identity exposure.

**Example:**
If a person appears in the same frame as possible wildfire smoke, and the person is not relevant to the hazard, the exported frame should preserve the smoke region while masking the human figure.

**Design rules:**
* Redact people by default in exported hazard footage.
* Do not use redaction as a reason to add identity detection.
* Do not store face embeddings or identity templates.
* Do not track people across cameras for redaction purposes.
* Preserve only the minimum internal evidence needed for review.
* Make exports visibly marked as redacted.
* Record redaction metadata, such as redaction time, redaction reason, and whether the original remains locally retained.

**Allowed export label examples:**
* `redacted_export`
* `human_masked_nonessential`
* `identity_details_removed`
* `hazard_region_preserved`

**Core rule:**
Export the hazard, not the bystander.
