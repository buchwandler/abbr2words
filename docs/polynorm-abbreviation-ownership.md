# PolyNorm abbreviation-stage ownership

This document records which PolyNorm observations belong to `abbr2words` and
which must remain in Spokenform or downstream layers. It is a review aid, not a
benchmark ground-truth override.

## Classification vocabulary

- `owned-abbr`: a reviewed lexical abbreviation or guarded expansion variant
  whose source span is owned by `abbr2words`.
- `owned-unit-identity`: a reviewed numeric unit identity with a stable
  canonical ID and locale label. Number verbalization and unit grammar remain
  downstream.
- `spokenform-number`: the abbreviation expands correctly, but a remaining
  number, decimal, date, or quantity rendering problem belongs to Spokenform.
- `spokenform-structured-collision`: a structured recognizer claims a span that
  should have been handled by the lexical stage, or otherwise changes stage
  ownership. Fix the recognizer boundary rather than adding a benchmark-only
  abbreviation rule.
- `grammar-out-of-scope`: article agreement, title grammar, or surrounding
  sentence repair is not an abbreviation expansion responsibility.
- `entity-resolution-out-of-scope`: initials, names, and entities must not be
  expanded from benchmark expectations without a dedicated entity policy.
- `benchmark-questionable`: the source/expected pair is malformed,
  inconsistent, or not a valid normalization contract and must not become
  package data.

## Examples

### Owned by abbr2words

- `Ej. 5 resuelto.` → `Ejercicio 5 resuelto.` through a narrow ordered Spanish
  context variant; ordinary `ej.` remains `ejemplo`.
- Sentence-aware lexical casing for Spanish `Av.`, `vol.`, and `cap.` and
  Italian professional titles such as `Avv.` and `Arch.`.
- French `St`/`St.` and `Ste`/`Ste.` as explicit proper-name `Saint`/`Sainte`
  expansions.
- Scientific unit identities such as `50 kW`, `550 nm`, `60 Hz`, and `0.01 M`
  when a numeric value and the reviewed symbol are present.
- German organization initialisms whose entries represent spelling, such as
  `GmbH` → `G m b H` and `AG` → `A G`; source case is preserved.
- Reviewed English initialisms such as `BBC`, `CBS`, `US`, `UK`, `USA`, `ISBN`,
  `HTML`, `ISO`, `IEC`, `TV`, `NFL`, `NHL`, and `MLB`; these are ordinary
  registry entries and report `abbr:<canonical>` provenance.
- Explicitly spaced ambiguous one-letter units such as `7 B`, `3 A`, and
  `300 K`. Compact `7B`, `3A`, and `5K` are deliberately left for downstream
  structured-code handling because their unit metadata requires a separator.

### Spokenform or structured-stage ownership

- `Abschn. 3.2.`: `Abschn.` can expand to `Abschnitt`; date/number handling of
  `3.2` is downstream.
- `Abb. ... Tab. 2`: both abbreviations can expand while rendering `2` remains
  a number-stage responsibility.
- `max. ... 50`: the abbreviation can expand while plain number rendering
  remains downstream.
- `z.B.` being claimed by a biological-classification recognizer is a
  structured-stage collision, not a reason to weaken or duplicate lexical
  abbreviation data.
- `n. 10`, room-number grouping, and date-year rendering after a month
  abbreviation remain downstream number/date concerns once the lexical span is
  correct.

### Out of scope or questionable

- Do not expand person initials such as `J.-P. Sartre` into full names.
- Do not change articles around titles (`Die` → `Der`) or repair sentence
  grammar around an expansion.
- Do not delete explanatory parentheticals or unrelated words to satisfy a
  malformed expected string.
- Rows with unrelated e-mail text, instruction-like expected text, inconsistent
  punctuation/decimal conventions, or other malformed pairs are
  `benchmark-questionable` and remain quarantined from package rules.

## Non-goals

`abbr2words` does not implement generic cardinal, decimal, ordinal, date, clock,
or currency-amount verbalization; phone, ISBN, VIN, license-plate, stock-ticker,
or product-code rendering; mathematical-expression parsing; URL/e-mail
normalization; entity-name expansion; grammar repair; or deletion of text not
represented by a reviewed abbreviation or unit span.

Compound unit expressions may be recognized compositionally by downstream
logic. This package is not a general UCUM parser and should only add a complete
compound when it is specifically reviewed and represented by the unit registry.

## Opt-in residual initialism policy

Unknown undotted uppercase tokens are intentionally unchanged by the default
API. A downstream speech normalizer should first claim typed structured spans
and then normally call `initialism_mode="conservative_undotted"` for residual
standalone ASCII uppercase tokens. This middle-ground matcher accepts only
three-to-six-letter, consonant-only residual shapes, rejects unknown two-letter
forms, lexical/headline runs, vowel-bearing words, Roman-like strings,
mixed/alphanumeric identifiers, and hyphenated code fragments, and reports
`abbr:initialism-conservative` provenance. The explicit `spell_undotted` mode
remains available when a caller knowingly wants broad spelling. Protected spans
remain untouched.

Reviewed locale registries and explicit lowercase aliases provide coverage for
known initialisms such as common organization names and technical forms like
`html`, `xml`, `xhtml`, `gtk`, `gfdl`, `sql`, and `glsl`. These aliases are
case-sensitive data entries; ordinary words such as `us`, `in`, `as`, `at`, and
`no` are not made globally case-insensitive.

Registered initialisms may expand in lexical hyphen compounds such as
`ZDF-Sendung` and `EU-Richtlinie`. Code-like neighbors remain protected,
including numeric, uppercase-code, compact mixed-alphanumeric, version-like,
and one-character segments such as `ISO-9001`, `HH-GT`, and `FW-1.2.3`.

The output case is independent of recognition: `initialism_case` may be
`source`, `upper`, or `lower`. Registered entries retain their semantic
expansions unless the caller explicitly requests
`registered_initialism_mode="spell"` and the reviewed entry carries
`speech_strategy="spell_source"`. This lets TTS profiles select surface
spelling without weakening the normal lexical registry.

The intended orchestration is:

1. Spokenform or another caller claims numbers, dates, URLs, e-mail addresses,
   phone numbers, stock tickers, product/version codes, and other typed spans.
2. `abbr2words` applies reviewed lexical abbreviations and units.
3. The caller optionally enables residual undotted initialism spelling for
   spans still unclaimed by its structured recognizers.

Use `iter_initialism_diagnostics()` to inspect why a candidate was accepted or
preserved. Diagnostics expose source offsets and stable reasons such as
`registered-semantic`, `conservative-unknown`, `vowel-bearing-unknown`,
`two-letter-unknown`, `lexical-acronym`, `uppercase-run`, `roman-like`,
`structured-candidate`, `hyphenated-code`, and `protected-span`;
benchmark triage must not infer these decisions from a downstream rendering
failure alone.

This policy does not make benchmark-specific rules for `MIT`, `v.`, `Co.`,
`e.g.`, `D.C.`, or language-data disagreements such as Italian `Onlus`.
Lexical acronyms such as `NASA`, `NATO`, `FIFA`, and `UNESCO` remain outside
the reviewed letter-spelling registry.

## Compact unit diagnostics

The separator policy is metadata-driven and defaults to allowing compact forms,
so it does not disable all compact units. For the reviewed collision symbols,
`iter_unit_diagnostics()` reports the source symbol, locale, canonical identity,
and `requires_separator` rejection reason alongside accepted unit decisions.
This makes ownership triage inspectable without moving numeric or structured
normalization into `abbr2words`.
