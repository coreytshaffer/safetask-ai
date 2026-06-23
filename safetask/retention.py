from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from safetask.ledger import EventReviewState

@dataclass
class RetentionReport:
    event_id: str
    current_review_status: str
    retention_policy: str
    eligible_for_deletion: bool
    reason: str
    evidence_references: List[str] = field(default_factory=list)

class RetentionSweeper:
    def __init__(self, temporary_age_threshold: timedelta = timedelta(days=7)):
        self.temporary_age_threshold = temporary_age_threshold

    def evaluate(self, state: EventReviewState, current_time: Optional[datetime] = None) -> RetentionReport:
        if current_time is None:
            current_time = datetime.now()

        is_pending = state.latest_review_status == "pending"

        # Pending events are never eligible for deletion
        if is_pending:
            return RetentionReport(
                event_id=state.event_id,
                current_review_status=state.latest_review_status,
                retention_policy=state.latest_retention_policy,
                eligible_for_deletion=False,
                reason="Pending events are never eligible for deletion."
            )

        if state.latest_retention_policy == "retain":
            return RetentionReport(
                event_id=state.event_id,
                current_review_status=state.latest_review_status,
                retention_policy=state.latest_retention_policy,
                eligible_for_deletion=False,
                reason="Policy is set to retain."
            )

        if state.latest_retention_policy == "delete_after_review":
            if state.latest_review_status in ("reviewed", "dismissed"):
                return RetentionReport(
                    event_id=state.event_id,
                    current_review_status=state.latest_review_status,
                    retention_policy=state.latest_retention_policy,
                    eligible_for_deletion=True,
                    reason="Event has been reviewed or dismissed under delete_after_review policy."
                )

        if state.latest_retention_policy == "temporary":
            # For temporary events, check if age threshold is passed based on the updated_at timestamp.
            event_time = state.updated_at or current_time
            if current_time - event_time > self.temporary_age_threshold:
                return RetentionReport(
                    event_id=state.event_id,
                    current_review_status=state.latest_review_status,
                    retention_policy=state.latest_retention_policy,
                    eligible_for_deletion=True,
                    reason="Temporary event has exceeded the age threshold."
                )
            else:
                return RetentionReport(
                    event_id=state.event_id,
                    current_review_status=state.latest_review_status,
                    retention_policy=state.latest_retention_policy,
                    eligible_for_deletion=False,
                    reason="Temporary event has not yet exceeded the age threshold."
                )

        return RetentionReport(
            event_id=state.event_id,
            current_review_status=state.latest_review_status,
            retention_policy=state.latest_retention_policy,
            eligible_for_deletion=False,
            reason="Unrecognized retention policy or state."
        )
