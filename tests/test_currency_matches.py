from __future__ import annotations

import pytest

from abbr2words import iter_unit_matches
from abbr2words.units import unit_entries


@pytest.mark.parametrize(
    ("source", "canonical_id", "value", "symbol"),
    [
        ("€ 1.500", "currency-euro", "1.500", "€"),
        ("25,99€", "currency-euro", "25,99", "€"),
        ("EUR 1.500", "currency-euro", "1.500", "EUR"),
        ("1.500 EUR", "currency-euro", "1.500", "EUR"),
        ("$19,95", "currency-us-dollar", "19,95", "$"),
        ("$ 9,99", "currency-us-dollar", "9,99", "$"),
        ("19,95 USD", "currency-us-dollar", "19,95", "USD"),
        ("USD 19,95", "currency-us-dollar", "19,95", "USD"),
        ("£12.50", "currency-pound-sterling", "12.50", "£"),
        ("GBP 12.50", "currency-pound-sterling", "12.50", "GBP"),
        ("12.50 GBP", "currency-pound-sterling", "12.50", "GBP"),
        ("87,50 CHF", "currency-swiss-franc", "87,50", "CHF"),
    ],
)
def test_german_currency_matches_are_complete(
    source: str, canonical_id: str, value: str, symbol: str
) -> None:
    matches = [match for match in iter_unit_matches(source, "de") if match.category == "currency"]

    assert len(matches) == 1
    match = matches[0]
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id
    assert match.category == "currency"


@pytest.mark.parametrize(
    ("source", "fragment"),
    [
        ("Es kostet € 1.500.", "€ 1.500"),
        ("Der Preis beträgt $19,95.", "$19,95"),
        ("Die Gebühr beträgt £12.50.", "£12.50"),
    ],
)
def test_german_currency_before_sentence_period_matches_full_amount(
    source: str, fragment: str
) -> None:
    match = next(match for match in iter_unit_matches(source, "de") if match.category == "currency")
    assert source[match.start : match.end] == fragment


@pytest.mark.parametrize(
    ("source", "canonical_id", "value"),
    [
        ("₩50,000", "currency-south-korean-won", "50,000"),
        ("₫1,000,000", "currency-vietnamese-dong", "1,000,000"),
        ("₮50,000", "currency-mongolian-tugrik", "50,000"),
        ("50,000 KRW", "currency-south-korean-won", "50,000"),
        ("1,000,000 VND", "currency-vietnamese-dong", "1,000,000"),
        ("50,000 MNT", "currency-mongolian-tugrik", "50,000"),
    ],
)
def test_spanish_extended_currency_identity(source: str, canonical_id: str, value: str) -> None:
    matches = list(iter_unit_matches(source, "es"))

    assert len(matches) == 1
    match = matches[0]
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.canonical_id == canonical_id
    assert match.category == "currency"


def test_non_english_western_comma_grouping_is_not_truncated() -> None:
    for source, value in (("1,000,000 kg", "1,000,000"), ("12,345,678.90 kg", "12,345,678.90")):
        matches = list(iter_unit_matches(source, "es"))
        assert len(matches) == 1
        assert matches[0].value == value


@pytest.mark.parametrize("source", ["1,234,56 kg", "1.234.56 kg", "1,00,000,00 VND"])
def test_malformed_grouping_fails_closed(source: str) -> None:
    assert tuple(iter_unit_matches(source, "es")) == ()


@pytest.mark.parametrize("language", ["de", "es"])
@pytest.mark.parametrize(
    "source", ["EUR", "USD", "GBP", "CHF", "VND", "MNT", "€", "$", "£", "₫", "₮"]
)
def test_currency_aliases_without_numeric_context_are_not_unit_matches(
    language: str, source: str
) -> None:
    assert tuple(iter_unit_matches(source, language)) == ()


def test_german_euro_identity_is_registered_once() -> None:
    euro_entries = [entry for entry in unit_entries("de") if entry.canonical_id == "currency-euro"]
    assert len(euro_entries) == 1
    assert euro_entries[0].symbols == ("€", "EUR")
