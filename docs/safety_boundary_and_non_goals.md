# Safety Boundary and Non-Goals

SafeTask maintains a strict boundary between objective hazard detection and behavioral surveillance. 

## Disallowed Features

These features fundamentally violate the Hazard-First Doctrine by prioritizing identity, behavioral compliance, or mass surveillance over objective safety. They will not be implemented.

* ALPR / license plate recognition
* Face recognition
* Person re-identification
* Suspicious person classification
* Loitering detection
* Behavioral compliance monitoring
* Movement tracking across cameras
* Public live feeds from private cameras

## Potentially Allowed (Review-Gated)

These features detect objective hazards and unsafe conditions. They are conditionally allowed for development, but they must remain strictly **review-gated**. "Review-gated" means detections are treated as claims requiring human validation, *not* as automatic triggers for escalation.

* Flame or smoke detection
* Hazardous object in roadway lane
* Flooding or standing water
* Blocked driveway or emergency access
* Fallen tree or access obstruction
* Downed utility line indicator
* Large wildlife hazard (e.g., bear or mountain lion in a safety-critical zone)
* Person prone in a configured hazard zone for longer than a prescribed interval

## Privacy-Preserving Export Redaction

Export redaction is a required privacy boundary for any generated hazard footage. While SafeTask may localize human figures or license plates strictly for the purpose of masking them, this capability must **never** be used to justify prohibited identity features. 

Redaction localization does not justify, and will not be used for:
* Face recognition or identity templates
* License plate OCR (ALPR), storage, hashing, or search
* Person or vehicle re-identification and tracking
* Behavioral compliance monitoring

The objective of redaction is entirely subtractive: hide sensitive identifiers to preserve the safety claim without exposing bystanders.
