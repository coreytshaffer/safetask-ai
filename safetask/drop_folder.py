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
