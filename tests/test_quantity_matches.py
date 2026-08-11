from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from abbr2words import (
    Expander,
    UnitEntry,
    UnitMatch,
    abbr2words,
    abbr2words_with_replacements,
    iter_unit_diagnostics,
    iter_unit_matches,
)


def only_match(source: str, language: str = "de", **kwargs: object) -> UnitMatch:
    matches = list(iter_unit_matches(source, language, **kwargs))
    assert len(matches) == 1
    return matches[0]


@pytest.mark.parametrize(
    ("source", "value", "symbol"),
    [
        ("2kg", "2", "kg"),
        ("1,5 kg", "1,5", "kg"),
        ("+12 kg", "+12", "kg"),
        ("−20 kg", "−20", "kg"),
        ("1 000 kg", "1 000", "kg"),
        ("1\u00a0000 kg", "1\u00a0000", "kg"),
        ("1\u202f000 kg", "1\u202f000", "kg"),
    ],
)
def test_matches_preserve_numeric_lexeme_and_complete_source_span(
    source: str, value: str, symbol: str
) -> None:
    match = only_match(source)
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == "mass-kilogram"
    assert match.language == "de"
    assert match.category == "unit"


@pytest.mark.parametrize("source", ["5 kg", "10.0 kg", "30,000 kg", ".5 kg", "1,5 kg", "1 000 kg"])
def test_existing_english_numeric_forms_remain_complete(source: str) -> None:
    match = only_match(source, "en")
    assert source[match.start : match.end] == source
    assert match.value == source[: -len(" kg")]
    assert match.canonical_id == "mass-kilogram"


@pytest.mark.parametrize(
    ("source", "symbol", "canonical_id"),
    [
        ("30,000.10 in.", "in.", "customary-inch"),
        ("30,000.10 ft.", "ft.", "customary-foot"),
        ("30,000.10 kg", "kg", "mass-kilogram"),
    ],
)
def test_english_grouped_decimal_units_match_complete_identity(
    source: str, symbol: str, canonical_id: str
) -> None:
    match = only_match(source, "en")
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == "30,000.10"
    assert match.value == "30,000.10"
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id


@pytest.mark.parametrize("source", ["1.02.3 kg", "30,00.10 kg", "2kg-rated", "1 m^2"])
def test_english_grouped_decimal_malformed_and_ambiguous_forms_remain_unmatched(
    source: str,
) -> None:
    assert list(iter_unit_matches(source, "en")) == []


def test_english_grouped_decimal_syntax_isolated_from_german() -> None:
    assert list(iter_unit_matches("30,000.10 kg", "de")) == []


@pytest.mark.parametrize(
    ("source", "canonical_id", "category"),
    [
        ("2kWh", "energy-kilowatt-hour", "unit"),
        ("3mAh", "charge-milliampere-hour", "unit"),
        ("4 Wh", "energy-watt-hour", "unit"),
        ("5 mA", "current-milliampere", "unit"),
        ("6 GHz", "frequency-gigahertz", "unit"),
        ("7 MHz", "frequency-megahertz", "unit"),
        ("8 kHz", "frequency-kilohertz", "unit"),
        ("9 Hz", "frequency-hertz", "unit"),
        ("10 W", "power-watt", "unit"),
        ("11 V", "voltage-volt", "unit"),
        ("1 mio.", "magnitude-million", "magnitude"),
        ("2 mrd.", "magnitude-billion", "magnitude"),
        ("3 TSD.", "magnitude-thousand", "magnitude"),
        ("4 STCK.", "count-piece", "unit"),
        ("5 Ltr.", "volume-liter", "unit"),
        ("6 EUR", "currency-euro", "currency"),
    ],
)
def test_required_german_inventory_and_case_variants(
    source: str, canonical_id: str, category: str
) -> None:
    match = only_match(source)
    assert match.canonical_id == canonical_id
    assert match.category == category


