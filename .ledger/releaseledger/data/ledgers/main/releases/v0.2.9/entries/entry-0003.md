---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0003
release_version: v0.2.9
kind: changed
summary:
  Changed undotted initialism handling to use separator-aware run detection
  and vowel-preserving fallback
status: accepted
audience: null
scopes: []
source_refs:
  - git:bd7f695353ba826fefdfdca0620e06b25acc9540
paths:
  - .ledger/releaseledger/data/ledgers/main/events/events.jsonl
  - .ledger/releaseledger/data/ledgers/main/releases/v0.2.8/entries/entry-0007.md
  - .ledger/releaseledger/data/ledgers/main/releases/v0.2.8/release.md
  - abbr2words/core.py
  - abbr2words/initialisms.py
  - abbr2words/language_data/initialisms.py
  - abbr2words/languages/de.py
  - abbr2words/languages/en.py
  - abbr2words/languages/es.py
  - abbr2words/languages/fr.py
  - abbr2words/languages/it.py
  - docs/api.md
  - docs/changelog.md
  - docs/polynorm-abbreviation-ownership.md
  - scripts/check_benchmark_freshness.py
  - tests/data/registries/de.json
  - tests/data/registries/en.json
  - tests/data/registries/en_GB.json
  - tests/data/registries/en_IN.json
  - tests/data/registries/en_NG.json
  - tests/data/registries/en_US.json
  - tests/data/registries/es.json
  - tests/data/registries/es_CO.json
  - tests/data/registries/es_CR.json
  - tests/data/registries/es_GT.json
  - tests/data/registries/es_MX.json
  - tests/data/registries/es_NI.json
  - tests/data/registries/es_VE.json
  - tests/data/registries/fr.json
  - tests/data/registries/fr_BE.json
  - tests/data/registries/fr_CH.json
  - tests/data/registries/fr_DZ.json
  - tests/data/registries/index.json
  - tests/data/registries/it.json
  - tests/test_benchmark_initialism_regressions.py
  - tests/test_conservative_undotted_initialisms.py
  - tests/test_initialism_false_positives.py
  - tests/test_undotted_initialisms.py
issues: []
prs: []
sources:
  - git:bd7f695353ba826fefdfdca0620e06b25acc9540
contributors: []
breaking: false
internal: false
order: 3
---
