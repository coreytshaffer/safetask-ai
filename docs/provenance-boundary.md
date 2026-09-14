# Source provenance boundary (A01-A02)

This remediation ships no approved regulatory or facility-policy sources.
`policy/reviewed_sources.json` is an empty, repository-controlled catalog. Runtime
uploads, source front matter and indexed metadata cannot write it or grant review.

Source kinds are `synthetic`, `external_source`, `facility_policy`, and `unknown`.
Review status is independently `unreviewed` or `reviewed`. A review record binds a
repository-relative path, complete artifact SHA-256, issuer, scope, source version,
locator, review ID and review date. Changing bytes requires review again. This
catalog is a code-review trust boundary, not authentication of a reviewer. A
reviewed source is not automatically applicable law. Facility workflow is deferred.

Retained test fixtures contain `SAFETASK_SYNTHETIC_FIXTURE` in their content and
explicit synthetic labels. Renaming a fixture or strengthening its metadata cannot
approve it. Neither this PR nor its tests approve any real-world source.

## What is enforced

- Source-owned `authority_level`, `review_status`, reviewer names, citations and
  official-domain lists cannot approve a source. `authority_level` remains only
  as a compatibility field and is never rendered as an authority badge.
- The catalog supplies review ID, issuer, scope, locator, version and review date.
  A match requires the exact repository-relative path and SHA-256 of all current
  file bytes, including front matter. Line-ending changes also invalidate the hash.
  Synthetic kinds, retained fixture markers and test-fixture locations cannot be
  approved. Missing/invalid catalogs fail closed.
- Chroma ranks IDs. It never supplies returned text or authority. Retrieval reads
  current contained source paths, rebuilds Markdown/PDF units, and compares unit ID,
  path, content hash and complete derived provenance with indexed state. Removed,
  modified, moved or revoked material is rejected. Cards are revalidated before
  return and again at incident adaptation; errors discard the entire adapted set.
- Only `field_docs_provenance_v1` is readable. There is no `field_docs` fallback.
  Rebuild deletes/recreates the new collection and marks it ready only after all
  units succeed. A failed build cannot serve partial results. In-process locking
  and generation checks reject an index replacement during retrieval.
- Search distinguishes `ready` (including zero usable matches), `index_required`,
  and `retrieval_unavailable`. Incident packets additionally distinguish
  `no_reviewed_sources` from `reviewed_sources`. The former describes the usable
  results for that search; it is not a legal determination.
- Gaming packs require both `validate_approved_pack` and content-bound catalog
  review as an external source. Permitted domains come from the trusted record.
  All three HTTP serving routes and CLI `--approved` apply that same boundary.
  The generic gaming route always returns non-cacheable 410. Upload publication
  returns non-cacheable 410 before reading or writing an upload.
- APIs, CLI, source cards and incident packets preserve derived provenance.
  Incident rendering suppresses an incomplete/malformed source set. Legacy
  print, PDF, portal and email output identify policy sources as unverified.
  No retrieval/type error supplies substitute regulations or fixed regulatory
  escalation instructions.

## Exact patch manifest

Paths are relative to this repository. This is one remediation unit.

