import pytest
import json
from pathlib import Path
import sys

# Ensure src is in the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from review_engine.harness.checker import CyberneticHarness

@pytest.fixture
def harness():
    policy_dir = Path(__file__).parent.parent / "policy"
    return CyberneticHarness(str(policy_dir))

def test_harness_loads_rules(harness):
    assert len(harness.rules) > 0, "Harness should load at least one rule"

def test_evaluate_sample_cases(harness):
    fixtures_path = Path(__file__).parent / "fixtures" / "sample_cases.json"
    with open(fixtures_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    for case in cases:
        packet = harness.evaluate(case["text"], artifact_name=case["id"])
        assert packet.decision_state == case["expected_decision"], f"Failed on case {case['id']}: expected {case['expected_decision']}, got {packet.decision_state}"

def test_severity_escalation(harness):
    # If text has a warning AND a block, it should return block
    text = "This absolutely proves they violated the law and you must sue."
    packet = harness.evaluate(text)
    assert packet.decision_state == "block"
