# Cybernetic Ecology Field Workbench - Project Management Plan

Project Name: Cybernetic Ecology Field Workbench (Working Title: FieldAware)
Prepared by: Corey Shaffer
Project Type: Portfolio product / local-first environmental technology prototype
Version: 0.1
Status: Planning Draft

## 1. Project Overview
The Cybernetic Ecology Field Workbench is a local-first environmental fieldwork support system designed to run on a ruggedized or field-capable laptop. The system combines local AI, document retrieval, geospatial automation, GPS-aware context, field notebooking, and human review workflows.

The purpose of the project is to help environmental practitioners generate responsible, source-grounded, reviewable fieldwork artifacts such as maps, field notes, regulatory context summaries, evidence packets, and public-facing project materials. The system is designed around Cybernetic Ecology principles: responsibility, caution, diversity, equity, inclusion, local resilience, transparency, and respect for community and sovereignty boundaries.

The project is intended first as a portfolio product and learning system. Commercialization may be considered later after the system proves useful, understandable, and safe in real workflows.

## 2. Project Purpose and Rationale
Environmental fieldwork often requires practitioners to move between many disconnected tools:
- GIS software
- Field notebooks
- PDF protocols
- Scientific literature
- regulatory documents
- sensor data
- GPS coordinates
- public communication drafts
- review and approval workflows

This fragmentation increases the chance of errors, overclaims, missing metadata, weak source tracking, and accidental publication of sensitive or premature conclusions.

The Cybernetic Ecology Field Workbench addresses this problem by creating a governed local workspace where field data, maps, documents, regulations, and AI assistance are integrated into a single workflow. The system does not replace professional judgment. Instead, it prepares review packets, flags risky claims, surfaces relevant evidence, and accelerates human decision-making.

## 3. Project Vision
The long-term vision is a rugged, offline-capable environmental intelligence workbench that helps field teams ask location-aware questions such as:
- “What site am I near?”
- “What field protocol applies here?”
- “What documents mention this waterbody, contaminant, or sampling method?”
- “Can I describe this observation publicly?”
- “Generate a context map for this field visit.”
- “What caveats should accompany this map or report?”
- “Does this output require review before release?”

The system should feel like a careful field assistant: useful, quiet, source-aware, and unwilling to overstep authority.

## 4. Project Objectives

### Primary Objectives
- Build a local-first prototype that can run without cloud dependency.
- Create a document repository for scientific, regulatory, project, and field protocol documents.
- Enable retrieval-augmented generation using local documents.
- Integrate approved QGIS workflows for map generation.
- Support GPS or manually entered location context.
- Create a field notebook workflow for observations, photos, coordinates, and metadata.
- Implement a Cybernetic Ecology boundary harness that classifies outputs as allow, warn, require review, or block.
- Generate exportable evidence packages that include maps, notes, citations, metadata, limitations, and review logs.
- Produce a polished portfolio case study explaining the system’s design, purpose, ethics, and limitations.

### Secondary Objectives
- Support future integration with sensors, such as water quality probes or weather stations.
- Support offline field packets for specific sites or missions.
- Support multiple project profiles, such as Clear Lake Watch or SafeTask-style workflows.
- Explore eventual consulting or open-source release potential.

## 5. Scope

### In Scope for MVP
The MVP will support one primary scenario:
A user prepares for or conducts a Clear Lake field visit, uses local documents and maps to understand the site, records field observations, generates a QGIS-based context map, and produces a reviewable field evidence package.

The MVP will include:
- Local document repository
- Basic RAG over selected documents
- Manual coordinate entry, with optional GPS support later
- QGIS map recipe runner
- Field note capture
- Review flags for public health, sensitive location, regulatory interpretation, and unsupported scientific claims
- Export folder containing field notes, map, source list, limitations, and review log
- Portfolio documentation

### Out of Scope for MVP
The MVP will not include:
- Full multi-user SaaS
- Automated public publishing
- Legal or regulatory compliance determinations
- Official public health advisories
- Autonomous emergency response recommendations
- Sensitive Tribal/cultural site mapping
- Real-time sensor network integration
- Complex mobile app development
- Enterprise authentication
- Paid customer support

## 6. Key Deliverables
| Deliverable | Description |
|---|---|
| Project README | Clear description, use case, setup instructions, and boundaries |
| Project Management Plan | This document, maintained as a portfolio artifact |
| System Architecture Diagram | Visual explanation of local agent, RAG, QGIS, GPS, and review layers |
| Policy Rule Files | YAML or JSON rules for Cybernetic Ecology boundaries |
| Local Document Repository | Structured folder/index for scientific, regulatory, project, and protocol docs |
| RAG Prototype | Local retrieval over selected documents |
| QGIS Workflow Prototype | Recipe-based map generation using QGIS models or scripts |
| Field Notebook Prototype | Capture site, date/time, location, observations, photos, and notes |
| Review Queue Prototype | Flags outputs requiring human review |
| Evidence Package Export | Map, notes, source list, metadata, limitations, and review log |
| Test Cases | Boundary tests for overclaiming, sensitive locations, weak sources, and public-facing outputs |
| Portfolio Case Study | Narrative explanation of the problem, design, implementation, and lessons learned |

