# Smoke-Demo Walkthrough

This document shows how to run the SafeTask end-to-end smoke demo locally.

> **Note**: This demo uses synthetic placeholder records. It does not represent live camera ingestion or network integration. SafeTask is a post-VMS local evidence workbench.

## 1. Generate the Demo Ledger

We provide a Python script that builds a valid, hash-chained local ledger representing a single household-safety event.

Run the generator from the repository root:
```powershell
python examples/create_demo_ledger.py --output .safetask/demo_evidence.jsonl
```
This script creates a deterministic event (`demo_evt_001`), adds a human review note, marks it as `dismissed`, and sets its retention policy to `delete_after_review`.

## 2. Verify Ledger Integrity

Use the CLI to verify the tamper-evident hash chain:
```powershell
python -m safetask.cli verify-ledger --ledger .safetask/demo_evidence.jsonl
```
*Expected Output: `Ledger integrity verified.`*

## 3. Check Event Review State

Inspect the current state of the synthetic event:
```powershell
python -m safetask.cli review-state --ledger .safetask/demo_evidence.jsonl --event-id demo_evt_001
```
*Expected Output: You should see the review status as `dismissed`, the policy as `delete_after_review`, and the notes appended.*

## 4. Run Retention Dry-Run

Evaluate whether the event is eligible for deletion under the current policy (it should be, since it is `delete_after_review` and `dismissed`):
```powershell
python -m safetask.cli retention-dry-run --ledger .safetask/demo_evidence.jsonl --event-id demo_evt_001
```
*Expected Output: `Eligible for Deletion: True` and the explicit reason.*
