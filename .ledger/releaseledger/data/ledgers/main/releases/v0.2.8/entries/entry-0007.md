---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0007
release_version: v0.2.8
kind: changed
summary:
  Hardened conservative undotted initialism handling and expanded reviewed
  locale coverage
status: accepted
audience: null
scopes: []
source_refs:
  - tl:task-0033
paths:
  - abbr2words/initialisms.py
  - abbr2words/core.py
  - abbr2words/language_data/initialisms.py
  - tests/test_initialism_false_positives.py
issues: []
prs: []
sources: []
contributors: []
breaking: false
internal: false
order: 7
---

Unknown two-letter and vowel-bearing uppercase words now remain unchanged in conservative mode, while reviewed technical aliases and locale initialisms provide explicit spelling coverage. Registered initialisms expand beside lexical hyphen compounds without claiming code-like identifiers.
