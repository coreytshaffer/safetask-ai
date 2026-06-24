import json
import os
from dataclasses import dataclass
from typing import Optional, List

from safetask.adapters import AdapterPayload

@dataclass
class DropFolderDryRunResult:
    file_path: str
    status: str
    reason: Optional[str] = None
    normalized_event_id: Optional[str] = None
    source_system: Optional[str] = None
    camera_id: Optional[str] = None
    event_type: Optional[str] = None
    ledger_written: bool = False
    files_moved: bool = False

def dry_run_incoming_folder(folder_path: str) -> List[DropFolderDryRunResult]:
    results = []

    if not os.path.isdir(folder_path):
        return results

    # Get all .json files in deterministic order
    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".json")])

    for filename in files:
        file_path = os.path.join(folder_path, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            payload = AdapterPayload(**data)
            event = payload.to_event()

            result = DropFolderDryRunResult(
                file_path=file_path,
                status="valid",
                normalized_event_id=event.event_id,
                source_system=event.source_system,
                camera_id=event.camera_id,
                event_type=event.event_type
            )
            results.append(result)

        except Exception as e:
            result = DropFolderDryRunResult(
                file_path=file_path,
                status="invalid",
                reason=str(e)
            )
            results.append(result)

    return results

def import_incoming_folder(folder_path: str, ledger: 'EvidenceLedger', commit: bool = False) -> List[DropFolderDryRunResult]:
    from safetask.ledger import ActionType
    results = []

    if not os.path.isdir(folder_path):
        return results

    # Fail early if ledger is malformed or corrupted
    ledger.verify_integrity()

    # Get all .json files in deterministic order
    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".json")])

    for filename in files:
        file_path = os.path.join(folder_path, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            payload = AdapterPayload(**data)
            event = payload.to_event()

            # Check duplicates
            existing_records = ledger.records_for_event(event.event_id)
            is_duplicate = any(r.action_type == ActionType.EVENT_CREATED for r in existing_records)

            if is_duplicate:
                result = DropFolderDryRunResult(
                    file_path=file_path,
                    status="duplicate",
                    reason="Event ID already exists in ledger",
                    normalized_event_id=event.event_id,
                    source_system=event.source_system,
                    camera_id=event.camera_id,
                    event_type=event.event_type
                )
                results.append(result)
                continue

            result = DropFolderDryRunResult(
                file_path=file_path,
                status="valid",
                normalized_event_id=event.event_id,
                source_system=event.source_system,
                camera_id=event.camera_id,
                event_type=event.event_type,
            )

            if commit:
                # Append to ledger
                # We save event as dict
                import dataclasses
                from datetime import datetime

                # Convert event fields that are datetime to isoformat
                payload_to_save = dataclasses.asdict(event)
                payload_to_save['start_time'] = payload_to_save['start_time'].isoformat()
                if payload_to_save['end_time']:
                    payload_to_save['end_time'] = payload_to_save['end_time'].isoformat()

                # Ensure enums are resolved to values
                payload_to_save['human_review_status'] = event.human_review_status.value
                payload_to_save['retention_policy'] = event.retention_policy.value

                ledger.append_record(event.event_id, ActionType.EVENT_CREATED, payload_to_save)
                result.ledger_written = True

            results.append(result)

        except Exception as e:
            result = DropFolderDryRunResult(
                file_path=file_path,
                status="invalid",
                reason=str(e)
            )
            results.append(result)

    return results
