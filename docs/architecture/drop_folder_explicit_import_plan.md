# Drop-Folder Explicit Import Plan

This document defines the architectural intent and precise constraints for the upcoming Drop-Folder Explicit Import command. This command is the sole entry point through which an external payload traverses the airlock and becomes a permanent record in the SafeTask Evidence Ledger.

## Future CLI Command Shape

The import command will take the following shape:

```powershell
python -m safetask.cli drop-folder-import --incoming PATH --ledger PATH [--commit]
```

### Dry-Run by Default
If the `--commit` flag is omitted, the command must execute in **dry-run mode**. It will scan the incoming folder, perform all validation and duplication checks, and output a detailed report of what *would* happen, without mutating the ledger or moving any files.

### Explicit Commit
Only the presence of the `--commit` flag authorizes the command to write to the ledger.

## Permitted Ledger Operations

During a committed import, the pipeline is strictly limited in its capabilities.

**What the import MUST append:**
- An `event_created` action for each valid, non-duplicate payload.

**What the import MUST NOT append:**
- `review_status_changed`
- `retention_policy_changed`
- `note_added`
- Any deletion records
- Any escalation records

Review notes and status changes remain exclusively the domain of the human operator via separate CLI commands.

## Validation Chain and Duplicate Handling

The import process will follow a strict, sequential pipeline:
1. **Parse JSON**: Read the incoming file.
2. **AdapterPayload Validation**: Enforce schema requirements.
3. **Prohibited Capability Rejection**: Explicitly reject claims involving biometric identification, face recognition, ALPR, law-enforcement workflows, cloud processing, or auto-escalation.
4. **Event Conversion**: Normalize the valid payload into the SafeTask `Event` schema.
5. **Duplicate Check**: The ledger must be checked to ensure the `event_id` does not already exist. If it does, the payload must be flagged as a duplicate and explicitly skipped. It must not silently append a duplicate `event_created` record.
6. **Append**: If the payload passes all checks and `--commit` is provided, append the `event_created` record to the ledger.

## File Handling Boundaries

In the immediate implementation (CR-ST-020), **no file movement will occur**.

Even with the `--commit` flag provided, the original JSON payload files must remain exactly where they are. Moving files to `accepted/`, `processed/`, `rejected/`, or `quarantine/` will be handled in a separate, dedicated future architectural slice.

## Operator Confirmation Behavior

The operator experience will focus on clarity and consent:
1. A dry-run report is generated.
2. The report must explicitly tally:
    - Valid payloads ready for import
    - Invalid payloads (schema failures)
    - Prohibited payloads (capability firewall violations)
    - Duplicate payloads (already in ledger)
3. If `--commit` is supplied, only the valid, non-duplicate payloads are committed to the ledger.
