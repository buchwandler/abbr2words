from __future__ import annotations

import json
from pathlib import Path

from abbr2words import get_shared_expander, reset_expanders, supported_languages
from abbr2words.units import unit_entries, unit_symbols

EXPECTED_DECLARATIONS = {
    "cs": 66,
    "de": 62,
    "en": 163,
    "es": 73,
    "fr": 58,
    "it": 85,
    "nl": 37,
    "pl": 39,
    "pt": 73,
    "ru": 16,
    "sv": 30,
    "tr": 15,
}
EXPECTED_EFFECTIVE = {
    "cs": 65,
    "de": 61,
    "en": 163,
    "es": 72,
    "fr": 57,
    "it": 84,
    "nl": 37,
    "pl": 39,
    "pt": 72,
    "ru": 16,
    "sv": 30,
    "tr": 15,
}
REQUIRED_ALL_LANGUAGE_EFFECTIVE_HASH = (
    "70c2d6395caaad7e22c66a51b001d2651c0a1d4545916f43964d66c913f1d868"
)
SNAPSHOT = json.loads(
    (Path(__file__).parent / "data" / "registry_snapshot.json").read_text(encoding="utf-8")
)


def test_effective_registry_counts_match_migration_contract() -> None:
    actual = {lang: len(get_shared_expander(lang).entries) for lang in supported_languages()}
    assert actual == EXPECTED_EFFECTIVE
    assert actual == SNAPSHOT["effective_counts"]
    assert sum(actual.values()) == 711
    assert SNAPSHOT["declarations"] == EXPECTED_DECLARATIONS
    assert sum(SNAPSHOT["declarations"].values()) == 717


def test_every_effective_registry_field_matches_snapshot() -> None:
    actual = []
    for lang in supported_languages():
        for key, entry in get_shared_expander(lang).entries.items():
            contexts = (
                None
                if entry.context_expansions is None
                else {context.value: value for context, value in entry.context_expansions.items()}
            )
            actual.append(
                {
                    "language": lang,
                    "key": key,
                    "abbreviation": entry.abbreviation,
                    "expansion": entry.expansion,
                    "aliases": list(entry.aliases),
                    "context_expansions": contexts,
                    "case_sensitive": entry.case_sensitive,
                    "description": entry.description,
                    "only_if_preceded_by": (
                        str(entry.only_if_preceded_by)
                        if entry.only_if_preceded_by is not None
                        else None
                    ),
                    "only_if_followed_by": (
                        str(entry.only_if_followed_by)
                        if entry.only_if_followed_by is not None
                        else None
                    ),
                }
            )
    assert sorted(actual, key=lambda row: (row["language"], row["key"])) == SNAPSHOT["entries"]


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
    for language in supported_languages():
        symbols = unit_symbols(language)
        for entry in get_shared_expander(language).entries.values():
            if entry.abbreviation in symbols:
                unit_entry = next(
                    item for item in unit_entries(language) if entry.abbreviation in item.symbols
                )
                if unit_entry.category == "magnitude":
                    continue
                assert entry.case_sensitive
                assert entry.only_if_preceded_by or entry.only_if_followed_by


def test_required_hash_is_a_committed_parity_contract() -> None:
    """Keep the brief's source snapshot hash visible to registry consumers."""
    assert REQUIRED_ALL_LANGUAGE_EFFECTIVE_HASH == SNAPSHOT["required_all_language_effective_hash"]


def teardown_module() -> None:
    reset_expanders()
