# Language sources and review policy

This document records the reviewed source basis for the bundled language
registries. The pinned `num2words` range is a candidate filter for number
spelling; it is not an abbreviation or morphology dependency.

## Registry scope

The registry contains the 49 base keys and 14 explicit locale overlays pinned in
`tests/data/num2words_language_registry.json`. Each new base has a conservative
seed inventory and the reviewed common duration, length, area, volume, mass,
temperature, and speed unit subset. Locale entries inherit their base and only
add reviewed local address, currency, or script-specific forms.

The source/review ledger for the newly added bases is intentionally explicit:

| Group | Codes | Primary language/orthography source | Unit source | Review status |
| ----- | ----- | ----------------------------------- | ---------- | ------------ |
| Latin | `ca`, `cy`, `da`, `eo`, `fi`, `hu`, `id`, `is`, `lt`, `lv`, `no`, `ro`, `sk`, `sl`, `tet`, `vi` | national orthography/abbreviation guidance; CLDR locale data | BIPM SI + CLDR | conservative agent seed; native review pending |
| Cyrillic | `be`, `kz`, `mn`, `sr`, `tg`, `uk` | national orthography and abbreviation guidance | BIPM SI + CLDR | conservative agent seed; native review pending |
| RTL | `ar`, `fa`, `he` | national orthography guidance | BIPM SI + CLDR | conservative agent seed; native review pending |
| Indic | `bn`, `hi`, `kn`, `te` | national orthography guidance | BIPM SI + CLDR | conservative agent seed; native review pending |
| East/Southeast Asian | `ja`, `ko`, `th`, `zh` | national orthography guidance | BIPM SI + CLDR | conservative agent seed; native review pending |
| Specialist | `am`, `az`, `ce`, `hy` | national orthography guidance | BIPM SI + CLDR | conservative agent seed; native review pending |

Locale overlays are `en_IN`, `en_NG`, `es_CO`, `es_CR`, `es_GT`, `es_NI`,
`es_VE`, `fr_BE`, `fr_CH`, `fr_DZ`, `pt_BR`, `zh_CN`, `zh_HK`, and `zh_TW`.

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
