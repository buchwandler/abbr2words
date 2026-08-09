from __future__ import annotations

import pytest

import abbr2words.core as core
from abbr2words import (
    Expander,
    TokenAnnotation,
    abbr2words,
    get_expander,
    get_shared_expander,
    reset_expanders,
)


@pytest.fixture(autouse=True)
def reset_shared_registries() -> None:
    reset_expanders()


def test_shared_mutation_is_visible_to_public_api() -> None:
    shared = get_shared_expander("en")
    shared.add_custom_abbreviation("Tech.", "Technology")

    assert abbr2words("Tech. works", lang="en") == "Technology works"
    assert get_shared_expander("en") is shared


def test_shared_context_customization_accepts_string_contexts() -> None:
    shared = get_shared_expander("en")
    shared.add_custom_abbreviation(
        "Ex.",
        {"default": "Example", "place": "Exit"},
        "Example or Exit",
    )

    assert shared.get_abbreviation("Ex.").get_expansion() == "Example"
    assert shared.get_abbreviation("Ex.").context_expansions


def test_expansion_uses_one_registry_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    expander = get_expander("en")
    expander.add_custom_abbreviation("First.", "first", case_sensitive=True)
    original_unit_replacements = core.iter_unit_replacements
    state = {"units_mutated": False, "entries_mutated": False}

    def mutate_units(text: str, language: str, overrides, suppressed):
        if not state["units_mutated"]:
            state["units_mutated"] = True
            expander.set_unit("kg", "custom kilogram")
        return original_unit_replacements(text, language, overrides, suppressed)

    monkeypatch.setattr(core, "iter_unit_replacements", mutate_units)
    original_entry_replacements = expander._iter_entry_replacements

    def mutate_entries(text: str, entry, annotation_index):
        if not state["entries_mutated"]:
            state["entries_mutated"] = True
            expander.add_custom_abbreviation("Late.", "late", case_sensitive=True)
        yield from original_entry_replacements(text, entry, annotation_index)

    monkeypatch.setattr(expander, "_iter_entry_replacements", mutate_entries)

    assert expander.expand("First. Late. 2 kg") == "first Late. 2 kilogram"
    assert expander.expand("First. Late. 2 kg") == "first late 2 custom kilogram"


def test_english_custom_add_matches_base_context_and_guard_behavior() -> None:
    expander = get_expander("en")
    expander.add_custom_abbreviation(
        "Ref.",
        {"default": "Reference", "title": "Referee"},
        only_if_followed_by=r"\s+\w",
        only_if_pos="NOUN",
        not_if_pos={"PROPN"},
    )

    assert (
        expander.expand("Ref. text", annotations=[TokenAnnotation(0, 4, "NOUN")])
        == "Reference text"
    )
    assert expander.expand("Ref. text", annotations=[TokenAnnotation(0, 4, "PROPN")]) == "Ref. text"
    assert expander.expand("Ref. text", annotations=[TokenAnnotation(0, 4, "VERB")]) == "Ref. text"
    assert expander.expand("Ref.-8", annotations=[TokenAnnotation(0, 4, "NOUN")]) == "Ref.-8"


def test_isolated_expanders_do_not_leak_into_shared_registry() -> None:
    isolated = Expander("en")
    isolated.add("Only.", "Isolated")

    assert isolated("Only.") == "Isolated"
    assert abbr2words("Only.", lang="en") == "Only."
    assert not get_shared_expander("en").has_abbreviation("Only.")


def test_get_expander_returns_a_new_isolated_registry() -> None:
    first = get_expander("de")
    second = get_expander("de")
    first.add_custom_abbreviation("One.", "First")

    assert first is not second
    assert first.has_abbreviation("One.")
    assert not second.has_abbreviation("One.")


def test_reset_removes_shared_custom_entries() -> None:
    get_shared_expander("en").add_custom_abbreviation("Gone.", "Gone")
    assert abbr2words("Gone.", lang="en") == "Gone"

    reset_expanders("en")

    assert abbr2words("Gone.", lang="en") == "Gone."
    assert get_shared_expander("en").has_abbreviation("Dr.")


def test_shared_registries_are_separate_per_context_mode() -> None:
    contextual = get_shared_expander("en", context=True)
    plain = get_shared_expander("en", context=False)

    assert contextual is not plain
    assert contextual.enable_context_detection is True
    assert plain.enable_context_detection is False


def test_context_mode_cache_is_reset_for_each_mode() -> None:
    contextual = get_shared_expander("en", context=True)
    plain = get_shared_expander("en", context=False)
    contextual.add_custom_abbreviation("Ctx.", "Contextual")
    plain.add_custom_abbreviation("Plain.", "Plain")

    reset_expanders("en")

    assert get_shared_expander("en", context=True) is not contextual
    assert get_shared_expander("en", context=False) is not plain
    assert not get_shared_expander("en", context=True).has_abbreviation("Ctx.")
    assert not get_shared_expander("en", context=False).has_abbreviation("Plain.")
