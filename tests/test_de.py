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
        ("Min. Beispiel", "Min. Beispiel"),
        ("MIN. warten", "MIN. warten"),
    ],
)
def test_german_minimum_and_minute_expansion(source: str, expected: str) -> None:
    assert abbr2words(source, lang="de") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Lfd. Nr.", "laufende Nummer."),
        ("Lfd.Nr.", "laufende Nummer."),
        ("z.B.", "zum Beispiel."),
        ("z. B.", "zum Beispiel."),
        ("z . b .", "zum Beispiel."),
        ("zB", "zum Beispiel"),
        ("d.h.", "das heißt."),
        ("d. h.", "das heißt."),
        ("u.a.", "unter anderem."),
        ("u. a.", "unter anderem."),
    ],
)
def test_german_compound_aliases(source: str, expected: str) -> None:
    assert abbr2words(source, lang="de") == expected


@pytest.mark.parametrize("source", ["pizzaB", "ModellzB12", "du.a.test"])
def test_german_compound_aliases_preserve_word_boundaries(source: str) -> None:
    assert abbr2words(source, lang="de") == source


def test_german_compound_aliases_work_at_punctuation_and_sentence_boundaries() -> None:
    source = '(z.B.), "d. h."; u. a.! Lfd.Nr.'
    assert abbr2words(source, lang="de") == (
        '(zum Beispiel), "das heißt"; unter anderem! laufende Nummer.'
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Abschn. 2", "Abschnitt 2"),
        ("Univ. Berlin", "Universität Berlin"),
        ("Fa. Müller", "Firma Müller"),
        ("Dipl.-Kfm. Weber", "Diplom-Kaufmann Weber"),
        ("Tab. 3", "Tabelle 3"),
        ("Tel. Nr. 12", "Telefonnummer 12"),
        ("Tel.Nr. 12", "Telefonnummer 12"),
        ("Tel.-Nr. 12", "Telefonnummer 12"),
    ],
)
def test_german_high_confidence_entries_and_compounds(source: str, expected: str) -> None:
    assert abbr2words(source, lang="de") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("gem. 12 BGB", "gemäß 12 BGB"),
        ("Abt. 3", "Abteilung 3"),
        ("(gem.; Abt.)", "(gemäß; Abteilung.)"),
        ("GEM. und ABT.", "gemäß und Abteilung."),
    ],
)
def test_german_reviewed_ordinary_abbreviations_expand_with_case_and_punctuation(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="de") == expected


@pytest.mark.parametrize(
    "source",
    [
        "angem.",
        "gemäß",
        "Gemäß",
        "Abteilung",
        "Abteilung.",
        "xAbt.",
        "AbtX",
    ],
)
def test_german_reviewed_ordinary_abbreviations_preserve_non_abbreviations(source: str) -> None:
    assert abbr2words(source, lang="de") == source


def test_german_reviewed_ordinary_abbreviations_are_registered_once() -> None:
    expander = get_shared_expander("de")
    gem = expander.get_abbreviation("gem.")
    abt = expander.get_abbreviation("Abt.")
    absatz = expander.get_abbreviation("Abs.")

    assert gem is not None
    assert gem.expansion == "gemäß"
    assert abt is not None
    assert abt.expansion == "Abteilung"
    assert absatz is not None
    assert sum(entry.abbreviation == "gem." for entry in expander.entries.values()) == 1
    assert sum(entry.abbreviation == "Abt." for entry in expander.entries.values()) == 1


def test_german_st_is_guarded_by_name_context() -> None:
    assert abbr2words("St. Pauli", lang="de") == "Sankt Pauli"
    assert abbr2words("St. ist eine Abkürzung", lang="de") == "St. ist eine Abkürzung"
