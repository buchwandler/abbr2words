from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from abbr2words import (
    Expander,
    UnitEntry,
    UnitMatch,
    abbr2words,
    abbr2words_with_replacements,
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
    assert abbr2words("Mio.", lang="de") == "Millionen"


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
