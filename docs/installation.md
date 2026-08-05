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

## Documentation

Documentation dependencies are separate from the runtime package:

```console
python -m pip install -r docs/requirements.txt
sphinx-build -W --keep-going -b html docs docs/_build/html
```
