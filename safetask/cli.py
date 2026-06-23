import argparse
import sys
from safetask.ledger import EvidenceLedger, ActionType
from safetask.retention import RetentionSweeper

def main(argv=None):
    parser = argparse.ArgumentParser(description="SafeTask Human Review CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_args(p, include_event_id=True):
        p.add_argument("--ledger", required=True, help="Path to the ledger file")
        if include_event_id:
            p.add_argument("--event-id", required=True, help="Target event ID")

    # verify-ledger
    p_verify = subparsers.add_parser("verify-ledger", help="Verify the integrity of the ledger")
    add_common_args(p_verify, include_event_id=False)

    # review-state
    p_state = subparsers.add_parser("review-state", help="Print the current review state of an event")
    add_common_args(p_state)

    # add-note
    p_note = subparsers.add_parser("add-note", help="Add a human review note to an event")
    add_common_args(p_note)
    p_note.add_argument("--note", required=True, help="Text of the note")

    # set-review-status
    p_status = subparsers.add_parser("set-review-status", help="Change human review status")
    add_common_args(p_status)
    p_status.add_argument("--status", required=True, choices=["pending", "reviewed", "dismissed", "retained"])

    # set-retention-policy
    p_policy = subparsers.add_parser("set-retention-policy", help="Change retention policy")
    add_common_args(p_policy)
    p_policy.add_argument("--policy", required=True, choices=["temporary", "retain", "delete_after_review"])

    # retention-dry-run
    p_dry_run = subparsers.add_parser("retention-dry-run", help="Evaluate retention eligibility")
    add_common_args(p_dry_run)

    args = parser.parse_args(argv)

    ledger = EvidenceLedger(args.ledger)

    if args.command == "verify-ledger":
        try:
            if ledger.verify_integrity():
                print("Ledger integrity verified.")
        except Exception as e:
            print(f"Ledger verification failed: {e}")
            sys.exit(1)

    elif args.command == "review-state":
        state = ledger.reconstruct_event_state(args.event_id)
        print(f"Event ID: {state.event_id}")
        print(f"Review Status: {state.latest_review_status}")
        print(f"Retention Policy: {state.latest_retention_policy}")
        print(f"Notes: {state.notes}")
        print(f"Updated At: {state.updated_at}")

    elif args.command == "add-note":
        ledger.append_record(args.event_id, ActionType.NOTE_ADDED, {"text": args.note})
        print(f"Note added to event {args.event_id}.")

    elif args.command == "set-review-status":
        ledger.append_record(args.event_id, ActionType.REVIEW_STATUS_CHANGED, {"status": args.status})
        print(f"Review status of event {args.event_id} set to {args.status}.")

    elif args.command == "set-retention-policy":
        ledger.append_record(args.event_id, ActionType.RETENTION_POLICY_CHANGED, {"policy": args.policy})
        print(f"Retention policy of event {args.event_id} set to {args.policy}.")

    elif args.command == "retention-dry-run":
        state = ledger.reconstruct_event_state(args.event_id)
        sweeper = RetentionSweeper()
        report = sweeper.evaluate(state)
        print(f"Event ID: {report.event_id}")
        print(f"Current Review Status: {report.current_review_status}")
        print(f"Retention Policy: {report.retention_policy}")
        print(f"Eligible for Deletion: {report.eligible_for_deletion}")
        print(f"Reason: {report.reason}")

if __name__ == "__main__":
    main()
