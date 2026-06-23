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
        record = self.ledger.append_record(
            event_id="evt_123",
            action_type=ActionType.EVENT_CREATED,
            payload={"source": "frigate"}
        )
        self.assertTrue(os.path.exists(self.ledger_path))
        records = self.ledger.read_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].record_id, record.record_id)
        self.assertEqual(records[0].action_type, ActionType.EVENT_CREATED)

    def test_invalid_action_type(self):
        with self.assertRaises(ValueError):
            self.ledger.append_record(
                event_id="evt_123",
                action_type="invalid_action",
                payload={}
            )

    def test_read_multiple_records(self):
        self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {})
        self.ledger.append_record("evt_2", ActionType.EVENT_CREATED, {})
        self.ledger.append_record("evt_1", ActionType.NOTE_ADDED, {"text": "suspicious"})

        records = self.ledger.read_records()
        self.assertEqual(len(records), 3)

    def test_filter_records_by_event(self):
        self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {})
        self.ledger.append_record("evt_2", ActionType.EVENT_CREATED, {})
        self.ledger.append_record("evt_1", ActionType.NOTE_ADDED, {"text": "suspicious"})

        evt_1_records = self.ledger.records_for_event("evt_1")
        self.assertEqual(len(evt_1_records), 2)
        for r in evt_1_records:
            self.assertEqual(r.event_id, "evt_1")

    def test_reconstruct_event_state(self):
        # Create event
        rec1 = self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {"source": "frigate"})
        # Add note
        self.ledger.append_record("evt_1", ActionType.NOTE_ADDED, {"text": "person detected"})
        # Change review status
        self.ledger.append_record("evt_1", ActionType.REVIEW_STATUS_CHANGED, {"status": "reviewed"})
        # Add another note
        self.ledger.append_record("evt_1", ActionType.NOTE_ADDED, {"text": "all clear"})
        # Change retention policy
        rec5 = self.ledger.append_record("evt_1", ActionType.RETENTION_POLICY_CHANGED, {"policy": "delete_after_review"})

        # Interleave another event
        self.ledger.append_record("evt_2", ActionType.EVENT_CREATED, {})

        state = self.ledger.reconstruct_event_state("evt_1")
        self.assertEqual(state.event_id, "evt_1")
        self.assertEqual(state.created_record_id, rec1.record_id)
        self.assertEqual(state.latest_review_status, "reviewed")
        self.assertEqual(state.latest_retention_policy, "delete_after_review")
        self.assertEqual(state.notes, ["person detected", "all clear"])
        self.assertEqual(state.updated_at, rec5.timestamp)

    def test_malformed_ledger_line(self):
        self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {})
        # Corrupt the file
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write("this is not json\n")

        with self.assertRaises(ValueError) as context:
            self.ledger.read_records()
        self.assertIn("Malformed record at line 2", str(context.exception))

    def test_malformed_record_data(self):
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write('{"record_id": "1", "event_id": "evt_1", "action_type": "event_created", "payload": {}}\n')

        with self.assertRaises(ValueError) as context:
            self.ledger.read_records()
        self.assertIn("Malformed record data", str(context.exception))

if __name__ == '__main__':
    unittest.main()
