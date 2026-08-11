from __future__ import annotations

from abbr2words import abbr2words, normalize_language


def test_russian_alias_and_flexible_horizontal_whitespace() -> None:
    assert normalize_language("rus_RU") == "ru"
    assert abbr2words("т. е. и т.\u00a0д. и\u202fт.\u202fп.", lang="ru") == (
        "то есть и так далее и тому подобное."
    )


def test_russian_ambiguous_one_letter_forms_are_unchanged() -> None:
    assert abbr2words("г. Москва; 2026 г.; р. Волга", lang="ru") == ("г. Москва; 2026 г.; р. Волга")


def test_russian_guarded_reference_and_units() -> None:
    assert abbr2words("стр. 4; 5 kg; 20 km/h", lang="ru") == (
        "страница 4; 5 килограмм; 20 километр в час"
    )
