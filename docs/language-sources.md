# Language sources and review policy

This document records the reviewed source basis for the bundled language
registries. The pinned `num2words` range is a candidate filter for number
spelling; it is not an abbreviation or morphology dependency.

## Registry scope

The registry contains the 49 base keys and 14 explicit locale overlays pinned in
`tests/data/num2words_language_registry.json`. Each new base has a conservative
seed inventory and the reviewed common duration, length, area, volume, mass,
temperature, and speed unit subset. Locale entries inherit their base and add
structured local currency identities in numeric context. Every seed carries a
source ID; `scripts/audit_language_data.py` verifies that IDs resolve and that
duplicate, alias, custom-boundary, and identity-rule policies are respected.

The development importer is deterministic and offline:

```console
python scripts/import_cldr_language_data.py \
  --cldr-root ../cldr-json --cldr-version 48.2.1 \
  --languages am ar ... zh --check
python scripts/audit_language_data.py
```

It reads only the pinned fields used by this package and never runs during
import, build, or normal runtime.

The source/review ledger for the newly added bases is intentionally explicit:

| Group                | Codes                                                                                           | Primary language/orthography source                          | Unit source     | Review status                                                   |
| -------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | --------------- | --------------------------------------------------------------- |
| Latin                | `ca`, `cy`, `da`, `eo`, `fi`, `hu`, `id`, `is`, `lt`, `lv`, `no`, `ro`, `sk`, `sl`, `tet`, `vi` | national orthography/abbreviation guidance; CLDR locale data | BIPM SI + CLDR  | conservative agent seed; native review pending                  |
| Cyrillic             | `be`, `kz`, `mn`, `sr`, `tg`, `uk`                                                              | national orthography and abbreviation guidance               | BIPM SI + CLDR  | conservative agent seed; native review pending                  |
| RTL                  | `ar`, `fa`, `he`                                                                                | national orthography guidance                                | BIPM SI + CLDR  | conservative agent seed; native review pending                  |
| Indic                | `bn`, `hi`, `kn`, `te`                                                                          | national orthography guidance                                | BIPM SI + CLDR  | conservative agent seed; native review pending                  |
| East/Southeast Asian | `th`                                                                                            | national orthography guidance                                | BIPM SI + CLDR  | conservative agent seed; native review pending                  |
| Mandarin Chinese     | `zh`                                                                                            | PRC legal measurement terminology; MOE translation guidance  | GB 3100 + CLDR  | conservative generic Chinese base; Mainland locale reviewed     |
| Korean               | `ko`                                                                                            | NIKL corporate/terminology guidance; KRISS SI terminology    | KRISS SI + CLDR | source-backed reviewed baseline; broader lexical review pending |
| Japanese             | `ja`                                                                                            | NTA organization and government usage guidance               | NMIJ SI + CLDR  | reviewed baseline / source-backed; native review pending        |
| Specialist           | `am`, `az`, `ce`, `hy`                                                                          | national orthography guidance                                | BIPM SI + CLDR  | conservative agent seed; native review pending                  |

Locale overlays are `en_IN`, `en_NG`, `es_CO`, `es_CR`, `es_GT`, `es_NI`,
`es_VE`, `fr_BE`, `fr_CH`, `fr_DZ`, `pt_BR`, `zh_CN`, `zh_HK`, and `zh_TW`.

For Mainland Chinese, the runtime terminology follows the currently effective GB 3100-1993 and the pinned CLDR 48.2.1 data. As of 2026-08-26, GB 3100-1993 remains current; SAMR opened consultation on a replacement draft published 2026-08-17. Draft terminology is not treated as normative until a replacement standard is formally issued.
Czech, English, French, Italian, Portuguese, and Spanish expose reviewed
structured currency identities. Czech recognizes `Kč`/`CZK` as
`currency-czech-koruna`; Portuguese recognizes `R$`/`BRL` as
`currency-brazilian-real`; English, French, Italian, and Spanish reuse the
shared `€`/`EUR`, `$`/`USD`, and `£`/`GBP` identities. These are recognition
metadata only: the API preserves source spans and numeric lexemes but does not
perform currency arithmetic, plural/agreement selection, or number-to-word
realization. French also exposes dotted numeric duration aliases `min.` and
`sec.`; a standalone French `min.` remains the lexical abbreviation for
`minimum`, while numeric context selects the structured `duration-minute`
identity. Downstream consumers such as `spokenform` own semantic grammar and
speech realization.