@pytest.mark.parametrize(
    ("source", "value", "symbol", "canonical_id"),
    [
        ("50 kW", "50", "kW", "power-kilowatt"),
        ("550 nm", "550", "nm", "length-nanometer"),
        ("60 Hz", "60", "Hz", "frequency-hertz"),
        ("750 W", "750", "W", "power-watt"),
        ("5 A", "5", "A", "current-ampere"),
        ("1000 kWh", "1000", "kWh", "energy-kilowatt-hour"),
        ("1000 lm", "1000", "lm", "luminous-flux-lumen"),
        ("20 N", "20", "N", "force-newton"),
        ("500 J", "500", "J", "energy-joule"),
        ("760 mmHg", "760", "mmHg", "pressure-millimeter-mercury"),
        ("3 mol", "3", "mol", "amount-mole"),
        ("0.01 M", "0.01", "M", "concentration-molar"),
        ("150 lbs", "150", "lbs", "customary-pound"),
    ],
)
def test_reviewed_scientific_units_preserve_identity_metadata(
    source: str, value: str, symbol: str, canonical_id: str
) -> None:
    match = only_match(source, "en")
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id


@pytest.mark.parametrize("source", ["7B", "2B", "45B", "3A", "5K"])
def test_separator_required_units_do_not_claim_compact_identifier_codes(source: str) -> None:
    assert list(iter_unit_matches(source, "en")) == []
    assert abbr2words(source, lang="en") == source


@pytest.mark.parametrize(
    ("source", "expected_symbol", "expected_canonical_id"),
    [
        ("7 B", "B", "data-byte"),
        ("3 A", "A", "current-ampere"),
        ("300 K", "K", "temperature-kelvin"),
    ],
)
def test_separator_required_units_remain_supported_when_spaced(
    source: str, expected_symbol: str, expected_canonical_id: str
) -> None:
    match = only_match(source, "en")
    assert (match.symbol, match.canonical_id) == (expected_symbol, expected_canonical_id)


def test_unit_diagnostics_explain_compact_rejection_without_changing_matches() -> None:
    diagnostics = list(iter_unit_diagnostics("Stamm 7B and 7 B", "en"))
    assert [(item.status, item.symbol, item.canonical_id, item.reason) for item in diagnostics] == [
        ("rejected", "B", "data-byte", "requires_separator"),
        ("accepted", "B", "data-byte", None),
    ]


@pytest.mark.parametrize("language", ["de", "es", "fr", "it"])
def test_reviewed_pound_aliases_are_localized_without_changing_identity(language: str) -> None:
    match = only_match("150 lbs", language)
    assert match.canonical_id == "customary-pound"
    assert match.symbol == "lbs"


@pytest.mark.parametrize(
    "source",
    ["A plan", "Plan A", "N. meningitidis", "Vitamin M", "model W"],
)
def test_ambiguous_single_letter_units_require_numeric_context(source: str) -> None:
    assert list(iter_unit_matches(source, "en")) == []


def test_directional_periods_are_left_for_english_abbreviations() -> None:
    assert list(iter_unit_matches("20 N.", "en")) == []
    assert only_match("20 N", "en").canonical_id == "force-newton"


