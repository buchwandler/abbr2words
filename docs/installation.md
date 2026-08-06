# Installation

## Users

Install the package from PyPI:

```console
python -m pip install abbr2words
```

`abbr2words` has no runtime dependencies. It supports Python 3.10 through Python
3.14, subject to the release matrix maintained by the project.

## Development

From a checkout, install the package and development tools in editable mode:

```console
python -m pip install -e ".[dev]"
pytest
```

The development extra includes the test, build, lint, and type-checking tools.

## Examples

Install the optional full-text demonstration dependency from a checkout or
alongside the package:

```console
python -m pip install "abbr2words[examples]"
```

This keeps `num2words` out of the core runtime installation. The abbreviation-only
examples work without it; full speech-text normalization uses it for numbers and
the example-local date, time, currency, temperature, and unit rules.

## Documentation

Documentation dependencies are separate from the runtime package:

```console
python -m pip install -r docs/requirements.txt
sphinx-build -W --keep-going -b html docs docs/_build/html
```
