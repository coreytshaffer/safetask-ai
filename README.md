# SafeTask AI - Surveillance Command Portal

SafeTask AI is an advanced Security Operations Center (SOC) portal built to bridge the gap between Casino Surveillance Code Compliance (MICS/TICS) and Industrial/OSHA Safety. It operates using a fully deterministic Retrieval-Augmented Generation (RAG) architecture running locally, ensuring strict chain-of-custody for regulatory audits.

**Authority Accelerator Principle:** SafeTask is not an AI decision-maker. The human observes. SafeTask structures. Authorized stakeholders review, decide, and approve.

> [!WARNING]
> **Human Review Disclaimer:** Generated reports are drafts. They must be reviewed and approved by an authorized stakeholder before operational, legal, regulatory, or emergency use. SafeTask does not make independent compliance or liability determinations.

## Features

- **Spatial Floor Map & Anomaly Detection:** Interactive CSS-Grid map showing Edge AI anomaly beacons across the facility.
- **Draggable VMS Picture-in-Picture:** Asynchronous multi-feed viewing (Live PTZ, Review Clip, Live Fixed) directly within the reporting interface.
- **Generative Compliance Reporting:** Automated, citation-constrained drafting of incident narratives to reduce unsupported claims, mapped to MICS regulations.
- **Deterministic Admin Policy Deployment:** Leadership can upload official PDFs (SOPs, SDS sheets). The system deterministically extracts the text and metadata to update the RAG database instantly.
- **TGRA Audit Engine:** Export generated compliance reports to watermarked, audit-ready PDFs.

## Architecture

- **Backend:** Python Flask REST API
- **Database:** SQLite (`safetask.db`)
- **Document Ingestion:** `PyPDF2` (Deterministic extraction)
- **PDF Engine:** `reportlab` (Watermarked TGRA Audit Exports)
- **Local AI proxy:** Interfaces with `LM Studio` (Nemotron Model) via port 1234.

## Setup Instructions

1. Ensure Python 3.10+ is installed.
2. Clone the repository.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start your local LLM server (e.g., LM Studio) on `http://127.0.0.1:1234/v1`.
5. Start the Flask backend:
   ```bash
   python app.py
   ```
6. Navigate to `http://localhost:8080` in your web browser.
