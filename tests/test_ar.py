from __future__ import annotations

import pytest

from abbr2words import abbr2words, get_expander, iter_unit_matches
from abbr2words.language_data import bundle_for
from abbr2words.unit_data.common import COMMON_UNIT_DEFINITIONS, UNIT_LABELS
from abbr2words.units import unit_entries


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("د. أحمد", "دكتور أحمد"),
        ("م. أحمد", "مهندس أحمد"),
        ("ص. 12", "صفحة 12"),
        ("ص. ١٢", "صفحة ١٢"),
        ("ص 12", "صفحة 12"),
        ("ص ١٢", "صفحة ١٢"),
    ],
)
def test_ar_source_backed_abbreviations(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ar") == expected


@pytest.mark.parametrize(
    "text",
    [
        "ص النص",
        "ص. النص",
        "3 م.",
        "3 م",
        "م",
        "هـ",
        "UN WHO ABC",
    ],
)
def test_ar_ambiguous_tokens_are_preserved(text: str) -> None:
    assert abbr2words(text, lang="ar") == text


def test_ar_dotted_gregorian_year_is_not_engineer() -> None:
    assert abbr2words("2026 م.", lang="ar") == "2026 ميلادي."
    assert abbr2words("2026 م.", lang="ar") != "2026 مهندس."


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("1447 هـ", "1447 هجري"),
        ("١٤٤٧ هـ", "١٤٤٧ هجري"),
        ("2026 م", "2026 ميلادي"),
        ("٢٠٢٦ م", "٢٠٢٦ ميلادي"),
        ("323 ق.م", "323 قبل الميلاد"),
        ("٣٢٣ ق.م", "٣٢٣ قبل الميلاد"),
        ("1447هـ", "1447هجري"),
        ("١٤٤٧هـ", "١٤٤٧هجري"),
        ("2026م", "2026ميلادي"),
        ("٢٠٢٦م", "٢٠٢٦ميلادي"),
    ],
)
def test_ar_numeric_era_markers(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ar") == expected


AR_UNIT_CASES = (
    ("1 s", "1 ثانية"),
    ("2 min", "2 دقيقة"),
    ("3 h", "3 ساعة"),
    ("4 d", "4 يوم"),
    ("5 mm", "5 مليمتر"),
    ("6 cm", "6 سنتيمتر"),
    ("7 m", "7 متر"),
    ("8 km", "8 كيلومتر"),
    ("9 mL", "9 مليلتر"),
    ("10 L", "10 لتر"),
    ("11 µg", "11 ميكروغرام"),
    ("12 mg", "12 مليغرام"),
    ("13 g", "13 غرام"),
    ("14 kg", "14 كيلوغرام"),
    ("15 t", "15 طن متري"),
    ("16 K", "16 درجة كلفن"),
    ("17 °C", "17 درجة مئوية"),
    ("18 °F", "18 درجة فهرنهايت"),
    ("19 m/s", "19 متر في الثانية"),
    ("20 km/h", "20 كيلومتر في الساعة"),
    ("21 mph", "21 ميل في الساعة"),
    ("22 Pa", "22 باسكال"),
    ("23 kPa", "23 كيلوباسكال"),
    ("24 atm", "24 ضغط جوي"),
    ("25 B", "25 بايت"),
    ("26 kB", "26 كيلوبايت"),
    ("27 MB", "27 ميغابايت"),
    ("28 GB", "28 غيغابايت"),
    ("29 L/100km", "29 لتر لكل 100 كيلومتر"),
    ("30 m³/s", "30 متر مكعب في الثانية"),
    ("31 mm²", "31 مليمتر مربع"),
    ("32 cm²", "32 سنتيمتر مربع"),
    ("33 m²", "33 متر مربع"),
    ("34 km²", "34 كيلومتر مربع"),
    ("35 ha", "35 هكتار"),
    ("36 mm³", "36 مليمتر مكعب"),
    ("37 cm³", "37 سنتيمتر مكعب"),
    ("38 m³", "38 متر مكعب"),
)


@pytest.mark.parametrize(("source", "expected"), AR_UNIT_CASES)
def test_ar_unit_labels(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ar") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("٥ kg", "٥ كيلوغرام"),
        ("١٠ cm", "١٠ سنتيمتر"),
        ("٢٠ °C", "٢٠ درجة مئوية"),
        ("٨٠ km/h", "٨٠ كيلومتر في الساعة"),
    ],
)
def test_ar_arabic_indic_quantity_labels(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ar") == expected


@pytest.mark.parametrize(
    "symbol", ["ug", "μg", "µg", "ml", "mL", "l", "L", "m2", "m²", "m3", "m³", "m3/s", "m³/s"]
)
def test_ar_shared_unit_aliases(symbol: str) -> None:
    assert abbr2words(f"2 {symbol}", lang="ar") != f"2 {symbol}"


@pytest.mark.parametrize("source", ["m is a symbol", "kg text", "MB file", "Pa value"])
def test_ar_units_do_not_expand_without_quantity(source: str) -> None:
    assert abbr2words(source, lang="ar") == source


def test_ar_has_labels_for_every_common_unit() -> None:
    expected = {definition.canonical_id for definition in COMMON_UNIT_DEFINITIONS}
    assert set(UNIT_LABELS["ar"]) == expected
    assert len(unit_entries("ar")) == len(COMMON_UNIT_DEFINITIONS)
    assert all(entry.expansion != entry.canonical_symbol for entry in unit_entries("ar"))


@pytest.mark.parametrize(
    ("source", "canonical_id", "symbol"),
    [
        ("5 m", "length-meter", "m"),
        ("6 kg", "mass-kilogram", "kg"),
        ("7 m²", "area-square-meter", "m²"),
        ("8 m3/s", "flow-cubic-meter-per-second", "m3/s"),
        ("9 L/100km", "fuel-consumption-liter-per-100-kilometer", "L/100km"),
    ],
)
def test_ar_unit_matches_preserve_semantic_identity(
    source: str, canonical_id: str, symbol: str
) -> None:
    match = next(iter_unit_matches(source, "ar"))
    assert match.canonical_id == canonical_id
    assert match.symbol == symbol


def test_ar_registry_and_sources_remain_resolvable() -> None:
    expander = get_expander("ar")
    assert expander.has_abbreviation("د.", case_sensitive=True)
    assert expander.has_abbreviation("م.", case_sensitive=True)
    assert expander.has_abbreviation("م", case_sensitive=True)
    assert {source.id for source in bundle_for("ar").sources} >= {
        "ar-unicode-cldr-48-units",
        "ar-unicode-cldr-48-calendar-eras",
        "ar-ksu-official-correspondence-titles",
        "ar-saudi-official-era-usage",
        "ar-ksu-reference-style",
        "bipm-si",
    }
    assert {
        source_id for seed in bundle_for("ar").abbreviations for source_id in seed.source_ids
    } >= {
        "ar-ksu-official-correspondence-titles",
        "ar-ksu-reference-style",
        "ar-unicode-cldr-48-calendar-eras",
    }


def test_ar_unknown_latin_initialisms_are_preserved() -> None:
    assert abbr2words("UN WHO ABC", lang="ar") == "UN WHO ABC"
