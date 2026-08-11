from __future__ import annotations

import pytest

from abbr2words import (
    AbbreviationEntry,
    abbr2words,
    get_expander,
    get_shared_expander,
    normalize_language,
    supported_languages,
)
from abbr2words.units import iter_unit_matches, unit_entries, validate_unit_registry

RELEASED_BASE_KEYS = (
    "am",
    "ar",
    "az",
    "be",
    "bn",
    "ca",
    "ce",
    "cs",
    "cy",
    "da",
    "de",
    "en",
    "eo",
    "es",
    "fa",
    "fi",
    "fr",
    "he",
    "hu",
    "id",
    "is",
    "it",
    "ja",
    "kn",
    "ko",
    "kz",
    "lt",
    "lv",
    "nl",
    "no",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sr",
    "sv",
    "te",
    "tet",
    "tg",
    "th",
    "tr",
    "uk",
    "vi",
)
RELEASED_LOCALE_KEYS = (
    "en_GB",
    "en_IN",
    "en_NG",
    "en_US",
    "es_CO",
    "es_CR",
    "es_GT",
    "es_NI",
    "es_MX",
    "es_VE",
    "fr_BE",
    "fr_CH",
    "fr_DZ",
    "pt_BR",
)
MASTER_ONLY_BASE_KEYS = ("hi", "hy", "mn", "zh")
MASTER_ONLY_LOCALE_KEYS = ("zh_CN", "zh_HK", "zh_TW")


def test_released_baseline_base_keys_are_explicit() -> None:
    base_keys = set(RELEASED_BASE_KEYS) | set(MASTER_ONLY_BASE_KEYS)
    assert set(supported_languages(include_locales=False)) == base_keys
    assert set(supported_languages()) == (
        base_keys | set(RELEASED_LOCALE_KEYS) | set(MASTER_ONLY_LOCALE_KEYS)
    )


@pytest.mark.parametrize("language", RELEASED_BASE_KEYS)
def test_every_released_base_instantiates_and_validates(language: str) -> None:
    expander = get_expander(language)
    assert expander.entries
    assert get_shared_expander(language).entries
    assert abbr2words("", lang=language) == ""
    assert unit_entries(language)
    validate_unit_registry(language)
    matches = tuple(iter_unit_matches("500 g", language))
    assert len(matches) == 1
    assert matches[0].value == "500"


@pytest.mark.parametrize("language", RELEASED_LOCALE_KEYS)
def test_every_released_locale_inherits_and_validates(language: str) -> None:
    base = language.split("_", 1)[0]
    assert normalize_language(language.replace("_", "-")) == language
    assert get_expander(language).entries
    assert len(unit_entries(language)) >= len(unit_entries(base))
    validate_unit_registry(language)
    assert abbr2words("Prof.", lang=language) == abbr2words("Prof.", lang=base)


def test_locale_shared_registry_mutations_do_not_leak_to_base_or_siblings() -> None:
    locale = get_shared_expander("pt_BR", context=False)
    base = get_shared_expander("pt", context=False)
    sibling = get_shared_expander("es_NI", context=False)
    locale.add_abbreviation(AbbreviationEntry("LOCALE.", "locale-only", origin="custom"))

    assert locale.expand("LOCALE.") == "locale-only."
    assert base.expand("LOCALE.") == "LOCALE."
    assert sibling.expand("LOCALE.") == "LOCALE."


@pytest.mark.parametrize("language", MASTER_ONLY_BASE_KEYS)
def test_current_master_only_base_is_conservative_and_unicode_safe(language: str) -> None:
    expander = get_expander(language)
    assert expander.entries
    assert abbr2words("ordinary prose", lang=language) == "ordinary prose"
    validate_unit_registry(language)


@pytest.mark.parametrize("language", MASTER_ONLY_LOCALE_KEYS)
def test_current_master_chinese_locales_are_distinct_inherited_overlays(language: str) -> None:
    base = get_shared_expander("zh")
    locale = get_shared_expander(language)
    assert locale.entries
    assert len(unit_entries(language)) > len(unit_entries("zh"))
    assert {entry.canonical_id for entry in unit_entries(language)} >= {
        entry.canonical_id for entry in unit_entries("zh")
    }
    assert locale.entries.keys() >= base.entries.keys()
    validate_unit_registry(language)
