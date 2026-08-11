# API reference

## Convenience functions

```{autofunction} abbr2words.abbr2words

```

```{autofunction} abbr2words.abbr2words_with_replacements

```

```{autofunction} abbr2words.iter_unit_matches

```

```{autofunction} abbr2words.iter_unit_diagnostics

```

`abbr2words(..., annotations=...)` accepts an iterable of source-aligned
`TokenAnnotation` objects. Their offsets refer to the original input text;
labels are normalized and overlapping or invalid spans raise `ValueError`.
Missing lexical POS evidence fails open, and numeric unit guards remain
authoritative.

The context enum includes `DEFAULT`, `TITLE`, `PLACE`, `TIME`, `DATE`,
`ACADEMIC`, and `RELIGIOUS`. `DATE` is selected only by bounded numeric or
date-punctuation evidence in the local source window; it does not parse dates.
Language profiles may add stricter policies, and uncased scripts do not use the
cased-letter title heuristic.

Abbreviation boundaries use symmetric Unicode word-character lookarounds:
registered spellings may start or end with punctuation, but cannot attach to a
surrounding `\w` character. Optional `protected_spans=[(start, end), ...]`
prevents replacements in caller-owned ranges such as URLs, markup, or code.

For source-aligned diagnostics or downstream text alignment, use
`abbr2words_with_replacements(...)` or
`Expander.expand_with_replacements(...)`. The immutable `ExpansionResult`
contains the original `source_text`, expanded `text`, and deterministic,
non-overlapping `ExpansionReplacement` records. Replacement offsets refer to
the original input, and applying the records from right to left reproduces the
result exactly. `expand_with_trace(...)` remains as a compatibility view of the
same result. Existing convenience calls continue to return strings.

```python
from abbr2words import abbr2words_with_replacements

result = abbr2words_with_replacements("Prof. Klein, S. 12", lang="de")
print(result.text)
for replacement in result.replacements:
    print(replacement.start, replacement.end, replacement.text, replacement.kind)
```

The bundled language registry follows a 66-key current-master parity snapshot:
49 base keys plus the explicit locale overlays `en_GB`, `en_IN`, `en_NG`,
`en_US`, `es_CO`, `es_CR`, `es_GT`, `es_MX`, `es_NI`, `es_VE`, `fr_BE`,
`fr_CH`, `fr_DZ`, `pt_BR`, `zh_CN`, `zh_HK`, and `zh_TW`. `normalize_language()` returns an exact locale
key when registered and otherwise its base key. Turkish unit symbols followed by straight or
curly apostrophe suffixes are intentionally not expanded until suffix
realization is implemented.

Bundled identity lexical rules are rejected. Locale currencies and similar
structured identities are recognized only in numeric quantity context, while
`iter_unit_matches()` remains the semantic API for canonical IDs and exact
source offsets. Non-English baseline unit replacement text is a localized
neutral label, not a complete quantity grammar.

```{autofunction} abbr2words.expand

```

```{autofunction} abbr2words.normalize_language

```

```{autofunction} abbr2words.base_language

```

```{autofunction} abbr2words.supported_languages

```

```{autofunction} abbr2words.get_expander

```

```{autofunction} abbr2words.get_shared_expander

```

```{autofunction} abbr2words.reset_expanders

```

## Mutable facade

```{autoclass} abbr2words.Expander
:members:
:special-members: __call__
```

## Guarded unit symbols

The stable API expands a reviewed set of unit symbols only when a numeric value
precedes the complete unit expression. Numeric forms such as `500 g`, `500g`,
`1.5 kg`, `1,5 kg`, and `5 km/h` are supported; standalone symbols and attached
words remain unchanged. This is symbol expansion, not number spelling, unit
conversion, or universal UCUM parsing.

The matcher is maximal and fail-closed: larger unsupported expressions such as
`5 km / h`, `1 m^2`, and `2kg-rated` remain unchanged instead of being
partially rewritten. Reviewed aliases include both `µg` and `μg`; unrelated
source characters are not Unicode-normalized. Unit metadata controls case
sensitivity, whether a numeric value is required, and whether a separator is
required between a numeric value and an ambiguous one-letter symbol. The
separator requirement defaults to false for compatibility; reviewed `B`, `A`,
and `K` candidates require spacing so compact identifier-like forms are not
claimed as units.

