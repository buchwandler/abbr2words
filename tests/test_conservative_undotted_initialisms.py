from __future__ import annotations

from itertools import product

import pytest

from abbr2words import (
    abbr2words,
    abbr2words_with_replacements,
    iter_initialism_diagnostics,
)
from scripts.check_benchmark_freshness import FreshnessError, validate_metadata


@pytest.mark.parametrize("token", ["SSP", "PTM", "HPRD", "BCR", "TST"])
def test_conservative_mode_spells_high_confidence_unknowns(token: str) -> None:
    assert abbr2words(token, initialism_mode="conservative_undotted") == " ".join(token)


@pytest.mark.parametrize(
    "source",
    [
        "WORLD FIRST FILM GETS TOP PRIZE AT CANNES",
        "THE QUICK BROWN FOX",
        "NASA NATO FIFA UNESCO",
        "IV VI XIX MCMLXXXIX",
        "ISO-9001 A-123 ABC123 A320 FW-1.2.3 WH-1000XM4",
        "AAPL NVDA AMD",
        "Lviv Aceh Mpa Enn PlayStation",
        "IN AS AT TO OR NO",
    ],
)
def test_conservative_mode_preserves_safety_cases(source: str) -> None:
    assert abbr2words(source, initialism_mode="conservative_undotted") == source


def test_conservative_mode_keeps_registered_precedence_and_speech_policy() -> None:
    assert abbr2words("BBC TST", initialism_mode="conservative_undotted") == "B B C T S T"
    assert abbr2words("MIT CEO", initialism_mode="conservative_undotted") == (
        "Massachusetts Institute of Technology chief executive officer"
    )


def test_protected_spans_and_url_like_text_are_absolute() -> None:
    source = "See TST at https://ABC.example"
    protected_start = source.index("https://")
    protected_end = len(source)
    assert (
        abbr2words(
            source,
            initialism_mode="conservative_undotted",
            protected_spans=[(protected_start, protected_end)],
        )
        == "See T S T at https://ABC.example"
    )


def test_conservative_replacements_are_source_aligned_and_named() -> None:
    source = "TST FBI"
    result = abbr2words_with_replacements(
        source,
        initialism_mode="conservative_undotted",
        initialism_case="lower",
    )
    assert result.text == "t s t F B I"
    assert [
        (item.start, item.end, source[item.start : item.end], item.source, item.rule)
        for item in result.replacements
    ] == [
        (0, 3, "TST", "abbr:initialism-conservative", "abbr:initialism-conservative"),
        (4, 7, "FBI", "abbr:FBI", "abbr:FBI"),
    ]


@pytest.mark.parametrize("token", ["SSP", "PTM", "HPRD", "BCR", "TST"])
def test_conservative_mode_is_idempotent_for_accepted_tokens(token: str) -> None:
    once = abbr2words(token, initialism_mode="conservative_undotted")
    assert abbr2words(once, initialism_mode="conservative_undotted") == once


def test_diagnostics_expose_reason_codes_and_registered_identity() -> None:
    source = "BBC TST ISO-9001 XIX NASA IN E.D."
    rows = list(
        iter_initialism_diagnostics(
            source,
            initialism_mode="conservative_undotted",
        )
    )
    by_source = {row.source_text: row for row in rows}
    assert by_source["BBC"].reason == "registered-semantic"
    assert by_source["BBC"].registered_entry_id == "abbr:BBC"
    assert by_source["TST"].reason == "conservative-unknown"
    assert by_source["ISO-9001"].reason == "structured-candidate"
    assert by_source["XIX"].reason == "roman-like"
    assert by_source["NASA"].reason == "lexical-acronym"
    assert by_source["IN"].reason == "ambiguous-uppercase-word"
    assert by_source["E.D."].reason == "dotted-initialism"
    assert by_source["E.D."].start == source.index("E.D.")
    assert by_source["E.D."].end == by_source["E.D."].start + len("E.D.")


def test_diagnostics_report_protection_and_structured_candidates() -> None:
    source = "TST AAPL https://ABC.example"
    url_start = source.index("https://")
    rows = list(
        iter_initialism_diagnostics(
            source,
            initialism_mode="conservative_undotted",
            protected_spans=[(url_start, len(source))],
        )
    )
    by_source = {row.source_text: row for row in rows}
    assert by_source["TST"].decision == "accepted"
    assert by_source["AAPL"].reason == "structured-candidate"
    assert by_source["ABC"].decision == "preserved"
    assert by_source["ABC"].reason == "protected-span"


def test_unicode_neighbors_do_not_extend_or_throw() -> None:
    assert abbr2words("éNGOé", initialism_mode="conservative_undotted") == "éNGOé"
    assert abbr2words("Ω TST Ω", initialism_mode="conservative_undotted") == "Ω T S T Ω"


def test_conservative_acceptance_is_a_subset_of_broad_acceptance() -> None:
    samples = [
        "".join(chars) for length in range(2, 5) for chars in product("ABCFGNOPSTVX", repeat=length)
    ][:400]
    for source in samples:
        conservative = abbr2words(source, initialism_mode="conservative_undotted")
        broad = abbr2words(source, initialism_mode="spell_undotted")
        if conservative != source:
            assert broad != source


def test_candidate_boundaries_and_identifier_neighbors_are_deterministic() -> None:
    samples = (
        "A",
        "AB",
        "ABC",
        "ABCD",
        "ABC1",
        "A-123",
        "(NGO)",
        "NGO.",
        "x NGO y",
        "fooBBCbar",
    )
    first = [
        tuple(iter_initialism_diagnostics(sample, initialism_mode="conservative_undotted"))
        for sample in samples
    ]
    second = [
        tuple(iter_initialism_diagnostics(sample, initialism_mode="conservative_undotted"))
        for sample in samples
    ]
    assert first == second


def test_benchmark_freshness_requires_reproducible_metadata() -> None:
    report = {
        "metadata": {
            "abbr2words_version": "0.2.7",
            "spokenform_version": "1.4.0",
            "abbr2words_source_commit": "a" * 40,
            "spokenform_source_commit": "b" * 40,
            "dataset_commit": "c" * 40,
            "benchmark_profile": "proteno-en",
            "normalization_options": {"initialism_mode": "conservative_undotted"},
        }
    }
    metadata = validate_metadata(
        report,
        expected_abbr2words_version="0.2.7",
        expected_abbr2words_source_commit="a" * 40,
    )
    assert metadata["benchmark_profile"] == "proteno-en"

    with pytest.raises(FreshnessError, match="spokenform_source_commit mismatch"):
        validate_metadata(report, expected_spokenform_source_commit="d" * 40)

    incomplete = dict(report["metadata"])
    del incomplete["dataset_commit"]
    with pytest.raises(FreshnessError, match="dataset_commit"):
        validate_metadata(incomplete)
