from __future__ import annotations

import json
from pathlib import Path

from abbr2words import get_shared_expander, reset_expanders, supported_languages

EXPECTED_DECLARATIONS = {
    "cs": 66,
    "de": 61,
    "en": 163,
    "es": 73,
    "fr": 58,
    "it": 85,
    "pt": 73,
}
EXPECTED_EFFECTIVE = {
    "cs": 65,
    "de": 60,
    "en": 163,
    "es": 72,
    "fr": 57,
    "it": 84,
    "pt": 72,
}
REQUIRED_ALL_LANGUAGE_EFFECTIVE_HASH = (
    "94c18aa22c7d2b26dae30e0cda6a5aedce6bc8ccc25396b5af16d8ddd43458c0"
)
SNAPSHOT = json.loads(
    (Path(__file__).parent / "data" / "registry_snapshot.json").read_text(encoding="utf-8")
)


def test_effective_registry_counts_match_migration_contract() -> None:
    actual = {lang: len(get_shared_expander(lang).entries) for lang in supported_languages()}
    assert actual == EXPECTED_EFFECTIVE
    assert actual == SNAPSHOT["effective_counts"]
    assert sum(actual.values()) == 573
    assert SNAPSHOT["declarations"] == EXPECTED_DECLARATIONS
    assert sum(SNAPSHOT["declarations"].values()) == 579


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
    assert sum(entry.case_sensitive for entry in entries) == 6
    assert (
        sum(bool(entry.only_if_preceded_by or entry.only_if_followed_by) for entry in entries) == 32
    )


def test_required_hash_is_a_committed_parity_contract() -> None:
    """Keep the brief's source snapshot hash visible to registry consumers."""
    assert REQUIRED_ALL_LANGUAGE_EFFECTIVE_HASH == SNAPSHOT["required_all_language_effective_hash"]


def teardown_module() -> None:
    reset_expanders()
