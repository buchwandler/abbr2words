from __future__ import annotations

import tarfile
import zipfile
from importlib.resources import files
from pathlib import Path

import pytest


def test_pep561_marker_is_present() -> None:
    assert files("abbr2words").joinpath("py.typed").is_file()


def _latest_artifact(pattern: str) -> Path:
    artifacts = sorted(Path("dist").glob(pattern), key=lambda path: path.stat().st_mtime)
    if not artifacts:
        pytest.fail(f"No artifact matching {pattern!r}; run python -m build first")
    return artifacts[-1]


def test_wheel_contains_runtime_and_license_files() -> None:
    wheel = _latest_artifact("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())

    assert "abbr2words/py.typed" in names
    assert "abbr2words/api.py" in names
    assert "abbr2words/languages/en.py" in names
    assert any(name.endswith(".dist-info/licenses/LICENSE") for name in names)
    assert any(name.endswith(".dist-info/licenses/NOTICE") for name in names)


def test_sdist_contains_source_docs_tests_and_legal_files() -> None:
    source_distribution = _latest_artifact("*.tar.gz")
    with tarfile.open(source_distribution, "r:gz") as archive:
        names = set(archive.getnames())

    assert any(name.endswith("/LICENSE") for name in names)
    assert any(name.endswith("/NOTICE") for name in names)
    assert any(name.endswith("/MANIFEST.in") for name in names)
    assert any(name.endswith("/abbr2words/py.typed") for name in names)
    assert any(name.endswith("/docs/conf.py") for name in names)
    assert any(name.endswith("/docs/requirements.txt") for name in names)
    assert any(name.endswith("/tests/test_api.py") for name in names)
    assert any(name.endswith("/examples/abbreviations.py") for name in names)
    assert any(name.endswith("/examples/german.py") for name in names)
    assert any(name.endswith("/examples/full_text_demo.py") for name in names)
    assert any(name.endswith("/examples/speech_numbers.py") for name in names)
    assert any(name.endswith("/examples/README.md") for name in names)
