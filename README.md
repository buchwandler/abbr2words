[![PyPI - Version](https://img.shields.io/pypi/v/abbr2words)](https://pypi.org/project/abbr2words/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/abbr2words)
![PyPI - Downloads](https://img.shields.io/pypi/dm/abbr2words)

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
- Portuguese (`pt`)

Locale forms such as `de-DE`, `en_GB`, and `pt-BR` are accepted and currently map
to their base-language registry.

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

`abbr2words` expands abbreviations only. It does not convert ordinary numbers,
dates, times, currencies, or measurements. Combine it with `num2words` or another
normalizer when broader text normalization is required.

## Versioning

The package version is derived from Git tags by `setuptools-scm`. Use tags in the
form `v0.2.0`, `v0.3.0`, and so on; the corresponding package version is generated
automatically during builds. A checkout without tags falls back to `0.2.0`.

For a release, commit the changes, create an annotated tag, and build from that
tag:

```bash
git tag -a v0.2.0 -m "Release 0.2.0"
uv build
```

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.
