import unittest
from datetime import datetime, timedelta
from safetask.events import Event, HumanReviewStatus, RetentionPolicy

class TestEventSchema(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now()

    def test_event_instantiation(self):
        """Test that a basic event can be instantiated."""
        event = Event(
            source_system="frigate",
            camera_id="front_door",
            event_id="12345",
            event_type="person",
            start_time=self.now,
            human_review_status="pending",
            retention_policy="temporary",
            confidence=0.92
        )
        self.assertEqual(event.source_system, "frigate")
        self.assertEqual(event.event_type, "person")
        self.assertEqual(event.human_review_status, HumanReviewStatus.PENDING)
        self.assertEqual(event.retention_policy, RetentionPolicy.TEMPORARY)
        self.assertEqual(event.confidence, 0.92)

    def test_invalid_human_review_status(self):
        """Test that invalid human review status fails."""
        with self.assertRaises(ValueError):
            Event(
                source_system="frigate",
                camera_id="front_door",
                event_id="12345",
                event_type="person",
                start_time=self.now,
                human_review_status="invalid_status",
                retention_policy="temporary"
            )

    def test_invalid_retention_policy(self):
        """Test that invalid retention policy fails."""
        with self.assertRaises(ValueError):
            Event(
                source_system="frigate",
                camera_id="front_door",
                event_id="12345",
                event_type="person",
                start_time=self.now,
                human_review_status="pending",
                retention_policy="invalid_policy"
            )

    def test_end_time_before_start_time(self):
        """Test that end_time cannot be earlier than start_time."""
        with self.assertRaises(ValueError):
            Event(
                source_system="frigate",
                camera_id="front_door",
                event_id="12345",
                event_type="person",
                start_time=self.now,
                human_review_status="pending",
                retention_policy="temporary",
                end_time=self.now - timedelta(seconds=1)
            )

    def test_invalid_confidence(self):
        """Test that confidence must be between 0.0 and 1.0."""
        with self.assertRaises(ValueError):
            Event(
                source_system="frigate",
                camera_id="front_door",
                event_id="12345",
                event_type="person",
                start_time=self.now,
                human_review_status="pending",
                retention_policy="temporary",
                confidence=1.5
            )

        with self.assertRaises(ValueError):
            Event(
                source_system="frigate",
                camera_id="front_door",
                event_id="12345",
                event_type="person",
                start_time=self.now,
                human_review_status="pending",
                retention_policy="temporary",
                confidence=-0.1
            )

    def test_serialization_deserialization(self):
        """Test JSON serialization and deserialization."""
        event = Event(
            source_system="frigate",
            camera_id="front_door",
            event_id="12345",
            event_type="person",
            start_time=self.now,
            human_review_status=HumanReviewStatus.PENDING,
            retention_policy=RetentionPolicy.TEMPORARY,
            end_time=self.now + timedelta(seconds=10),
            clip_uri="/clips/12345.mp4",
            confidence=0.85
        )
        json_str = event.to_json()
        deserialized_event = Event.from_json(json_str)

        self.assertEqual(event.source_system, deserialized_event.source_system)
        self.assertEqual(event.camera_id, deserialized_event.camera_id)
        self.assertEqual(event.event_id, deserialized_event.event_id)
        self.assertEqual(event.start_time, deserialized_event.start_time)
        self.assertEqual(event.end_time, deserialized_event.end_time)
        self.assertEqual(event.human_review_status, deserialized_event.human_review_status)
        self.assertEqual(event.retention_policy, deserialized_event.retention_policy)
        self.assertEqual(event.clip_uri, deserialized_event.clip_uri)
        self.assertEqual(event.confidence, deserialized_event.confidence)

if __name__ == '__main__':
    unittest.main()
