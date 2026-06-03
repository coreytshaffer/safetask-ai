import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from logger import logger
from notebook.db import NotebookDB
from notebook.schema import FieldNote


class AnalysisSandbox:
    def __init__(self, db_path: str = "data/field_notes.db", notes_dir: str = "data/notes"):
        self.db = NotebookDB(db_path=db_path, notes_dir=notes_dir)

    def run_script(self, script_path: str) -> Dict[str, Any]:
        path = Path(script_path)
        if not path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        logger.info(f"Preparing sandbox for script: {script_path}")

        # 1. Fetch all data
        notes = self.db.get_all_notes()
        notes_list = []
        for n in notes:
            notes_list.append(
                {
                    "id": n.id,
                    "site_id": n.site_id,
                    "timestamp": n.timestamp,
                    "observer": n.observer,
                    "coordinates": n.coordinates,
                    "notes": n.notes,
                    "confidence_level": n.confidence_level,
                    "evidence_type": n.evidence_type,
                }
            )

        notes_json = json.dumps(notes_list)

        # 2. Setup environment
        env = os.environ.copy()
        env["FIELD_NOTES_JSON"] = notes_json

        # 3. Run script
        logger.info(f"Executing {script_path} in sandbox...")
        cmd = [sys.executable, str(path)]
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Script failed with error:\n{result.stderr}")
            raise RuntimeError(f"Script execution failed: {result.stderr}")

        # 4. Parse stdout for JSON response
        # The script should print a JSON payload as its last line or only output
        # Let's try to find the JSON
        output = result.stdout.strip()

        try:
            # We assume the script outputs exactly one JSON object
            data = json.loads(output)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse script output as JSON. Output:\n{output}")
            raise ValueError(f"Script did not return valid JSON. Output: {output}")

        logger.info(f"Script completed successfully. Result: {data}")

        # 5. Automatically create a new notebook entry from the analysis
        new_note = FieldNote(
            site_id=data.get("site_id", "System Analysis"),
            timestamp=data.get("timestamp", ""),
            observer="AnalysisSandbox",
            notes=data.get("notes", json.dumps(data)),
            confidence_level=data.get("confidence_level", "high"),
            evidence_type="statistical_analysis",
        )

        self.db.insert_note(new_note)
        logger.info(f"Saved analysis result to notebook with ID: {new_note.id}")

        return data
