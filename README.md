# SafeTask AI: Local-First Safety and Review Operations Platform

**Prototype | Local-First | Simulation Mode**

> [!WARNING]
> **Human Review Required:** This system does not make autonomous compliance decisions and is not intended for production biometric identification. Generated reports are drafts. They must be reviewed and approved by an authorized stakeholder before operational, legal, regulatory, or emergency use.

SafeTask AI is an operations platform built to bridge the gap between compliance documentation (SDS, JHA, Incident Packets) and surveillance evidence review. It operates using a fully deterministic Retrieval-Augmented Generation (RAG) architecture running locally, ensuring strict chain-of-custody.

## Product Ecosystem

We are building SafeTask through a staged approach to prioritize immediate pain points before expanding into complex surveillance modules.

### 1. SafeTask Field (Current Focus)
**The practical, sellable wedge.**
Turns messy safety, SDS, JHA, incident, inspection, and compliance packet chaos into a local-first assistant. 
*Target: Small casinos, hotels, gas stations, maintenance departments, EHS coordinators, and tribal enterprises.*

### 2. SafeTask Review Workbench
**General evidence/review operations layer.**
Helps authorized staff find, organize, annotate, and package operational evidence without losing live situational awareness.
- Protected live shot / PiP review deck
- Timestamp and event pinning
- Policy-aware checklists and human approval gates
- Authorized Evidence Release Portal (governed by facility policy and audit trails)

### 3. PitLens / Table Games Workbench (Specialty Module)
**Casino-specific prestige module.**
Supports human-reviewed table-games analysis using variant-aware overlays and workflows.
- Human-confirmed active bet shot first, automation second
- Blackjack and Pai Gow Baccarat presets
- Chip-depth and bet-spread review assistance

### 4. SafeTask VMS (Long-term Flagship Direction)
A full facility surveillance operations platform with policy ingestion, evidence workflows, review tools, dispatch/roster support, emergency coordination, and compliance-aware reporting.

## Architecture

- **Backend:** Python FastAPI REST API (`src/web/app.py`)
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Database:** SQLite (`safetask.db`) for incident and policy storage
- **Local AI Proxy:** Interfaces with local LLMs (e.g. LM Studio) on `http://127.0.0.1:1234/v1`

## Setup Instructions

1. Ensure Python 3.10+ is installed.
2. Clone the repository.
3. Create and activate a local virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install the required dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
5. Start your local LLM server (e.g., LM Studio) on `http://127.0.0.1:1234/v1`.
6. Start the FastAPI backend from the repository root:
   ```powershell
   python src/web/app.py
   ```
7. Navigate to `http://localhost:8080` in your web browser.

## Validation

Run the validation script to check python compilation, pytest, and regulation pack parsing before pushing code:
```powershell
.\validate.bat
```
