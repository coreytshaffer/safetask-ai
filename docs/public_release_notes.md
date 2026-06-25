# SafeTask-AI v0.1-prototype Release Notes

This marks the first public release candidate for SafeTask-AI.

## What is Included
- **Event Schemas**: Defined structures for hazard claims and export records.
- **Evidence Ledger**: Immutable, hash-chained local JSONL data store.
- **Human Review CLI**: Local operator tool for state inspection and dry-runs.
- **Privacy-Preserving Export Pipeline**: Prototype static redaction engine to enforce fail-closed visual bounds.
- **Synthetic Test Fixtures**: 85 tests proving the architecture with mocked JSON events.

## What is Intentionally Not Included
SafeTask-AI is a hazard-first workbench, not surveillance intelligence software.
- **No real footage or images**: The repository is entirely synthetic.
- **No ALPR (License Plate Recognition)**
- **No Face Recognition or Biometrics**
- **No Tracking of individuals across frames**
- **No Cloud Services or Network broadcasting**

## Why is there no detector model?
SafeTask establishes the *boundary* above computer vision. Providing a real hazard detector (like a PyTorch flame model or OpenCV script) would unnecessarily couple the project to heavy machine learning stacks and distract from the core goal: ensuring the privacy contract and review gates are impenetrable *before* visual inference is added.

## Privacy & Safety Boundaries
The core philosophy is **"Detect hazards, not identities."** All workflows enforce human review. If redaction is requested for a hazard export but the renderer fails, the system strictly fails closed and blocks the export entirely.

## Known Limitations
- The current redaction renderer only processes opaque black masks for standard rectangular bounding boxes on static JPEG images. Video rendering is strictly prohibited in this phase.
- There are no live VMS integrations. All tests are mock scenarios simulating what an upstream adapter might send.
