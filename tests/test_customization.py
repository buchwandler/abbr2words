from __future__ import annotations

import warnings

import pytest

from abbr2words import Expander, abbr2words, get_expander, get_shared_expander, reset_expanders


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


def test_context_mode_change_preserves_singleton_warning_semantics() -> None:
    get_shared_expander("en", context=True)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        same = get_shared_expander("en", context=False)

    assert same.enable_context_detection is True
    assert any("already initialized" in str(item.message) for item in caught)
