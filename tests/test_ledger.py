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
        rec1 = self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {"source": "frigate"})
        self.ledger.append_record("evt_1", ActionType.NOTE_ADDED, {"text": "person detected"})
        self.ledger.append_record("evt_1", ActionType.REVIEW_STATUS_CHANGED, {"status": "reviewed"})
        self.ledger.append_record("evt_1", ActionType.NOTE_ADDED, {"text": "all clear"})
        rec5 = self.ledger.append_record("evt_1", ActionType.RETENTION_POLICY_CHANGED, {"policy": "delete_after_review"})

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

    def test_empty_ledger_verification(self):
        self.assertTrue(self.ledger.verify_integrity())

    def test_valid_one_record_chain(self):
        self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {})
        self.assertTrue(self.ledger.verify_integrity())

    def test_valid_multi_record_chain(self):
        self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {})
        self.ledger.append_record("evt_1", ActionType.NOTE_ADDED, {"text": "note"})
        self.ledger.append_record("evt_2", ActionType.EVENT_CREATED, {})
        self.assertTrue(self.ledger.verify_integrity())

    def test_tampered_payload_detection(self):
        self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {"important": "data"})
        self.ledger.append_record("evt_2", ActionType.EVENT_CREATED, {})

        # Tamper payload of the first record
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        record_data = json.loads(lines[0])
        record_data["payload"]["important"] = "tampered"
        lines[0] = json.dumps(record_data) + "\n"

        with open(self.ledger_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        with self.assertRaisesRegex(ValueError, "Payload tampered at record 1"):
            self.ledger.verify_integrity()

    def test_tampered_previous_hash_detection(self):
        self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {})
        self.ledger.append_record("evt_2", ActionType.EVENT_CREATED, {})

        # Tamper previous_hash of the second record
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        record_data = json.loads(lines[1])
        record_data["previous_hash"] = "tampered_hash"

        # Recompute record_hash so payload tamper doesn't fire first
        # We need a proper LedgerRecord to compute hash to strictly trigger previous_hash check
        tampered_record = LedgerRecord.from_json(json.dumps(record_data))
        tampered_record.record_hash = tampered_record.compute_hash()

        lines[1] = tampered_record.to_json() + "\n"

        with open(self.ledger_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        with self.assertRaisesRegex(ValueError, "Hash chain broken at record 2"):
            self.ledger.verify_integrity()

    def test_missing_hash_field_detection(self):
        self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {})

        with open(self.ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        record_data = json.loads(lines[0])
        record_data["record_hash"] = ""
        lines[0] = json.dumps(record_data) + "\n"

        with open(self.ledger_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        with self.assertRaisesRegex(ValueError, "Missing hash fields at record 1"):
            self.ledger.verify_integrity()

if __name__ == '__main__':
    unittest.main()
