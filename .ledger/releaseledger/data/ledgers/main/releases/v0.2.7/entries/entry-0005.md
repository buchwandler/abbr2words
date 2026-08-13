---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 4
entry_id: entry-0005
release_version: v0.2.7
kind: changed
summary:
  Changed ambiguous English dotted forms to prefer letter readings without
  positive place evidence
status: accepted
audience: null
scopes: []
source_refs:
  - tl:task-0028
paths:
  - abbr2words/initialisms.py
  - abbr2words/core.py
  - abbr2words/context.py
  - abbr2words/languages/en.py
issues: []
prs: []
sources: []
contributors: []
breaking: false
internal: false
order: 5
---

Uppercase dotted initialisms now expand from source graphemes as a low-priority fallback. English e.g., I.D., compass letters, D.C., and L.A. handling now distinguish semantic abbreviation use from personal and bibliographic initials while preserving registered-rule precedence.
