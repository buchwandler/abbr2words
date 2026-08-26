---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0001
release_version: v0.2.11
kind: added
summary: Added immutable source-aligned expansion replacements with exact matched
  text, stable rule identities, and canonical unit identities for downstream normalization
status: accepted
audience: null
scopes: []
source_refs:
- tl:task-0039
- git:37eb9b2a5b62131209ba9cbbe01bdcb8a31a5e25
paths:
- abbr2words/core.py
- abbr2words/_replacements.py
- abbr2words/units.py
- abbr2words/api.py
- abbr2words/__init__.py
- tests/test_expansion_result.py
- docs/api.md
- docs/customization.md
- examples/replacements.py
- README.md
issues: []
prs: []
sources: []
contributors: []
breaking: false
internal: false
order: 1
---
The structured expansion API now exposes accepted edits directly, including lexical registry identity only when available and explicit unit identity across locales and aliases. Generic initialism fallbacks retain rule provenance without leaking it as abbreviation metadata.
