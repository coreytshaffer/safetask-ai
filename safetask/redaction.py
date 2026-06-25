import uuid
from datetime import datetime, timezone
from safetask.schema_validation import validate_payload
from safetask.renderer import apply_redaction_masks

def simulate_redaction_request(request_payload, input_image_path=None, output_image_path=None):
    """
    Dry-run stub for redaction engine.
    Validates request, checks for unsupported targets, and returns either a
    redaction_export_record or a redaction_failure_event.
    """
    # 1. Validate request
    validate_payload(request_payload, 'redaction_export_request.schema.json')
    
    export_request_id = request_payload.get('export_request_id')
    source_event_id = request_payload.get('source_event_id')
    
    # 2. Check for video export (currently unsupported in this prototype)
    if request_payload.get('export_format') == 'video':
        return _build_failure_event(
            export_request_id, 
            source_event_id, 
            "Video export is currently unsupported. Redaction engine handles still images only."
        )

    # 3. Check for unsupported targets
    # For the stub, we explicitly support 'human_figure', 'face_region', 'license_plate_region', 'vehicle_identifier'
    supported_targets = {'human_figure', 'face_region', 'license_plate_region', 'vehicle_identifier'}
    targets = request_payload.get('redaction_targets', [])
    for target in targets:
        target_type = target.get('target_type')
        if target_type not in supported_targets:
            return _build_failure_event(
                export_request_id,
                source_event_id,
                f"Unsupported redaction target type: {target_type}"
            )
            
    # 4. Optional Rendering
    if input_image_path and output_image_path:
        try:
            apply_redaction_masks(input_image_path, output_image_path, targets)
        except Exception as e:
            return _build_failure_event(
                export_request_id,
                source_event_id,
                f"Redaction rendering failed: {e}"
            )

    # 5. Success path (simulated)
    record = {
        "schema_version": "1.0",
        "export_request_id": export_request_id,
        "source_event_id": source_event_id,
        "redacted_export_id": f"sim-exp-{uuid.uuid4().hex[:8]}",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "redaction_status": "redaction_applied",
        "export_allowed": True,
        "redacted_frame_reference": f"simulated://redacted-export/{export_request_id}-redacted",
        "redaction_summary": f"Simulated masking of {len(targets)} regions.",
        "hazard_region_preserved": request_payload.get('hazard_region_to_preserve'),
        "original_retention_until": "2026-07-02T00:00:00Z", # Mocked
        "review_status": "approved"
    }
    
    validate_payload(record, 'redaction_export_record.schema.json')
    return record


def _build_failure_event(export_request_id, source_event_id, reason):
    event = {
        "schema_version": "1.0",
        "export_request_id": export_request_id,
        "source_event_id": source_event_id,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "redaction_status": "redaction_failed_export_blocked",
        "failure_reason": reason,
        "export_allowed": False,
        "required_human_review": True,
        "source_frame_retention_until": "2026-07-02T00:00:00Z"
    }
    validate_payload(event, 'redaction_failure_event.schema.json')
    return event
