import os
import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stdout
from safetask.cli import main
from safetask.ledger import EvidenceLedger, ActionType

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ledger_path = os.path.join(self.temp_dir.name, "ledger.jsonl")
        self.ledger = EvidenceLedger(self.ledger_path)
        self.ledger.append_record("evt_1", ActionType.EVENT_CREATED, {"source": "cli_test"})

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, *args):
        out = StringIO()
        with redirect_stdout(out):
            main(list(args))
        return out.getvalue()

    def test_verify_ledger(self):
        output = self.run_cli("verify-ledger", "--ledger", self.ledger_path)
        self.assertIn("Ledger integrity verified.", output)

    def test_add_note(self):
        output = self.run_cli("add-note", "--ledger", self.ledger_path, "--event-id", "evt_1", "--note", "hello world")
        self.assertIn("Note added to event evt_1.", output)

        state = self.ledger.reconstruct_event_state("evt_1")
        self.assertIn("hello world", state.notes)

    def test_review_state(self):
        self.run_cli("add-note", "--ledger", self.ledger_path, "--event-id", "evt_1", "--note", "cli note")
        output = self.run_cli("review-state", "--ledger", self.ledger_path, "--event-id", "evt_1")
        self.assertIn("Event ID: evt_1", output)
        self.assertIn("Review Status: pending", output)
        self.assertIn("cli note", output)

    def test_set_review_status(self):
        output = self.run_cli("set-review-status", "--ledger", self.ledger_path, "--event-id", "evt_1", "--status", "reviewed")
        self.assertIn("Review status of event evt_1 set to reviewed.", output)

        state = self.ledger.reconstruct_event_state("evt_1")
        self.assertEqual(state.latest_review_status, "reviewed")

    def test_set_retention_policy(self):
        output = self.run_cli("set-retention-policy", "--ledger", self.ledger_path, "--event-id", "evt_1", "--policy", "retain")
        self.assertIn("Retention policy of event evt_1 set to retain.", output)

        state = self.ledger.reconstruct_event_state("evt_1")
        self.assertEqual(state.latest_retention_policy, "retain")

    def test_retention_dry_run(self):
        self.run_cli("set-review-status", "--ledger", self.ledger_path, "--event-id", "evt_1", "--status", "reviewed")
        self.run_cli("set-retention-policy", "--ledger", self.ledger_path, "--event-id", "evt_1", "--policy", "delete_after_review")

        output = self.run_cli("retention-dry-run", "--ledger", self.ledger_path, "--event-id", "evt_1")
        self.assertIn("Eligible for Deletion: True", output)

if __name__ == "__main__":
    unittest.main()
