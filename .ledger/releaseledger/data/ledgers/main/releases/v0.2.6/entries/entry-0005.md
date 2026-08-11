---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0005
release_version: v0.2.6
kind: docs
summary: Documented the v0.2.6 release handoff and Spokenform dependency baseline
status: accepted
audience: null
scopes: []
source_refs: []
paths:
- docs/changelog.md
issues: []
prs: []
sources:
- tl:task-0023
contributors: []
breaking: false
internal: false
order: 5
---
Current checkout package version: 0.2.6.dev2+g423dcf838.d20260811. Git HEAD at handoff: b94b4e4726f8492828a2648c0e40dba9bf92cee4. Direct package verification: PYTHONPATH=. pytest -q and ruff check abbr2words tests passed; registry, robustness, PyKokoro, and examples suites passed. PolyNorm rerun: unavailable in this checkout. Spokenform minimum dependency for the shipped baseline: abbr2words v0.2.6; no separate Spokenform checkout was available for an actual dependency edit or published tag.
