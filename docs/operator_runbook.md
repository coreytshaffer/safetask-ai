# SafeTask-AI Operator Runbook

This document describes the operational procedures for managing SafeTask-AI. The system is designed to be local-first, private, and deterministic. Operations should be run locally using the provided CLI tools.

## 1. Importing Evidence via Drop Folder

The primary method for introducing new evidence into SafeTask-AI is the drop folder. Adapters should drop well-formed `.json` payloads into the designated incoming directory.

**Dry Run:**
To validate payloads without committing to the ledger:
```bash
python -m safetask.cli drop-folder-dry-run --incoming /path/to/incoming
```
*Note: A non-zero exit code will be returned if any payload is invalid.*

**Commit Import:**
To validate and commit valid payloads into the ledger:
```bash
python -m safetask.cli drop-folder-import --incoming /path/to/incoming --ledger /path/to/ledger.jsonl --commit
```
*Note: A non-zero exit code will be returned if any payload is invalid. Duplicates will be skipped without error. Changed duplicates (same source ID but different content) will be marked as invalid/tampered.*

## 2. Managing the Evidence Ledger

The Evidence Ledger is an append-only JSONL file representing the source of truth for all events.

**Verify Integrity:**
```bash
python -m safetask.cli verify-ledger --ledger /path/to/ledger.jsonl
```

**View Review State:**
```bash
python -m safetask.cli review-state --ledger /path/to/ledger.jsonl --event-id <EVENT_ID>
```

**Set Review Status:**
Choices: `pending`, `reviewed`, `dismissed`, `retained`
```bash
python -m safetask.cli set-review-status --ledger /path/to/ledger.jsonl --event-id <EVENT_ID> --status reviewed
```

**Add Note:**
```bash
python -m safetask.cli add-note --ledger /path/to/ledger.jsonl --event-id <EVENT_ID> --note "Review completed, false alarm."
```

## 3. Retention Policies

Events have an associated retention policy that determines if their underlying evidence should be kept or deleted.

**Change Policy:**
Choices: `temporary`, `retain`, `delete_after_review`
```bash
python -m safetask.cli set-retention-policy --ledger /path/to/ledger.jsonl --event-id <EVENT_ID> --policy retain
```

**Retention Dry Run:**
```bash
python -m safetask.cli retention-dry-run --ledger /path/to/ledger.jsonl --event-id <EVENT_ID>
```

## 4. Troubleshooting and Recovery

### Duplicate Event Skipped
If you import the exact same payload twice, it will be skipped safely. 

### Invalid Payload (Tampering Alert)
If a payload has the same `source_event_id` and `source_system` but different contents, it will be rejected as an `invalid` payload. This is a tamper-prevention mechanism.

### Broken Ledger Hash Chain
If `verify-ledger` fails, the ledger file has been manually tampered with or corrupted. Restore the `ledger.jsonl` from the latest known-good backup. SafeTask will refuse to import new items if the ledger is corrupted.
