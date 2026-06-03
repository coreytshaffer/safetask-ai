import pytest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis.sandbox import AnalysisSandbox
from notebook.schema import FieldNote

def test_sandbox_execution(tmp_path):
    # Setup test DB
    db_path = tmp_path / "test_notes.db"
    notes_dir = tmp_path / "notes"
    sandbox = AnalysisSandbox(db_path=str(db_path), notes_dir=str(notes_dir))
    
    # Insert some dummy notes
    note1 = FieldNote(site_id="Site A", timestamp="2026-06-01T10:00:00Z", notes="Bird spotted")
    note2 = FieldNote(site_id="Site A", timestamp="2026-06-01T11:00:00Z", notes="Another bird")
    note3 = FieldNote(site_id="Site B", timestamp="2026-06-01T12:00:00Z", notes="Fish")
    
    sandbox.db.insert_note(note1)
    sandbox.db.insert_note(note2)
    sandbox.db.insert_note(note3)
    
    # Create a dummy script that mimics what we want
    script_path = tmp_path / "dummy_script.py"
    script_content = """
import os
import json
import sys

def main():
    notes_json = os.environ.get("FIELD_NOTES_JSON", "[]")
    data = json.loads(notes_json)
    
    # Calculate simple stats
    counts = {}
    for note in data:
        site = note.get("site_id", "Unknown")
        counts[site] = counts.get(site, 0) + 1
        
    result = {
        "site_id": "System Analysis Test",
        "timestamp": "2026-06-01T13:00:00Z",
        "notes": f"Counts: {json.dumps(counts)}",
        "confidence_level": "high"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
"""
    with open(script_path, "w") as f:
        f.write(script_content)
        
    # Run sandbox
    res = sandbox.run_script(str(script_path))
    
    # Validate result dictionary
    assert res["site_id"] == "System Analysis Test"
    assert "Site A" in res["notes"]
    
    # Validate it was inserted into NotebookDB
    all_notes = sandbox.db.get_all_notes()
    assert len(all_notes) == 4
    
    # The last note should be our generated one
    gen_note = all_notes[-1]
    assert gen_note.observer == "AnalysisSandbox"
    assert gen_note.site_id == "System Analysis Test"
    assert "Site A" in gen_note.notes
