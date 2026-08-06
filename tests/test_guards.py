from __future__ import annotations

import pytest

from abbr2words import (
    AbbreviationEntry,
    abbreviation_guards_match,
    get_shared_expander,
    supported_languages,
)
from abbr2words.units import unit_symbols


def test_every_registry_unit_entry_has_numeric_guard() -> None:
    for language in supported_languages():
        symbols = unit_symbols(language)
        for entry in get_shared_expander(language).entries.values():
            if entry.abbreviation in symbols:
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