@pytest.mark.parametrize(
    ("source", "value", "symbol", "canonical_id", "canonical_symbol"),
    [
        ("$12.50", "12.50", "$", "currency-us-dollar", "$"),
        ("$ 12.50", "12.50", "$", "currency-us-dollar", "$"),
        ("$30,000.10", "30,000.10", "$", "currency-us-dollar", "$"),
        ("12.50$", "12.50", "$", "currency-us-dollar", "$"),
        ("12.50 $", "12.50", "$", "currency-us-dollar", "$"),
        ("USD 12.50", "12.50", "USD", "currency-us-dollar", "$"),
        ("12.50 USD", "12.50", "USD", "currency-us-dollar", "$"),
        ("30,000.10 USD", "30,000.10", "USD", "currency-us-dollar", "$"),
        ("£1.01", "1.01", "£", "currency-pound-sterling", "£"),
        ("GBP 1.01", "1.01", "GBP", "currency-pound-sterling", "£"),
        ("1.01 GBP", "1.01", "GBP", "currency-pound-sterling", "£"),
        ("€2", "2", "€", "currency-euro", "€"),
        ("EUR 2", "2", "EUR", "currency-euro", "€"),
        ("2 EUR", "2", "EUR", "currency-euro", "€"),
    ],
)
def test_english_currency_matches_preserve_identity_and_offsets(
    source: str,
    value: str,
    symbol: str,
    canonical_id: str,
    canonical_symbol: str,
) -> None:
    match = only_match(source, "en")
    assert match.start == 0
    assert match.end == len(source)
    assert match.value_start == source.index(value)
    assert match.value_end == match.value_start + len(value)
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id
    assert match.canonical_symbol == canonical_symbol
    assert match.category == "currency"
    assert match.language == "en"
    assert abbr2words(source, lang="en") == source


def test_english_currency_alias_normalizes_language() -> None:
    match = only_match("USD 12.50", "en-gb")
    assert match.language == "en_GB"
    assert match.canonical_id == "currency-us-dollar"


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
        "USD 12.50foo",
        "USD 12.50.75",
        "name@example.com",
        "https://example.com/12.50EUR",
        "12 EUR/USD",
    ],
)
def test_english_currency_matching_rejects_lexical_and_malformed_material(
    source: str,
) -> None:
    assert list(iter_unit_matches(source, "en")) == []


def test_english_currency_protected_spans_suppress_only_protected_quantity() -> None:
    source = "prefix $5 and EUR 6"
    protected_start = source.index("$5")
    protected_end = protected_start + len("$5")
    matches = list(
        iter_unit_matches(source, "en", protected_spans=[(protected_start, protected_end)])
    )
    assert [source[item.start : item.end] for item in matches] == ["EUR 6"]
    assert matches[0].start == source.index("EUR 6")
    assert matches[0].value == "6"


def test_english_currency_sentence_punctuation_is_outside_match() -> None:
    source = "$12.50."
    match = only_match(source, "en")
    assert source[match.start : match.end] == "$12.50"
    assert source[match.end :] == "."


@pytest.mark.parametrize(
    ("source", "canonical_id"),
    [
        ("10 in.", "customary-inch"),
        ("37°C.", "temperature-celsius"),
        ("2 kg", "mass-kilogram"),
    ],
)
def test_existing_english_unit_matches_remain_unchanged(source: str, canonical_id: str) -> None:
    match = only_match(source, "en")
    assert match.canonical_id == canonical_id
    if source == "37°C.":
        assert source[match.end :] == "."


@pytest.mark.parametrize(
    ("source", "value", "symbol", "canonical_id", "canonical_symbol"),
    [
        ("37°C", "37", "°C", "temperature-celsius", "°C"),
        ("37 °C", "37", "°C", "temperature-celsius", "°C"),
        ("37° C", "37", "° C", "temperature-celsius", "°C"),
        ("37 ° C", "37", "° C", "temperature-celsius", "°C"),
        ("37 C", "37", "C", "temperature-celsius", "°C"),
        ("37C", "37", "C", "temperature-celsius", "°C"),
        ("37 c.", "37", "c.", "temperature-celsius", "°C"),
        ("-40 C.", "-40", "C.", "temperature-celsius", "°C"),
        ("98°F", "98", "°F", "temperature-fahrenheit", "°F"),
        ("98 °F", "98", "°F", "temperature-fahrenheit", "°F"),
        ("98° F", "98", "° F", "temperature-fahrenheit", "°F"),
        ("98 F", "98", "F", "temperature-fahrenheit", "°F"),
        ("98F", "98", "F", "temperature-fahrenheit", "°F"),
        ("98 f.", "98", "f.", "temperature-fahrenheit", "°F"),
    ],
)
def test_english_temperature_aliases_preserve_source_identity_and_offsets(
    source: str,
    value: str,
    symbol: str,
    canonical_id: str,
    canonical_symbol: str,
) -> None:
    match = only_match(source, "en")
    assert match.start == 0
    assert match.end == len(source)
    assert match.value_start == source.index(value)
    assert match.value_end == match.value_start + len(value)
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id
    assert match.canonical_symbol == canonical_symbol


