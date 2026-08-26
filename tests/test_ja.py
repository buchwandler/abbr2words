from __future__ import annotations

import pytest

from abbr2words import UnitEntry, abbr2words
from abbr2words.units import unit_entries


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("№12", "番号12"),
        ("№ 12", "番号 12"),
        ("（株）東京商事", "株式会社東京商事"),
        ("東京商事（株）", "東京商事株式会社"),
        ("(株)東京商事", "株式会社東京商事"),
        ("㈱東京商事", "株式会社東京商事"),
        ("（有）山田商店", "有限会社山田商店"),
        ("山田商店（有）", "山田商店有限会社"),
        ("㈲山田商店", "有限会社山田商店"),
    ],
)
def test_japanese_reviewed_abbreviations(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ja") == expected


@pytest.mark.parametrize(
    "text",
    [
        "№ example",
        "一番人気",
        "当番12人",
        "番組",
        "13番10号",
        "第3番",
        "株価が上昇した",
        "有効期限",
        "学校で学ぶ",
        "頁 text",
        "頁 12",
    ],
)
def test_japanese_false_positives_are_unchanged(text: str) -> None:
    assert abbr2words(text, lang="ja") == text


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("5 s", "5 秒"),
        ("5 h", "5 時間"),
        ("5 d", "5 日"),
        ("5 mm", "5 ミリメートル"),
        ("5 cm", "5 センチメートル"),
        ("5 m", "5 メートル"),
        ("5 mL", "5 ミリリットル"),
        ("5 L", "5 リットル"),
        ("5 µg", "5 マイクログラム"),
        ("5 mg", "5 ミリグラム"),
        ("5 t", "5 トン"),
        ("300 K", "300 ケルビン"),
        ("100 Pa", "100 パスカル"),
        ("100 kPa", "100 キロパスカル"),
        ("2 atm", "2 気圧"),
        ("500 MB", "500 メガバイト"),
        ("2 m²", "2 平方メートル"),
        ("3 m³", "3 立方メートル"),
    ],
)
def test_japanese_unit_labels(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ja") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("20°C", "摂氏 20 度"),
        ("68°F", "華氏 68 度"),
        ("5 m/s", "秒速 5 メートル"),
        ("80 km/h", "時速 80 キロメートル"),
        ("60 mph", "時速 60 マイル"),
    ],
)
def test_japanese_quantity_templates(source: str, expected: str) -> None:
    assert abbr2words(source, lang="ja") == expected


def test_japanese_common_inventory_is_complete_and_localized() -> None:
    entries = unit_entries("ja")

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


@pytest.mark.parametrize("language", ["ja-JP", "ja_JP"])
def test_japanese_language_aliases(language: str) -> None:
    assert abbr2words("5 km", lang=language) == abbr2words("5 km", lang="ja")


def test_jp_is_not_a_language_key() -> None:
    with pytest.raises(ValueError, match="Unsupported language"):
        abbr2words("№ 12", lang="jp")


@pytest.mark.parametrize("template", ["{value} {other}", "{value}{value}", "{}"])
def test_quantity_template_requires_one_value_placeholder(template: str) -> None:
    with pytest.raises(ValueError, match="exactly one"):
        UnitEntry(("x",), "x", quantity_template=template)
