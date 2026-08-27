from __future__ import annotations

import pytest

from abbr2words import abbr2words, get_expander, iter_unit_matches
from abbr2words.language_data import bundle_for
from abbr2words.unit_data.common import COMMON_UNIT_DEFINITIONS, UNIT_LABELS


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("นพ. สมชาย", "นายแพทย์ สมชาย"),
        ("นพ.สมชาย", "นายแพทย์สมชาย"),
        ("พญ. สมหญิง", "แพทย์หญิง สมหญิง"),
        ("พญ.สมหญิง", "แพทย์หญิงสมหญิง"),
        ("ทพ. สมชาย", "ทันตแพทย์ สมชาย"),
        ("ทพญ. สมหญิง", "ทันตแพทย์หญิง สมหญิง"),
        ("รศ. สมชาย", "รองศาสตราจารย์ สมชาย"),
        ("ผศ.ดร.สมหญิง", "ผู้ช่วยศาสตราจารย์ดร.สมหญิง"),
        ("ดร.สมชาย", "ดอกเตอร์สมชาย"),
    ],
)
def test_th_source_backed_titles(source: str, expected: str) -> None:
    assert abbr2words(source, lang="th") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("พ.ศ. 2569", "พุทธศักราช 2569"),
        ("พ.ศ. ๒๕๖๙", "พุทธศักราช ๒๕๖๙"),
        ("ค.ศ. 2026", "คริสต์ศักราช 2026"),
    ],
)
def test_th_eras(source: str, expected: str) -> None:
    assert abbr2words(source, lang="th") == expected


THAI_MONTHS = (
    ("ม.ค.", "มกราคม"),
    ("ก.พ.", "กุมภาพันธ์"),
    ("มี.ค.", "มีนาคม"),
    ("เม.ย.", "เมษายน"),
    ("พ.ค.", "พฤษภาคม"),
    ("มิ.ย.", "มิถุนายน"),
    ("ก.ค.", "กรกฎาคม"),
    ("ส.ค.", "สิงหาคม"),
    ("ก.ย.", "กันยายน"),
    ("ต.ค.", "ตุลาคม"),
    ("พ.ย.", "พฤศจิกายน"),
    ("ธ.ค.", "ธันวาคม"),
)


@pytest.mark.parametrize(("abbreviation", "expansion"), THAI_MONTHS)
def test_th_months_require_date_context(abbreviation: str, expansion: str) -> None:
    assert abbr2words(f"27 {abbreviation} 2569", lang="th") == f"27 {expansion} 2569"
    assert abbr2words(f"๒๗{abbreviation}๒๕๖๙", lang="th") == f"๒๗{expansion}๒๕๖๙"


@pytest.mark.parametrize(
    "source",
    ["สำนักงาน ก.พ.", "ก.พ. รายงานผล", "ABCก.พ.XYZ", "กข.", "xyz."],
)
def test_th_ambiguous_or_unknown_forms_are_preserved(source: str) -> None:
    assert abbr2words(source, lang="th") == source


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("05.00 น.", "05.00 นาฬิกา"),
        ("05:00 น.", "05:00 นาฬิกา"),
        ("๐๕.๐๐ น.", "๐๕.๐๐ นาฬิกา"),
        ("๐๕:๐๐ น.", "๐๕:๐๐ นาฬิกา"),
    ],
)
def test_th_clock_marker(source: str, expected: str) -> None:
    assert abbr2words(source, lang="th") == expected


@pytest.mark.parametrize("source", ["น. สมชาย", "ตัวอักษร น."])
def test_th_clock_marker_requires_time_context(source: str) -> None:
    assert abbr2words(source, lang="th") == source


