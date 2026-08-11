from __future__ import annotations

import re

import pytest

from abbr2words import (
    AbbreviationEntry,
    ExpansionVariant,
    ProtectedSpan,
    abbreviation_guards_match,
    get_expander,
    get_shared_expander,
    supported_languages,
)
from abbr2words.units import unit_entries, unit_symbols


def test_every_registry_unit_entry_has_numeric_guard() -> None:
    for language in supported_languages():
        symbols = unit_symbols(language)
        for entry in get_shared_expander(language).entries.values():
            if entry.abbreviation in symbols:
                unit_entry = next(
                    item for item in unit_entries(language) if entry.abbreviation in item.symbols
                )
                if unit_entry.category == "magnitude":
                    continue
                if unit_entry.allow_lexical_overlap:
                    continue
                assert entry.only_if_preceded_by or entry.only_if_followed_by


@pytest.mark.parametrize(
    ("entry", "text", "start", "end", "expected"),
    [
        (
            AbbreviationEntry("in.", "inch", only_if_preceded_by=r"\d\s*$"),
            "10 in. wide",
            3,
            6,
            True,
        ),
        (
            AbbreviationEntry("in.", "inch", only_if_preceded_by=r"\d\s*$"),
            "stand in. line",
            6,
            9,
            False,
        ),
        (
            AbbreviationEntry("Ref.", "Reference", only_if_followed_by=r"\s+\d"),
            "Ref. 8",
            0,
            4,
            True,
        ),
        (
            AbbreviationEntry("Ref.", "Reference", only_if_followed_by=r"\s+\d"),
            "Ref. text",
            0,
            4,
            False,
        ),
    ],
)
def test_guard_matcher_is_fail_closed(
    entry: AbbreviationEntry,
    text: str,
    start: int,
    end: int,
    expected: bool,
) -> None:
    assert abbreviation_guards_match(entry, text, start, end) is expected


def test_guard_matcher_rejects_invalid_offsets() -> None:
    entry = AbbreviationEntry("No.", "Number")
    assert not abbreviation_guards_match(entry, "No.", -1, 3)
    assert not abbreviation_guards_match(entry, "No.", 0, 4)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("S. 12", "Seite 12"),
        ("Siehe S. 12", "Siehe Seite 12"),
        ("S. Beispiel", "S. Beispiel"),
    ],
)
def test_anchored_followed_by_guard_is_relative_to_candidate(source: str, expected: str) -> None:
    assert get_shared_expander("de").expand(source) == expected


@pytest.mark.parametrize(
    ("pattern", "text", "expected"),
    [
        (r"^\s*\d", "Ref. 8", True),
        (re.compile(r"^\s*\d"), "prefix Ref.\t8", True),
        (r"^\d", "Ref.8", True),
        (r"^$", "Ref.", True),
        (r"^\n\d", "Ref.\n8", True),
        (r"^\s*(?!x)\w", "Ref. text", True),
        (r"^\s*(?!x)\w", "Ref. x", False),
        (r"\s+\d", "Ref. 8", True),
        (r"\d", "Ref. text 8", False),
    ],
)
def test_followed_by_patterns_match_the_candidate_suffix(
    pattern: str | re.Pattern[str], text: str, expected: bool
) -> None:
    entry = AbbreviationEntry("Ref.", "Reference", only_if_followed_by=pattern)
    start = text.index("Ref.")
    assert abbreviation_guards_match(entry, text, start, start + len("Ref.")) is expected


def test_preceded_by_negative_lookbehind_remains_bounded_and_relative() -> None:
    entry = AbbreviationEntry("Ref.", "Reference", only_if_preceded_by=r"(?<!x)foo$")
    assert abbreviation_guards_match(entry, "foo Ref.", 4, 8)
    assert not abbreviation_guards_match(entry, "xfoo Ref.", 7, 11)


def test_ordered_variants_use_original_source_and_fall_back_to_default() -> None:
    expander = get_expander("en")
    expander.add_abbreviation(
        AbbreviationEntry(
            "Prof.",
            "Professor",
            variants=(
                ExpansionVariant("professor emerita", only_if_preceded_by=r"La\s+$"),
                ExpansionVariant("professor", only_if_followed_by=r"\s+\w+"),
            ),
        )
    )

    assert expander.expand("La Prof. García") == "La professor emerita García"
    assert expander.expand("Prof. Smith") == "professor Smith"
    assert expander.expand("Prof.") == "Professor."


def test_variant_aliases_and_protected_spans_preserve_exact_source_ranges() -> None:
    expander = get_expander("en")
    expander.add_abbreviation(
        AbbreviationEntry(
            "Ref.",
            "Reference",
            aliases=("Reference.",),
            variants=(ExpansionVariant("referee", only_if_followed_by=r"\s+\d"),),
        )
    )

    result = expander.expand_with_replacements("Reference. 8 Ref. 9")
    assert result.text == "referee 8 referee 9"
    assert [(item.start, item.end, item.source) for item in result.replacements] == [
        (0, 10, "abbr:Ref."),
        (13, 17, "abbr:Ref."),
    ]
    assert expander.expand("Reference. 8 Ref. 9", protected_spans=(ProtectedSpan(0, 10),)) == (
        "Reference. 8 referee 9"
    )


def test_variant_validation_is_eager_and_pos_guards_follow_entry_policy() -> None:
    with pytest.raises(ValueError, match="only_if_followed_by"):
        ExpansionVariant("x", only_if_followed_by="[")

    expander = get_expander("en")
    expander.add_abbreviation(
        AbbreviationEntry(
            "Ref.",
            "Reference",
            variants=(ExpansionVariant("referee", only_if_pos="NOUN", not_if_pos="PROPN"),),
        )
    )
    assert expander.expand("Ref.") == "referee."
