---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0008
release_version: v0.2.7
kind: added
summary:
  Added opt-in policy controls for spelling bounded undotted uppercase initialisms
  with source, upper, or lower casing
status: accepted
audience: null
scopes: []
source_refs:
  - tl:task-0029
paths:
  - abbr2words/initialisms.py
  - abbr2words/api.py
  - abbr2words/core.py
  - tests/test_undotted_initialisms.py
issues: []
prs: []
sources: []
contributors: []
breaking: false
internal: false
order: 8
---

Preserves dotted-only and semantic registered expansion defaults while exposing source-aligned fallback provenance, protected-span safeguards, Roman-like exclusions, and metadata-driven registered initialism surface spelling for downstream TTS orchestration.
