from __future__ import annotations

import pytest

from abbr2words import abbr2words, get_expander


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Le Bd. Voltaire", "Le boulevard Voltaire"),
        ("Le bd Voltaire", "Le boulevard Voltaire"),
        ("Le Bd.", "Le boulevard."),
        ("bdVoltaire", "bdVoltaire"),
    ],
)
def test_french_boulevard_forms_consume_dotted_spelling_safely(source: str, expected: str) -> None:
    assert abbr2words(source, lang="fr") == expected


def test_italian_reviewed_titles_and_organization_entries() -> None:
    assert abbr2words("La Rag. Viola", lang="it") == "La ragioniera Viola"
    assert abbr2words("Rag. Rossi", lang="it") == "Ragioniere Rossi"
    assert (
        abbr2words("La Onlus Solidarietà", lang="it")
        == "La organizzazione non lucrativa di utilità sociale Solidarietà"
    )
    assert abbr2words("Il Dott. Mag. Bianchi", lang="it") == "Il dottor magistrato Bianchi"
    assert abbr2words("5 mag. 2024", lang="it") == "5 maggio 2024"
    assert abbr2words("L'Ing. Verdi", lang="it") == "L'ingegnere Verdi"
    assert abbr2words("Il Prof. Emerito", lang="it") == "Il professore Emerito"


def test_spanish_professor_variant_is_local_and_parentheticals_survive() -> None:
    assert abbr2words("La Prof. García (fábrica)", lang="es") == ("La profesora García (fábrica)")
    assert abbr2words("El Prof. García", lang="es") == "El profesor García"
    assert abbr2words("Prof. García", lang="es") == "Profesor García"
    assert abbr2words("Ej. 4", lang="es") == "Ejemplo 4"


@pytest.mark.parametrize(
    ("source", "expected", "language"),
    [
        ("Av. Reforma", "Avenida Reforma", "es"),
        ("Vivo en Av. Reforma", "Vivo en avenida Reforma", "es"),
        ("Vol. 2", "Volumen 2", "es"),
        ("véase vol. 2", "véase volumen 2", "es"),
        ("Cap. 10", "Capítulo 10", "es"),
        ("véase cap. 10", "véase capítulo 10", "es"),
        ("Avv. Rossi", "Avvocato Rossi", "it"),
        ("con l'Avv. Rossi", "con l'avvocato Rossi", "it"),
        ("Arch. Rossi", "Architetto Rossi", "it"),
        ("con l'Arch. Rossi", "con l'architetto Rossi", "it"),
        ("rue St. Michel", "rue Saint Michel", "fr"),
        ("rue Ste. Anne", "rue Sainte Anne", "fr"),
    ],
)
def test_reviewed_sentence_and_proper_name_casing(
    source: str, expected: str, language: str
) -> None:
    assert abbr2words(source, lang=language) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Ej. 5 resuelto.", "Ejercicio 5 resuelto."),
        ("véase ej. 5 resuelto", "véase ejercicio 5 resuelto"),
        ("véase ej. 5", "véase ejemplo 5"),
        ("p.ej. 5", "por ejemplo 5"),
        ("p.ej. 5 resuelto", "por ejemplo 5 resuelto"),
    ],
)
def test_spanish_ejercicio_variant_is_narrow_and_longest_match_wins(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="es") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Die max. Teilnehmerzahl", "Die maximale Teilnehmerzahl"),
        ("Die evtl. Verspätung", "Die eventuelle Verspätung"),
        ("max. 5 Teilnehmer", "maximal 5 Teilnehmer"),
        ("ggf. maximal", "gegebenenfalls maximal"),
    ],
)
def test_german_attributive_variants_are_conservative(source: str, expected: str) -> None:
    assert abbr2words(source, lang="de") == expected


def test_existing_german_longest_and_gmbh_policies_remain_stable() -> None:
    expander = get_expander("de")
    assert expander.expand("Dipl.-Ing. Weber") == "Diplom Ingenieur Weber"
    assert expander.expand("GmbH") == "Geh Em Beh Hah"


@pytest.mark.parametrize(
    "source",
    ["E. coli", "E. faecalis", "N. meningitidis", "S. aureus"],
)
def test_english_directional_initials_do_not_rewrite_biological_names(source: str) -> None:
    assert abbr2words(source, lang="en") == source


@pytest.mark.parametrize("source", ["Brown v. Board", "A v. B"])
def test_english_lowercase_versus_abbreviation_remains_supported(source: str) -> None:
    assert abbr2words(source, lang="en") == source.replace(" v. ", " versus ")


@pytest.mark.parametrize("source", ["I-IV-V.", "Chapter V.", "V. Allegro"])
def test_english_uppercase_roman_or_musical_v_is_not_versus(source: str) -> None:
    assert abbr2words(source, lang="en") == source


@pytest.mark.parametrize("source", ["n. 10", "n. 25"])
def test_italian_number_marker_requires_numeric_following_context(source: str) -> None:
    assert abbr2words(source, lang="it") == source.replace("n.", "numero")


@pytest.mark.parametrize(
    ("source", "expected"),
    [("20 N.", "20 N."), ("30 N", "30 newton"), ("N. meningitidis", "N. meningitidis")],
)
def test_italian_number_marker_does_not_steal_units_or_biological_initials(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="it") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Main St.", "Main Street."),
        ("Dec.", "December."),
        ('Dr."', 'Doctor."'),
        ("Dr.)", "Doctor.)"),
        ("Co.,", "company,"),
        ("Inc.;", "incorporated;"),
        ("St. Martin", "Saint Martin"),
    ],
)
def test_dotted_abbreviations_preserve_only_sentence_final_period(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="en") == expected


def test_french_honorific_preserves_period_before_closing_quote() -> None:
    assert abbr2words('M."', lang="fr") == 'Monsieur."'
