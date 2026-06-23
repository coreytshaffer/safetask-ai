import unittest
from datetime import datetime
from safetask.events import Event

class TestEventSchema(unittest.TestCase):
    def test_event_instantiation(self):
        """Test that a basic event can be instantiated."""
        now = datetime.now()
        event = Event(
            source_system="frigate",
            camera_id="front_door",
            event_id="12345",
            event_type="person",
            start_time=now,
            human_review_status="pending",
            retention_policy="default",
            confidence=0.92
        )
        self.assertEqual(event.source_system, "frigate")
        self.assertEqual(event.event_type, "person")
        self.assertEqual(event.human_review_status, "pending")
        self.assertEqual(event.confidence, 0.92)

if __name__ == '__main__':
    unittest.main()
