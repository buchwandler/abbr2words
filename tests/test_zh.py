from __future__ import annotations

import pytest

from abbr2words import abbr2words
from abbr2words.units import unit_entries


@pytest.mark.parametrize(
    ("source", "expected"),
    [("№12", "编号12"), ("№ 12", "编号 12")],
)
def test_chinese_reviewed_abbreviations(source: str, expected: str) -> None:
    assert abbr2words(source, lang="zh_CN") == expected


@pytest.mark.parametrize(
    "text",
    ["页 12", "号 12", "12页", "12号", "第12页", "编号12", "页码12", "号码12"],
)
def test_chinese_plain_reference_words_are_not_abbreviations(text: str) -> None:
    assert abbr2words(text, lang="zh_CN") == text


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("5 s", "5 秒"),
        ("5 min", "5 分钟"),
        ("5 h", "5 小时"),
        ("5 d", "5 天"),
        ("5 mm", "5 毫米"),
        ("5 cm", "5 厘米"),
        ("5 m", "5 米"),
        ("5 km", "5 公里"),
        ("250 mL", "250 毫升"),
        ("2 L", "2 升"),
        ("10 µg", "10 微克"),
        ("10 mg", "10 毫克"),
        ("500 g", "500 克"),
        ("2 kg", "2 千克"),
        ("3 t", "3 吨"),
        ("300 K", "300 开尔文"),
        ("20°C", "20 摄氏度"),
        ("68°F", "68 华氏度"),
        ("100 Pa", "100 帕斯卡"),
        ("101.3 kPa", "101.3 千帕斯卡"),
        ("2 atm", "2 标准大气压"),
        ("2 B", "2 字节"),
        ("2 kB", "2 千字节"),
        ("500 MB", "500 兆字节"),
        ("16 GB", "16 吉字节"),
        ("2 mm²", "2 平方毫米"),
        ("2 cm²", "2 平方厘米"),
        ("2 m²", "2 平方米"),
        ("2 km²", "2 平方公里"),
        ("5 ha", "5 公顷"),
        ("2 mm³", "2 立方毫米"),
        ("2 cm³", "2 立方厘米"),
        ("3 m³", "3 立方米"),
    ],
)
def test_chinese_mainland_unit_labels(source: str, expected: str) -> None:
    assert abbr2words(source, lang="zh_CN") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("5 m/s", "每秒5米"),
        ("80 km/h", "每小时80公里"),
        ("60 mph", "每小时60英里"),
        ("7 L/100km", "每100公里7升"),
        ("5 m³/s", "每秒5立方米"),
    ],
)
def test_chinese_mainland_quantity_templates(source: str, expected: str) -> None:
    assert abbr2words(source, lang="zh_CN") == expected


def test_chinese_mainland_common_inventory_is_complete_and_localized() -> None:
    entries = [entry for entry in unit_entries("zh_CN") if entry.category != "currency"]

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
    assert len(unit_entries("zh_CN")) == 39
    assert any(entry.canonical_id == "currency-chinese-yuan" for entry in unit_entries("zh_CN"))


def test_chinese_mainland_does_not_localize_sibling_units() -> None:
    assert abbr2words("16 GB", lang="zh_HK") == "16 GB"
    assert abbr2words("16 GB", lang="zh_TW") == "16 GB"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("AI", "人工智能"),
        ("AI技术", "人工智能技术"),
        ("生成式AI模型", "生成式人工智能模型"),
        ("AIDS患者", "艾滋病患者"),
        ("GDP增长", "国内生产总值增长"),
        ("IQ测试", "智商测试"),
        ("IT行业", "信息技术行业"),
        ("OECD报告", "经济合作与发展组织报告"),
        ("OPEC会议", "石油输出国组织会议"),
        ("WHO发布", "世界卫生组织发布"),
        ("WTO规则", "世界贸易组织规则"),
    ],
)
def test_chinese_mainland_reviewed_latin_abbreviations(source: str, expected: str) -> None:
    assert abbr2words(source, lang="zh_CN") == expected


@pytest.mark.parametrize(
    "source",
    ["OpenAI", "AIGC", "GDP2", "WHO.int", "AI-model", "A320", "H100", "AAPL", "NVDA", "NASA"],
)
def test_chinese_mainland_unreviewed_or_embedded_tokens_are_unchanged(source: str) -> None:
    assert abbr2words(source, lang="zh_CN") == source


@pytest.mark.parametrize("language", ["zh-CN", "zh_CN"])
def test_chinese_mainland_language_aliases(language: str) -> None:
    assert abbr2words("5 km", lang=language) == "5 公里"
