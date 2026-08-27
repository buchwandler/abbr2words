from __future__ import annotations

import pytest

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


def test_swedish_cirka_standard_and_compatibility_spellings() -> None:
    assert abbr2words("ca 5 km", lang="sv") == "cirka 5 kilometer"
    assert abbr2words("ca. 5 km", lang="sv") == "cirka 5 kilometer"
    assert abbr2words("CA-123", lang="sv") == "CA-123"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("p.g.a. regn", "på grund av regn"),
        ("f.d. chef", "före detta chef"),
        ("m.a.o. klart", "med andra ord klart"),
        ("jfr tabell 2", "jämför tabell 2"),
        ("obs. detta", "observera detta"),
        ("etc. exempel", "etcetera exempel"),
        ("e.d. exempel", "eller dylikt exempel"),
    ],
)
def test_swedish_reviewed_prose_abbreviations(source: str, expected: str) -> None:
    assert abbr2words(source, lang="sv") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("s. 12", "sida 12"),
        ("sid. 12", "sida 12"),
        ("bil. 3", "bilaga 3"),
        ("kap. 4", "kapitel 4"),
        ("fig. 2", "figur 2"),
        ("tab. 7", "tabell 7"),
        ("p. 6", "punkt 6"),
        ("prop. 2025", "proposition 2025"),
        ("dir. 12", "direktiv 12"),
        ("dnr 123", "diarienummer 123"),
        ("bet. 9", "betänkande 9"),
        ("kl. 19.10", "klockan 19.10"),
        ("tfn 08-123", "telefon 08-123"),
        ("tel. 08-123", "telefon 08-123"),
    ],
)
def test_swedish_numeric_reference_abbreviations(source: str, expected: str) -> None:
    assert abbr2words(source, lang="sv") == expected


@pytest.mark.parametrize(
    "source", ("kap. avslutas här", "tab. finns nedan", "dnr saknas", "kl. snart")
)
def test_swedish_numeric_reference_abbreviations_require_numeric_context(source: str) -> None:
    assert abbr2words(source, lang="sv") == source


def test_swedish_initialisms_remain_unchanged() -> None:
    for source in ("EU", "USA", "vd", "mc", "AI"):
        assert abbr2words(source, lang="sv") == source
