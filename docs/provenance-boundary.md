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

Implementation and migration checks are recorded below as the remediation is verified.
