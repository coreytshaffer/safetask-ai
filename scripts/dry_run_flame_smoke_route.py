import sys
import json
import argparse
from jsonschema import ValidationError
from safetask.flame_smoke import route_flame_smoke_claim

def main():
    parser = argparse.ArgumentParser(description="Simulate routing a flame/smoke claim through the redaction gate.")
    parser.add_argument("claim_file", help="Path to flame_smoke_claim JSON")
    parser.add_argument("--target", action="append", default=[], help="Redaction target types (e.g. human_figure)")
    parser.add_argument("--format", default="image", help="Export format")
    args = parser.parse_args()

    try:
        with open(args.claim_file, 'r', encoding='utf-8') as f:
            claim_payload = json.load(f)
    except Exception as e:
        print(f"Error loading {args.claim_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # Build mocked targets array
    targets = []
    for t in args.target:
        targets.append({
            "target_type": t,
            "region": {"bbox": [10, 10, 50, 50]}  # Dummy valid geometry
        })

    try:
        result = route_flame_smoke_claim(claim_payload, redaction_targets=targets, export_format=args.format)
        print(json.dumps(result, indent=2))
        
        # If it's blocked/failed, exit non-zero
        if result.get("redaction_status") == "redaction_failed_export_blocked":
            sys.exit(1)
            
    except ValidationError as e:
        print(f"Validation Error: {e.message}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Routing Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Internal Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
