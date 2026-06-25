import sys
import json
import argparse
from jsonschema import ValidationError
from safetask.redaction import simulate_redaction_request

def main():
    parser = argparse.ArgumentParser(description="Dry-run redaction engine stub.")
    parser.add_argument("request_file", help="Path to redaction_export_request JSON")
    args = parser.parse_args()

    try:
        with open(args.request_file, 'r', encoding='utf-8') as f:
            request_payload = json.load(f)
    except Exception as e:
        print(f"Error loading {args.request_file}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = simulate_redaction_request(request_payload)
        print(json.dumps(result, indent=2))
        
        # If it's a failure event, we exit non-zero to signal that the export was blocked
        if result.get("redaction_status") == "redaction_failed_export_blocked":
            sys.exit(1)
            
    except ValidationError as e:
        print(f"Validation Error: {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Internal Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
