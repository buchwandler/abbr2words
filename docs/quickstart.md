# Quickstart

The main convenience function expands known abbreviations while preserving the
rest of the input:

```python
from abbr2words import abbr2words

text = "Prof. Klein kommt ggf. am Fr."
print(abbr2words(text, lang="de"))
# Professor Klein kommt gegebenenfalls am Freitag
```

Locale forms and common aliases use exact-locale-first resolution with base fallback:

```python
abbr2words("Prof. Klein", lang="de-DE")
abbr2words("Prof. Klein", lang="ger")
normalize_language("pt-BR")  # "pt_BR"
normalize_language("en_GB")  # "en"
```

Context detection is enabled by default. For German `Fr.`, the surrounding text
can distinguish a title from the weekday:

```python
abbr2words("Fr. Klein", lang="de")       # Frau Klein
abbr2words("Fr. Klein", lang="de", context=False)  # Freitag Klein
```

The `context` choice applies to each call and is independent of earlier calls.

The generic `DATE` context is bounded: a custom date-sensitive rule can use
numeric evidence such as `5 X. 2026`, but the package does not parse or
normalize complete dates.

The package expands abbreviations and reviewed unit symbols after numeric
quantities. Ordinary numeric values are preserved, while unit symbols such as
`500 g` can become `500 gram`. Complete number wording, dates, times, currency
realization, measurement conversion, and grammatical agreement remain outside
this package. The input must be a string; a non-string raises `TypeError`, and
an unknown language raises `ValueError`. `base_language("pt-BR")` returns `"pt"`.