| Paths | Change |
|---|---|
| `safetask/core/provenance.py`; `policy/reviewed_sources.json`; `data/schema.json`; `src/rag/schema.py` | Minimal content-bound contract, empty trusted catalog, serializable cards and labels. |
| `data/documents/state_water_reg_402.md`; `safetask/domains/gaming/regulations.json` | Delete original A01/A02 fixtures. |
| `tests/fixtures/synthetic/water_policy.md`; `tests/fixtures/synthetic/gaming_policies.json`; `safetask/domains/gaming/test_gaming_rag.js` | Neutral marked test fixtures and their matcher. |
| `src/rag/indexer.py`; `src/rag/retriever.py` | Replacement index, current-source reconstruction, fail-closed validation/status. |
| `safetask/core/regulation_pack.py`; `safetask/apps/legacy_scc/app.py`; `safetask/apps/legacy_scc/server.py`; `safetask/apps/surveillance_command_center/server.py` | Shared approved-pack/catalog boundary and retired gaming route. |
| `safetask/core/doc_processor.py` | Disable direct publication. |
| `safetask/api/router.py`; `src/web/app.py`; `src/cli.py` | Typed card adaptation, explicit errors, source labels, no fabricated fallback. |
| `src/web/static/app.js`; `safetask/web_ui/app.js`; `safetask/web_ui/index.html` | Preserve provenance in presentation and clear/suppress unusable results. |
| `safetask/apps/legacy_scc/index.html`; `safetask/apps/legacy_scc/app.js`; `safetask/apps/legacy_scc/portal.html`; `safetask/core/pdf_engine.py` | Remove duplicated policy cards, disable publication controls, label legacy outputs unreviewed. |
| `safetask/apps/legacy_scc/sw.js`; `safetask/apps/legacy_scc/provenance-migration.js` | Independent migration, owned-cache cleanup, no cached policy/API fallback, explicit user-controlled reload. |
| `archive/scratch/epic9.js`; `field_aware_mvp.zip` | Remove obsolete policy UI and current archive distribution. |
| `data/chroma_db/chroma.sqlite3`; `data/chroma_db/86f09db9-2064-490e-a20b-a0172f769dc7/data_level0.bin`, `header.bin`, `length.bin`, `link_lists.bin`; `src/data/chroma_db/chroma.sqlite3` | Remove the tracked obsolete corpus. |
| `src/rag/__pycache__/indexer.cpython-314.pyc`, `retriever.cpython-314.pyc`, `schema.cpython-314.pyc`; `src/web/__pycache__/app.cpython-314.pyc`; `safetask/api/__pycache__/router.cpython-314.pyc`; `tests/__pycache__/test_rag.cpython-314-pytest-9.0.3.pyc` | Remove affected executable residue. |
| `.gitignore`; `requirements-provenance.txt` | Prevent index/archive republishing; declare focused runtime/test dependencies. |
| `tests/test_rag.py` | Replace the old download-dependent RAG test with deterministic boundary tests. |
| `tests/conftest.py`; `tests/test_provenance.py`; `tests/test_retrieval_boundary.py`; `tests/test_policy_delivery.py`; `tests/test_source_presentation.py`; `tests/test_provenance_distribution.py`; `tests/browser/provenance.cjs` | Regression and migration verification below. |
| `docs/provenance-boundary.md`; `docs/schemas/regulation-pack.md` | Contract, migration, verification, limitations. |

Three small prerequisites were also corrected in the affected interfaces: a
duplicate Flask endpoint registration prevented import; the CLI search parser
rejected its query argument; and a missing brace prevented the SafeTask UI script
from parsing. These do not change authentication, reviewer permissions or custody.

## Deployment and data/cache migration

1. Deploy all remediation commits together after human review. Do not publish an
   intermediate commit. Stop old application processes before updating a local
   installation; do not continue running an old binary against the new checkout.
2. Install the focused dependencies in the application's environment. Run with
   the updated Python source. Remove only the listed retired tracked artifacts.
   Do not package a previous ZIP, a persistent Chroma directory, or stale bytecode.
   The distribution test checks the remaining current ZIP recursively without
   executing it; no historical archive clearance is implied.
3. Keep the supplied review catalog empty. Existing external/local reference
   documents remain unreviewed. A former local `field_docs` collection may remain
   on disk but is permanently ignored by this code. It is neither migrated nor
   used as a rebuild source. No broad deletion of user databases is required.
4. Rebuild from current source files using the existing CLI from the repository
   root: `python src/cli.py index`. That CLI also requires its existing FieldAware
   dependencies. Alternatively, with this repository and `src` on Python's import
   path, call `DocumentIndexer().index_directory()` from `rag.indexer`.
   The normal embedding model must already be available for offline operation;
   deterministic test embeddings are not a production index. A missing index
   yields `index_required`; an interrupted build yields `retrieval_unavailable`.
5. Rebuilds replace only `field_docs_provenance_v1`. Verify its returned unit count,
   query current reference files, and confirm their unreviewed labels. Approved
   incident sources should be empty with the shipped catalog. Source/catalog
   changes require rebuilding for newly eligible results; stale review is rejected
   even before a rebuild.
6. Serve the corrected legacy page, standalone migration script and worker at
   their existing origin/scope. Installation precaches corrected shell assets with
   HTTP-cache bypass, using `safetask-ai-provenance-v2`. Activation removes only
   obsolete `safetask-ai-*` caches and claims clients. It never navigates them.
   APIs and policy packs are never cached; retired gaming returns 410 even offline,
   other unavailable policy/API requests return 503 with empty entries.
7. The corrected page checks its own version and the activated controlling worker,
   then reports migration complete. A new worker controlling an old open page is
   not sufficient. Save unsaved work before choosing reload. An old page without
   the new listener may not display the notification; operators must reconnect
   and deliberately load the corrected page. No automatic reload is used.
8. Verify a corrected page and active v2 worker while online, then repeat offline.
   A permanently offline client still running the old application cannot be
   remotely remediated by this release. Historical downloads, old tabs and old
   deployments remain outside current-tree containment until their owners update.

## Verification matrix

