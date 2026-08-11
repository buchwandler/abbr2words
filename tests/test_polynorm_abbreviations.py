from __future__ import annotations

import pytest

from abbr2words import abbr2words, get_expander


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Le Bd. Voltaire", "Le boulevard Voltaire"),
        ("Le bd Voltaire", "Le boulevard Voltaire"),
        ("Le Bd.", "Le boulevard"),
        ("bdVoltaire", "bdVoltaire"),
    ],
)
def test_french_boulevard_forms_consume_dotted_spelling_safely(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="fr") == expected


def test_italian_reviewed_titles_and_organization_entries() -> None:
    assert abbr2words("La Rag. Viola", lang="it") == "La Ragioniere Viola"
    assert (
        abbr2words("La Onlus Solidarietà", lang="it")
        == "La organizzazione non lucrativa di utilità sociale Solidarietà"
    )
    assert abbr2words("Il Dott. Mag. Bianchi", lang="it") == "Il Dottor Magistrato Bianchi"
    assert abbr2words("5 mag. 2024", lang="it") == "5 maggio 2024"
    assert abbr2words("L'Ing. Verdi", lang="it") == "L'Ingegnere Verdi"
    assert abbr2words("Il Prof. Emerito", lang="it") == "Il Professore Emerito"


def test_spanish_professor_variant_is_local_and_parentheticals_survive() -> None:
    assert abbr2words("La Prof. García (fábrica)", lang="es") == (
        "La Profesora García (fábrica)"
    )
    assert abbr2words("El Prof. García", lang="es") == "El Profesor García"
    assert abbr2words("Prof. García", lang="es") == "Profesor García"
    assert abbr2words("Ej. 4", lang="es") == "ejemplo 4"


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
