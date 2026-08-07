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

- Czech (`cs`)
- German (`de`)
- English (`en`)
- Spanish (`es`)
- French (`fr`)
- Italian (`it`)
- Dutch (`nl`)
- Polish (`pl`)
- Portuguese (`pt`)
- Russian (`ru`)
- Swedish (`sv`)
- Turkish (`tr`)

Locale forms such as `de-DE`, `en_GB`, and `pt-BR` are accepted and currently map
to their base-language registry.

Dutch, Polish, Russian, Swedish, and Turkish currently provide conservative
abbreviation and reviewed numeric-unit registries. Their multilingual examples
are abbreviation-only; full speech-number normalization remains limited to the
optional examples configured for the original scenario languages.

## Installation

```bash
python -m pip install abbr2words
```

For development:

```bash
python -m pip install -e ".[dev]"
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
form `v0.2.0`, `v0.3.0`, and so on; the corresponding package version is generated
automatically during builds. A checkout without tags falls back to `0.2.2` for
this additive release.

For a release, commit the changes, create an annotated tag, and build from that
tag:

```bash
git tag -a v0.2.0 -m "Release 0.2.0"
uv build
```

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.
