import os
import argparse
from safetask.ledger import EvidenceLedger, ActionType

def main():
    parser = argparse.ArgumentParser(description="Generate a synthetic SafeTask demo ledger.")
    parser.add_argument("--output", default=".safetask/demo_evidence.jsonl", help="Path to output ledger file")
    args = parser.parse_args()

    ledger_path = args.output
    if os.path.exists(ledger_path):
        os.remove(ledger_path)

    ledger = EvidenceLedger(ledger_path)

    event_id = "demo_evt_001"

    print(f"Creating demo ledger at {ledger_path}...")

    # Event Created
    ledger.append_record(
        event_id,
        ActionType.EVENT_CREATED,
        {"source": "synthetic_demo", "description": "Motion detected near backdoor"}
    )

    # Note Added
    ledger.append_record(
        event_id,
        ActionType.NOTE_ADDED,
        {"text": "Subject identified as family dog fetching a ball. No threat."}
    )

    # Review Status Changed
    ledger.append_record(
        event_id,
        ActionType.REVIEW_STATUS_CHANGED,
        {"status": "dismissed"}
    )

    # Retention Policy Changed
    ledger.append_record(
        event_id,
        ActionType.RETENTION_POLICY_CHANGED,
        {"policy": "delete_after_review"}
    )

    print("Demo ledger generated successfully.")
    print("Verify integrity using:")
    print(f"  python -m safetask.cli verify-ledger --ledger {ledger_path}")

if __name__ == "__main__":
    main()
