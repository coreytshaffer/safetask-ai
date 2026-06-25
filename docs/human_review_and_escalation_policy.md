# Human Review and Escalation Policy

## Core Principle
**Detection is a claim, not a conclusion.** All automated detections are probabilistic claims about the environment. They hold no authority until validated by a human.

## Strict Restrictions

To prevent mission creep and systemic overreach, the following actions are strictly prohibited in SafeTask:

* No automatic law enforcement notification.
* No automatic EMS/911 calls by default.
* No public broadcast of private detections.

## Review and Escalation Requirements

1. **Review-Gated Escalation**: Escalation must be explicitly user-controlled and review-gated. An authorized human operator must confirm the validity of a claim before any external notification or response is triggered.
2. **Minimal Evidence Retention**: Evidence retention should be aggressively minimized. Short retained clips or frames should only be kept when necessary for incident documentation or emergency response.
3. **Configurable Thresholds**: Review thresholds must be configurable to adapt to specific environments and minimize alert fatigue.
4. **Mandatory Event Context**: Every event sent for review must include:
   * Reason code
   * Source ID
   * Timestamp
   * Confidence (if applicable)
   * Model/version (if applicable)
   * Current review status

## Privacy-Preserving Export Redaction

There is a fundamental difference between internal review evidence and exported evidence. When footage or images are exported from a hazard event, the core rule applies: **Export the hazard, not the bystander.**

* **Default Redaction**: Exported footage must redact nonessential humans, license plates, vehicle identifiers, interiors, screens, and private identifying details by default.
* **Opaque Masking**: Prefer opaque masking or solid privacy blobs over ordinary blur when feasible to prevent reversal or identity exposure.
* **License Plate Rule**: License plates that enter exported frames must be masked by default when not essential. SafeTask may localize a plate-shaped region for redaction, but it must not perform ALPR, OCR, plate-number storage, plate hashing, plate search, vehicle identity tracking, or movement analysis. *Obscure the identifier. Do not extract it.*
* **Marking and Metadata**: Exports must be visibly marked as redacted. SafeTask must record redaction metadata (time, reason, tools used) alongside the export record.
