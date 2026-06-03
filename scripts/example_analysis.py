import os
import sys
import json
from datetime import datetime, timezone

try:
    import pandas as pd
except ImportError:
    print(json.dumps({"error": "pandas not installed in this environment"}))
    sys.exit(1)

def main():
    notes_json = os.environ.get("FIELD_NOTES_JSON", "[]")
    
    try:
        data = json.loads(notes_json)
    except Exception as e:
        print(json.dumps({"error": f"Failed to parse FIELD_NOTES_JSON: {e}"}))
        sys.exit(1)
        
    if not data:
        print(json.dumps({
            "site_id": "System Analysis",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": "No field notes available for analysis.",
            "confidence_level": "low"
        }))
        sys.exit(0)
        
    # Load into pandas DataFrame
    df = pd.DataFrame(data)
    
    # Calculate some basic statistics
    total_notes = len(df)
    
    # Check if 'site_id' exists and group by it
    if 'site_id' in df.columns:
        counts_by_site = df['site_id'].value_counts().to_dict()
    else:
        counts_by_site = {}
        
    # Format the result as a Markdown string to be saved as a new note
    report = f"### Field Data Statistical Summary\n\n"
    report += f"- **Total Observations**: {total_notes}\n"
    report += f"- **Observations by Site**:\n"
    for site, count in counts_by_site.items():
        report += f"  - `{site}`: {count}\n"
        
    # Output the exact JSON payload expected by the AnalysisSandbox
    result = {
        "site_id": "System Analysis",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "notes": report,
        "confidence_level": "high"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
