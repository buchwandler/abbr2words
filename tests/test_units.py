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
    "es": {
        "h",
        "min",
        "min.",
        "seg",
        "seg.",
        "km",
        "m",
        "cm",
        "mm",
        "kg",
        "g",
        "mg",
        "l",
        "ml",
        "€",
        "EUR",
        "$",
        "USD",
        "£",
        "GBP",
    },
    "fr": {
        "h",
        "min",
        "min.",
        "sec",
        "sec.",
        "km",
        "m",
        "cm",
        "mm",
        "kg",
        "g",
        "mg",
        "l",
        "ml",
        "€",
        "EUR",
        "$",
        "USD",
        "£",
        "GBP",
    },
    "it": {
        "h",
        "min",
        "min.",
        "sec",
        "sec.",
        "km",
        "m",
        "cm",
        "mm",
        "kg",
        "g",
        "mg",
        "l",
        "ml",
        "€",
        "EUR",
        "$",
        "USD",
        "£",
        "GBP",
    },
    "pt": {
        "h",
        "min",
        "min.",
        "seg",
        "seg.",
        "km",
        "m",
        "cm",
        "mm",
        "kg",
        "g",
        "mg",
        "l",
        "ml",
        "€",
        "EUR",
        "$",
        "USD",
        "£",
        "GBP",
        "R$",
        "BRL",
    },
}


@pytest.mark.parametrize("language", supported_languages())
def test_basic_metric_quantities_expand(language: str) -> None:
    symbol = "kg" if language == "de" else "g"
    assert abbr2words(f"500 {symbol}", lang=language) != f"500 {symbol}"


@pytest.mark.parametrize("source", ("500 g", "500g", "1.5 kg", "1,5 kg", "-20 °C", "−20 °C"))
def test_numeric_forms_expand(source: str) -> None:
    assert abbr2words(source, lang="en") != source


@pytest.mark.parametrize(
    ("source", "expected"),
    (
        ("30,000.10 in.", "30,000.10 inch"),
        ("30,000.10 ft.", "30,000.10 foot"),
        ("30,000.10 kg", "30,000.10 kilogram"),
    ),
)
def test_english_grouped_decimal_units_expand_lexically(source: str, expected: str) -> None:
    assert abbr2words(source, lang="en") == expected


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
            if entry.allow_lexical_overlap:
                assert language == "fr"
                assert symbol == "min."
                assert abbr2words(symbol, lang=language) == "minimum"
                continue
            if entry.category == "magnitude":
                assert abbr2words(symbol, lang=language) == entry.expansion
                continue
            assert abbr2words(symbol, lang=language) == symbol


def test_case_sensitive_near_misses_and_attached_words() -> None:
    assert abbr2words("500 G", lang="en") == "500 G"
    assert abbr2words("500kgtest", lang="en") == "500kgtest"
    assert abbr2words("vitamin C", lang="en") == "vitamin C"
    assert abbr2words("Model T", lang="en") == "Model T"
    assert abbr2words("Plan B", lang="en") == "Plan B"


def test_inventory_contains_expected_symbols() -> None:
    assert {"g", "m", "ml", "mL", "L", "km/h", "m/s", "°C"} <= unit_symbols("en")
    assert {"€", "EUR", "$", "USD", "£", "GBP"} <= unit_symbols("en")
    assert {"Kč", "CZK", "€", "EUR", "$", "USD", "£", "GBP"} <= unit_symbols("cs")
    assert {"€", "EUR", "$", "USD", "£", "GBP"} <= unit_symbols("es")
    assert {"€", "EUR", "$", "USD", "£", "GBP", "min.", "sec."} <= unit_symbols("fr")
    assert {"€", "EUR", "$", "USD", "£", "GBP"} <= unit_symbols("it")


