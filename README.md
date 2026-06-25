# SafeTask-AI

SafeTask is a hazard-first, local-first safety evidence pipeline prototype. It demonstrates schema validation, human-review gates, fail-closed redaction, and privacy-preserving export controls using synthetic fixtures. It is not production security software and does not perform surveillance detection, ALPR, face recognition, identity tracking, or emergency automation.

## Project Status: Prototype
**WARNING**: SafeTask-AI is a research prototype. It is **not** production security software. It does not provide real-time alerting, physical security guarantees, or emergency dispatch capabilities. Do not rely on it for life safety or property protection.

## Core Safety Doctrine
- **"Detect hazards, not identities."**
- **"Export the hazard, not the bystander."**
- **"Safety evidence may be useful, but privacy failure blocks sharing."**

## Intentional Non-Capabilities (Safety Boundaries)
To ensure the system remains a privacy-preserving workbench rather than a surveillance tool, the following capabilities are explicitly **excluded**:
- **No ALPR (Automated License Plate Recognition)**
- **No face recognition**
- **No suspicious-person detection**
- **No video tracking or identity association across frames**
- **No law-enforcement automation or direct integration**
- **No emergency escalation automation**
- **No biometrics or gait analysis**
- **No weapon detection**
- **No public surveillance deployment**
- **No cloud dependencies for core architecture**
- **No real camera ingestion** (Currently accepts only mocked JSON payloads)

## Current Implemented Capabilities
- **Strict Schema Validation**: A rigidly defined standard for generic event envelopes and claims (`safetask.events`).
- **Evidence Ledger**: An append-only JSONL data store to securely record events and human actions (`safetask.ledger`).
- **Ledger Replay and Review State**: Reconstruction of an event's active state based on ledger history.
- **Ledger Integrity Hash Chain**: Deterministic verification of ledger mutations to prevent silent tampering.
- **Privacy-Preserving Export Pipeline**: Static image redaction prototype to ensure hazards can be exported while obscuring private details. Fails closed on any invalid geometry.
- **Human Review CLI**: A command-line tool for local operators to inspect states, add notes, update policies, and perform dry-runs.

## Simulated Pipeline Explanation
SafeTask currently relies on synthetic JSON fixtures to prove out its logic. The simulated pipeline functions as a series of strict gates:
1. **Schema Check**: Incoming claims must match exact JSONSchema definitions.
2. **Review Check**: Ambiguous hazards are forced into a manual human review state.
3. **Redaction Gate**: Exporting evidence requires passing through a strict redaction gate. Valid bounds yield opaque masks over sensitive regions; invalid requests instantly fail closed, blocking export entirely.

## Reviewer Quickstart

Check out the [Reviewer Quickstart](docs/reviewer_quickstart.md) to explore the system using synthetic data.

### Quick Install & Test
```powershell
pip install -r requirements.txt
python -m unittest discover tests
python -m compileall safetask tests
```

## Public Release Safety Note
This repository has been audited for public release. It contains **no real images**, **no real incidents**, **no camera paths**, and **no local private footage**. All tests rely exclusively on synthetic JSON structures and in-memory mock images.