@pytest.mark.parametrize(
    "source",
    ["C.", "F.", "Plan C.", "Press F.", "abcC", "Celsius", "Fahrenheit"],
)
def test_english_temperature_aliases_require_numeric_evidence(source: str) -> None:
    assert list(iter_unit_matches(source, "en")) == []
    assert abbr2words(source, lang="en") == source


def test_english_temperature_protected_spans_suppress_only_protected_quantity() -> None:
    source = "37 c. and 98 F."
    protected_start = source.index("37 c.")
    protected_end = protected_start + len("37 c.")
    matches = list(
        iter_unit_matches(source, "en", protected_spans=[(protected_start, protected_end)])
    )
    assert [source[item.start : item.end] for item in matches] == ["98 F."]


def test_english_temperature_repeated_occurrences_expand_independently() -> None:
    assert abbr2words("37 c. and 37 c.", lang="en") == ("37 degree Celsius and 37 degree Celsius.")


def test_english_in_sentence_is_not_a_unit_match() -> None:
    assert list(iter_unit_matches("They wandered around in.", "en")) == []


@pytest.mark.parametrize(
    ("source", "value", "symbol", "canonical_id"),
    [
        ("5€", "5", "€", "currency-euro"),
        ("5 €", "5", "€", "currency-euro"),
        ("€5", "5", "€", "currency-euro"),
        ("€ 5", "5", "€", "currency-euro"),
        ("12,80 EUR", "12,80", "EUR", "currency-euro"),
        ("$5", "5", "$", "currency-us-dollar"),
        ("USD 5", "5", "USD", "currency-us-dollar"),
        ("5 USD", "5", "USD", "currency-us-dollar"),
        ("£1", "1", "£", "currency-pound-sterling"),
        ("2 GBP", "2", "GBP", "currency-pound-sterling"),
    ],
)
def test_french_currency_matches_preserve_source_identity(
    source: str, value: str, symbol: str, canonical_id: str
) -> None:
    match = only_match(source, "fr")
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id
    assert (
        match.canonical_symbol == symbol
        if symbol in {"€", "$", "£"}
        else match.canonical_symbol in {"€", "$", "£"}
    )
    assert match.language == "fr"
    assert match.category == "currency"
    assert abbr2words(source, lang="fr") == source


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
def test_spanish_currency_matches_preserve_source_identity(
    source: str,
    value: str,
    symbol: str,
    canonical_id: str,
    canonical_symbol: str,
) -> None:
    match = only_match(source, "es")
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id
    assert match.canonical_symbol == canonical_symbol
    assert match.language == "es"
    assert match.category == "currency"
    assert abbr2words(source, lang="es") == source


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
def test_spanish_currency_false_positive_boundaries(source: str) -> None:
    assert list(iter_unit_matches(source, "es")) == []


@pytest.mark.parametrize(
    ("source", "value", "symbol", "canonical_id", "canonical_symbol"),
    [
        ("12,80 EUR", "12,80", "EUR", "currency-euro", "€"),
        ("12,80 €", "12,80", "€", "currency-euro", "€"),
        ("€12,80", "12,80", "€", "currency-euro", "€"),
        ("10 USD", "10", "USD", "currency-us-dollar", "$"),
        ("$10", "10", "$", "currency-us-dollar", "$"),
        ("5 GBP", "5", "GBP", "currency-pound-sterling", "£"),
        ("£5", "5", "£", "currency-pound-sterling", "£"),
    ],
)
def test_italian_structured_currency_matches_preserve_identity_and_offsets(
    source: str,
    value: str,
    symbol: str,
    canonical_id: str,
    canonical_symbol: str,
) -> None:
    matches = list(iter_unit_matches(source, "it_IT"))
    assert len(matches) == 1
    match = matches[0]
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id
    assert match.canonical_symbol == canonical_symbol
    assert match.category == "currency"
    assert match.language == "it"
    assert abbr2words(source, lang="it") == source


