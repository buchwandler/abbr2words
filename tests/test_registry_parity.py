from __future__ import annotations

import hashlib
import json
from pathlib import Path

from abbr2words import get_shared_expander, reset_expanders, supported_languages
from abbr2words.units import unit_entries, unit_symbols

SHARDS = Path(__file__).parent / "data" / "registries"
INDEX = json.loads((SHARDS / "index.json").read_text(encoding="utf-8"))


def _shard(language: str) -> list[dict[str, object]]:
    payload = json.loads((SHARDS / f"{language}.json").read_text(encoding="utf-8"))
    assert payload["language"] == language
    return payload["entries"]


def _canonical(rows: list[dict[str, object]]) -> str:
    return json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def test_effective_registry_counts_match_sharded_contract() -> None:
    actual = {lang: len(get_shared_expander(lang).entries) for lang in supported_languages()}
    expected = {lang: metadata["count"] for lang, metadata in INDEX["languages"].items()}
    assert actual == expected
    assert len(actual) == 66


def test_every_effective_registry_field_matches_its_shard() -> None:
    for language in supported_languages():
        actual = []
        for key, entry in get_shared_expander(language).entries.items():
            contexts = (
                None
                if entry.context_expansions is None
                else {context.value: value for context, value in entry.context_expansions.items()}
            )
            actual.append(
                {
                    "language": language,
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
                    "variants": [
                        {
                            "expansion": variant.expansion,
                            "only_if_preceded_by": (
                                str(variant.only_if_preceded_by)
                                if variant.only_if_preceded_by is not None
                                else None
                            ),
                            "only_if_followed_by": (
                                str(variant.only_if_followed_by)
                                if variant.only_if_followed_by is not None
                                else None
                            ),
                            "only_if_pos": sorted(variant.only_if_pos)
                            if variant.only_if_pos
                            else None,
                            "not_if_pos": sorted(variant.not_if_pos)
                            if variant.not_if_pos
                            else None,
                        }
                        for variant in entry.variants
                    ],
                }
            )
        actual.sort(key=lambda row: row["key"])
        assert actual == _shard(language)


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


def test_registry_metadata_and_unit_guards_match_contract() -> None:
    entries = [
        entry
        for lang in supported_languages()
        for entry in get_shared_expander(lang).entries.values()
    ]
    assert sum(bool(entry.context_expansions) for entry in entries) >= 3
    for language in supported_languages():
        symbols = unit_symbols(language)
        for entry in get_shared_expander(language).entries.values():
            if entry.abbreviation in symbols and entry.origin != "custom":
                unit_entry = next(
                    item for item in unit_entries(language) if entry.abbreviation in item.symbols
                )
                if unit_entry.category == "magnitude" or unit_entry.allow_lexical_overlap:
                    continue
                assert entry.case_sensitive
                assert entry.only_if_preceded_by or entry.only_if_followed_by


def test_shard_hashes_and_all_registry_hash_are_deterministic() -> None:
    all_rows = []
    for language in sorted(supported_languages()):
        rows = _shard(language)
        all_rows.extend(rows)
        assert (
            hashlib.sha256(_canonical(rows).encode()).hexdigest()
            == INDEX["languages"][language]["sha256"]
        )
    assert hashlib.sha256(_canonical(all_rows).encode()).hexdigest() == INDEX["all_sha256"]


def teardown_module() -> None:
    reset_expanders()
