from __future__ import annotations

import pytest

from abbr2words import (
    Expander,
    abbr2words,
    abbr2words_with_replacements,
    get_shared_expander,
)


def test_unknown_undotted_initialisms_are_unchanged_by_default() -> None:
    assert abbr2words("BBC News; The UK left the EU.", lang="en") == (
        "BBC News; The UK left the EU."
    )


def test_initialism_compatibility_matrix_keeps_conservative_defaults() -> None:
    assert abbr2words("ABC", lang="en") == "ABC"
    assert (
        abbr2words("ABC", lang="en", initialism_mode="spell_undotted", initialism_case="upper")
        == "A B C"
    )
    assert (
        abbr2words("ABC", lang="en", initialism_mode="spell_undotted", initialism_case="lower")
        == "a b c"
    )
    assert (
        abbr2words(
            "U.S.", lang="en", initialism_case="lower", registered_initialism_mode="spell"
        )
        == "u s."
    )
    assert (
        abbr2words("pp. 12", lang="en", registered_initialism_mode="spell") == "p p 12"
    )


def test_undotted_initialisms_can_be_spelled_in_source_case() -> None:
    assert (
        abbr2words("BBC News Online.", lang="en", initialism_mode="spell_undotted")
        == "B B C News Online."
    )


def test_detection_and_output_case_are_independent() -> None:
    assert (
        abbr2words(
            "BBC PDF",
            lang="en",
            initialism_mode="spell_undotted",
            initialism_case="lower",
        )
        == "b b c p d f"
    )
    assert (
        abbr2words(
            "BBC PDF",
            lang="en",
            initialism_mode="spell_undotted",
            initialism_case="upper",
        )
        == "B B C P D F"
    )


def test_registered_semantic_entries_outrank_generic_fallback() -> None:
    assert abbr2words("MIT CEO", lang="en", initialism_mode="spell_undotted") == (
        "Massachusetts Institute of Technology chief executive officer"
    )


def test_registered_surface_mode_is_explicit_and_metadata_driven() -> None:
    assert abbr2words("MIT CEO D.C.", lang="en") == (
        "Massachusetts Institute of Technology chief executive officer D C."
    )
    assert (
        abbr2words(
            "MIT CEO D.C.", lang="en", registered_initialism_mode="spell", initialism_case="lower"
        )
        == "m i t c e o d c."
    )


def test_protected_spans_skip_the_generic_fallback() -> None:
    source = "BBC News"
    assert (
        abbr2words(
            source,
            lang="en",
            initialism_mode="spell_undotted",
            protected_spans=[(0, 3)],
        )
        == source
    )


@pytest.mark.parametrize(
    "source",
    [
        "XXI MCMXC VI IV",
        "A320 B2B ABC123",
        "FW-1.2.3 WH-1000XM4",
        "fooBBCbar",
    ],
)
def test_roman_like_and_structured_identifiers_are_not_claimed(source: str) -> None:
    assert abbr2words(source, lang="en", initialism_mode="spell_undotted") == source


def test_replacement_offsets_and_provenance_are_source_aligned() -> None:
    source = "See BBC, PDF."
    result = abbr2words_with_replacements(
        source, lang="en", initialism_mode="spell_undotted", initialism_case="lower"
    )
    assert result.text == "See b b c, p d f."
    assert [
        (item.start, item.end, source[item.start : item.end], item.text, item.source, item.entry_id)
        for item in result.replacements
    ] == [
        (4, 7, "BBC", "b b c", "abbr:initialism-undotted", "abbr:initialism-undotted"),
        (9, 12, "PDF", "p d f", "abbr:initialism-undotted", "abbr:initialism-undotted"),
    ]


def test_shared_cache_includes_initialism_policy() -> None:
    default = get_shared_expander("en")
    undotted = get_shared_expander("en", initialism_mode="spell_undotted")
    lower = get_shared_expander("en", initialism_mode="spell_undotted", initialism_case="lower")
    assert default is not undotted
    assert undotted is not lower
    assert default.initialism_policy.mode == "dotted_only"
    assert undotted.initialism_policy.mode == "spell_undotted"
    assert lower.initialism_policy.case == "lower"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"initialism_mode": "invalid"}, "initialism_mode"),
        ({"initialism_case": "invalid"}, "initialism_case"),
        ({"registered_initialism_mode": "invalid"}, "registered_initialism_mode"),
    ],
)
def test_invalid_policies_are_rejected(kwargs: dict[str, str], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        Expander("en", **kwargs)  # type: ignore[arg-type]
