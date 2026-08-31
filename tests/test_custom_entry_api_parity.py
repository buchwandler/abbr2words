from __future__ import annotations

import pytest

from abbr2words import AbbreviationContext, get_expander


def test_context_mapping_preserves_all_custom_entry_metadata() -> None:
    expander = get_expander("en")
    expander.add(
        "Ref.",
        {"default": "reference", "title": "referee"},
        description="Reference abbreviation",
        case_sensitive=True,
        only_if_preceded_by=r"\b",
        only_if_followed_by=r"\s+\w",
        only_if_pos="NOUN",
        not_if_pos={"PROPN"},
        case_policy="sentence",
        speech_strategy="custom",
        spoken_form="R E F",
        aliases=("ReferenceAbbr.",),
    )

    entry = expander.get_abbreviation("Ref.", case_sensitive=True)
    assert entry is not None
    assert entry.context_expansions == {AbbreviationContext.TITLE: "referee"}
    assert entry.description == "Reference abbreviation"
    assert entry.case_sensitive is True
    assert entry.only_if_preceded_by == r"\b"
    assert entry.only_if_followed_by == r"\s+\w"
    assert entry.only_if_pos == frozenset({"NOUN"})
    assert entry.not_if_pos == frozenset({"PROPN"})
    assert entry.case_policy == "sentence"
    assert entry.speech_strategy == "custom"
    assert entry.spoken_form == "R E F"
    assert entry.aliases == ("ReferenceAbbr.",)
    assert entry.origin == "custom"


def test_add_custom_abbreviation_matches_add() -> None:
    first = get_expander("en")
    second = get_expander("en")
    kwargs = {
        "description": "Reference abbreviation",
        "case_sensitive": True,
        "case_policy": "sentence",
        "speech_strategy": "custom",
        "spoken_form": "R E F",
        "aliases": ("ReferenceAbbr.",),
    }
    first.add("Ref.", {"default": "reference", "title": "referee"}, **kwargs)
    second.add_custom_abbreviation("Ref.", {"default": "reference", "title": "referee"}, **kwargs)

    left = first.get_abbreviation("Ref.", case_sensitive=True)
    right = second.get_abbreviation("Ref.", case_sensitive=True)
    assert left == right
    assert first.expand("Ref. ReferenceAbbr.") == second.expand("Ref. ReferenceAbbr.")


@pytest.mark.parametrize(
    "build",
    [
        lambda expander: expander.add("", "value"),
        lambda expander: expander.add_custom_abbreviation("", "value"),
    ],
)
def test_custom_entry_paths_validate_empty_abbreviation_consistently(build) -> None:
    with pytest.raises(ValueError, match="abbreviation must not be empty"):
        build(get_expander("en"))


def test_context_mapping_without_default_keeps_deterministic_first_value() -> None:
    expander = get_expander("en")
    expander.add_custom_abbreviation("Ref.", {"title": "referee", "place": "reference"})

    entry = expander.get_abbreviation("Ref.")
    assert entry is not None
    assert entry.expansion == "referee"
    assert entry.context_expansions == {
        AbbreviationContext.TITLE: "referee",
        AbbreviationContext.PLACE: "reference",
    }
