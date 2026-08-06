from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from abbr2words.units import unit_symbols
from examples.full_text_demo import (
    CZECH_TEXT,
    FRENCH_TEXT,
    GERMAN_TEXT,
    ITALIAN_TEXT,
    PORTUGUESE_TEXT,
    SPANISH_TEXT,
    abbreviation_only,
    normalize_for_speech,
)
from examples.speech_numbers import (
    _APPROVED_EXAMPLE_ONLY_ALIASES,
    _UNITS,
    normalize_numbers_for_speech,
)

ROOT = Path(__file__).parents[1]


def test_example_unit_symbols_have_canonical_parity() -> None:
    for language, forms in _UNITS.items():
        uncovered = (
            set(forms)
            - set(unit_symbols(language))
            - _APPROVED_EXAMPLE_ONLY_ALIASES.get(language, frozenset())
        )
        assert not uncovered


def run_example(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_abbreviation_only_is_dependency_free_and_stage_specific() -> None:
    output = abbreviation_only("Prof. Klein zahlt 42 EUR.", lang="de")
    assert output == "Professor Klein zahlt 42 EUR."


def test_german_full_text_properties() -> None:
    output = normalize_for_speech(GERMAN_TEXT, lang="de")
    assert "Professor Klein" in output
    assert "gegebenenfalls" in output
    assert "zirka" in output
    assert "zuzüglich" in output
    assert "Kilogramm" in output
    assert "Gramm" in output
    assert "Liter" in output
    assert "Zentimeter" in output
    assert "Minuten" in output
    assert "Euro" in output
    assert "14.05.2026" not in output
    assert "18:20" not in output
    assert "__ABBR" not in output


@pytest.mark.parametrize(
    ("text", "lang", "needles"),
    [
        ("1 Min. 2 Min. 45 Min.", "de", ("Minute", "Minuten")),
        (
            "1 lb. 5 lbs. 1 ft. 10 ft. 1 in. 3 in.",
            "en",
            ("pound", "pounds", "foot", "feet", "inch", "inches"),
        ),
        ("98°F 37°C", "en", ("degrees Fahrenheit", "degrees Celsius")),
        ("15th 1st", "en", ("fifteenth", "first")),
        ("3:00 p.m. 9:30 a.m.", "en", ("three P M", "nine thirty A M")),
    ],
)
def test_focused_speech_number_transformations(
    text: str, lang: str, needles: tuple[str, ...]
) -> None:
    output = normalize_numbers_for_speech(text, lang=lang)
    for needle in needles:
        assert needle in output


def test_currency_decimal_cents_and_protected_spans() -> None:
    output = normalize_numbers_for_speech(
        "12,80 EUR $12.80 info@example.com https://example.com/v2 Apt. 4B version 2.0.1",
        lang="de",
    )
    assert "12,80 EUR" not in output
    assert "Euro" in output
    assert "Cent" in output
    assert "info@example.com" in output
    assert "https://example.com/v2" in output
    assert "Apt. 4B" in output
    assert "version 2.0.1" in output
    assert "__ABBR" not in output


@pytest.mark.parametrize(
    ("lang", "text"),
    [
        ("cs", CZECH_TEXT),
        ("es", SPANISH_TEXT),
        ("fr", FRENCH_TEXT),
        ("it", ITALIAN_TEXT),
        ("pt", PORTUGUESE_TEXT),
    ],
)
def test_all_additional_language_samples_expand_abbreviations(lang: str, text: str) -> None:
    output = abbreviation_only(text, lang=lang)
    assert output != text


def test_abbreviation_cli_compact() -> None:
    result = run_example("examples/abbreviations.py", "--compact")
    assert result.returncode == 0
    assert "=== Source ===" not in result.stdout
    assert "identification card" in result.stdout
    assert result.stderr == ""


def test_german_cli_default_shows_abbreviation_stage() -> None:
    result = run_example("examples/german.py")
    assert result.returncode == 0
    assert "=== Source ===" in result.stdout
    assert "=== Abbreviations only ===" in result.stdout
    assert "Full speech text" not in result.stdout
    assert result.stderr == ""


def test_german_cli_full_shows_abbreviations_plus_num2words_stage() -> None:
    result = run_example("examples/german.py", "--full")
    assert result.returncode == 0
    assert "=== Abbreviations only ===" in result.stdout
    assert "=== Abbreviations + num2words ===" in result.stdout
    assert "=== Full speech text ===" in result.stdout
    assert result.stderr == ""


def test_unified_cli_stages_and_all_samples() -> None:
    abbreviation = run_example(
        "examples/full_text_demo.py", "--sample", "english", "--stage", "abbr", "--compact"
    )
    assert abbreviation.returncode == 0
    assert "=== Source ===" not in abbreviation.stdout
    assert "37 degree Celsius." in abbreviation.stdout

    full = run_example(
        "examples/full_text_demo.py", "--sample", "german", "--stage", "full", "--compact"
    )
    assert full.returncode == 0
    assert "=== Full speech text ===" not in full.stdout
    assert "Euro" in full.stdout

    all_samples = run_example("examples/full_text_demo.py", "--all", "--stage", "abbr")
    assert all_samples.returncode == 0
    for name in ("english", "german", "czech", "spanish", "french", "italian", "portuguese"):
        assert name in all_samples.stdout
    assert "Novák" in all_samples.stdout
    assert all_samples.stderr == ""


def test_unified_cli_requires_language_for_custom_text() -> None:
    result = run_example("examples/full_text_demo.py", "--text", "42")
    assert result.returncode != 0
    assert "--lang is required with --text" in result.stderr
