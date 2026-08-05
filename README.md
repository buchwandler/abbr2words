# abbr2words

Multilingual, context-aware abbreviation expansion for text normalization and speech.

This MVP was extracted from the abbreviation framework and language registries in
`kokorog2p`. It has no runtime dependencies and uses a flat package layout (no
`src/` directory).

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
python -m pip install .
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

The project version is declared dynamically in `pyproject.toml` and read by
Setuptools from `abbr2words/__about__.py`. Change only `__version__` there when
preparing a release.

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.
