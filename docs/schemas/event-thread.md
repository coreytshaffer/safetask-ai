# SafeTask AI - Event Thread Schema

The **Incident Thread** is the core spatial-temporal event graph object used in SafeTask AI. It groups observations across time and space, associates them with policy, and tracks the review status.

## Incident Thread Object

| Field | Type | Description |
|---|---|---|
| `id` | String | Unique UUID for the incident thread. |
| `type` | String | Domain type: `gaming_surveillance`, `field_safety`, `evacuation`. |
| `date` | String | Creation date of the thread. |
| `inc_date` | String | The actual date/time the incident occurred. |
| `location` | String | Primary location or zone of the incident. |
| `incident_title` | String | Short title of the event. |
| `observations` | Array[Observation] | List of structured observations pinned by the agent. |
| `evidence_references` | Array[Evidence] | Links to exported clips, stills, or SDS sheets. |
| `mobile_evidence_submissions` | Array[MobileEvidenceSubmission] | Security or field-submitted media waiting for or accepted after Surveillance review. |
| `authority_lanes` | Array[String] | Which stakeholders need to review this (e.g. `safety`, `compliance`, `tribal_police`). |
| `jurisdiction_pack` | String | Active regulation pack used for policy hooks, such as `gaming-us-tribal`, `gaming-us-nv`, or `gaming-macau`. |
| `preferred_language` | String | User-facing language tag for drafts, alerts, and policy explanations. |
| `review_status` | String | `draft`, `pending_review`, `approved`, `closed`. |
| `narrative` | String | AI-generated draft narrative (requires review). |
| `reasoning` | String | AI reasoning and policy hooks. |

## Observation Object

| Field | Type | Description |
|---|---|---|
| `id` | String/Int | Unique ID for the observation note. |
| `camera_id` | String | Camera node ID (e.g., `PTZ-42`). |
| `timestamp` | String | Video timestamp of the observation. |
| `location` | String | Contextual location for this specific observation. |
| `text` | String | Human-dictated or typed observation note. |
| `confidence` | String | AI or Human confidence score (e.g., `High`, `Low`). |
| `evidence_quality` | String | Visual quality constraint: `observed`, `partial`, `missing`, `conflicting`. |

## Mobile Evidence Submission

See [evidence-intake-gateway.md](evidence-intake-gateway.md) for the mobile-to-gateway schema. Incident Threads should link gateway submissions by reference and review status; they should not assume a Security mobile upload is already a Surveillance finding.
