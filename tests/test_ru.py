from __future__ import annotations

import pytest

from abbr2words import abbr2words, normalize_language
from abbr2words.units import iter_unit_matches


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("т. е.", "то есть."),
        ("и т. д.", "и так далее."),
        ("и т. п.", "и тому подобное."),
        ("ж. д.", "железная дорога."),
        ("и др.", "и другие."),
        ("и пр.", "и прочие."),
        ("напр.", "например."),
        ("проф.", "профессор."),
        ("доц.", "доцент."),
        ("акад.", "академик."),
        ("д-р", "доктор"),
    ],
)
def test_russian_lexical_entries(text: str, expected: str) -> None:
    assert abbr2words(text, lang="ru") == expected


def test_russian_alias_and_flexible_horizontal_whitespace() -> None:
    assert normalize_language("rus_RU") == "ru"
    assert abbr2words("т. е. и т.\u00a0д. и\u202fт.\u202fп.", lang="ru") == (
        "то есть и так далее и тому подобное."
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("стр. 4", "страница 4"),
        ("см. 7", "смотри 7"),
        ("см. № 7", "смотри номер 7"),
        ("ср. 4", "сравни 4"),
        ("им. Пушкина", "имени Пушкина"),
        ("обл. Московская", "область Московская"),
    ],
)
def test_russian_guarded_entries(text: str, expected: str) -> None:
    assert abbr2words(text, lang="ru") == expected


@pytest.mark.parametrize(
    "text", ["стр. тест", "см. внимательно", "ср. показатель", "им. значение", "обл. данные"]
)
def test_russian_guarded_entries_reject_weak_context(text: str) -> None:
    assert abbr2words(text, lang="ru") == text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("№ 7", "номер 7"),
        ("г-н Иванов", "господин Иванов"),
        ("г-жа Петрова", "госпожа Петрова"),
        ("тел.: +7 495 123-45-67", "телефон: +7 495 123-45-67"),
        ("тел. 8 800 123-45-67", "телефон 8 800 123-45-67"),
        ("рис. 2", "рисунок 2"),
        ("табл. 3", "таблица 3"),
        ("разд. № 4", "раздел номер 4"),
    ],
)
def test_russian_safe_guarded_additions(text: str, expected: str) -> None:
    assert abbr2words(text, lang="ru") == expected


@pytest.mark.parametrize(
    "text",
    [
        "№ дома",
        "г-н",
        "г-жа.",
        "тел. версия",
        "тел.: нет",
        "рис. текст",
        "табл. данные",
        "разд. содержание",
    ],
)
def test_russian_safe_guarded_additions_reject_weak_context(text: str) -> None:
    assert abbr2words(text, lang="ru") == text


def test_russian_ambiguous_one_letter_forms_are_unchanged() -> None:
    assert abbr2words("г. Москва; 2026 г.; р. Волга", lang="ru") == ("г. Москва; 2026 г.; р. Волга")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("5 кг", "5 килограмм"),
        ("500 г", "500 грамм"),
        ("3 м", "3 метр"),
        ("12 км", "12 километр"),
        ("10 с", "10 секунда"),
        ("2 ч", "2 час"),
        ("20 км/ч", "20 километр в час"),
        ("15 м/с", "15 метр в секунду"),
        ("20 °С", "20 градус Цельсия"),
        ("20 °C", "20 градус Цельсия"),
        ("1 га", "1 гектар"),
        ("100 м²", "100 квадратный метр"),
        ("2 м³", "2 кубический метр"),
        ("100 Вт", "100 ватт"),
        ("5 кВт", "5 киловатт"),
        ("2 кВт·ч", "2 киловатт-час"),
        ("60 Гц", "60 герц"),
        ("2 кГц", "2 килогерц"),
        ("3 МГц", "3 мегагерц"),
        ("4 ГГц", "4 гигагерц"),
        ("220 В", "220 вольт"),
        ("10 А", "10 ампер"),
        ("500 мА", "500 миллиампер"),
        ("101 кПа", "101 килопаскаль"),
        ("1 Па", "1 паскаль"),
        ("1 моль", "1 моль"),
        ("100 Н", "100 ньютон"),
        ("12 Дж", "12 джоуль"),
        ("500 лм", "500 люмен"),
        ("5 МБ", "5 мегабайт"),
        ("100 W", "100 ватт"),
        ("5 kW", "5 киловатт"),
        ("2 kWh", "2 киловатт-час"),
        ("60 Hz", "60 герц"),
        ("220 V", "220 вольт"),
        ("101 kPa", "101 килопаскаль"),
        ("1 mol", "1 моль"),
        ("5 MB", "5 мегабайт"),
    ],
)
def test_russian_unit_expansions(text: str, expected: str) -> None:
    assert abbr2words(text, lang="ru") == expected


@pytest.mark.parametrize("text", ["м", "с", "г", "т", "В", "А"])
def test_russian_single_letter_unit_symbols_require_quantity(text: str) -> None:
    assert abbr2words(text, lang="ru") == text


@pytest.mark.parametrize(
    "text",
    [
        "5 л/100 км",
        "5 л/100\u00a0км",
        "5 л/100\u202fкм",
        "5 мм рт. ст.",
        "5 мм\u00a0рт.\u00a0ст.",
        "5 мм\u202fрт.\u202fст.",
    ],
)
def test_russian_compound_unit_symbols_accept_horizontal_whitespace(text: str) -> None:
    assert abbr2words(text, lang="ru") != text


def test_russian_guarded_reference_and_units() -> None:
    assert abbr2words("стр. 4; 5 kg; 20 km/h", lang="ru") == (
        "страница 4; 5 килограмм; 20 километр в час"
    )


@pytest.mark.parametrize(
    ("latin_text", "russian_text", "canonical_id"),
    [
        ("5 kg", "5 кг", "mass-kilogram"),
        ("60 Hz", "60 Гц", "frequency-hertz"),
        ("100 W", "100 Вт", "power-watt"),
        ("220 V", "220 В", "voltage-volt"),
        ("101 kPa", "101 кПа", "pressure-kilopascal"),
    ],
)
def test_russian_symbol_aliases_share_canonical_unit_identity(
    latin_text: str, russian_text: str, canonical_id: str
) -> None:
    latin = list(iter_unit_matches(latin_text, "ru"))
    russian = list(iter_unit_matches(russian_text, "ru"))

    assert len(latin) == 1
    assert len(russian) == 1
    assert latin[0].canonical_id == russian[0].canonical_id == canonical_id
    assert latin[0].expansion == russian[0].expansion
