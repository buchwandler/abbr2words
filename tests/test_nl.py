from __future__ import annotations

from abbr2words import abbr2words, normalize_language


def test_dutch_aliases_and_common_abbreviations() -> None:
    assert normalize_language("nld-NL") == "nl"
    assert abbr2words("dhr. Jansen gebruikt bijv. 500 g.", lang="nl") == (
        "de heer Jansen gebruikt bijvoorbeeld 500 gram."
    )


def test_dutch_ambiguous_forms_are_not_added() -> None:
    assert abbr2words("ma is thuis; BV Example; calcium ca", lang="nl") == (
        "ma is thuis; BV Example; calcium ca"
    )


def test_dutch_numeric_units_use_lemma_expansions() -> None:
    assert abbr2words("4 m², 3 m3, 20 km/h", lang="nl") == (
        "4 vierkante meter, 3 kubieke meter, 20 kilometer per uur"
    )
