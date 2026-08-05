from __future__ import annotations

import pytest

from abbr2words import abbr2words, get_shared_expander, reset_expanders


@pytest.fixture(autouse=True)
def reset_shared_registries() -> None:
    reset_expanders()


def test_minimum_and_minute_are_distinct_case_sensitive_entries() -> None:
    expander = get_shared_expander("de")
    minimum = expander.get_abbreviation("min.", case_sensitive=True)
    minute = expander.get_abbreviation("Min.", case_sensitive=True)

    assert minimum is not None
    assert minimum.expansion == "minimal"
    assert minimum.case_sensitive is True
    assert minute is not None
    assert minute.expansion == "Minute"
    assert minute.case_sensitive is True


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("min. 5 Zeichen", "minimal 5 Zeichen"),
        ("Min. Beispiel", "Minute Beispiel"),
        ("MIN. warten", "MIN. warten"),
    ],
)
def test_german_minimum_and_minute_expansion(source: str, expected: str) -> None:
    assert abbr2words(source, lang="de") == expected
