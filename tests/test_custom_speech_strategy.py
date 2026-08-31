from __future__ import annotations

import pytest

from abbr2words import (
    AbbreviationEntry,
    TokenAnnotation,
    get_expander,
)


def test_mixed_custom_speech_strategies() -> None:
    expander = get_expander("en", registered_initialism_mode="spell")
    expander.add("AAR", "after-action review")
    expander.add("AO", "area of operations", speech_strategy="spell_source")
    expander.add(
        "AAA",
        "anti-aircraft artillery",
        speech_strategy="custom",
        spoken_form="Triple A",
    )

    assert expander.expand("AAR AO AAA") == "after-action review A O Triple A"


def test_custom_spoken_form_preserves_semantic_expansion_and_is_exact() -> None:
    entry = AbbreviationEntry(
        "AAA",
        "anti-aircraft artillery",
        speech_strategy="custom",
        spoken_form="Triple A",
    )

    assert entry.expansion == "anti-aircraft artillery"
    assert entry.spoken_form == "Triple A"


def test_custom_spoken_form_does_not_depend_on_registered_spell_mode() -> None:
    expander = get_expander("en", registered_initialism_mode="expand")
    expander.add("AAA", "anti-aircraft artillery", speech_strategy="custom", spoken_form="Triple A")

    assert expander.expand("AAA") == "Triple A"


@pytest.mark.parametrize("speech_strategy", ["expand", "spell_source"])
def test_spoken_form_is_rejected_for_non_custom_strategy(speech_strategy: str) -> None:
    with pytest.raises(ValueError, match="spoken_form is only valid"):
        AbbreviationEntry(
            "AAA",
            "anti-aircraft artillery",
            speech_strategy=speech_strategy,  # type: ignore[arg-type]
            spoken_form="Triple A",
        )


@pytest.mark.parametrize("spoken_form", [None, "", "   "])
def test_custom_strategy_requires_non_empty_spoken_form(spoken_form: str | None) -> None:
    with pytest.raises(ValueError, match="requires a non-empty spoken_form"):
        AbbreviationEntry(
            "AAA", "anti-aircraft artillery", speech_strategy="custom", spoken_form=spoken_form
        )


def test_aliases_use_matched_source_for_spelling_and_custom_form() -> None:
    expander = get_expander("en", registered_initialism_mode="spell")
    expander.add("AO", "area of operations", speech_strategy="spell_source", aliases=("A.O.",))
    expander.add(
        "AAA",
        "anti-aircraft artillery",
        speech_strategy="custom",
        spoken_form="Triple A",
        aliases=("A.A.A.",),
    )

    assert expander.expand("AO A.O. AAA A.A.A.") == "A O A O Triple A Triple A."


def test_context_and_case_policy_are_independent_from_realization() -> None:
    expander = get_expander("en", registered_initialism_mode="spell")
    expander.add(
        "Ref.",
        {"default": "reference", "title": "referee"},
        case_policy="sentence",
        speech_strategy="custom",
        spoken_form="R E F",
    )
    expander.add(
        "AO.",
        {"default": "area of operations", "title": "area officer"},
        case_policy="sentence",
        speech_strategy="spell_source",
    )

    assert expander.expand("Ref. AO.") == "R E F A O."


def test_guards_and_pos_apply_before_realization() -> None:
    expander = get_expander("en", registered_initialism_mode="spell")
    expander.add(
        "AO",
        "area of operations",
        speech_strategy="spell_source",
        only_if_preceded_by=r"\d\s*$",
        only_if_followed_by=r"^\s+now",
        only_if_pos="NOUN",
        not_if_pos="PROPN",
    )
    expander.add(
        "AAA",
        "anti-aircraft artillery",
        speech_strategy="custom",
        spoken_form="Triple A",
        only_if_pos="NOUN",
    )

    assert (
        expander.expand(
            "2 AO now AAA",
            annotations=[TokenAnnotation(2, 4, "NOUN"), TokenAnnotation(8, 11, "NOUN")],
        )
        == "2 A O now Triple A"
    )
    assert (
        expander.expand("AO now AAA", annotations=[TokenAnnotation(7, 10, "VERB")]) == "AO now AAA"
    )
    assert expander.expand("2 AO now", annotations=[TokenAnnotation(2, 4, "PROPN")]) == "2 AO now"


def test_protected_spans_apply_to_all_strategies() -> None:
    expander = get_expander("en", registered_initialism_mode="spell")
    expander.add("AAR", "after-action review")
    expander.add("AO", "area of operations", speech_strategy="spell_source")
    expander.add("AAA", "anti-aircraft artillery", speech_strategy="custom", spoken_form="Triple A")

    assert (
        expander.expand("AAR AO AAA", protected_spans=[(4, 6)]) == "after-action review AO Triple A"
    )


def test_custom_spoken_form_replacement_metadata_is_source_aligned() -> None:
    expander = get_expander("en", registered_initialism_mode="spell")
    expander.add("AAA", "anti-aircraft artillery", speech_strategy="custom", spoken_form="Triple A")

    result = expander.expand_with_replacements("Use AAA now.")
    replacement = result.replacements[0]

    assert (replacement.start, replacement.end) == (4, 7)
    assert replacement.matched_text == "AAA"
    assert replacement.text == "Triple A"
    assert replacement.kind == "abbreviation"
    assert replacement.abbreviation == "AAA"
    assert replacement.rule_id == "abbr:AAA"


def test_bundled_semantic_entries_remain_semantic_in_spell_mode() -> None:
    expander = get_expander("en", registered_initialism_mode="spell")
    expander.add("AO", "area of operations", speech_strategy="spell_source")

    assert expander.expand("Dr. AO") == "Doctor A O"


def test_strategy_aliases_are_public_types() -> None:
    from abbr2words import CasePolicy, SpeechStrategy

    assert CasePolicy is not None
    assert SpeechStrategy is not None
