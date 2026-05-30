# SafeTask Domain Packs

Domain packs keep SafeTask source-bound and jurisdiction-aware.

The current `gaming` folder is the legacy demo pack used by the prototype UI. Future public regulatory packs should use stable IDs that name both domain and jurisdiction, such as:

- `gaming-us-tribal`
- `gaming-us-nv`
- `gaming-macau`

## Multilingual Pack Rule

Do not collapse multilingual source material into a single English summary. A jurisdiction pack should preserve:

1. Original `source_text`
2. Close `literal_translation`
3. Reviewer-approved `operational_interpretation`

The UI may show the user's preferred language first, but exports and reviewer views should retain traceability to the original source language.

## Macau Source Review Policy

Macau source acquisition is official public sources only.

Acceptable source roots for initial scaffolding:

- Macao SAR Government Portal
- Gaming Inspection and Coordination Bureau (DICJ)
- MSAR Official Gazette / legislation pages

Macau uses this model:

```text
official source text
-> human-reviewed literal translation
-> reviewer-approved operational interpretation for surveillance users
```

Draft source entries may be stored before review, but they must stay labeled `needs_review`. Operator-facing guidance requires `source_policy: official_public_sources_only`, `review_status: approved`, named translation review ownership, named operational interpretation ownership, source URLs matching declared official domains, and entry confidence `reviewed_operational_interpretation`.