@pytest.mark.parametrize(
    ("source", "value", "symbol", "canonical_id", "canonical_symbol"),
    [
        ("100 Kč", "100", "Kč", "currency-czech-koruna", "Kč"),
        ("100 CZK", "100", "CZK", "currency-czech-koruna", "Kč"),
        ("Kč 100", "100", "Kč", "currency-czech-koruna", "Kč"),
        ("CZK 100", "100", "CZK", "currency-czech-koruna", "Kč"),
        ("12,80 Kč", "12,80", "Kč", "currency-czech-koruna", "Kč"),
        ("€ 12,80", "12,80", "€", "currency-euro", "€"),
        ("12,80 EUR", "12,80", "EUR", "currency-euro", "€"),
        ("$ 5", "5", "$", "currency-us-dollar", "$"),
        ("5 USD", "5", "USD", "currency-us-dollar", "$"),
        ("£ 7", "7", "£", "currency-pound-sterling", "£"),
        ("7 GBP", "7", "GBP", "currency-pound-sterling", "£"),
    ],
)
def test_czech_currency_matches_preserve_identity_and_offsets(
    source: str,
    value: str,
    symbol: str,
    canonical_id: str,
    canonical_symbol: str,
) -> None:
    match = only_match(source, "cs")
    assert match.start == 0
    assert match.end == len(source)
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id
    assert match.canonical_symbol == canonical_symbol
    assert match.category == "currency"
    assert match.language == "cs"


@pytest.mark.parametrize(
    "source",
    [
        "Kč",
        "CZK",
        "EUR",
        "priceCZK",
        "CZKprice",
        "A12CZKB",
        "https://example.test/CZK/100",
        "name+CZK@example.test",
        "v1.2.3",
    ],
)
def test_czech_currency_matching_rejects_standalone_and_compound_material(source: str) -> None:
    assert list(iter_unit_matches(source, "cs")) == []


def test_czech_currency_protected_span_suppresses_complete_expression() -> None:
    source = "prefix 100 Kč and CZK 100"
    protected_start = source.index("100 Kč")
    protected_end = protected_start + len("100 Kč")
    matches = list(
        iter_unit_matches(source, "cs", protected_spans=[(protected_start, protected_end)])
    )
    assert [source[item.start : item.end] for item in matches] == ["CZK 100"]
    assert matches[0].canonical_id == "currency-czech-koruna"
    assert matches[0].start == source.index("CZK 100")


@pytest.mark.parametrize(
    "source",
    [
        "Costa 12,80 EUR.",
        "Costa €12,80.",
    ],
)
def test_italian_currency_sentence_punctuation_is_outside_match(source: str) -> None:
    match = only_match(source, "it")
    assert source[match.start : match.end] == source[match.start : -1]
    assert source[match.end :] == "."


def test_italian_currency_protected_spans_suppress_only_protected_quantity() -> None:
    source = "12,80 EUR e 5 EUR"
    protected_end = len("12,80 EUR")
    matches = list(iter_unit_matches(source, "it", protected_spans=[(0, protected_end)]))
    assert [source[item.start : item.end] for item in matches] == ["5 EUR"]
    assert matches[0].start == source.index("5 EUR")
    assert matches[0].value == "5"


@pytest.mark.parametrize(
    "source",
    [
        "EUR",
        "€",
        "$",
        "£",
        "priceEUR",
        "A12EURB",
        "12,80 EURfoo",
        "name@example.com",
        "https://example.com/12,80EUR",
        "12 EUR/USD",
    ],
)
def test_italian_currency_matching_rejects_lexical_and_compound_material(source: str) -> None:
    assert list(iter_unit_matches(source, "it")) == []