Unit replacements have `kind="unit"` in the exact replacement result. This
layer expands unit symbols/abbreviations lexically; it does not verbalize the
numeric quantity or choose grammatical singular/plural forms. Callers that
need a phrase such as `zwei Minuten` should consume the complete numeric
quantity in a structured quantity stage before calling abbreviation expansion.

```python
abbr2words("500 g", lang="en")  # "500 gram"
abbr2words("section g", lang="en")  # "section g"
```

## Structured quantity matches

Use `iter_unit_matches()` when a downstream semantic stage needs the recognized
quantity before it performs number or grammar realization:

```python
from abbr2words import iter_unit_matches

source = "Für 1,5 kg Mehl"
match = next(iter_unit_matches(source, "de"))
assert source[match.start : match.end] == "1,5 kg"
assert source[match.value_start : match.value_end] == "1,5"
assert match.value == "1,5"
assert match.symbol == "kg"
assert match.canonical_id == "mass-kilogram"
```

`UnitMatch` is immutable and source-aligned. Its `start:end` range covers the
complete numeric expression and symbol; `value_start:value_end` identifies the
original numeric lexeme exactly. Matches are deterministic, maximal, and
non-overlapping. `protected_spans=[(start, end), ...]` suppresses caller-owned
ranges such as markup, URLs, or code. `overrides` and `suppressed` accept unit
symbols; suppression also accepts a canonical ID.

`iter_unit_diagnostics()` returns the same accepted decisions plus compact
separator-policy rejections with `status="rejected"` and
`reason="requires_separator"`. Each record retains the symbol, locale, and
canonical identity so downstream ownership diagnostics do not need to infer
decisions from replacement text.

The matcher recognizes and identifies quantity symbols. It does not decide how
the complete quantity is spoken: number-to-words conversion, singular/plural
grammar, currency decomposition, and locale-specific decimal policy belong to
the consuming semantic normalizer. Currency and magnitude matches expose their
`category` without turning this package into a structured-number parser.

Reviewed semantic identities include speed, pressure, data, fuel-consumption,
and flow units plus JPY, CHF, INR, KRW, and MXN currencies. The `es_MX`
overlay gives unqualified `$` the Mexican-peso identity while `US$` and `USD`
remain US dollar. These are recognition contracts for a downstream consumer,
not amount or number grammar.

## Core types

```{autoclass} abbr2words.TokenAnnotation
:members:
```

```{autoclass} abbr2words.AbbreviationEntry
:members:
```

`AbbreviationEntry.variants` is an ordered tuple of immutable,
declarative `ExpansionVariant` values. The first variant whose guards match
the original source wins, followed by existing context and default expansion
fallback. Variants do not accept callbacks.

`AbbreviationEntry.case_policy` is `"fixed"` by default. Set it to
`"sentence"` only for reviewed lexical expansions whose canonical stored form
is appropriate in mid-sentence text. The matcher applies it after selecting a
variant or context expansion, and aliases share the entry policy. Dotted
abbreviations retain one final period when their consumed dot is also
sentence-final.

```{autoclass} abbr2words.ExpansionVariant
:members:
```

`AbbreviationEntry.only_if_pos` and `not_if_pos` accept coarse POS labels such
as `NOUN`, `PROPN`, and `ADP`. They are evaluated only when annotations are
provided. `Expander.add()` exposes the same optional `only_if_pos` and
`not_if_pos` keyword arguments.

The abbreviation stage returns lexical replacements with source-aligned spans;
it does not interpret following numbers, dates, decimals, structured
identifiers, article elision, surrounding grammar, or speech rendering. Those
concerns remain with the consuming normalizer, including `spokenform`.

```{autoclass} abbr2words.AbbreviationContext
:members:
```

```{autoclass} abbr2words.ExpansionMatch
:members:
```

```{autoclass} abbr2words.AbbreviationExpander
:members:
```

```{autoclass} abbr2words.ExpansionReplacement
:members:
```

```{autoclass} abbr2words.ExpansionResult
:members:
```

```{autoclass} abbr2words.UnitMatch
:members:
```

```{autoclass} abbr2words.ProtectedSpan
:members:
```

```{autoclass} abbr2words.UnitEntry
:members:
```

The public `abbr2words.core.abbreviation_guards_match()` helper accepts either
an `AnnotationIndex` or an annotation iterable. Iterable input is normalized
and validated the same way as expansion. It evaluates coarse `pos` only;
provider-specific `tag` values are retained but not matched.
