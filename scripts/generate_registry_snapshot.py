"""Regenerate the committed effective abbreviation registry snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from abbr2words import get_shared_expander, supported_languages

DECLARATION_COUNTS = {
    "cs": 66,
    "de": 61,
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


def _entry_row(language: str, key: str, entry: Any) -> dict[str, Any]:
    contexts = (
        None
        if entry.context_expansions is None
        else {context.value: value for context, value in entry.context_expansions.items()}
    )
    return {
        "language": language,
        "key": key,
        "abbreviation": entry.abbreviation,
        "expansion": entry.expansion,
        "context_expansions": contexts,
        "case_sensitive": entry.case_sensitive,
        "description": entry.description,
        "only_if_preceded_by": (
            str(entry.only_if_preceded_by) if entry.only_if_preceded_by is not None else None
        ),
        "only_if_followed_by": (
            str(entry.only_if_followed_by) if entry.only_if_followed_by is not None else None
        ),
    }


def build_snapshot() -> dict[str, Any]:
    """Return the current registry data in the test snapshot format."""
    entries = [
        _entry_row(language, key, entry)
        for language in supported_languages()
        for key, entry in get_shared_expander(language).entries.items()
    ]
    entries.sort(key=lambda row: (row["language"], row["key"]))
    canonical = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "declarations": DECLARATION_COUNTS,
        "effective_counts": {
            language: sum(row["language"] == language for row in entries)
            for language in supported_languages()
        },
        "required_all_language_effective_hash": hashlib.sha256(canonical.encode()).hexdigest(),
        "entries": entries,
    }


def main() -> int:
    """Write the snapshot consumed by the registry parity tests."""
    output = Path(__file__).parents[1] / "tests" / "data" / "registry_snapshot.json"
    output.write_text(
        json.dumps(build_snapshot(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