def test_spanish_currency_protected_spans_are_source_relative() -> None:
    source = "prefix 12,80 EUR and €5"
    protected_start = source.index("12,80 EUR")
    protected_end = protected_start + len("12,80 EUR")
    matches = list(
        iter_unit_matches(source, "es", protected_spans=[(protected_start, protected_end)])
    )
    assert [source[item.start : item.end] for item in matches] == ["€5"]
    assert matches[0].start == source.index("€5")
    assert source[matches[0].value_start : matches[0].value_end] == "5"


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
        ("12,80 BRL", "12,80", "BRL", "currency-brazilian-real", "R$"),
        ("BRL 12,80", "12,80", "BRL", "currency-brazilian-real", "R$"),
        ("R$12,80", "12,80", "R$", "currency-brazilian-real", "R$"),
        ("12,80 R$", "12,80", "R$", "currency-brazilian-real", "R$"),
    ],
)
def test_portuguese_currency_matches_preserve_identity_and_offsets(
    source: str,
    value: str,
    symbol: str,
    canonical_id: str,
    canonical_symbol: str,
) -> None:
    match = only_match(source, "pt")
    assert match.start == 0
    assert match.end == len(source)
    assert source[match.start : match.end] == source
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id
    assert match.canonical_symbol == canonical_symbol
    assert match.category == "currency"
    assert match.language == "pt"


@pytest.mark.parametrize(
    "source",
    [
        "EUR",
        "BRL",
        "priceEUR",
        "priceBRL",
        "EURprice",
        "BRLprice",
        "A12EURB",
        "A12BRLB",
        "https://example.com/12,80EUR",
        "https://example.com/12,80BRL",
        "12 EUR/USD",
    ],
)
def test_portuguese_currency_matching_rejects_standalone_and_compound_material(
    source: str,
) -> None:
    assert list(iter_unit_matches(source, "pt")) == []


def test_portuguese_currency_protected_spans_suppress_only_protected_quantity() -> None:
    source = "12,80 EUR e R$12,80"
    protected_end = len("12,80 EUR")
    matches = list(iter_unit_matches(source, "pt", protected_spans=[(0, protected_end)]))
    assert [source[item.start : item.end] for item in matches] == ["R$12,80"]
    assert matches[0].start == source.index("R$12,80")
    assert matches[0].value == "12,80"
    assert matches[0].canonical_id == "currency-brazilian-real"


@pytest.mark.parametrize(
    ("source", "value", "symbol", "canonical_id"),
    [
        ("45 min.", "45", "min.", "duration-minute"),
        ("30 sec.", "30", "sec.", "duration-second"),
        ("45 min. puis", "45", "min.", "duration-minute"),
        ("30 sec. avant", "30", "sec.", "duration-second"),
    ],
)
def test_french_dotted_duration_matches_include_complete_symbol(
    source: str, value: str, symbol: str, canonical_id: str
) -> None:
    match = only_match(source, "fr")
    assert source[match.start : match.end] == f"{value} {symbol}"
    assert source[match.value_start : match.value_end] == value
    assert match.value == value
    assert match.symbol == symbol
    assert match.canonical_id == canonical_id
    assert match.language == "fr"
    assert match.category == "unit"


def test_french_numeric_and_lexical_minimum_cases_remain_distinct() -> None:
    assert list(iter_unit_matches("min. requis", "fr")) == []
    assert abbr2words("min. requis", lang="fr") == "minimum requis"
    assert [match.canonical_id for match in iter_unit_matches("45 min. requis", "fr")] == [
        "duration-minute"
    ]


@pytest.mark.parametrize("source", ["admin. requis", "45 minuted", "45 min.-rated", "45 secx"])
def test_french_dotted_duration_boundaries_fail_closed(source: str) -> None:
    assert list(iter_unit_matches(source, "fr")) == []


def test_case_sensitive_milliampere_does_not_accept_lowercase_ma() -> None:
    assert list(iter_unit_matches("2 ma", "de")) == []
    assert only_match("2 mA").symbol == "mA"


