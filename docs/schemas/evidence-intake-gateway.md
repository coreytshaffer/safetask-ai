# SafeTask AI - Evidence Intake Gateway

The Evidence Intake Gateway is a middle layer between Security mobile capture and Surveillance review. Mobile devices should not send files directly into the surveillance VLAN or directly into final incident findings.

## Intake Flow

```text
Security mobile app
-> Evidence Intake Gateway
-> quarantine, validation, hash, metadata, and access checks
-> Surveillance review queue
-> Incident Thread and Evidence Registry
-> approved report packet
```

## Mobile Evidence Submission Object

| Field | Type | Description |
|---|---|---|
| `id` | String | Unique submission ID. |
| `temporary_case_id` | String | Field case ID before linkage to a SafeTask Incident Thread. |
| `incident_thread_id` | String | Optional linked Incident Thread ID after review. |
| `submitted_by_role` | String | Role such as `security_officer` or `security_supervisor`. |
| `submitted_by_id` | String | Authenticated user or badge ID, if allowed by policy. |
| `device_id` | String | Registered mobile device identifier. |
| `submitted_at` | String | Gateway receipt timestamp. |
| `captured_at` | String | Capture timestamp from the mobile device. |
| `location` | String | Zone, property area, or GPS/indoor location if policy allows it. |
| `media_type` | String | `photo`, `video`, `audio`, or `document`. |
| `file_reference` | String | Gateway-managed storage reference, not a direct surveillance VLAN path. |
| `sha256` | String | File hash calculated by the gateway. |
| `notes` | String | Security-submitted field note. |
| `status` | String | `submitted`, `quarantined`, `validated`, `pending_surveillance_review`, `accepted`, `rejected`, or `linked`. |
| `authority_lanes` | Array[String] | Review lanes such as `security`, `surveillance`, `safety`, `compliance`, or `legal_risk`. |

## Gateway Controls

- Authenticated uploads only.
- Encryption in transit and at rest.
- File type validation and malware scanning before Surveillance opens files.
- Hashing and immutable-style intake log at receipt.
- No direct write into VMS storage.
- Thumbnail or proxy generation for review when appropriate.
- Role-based release into the Surveillance review queue.
- Field submissions are labeled `Submitted by Security - Pending Surveillance Review` until accepted.

## Authority Boundary

Security can submit observations and media. Surveillance reviews and links evidence to camera context. Authorized stakeholders approve conclusions. The gateway should preserve submitted evidence and metadata without turning a mobile upload into a final surveillance finding.
