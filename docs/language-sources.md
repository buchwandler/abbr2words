# Language sources and review policy

This document records the reviewed source basis for the bundled language
registries. The pinned `num2words` range is a candidate filter for number
spelling; it is not an abbreviation or morphology dependency.

## Registry scope

The current added registries are Dutch (`nl`), Polish (`pl`), Russian (`ru`),
Swedish (`sv`), and Turkish (`tr`). Locale inputs continue to resolve to the
base registry. The inventories cover common abbreviations and the existing
duration, length, area, volume, mass, temperature, and speed unit subset.

French additionally exposes reviewed structured currency identities for
`€`/`EUR`, `$`/`USD`, and `£`/`GBP`, plus dotted numeric duration aliases
`min.` and `sec.`. These are recognition metadata only: the API preserves
source spans and numeric lexemes but does not perform currency arithmetic,
French plural/agreement selection, or number-to-word realization. A standalone
French `min.` remains the lexical abbreviation for `minimum`; numeric context
selects the structured `duration-minute` identity. Downstream consumers such
as `spokenform` own semantic grammar and speech realization.

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
