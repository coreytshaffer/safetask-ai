import re
from pathlib import Path
from typing import List, Tuple

import yaml

from .schema import PolicyRule, ReviewPacket, RuleTrigger


class CyberneticHarness:
    def __init__(self, policy_dir: str):
        self.policy_dir = Path(policy_dir)
        self.rules: List[PolicyRule] = []
        self.load_policies()

    def load_policies(self):
        """Loads all YAML policies from the policy directory."""
        if not self.policy_dir.exists():
            return

        for filepath in self.policy_dir.glob("*.yaml"):
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if "rules" in data:
                    for r in data["rules"]:
                        trigger_data = r.get("trigger", {})
                        trigger = RuleTrigger(
                            terms=trigger_data.get("terms", []),
                            regex=trigger_data.get("regex", []),
                        )
                        rule = PolicyRule(
                            id=r["id"],
                            description=r["description"],
                            decision=r["decision"].lower(),
                            message=r["message"],
                            trigger=trigger,
                        )
                        self.rules.append(rule)

    def evaluate(self, text: str, artifact_name: str = "text_input") -> ReviewPacket:
        """Evaluates input text against all loaded rules."""
        triggered = []
        text_lower = text.lower()

        highest_severity = "allow"
        severity_rank = {"allow": 0, "warn": 1, "require_review": 2, "block": 3}

        for rule in self.rules:
            is_triggered = False

            # Check terms
            for term in rule.trigger.terms:
                if term.lower() in text_lower:
                    is_triggered = True
                    break

            # Check regex if not already triggered
            if not is_triggered:
                for pattern in rule.trigger.regex:
                    if re.search(pattern, text):
                        is_triggered = True
                        break

            if is_triggered:
                triggered.append(
                    {
                        "rule_id": rule.id,
                        "description": rule.description,
                        "decision": rule.decision,
                        "message": rule.message,
                    }
                )

                if severity_rank[rule.decision] > severity_rank[highest_severity]:
                    highest_severity = rule.decision

        return ReviewPacket.create(
            artifact_name=artifact_name,
            decision_state=highest_severity,
            triggered_rules=triggered,
            input_text=text,
        )
