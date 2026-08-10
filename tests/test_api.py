from __future__ import annotations

import pytest

from abbr2words import Expander, __version__, abbr2words, reset_expanders, supported_languages
from abbr2words.__about__ import __version__ as fallback_version


@pytest.fixture(autouse=True)
def reset_shared_registries() -> None:
    reset_expanders()


def test_source_fallback_version_is_neutral() -> None:
    assert fallback_version == "0+unknown"
    assert fallback_version != "0.2.3"
    assert __version__


def test_supported_languages() -> None:
    assert supported_languages() == (
        "cs",
        "de",
        "en",
        "es",
        "fr",
        "it",
        "nl",
        "pl",
        "pt",
        "ru",
        "sv",
        "tr",
    )


def test_german_expansion() -> None:
    assert (
        abbr2words("Prof. Klein kommt ggf. für ca. 1 Min.", lang="de")
        == "Professor Klein kommt gegebenenfalls für zirka 1 Minute"
    )


def test_locale_alias() -> None:
    assert abbr2words("Prof. Klein", lang="de-DE") == "Professor Klein"


def test_german_context_for_fr() -> None:
    assert abbr2words("Fr. Klein", lang="de") == "Frau Klein"
    assert abbr2words("am Fr.", lang="de") == "am Freitag"


def test_context_mode_is_respected_independent_of_call_order() -> None:
    assert abbr2words("Fr. Klein", lang="de", context=True) == "Frau Klein"
    assert abbr2words("Fr. Klein", lang="de", context=False) == "Freitag Klein"

    reset_expanders("de")

    assert abbr2words("Fr. Klein", lang="de", context=False) == "Freitag Klein"
    assert abbr2words("Fr. Klein", lang="de", context=True) == "Frau Klein"


def test_english_guard_does_not_expand_sentence_final_in() -> None:
    assert abbr2words("They wandered around in.", lang="en") == "They wandered around in."
    assert abbr2words("The board is 10 in. wide.", lang="en") == "The board is 10 inch wide."


def test_isolated_custom_expander() -> None:
    expander = Expander("de")
    expander.add("KI", "Künstliche Intelligenz", case_sensitive=True)
    assert expander("KI hilft.") == "Künstliche Intelligenz hilft."
    assert abbr2words("KI hilft.", lang="de") == "KI hilft."


def test_context_can_be_disabled() -> None:
    assert abbr2words("Fr. Klein", lang="de", context=False) == "Freitag Klein"


def test_invalid_language() -> None:
    with pytest.raises(ValueError, match="Unsupported language"):
        abbr2words("Dr. Test", lang="xx")


def test_non_string_rejected() -> None:
    with pytest.raises(TypeError, match="text must be a string"):
        abbr2words(123, lang="de")  # type: ignore[arg-type]