def test_dotted_and_undotted_punctuation_is_source_aligned() -> None:
    source = "45 Min., dann 2 kg."
    matches = list(iter_unit_matches(source, "de"))
    assert [(source[item.start : item.end], item.symbol) for item in matches] == [
        ("45 Min.", "Min."),
        ("2 kg", "kg"),
    ]


def test_aliases_share_canonical_identity_with_base_symbols() -> None:
    for source, expected_id, expected_symbol in (
        ("1 h", "duration-hour", "h"),
        ("1 Std.", "duration-hour", "h"),
        ("1 MIN.", "duration-minute", "min"),
        ("1 min", "duration-minute", "min"),
        ("1 l", "volume-liter", "l"),
        ("1 Ltr.", "volume-liter", "l"),
    ):
        match = only_match(source)
        assert match.canonical_id == expected_id
        assert match.canonical_symbol == expected_symbol


@pytest.mark.parametrize(
    "source",
    [
        "2 ma",
        "Model5kg",
        "abc2mA",
        "version1.2kg",
        "5 kg-rated",
        "5 km / h",
        "kg",
        "mA",
        "EUR",
        "Min.",
        "Min. Beispiel",
        "min. 5 Zeichen",
    ],
)
def test_false_positive_and_standalone_protections(source: str) -> None:
    assert list(iter_unit_matches(source, "de")) == []
    assert abbr2words(source, lang="de") == source or source in {
        "Min. Beispiel",
        "min. 5 Zeichen",
    }


def test_magnitude_structured_match_wins_over_lexical_abbreviation() -> None:
    result = abbr2words_with_replacements("1 Mio.", lang="de")
    assert result.text == "1 Millionen"
    assert len(result.replacements) == 1
    assert result.replacements[0].kind == "unit"
    assert abbr2words("Mio.", lang="de") == "Millionen."


def test_protected_spans_suppress_only_the_protected_quantity() -> None:
    source = "2 kg; 3 mA"
    protected_start = source.index("2")
    protected_end = protected_start + len("2 kg")
    matches = list(
        iter_unit_matches(source, "de", protected_spans=[(protected_start, protected_end)])
    )
    assert [source[item.start : item.end] for item in matches] == ["3 mA"]


def test_overrides_and_canonical_suppression_are_explicit() -> None:
    custom = UnitEntry(
        ("kg",),
        "custom kilogram",
        canonical_id="custom-mass-kilogram",
    )
    overridden = only_match("2 kg", overrides={"kg": custom})
    assert overridden.expansion == "custom kilogram"
    assert overridden.canonical_id == "custom-mass-kilogram"
    assert list(iter_unit_matches("2 kg", "de", suppressed={"mass-kilogram"})) == []


def test_expander_unit_customization_retains_identity_and_supports_id_suppression() -> None:
    expander = Expander("de")
    expander.set_unit("kg", "custom kilogram")
    match = next(expander.iter_unit_matches("2 kg"))
    assert match.canonical_id == "mass-kilogram"
    assert match.expansion == "custom kilogram"
    assert expander.remove_unit("mass-kilogram")
    assert list(expander.iter_unit_matches("2 kg")) == []


def test_match_type_is_immutable_and_matches_are_non_overlapping() -> None:
    source = "2 kWh and 3 mAh"
    matches = list(iter_unit_matches(source, "de"))
    assert [(item.symbol, item.canonical_id) for item in matches] == [
        ("kWh", "energy-kilowatt-hour"),
        ("mAh", "charge-milliampere-hour"),
    ]
    assert all(left.end <= right.start for left, right in zip(matches, matches[1:], strict=False))
    with pytest.raises(FrozenInstanceError):
        matches[0].symbol = "Wh"  # type: ignore[misc]


def test_invalid_category_metadata_fails_eagerly() -> None:
    with pytest.raises(ValueError, match="category"):
        UnitEntry(("x",), "x", category="")
