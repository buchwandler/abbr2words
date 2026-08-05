from __future__ import annotations

import pytest

from abbr2words import abbr2words, reset_expanders


@pytest.fixture(autouse=True)
def reset_shared_registries() -> None:
    reset_expanders()


@pytest.mark.parametrize(
    ("source", "lang", "expected"),
    [
        ("(Dr.) Smith", "en", "(Doctor) Smith"),
        ('He said "etc."', "en", 'He said "et cetera"'),
        ("(Prof.) Klein", "de", "(Professor) Klein"),
        ('Er sagte "ggf."', "de", 'Er sagte "gegebenenfalls"'),
        ("Prof.–Klein", "de", "Professor–Klein"),
    ],
)
def test_dotted_abbreviations_accept_non_word_delimiters(
    source: str, lang: str, expected: str
) -> None:
    assert abbr2words(source, lang=lang) == expected


@pytest.mark.parametrize("lang", ["en", "de"])
def test_dotted_abbreviations_reject_attached_words(lang: str) -> None:
    assert abbr2words("Dr.foo", lang=lang) == "Dr.foo"

