#!/usr/bin/env python3
"""Classify PolyNorm abbreviation cases at the abbr2words boundary.

The helper intentionally runs only the lexical abbr2words stage.  Input is
JSONL with at least ``text`` and ``lang`` (``language`` is accepted as an
alias).  Optional ``expected`` is the complete downstream expected text;
optional ``expected_abbr2words`` is the expected lexical-stage result.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from abbr2words import abbr2words_with_replacements

OWNERSHIP_CLASSES = frozenset(
    {
        "owned-abbr",
        "owned-unit-identity",
        "spokenform-number",
        "spokenform-structured-collision",
        "grammar-out-of-scope",
        "entity-resolution-out-of-scope",
        "benchmark-questionable",
    }
)


def _classification(record: Mapping[str, Any], actual: str, replacements: tuple[Any, ...]) -> str:
    expected_lexical = record.get("expected_abbr2words", record.get("expected_lexical"))
    if expected_lexical is not None:
        return "lexical-defect" if actual != expected_lexical else "lexical-stage-match"

    expected = record.get("expected")
    if expected is None:
        return "unassessed"
    if actual == expected:
        return "matched"
    if replacements:
        return "downstream-numeric-structured"
    return "unsupported-benchmark-specific/entity"


def _ownership_metadata(record: Mapping[str, Any]) -> tuple[str | None, str | None]:
    """Read reviewed fixture metadata and fail closed for lexical expectations."""
    expected_lexical = record.get("expected_abbr2words", record.get("expected_lexical"))
    reason = record.get("reason")
    owner = record.get("owner")
    if expected_lexical is not None:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("lexical fixture cases require a non-empty 'reason'")
        if not isinstance(owner, str) or owner not in OWNERSHIP_CLASSES:
            allowed = ", ".join(sorted(OWNERSHIP_CLASSES))
            raise ValueError(f"lexical fixture cases require owner in: {allowed}")
    return reason if isinstance(reason, str) else None, owner if isinstance(owner, str) else None


def diagnose(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return one JSON-serializable abbreviation-stage diagnostic row."""
    text = record.get("text", record.get("source"))
    language = record.get("lang", record.get("language"))
    if not isinstance(text, str) or not isinstance(language, str):
        raise ValueError("each case requires string fields 'text' and 'lang' (or their aliases)")

    reason, owner = _ownership_metadata(record)
    result = abbr2words_with_replacements(text, lang=language)
    replacements = tuple(result.replacements)
    return {
        "id": record.get("id"),
        "category": record.get("category", "Abbreviation"),
        "lang": language,
        "source": text,
        "abbr2words": result.text,
        "classification": _classification(record, result.text, replacements),
        "reason": reason,
        "owner": owner,
        "replacements": [
            {
                "start": item.start,
                "end": item.end,
                "source": item.source,
                "replacement": item.text,
                "kind": item.kind,
                "rule": item.rule,
                "context": item.context.value if item.context is not None else None,
            }
            for item in replacements
        ],
    }


def _records(path: Path) -> Iterable[Mapping[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, Mapping):
                raise ValueError(f"line {line_number} must contain a JSON object")
            yield value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSONL PolyNorm abbreviation cases")
    args = parser.parse_args(argv)

    for record in _records(args.input):
        print(json.dumps(diagnose(record), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
