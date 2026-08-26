from dataclasses import FrozenInstanceError

import pytest

from abbr2words import ExpansionResult, abbr2words, abbr2words_with_replacements, iter_unit_matches


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
