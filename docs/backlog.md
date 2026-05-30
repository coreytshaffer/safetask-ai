# SafeTask AI: Agile and PMI Backlog Handoff

## 1. Product thesis

SafeTask AI is a local-first surveillance, safety, evidence, policy, and emergency-preparedness platform designed to reduce operational friction in surveillance-heavy environments.

The core product insight is this:

> Surveillance agents already think spatially, temporally, relationally, and evidentially. SafeTask should capture that expertise directly instead of forcing agents through clumsy dropdowns and disconnected report forms.

SafeTask should not be positioned as an AI decision-maker. It should be positioned as an authority accelerator:

> The human observes. SafeTask structures. Authorized stakeholders review, decide, and approve.

## 2. Product family

```text
SafeTask Core
├── SafeTask Surveillance Command Center
│   ├── Live Continuity Deck
│   ├── Constellation Review
│   ├── Incident Threads
│   ├── Evidence Registry
│   ├── Recall Search
│   ├── Admin Governance Console
│   ├── Emergency Plan Assistant
│   └── SafeTask Field Module
└── SafeTask Field
    ├── standalone JHA and workplace safety tool
    ├── task hazard analysis
    ├── safety incident drafting
    ├── SDS and policy reference support
    └── emergency response support
└── SafeTask Security & Dispatch
    ├── Dispatch log & officer task tracking
    ├── Lost and found registry
    ├── Field incident reporting
    └── Credential-gated evidence inbox

SafeTask Field should exist both as:

1. A standalone safety and JHA product.
2. An added module inside the Surveillance Command Center for workplace safety, biohazard, injury, evacuation, and emergency response workflows.

## 3. Non-negotiable design principles

### 3.1 Authority acceleration, not authority replacement

SafeTask must route evidence, drafts, gaps, and questions to the appropriate authorized stakeholders. It must not talk over tribal government, TGRA, compliance, safety, emergency management, legal, operations, or supervisory authority.

### 3.2 Source-bound drafting

Generated text must be grounded in approved source documents, incident observations, evidence metadata, and configured policy packs. Drafts require human review before operational, legal, regulatory, or emergency use.

### 3.3 Respect the surveillance VLAN

SafeTask should index evidence and manage references, metadata, hashes, retention status, and report lineage. It should not become an uncontrolled evidence archive unless explicitly configured and approved.

### 3.4 Search incident evidence, not people

Recall Search may use human memory fragments such as clothing, behavior, location, and event type. It should be framed as incident evidence retrieval, not generalized person tracking.

### 3.5 Preserve live coverage

Review activity must never silently displace protected live shots. The product exists partly because agents are forced to juggle live monitoring, video review, report writing, and interruptions at the same time.

### 3.6 Make spatial cognition first-class

The interface should capture routes, camera adjacency, blind spots, timestamp pins, evidence quality, and stakeholder reports. Dropdowns should be fallback tools, not the main operating model.

### 3.7 Translate meaning, not only words

Jurisdiction packs must preserve original source language, literal translation, and operational interpretation as separate fields. SafeTask should present the user-facing explanation in the user's preferred language while making clear what is source text, what is a literal translation, and what is reviewer-approved practical guidance.

## 4. North-star workflow

```text
Agent observes live event
↓
Protected Live Shot remains visible
↓
Agent opens review clips in PiP without losing live coverage
↓
Agent pins timestamps and dictates observations
↓
SafeTask builds a spatial-temporal event graph
↓
Policy and authority lanes are suggested from approved sources
↓
Incident thread collects evidence, reports, gaps, and stakeholders
↓
Authorized reviewer approves, routes, or requests more information
↓
Reports, evidence references, retention status, and after-action items are preserved
```

## 5. Agile backlog

### Epic 0: Stabilize the prototype
* Story 0.1: Fix JavaScript parse failure
* Story 0.2: Align launcher with full backend
* Story 0.3: Add domain-specific test suites
* Story 0.4: Update commercial safety copy

### Epic 1: SafeTask Core domain architecture
* Story 1.1: Create core plus domain pack structure
* Story 1.2: Define shared event schema

### Epic 2: Live Continuity Deck
* Story 2.1: Protected live shot state (prototype implemented)
* Story 2.2: Live Continuity Rail (prototype implemented)
* Story 2.3: Live coverage interruption warning (prototype implemented)

### Epic 3: PiP Review Deck
* Story 3.1: Draggable PiP review panes
* Story 3.2: Review pane offset controls

### Epic 4: Constellation Review and spatial event graph
* Story 4.1: Camera and zone nodes
* Story 4.2: Observation nodes
* Story 4.3: Evidence quality markers

### Epic 5: Spoken dictation and commands
* Story 5.1: Voice command controller
* Story 5.2: Dictation capture
* Story 5.3: Voice safety controls

### Epic 6: Active Duty Stack and concurrent incident threads
* Story 6.1: Active Duty Stack
* Story 6.2: Concurrent incident threads
* Story 6.3: Lunch coverage mode

### Epic 7: Evidence Registry, Retention Ledger, and VLAN-aware design
* Story 7.1: Evidence Registry metadata model
* Story 7.2: Stakeholder report graph
* Story 7.3: Retention status tracker
* Story 7.4: Security mobile evidence intake gateway
* Story 7.5: Surveillance review queue for field-submitted evidence
* Story 7.6: Radio traffic audio ingestion and transcription

### Epic 8: Recall Search for old exports
* [x] Story 8.1: Natural-language search parser
* [x] Story 8.2: SQLite full-text search index (FTS5)
* [x] Story 8.3: Search result cards

### Epic 9: Admin Governance Console and policy ingestion
* [x] Story 9.1: Admin document upload
* [x] Story 9.2: Source Registry and versioning
* [x] Story 9.3: Policy retrieval with citation display
* [ ] Story 9.4: Jurisdiction-specific public regulatory packs for `gaming-us-tribal`, `gaming-us-nv`, and `gaming-macau` (stretch)
* [ ] Story 9.5: Multilingual source, translation, and operational-meaning layers for Macau and other non-English jurisdictions using official public source text plus reviewed operational interpretation (stretch)

### Epic 10: Emergency Plan Assistant
* Story 10.1: Emergency plan gap check
* Story 10.2: Scenario annex builder
* Story 10.3: Incident-to-plan improvement loop

### Epic 11: Evacuation Accountability and roster integration
* Story 11.1: Emergency roster snapshot import
* Story 11.2: Evacuation Accountability Board
* Story 11.3: Evacuation voice commands

### Epic 12: Authority Matrix and Authority Lanes
* [x] Story 12.1: Authority Matrix configuration (RBAC Module)
* [x] Story 12.2: Authority lane routing
* [x] Story 12.3: Review and approval trail (Gaming Commission Signatures & Telephonic)

### Epic 13: SafeTask Field standalone and SCC module
* Story 13.1: Field safety event schema
* Story 13.2: SCC safety handoff
* Story 13.3: JHA draft assistant

### Epic 14: Audit, permissions, and deployment hardening
* [x] Story 14.1: Role-based access controls (Implemented across Dispatch, Surveillance, Admin, Auditor)
* [x] Story 14.2: Action audit log (Evidence hashes, authorization timestamps)
* [x] Story 14.3: Local-first deployment profile

### Epic 15: Demo data and story-driven validation
* Story 15.1: Synthetic casino incident scenarios
* Story 15.2: Demo script for Live Continuity Deck
* Story 15.3: Demo script for Recall Search

### Epic 16: Security Management & Dispatch (iTrak Competitor)
* [x] Story 16.1: Role-based evidence and report gating (Credentials check)
* [ ] Story 16.2: Dispatch log and officer task tracking
* [ ] Story 16.3: Lost and found registry
* [x] Story 16.4: Secure distribution queue for photos/video exports (Self-Destructing LE Portal)

### Epic 17: Physical Security Systems Integration (Keywatcher & ACS)
* Story 17.1: Keywatcher API/syslog ingestion for real-time key events
* Story 17.2: Overdue key alerts and automatic dispatch routing
* Story 17.3: Auto-correlation between key pulls and camera timeline pinning
* Story 17.4: Secure key audit ledger
* Story 17.5: Access Control System (ACS) integration for badge swipe alerts
* Story 17.6: High-value key/badge usage triggers automated PiP camera spawn

### Epic 18: Biometric Subject Management
* [x] Story 18.1: Subject Database with facial hashes and gait profiles
* [x] Story 18.2: Biometric Profiles Directory
* [x] Story 18.3: Biometric Camera Feed Scanner
* [x] Story 18.4: Human-in-the-Loop Verification Module
