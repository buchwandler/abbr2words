---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0003
release_version: v0.2.10
kind: added
summary:
  Added Korean organization abbreviations, reviewed initialisms, and localized
  unit and quantity expansions
status: accepted
audience: null
scopes: []
source_refs:
  - git:d8187af92aa10c741e467f811f27292d26745ed7
paths:
  - abbr2words/language_data/bundles.py
  - abbr2words/language_data/initialisms.py
  - abbr2words/languages/ko.py
  - abbr2words/unit_data/common.py
  - tests/data/registries/ko.json
  - tests/test_ko.py
issues: []
prs: []
sources:
  - git:d8187af92aa10c741e467f811f27292d26745ed7
contributors: []
breaking: false
internal: false
order: 3
---
