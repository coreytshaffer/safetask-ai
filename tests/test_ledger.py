import json
import os
import tempfile
import unittest
from datetime import datetime
from safetask.ledger import EvidenceLedger, ActionType, LedgerRecord

class TestEvidenceLedger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ledger_path = os.path.join(self.temp_dir.name, "ledger.jsonl")
        self.ledger = EvidenceLedger(self.ledger_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_append_record_success(self):
        """Test that a valid record appends correctly."""
        record = self.ledger.append_record(
            event_id="evt_123",
            action_type=ActionType.EVENT_CREATED,
            payload={"source": "frigate"}
        )
        
        self.assertTrue(os.path.exists(self.ledger_path))
        
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        self.assertEqual(len(lines), 1)
        loaded_record = LedgerRecord.from_json(lines[0])
        
        self.assertEqual(loaded_record.record_id, record.record_id)
        self.assertEqual(loaded_record.event_id, "evt_123")
        self.assertEqual(loaded_record.action_type, ActionType.EVENT_CREATED)
        self.assertEqual(loaded_record.payload, {"source": "frigate"})

    def test_append_multiple_records(self):
        """Test appending multiple records."""
        self.ledger.append_record("evt_1", "event_created", {})
        self.ledger.append_record("evt_1", "note_added", {"text": "suspicious"})
        self.ledger.append_record("evt_1", "review_status_changed", {"status": "reviewed"})
        
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        self.assertEqual(len(lines), 3)

    def test_invalid_action_type(self):
        """Test that an invalid action type raises an error."""
        with self.assertRaises(ValueError):
            self.ledger.append_record(
                event_id="evt_123",
                action_type="invalid_action",
                payload={}
            )
            
    def test_ledger_record_validation(self):
        """Test that LedgerRecord validates action_type upon instantiation."""
        with self.assertRaises(ValueError):
            LedgerRecord(
                timestamp=datetime.now(),
                record_id="rec_1",
                event_id="evt_1",
                action_type="bad_type",
                payload={}
            )

if __name__ == '__main__':
    unittest.main()