def test_english_currency_registry_uses_shared_identities_and_metadata() -> None:
    entries = {
        entry.canonical_id: entry for entry in unit_entries("en") if entry.category == "currency"
    }
    assert {
        canonical_id: (entry.symbols, entry.expansion, entry.canonical_symbol)
        for canonical_id, entry in entries.items()
    } == {
        "currency-euro": (("€", "EUR"), "euro", "€"),
        "currency-us-dollar": (("$", "USD"), "US dollar", "$"),
        "currency-pound-sterling": (("£", "GBP"), "pound sterling", "£"),
    }
    assert all(entry.quantity_position == "both" for entry in entries.values())
    assert all(entry.requires_numeric_value for entry in entries.values())


def test_italian_currency_registry_uses_reviewed_lemmas() -> None:
    entries = {
        entry.canonical_id: entry for entry in unit_entries("it") if entry.category == "currency"
    }
    assert {
        canonical_id: (entry.symbols, entry.expansion, entry.canonical_symbol)
        for canonical_id, entry in entries.items()
    } == {
        "currency-euro": (("€", "EUR"), "euro", "€"),
        "currency-us-dollar": (("$", "USD"), "dollaro statunitense", "$"),
        "currency-pound-sterling": (("£", "GBP"), "sterlina britannica", "£"),
    }
    assert all(entry.quantity_position == "both" for entry in entries.values())


def test_czech_currency_registry_uses_shared_identities_and_metadata() -> None:
    entries = {
        entry.canonical_id: entry for entry in unit_entries("cs") if entry.category == "currency"
    }
    assert {
        canonical_id: (
            entry.symbols,
            entry.expansion,
            entry.canonical_symbol,
            entry.category,
            entry.quantity_position,
            entry.requires_numeric_value,
        )
        for canonical_id, entry in entries.items()
    } == {
        "currency-czech-koruna": (
            ("Kč", "CZK"),
            "česká koruna",
            "Kč",
            "currency",
            "both",
            True,
        ),
        "currency-euro": (("€", "EUR"), "euro", "€", "currency", "both", True),
        "currency-us-dollar": (
            ("$", "USD"),
            "americký dolar",
            "$",
            "currency",
            "both",
            True,
        ),
        "currency-pound-sterling": (
            ("£", "GBP"),
            "libra šterlinků",
            "£",
            "currency",
            "both",
            True,
        ),
    }


def test_portuguese_currency_registry_uses_reviewed_lemmas_and_metadata() -> None:
    entries = {
        entry.canonical_id: entry for entry in unit_entries("pt") if entry.category == "currency"
    }
    assert {
        canonical_id: (
            entry.symbols,
            entry.expansion,
            entry.canonical_symbol,
            entry.category,
            entry.quantity_position,
            entry.requires_numeric_value,
        )
        for canonical_id, entry in entries.items()
    } == {
        "currency-euro": (("€", "EUR"), "euro", "€", "currency", "both", True),
        "currency-us-dollar": (
            ("$", "USD"),
            "dólar americano",
            "$",
            "currency",
            "both",
            True,
        ),
        "currency-pound-sterling": (
            ("£", "GBP"),
            "libra esterlina",
            "£",
            "currency",
            "both",
            True,
        ),
        "currency-brazilian-real": (("R$", "BRL"), "real", "R$", "currency", "both", True),
    }


def test_all_legacy_unit_spellings_are_in_reviewed_inventory() -> None:
    assert sum(len(spellings) for spellings in CURRENT_UNIT_SPELLINGS.values()) == 116
    for language, spellings in CURRENT_UNIT_SPELLINGS.items():
        assert spellings <= unit_symbols(language)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Attendez 45 min.", "Attendez 45 minute."),
        ("Attendez 45 min. puis partez.", "Attendez 45 minute puis partez."),
        ("Attendez 45 Min.", "Attendez 45 Minute"),
        ("Attendez 45 Min., puis partez.", "Attendez 45 Minute, puis partez."),
    ],
)
def test_dotted_unit_rendering_preserves_only_sentence_final_punctuation(
    source: str, expected: str
) -> None:
    language = "de" if "Min." in source else "fr"
    assert abbr2words(source, lang=language) == expected
