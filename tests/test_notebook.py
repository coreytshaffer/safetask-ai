import pytest
from pathlib import Path
import sys

# Ensure src is in the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notebook.db import NotebookDB
from notebook.schema import FieldNote
from notebook.parser import DictationParser

def test_notebook_db(tmp_path):
    db_file = tmp_path / "test_notes.db"
    notes_dir = tmp_path / "notes"
    db = NotebookDB(db_path=str(db_file), notes_dir=str(notes_dir))
    
    note = FieldNote(
        site_id="test_site",
        timestamp="2024-01-01T12:00:00Z",
        notes="Just testing the SQLite DB"
    )
    
    db.insert_note(note)
    
    all_notes = db.get_all_notes()
    assert len(all_notes) == 1
    assert all_notes[0].site_id == "test_site"
    assert all_notes[0].notes == "Just testing the SQLite DB"

def test_dictation_parser_fallback():
    # Test that the parser gracefully falls back if the API is down
    parser = DictationParser(api_url="http://localhost:9999/invalid")
    
    raw_text = "I'm at Clear Lake and it's bad."
    note = parser.parse(raw_text)
    
    # Should fallback to returning the raw text as notes
    assert note.notes == raw_text
    assert note.site_id == "Unknown"
