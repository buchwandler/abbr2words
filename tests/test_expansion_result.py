from dataclasses import FrozenInstanceError

import pytest

from abbr2words import (
    Expander,
    ExpansionResult,
    abbr2words,
    abbr2words_with_replacements,
    iter_unit_matches,
)


def test_string_api_and_structured_api_remain_available() -> None:
    source = "Prof. Klein"
    result = abbr2words_with_replacements(source, lang="de")

    assert isinstance(abbr2words(source, lang="de"), str)
    assert isinstance(result, ExpansionResult)
    assert result.source_text == source
    assert isinstance(result.replacements, tuple)


def test_replacement_exposes_exact_matched_source_text() -> None:
    source = "Prof. Klein"
    item = abbr2words_with_replacements(source, lang="de").replacements[0]

    assert item.matched_text == "Prof."
    assert item.source_text == "Prof."
    assert item.matched_text == source[item.start : item.end]


def test_unit_replacement_exposes_canonical_identity() -> None:
    source = "500 g"
    result = abbr2words_with_replacements(source, lang="en")
    item = result.replacements[0]
    match = next(iter_unit_matches(source, "en"))

    assert item.kind == "unit"
    assert item.matched_text == source[item.start : item.end]
    assert item.rule_id == "unit:en:mass-gram"
    assert item.canonical_id == "mass-gram"
    assert item.canonical_id == match.canonical_id


def test_rule_id_is_explicit_and_compatible() -> None:
    item = abbr2words_with_replacements("Prof.", lang="de").replacements[0]

    assert item.kind == "abbreviation"
    assert item.abbreviation == "Prof."
    assert item.rule_id == item.rule
    assert item.entry_id == item.rule_id


@pytest.mark.parametrize("source, language", [("Dr. Dr.", "de"), ("Prof. 500 g", "de")])
def test_replacements_are_ordered_non_overlapping_and_reconstruct_result(
    source: str, language: str
) -> None:
    result = abbr2words_with_replacements(source, lang=language)

    assert [item.start for item in result.replacements] == sorted(
        item.start for item in result.replacements
    )
    for left, right in zip(result.replacements, result.replacements[1:], strict=False):
        assert left.end <= right.start
    for item in result.replacements:
        assert 0 <= item.start <= item.end <= len(source)
        assert item.matched_text == source[item.start : item.end]

    rebuilt = source
    for item in reversed(result.replacements):
        rebuilt = rebuilt[: item.start] + item.text + rebuilt[item.end :]
    assert rebuilt == result.text


def test_repeated_abbreviations_keep_distinct_source_spans() -> None:
    source = "Dr. Dr."
    result = abbr2words_with_replacements(source, lang="de")

    assert [(item.start, item.end, item.matched_text) for item in result.replacements] == [
        (0, 3, "Dr."),
        (4, 7, "Dr."),
    ]


def test_unicode_source_offsets_are_python_character_offsets() -> None:
    source = "Ä Prof."
    item = abbr2words_with_replacements(source, lang="de").replacements[0]

    assert item.start == 2
    assert item.end == 7
    assert item.matched_text == "Prof."
    assert item.matched_text == source[item.start : item.end]


def test_protected_spans_remain_authoritative() -> None:
    source = "Prof. Dr."
    result = abbr2words_with_replacements(source, lang="de", protected_spans=[(0, 5)])

    assert all(item.end <= 0 or item.start >= 5 for item in result.replacements)
    assert all(item.matched_text == source[item.start : item.end] for item in result.replacements)
    assert result.text.startswith("Prof.")


def test_unchanged_input_has_no_replacements() -> None:
    result = abbr2words_with_replacements("Klein", lang="de")

    assert result.text == result.source_text == "Klein"
    assert result.replacements == ()


def test_replacement_records_are_immutable() -> None:
    item = abbr2words_with_replacements("Prof.", lang="de").replacements[0]

    with pytest.raises(FrozenInstanceError):
        item.text = "changed"  # type: ignore[misc]


def test_generic_initialism_does_not_leak_rule_name_into_abbreviation() -> None:
    item = abbr2words_with_replacements("E.D.", lang="en").replacements[0]

    assert item.matched_text == "E.D."
    assert item.rule_id == "abbr:initialism"
    assert item.abbreviation is None
    assert item.source == "abbr:initialism"


@pytest.mark.parametrize(
    ("mode", "expected_rule"),
    [
        ("conservative_undotted", "abbr:initialism-conservative"),
        ("spell_undotted", "abbr:initialism-undotted"),
    ],
)
def test_unknown_initialism_fallback_keeps_source_surface_separate(
    mode: str, expected_rule: str
) -> None:
    item = abbr2words_with_replacements(
        "TSK",
        lang="en",
        initialism_mode=mode,  # type: ignore[arg-type]
    ).replacements[0]

    assert item.matched_text == "TSK"
    assert item.rule_id == expected_rule
    assert item.abbreviation is None


def test_alias_keeps_exact_surface_and_canonical_abbreviation_identity() -> None:
    item = abbr2words_with_replacements("z. B.", lang="de").replacements[0]

    assert item.matched_text == "z. B."
    assert item.abbreviation == "z.B."
    assert item.rule_id == "abbr:z.B."


@pytest.mark.parametrize("source", ["2 µg", "2 μg"])
def test_unit_aliases_share_canonical_identity(source: str) -> None:
    item = abbr2words_with_replacements(source, lang="en").replacements[0]

    assert item.kind == "unit"
    assert item.matched_text == source
    assert item.canonical_id == "mass-microgram"


@pytest.mark.parametrize(
    ("language", "source", "canonical_id"),
    [
        ("ja", "5 km", "length-kilometer"),
        ("ko", "5 km", "length-kilometer"),
        ("zh_CN", "5 km", "length-kilometer"),
    ],
)
def test_localized_unit_replacement_keeps_canonical_identity(
    language: str, source: str, canonical_id: str
) -> None:
    item = abbr2words_with_replacements(source, lang=language).replacements[0]

    assert item.language == language
    assert item.matched_text == source
    assert item.canonical_id == canonical_id


def test_custom_unit_replacement_retains_bundled_identity() -> None:
    expander = Expander("en")
    expander.set_unit("kg", "custom kilogram")

    item = expander.expand_with_replacements("2 kg").replacements[0]

    assert item.canonical_id == "mass-kilogram"


def test_custom_unit_without_identity_exposes_none() -> None:
    expander = Expander("en")
    expander.set_unit("zz", "custom z")

    item = expander.expand_with_replacements("2 zz").replacements[0]

    assert item.matched_text == "2 zz"
    assert item.canonical_id is None
