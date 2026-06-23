# Operator Quickstart

This document details how a local operator interacts with SafeTask using the Human Review CLI.

> **Note**: The CLI currently operates on existing ledger records only. It does not interface with or fetch events directly from cameras or network video recorders.

## Basic Usage

The CLI requires `--ledger` for the file path to the evidence JSONL file. Most commands also require an `--event-id`.

### Verify Ledger Integrity
Use this command to validate that the tamper-evident hash chain remains unbroken:
```powershell
python -m safetask.cli verify-ledger --ledger .safetask/evidence.jsonl
```

### Check Event Review State
Reconstruct and display the current status, policy, notes, and latest interaction time of a specific event:
```powershell
python -m safetask.cli review-state --ledger .safetask/evidence.jsonl --event-id evt_001
```

### Add a Review Note
Append a human observation to an event record:
```powershell
python -m safetask.cli add-note --ledger .safetask/evidence.jsonl --event-id evt_001 --note "Subject identified as family dog."
```

### Set Review Status
Update the human review status of the event (`pending`, `reviewed`, `dismissed`, `retained`):
```powershell
python -m safetask.cli set-review-status --ledger .safetask/evidence.jsonl --event-id evt_001 --status dismissed
```

### Set Retention Policy
Update the lifecycle rules governing an event (`temporary`, `retain`, `delete_after_review`):
```powershell
python -m safetask.cli set-retention-policy --ledger .safetask/evidence.jsonl --event-id evt_001 --policy delete_after_review
```

### Run Retention Dry-Run
Evaluate whether an event is currently eligible for physical deletion based on its current state and policy. **No files will be deleted.**
```powershell
python -m safetask.cli retention-dry-run --ledger .safetask/evidence.jsonl --event-id evt_001
```
