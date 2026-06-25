import uuid
from datetime import datetime, timezone
from jsonschema.exceptions import ValidationError
from safetask.schema_validation import validate_payload
from safetask.redaction import simulate_redaction_request

def route_flame_smoke_claim(claim_payload: dict, redaction_targets: list = None, export_format: str = "image") -> dict:
    """
    Simulated routing path that validates a hazard claim and routes it through the redaction dry-run stub.
    """
    if redaction_targets is None:
        redaction_targets = []

    # 1. Validate the claim
    validate_payload(claim_payload, 'flame_smoke_claim.schema.json')

    # 2. Confirm review_required is true
    if not claim_payload.get('review_required', False):
        raise ValueError("Claim bypassed review_required constraint. This violates doctrine.")

    # 3. Confirm export_allowed is false before redaction
    if claim_payload.get('export_allowed', False) is True:
        raise ValueError("Claim attempted to set export_allowed=True before redaction. This is prohibited.")

    # For ambiguous claims, it just requires human review and doesn't auto-generate an export request yet
    if claim_payload.get('claim_type') == 'ambiguous_fire_signature':
        return {
            "status": "review_required_no_export",
            "source_event_id": claim_payload.get("source_event_id"),
            "message": "Ambiguous claim requires manual review before any export can be requested."
        }

    # 4. Build a simulated redaction export request
    export_request_id = f"req-{uuid.uuid4().hex[:8]}"
    redaction_request = {
        "schema_version": "1.0",
        "source_event_id": claim_payload.get("source_event_id"),
        "export_request_id": export_request_id,
        "requested_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "request_reason": f"Export evidence for {claim_payload.get('claim_type')}",
        "source_frame_reference": claim_payload.get("frame_reference"),
        "hazard_region_to_preserve": claim_payload.get("hazard_region"),
        "redaction_targets": redaction_targets,
        "export_format": export_format,
        "review_required": True
    }

    # 5. Route through redaction gate
    return simulate_redaction_request(redaction_request)