Unit expansions are canonical lemmas. They intentionally do not realize plural,
case, numeral government, gender, vowel harmony, or apostrophe-attached suffixes.
Turkish unit symbols followed by `'` or `’` remain unchanged under the restricted
first-release policy.

## Swedish source ledger

The Swedish registry uses the following sources by scope:

- **ISOF, Språkrådet, Snabba skrivregler, 2024**. Lexical abbreviation spelling, including `ca`, prose abbreviations, and weekday forms. https://www.isof.se/utforska/publikationer/publikationer/2024-01-22-snabba-skrivregler
- **ISOF, Myndigheternas skrivregler, section 11.4**. Numeric and reference abbreviations such as `bil.`, `ca`, `kap.`, `kl.`, `nr`, `s.`, `tfn`, and `tim`. https://www.isof.se/download/18.17dda5f1791cdbd2873a99/1620030264840/Mynd-skrivreg2014-1.pdf
- **ISOF Frågelådan, FAQ 22308**. Formal spelling recommendation for `p.g.a.`. https://frageladan.isof.se/faqs/22308
- **ISOF Frågelådan, FAQ 22191**. Current dotted weekday abbreviations. https://frageladan.isof.se/faqs/22191
- **Unicode CLDR 49 Swedish locale data**. Localized unit and shared currency display labels. https://unicode.org/cldr/charts/49/summary/sv.html and https://www.unicode.org/cldr/charts/49/by_type/units.energy_and_power.html
- **Sveriges Riksbank, Valutakoder**. Swedish krona identity, `SEK`, and `krona`. https://www.riksbank.se/sv/statistik/rantor-och-valutakurser/forklaringar---rantor-och-valutakurser/valutakoder/

The Swedish implementation keeps compact undotted weekday and month table forms, initialisms, ambiguous abbreviations, pluralization, and time normalization out of this change. Unit expansions remain canonical labels without Swedish inflection.

## Source authority

- `num2words` v0.5.14 release registry: candidate-language compatibility baseline.
- BIPM SI Brochure: canonical SI symbols and capitalization.
- Unicode CLDR unit and date/time data: localized unit and calendar guidance.
- Taaladvies: Dutch abbreviation, date, title, and SI-symbol guidance.
- ISOF: Swedish abbreviation and number/unit spacing guidance.
- Rada Języka Polskiego: current Polish spelling, abbreviations, month names, and
  unit-spacing guidance, including the 2026 spelling change notice.
- Gramota and GOST R 7.0.12-2011 guidance: Russian graphical abbreviations.
- Türk Dil Kurumu: Turkish abbreviation, abbreviation-index, and punctuation
  guidance.
- ISO 4217: currency codes and locale currency identities.
- National Tax Agency: organization-name abbreviations and parenthesized `(株)`/`(有)` forms.
- NMIJ/AIST: Japanese SI terminology and unit names.
- Unicode CLDR Japanese locale data: localized display names and quantity patterns.
- Japanese government usage examples: suffixal page markers and address counters.
- National Institute of Korean Language: `(주)`/`㈜` corporate abbreviation guidance, `기압`/`atm` terminology, and reviewed Korean initialism spellings.
- KRISS: Korean names and symbols for the International System of Units.
- Unicode CLDR 48.2.1: Korean locale and common-unit quantity guidance.
- PRC State Council legal measurement-unit order and Ministry of Justice database: GB 3100-1993 terminology and statutory units.
- State Administration for Market Regulation: current GB 3100-1993 record and 2026 revision consultation status.
- Ministry of Education / State Language Commission: recommended Chinese translations for reviewed foreign abbreviations.
- Unicode CLDR 48.2.1: Mainland Chinese unit names and quantity patterns.

