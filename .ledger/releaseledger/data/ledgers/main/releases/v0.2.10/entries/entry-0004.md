---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0004
release_version: v0.2.10
kind: added
summary:
  Added Mainland Chinese reviewed abbreviations and localized unit and quantity
  expansions
status: accepted
audience: null
scopes: []
source_refs:
  - git:601a91f605cd47d5e8dbb5b12115cf2ee7321e9e
paths:
  - abbr2words/languages/_locales.py
  - abbr2words/languages/zh_CN.py
  - abbr2words/unit_data/common.py
  - abbr2words/units.py
  - tests/data/registries/zh_CN.json
  - tests/test_zh.py
issues: []
prs: []
sources:
  - git:601a91f605cd47d5e8dbb5b12115cf2ee7321e9e
contributors: []
breaking: false
internal: false
order: 4
---
