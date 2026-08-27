from __future__ import annotations

import pytest

from abbr2words import abbr2words
from abbr2words.unit_data.common import COMMON_UNIT_DEFINITIONS, UNIT_LABELS
from abbr2words.units import iter_unit_matches, unit_entries


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("tr. 12", "trang 12"),
        ("ĐT: 0914.858.982", "điện thoại: 0914.858.982"),
        ("ĐT. 0914.858.982", "điện thoại 0914.858.982"),
        ("SĐT: 0914.858.982", "số điện thoại: 0914.858.982"),
        ("SĐT. 0914.858.982", "số điện thoại 0914.858.982"),
        ("TP. Hà Nội", "thành phố Hà Nội"),
        ("TP. Hồ Chí Minh", "thành phố Hồ Chí Minh"),
        ("TP. Đà Nẵng", "thành phố Đà Nẵng"),
    ],
)
def test_vietnamese_reviewed_abbreviations(source: str, expected: str) -> None:
    assert abbr2words(source, lang="vi") == expected


@pytest.mark.parametrize(
    "source",
    [
        "tr. văn bản",
        "ĐT: văn phòng",
        "SĐT: chưa cập nhật",
        "đt: 0914.858.982",
        "sđt: 0914.858.982",
        "tp. Hà Nội",
        "TP. 123",
        "TP. = 0.8",
        "TP. abc",
        "Số 30/2020/NĐ-CP",
        "QĐ-TTg",
        "UBND",
        "HĐND",
    ],
)
def test_vietnamese_ambiguous_or_structured_tokens_are_preserved(source: str) -> None:
    assert abbr2words(source, lang="vi") == source


def test_vietnamese_mixed_address_and_identifier() -> None:
    assert abbr2words("UBND TP. Hà Nội", lang="vi") == "UBND thành phố Hà Nội"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("PGS.TS. Trần Văn Quy", "phó giáo sư tiến sĩ Trần Văn Quy"),
        ("TS. Nguyễn Xuân Huân", "tiến sĩ Nguyễn Xuân Huân"),
    ],
)
def test_vietnamese_academic_titles(source: str, expected: str) -> None:
    assert abbr2words(source, lang="vi") == expected


@pytest.mark.parametrize("source", ["TS. văn bản", "ts. Nguyễn Văn A", "TS. 123"])
def test_vietnamese_academic_title_false_positives(source: str) -> None:
    assert abbr2words(source, lang="vi") == source


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("1 s", "1 giây"),
        ("2 min", "2 phút"),
        ("3 h", "3 giờ"),
        ("4 d", "4 ngày"),
        ("5 mm", "5 milimét"),
        ("6 cm", "6 xentimét"),
        ("7 m", "7 mét"),
        ("8 km", "8 kilômét"),
        ("9 mL", "9 mililít"),
        ("10 L", "10 lít"),
        ("11 µg", "11 micrôgam"),
        ("12 mg", "12 miligam"),
        ("13 g", "13 gam"),
        ("14 kg", "14 kilôgam"),
        ("15 t", "15 tấn"),
        ("273 K", "273 kenvin"),
        ("20 °C", "20 độ Celsius"),
        ("70 °F", "70 độ Fahrenheit"),
        ("5 m/s", "5 mét trên giây"),
        ("80 km/h", "80 kilômét trên giờ"),
        ("60 mph", "60 dặm trên giờ"),
        ("100 Pa", "100 pascan"),
        ("100 kPa", "100 kilôpascan"),
        ("1 atm", "1 átmốtphe"),
        ("1 B", "1 byte"),
        ("2 kB", "2 kilobyte"),
        ("3 MB", "3 megabyte"),
        ("4 GB", "4 gigabyte"),
        ("6 L/100km", "6 lít trên 100 kilômét"),
        ("2 m³/s", "2 mét khối trên giây"),
        ("2 mm²", "2 milimét vuông"),
        ("2 cm²", "2 xentimét vuông"),
        ("2 m²", "2 mét vuông"),
        ("2 km²", "2 kilômét vuông"),
        ("2 ha", "2 héc-ta"),
        ("2 mm³", "2 milimét khối"),
        ("2 cm³", "2 xentimét khối"),
        ("2 m³", "2 mét khối"),
    ],
)
def test_vietnamese_unit_labels(source: str, expected: str) -> None:
    assert abbr2words(source, lang="vi") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("ug", "micrôgam"),
        ("μg", "micrôgam"),
        ("ml", "mililít"),
        ("l", "lít"),
        ("m3/s", "mét khối trên giây"),
        ("m2", "mét vuông"),
        ("m3", "mét khối"),
    ],
)
def test_vietnamese_unit_aliases(source: str, expected: str) -> None:
    assert abbr2words(f"2 {source}", lang="vi") == f"2 {expected}"


@pytest.mark.parametrize("source", ["m is a letter", "L is a label", "Pa is a name"])
def test_vietnamese_standalone_unit_symbols_are_preserved(source: str) -> None:
    assert abbr2words(source, lang="vi") == source


def test_all_common_vietnamese_units_have_spoken_labels() -> None:
    expected = {definition.canonical_id for definition in COMMON_UNIT_DEFINITIONS}
    assert set(UNIT_LABELS["vi"]) == expected
    assert len(unit_entries("vi")) == len(COMMON_UNIT_DEFINITIONS) + 1
    assert all(
        entry.expansion != entry.canonical_symbol
        for entry in unit_entries("vi")
        if entry.category != "currency"
    )


def test_vietnamese_currency_identity() -> None:
    for source, symbol in (("1000 VND", "VND"), ("₫1000", "₫")):
        matches = tuple(iter_unit_matches(source, "vi"))
        assert len(matches) == 1
        assert matches[0].canonical_id == "currency-vietnamese-dong"
        assert matches[0].symbol == symbol
        assert matches[0].value == "1000"
        assert matches[0].expansion == "đồng Việt Nam"
