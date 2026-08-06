from __future__ import annotations

from time import perf_counter

import pytest

from abbr2words import (
    AbbreviationEntry,
    Expander,
    ProtectedSpan,
    abbr2words,
    get_expander,
    supported_languages,
)
from abbr2words.units import UnitEntry, validate_unit_registry


@pytest.mark.parametrize(
    ("lang", "source", "expected"),
    [
        ("es", "C/ Mayor", "Calle Mayor"),
        ("es", "N° 5", "número 5"),
        ("fr", "N° 5", "numéro 5"),
        ("it", "n° 5", "numero 5"),
    ],
)
def test_punctuation_ending_builtins_use_symmetric_boundaries(lang: str, source: str, expected: str):
    assert abbr2words(source, lang=lang) == expected


@pytest.mark.parametrize("abbreviation", ["(R)", "C++", ".NET", "#1"])
def test_custom_punctuation_spellings_and_word_attachment(abbreviation: str):
    expander = Expander("en")
    expander.add(abbreviation, "CUSTOM", case_sensitive=True)
    assert "CUSTOM" in expander(f"Use {abbreviation} now.")
    assert expander(f"x{abbreviation}") == f"x{abbreviation}"
    assert expander(f"{abbreviation}x") == f"{abbreviation}x"


def test_initialism_period_guard_allows_ellipsis_but_preserves_embedded_initialisms():
    assert abbr2words("A.B.S.", lang="en") == "A.B.S."
    assert abbr2words("Hello.Dr.", lang="en") == "Hello.Dr."
    assert abbr2words("...Dr. Smith", lang="en") == "...Doctor Smith"
    assert abbr2words(".Dr. Smith", lang="en") == ".Doctor Smith"


@pytest.mark.parametrize(
    "source",
    ["5 km / h", "1 m^2", "2kg-rated", "5 km/hx", "5 kg*m", "5 kg·m", "5 in.x"],
)
def test_unsupported_unit_expressions_fail_closed(source: str):
    assert abbr2words(source, lang="en") == source


def test_unicode_micro_alias_and_complete_units():
    assert abbr2words("37 µg", lang="en") == "37 microgram"
    assert abbr2words("37 μg", lang="en") == "37 microgram"
    assert abbr2words("5 km/h", lang="en") == "5 kilometer per hour"


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda: AbbreviationEntry("", "x"), "abbreviation"),
        (lambda: AbbreviationEntry(" Dr.", "x"), "whitespace"),
        (lambda: AbbreviationEntry("Dr.", 3), "expansion"),
        (lambda: AbbreviationEntry("Dr.", ""), "expansion"),
        (lambda: AbbreviationEntry("Dr.", "x", case_sensitive=1), "case_sensitive"),
        (lambda: AbbreviationEntry("Dr.", "x", only_if_preceded_by="("), "regular expression"),
        (lambda: AbbreviationEntry("Dr.", "x", context_expansions={}), "context_expansions"),
        (lambda: AbbreviationEntry("Dr.", "x", context_expansions={"title": "x"}), "keys"),
    ],
)
def test_custom_entry_validation_is_eager(factory, message: str):
    with pytest.raises((TypeError, ValueError), match=message):
        factory()


def test_custom_context_validation_and_default_fallback_are_deterministic():
    expander = Expander("en")
    with pytest.raises(ValueError, match="Unknown context"):
        expander.add("X.", {"unknown": "x"})
    expander.add("X.", {"title": "Title"})
    assert expander.has("X.")


def test_preceding_guard_is_immediate_not_an_unrestricted_window_search():
    expander = Expander("en", context=False)
    expander.add("ZZ.", "z", only_if_preceded_by="foo")
    assert expander("foo ZZ.") == "foo z"
    assert expander("foo long gap ZZ.") == "foo long gap ZZ."
    assert expander("x foo y ZZ.") == "x foo y ZZ."


def test_exact_custom_override_beats_case_insensitive_fallback():
    expander = Expander("en")
    expander.add("Dr.", "CUSTOM", case_sensitive=True)
    assert expander("Dr. Smith") == "CUSTOM Smith"
    assert expander("dr. Smith") == "Doctor Smith"


def test_unit_customization_is_truthful_and_instance_local():
    first = Expander("en")
    second = Expander("en")
    with pytest.raises(ValueError, match="set_unit"):
        first.add("kg", "custom")
    first.set_unit("kg", "custom kilogram")
    assert first("2 kg") == "2 custom kilogram"
    assert second("2 kg") == "2 kilogram"
    assert first.remove_unit("kg")
    assert first("2 kg") == "2 kg"


def test_trace_is_source_aligned_reconstructible_and_protected():
    source = "Dr. Smith; 2 kg; https://example.com/dr."
    start = source.index("https://")
    end = len(source)
    result = get_expander("en").expand_with_trace(
        source, protected_spans=[ProtectedSpan(start, end, "url")]
    )
    assert result.text == "Doctor Smith; 2 kilogram; https://example.com/dr."
    assert all(source[item.start : item.end] == item.source_text for item in result.matches)
    rebuilt = source
    for item in reversed(result.matches):
        rebuilt = rebuilt[: item.start] + item.replacement + rebuilt[item.end :]
    assert rebuilt == result.text
    assert [item.kind for item in result.matches] == ["abbreviation", "unit"]


def test_unicode_context_profiles_disambiguate_names_and_addresses():
    assert abbr2words("Fr. Müller kommt.", lang="de") == "Frau Müller kommt."
    assert abbr2words("Fr. Élodie kommt.", lang="de") == "Frau Élodie kommt."
    assert abbr2words("Fr. O'Neil kommt.", lang="de") == "Frau O'Neil kommt."
    assert abbr2words("Main St. is closed.", lang="en") == "Main Street is closed."
    assert abbr2words("Oak Dr. is nearby.", lang="en") == "Oak Drive is nearby."


def test_registry_invariants_and_casing_audit():
    for language in supported_languages():
        validate_unit_registry(language)
        for entry in get_expander(language).entries.values():
            if entry.abbreviation.isupper() and sum(char.isalpha() for char in entry.abbreviation) >= 2:
                assert entry.case_sensitive or "." in entry.abbreviation


def test_idempotence_on_a_deterministic_unicode_matrix():
    samples = [
        "Dr. Müller",
        "...Dr. Smith",
        "37 μg",
        "5 km/h",
        "N° 5",
        "Cafe\u0301 C++ 😀",
        "Пр. тест",
    ]
    for language in supported_languages():
        for sample in samples:
            expanded = abbr2words(sample, lang=language)
            assert abbr2words(expanded, lang=language) == expanded


def test_dense_matches_scale_without_quadratic_resolver_growth():
    expander = get_expander("en")
    measurements = []
    for count in (1000, 2000):
        source = " ".join(["Dr."] * count)
        started = perf_counter()
        assert expander.expand(source).count("Doctor") == count
        measurements.append(perf_counter() - started)
    assert measurements[1] < max(measurements[0] * 3.5, 0.25)


def test_unit_metadata_is_validated():
    with pytest.raises(ValueError, match="canonical_symbol"):
        UnitEntry(("kg",), "kilogram", canonical_symbol="g")
    with pytest.raises(TypeError, match="requires_numeric_value"):
        UnitEntry(("kg",), "kilogram", requires_numeric_value=1)