| Check | Automated coverage |
|---|---|
| T1: source metadata cannot approve itself | Five source kinds; supplied review/authority fields ignored. |
| T2: synthetic material cannot be reviewed | Renamed/stronger-metadata fixture with an otherwise matching test catalog; schema rejects synthetic reviewed state. |
| T3: current trusted content binding | External/facility records; modified bytes, revocation, review replacement and malformed/duplicate catalog. |
| T4: stale index and migration | Legacy-only index, absent index, valid empty build, replacement rebuild, failed build, rebuild during query; removed/moved/hash/path/unit/provenance mismatches. |
| T5: end-to-end source data | Real local Chroma with deterministic embeddings; forged cached text ignored; Markdown/PDF page/hash/provenance round trip; serialized schema. |
| T6: API and incident errors | Actual route bodies, typed incident adaptation, unreviewed/missing/error/partial/revoked results; saved packet equality; no fallback regulation/escalation. |
| T7: presentation | Actual CLI body and browser renderer bodies; source kind/status/scope/page labels; stale/partial card suppression; every generated PDF page labelled. |
| T8: all gaming servers | Flask route and both stdlib HTTP dispatch handlers; approved test-only pack positive control and rejection cases; 410/no-store generic route. |
| T9: publication and approved-pack gate | Disabled upload before file read/write; legacy array, source-owned domains, missing review, malformed and modified packs rejected. |
| T10: browser cache migration | Real headless Edge, old worker/cache/open form; no forced reload; unrelated cache retained; corrected page plus active worker; online/no-cache and offline/no-fallback checks. |
| T11: current distribution | Git-tracked paths, recursive current ZIP membership, empty catalog, neutral fixtures, duplicate HTML authority cards, affected bytecode/index/archive absence. |

Run the focused Python suite:

```text
python -B -m pytest tests/test_provenance.py tests/test_retrieval_boundary.py tests/test_policy_delivery.py tests/test_source_presentation.py tests/test_provenance_distribution.py -q
node tests/browser/provenance.cjs
node safetask/domains/gaming/test_gaming_rag.js
```

Install Playwright for the browser test; it uses installed Edge by default.
`SAFETASK_TEST_BROWSER` can select another Chromium executable. The test serves
only a temporary loopback origin; external browser requests are blocked.
Python tests use temporary catalogs/databases, deterministic embeddings and a
socket guard. Windows' event-loop socket pair is initialized before that guard.
No LLM or external service is used during tests.

Validation environment: Python 3.12, Chroma 1.5.9, Node 24.19.0,
Microsoft Edge 152.0.4191.66.

Final September 11 implementation verification:

- Python suite: **66 passed, 1 warning in 8.35s**. The warning is the existing
  PyPDF2 deprecation, encountered when testing that upload processing is disabled.
  Includes source/review changes during gaming pack reads.
- Real-browser checks: **5/5 verification groups passed**, including migration,
  offline behavior, incident rendering and search rendering.
- Synthetic gaming matcher: **3/3 passed**.
- Syntax/data checks: **19 changed Python files parsed**, **3 changed JSON files
  parsed**, and **4 affected JavaScript scripts passed Node syntax checks**.
  The independent legacy migration was tested with the old broken application
  script present. The legacy script itself is not counted as a syntax pass.
- Git diff whitespace checks passed. The current-tracked-tree and recursive
  current-ZIP distribution checks passed as part of the Python suite.

## Limits, risks and rollback

- The catalog is a repository trust boundary, not proof that a named reviewer
  authenticated. No administration system, approval workflow, external approval
  service, new real-world review, or facility-policy workflow is introduced.
- Corpus removal reduces available retrieval. The approved behavior is an
  explicit unavailable/no-reviewed-source state. Downstream clients must handle
  the new statuses, provenance-bearing objects, nullable page and 410 route.
- The full application/LLM/GIS suite and production deployment were not exercised.
  API/CLI bodies and renderer bodies were exercised without unrelated startup
  side effects or model downloads. Other browsers and existing user installations
  require rollout verification. This is not a claim that all legacy features work.
- The old `safetask/apps/legacy_scc/app.js` has pre-existing syntax damage beyond
  this PR. The independent worker migration was tested despite it. Policy
  publication remains disabled; this PR does not restore the legacy application.
- Do not roll back by restoring old JSON, indexes, archives, fabricated guidance
  or cached policy. If a release fails, disable affected serving or deploy a
  corrective release retaining these boundaries. Rebuild only from current sources.
- Deleting `field_aware_mvp.zip` also removes its nested privacy/history material
  from the current tree. A03 historical exposure needs separate review: existing
  Git history and previously published copies were not rewritten or removed.
- A04 (SafeGate), A05 (Clear Lake Watch), and the broader A06 marketing/custody/
  profile work are out of scope. SafeTask README/profile claims, unrelated logs,
  SQLite databases, bytecode, and the previously inspected Clear Lake export ZIP
  remain unchanged. Narrow wording changes above are only for A01/A02 presentation.
- No merge, push, release, account-setting change, or change to another repository
  is part of this implementation.
