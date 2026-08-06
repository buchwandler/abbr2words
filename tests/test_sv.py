from __future__ import annotations

from abbr2words import abbr2words, normalize_language


def test_swedish_alias_and_prose_abbreviations() -> None:
    assert normalize_language("swe-SE") == "sv"
    assert abbr2words("t.ex. bl.a. nr 4", lang="sv") == "till exempel bland annat nummer 4"


def test_swedish_minute_and_month_boundaries() -> None:
    assert abbr2words("min bok; mars är kall", lang="sv") == "min bok; mars är kall"
    assert abbr2words("5 min och 2 km", lang="sv") == "5 minut och 2 kilometer"


def test_swedish_units() -> None:
    assert abbr2words("4 m², 3 m3, 20 km/h", lang="sv") == (
        "4 kvadratmeter, 3 kubikmeter, 20 kilometer per timme"
    )
