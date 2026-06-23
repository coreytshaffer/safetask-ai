import os
import tempfile
import unittest
import subprocess
from safetask.ledger import EvidenceLedger

class TestDemoGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ledger_path = os.path.join(self.temp_dir.name, "demo_evidence.jsonl")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_demo_ledger_generation_and_verification(self):
        script_path = os.path.join(os.path.dirname(__file__), "..", "examples", "create_demo_ledger.py")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        try:
            subprocess.run(["python", script_path, "--output", self.ledger_path], env=env, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Demo generator failed. STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")
            raise

        self.assertTrue(os.path.exists(self.ledger_path))

        ledger = EvidenceLedger(self.ledger_path)

        self.assertTrue(ledger.verify_integrity())

        state = ledger.reconstruct_event_state("demo_evt_001")
        self.assertEqual(state.event_id, "demo_evt_001")
        self.assertEqual(state.latest_review_status, "dismissed")
        self.assertEqual(state.latest_retention_policy, "delete_after_review")
        self.assertTrue(len(state.notes) > 0)

if __name__ == '__main__':
    unittest.main()
