from __future__ import annotations

from abbr2words import abbr2words, normalize_language


def test_polish_alias_and_guarded_references() -> None:
    assert normalize_language("pol-PL") == "pl"
    assert abbr2words("np. str. 4, godz. 8", lang="pl") == ("na przykład strona 4, godzina 8")


def test_polish_ambiguous_short_forms_are_guarded_or_omitted() -> None:
    assert abbr2words("siostra s. Anna; por. Kowalski", lang="pl") == (
        "siostra s. Anna; por. Kowalski"
    )
    assert abbr2words("2026 r.", lang="pl") == "2026 rok."


def test_polish_units_are_canonical_lemmas() -> None:
    assert abbr2words("4 m², 3 m3, 20 km/h", lang="pl") == (
        "4 metr kwadratowy, 3 metr sześcienny, 20 kilometr na godzinę"
    )
