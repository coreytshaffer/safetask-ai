# Reviewer Quickstart

Welcome to SafeTask-AI! As a reviewer, you should be able to get this prototype running and verify its privacy boundaries in under five minutes. 

This guide uses exclusively synthetic fixtures. No actual images, video feeds, or hardware are required.

## 1. What SafeTask Intentionally Does NOT Do
Before running anything, it is important to understand the boundaries:
- **No ALPR (License Plate Recognition)**
- **No Face Recognition**
- **No Suspicious Person Detection**
- **No Tracking across frames**
- **No Emergency Escalation**
- **No Surveillance Intelligence**

## 2. Environment Setup

Ensure you are running Python 3.9+ and have a virtual environment active if you prefer.

Install the minimal required dependencies:
```powershell
pip install -r requirements.txt
```

## 3. Run Validation Checks

First, confirm the codebase is intact by running the test suite:
```powershell
python -m unittest discover tests
```

Next, ensure everything compiles cleanly:
```powershell
python -m compileall safetask tests
```

## 4. Explore the Privacy-Preserving Pipeline

SafeTask acts as a strict gateway. Try running the simulated flame/smoke routing CLI, which passes claims through schema validation, human review, and a redaction gate:

```powershell
python scripts/dry_run_flame_smoke_route.py
```

### Expected Output
You will see simulated claims processed:
- **Valid Flame Claim**: Successfully requests redaction for a bystander's face and license plate, creating a compliant export record.
- **Ambiguous Smoke Claim**: Forced into a human review state instead of being exported.
- **Identity Violation**: Rejects a claim trying to include prohibited fields (like facial identity).
- **Prohibited Flags**: Instantly rejects if the payload admits it skipped local processing.

## 5. Test the Redaction Gate

You can test the lower-level redaction engine dry-run directly:

```powershell
python scripts/dry_run_redaction_export.py
```

### Expected Output (Fail-Closed)
This simulates what happens when an upstream component requests an invalid or prohibited redaction format (like a video):
- The export is instantly blocked (`export_allowed: false`).
- The `redaction_status` becomes `redaction_failed_export_blocked`.
- The reason is explicitly cited (e.g., "Video export is currently unsupported").

By failing closed, SafeTask guarantees that privacy faults prevent evidence from ever leaving the local environment.
