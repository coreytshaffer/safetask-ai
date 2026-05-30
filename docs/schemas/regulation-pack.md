# SafeTask AI - Regulation Pack Schema

Regulation packs are source-bound jurisdiction modules used by SafeTask RAG. They keep legal or policy source material separate from report-writing examples, operational guidance, and AI-generated drafts.

## Design Rule

For multilingual jurisdictions, SafeTask must preserve three separate layers:

1. `source_text`: the original source language text.
2. `literal_translation`: a close translation of the source wording.
3. `operational_interpretation`: reviewer-approved practical meaning for the user's work context.

The UI should show the user's preferred language first, but it must keep these layers traceable so users can see whether they are reading source text, literal translation, or operational guidance.

## Regulation Pack Object

| Field | Type | Description |
|---|---|---|
| `id` | String | Stable pack ID, such as `gaming-us-tribal`, `gaming-us-nv`, or `gaming-macau`. |
| `domain` | String | Product domain, such as `gaming_surveillance`, `field_safety`, or `emergency_response`. |
| `jurisdiction` | String | Jurisdiction label shown to the user. |
| `issuing_authority` | String | Agency, regulator, company, or other source authority. |
| `source_policy` | String | Source acquisition policy. Use `official_public_sources_only` for Macau. |
| `source_review_model` | String | Review model for the pack. Macau uses `official_source_plus_reviewed_operational_interpretation`. |
| `official_source_domains` | Array[String] | Domains allowed for official source links, such as `gov.mo`, `dicj.gov.mo`, and `bo.dsaj.gov.mo`. |
| `default_language` | String | BCP 47 language tag for the source pack default, such as `en-US`, `zh-Hant-MO`, or `pt-PT`. |
| `supported_languages` | Array[String] | Languages SafeTask can display for this pack. |
| `source_url` | String | Public source URL or internal source registry reference. |
| `effective_date` | String | Date the source became effective, if known. |
| `last_checked` | String | Date SafeTask last checked or refreshed the source. |
| `review_status` | String | `draft`, `translated`, `review_required`, `approved`, `superseded`, or `archived`. |
| `entries` | Array[RegulationEntry] | Individual sections, rules, or policy items. |

## Regulation Entry Object

| Field | Type | Description |
|---|---|---|
| `citation` | String | Official citation or section identifier. |
| `title` | String | Source title or locally approved translated title. |
| `topic_tags` | Array[String] | Search tags such as `surveillance`, `table_games`, `cage`, `drop_count`, or `responsible_gaming`. |
| `source_language` | String | Language tag for the source text. |
| `source_url` | String | Official public source URL for this entry. |
| `source_text` | String | Original source wording or approved excerpt. |
| `literal_translation` | Object | Language-keyed literal translations, e.g. `{ "en-US": "..." }`. |
| `operational_interpretation` | Object | Language-keyed practical meaning approved for users, e.g. `{ "en-US": "..." }`. |
| `applicability_notes` | String | When this entry applies or does not apply. |
| `required_report_fields` | Array[String] | Fields a draft should request when this rule is relevant. |
| `authority_lanes` | Array[String] | Stakeholders who should review related incident output. |
| `translation_reviewed_by` | String | Role or reviewer ID for translation approval. |
| `interpretation_reviewed_by` | String | Role or reviewer ID for operational interpretation approval. |
| `confidence` | String | `source_only`, `machine_translation`, `reviewed_translation`, `reviewed_operational_interpretation`, or `needs_review`. |

## Macau Pack Notes

Macau support should not be treated as a simple English rewrite. SafeTask uses official public sources only for Macau. Official source candidates include the Macao SAR Government Portal, the Gaming Inspection and Coordination Bureau (DICJ), and MSAR Official Gazette / legislation pages. DICJ reference pages should not be treated as controlling legal text when they direct users back to the Official Gazette for Chinese and Portuguese versions.

SafeTask uses the `official_source_plus_reviewed_operational_interpretation` model for Macau: source text is preserved, literal translation is reviewed, and operational interpretation must be approved before it is used as operator-facing guidance. Cross-jurisdiction answers must be labeled as comparisons and must not blend Macau, Nevada, and tribal gaming standards into one universal rule.

## Validation Modes

Use the regulation pack validator in two modes:

```powershell
python -m safetask.core.regulation_pack path\to\regulations.json
python -m safetask.core.regulation_pack path\to\regulations.json --approved
```

The default mode checks structure and allows draft templates. The `--approved` mode requires `review_status` to be `approved`, requires `source_policy` to be `official_public_sources_only`, requires the Macau-style source review model, rejects placeholder reviewer fields, requires source URLs to match declared official domains, and requires entry confidence to be `reviewed_operational_interpretation`.
