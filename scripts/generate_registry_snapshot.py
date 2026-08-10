"""Regenerate deterministic sharded effective abbreviation registry snapshots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from abbr2words import get_shared_expander, supported_languages


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
        "aliases": list(entry.aliases),
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


def build_registry(language: str) -> list[dict[str, Any]]:
    """Return one sorted effective registry shard."""
    rows = [
        _entry_row(language, key, entry)
        for key, entry in get_shared_expander(language).entries.items()
    ]
    return sorted(rows, key=lambda row: row["key"])


def _canonical(rows: list[dict[str, Any]]) -> str:
    return json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_index(registries: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Return the compact shard index and all-registry integrity hash."""
    all_rows = [row for language in sorted(registries) for row in registries[language]]
    return {
        "repository": "abbr2words",
        "languages": {
            language: {
                "count": len(rows),
                "sha256": hashlib.sha256(_canonical(rows).encode()).hexdigest(),
            }
            for language, rows in sorted(registries.items())
        },
        "all_sha256": hashlib.sha256(_canonical(all_rows).encode()).hexdigest(),
    }


def main() -> int:
    root = Path(__file__).parents[1] / "tests" / "data" / "registries"
    root.mkdir(parents=True, exist_ok=True)
    registries = {language: build_registry(language) for language in supported_languages()}
    for language, rows in registries.items():
        (root / f"{language}.json").write_text(
            json.dumps({"language": language, "entries": rows}, indent=2, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )
    (root / "index.json").write_text(
        json.dumps(build_index(registries), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(registries)} registry shards to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
