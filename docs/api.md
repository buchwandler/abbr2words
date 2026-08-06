# API reference

## Convenience functions

```{autofunction} abbr2words.abbr2words

```

`abbr2words(..., annotations=...)` accepts an iterable of source-aligned
`TokenAnnotation` objects. Their offsets refer to the original input text;
labels are normalized and overlapping or invalid spans raise `ValueError`.
Missing lexical POS evidence fails open, and numeric unit guards remain
authoritative.

Abbreviation boundaries use symmetric Unicode word-character lookarounds:
registered spellings may start or end with punctuation, but cannot attach to a
surrounding `\w` character. Optional `protected_spans=[(start, end), ...]`
prevents replacements in caller-owned ranges such as URLs, markup, or code.

For source-aligned diagnostics, use `Expander.expand_with_trace(...)`. It
returns an `ExpansionResult` containing expanded text and deterministic,
non-overlapping `ExpansionMatch` records. Existing convenience calls continue
to return strings.

The bundled language registry includes `cs`, `de`, `en`, `es`, `fr`, `it`, `nl`,
`pl`, `pt`, `ru`, `sv`, and `tr`. Turkish unit symbols followed by straight or
curly apostrophe suffixes are intentionally not expanded until suffix
realization is implemented.

```{autofunction} abbr2words.expand

```

```{autofunction} abbr2words.normalize_language

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
sensitivity and whether a numeric value is required.

```python
abbr2words("500 g", lang="en")  # "500 gram"
abbr2words("section g", lang="en")  # "section g"
```

## Core types

```{autoclass} abbr2words.TokenAnnotation
:members:
```

```{autoclass} abbr2words.AbbreviationEntry
:members:
```

`AbbreviationEntry.only_if_pos` and `not_if_pos` accept coarse POS labels such
as `NOUN`, `PROPN`, and `ADP`. They are evaluated only when annotations are
provided. `Expander.add()` exposes the same optional `only_if_pos` and
`not_if_pos` keyword arguments.

```{autoclass} abbr2words.AbbreviationContext
:members:
```

```{autoclass} abbr2words.AbbreviationExpander
:members:
```

The public `abbr2words.core.abbreviation_guards_match()` helper accepts either
an `AnnotationIndex` or an annotation iterable. Iterable input is normalized
and validated the same way as expansion. It evaluates coarse `pos` only;
provider-specific `tag` values are retained but not matched.
