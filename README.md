# FieldAware & SafeTask: Review Packet Engine

This repository hosts a shared local-first **Review Packet Engine**, serving two related verticals:

1. **FieldAware**: Environmental fieldwork review packets (GIS/context maps, field notes, evidence packages).
2. **SafeTask**: Safety document and incident response packets (SDSs, chemical inventory context, response contacts).

Both tools share a common architecture built around local-first document retrieval (RAG), a human review boundary harness, precise source-linking, and exportable markdown/zip packets.

---

## SafeTask Response Navigator

SafeTask Response Navigator is a safety-document and chemical-context vertical built on the FieldAware Review Packet Engine.

It helps safety officers and supervisors retrieve source-linked SDS sections, emergency procedures, chemical inventory context, and contact workflows for human-reviewed incident response packets.

SafeTask does not make legal, medical, regulatory, engineering, emergency-response, or compliance determinations.

### First Monetizable Offer

**Safety Document Navigator Pilot:**
A paid setup service for small facilities that need SDSs, emergency procedures, chemical inventory sheets, and safety contacts organized into a searchable, source-linked response packet system.

**Beta scope:**
- Up to 25 documents
- One inventory CSV
- One contacts CSV
- One response-mode demo
- One walkthrough

### How to Demo SafeTask

1. Install dependencies: `pip install -r requirements-safetask.txt`
2. Run the UI: `streamlit run safetask/ui/streamlit_app.py`
3. Load the demo data from `demo_data/` (Inventory CSV, Contacts CSV).
4. Go to **Response Mode Lite** and enter the demo incident:
   > "Methyl isocyanate leak in Building 3, first floor. Tank on northwest corner."
5. View the generated incident packet, complete with chemical context, escalation workflow, and strict human review boundaries.

---

## FieldAware: Cybernetic Ecology Field Workbench

**FieldAware** is an environmental fieldwork support system designed to run on a ruggedized or field-capable laptop. 

The system combines local AI, document retrieval, geospatial automation, GPS-aware context, field notebooking, and human review workflows.

### 🛡️ Cybernetic Ecology Boundaries

The system is designed around responsibility, caution, and transparency. A core component is the **Cybernetic Ecology Harness**, which classifies actions and outputs into four states:
- **Allow:** Safe, routine, reversible.
- **Warn:** Proceed with a caveat.
- **Require Review:** Human approval required before export or publication.
- **Block:** Action violates a hard boundary (e.g., providing direct legal advice).

### 🚀 Getting Started with FieldAware

To explore the latest MVP features:
1. `python src/cli.py export <base_filename>`: Automatically renders an Evidence Package report.
2. `python src/cli.py serve`: Launches the local dashboard exposing the `/api/flag` endpoint and a UI.

---

## 📂 Project Structure

- `review_engine/` - Shared core for RAG, chunking, and boundary harness logic.
- `safetask/` - Vertical for safety documents, inventory, contacts, and response mode.
- `fieldaware/` (legacy `src/`) - Vertical for environmental context, field notes, and QGIS recipes.
- `policy/` - YAML/JSON rules defining boundary harnesses.
- `data/` - Local databases and indexes.
- `demo_data/` - Sample CSVs and incidents for SafeTask demoing.
