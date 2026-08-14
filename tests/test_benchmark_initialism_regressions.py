from __future__ import annotations

import pytest

from abbr2words import abbr2words, abbr2words_with_replacements


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("BBC News", "B B C News"),
        ("The US and UK", "The U S and U K"),
        ("ISBN PDF TV", "I S B N P D F T V"),
        ("ABC, CBS, CBC.", "A B C, C B S, C B C."),
        ("NFL NHL MLB IUCN ITV MTV LLC", "N F L N H L M L B I U C N I T V M T V L L C"),
    ],
)
def test_reviewed_english_initialisms_are_owned_by_the_registry(source: str, expected: str) -> None:
    assert abbr2words(source, lang="en") == expected


@pytest.mark.parametrize("language", ["de", "es", "fr", "it"])
def test_reviewed_technical_initialisms_use_source_graphemes(language: str) -> None:
    assert abbr2words("HTML ISO IEC ISBN TV", lang=language) == ("H T M L I S O I E C I S B N T V")


@pytest.mark.parametrize("source", ["NASA", "NATO", "FIFA", "UNESCO", "WORLD", "FIRST"])
def test_lexical_acronyms_and_uppercase_words_are_not_registered(source: str) -> None:
    assert abbr2words(source, lang="en") == source


def test_registered_semantic_and_spell_modes_remain_distinct() -> None:
    assert abbr2words("MIT CEO", lang="en") == (
        "Massachusetts Institute of Technology chief executive officer"
    )
    assert abbr2words("MIT CEO", lang="en", registered_initialism_mode="spell") == ("M I T C E O")


def test_aliases_and_sentence_punctuation_are_source_aligned() -> None:
    assert abbr2words("U.S.A.", lang="en") == "U S A."
    assert abbr2words("USA.", lang="en") == "U S A."
    assert abbr2words("(BBC),", lang="en") == "(B B C),"


def test_reviewed_and_generic_provenance_are_distinct() -> None:
    result = abbr2words_with_replacements(
        "BBC TST E.G.", lang="en", initialism_mode="spell_undotted"
    )
    assert result.text == "B B C T S T E G."
    assert [(item.source, item.rule) for item in result.replacements] == [
        ("abbr:BBC", "abbr:BBC"),
        ("abbr:initialism-undotted", "abbr:initialism-undotted"),
        ("abbr:initialism", "abbr:initialism"),
    ]


def test_default_unknown_uppercase_and_headlines_remain_conservative() -> None:
    source = "ZXQK WORLD FIRST FILM GETS TOP PRIZE AT CANNES"
    assert abbr2words(source, lang="en") == source


@pytest.mark.parametrize("source", ["XIX", "MCMLXXXIX", "ISO-9001", "A-123", "HH-GT"])
def test_roman_numerals_and_identifier_fragments_remain_unchanged(source: str) -> None:
    assert abbr2words(source, lang="en", initialism_mode="spell_undotted") == source
