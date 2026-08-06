from __future__ import annotations

import pytest

from abbr2words import abbr2words, supported_languages
from abbr2words.units import unit_entries, unit_symbols

CURRENT_UNIT_SPELLINGS = {
    "cs": {"hod.", "min.", "sek.", "km", "m", "cm", "mm", "kg", "g", "l"},
    "de": {"Std.", "Min.", "Sek."},
    "en": {
        "yrs.",
        "in.",
        "ft.",
        "yd.",
        "mi.",
        "mm",
        "cm",
        "km",
        "oz.",
        "lb.",
        "lbs.",
        "mg",
        "kg",
        "gal.",
        "qt.",
        "pt.",
        "tsp.",
        "tbsp.",
        "hr.",
        "hrs.",
        "sec.",
    },
    "es": {"h", "min", "min.", "seg", "seg.", "km", "m", "cm", "mm", "kg", "g", "mg", "l", "ml"},
    "fr": {"h", "min", "sec", "km", "m", "cm", "mm", "kg", "g", "mg", "l", "ml"},
    "it": {"h", "min", "min.", "sec", "sec.", "km", "m", "cm", "mm", "kg", "g", "mg", "l", "ml"},
    "pt": {"h", "min", "min.", "seg", "seg.", "km", "m", "cm", "mm", "kg", "g", "mg", "l", "ml"},
}


@pytest.mark.parametrize("language", supported_languages())
def test_basic_metric_quantities_expand(language: str) -> None:
    symbol = "kg" if language == "de" else "g"
    assert abbr2words(f"500 {symbol}", lang=language) != f"500 {symbol}"


@pytest.mark.parametrize("source", ("500 g", "500g", "1.5 kg", "1,5 kg", "-20 °C", "−20 °C"))
def test_numeric_forms_expand(source: str) -> None:
    assert abbr2words(source, lang="en") != source


@pytest.mark.parametrize("space", (" ", "\u00a0", "\u202f", ""))
def test_grouped_numbers_and_compact_units(space: str) -> None:
    source = f"1{space}000{space}kg"
    assert "kilogram" in abbr2words(source, lang="en")


@pytest.mark.parametrize("source", ("m", "g", "h", "s", "C", "F", "B", "T", "section g", "m/s"))
def test_standalone_symbols_and_partial_compounds_are_unchanged(source: str) -> None:
    assert abbr2words(source, lang="en") == source


@pytest.mark.parametrize(
    ("source", "expected"),
    (
        ("500 g,", "500 gram,"),
        ("500 g.", "500 gram."),
        ("5 km/h", "5 kilometer per hour"),
        ("20 m²", "20 square meter"),
        ("20 °C", "20 degree Celsius"),
    ),
)
def test_complete_units_preserve_suffix_and_expand_as_one_expression(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="en") == expected


@pytest.mark.parametrize("language", supported_languages())
def test_every_reviewed_unit_requires_numeric_context(language: str) -> None:
    for entry in unit_entries(language):
        assert entry.requires_numeric_value
        for symbol in entry.symbols:
            assert abbr2words(symbol, lang=language) == symbol


def test_case_sensitive_near_misses_and_attached_words() -> None:
    assert abbr2words("500 G", lang="en") == "500 G"
    assert abbr2words("500kgtest", lang="en") == "500kgtest"
    assert abbr2words("vitamin C", lang="en") == "vitamin C"
    assert abbr2words("Model T", lang="en") == "Model T"
    assert abbr2words("Plan B", lang="en") == "Plan B"


def test_inventory_contains_expected_symbols() -> None:
    assert {"g", "m", "ml", "mL", "L", "km/h", "m/s", "°C"} <= unit_symbols("en")


def test_all_legacy_unit_spellings_are_in_reviewed_inventory() -> None:
    assert sum(len(spellings) for spellings in CURRENT_UNIT_SPELLINGS.values()) == 88
    for language, spellings in CURRENT_UNIT_SPELLINGS.items():
        assert spellings <= unit_symbols(language)