@pytest.mark.parametrize(
    ("source", "expected", "canonical_id"),
    [
        ("5 ม.", "5 เมตร", "length-meter"),
        ("๕ ม.", "๕ เมตร", "length-meter"),
        ("5 กม.", "5 กิโลเมตร", "length-kilometer"),
        ("๕ กม.", "๕ กิโลเมตร", "length-kilometer"),
        ("10 ซม.", "10 เซนติเมตร", "length-centimeter"),
        ("10 มม.", "10 มิลลิเมตร", "length-millimeter"),
        ("2 กก.", "2 กิโลกรัม", "mass-kilogram"),
        ("250 ก.", "250 กรัม", "mass-gram"),
        ("5 มก.", "5 มิลลิกรัม", "mass-milligram"),
        ("2 ล.", "2 ลิตร", "volume-liter"),
        ("3 ชม.", "3 ชั่วโมง", "duration-hour"),
        ("25 ตร.ม.", "25 ตารางเมตร", "area-square-meter"),
        ("4 ลบ.ม.", "4 ลูกบาศก์เมตร", "volume-cubic-meter"),
    ],
)
def test_th_native_unit_aliases(source: str, expected: str, canonical_id: str) -> None:
    assert abbr2words(source, lang="th") == expected
    match = next(iter_unit_matches(source, "th"))
    assert (match.symbol, match.canonical_id) == (source.split()[-1], canonical_id)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("5 m", "5 เมตร"),
        ("10 cm", "10 เซนติเมตร"),
        ("20 mm", "20 มิลลิเมตร"),
        ("2 h", "2 ชั่วโมง"),
        ("3 s", "3 วินาที"),
        ("25 °C", "25 องศาเซลเซียส"),
        ("100 kPa", "100 กิโลปาสกาล"),
        ("1 GB", "1 กิกะไบต์"),
    ],
)
def test_th_latin_units_use_localized_labels(source: str, expected: str) -> None:
    assert abbr2words(source, lang="th") == expected


def test_th_common_units_are_fully_localized() -> None:
    expected_ids = {definition.canonical_id for definition in COMMON_UNIT_DEFINITIONS}
    assert set(UNIT_LABELS["th"]) == expected_ids
    assert all(
        entry.expansion != entry.canonical_symbol for entry in get_expander("th").unit_entries
    )


@pytest.mark.parametrize(
    ("source", "canonical_id", "symbol"),
    [
        ("5 ม.", "length-meter", "ม."),
        ("๕ กม.", "length-kilometer", "กม."),
        ("2 กก.", "mass-kilogram", "กก."),
        ("3 ชม.", "duration-hour", "ชม."),
        ("25 ตร.ม.", "area-square-meter", "ตร.ม."),
    ],
)
def test_th_unit_matches_preserve_semantic_identity(
    source: str, canonical_id: str, symbol: str
) -> None:
    match = next(iter_unit_matches(source, "th"))
    assert match.canonical_id == canonical_id
    assert match.symbol == symbol


@pytest.mark.parametrize("source", ["฿100", "100 ฿", "THB 100", "100 THB"])
def test_th_baht_currency_identity(source: str) -> None:
    match = next(iter_unit_matches(source, "th"))
    assert match.canonical_id == "currency-thai-baht"
    assert abbr2words(source, lang="th") == source


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("ระยะ 5 ม.", "ระยะ 5 เมตร"),
        ("น้ำหนัก 2 กก.", "น้ำหนัก 2 กิโลกรัม"),
        ("ใช้เวลา 3 ชม.", "ใช้เวลา 3 ชั่วโมง"),
        ("5กม.", "5 กิโลเมตร"),
        ("๕กม.", "๕ กิโลเมตร"),
        ("25ตร.ม.", "25 ตารางเมตร"),
    ],
)
def test_th_unit_punctuation_and_no_space_rendering(source: str, expected: str) -> None:
    assert abbr2words(source, lang="th") == expected


def test_th_meter_alias_is_not_guessed_as_university() -> None:
    assert abbr2words("5 ม.", lang="th") == "5 เมตร"
    assert abbr2words("๕ ม.", lang="th") == "๕ เมตร"
    assert abbr2words("ม.เชียงใหม่", lang="th") == "ม.เชียงใหม่"


def test_th_registry_and_sources_remain_resolvable() -> None:
    assert get_expander("th").has_abbreviation("นพ.", case_sensitive=True)
    assert {source.id for source in bundle_for("th").sources} >= {
        "th-orst-abbreviation-rules",
        "th-orst-professional-titles",
        "unicode-cldr-48.2.1-th",
        "th-tisi-si-units",
    }