## 7. Product Architecture
The system will use a modular local-first architecture.

```text
User Interface
  ↓
Local Agent Planner
  ↓
Cybernetic Ecology Harness
  ↓
Tool Layer
  ├─ RAG Document Repository
  ├─ QGIS Workflow Runner
  ├─ GPS / Location Context
  ├─ Field Notebook Database
  └─ Export Package Generator
  ↓
Review Queue
  ↓
Approved Artifact
```

## 8. Cybernetic Ecology Boundary Model
The system will operationalize project principles as enforceable review rules.

### Core Boundary Categories
| Category | Example Trigger | Default Decision |
|---|---|---|
| Public health language | “Unsafe water,” “toxic bloom,” “health hazard” | Require Review |
| Scientific overclaiming | Field observation stated as confirmed finding | Warn or Require Review |
| Regulatory interpretation | “This violates regulation” | Require Review |
| Legal advice | Direct legal instruction | Block |
| Sensitive location | Exact coordinates of sensitive site | Require Review |
| Private property | Field location near private parcel | Warn or Require Review |
| Tribal/cultural context | Tribal land, sacred site, cultural resource | Require Review |
| Official authority confusion | Output sounds like agency advisory | Require Review |
| Missing source date | Regulation or dataset lacks date | Warn |
| Public export of raw GPS | Precise coordinates in public artifact | Require Review |

### Example Rule
```yaml
id: public_health_language_review
description: Require review before publishing public-health-adjacent claims.
trigger:
  terms:
    - unsafe
    - toxic
    - public health hazard
    - cyanobacteria bloom
    - do not swim
decision: require_review
message: Public health or water safety language requires human review and official-source grounding.
```

## 9. Human Review Philosophy
The system will use a “review by exception” model.
The goal is not to slow users down. The goal is to accelerate responsible work by preparing review packets only when human judgment matters.

### Review Principles
- Do not interrupt routine, reversible actions.
- Prepare review packets instead of vague warnings.
- Route decisions to the right authority type when possible.
- Suggest safer wording when language is the problem.
- Log decisions for transparency and later learning.
- Never publish public-facing outputs automatically.

### Review Packet Contents
Each review packet should include:
- Artifact name
- Triggering rule
- Risk level
- Why review is needed
- Evidence status
- Suggested action
- Quick actions
- Reviewer decision
- Timestamp

## 10. Work Breakdown Structure

### Phase 1: Project Definition and Repository Setup
- Select project name
- Create GitHub repository
- Create README
- Add project management plan
- Define project boundaries
- Define MVP scenario
- Create folder structure
- Create initial architecture diagram

### Phase 2: Policy Harness Prototype
- Define decision states
- Create policy schema
- Write initial boundary rules
- Build CLI rule checker
- Create sample risky text cases
- Create unit tests
- Generate review packet JSON

### Phase 3: Document Repository and Local RAG
- Create document metadata schema
- Add sample scientific, regulatory, and project documents
- Build local document index
- Implement basic retrieval
- Return source-grounded cards
- Add freshness and authority metadata
- Add citation tracking

### Phase 4: Field Notebook Prototype
- Define field note schema
- Build simple form or CLI entry workflow
- Store observations in SQLite or JSON
- Support site ID, time, coordinates, observer, and notes
- Attach or index photos
- Add confidence and evidence type fields

### Phase 5: QGIS Workflow Automation
- Define approved map recipe schema
- Build first QGIS map recipe
- Test map generation using local data
- Export PNG and PDF
- Generate map metadata
- Add map review flags

### Phase 6: Location Awareness
- Add manual coordinate input
- Match coordinates to nearest site
- Add spatial context lookup
- Filter documents by site or location
- Add sensitive coordinate review rule
- Later: test USB or Bluetooth GPS input

### Phase 7: Evidence Package Export
- Combine field notes, map, source cards, limitations, and review log
- Create export folder structure
- Generate Markdown summary
- Generate metadata JSON
- Mark public/internal/private status
- Add final boundary check

### Phase 8: Portfolio Case Study
- Write project narrative
- Explain problem and use case
- Include architecture diagram
- Include screenshots or terminal outputs
- Include sample map package
- Explain boundaries and limitations
- Describe future roadmap

## 11. MVP Timeline
A realistic MVP can be structured as an 8-week build.
- **Week 1:** Scope and repo setup (README, project plan, architecture)
- **Week 2:** Boundary harness (Policy schema and CLI checker)
- **Week 3:** Review packets (Review JSON and sample cases)
- **Week 4:** Document repository (Metadata schema and local RAG prototype)
- **Week 5:** Field notebook (Field note schema and storage)
- **Week 6:** QGIS recipe (First automated map output)
- **Week 7:** Evidence package (Combined export folder)
- **Week 8:** Portfolio polish (Case study, screenshots, roadmap)

