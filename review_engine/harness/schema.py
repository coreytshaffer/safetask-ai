from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class RuleTrigger:
    terms: List[str] = field(default_factory=list)
    regex: List[str] = field(default_factory=list)


@dataclass
class PolicyRule:
    id: str
    description: str
    decision: str
    message: str
    trigger: RuleTrigger


@dataclass
class ReviewPacket:
    artifact_name: str
    timestamp: str
    decision_state: str  # allow, warn, require_review, block
    triggered_rules: List[dict]
    input_text: str

    @classmethod
    def create(
        cls,
        artifact_name: str,
        decision_state: str,
        triggered_rules: List[dict],
        input_text: str,
    ):
        return cls(
            artifact_name=artifact_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision_state=decision_state,
            triggered_rules=triggered_rules,
            input_text=input_text,
        )
