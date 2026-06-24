import os
import tempfile
import unittest
import json
from safetask.drop_folder import dry_run_incoming_folder

class TestDropFolder(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.incoming_dir = os.path.join(self.temp_dir.name, "incoming")
        os.makedirs(self.incoming_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_empty_folder(self):
        results = dry_run_incoming_folder(self.incoming_dir)
        self.assertEqual(len(results), 0)

    def test_valid_payload(self):
        payload = {
            "adapter_name": "test-adapter",
            "adapter_version": "1.0",
            "source_system": "drop_folder",
            "source_event_id": "test_evt_1",
            "camera_id": "cam_1",
            "event_type": "motion",
            "start_time": "2026-06-23T12:00:00Z",
            "evidence_references": {"clip_path": "/clip.mp4"},
            "local_processing_required": True
        }
        with open(os.path.join(self.incoming_dir, "001.json"), "w") as f:
            json.dump(payload, f)

        results = dry_run_incoming_folder(self.incoming_dir)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, "valid")
        self.assertEqual(results[0].normalized_event_id, "test_evt_1")
        self.assertFalse(results[0].ledger_written)
        self.assertFalse(results[0].files_moved)

    def test_invalid_payload(self):
        payload = {
            "adapter_name": "test-adapter",
            "adapter_version": "1.0",
            "source_system": "drop_folder",
            "source_event_id": "test_evt_1",
            "camera_id": "cam_1",
            "event_type": "motion",
            "start_time": "2026-06-23T12:00:00Z",
            "evidence_references": {"clip_path": "/clip.mp4"},
            "local_processing_required": True,
            "capability_claims": ["face_recognition"]
        }
        with open(os.path.join(self.incoming_dir, "002.json"), "w") as f:
            json.dump(payload, f)

        results = dry_run_incoming_folder(self.incoming_dir)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, "invalid")
        self.assertIn("prohibited capability", results[0].reason)

    def test_non_json_files_ignored(self):
        with open(os.path.join(self.incoming_dir, "ignore.txt"), "w") as f:
            f.write("hello")

        results = dry_run_incoming_folder(self.incoming_dir)
        self.assertEqual(len(results), 0)

    def test_deterministic_sorting(self):
        # Create b.json and then a.json
        with open(os.path.join(self.incoming_dir, "b.json"), "w") as f:
            json.dump({"start_time": "1"}, f)
        with open(os.path.join(self.incoming_dir, "a.json"), "w") as f:
            json.dump({"start_time": "2"}, f)

        results = dry_run_incoming_folder(self.incoming_dir)
        self.assertEqual(len(results), 2)
        # Check that file paths end with a.json and b.json in order
        self.assertTrue(results[0].file_path.endswith("a.json"))
        self.assertTrue(results[1].file_path.endswith("b.json"))

    def test_import_incoming_folder_dry_run(self):
        from safetask.ledger import EvidenceLedger
        ledger_path = os.path.join(self.temp_dir.name, "ledger.jsonl")
        ledger = EvidenceLedger(ledger_path)

        payload = {
            "adapter_name": "test", "adapter_version": "1.0", "source_system": "drop_folder",
            "source_event_id": "test_1", "camera_id": "cam_1", "event_type": "motion",
            "start_time": "2026-06-23T12:00:00Z", "evidence_references": {"clip_path": "/clip.mp4"},
            "local_processing_required": True
        }
        with open(os.path.join(self.incoming_dir, "001.json"), "w") as f:
            json.dump(payload, f)

        from safetask.drop_folder import import_incoming_folder
        results = import_incoming_folder(self.incoming_dir, ledger, commit=False)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, "valid")
        self.assertFalse(results[0].ledger_written)
        self.assertEqual(len(ledger.read_records()), 0)

    def test_import_incoming_folder_commit(self):
        from safetask.ledger import EvidenceLedger
        ledger_path = os.path.join(self.temp_dir.name, "ledger.jsonl")
        ledger = EvidenceLedger(ledger_path)

        payload = {
            "adapter_name": "test", "adapter_version": "1.0", "source_system": "drop_folder",
            "source_event_id": "test_1", "camera_id": "cam_1", "event_type": "motion",
            "start_time": "2026-06-23T12:00:00Z", "evidence_references": {"clip_path": "/clip.mp4"},
            "local_processing_required": True
        }
        with open(os.path.join(self.incoming_dir, "001.json"), "w") as f:
            json.dump(payload, f)

        from safetask.drop_folder import import_incoming_folder
        results = import_incoming_folder(self.incoming_dir, ledger, commit=True)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].ledger_written)
        self.assertEqual(len(ledger.read_records()), 1)
        self.assertEqual(ledger.read_records()[0].action_type, "event_created")
        self.assertTrue(ledger.verify_integrity())

    def test_import_incoming_folder_duplicate_check(self):
        from safetask.ledger import EvidenceLedger, ActionType
        ledger_path = os.path.join(self.temp_dir.name, "ledger.jsonl")
        ledger = EvidenceLedger(ledger_path)
        ledger.append_record("test_1", ActionType.EVENT_CREATED, {})

        payload = {
            "adapter_name": "test", "adapter_version": "1.0", "source_system": "drop_folder",
            "source_event_id": "test_1", "camera_id": "cam_1", "event_type": "motion",
            "start_time": "2026-06-23T12:00:00Z", "evidence_references": {"clip_path": "/clip.mp4"},
            "local_processing_required": True
        }
        with open(os.path.join(self.incoming_dir, "001.json"), "w") as f:
            json.dump(payload, f)

        from safetask.drop_folder import import_incoming_folder
        results = import_incoming_folder(self.incoming_dir, ledger, commit=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, "duplicate")
        self.assertFalse(results[0].ledger_written)
        self.assertEqual(len(ledger.read_records()), 1)

    def test_import_incoming_folder_malformed_ledger(self):
        from safetask.ledger import EvidenceLedger
        ledger_path = os.path.join(self.temp_dir.name, "ledger.jsonl")
        with open(ledger_path, "w") as f:
            f.write("not a json\n")

        ledger = EvidenceLedger(ledger_path)

        payload = {
            "adapter_name": "test", "adapter_version": "1.0", "source_system": "drop_folder",
            "source_event_id": "test_1", "camera_id": "cam_1", "event_type": "motion",
            "start_time": "2026-06-23T12:00:00Z", "evidence_references": {"clip_path": "/clip.mp4"},
            "local_processing_required": True
        }
        with open(os.path.join(self.incoming_dir, "001.json"), "w") as f:
            json.dump(payload, f)

        from safetask.drop_folder import import_incoming_folder
        with self.assertRaises(ValueError):
            import_incoming_folder(self.incoming_dir, ledger, commit=True)

    def test_import_incoming_folder_empty(self):
        from safetask.ledger import EvidenceLedger
        ledger_path = os.path.join(self.temp_dir.name, "ledger.jsonl")
        ledger = EvidenceLedger(ledger_path)

        from safetask.drop_folder import import_incoming_folder
        results = import_incoming_folder(self.incoming_dir, ledger, commit=True)
        self.assertEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main()
