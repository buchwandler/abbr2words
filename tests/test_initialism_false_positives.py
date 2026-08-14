from __future__ import annotations

import pytest

from abbr2words import (
    abbr2words,
    abbr2words_with_replacements,
    iter_initialism_diagnostics,
)


@pytest.mark.parametrize(
    "token",
    [
        "WHY",
        "TRY",
        "FLY",
        "CRY",
        "MY",
        "BY",
        "SMITH",
        "THY",
        "NOT",
        "GYM",
        "LYNX",
        "CRYPT",
        "SYNC",
        "WORLD",
        "FIRST",
        "FINAL",
        "RESULTS",
        "PENDING",
    ],
)
def test_conservative_mode_preserves_ordinary_uppercase_words(token: str) -> None:
    assert abbr2words(token, initialism_mode="conservative_undotted") == token


@pytest.mark.parametrize(
    "source",
    [
        "WHY NOT TRY",
        "FINAL RESULTS PENDING",
        "THE QUICK BROWN FOX",
        "THE QUICK BROWN FOX",
    ],
)
def test_conservative_mode_preserves_uppercase_prose_runs(source: str) -> None:
    assert abbr2words(source, initialism_mode="conservative_undotted") == source


def test_reviewed_honorific_can_expand_without_spelling_the_surname() -> None:
    assert abbr2words("DR SMITH", initialism_mode="conservative_undotted") == "Doctor SMITH"


@pytest.mark.parametrize(
    "token", ["IN", "AS", "AT", "TO", "OR", "NO", "PA", "MD", "DC", "CA", "AA"]
)
def test_unknown_two_letter_forms_are_not_guessed(token: str) -> None:
    assert abbr2words(token, initialism_mode="conservative_undotted") == token


@pytest.mark.parametrize(
    "source",
    [
        "AAPL",
        "NVDA",
        "AMD",
        "ISO-9001",
        "ABC-123",
        "HH-GT",
        "A-123",
        "WH-1000XM4",
        "XIX",
        "MCMLXXXIX",
    ],
)
def test_structured_and_protected_forms_are_not_claimed_by_conservative_fallback(
    source: str,
) -> None:
    assert abbr2words(source, initialism_mode="conservative_undotted") == source


@pytest.mark.parametrize("source", ["NASA", "NATO", "FIFA", "UNESCO"])
def test_lexical_acronyms_remain_lexical(source: str) -> None:
    assert abbr2words(source, initialism_mode="conservative_undotted") == source


def test_lowercase_aliases_are_explicit_and_case_safe() -> None:
    assert abbr2words("html xml xhtml gtk gfdl") == "H T M L X M L X H T M L G T K G F D L"
    assert (
        abbr2words(
            "html XML",
            registered_initialism_mode="spell",
            initialism_case="lower",
        )
        == "h t m l x m l"
    )
    assert abbr2words("us in as at no") == "us in as at no"


@pytest.mark.parametrize(
    ("language", "source", "expected"),
    [
        ("en", "FBI IRS CIA EU GPS", "F B I I R S C I A E U G P S"),
        ("de", "USA WHO CDU ZDF BND", "U S A W H O C D U Z D F B N D"),
        ("es", "UNAM ONU IMSS SRE", "U N A M O N U I M S S S R E"),
        ("fr", "UE PDG OMS SNCF", "U E P D G O M S S N C F"),
        ("it", "USA PIL OMS ADSL", "U S A P I L O M S A D S L"),
    ],
)
def test_reviewed_locale_initialisms_are_registered(
    language: str, source: str, expected: str
) -> None:
    assert abbr2words(source, lang=language) == expected
    rows = list(iter_initialism_diagnostics(source, language=language))
    assert all(row.reason == "registered-semantic" for row in rows)
    assert all(row.registered_entry_id is not None for row in rows)


def test_locale_registry_entries_do_not_leak_between_languages() -> None:
    assert abbr2words("ZDF", lang="de") == "Z D F"
    assert abbr2words("ZDF", lang="en") == "ZDF"
    assert abbr2words("UE", lang="fr") == "U E"
    assert abbr2words("UE", lang="en") == "UE"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("ZDF-Sendung", "Z D F-Sendung"),
        ("BND-Affäre", "B N D-Affäre"),
        ("EU-Richtlinie", "E U-Richtlinie"),
    ],
)
def test_registered_initialisms_expand_in_lexical_hyphen_compounds(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="de") == expected


@pytest.mark.parametrize(
    "source",
    ["ISO-9001", "ABC-123", "KA-T", "HH-GT", "FW-1.2.3", "WH-1000XM4"],
)
def test_code_like_hyphen_compounds_remain_protected(source: str) -> None:
    assert abbr2words(source, lang="de") == source


def test_diagnostics_and_replacements_share_candidates_and_offsets() -> None:
    source = "TST FBI WHY E.D. ISO-9001"
    diagnostics = tuple(
        iter_initialism_diagnostics(source, initialism_mode="conservative_undotted")
    )
    result = abbr2words_with_replacements(source, initialism_mode="conservative_undotted")
    accepted = {(item.start, item.end) for item in diagnostics if item.decision == "accepted"}
    replaced = {(item.start, item.end) for item in result.replacements}
    assert replaced == accepted
    assert all(
        source[item.start : item.end]
        == next(
            row.source_text
            for row in diagnostics
            if row.start == item.start and row.end == item.end
        )
        for item in result.replacements
    )
    assert all(item.reason for item in diagnostics)


@pytest.mark.parametrize("source", ["TST", "BCR", "SSP", "TST FBI", "E.D."])
def test_initialism_processing_is_idempotent(source: str) -> None:
    once = abbr2words(source, initialism_mode="conservative_undotted")
    assert abbr2words(once, initialism_mode="conservative_undotted") == once


def test_protected_span_is_byte_for_byte_unchanged() -> None:
    source = "TST https://ABC.example FBI"
    start = source.index("https://")
    end = start + len("https://ABC.example")
    result = abbr2words_with_replacements(
        source,
        initialism_mode="conservative_undotted",
        protected_spans=[(start, end)],
    )
    assert result.text == "T S T https://ABC.example F B I"
    assert source[start:end] in result.text


@pytest.mark.parametrize("source", ["https://ABC.example", "ABC@example.com"])
def test_caller_protected_spans_cover_structured_text(source: str) -> None:
    assert (
        abbr2words(
            source,
            initialism_mode="conservative_undotted",
            protected_spans=[(0, len(source))],
        )
        == source
    )


@pytest.mark.parametrize("token", ["TST", "BCR", "SSP", "HPRD"])
def test_conservative_unknown_acceptance_is_a_subset_of_broad_mode(token: str) -> None:
    conservative = abbr2words(token, initialism_mode="conservative_undotted")
    broad = abbr2words(token, initialism_mode="spell_undotted")
    assert conservative != token
    assert broad != token
