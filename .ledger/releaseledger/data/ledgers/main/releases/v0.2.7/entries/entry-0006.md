---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 2
entry_id: entry-0006
release_version: v0.2.7
kind: fixed
summary: Fixed compass and geographic expansions that corrupted names and initials
status: accepted
audience: null
scopes: []
source_refs: []
paths:
  - tests/test_initialisms.py
  - tests/test_pykokoro_example_regressions.py
issues: []
prs: []
sources:
  - tl:task-0028
contributors: []
breaking: false
internal: false
order: 6
---

Address and explicit Washington place evidence remain eligible for directional and D.C. semantic expansions; author-initial forms remain letter-spelled.
