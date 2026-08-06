from __future__ import annotations

from abbr2words import abbr2words, normalize_language


def test_turkish_alias_and_case_sensitive_entries() -> None:
    assert normalize_language("tur_TR") == "tr"
    assert abbr2words("Prof. Kaya, s. 4", lang="tr") == "profesör Kaya, sayfa 4"
    assert abbr2words("prof. Kaya", lang="tr") == "prof. Kaya"


def test_turkish_unit_suffix_policy_rejects_both_apostrophes() -> None:
    assert abbr2words("5 kg", lang="tr") == "5 kilogram"
    assert abbr2words("5 kg'dan", lang="tr") == "5 kg'dan"
    assert abbr2words("5 kg’dan", lang="tr") == "5 kg’dan"


def test_turkish_units_use_reviewed_lemma_inventory() -> None:
    assert abbr2words("4 m², 3 m3, 20 km/h", lang="tr") == (
        "4 metre kare, 3 metre küp, 20 saatte kilometre"
    )
