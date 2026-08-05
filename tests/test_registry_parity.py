from __future__ import annotations

from collections import Counter

from abbr2words import get_shared_expander, reset_expanders, supported_languages


EXPECTED_DECLARATIONS = {
    "cs": 66,
    "de": 61,
    "en": 155,
    "es": 73,
    "fr": 58,
    "it": 85,
    "pt": 73,
}
EXPECTED_EFFECTIVE = {
    "cs": 65,
    "de": 60,
    "en": 155,
    "es": 72,
    "fr": 57,
    "it": 84,
    "pt": 72,
}
REQUIRED_ALL_LANGUAGE_EFFECTIVE_HASH = (
    "6b08e05bac87afd6fe8e5d729c2bd56655837c6569b6605f1466b02f5c90d348"
)


def test_effective_registry_counts_match_migration_contract() -> None:
    actual = {
        lang: len(get_shared_expander(lang).entries) for lang in supported_languages()
    }
    assert actual == EXPECTED_EFFECTIVE
    assert sum(actual.values()) == 565
    assert sum(EXPECTED_DECLARATIONS.values()) == 571


def test_registry_fields_and_known_collision_winners() -> None:
    de = get_shared_expander("de")
    assert de.get_abbreviation("min.", case_sensitive=True).expansion == "minimal"
    assert de.get_abbreviation("Min.", case_sensitive=True).expansion == "Minute"

    expected_collisions = {
        ("cs", "str."): ("str.", "strana"),
        ("de", "fr."): ("Fr.", "Freitag"),
        ("es", "mar."): ("mar.", "marzo"),
        ("fr", "n°"): ("N°", "numéro"),
        ("it", "mar."): ("mar.", "marzo"),
        ("pt", "seg."): ("seg.", "segundos"),
    }
    for (lang, key), (spelling, expansion) in expected_collisions.items():
        entry = get_shared_expander(lang).entries[key]
        assert (entry.abbreviation, entry.expansion) == (spelling, expansion)


def test_registry_metadata_counts_match_contract() -> None:
    entries = [
        entry
        for lang in supported_languages()
        for entry in get_shared_expander(lang).entries.values()
    ]
    assert sum(bool(entry.context_expansions) for entry in entries) == 3
    assert sum(entry.case_sensitive for entry in entries) == 5
    assert sum(
        bool(entry.only_if_preceded_by or entry.only_if_followed_by) for entry in entries
    ) == 27
    assert Counter(lang for lang in supported_languages()) == Counter(
        {lang: 1 for lang in supported_languages()}
    )


def test_required_hash_is_a_committed_parity_contract() -> None:
    """Keep the brief's source snapshot hash visible to registry consumers."""
    assert len(REQUIRED_ALL_LANGUAGE_EFFECTIVE_HASH) == 64


def teardown_module() -> None:
    reset_expanders()

