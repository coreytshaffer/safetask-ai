import unittest
from datetime import datetime, timedelta
from safetask.ledger import EventReviewState
from safetask.retention import RetentionSweeper

class TestRetentionSweeper(unittest.TestCase):
    def setUp(self):
        self.sweeper = RetentionSweeper(temporary_age_threshold=timedelta(days=7))
        self.now = datetime.now()

    def test_retained_event_not_eligible(self):
        state = EventReviewState(
            event_id="evt_1",
            latest_review_status="reviewed",
            latest_retention_policy="retain",
            updated_at=self.now - timedelta(days=10)
        )
        report = self.sweeper.evaluate(state, current_time=self.now)
        self.assertFalse(report.eligible_for_deletion)
        self.assertEqual(report.reason, "Policy is set to retain.")

    def test_pending_delete_after_review_not_eligible(self):
        state = EventReviewState(
            event_id="evt_2",
            latest_review_status="pending",
            latest_retention_policy="delete_after_review",
            updated_at=self.now - timedelta(days=2)
        )
        report = self.sweeper.evaluate(state, current_time=self.now)
        self.assertFalse(report.eligible_for_deletion)
        self.assertEqual(report.reason, "Pending events are never eligible for deletion.")

    def test_reviewed_delete_after_review_eligible(self):
        state = EventReviewState(
            event_id="evt_3",
            latest_review_status="reviewed",
            latest_retention_policy="delete_after_review",
            updated_at=self.now - timedelta(days=1)
        )
        report = self.sweeper.evaluate(state, current_time=self.now)
        self.assertTrue(report.eligible_for_deletion)
        self.assertEqual(report.reason, "Event has been reviewed or dismissed under delete_after_review policy.")

    def test_dismissed_delete_after_review_eligible(self):
        state = EventReviewState(
            event_id="evt_4",
            latest_review_status="dismissed",
            latest_retention_policy="delete_after_review",
            updated_at=self.now - timedelta(days=1)
        )
        report = self.sweeper.evaluate(state, current_time=self.now)
        self.assertTrue(report.eligible_for_deletion)
        self.assertEqual(report.reason, "Event has been reviewed or dismissed under delete_after_review policy.")

    def test_temporary_event_below_age_threshold_not_eligible(self):
        state = EventReviewState(
            event_id="evt_5",
            latest_review_status="reviewed",
            latest_retention_policy="temporary",
            updated_at=self.now - timedelta(days=6)
        )
        report = self.sweeper.evaluate(state, current_time=self.now)
        self.assertFalse(report.eligible_for_deletion)
        self.assertEqual(report.reason, "Temporary event has not yet exceeded the age threshold.")

    def test_temporary_event_above_age_threshold_eligible(self):
        state = EventReviewState(
            event_id="evt_6",
            latest_review_status="reviewed",
            latest_retention_policy="temporary",
            updated_at=self.now - timedelta(days=8)
        )
        report = self.sweeper.evaluate(state, current_time=self.now)
        self.assertTrue(report.eligible_for_deletion)
        self.assertEqual(report.reason, "Temporary event has exceeded the age threshold.")

    def test_temporary_pending_event_above_age_threshold_not_eligible(self):
        state = EventReviewState(
            event_id="evt_7",
            latest_review_status="pending",
            latest_retention_policy="temporary",
            updated_at=self.now - timedelta(days=8)
        )
        report = self.sweeper.evaluate(state, current_time=self.now)
        self.assertFalse(report.eligible_for_deletion)
        self.assertEqual(report.reason, "Pending events are never eligible for deletion.")

if __name__ == '__main__':
    unittest.main()
