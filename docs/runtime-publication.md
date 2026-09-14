# Runtime state and repository publication (A03a)

SafeTask creates local databases, logs, note history and optional shoreline data
on demand. Those files are runtime state, and must not be committed or packed into
a distributed archive. This cleanup follows the A01–A02 merge and changes no
application source logic.

The current tree no longer tracks the field log, either field-note database, the
empty PitLens database, 43 bytecode files, or the two accidental Git links at
`data/notes` and `data/clear-lake-watch-repo`. There is no submodule initialization
step for those local paths.

`NotebookDB` still creates SQLite storage and versions Markdown notes in a local
Git repository. The logger still creates `data/logs/fieldaware.log`. PitLens still
initializes its database schema. Map generation works with or without the optional
local `data/clear-lake-watch-repo/data/lake-shoreline.json`. No network sync or
storage redesign is introduced.

Before updating an existing checkout, preserve any runtime data you need in
controlled local storage: a Git update can remove formerly tracked files. A fresh
checkout starts without the previously shipped runtime state. Ignore rules keep
new local state out of ordinary `git add`; force-adding it is rejected by the
publication check below.

The reviewed export bundle at
`data/exports/clear_lake_context_20260602_064501_bundle.zip` and its loose files are
unchanged. Bundle SHA-256:
`f8aed49776e99ea889887a843b062563f344a44b3acaf7d33f57779d90b63230`.

## Publication check

After staging the intended changes and before committing or publishing, run:

```sh
python -B scripts/check_publication.py
```

This read-only command examines the complete Git index, including the staged blob
bytes. It does not substitute edited, missing or ignored working-copy files for
what Git would publish. Resolve conflicts before running it. Re-run after any
further staging. A Git source archive of that checked commit contains those
checked entries; an ad hoc working-directory ZIP is not covered by the index check.
Do not distribute working-directory bundles without separate content review.

The gate rejects databases and SQLite sidecars, bytecode, logs, stored Chroma state,
local runtime checkout paths and runtime-data Git links. ZIP contents are read in
memory recursively, including ZIPs renamed to other suffixes. Embedded `.git`
directories/files, links, encrypted members, ambiguous or duplicate normalized
paths, and runtime residue fail the check. Archive content is never executed or
extracted. Other recognized archive formats are rejected for explicit review;
adding a format requires a reviewed bounded reader and tests.

Limits are five archive levels, 10,000 members and 50 MB expanded bytes shared
across all archives, and 128 MB of unique staged blob bytes. Exceeding a limit
fails closed. This is a publication-residue gate, not a complete secret scanner
or a certification of arbitrary binary content.

No database fixture exceptions are configured, including for empty databases.
A future exception requires an exact repository path, synthetic-content rationale,
approved content digest and focused test in the same reviewed change. Neither an
ignore rule nor an archive member's own metadata grants an exception.

No hosted CI workflow is currently configured. Run this check locally and attach
the result to review; it is not automatically enforced by GitHub.

## Focused verification

Use the existing provenance test dependencies plus `folium` (already listed in
`requirements-fieldaware.txt`). From a disposable working directory, run these
commands with an absolute path to the repository:

```sh
python -B -m pytest /path/to/safetask/tests/test_publication.py /path/to/safetask/tests/test_runtime_publication.py -q -p no:cacheprovider
```

The runtime tests create only synthetic notes and shoreline points, initialize
databases, commit a note in a test-owned local Git repository, generate a map with
the shoreline present/absent, and create ignored bytecode. Imports occur in child
processes after changing to disposable directories. The test never calls note
remote sync or opens the generated map in a networked browser.

Also run the existing commands in [provenance-boundary.md](provenance-boundary.md)
to verify the unchanged A01–A02 boundary. Keep Python bytecode disabled and use a
fresh temporary test directory so this verification does not recreate artifacts
in the source checkout.

## Audit disposition

A03a removes current-tree runtime residue. It does not retract earlier commits,
other branches, historical archives, PR objects or prior downloads. A03b history
retraction remains a separate, gated operation. A01–A02 public closure still needs
deployment and deployed retrieval/cache verification. Authentication, assurance
wording, freshness labels, CI setup and incident-persistence hardening remain
outside this cleanup.