## 12. Milestones
- **M1: Project Defined** - README, scope, and project plan completed
- **M2: Harness Working** - CLI returns allow, warn, review, or block
- **M3: Review Packet Generated** - Risky sample produces structured review packet
- **M4: Local RAG Working** - User can query local documents and receive source cards
- **M5: Field Note Captured** - A field observation can be saved and exported
- **M6: Map Generated** - QGIS recipe produces a map from local data
- **M7: Evidence Package Exported** - Map, notes, sources, limitations, and review log exported together
- **M8: Portfolio Case Study Published** - Project can be reviewed by advisor, employer, or internship reviewer

## 13. Stakeholder Analysis
(Details omitted for brevity in summary file, see original plan for full table)

## 14. RACI Matrix
(Details omitted for brevity in summary file, see original plan for full table)

## 15. Risk Register
(Details omitted for brevity in summary file, see original plan for full table)

## 16. Quality Management Plan
Quality will be evaluated through functional, ethical, and portfolio criteria.
- **Functional Quality:** CLI tools run without errors, Documents can be indexed and retrieved, Field notes can be saved and exported, QGIS recipe produces expected map output, Evidence package includes all required files
- **Ethical and Governance Quality:** Public-health claims trigger review, Unsupported scientific claims are flagged, Sensitive coordinates are not exported without review, Regulatory outputs include caveats, Sources and dates are visible, Public/private/internal status is marked
- **Portfolio Quality:** README explains the project clearly, Architecture is understandable, Demo scenario is concrete, Screenshots or outputs are included, Limitations are honest, Future roadmap is realistic

## 17. Acceptance Criteria
The MVP is complete when the system can:
- Accept a Clear Lake fieldwork prompt or scenario.
- Retrieve relevant local documents.
- Create a source-grounded context summary.
- Capture or load a field observation.
- Generate a QGIS context map.
- Flag at least three boundary types (public health, scientific claim, precise location).
- Generate a review packet.
- Export a field evidence package.
- Provide enough documentation for a portfolio reviewer to understand the system.

## 18. Communications Plan
- Project changelog: Weekly
- Milestone summary: At major milestones
- Technical notes: As needed
- Review logs: Per artifact
- Portfolio case study: Final MVP

## 19. Change Control
Changes should be evaluated using three questions:
1. Does this change improve the MVP scenario?
2. Does this change strengthen the portfolio story?
3. Does this change reduce or increase risk?

## 20. Initial Product Backlog
- Epic 1: Boundary Harness
- Epic 2: Local RAG Repository
- Epic 3: QGIS Automation
- Epic 4: Field Notebook
- Epic 5: Location Awareness
- Epic 6: Evidence Package Export
- Epic 7: Scientific Integrations & Workflows MVP Upgrades
  - Spatial data ingestion & preprocessing (GDAL/OGR Wrapper & GeoPandas)
  - Statistical analysis & modelling (Python/R sandbox)
  - Literature indexing (sentence-transformers + ChromaDB)
  - Versioned, collaborative field notes (Git-backed)
  - Policy-driven compliance (YAML rule packs)
  - Automated report generation (Jinja2 export engine)
  - Sensor & IoT data streams (Data ingestion plugin)
  - Interactive mapping (Folium)
  - Citation tracking (Crossref API)
  - Offline peer-to-peer sync (pygit2)

## 21. Roadmap
- Version 0.1: Planning and Policy
- Version 0.2: RAG and Review
- Version 0.3: Field Notebook
- Version 0.4: QGIS Automation
- Version 0.5: Evidence Package
- Version 1.0: Field Workbench MVP

## 22. Definition of Done
A feature is complete when: It works locally, has clear input/output, has tests, is documented, respects boundary rules, does not require cloud services, produces reviewable artifacts, supports the MVP scenario.

## 23. Portfolio Positioning Statement
The Cybernetic Ecology Field Workbench demonstrates the design of a local-first, boundary-aware AI system for environmental fieldwork. The project integrates local language models, retrieval-augmented generation, GIS automation, field note capture, GPS-aware context, and human review workflows.

## 24. Success Measures
- Working local MVP
- Clear GitHub repository
- Portfolio-ready case study
- Generated map package
- Source-grounded document retrieval demo
- Field note and evidence package
- Visible human review workflow
- Credible explanation of limitations and future work.

## 25. Guiding Principle
The system should help users move faster without becoming careless.
It should not replace field expertise, regulatory authority, community review, or scientific judgment. Its purpose is to make good judgment easier to apply by bringing together the right maps, documents, notes, sources, caveats, and review prompts at the right moment.
