import unittest
from safetask.adapters import AdapterPayload, AdapterValidationError
from safetask.events import Event

class TestAdapterPayload(unittest.TestCase):

    def setUp(self):
        self.valid_payload = {
            "adapter_name": "safetask-drop-folder-adapter",
            "adapter_version": "0.1.0",
            "source_system": "drop_folder",
            "source_event_id": "file_12345",
            "camera_id": "driveway_local",
            "event_type": "motion",
            "start_time": "2026-06-23T12:00:00Z",
            "end_time": "2026-06-23T12:01:00Z",
            "evidence_references": {"clip_path": "/local/driveway.mp4"},
            "confidence": 0.95,
            "local_processing_required": True,
            "prohibited_capability_flags": ["no_face_recognition"]
        }

    def test_valid_synthetic_adapter_payload_passes(self):
        payload = AdapterPayload(**self.valid_payload)
        payload.validate() # Should not raise

    def test_missing_required_field_fails(self):
        invalid_payload = dict(self.valid_payload)
        del invalid_payload["source_system"]
        with self.assertRaises(TypeError): # Missing required argument
            AdapterPayload(**invalid_payload)

    def test_empty_required_field_fails(self):
        invalid_payload = dict(self.valid_payload)
        invalid_payload["source_system"] = ""
        payload = AdapterPayload(**invalid_payload)
        with self.assertRaises(AdapterValidationError):
            payload.validate()

    def test_end_time_before_start_time_fails(self):
        invalid_payload = dict(self.valid_payload)
        invalid_payload["end_time"] = "2026-06-23T11:00:00Z"
        payload = AdapterPayload(**invalid_payload)
        with self.assertRaisesRegex(AdapterValidationError, "end_time cannot be earlier than start_time"):
            payload.validate()

    def test_confidence_below_zero_fails(self):
        invalid_payload = dict(self.valid_payload)
        invalid_payload["confidence"] = -0.1
        payload = AdapterPayload(**invalid_payload)
        with self.assertRaisesRegex(AdapterValidationError, "confidence must be between 0.0 and 1.0"):
            payload.validate()

    def test_confidence_above_one_fails(self):
        invalid_payload = dict(self.valid_payload)
        invalid_payload["confidence"] = 1.1
        payload = AdapterPayload(**invalid_payload)
        with self.assertRaisesRegex(AdapterValidationError, "confidence must be between 0.0 and 1.0"):
            payload.validate()

    def test_missing_evidence_reference_fails(self):
        invalid_payload = dict(self.valid_payload)
        invalid_payload["evidence_references"] = {}
        payload = AdapterPayload(**invalid_payload)
        with self.assertRaisesRegex(AdapterValidationError, "At least one evidence reference is required"):
            payload.validate()

    def test_local_processing_required_false_fails(self):
        invalid_payload = dict(self.valid_payload)
        invalid_payload["local_processing_required"] = False
        payload = AdapterPayload(**invalid_payload)
        with self.assertRaisesRegex(AdapterValidationError, "local_processing_required must be true"):
            payload.validate()

    def test_prohibited_capability_claim_fails(self):
        invalid_payload = dict(self.valid_payload)
        invalid_payload["capability_claims"] = ["face_recognition"]
        payload = AdapterPayload(**invalid_payload)
        with self.assertRaisesRegex(AdapterValidationError, "Adapter claims prohibited capability: face_recognition"):
            payload.validate()

    def test_valid_payload_converts_into_event(self):
        payload = AdapterPayload(**self.valid_payload)
        event = payload.to_event()
        self.assertIsInstance(event, Event)
        self.assertEqual(event.source_system, "drop_folder")
        self.assertEqual(event.event_id, "file_12345")
        self.assertEqual(event.camera_id, "driveway_local")
        self.assertEqual(event.event_type, "motion")
        self.assertEqual(event.start_time.isoformat(), "2026-06-23T12:00:00+00:00")
        self.assertEqual(event.confidence, 0.95)
        self.assertEqual(event.clip_uri, "/local/driveway.mp4")
        self.assertEqual(event.end_time.isoformat(), "2026-06-23T12:01:00+00:00")
        self.assertEqual(event.human_review_status, "pending")
        self.assertEqual(event.retention_policy, "temporary")

if __name__ == "__main__":
    unittest.main()
