from __future__ import annotations

import pytest

from abbr2words import abbr2words
from abbr2words.units import unit_entries


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("№12", "번호12"),
        ("№ 12", "번호 12"),
        ("p. 12", "페이지 12"),
        ("(주)한빛", "주식회사한빛"),
        ("한빛(주)", "한빛주식회사"),
        ("㈜한빛", "주식회사한빛"),
        ("한빛㈜", "한빛주식회사"),
    ],
)
def test_korean_reviewed_abbreviations(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ko") == expected


@pytest.mark.parametrize(
    "text",
    [
        "1번",
        "1 번",
        "12번",
        "한 번",
        "두 번",
        "이번",
        "저번",
        "번호 12",
        "번 12",
    ],
)
def test_korean_beon_is_not_abbreviation(text: str) -> None:
    assert abbr2words(text, lang="ko") == text


@pytest.mark.parametrize("text", ["이번 주", "주가가 올랐다", "주 5일", "주식", "주문"])
def test_korean_plain_ju_is_unchanged(text: str) -> None:
    assert abbr2words(text, lang="ko") == text


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("5 s", "5 초"),
        ("5 min", "5 분"),
        ("5 h", "5 시간"),
        ("5 d", "5 일"),
        ("5 mm", "5 밀리미터"),
        ("5 cm", "5 센티미터"),
        ("5 m", "5 미터"),
        ("5 km", "5 킬로미터"),
        ("250 mL", "250 밀리리터"),
        ("2 L", "2 리터"),
        ("10 µg", "10 마이크로그램"),
        ("10 mg", "10 밀리그램"),
        ("500 g", "500 그램"),
        ("2 kg", "2 킬로그램"),
        ("3 t", "3 메트릭 톤"),
        ("300 K", "300 켈빈"),
        ("100 Pa", "100 파스칼"),
        ("100 kPa", "100 킬로파스칼"),
        ("2 atm", "2 기압"),
        ("2 B", "2 바이트"),
        ("500 MB", "500 메가바이트"),
        ("2 m²", "2 제곱미터"),
        ("3 m³", "3 세제곱미터"),
    ],
)
def test_korean_unit_labels(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ko") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("20°C", "섭씨 20도"),
        ("68°F", "화씨 68도"),
        ("5 m/s", "초속 5미터"),
        ("80 km/h", "시속 80킬로미터"),
        ("60 mph", "시속 60마일"),
        ("7 L/100km", "100킬로미터당 7리터"),
        ("5 m³/s", "초당 5세제곱미터"),
    ],
)
def test_korean_quantity_templates(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ko") == expected


def test_korean_common_inventory_is_complete_and_localized() -> None:
    entries = unit_entries("ko")

    assert len(entries) == 38
    assert all(entry.expansion != entry.canonical_symbol for entry in entries)
    assert {entry.canonical_id for entry in entries} == {
        "duration-second",
        "duration-minute",
        "duration-hour",
        "duration-day",
        "length-millimeter",
        "length-centimeter",
        "length-meter",
        "length-kilometer",
        "volume-milliliter",
        "volume-liter",
        "mass-microgram",
        "mass-milligram",
        "mass-gram",
        "mass-kilogram",
        "mass-tonne",
        "temperature-kelvin",
        "temperature-celsius",
        "temperature-fahrenheit",
        "speed-meter-per-second",
        "speed-kilometer-per-hour",
        "speed-mile-per-hour",
        "pressure-pascal",
        "pressure-kilopascal",
        "pressure-atmosphere",
        "data-byte",
        "data-kilobyte",
        "data-megabyte",
        "data-gigabyte",
        "fuel-consumption-liter-per-100-kilometer",
        "flow-cubic-meter-per-second",
        "area-square-millimeter",
        "area-square-centimeter",
        "area-square-meter",
        "area-square-kilometer",
        "area-hectare",
        "volume-cubic-millimeter",
        "volume-cubic-centimeter",
        "volume-cubic-meter",
    }


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("AI", "에이아이"),
        ("KTX", "케이티엑스"),
        ("TV", "티브이"),
        ("PC", "피시"),
        ("ICT", "아이시티"),
        ("LED", "엘이디"),
    ],
)
def test_korean_reviewed_initialisms(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ko") == expected


@pytest.mark.parametrize("source", ["NASA", "AAPL", "NVDA", "LG", "SK", "KT", "A320", "H100"])
def test_korean_unreviewed_initialisms_are_not_guessed(source: str) -> None:
    assert abbr2words(source, lang="ko") == source


@pytest.mark.parametrize("language", ["ko-KR", "ko_KR"])
def test_korean_language_aliases(language: str) -> None:
    assert abbr2words("5 km", lang=language) == abbr2words("5 km", lang="ko")
