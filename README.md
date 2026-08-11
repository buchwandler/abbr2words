[![PyPI - Version](https://img.shields.io/pypi/v/abbr2words)](https://pypi.org/project/abbr2words/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/abbr2words)
![PyPI - Downloads](https://img.shields.io/pypi/dm/abbr2words)
[![codecov](https://codecov.io/github/buchwandler/abbr2words/graph/badge.svg?token=VaXeMMGZbh)](https://codecov.io/github/buchwandler/abbr2words)

# abbr2words

Multilingual, context-aware abbreviation expansion for text normalization and speech.

This standalone package was extracted from the abbreviation framework and language
registries in `kokorog2p`. It has no runtime dependencies and uses a flat package
layout (no `src/` directory).

## Supported languages

The registry follows the pinned current-master `num2words` key contract. It has
49 base keys:

`am`, `ar`, `az`, `be`, `bn`, `ca`, `ce`, `cs`, `cy`, `da`, `de`, `en`, `eo`,
`es`, `fa`, `fi`, `fr`, `he`, `hi`, `hu`, `hy`, `id`, `is`, `it`, `ja`, `kn`,
`ko`, `kz`, `lt`, `lv`, `mn`, `nl`, `no`, `pl`, `pt`, `ro`, `ru`, `sk`, `sl`,
`sr`, `sv`, `te`, `tet`, `tg`, `th`, `tr`, `uk`, `vi`, and `zh`.

The 14 explicit locale overlays are `en_IN`, `en_NG`, `es_CO`, `es_CR`,
`es_GT`, `es_NI`, `es_VE`, `fr_BE`, `fr_CH`, `fr_DZ`, `pt_BR`, `zh_CN`,
`zh_HK`, and `zh_TW`.

Language resolution trims input, accepts hyphens and underscores, canonicalizes
base/region casing, tries an exact locale first, then falls back to its base.
Thus `pt-BR` resolves to `pt_BR`, `fr_FR` to `fr`, and `en_GB` to `en`.
`eo` and `es_NI` are explicit registry keys; `eu` is unsupported. Use
`base_language()` when a caller needs the resolved base key.

Coverage is intentionally tiered rather than uniform:

- **Reviewed extended registries** retain mature bespoke inventories for Czech,
  Dutch, English, French, German, Italian, Polish, Portuguese, Russian,
  Spanish, Swedish, and Turkish.
- **Reviewed baseline registries** provide source-tagged references/titles,
  guarded numeric markers, localized neutral unit labels, and script-specific
  boundaries for the remaining base languages.
- **Locale overlays** inherit their base and add structured numeric identities;
  they do not create ordinary-prose currency rewrites.

`DATE` is a bounded context mode for numeric evidence such as `5 Mar. 2026`,
not a date parser. Uncased scripts do not receive the Latin uppercase-name
heuristic, and CJK lexical rules use explicit boundaries. CLDR 48.2.1 and BIPM
are development/source inputs only; the installed package has no CLDR, Babel,
spaCy, or network runtime dependency.

This is abbreviation and unit support. Optional `num2words` remains a separate
number-verbalization component, and installed releases may support fewer keys
than this registry. No num2words code or runtime dependency is copied here.

## Installation

```bash
python -m pip install abbr2words
```

For development:

```bash
python -m pip install -e ".[dev]"
python -m build
pytest
```

## API

```python
from abbr2words import abbr2words

text = "Prof. Klein kommt ggf. am Fr."
print(abbr2words(text, lang="de"))
# Professor Klein kommt gegebenenfalls am Freitag
```

Context can be disabled:

```python
abbr2words("Fr. Klein", lang="de", context=False)
# Freitag Klein
```

## External linguistic annotations

`abbr2words` remains dependency-free. Applications that already tokenize and
tag text can pass provider-neutral `TokenAnnotation` objects with character
offsets and optional POS labels. spaCy is not installed or imported by
`abbr2words`; see the [external POS annotation guide](docs/pos-annotations.md)
and `examples/spacy_pos.py`.
Bundled registries do not currently require POS labels; annotations are used by
custom entries configured with POS guards. The provider-specific `tag` value is
retained as metadata but is not currently evaluated.

Use an isolated mutable registry for project-specific entries:

```python
from abbr2words import Expander

expander = Expander("de")
expander.add("KI", "Künstliche Intelligenz", case_sensitive=True)
print(expander("KI hilft."))
```

Consumers that need the shared language registry can use `get_shared_expander()` and
`reset_expanders()`. `Expander` and `get_expander()` remain isolated mutable registries.

## Command line

```bash
python -m abbr2words --lang de "Prof. Klein kommt ggf."
printf 'Prof. Klein kommt ggf.' | abbr2words --lang de
```

## Scope

`abbr2words` expands registered abbreviations and a reviewed set of unit symbols
when they occur after numeric quantities. It preserves numeric values and does
not spell ordinary numbers, dates, or times, and does not perform unit conversion
or currency realization. Unit support is not universal UCUM support. Use the
public `iter_unit_matches()` API when a downstream semantic normalizer needs the
original numeric lexeme, source span, and stable canonical quantity identity.

`abbr2words` recognizes and identifies quantity symbols; it does not decide how
a complete numeric quantity is spoken. Number words, grammatical number,
currency major/minor decomposition, and locale-specific spoken decimal policy
belong to the consuming speech normalizer.

Structured currency identities are available in the reviewed quantity registry
for Czech, English, French, Italian, Portuguese, and Spanish. Czech recognizes
`Kč`/`CZK` as `currency-czech-koruna`; Portuguese also recognizes
`R$`/`BRL` as `currency-brazilian-real`; English, French, Italian, and Spanish
recognize the shared `currency-euro`, `currency-us-dollar`, and
`currency-pound-sterling` identities for EUR/USD/GBP. The other listed
other locales keep locale-specific identities numeric-context-only where provided.
These identities are recognized when a numeric value is adjacent in either
prefix or suffix position:

```python
from abbr2words import iter_unit_matches

match = next(iter_unit_matches("12,80 EUR", "it"))
match.value           # "12,80"
match.canonical_id    # "currency-euro"
match.canonical_symbol  # "€"
```

The match preserves the written numeric lexeme, symbol, and source-relative
offsets. Currency names, number wording, singular/plural agreement, gender,
cents, decimal realization, and arithmetic remain the responsibility of the
downstream speech normalizer; standalone currency symbols and codes are not
lexical rewrites. The reviewed shared inventory is limited to EUR/USD/GBP.

```python
abbr2words("500 g", lang="en")
# "500 gram"

abbr2words("section g", lang="en")
# "section g"
```

## Examples

The repository includes runnable examples for abbreviation-only expansion and
for composing `abbr2words` with `num2words`:

```console
python -m pip install "abbr2words[examples]"
python examples/abbreviations.py
python examples/full_text_demo.py --sample german
```

`abbr2words` itself expands abbreviations only. The optional examples show how
to combine it with `num2words` for broader speech-text normalization, including
output such as `500 g -> five hundred grams`. The full-text demo is example code,
not part of the stable public API. See
[`examples/README.md`](examples/README.md) for the complete command reference.

## Versioning

The package version is derived from Git tags by `setuptools-scm`. Use tags in the
form `v<version>`; the corresponding package version is generated automatically
during builds. A checkout without tags falls back to `0+unknown`.

For a release, commit the changes, create an annotated tag, and build from that
tag:

```bash
git tag -a v<version> -m "Release <version>"
git push origin v<version>
python -m build
```

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.
