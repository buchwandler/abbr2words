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