The checked-in source IDs are `legacy-abbr2words` for compatibility-preserved
entries, `language-style-baseline` for baseline lexical rules, and
`unicode-cldr-48.2.1` for the pinned locale-data baseline. Japanese additionally
uses `ja-nta-organization-abbreviations`, `ja-nmij-si`, and
`ja-government-page-reference-examples`. Korean additionally uses
`ko-nikl-corporate-ju`, `ko-kriss-si`, and `ko-nikl-atmosphere`. Mainland Chinese
uses `zh-cn-prc-legal-units`, `zh-cn-moe-foreign-terms-batch-1`,
`zh-cn-moe-foreign-terms-batch-6-7`, and `unicode-cldr-48.2.1`. Review status is
`legacy-preserved`, `generated-reviewed`, or `linguistically-reviewed` as
appropriate. Japanese is reviewed baseline and Korean is a source-backed reviewed
baseline with broader lexical abbreviation review pending; Mainland Chinese is a
source-backed locale enhancement. This repository does not claim native-speaker
sign-off for the complete registries.

## Per-language ledger

| Codes                                                                                        | Source ID                                                                                                              | Categories                                                                    | Status                                                          |
| -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `am ar az be bn ca ce cy da eo fa fi he hi kn kz lt lv mn no ro sk sl sr te tet tg th uk vi` | `language-style-baseline`, `unicode-cldr-48.2.1`                                                                       | guarded reference/title baseline and neutral units                            | linguistically-reviewed pending native review                   |
| `zh`                                                                                         | `legacy-abbr2words`, `unicode-cldr-48.2.1`                                                                             | guarded № reference and neutral generic units                                 | conservative generic base; plain Han words remain unchanged     |
| `ko`                                                                                         | `ko-nikl-corporate-ju`, `ko-kriss-si`, `ko-nikl-atmosphere`, `unicode-cldr-48.2.1`                                     | № and organization abbreviations; complete common units; reviewed initialisms | source-backed reviewed baseline; broader lexical review pending |
| `ja`                                                                                         | `ja-nta-organization-abbreviations`, `ja-nmij-si`, `ja-government-page-reference-examples`, `unicode-cldr-48.2.1`      | guarded № and structural organization abbreviations; complete common units    | reviewed baseline / source-backed; native review pending        |
| `cs de en es fr it nl pl pt ru sv tr`                                                        | `legacy-<code>` plus pinned common sources                                                                             | preserved mature lexical registry and structured quantities                   | legacy-preserved; parity tested                                 |
| `en_IN en_NG es_CO es_CR es_GT es_NI es_VE fr_BE fr_CH fr_DZ pt_BR zh_HK zh_TW`              | locale overlay modules plus ISO 4217/CLDR                                                                              | numeric currency and locale-specific overlay data                             | generated-reviewed                                              |
| `zh_CN`                                                                                      | `zh-cn-prc-legal-units`, `zh-cn-moe-foreign-terms-batch-1`, `zh-cn-moe-foreign-terms-batch-6-7`, `unicode-cldr-48.2.1` | Mainland semantic abbreviations and complete localized common units           | source-backed reviewed locale                                   |

The brief that introduced this registry was reviewed on 2026-08-06. The
implementation preserves a source description on each seed category and keeps
ambiguous entries guarded or omitted. Native-speaker sign-off remains a human
review prerequisite; this agent does not claim that review has occurred.

## Known limitations

- Russian numeral government and Turkish suffix realization are not performed.
- Dotless Dutch day forms, Polish one-letter ambiguities, Russian one-letter
  forms, and Turkish locale-sensitive casing are not guessed.
- The examples for the five added languages are abbreviation-only until their
  optional speech-number morphology is separately reviewed.
