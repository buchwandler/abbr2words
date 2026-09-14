from __future__ import annotations

import pytest

from abbr2words import abbr2words, abbr2words_with_replacements


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("IP-Adresse", "I P Adresse"),
        ("IP", "I P"),
        ("IBAN", "IBAN"),
        ("LTS", "L T S"),
        ("15. Jh.", "15. Jahrhundert."),
    ],
)
def test_german_spokenform_lexical_regressions(source: str, expected: str) -> None:
    assert abbr2words(source, lang="de") == expected


def test_ip_address_is_an_exact_entry_not_a_boundary_relaxation() -> None:
    source = "Die IP-Adresse ist bekannt."
    result = abbr2words_with_replacements(source, lang="de")

    assert result.text == "Die I P Adresse ist bekannt."
    assert len(result.replacements) == 1

    replacement = result.replacements[0]
    assert source[replacement.start : replacement.end] == "IP-Adresse"
    assert replacement.replacement == "I P Adresse"
    assert replacement.rule == "abbr:IP-Adresse"


@pytest.mark.parametrize("source", ["ABC-123", "HH-GT"])
def test_ip_address_registration_does_not_relax_generic_hyphen_boundaries(
    source: str,
) -> None:
    assert abbr2words(source, lang="de") == source
