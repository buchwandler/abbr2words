from __future__ import annotations

import pytest

from abbr2words import abbr2words, get_shared_expander, iter_unit_matches
from abbr2words.units import unit_entries


@pytest.mark.parametrize(
    ("source", "value", "symbol", "canonical_id", "canonical_symbol"),
    [
        ("12,80 EUR", "12,80", "EUR", "currency-euro", "€"),
        ("EUR 12,80", "12,80", "EUR", "currency-euro", "€"),
        ("12,80 €", "12,80", "€", "currency-euro", "€"),
        ("€12,80", "12,80", "€", "currency-euro", "€"),
        ("10 USD", "10", "USD", "currency-us-dollar", "$"),
        ("USD 10", "10", "USD", "currency-us-dollar", "$"),
        ("10 $", "10", "$", "currency-us-dollar", "$"),
        ("$10", "10", "$", "currency-us-dollar", "$"),
        ("5 GBP", "5", "GBP", "currency-pound-sterling", "£"),
        ("GBP 5", "5", "GBP", "currency-pound-sterling", "£"),
        ("5 £", "5", "£", "currency-pound-sterling", "£"),
        ("£5", "5", "£", "currency-pound-sterling", "£"),
    ],
)
def test_spanish_structured_currency_matches_preserve_identity_and_offsets(
    source: str,
    value: str,
    symbol: str,
    canonical_id: str,
    canonical_symbol: str,
) -> None:
    matches = list(iter_unit_matches(source, "es"))
    assert len(matches) == 1
    match = matches[0]
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id
    assert match.canonical_symbol == canonical_symbol
    assert match.language == "es"
    assert match.category == "currency"
    assert abbr2words(source, lang="es") == source


def test_spanish_currency_registry_uses_reviewed_lemmas() -> None:
    entries = {
        entry.canonical_id: entry for entry in unit_entries("es") if entry.category == "currency"
    }
    assert {
        canonical_id: (entry.symbols, entry.expansion, entry.canonical_symbol)
        for canonical_id, entry in entries.items()
    } == {
        "currency-euro": (("€", "EUR"), "euro", "€"),
        "currency-us-dollar": (("$", "USD"), "dólar estadounidense", "$"),
        "currency-pound-sterling": (("£", "GBP"), "libra esterlina", "£"),
    }
    assert all(entry.quantity_position == "both" for entry in entries.values())


@pytest.mark.parametrize(
    "source",
    [
        "EUR",
        "USD",
        "GBP",
        "€",
        "$",
        "£",
        "priceEUR",
        "EURprice",
        "A12EURB",
        "v1.2.3",
        "name@example.com",
        "https://example.com/12,80EUR",
    ],
)
def test_spanish_currency_matching_is_numeric_context_only(source: str) -> None:
    assert list(iter_unit_matches(source, "es")) == []


def test_spanish_lexical_collision_and_numeric_duration_policy_are_preserved() -> None:
    entry = get_shared_expander("es").get_abbreviation("mar.", case_sensitive=True)
    assert entry.expansion == "marzo"
    assert abbr2words("mar.", lang="es") == "marzo"
    assert [
        (match.value, match.symbol, match.canonical_id)
        for match in iter_unit_matches("5 min. y 5 seg.", "es")
    ] == [
        ("5", "min.", "duration-minute"),
        ("5", "seg.", "duration-second"),
    ]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("1 kg", "mass-kilogram"),
        ("2 kg", "mass-kilogram"),
        ("1,5 kg", "mass-kilogram"),
        ("25°C", "temperature-celsius"),
        ("-1 °C", "temperature-celsius"),
        ("5 min.", "duration-minute"),
        ("5 seg.", "duration-second"),
        ("20 m²", "area-square-meter"),
        ("5 km/h", "speed-kilometer-per-hour"),
    ],
)
def test_existing_spanish_unit_identities_remain_stable(source: str, expected: str) -> None:
    matches = list(iter_unit_matches(source, "es"))
    assert len(matches) == 1
    assert matches[0].canonical_id == expected
    assert matches[0].language == "es"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Blvd. Juárez", "bulevar Juárez"),
        ("Mtro. López", "maestro López"),
        ("Gral. Díaz", "general Díaz"),
        ("Fís. 2", "físico 2"),
        ("Pte. Fox", "presidente Fox"),
        ("Fca. 4", "fábrica 4"),
        ("No. 12", "número 12"),
        ("N.º 12", "número 12"),
        ("No. idea", "No. idea"),
    ],
)
def test_high_confidence_spanish_entries_and_numeric_number_marker(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="es") == expected
