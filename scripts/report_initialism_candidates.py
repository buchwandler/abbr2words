#!/usr/bin/env python3
"""Group unresolved initialism candidates from benchmark failure rows.

Input may be JSONL or JSON. Each record must provide source text, language,
and expected output using one of the accepted field aliases:

- source text: ``text`` or ``source``
- language: ``lang``, ``language``, or ``locale``
- expected output: ``expected``, ``target``, or ``reference``

Optional fields:

- actual output: ``actual``, ``output``, ``normalized``, or ``prediction``
- protected spans: ``protected_spans`` as ``[start, end]`` pairs or
  ``{"start": ..., "end": ...}`` objects
- semantic-failure metadata such as ``semantic_failure`` or ``speech_wer``

If ``actual`` is omitted, the script evaluates the current repository build
with ``initialism_mode="conservative_undotted"``. Only rows whose expected
output spells a candidate token while the actual output does not are reported.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from functools import cache
from pathlib import Path
from typing import Any

from abbr2words import (
    abbr2words,
    get_shared_expander,
    iter_initialism_diagnostics,
    supported_languages,
)

_SOURCE_KEYS = ("text", "source")
_LANGUAGE_KEYS = ("lang", "language", "locale")
_EXPECTED_KEYS = ("expected", "target", "reference")
_ACTUAL_KEYS = ("actual", "output", "normalized", "prediction")
_ROW_COLLECTION_KEYS = ("rows", "records", "cases", "failures", "items")
_ROMAN_ONLY = re.compile(r"^[IVXLCDM]+$")
_VOWELS = frozenset("AEIOUY")


def _first_string(record: Mapping[str, Any], keys: Sequence[str], *, required: bool = True) -> str | None:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str):
            return value
    if required:
        joined = ", ".join(keys)
        raise ValueError(f"row requires one of these string fields: {joined}")
    return None


def _normalize_surface(text: str) -> str:
    return " ".join(text.split()).casefold()


def _semantic_failure(record: Mapping[str, Any], actual: str, expected: str) -> bool:
    for key in ("semantic_failure", "speech_failure", "speech_mismatch"):
        value = record.get(key)
        if isinstance(value, bool):
            return value
    for key in ("speech_wer", "semantic_wer", "wer"):
        value = record.get(key)
        if isinstance(value, (int, float)):
            return float(value) > 0.0
    return _normalize_surface(actual) != _normalize_surface(expected)


def _normalize_protected_spans(value: Any) -> tuple[tuple[int, int], ...]:
    if value in (None, ()):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("protected_spans must be a sequence of spans")

    normalized: list[tuple[int, int]] = []
    for item in value:
        start: Any
        end: Any
        if isinstance(item, Mapping):
            start = item.get("start")
            end = item.get("end")
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)) and len(item) >= 2:
            start, end = item[0], item[1]
        else:
            raise ValueError("protected_spans entries must be [start, end] or {start, end}")
        if not isinstance(start, int) or not isinstance(end, int):
            raise ValueError("protected_spans start/end must be integers")
        if start < 0 or end < start:
            raise ValueError("protected_spans entries must satisfy 0 <= start <= end")
        normalized.append((start, end))
    return tuple(normalized)


def _text_records(payload: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, Mapping):
        rows = None
        for key in _ROW_COLLECTION_KEYS:
            candidate = payload.get(key)
            if isinstance(candidate, list):
                rows = candidate
                break
        if rows is None:
            rows = [payload]
    else:
        raise ValueError("benchmark report must be a JSON object, array, or JSONL objects")

    result: list[Mapping[str, Any]] = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, Mapping):
            raise ValueError(f"row {index} must be a JSON object")
        result.append(row)
    return tuple(result)


def load_records(path: Path) -> tuple[Mapping[str, Any], ...]:
    """Load benchmark rows from *path*."""
    if path.suffix == ".jsonl":
        rows: list[Mapping[str, Any]] = []
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, Mapping):
                    raise ValueError(f"line {line_number} must contain a JSON object")
                rows.append(value)
        return tuple(rows)
    return _text_records(json.loads(path.read_text(encoding="utf-8")))


@cache
def _spelled_pattern(token: str) -> re.Pattern[str]:
    letters = r"\s+".join(re.escape(char) for char in token)
    return re.compile(rf"(?<!\w){letters}(?!\w)", re.IGNORECASE)


@cache
def _compact_pattern(token: str) -> re.Pattern[str]:
    return re.compile(rf"(?<!\w){re.escape(token)}(?!\w)", re.IGNORECASE)


def _contains_spelling(text: str, token: str) -> bool:
    return _spelled_pattern(token).search(text) is not None


def _contains_compact_token(text: str, token: str) -> bool:
    return _compact_pattern(token).search(text) is not None


def _registry_entry_for(token: str, language: str) -> bool:
    expander = get_shared_expander(language)
    for entry in expander.entries.values():
        spellings = (entry.abbreviation, *entry.aliases)
        if entry.case_sensitive:
            if token in spellings:
                return True
            continue
        if any(token.casefold() == spelling.casefold() for spelling in spellings):
            return True
    return False


@cache
def _registered_locales(token: str) -> tuple[str, ...]:
    locales: list[str] = []
    for language in supported_languages():
        if _registry_entry_for(token, language):
            locales.append(language)
    return tuple(locales)


def _reason_summary(reasons: Counter[str]) -> str:
    ordered = sorted(reasons.items(), key=lambda item: (-item[1], item[0]))
    if len(ordered) == 1:
        return ordered[0][0]
    return "; ".join(
        reason if count == 1 else f"{reason}:{count}" for reason, count in ordered
    )


def _sample_summary(samples: Sequence[str]) -> str:
    return " || ".join(samples)


def analyze_records(
    records: Iterable[Mapping[str, Any]],
    *,
    sample_limit: int = 3,
) -> list[dict[str, Any]]:
    """Return grouped unresolved initialism candidates."""
    groups: dict[str, dict[str, Any]] = {}

    for row in records:
        source = _first_string(row, _SOURCE_KEYS)
        language = _first_string(row, _LANGUAGE_KEYS)
        expected = _first_string(row, _EXPECTED_KEYS)
        assert source is not None and language is not None and expected is not None
        protected_spans = _normalize_protected_spans(row.get("protected_spans"))
        actual = _first_string(row, _ACTUAL_KEYS, required=False)
        if actual is None:
            actual = abbr2words(
                source,
                lang=language,
                initialism_mode="conservative_undotted",
                protected_spans=protected_spans,
            )

        diagnostics = tuple(
            iter_initialism_diagnostics(
                source,
                language,
                initialism_mode="conservative_undotted",
                protected_spans=protected_spans,
            )
        )
        semantic_failure = _semantic_failure(row, actual, expected)
        for diagnostic in diagnostics:
            token = diagnostic.source_text
            if not _contains_spelling(expected, token):
                continue
            if _contains_spelling(actual, token):
                continue

            group = groups.setdefault(
                token,
                {
                    "token": token,
                    "count": 0,
                    "semantic_failures": 0,
                    "presentation_only": 0,
                    "locales": set(),
                    "reasons": Counter(),
                    "protected": False,
                    "uppercase_run": False,
                    "registered_in_observed_locale": False,
                    "actual_compact": False,
                    "samples": [],
                },
            )
            group["count"] += 1
            group["semantic_failures"] += int(semantic_failure)
            group["presentation_only"] += int(not semantic_failure)
            group["locales"].add(language)
            group["reasons"][diagnostic.reason] += 1
            group["protected"] = group["protected"] or diagnostic.reason == "protected-span"
            group["uppercase_run"] = group["uppercase_run"] or diagnostic.reason == "uppercase-run"
            group["registered_in_observed_locale"] = (
                group["registered_in_observed_locale"] or diagnostic.registered_entry_id is not None
            )
            group["actual_compact"] = group["actual_compact"] or _contains_compact_token(actual, token)
            if source not in group["samples"] and len(group["samples"]) < sample_limit:
                group["samples"].append(source)

    rows: list[dict[str, Any]] = []
    for token, group in groups.items():
        registered_locales = _registered_locales(token)
        rows.append(
            {
                "token": token,
                "count": group["count"],
                "semantic_failures": group["semantic_failures"],
                "presentation_only": group["presentation_only"],
                "locales": sorted(group["locales"]),
                "reason": _reason_summary(group["reasons"]),
                "roman_like": _ROMAN_ONLY.fullmatch(token) is not None,
                "vowel_bearing": any(character in _VOWELS for character in token),
                "two_letter": len(token) == 2,
                "registered": bool(registered_locales),
                "registered_in_observed_locale": group["registered_in_observed_locale"],
                "registered_locales": list(registered_locales),
                "protected": group["protected"],
                "uppercase_run": group["uppercase_run"],
                "actual_compact": group["actual_compact"],
                "samples": list(group["samples"]),
            }
        )
    rows.sort(key=lambda row: (-int(row["semantic_failures"]), -int(row["count"]), str(row["token"])))
    return rows


def _csv_ready_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            **row,
            "locales": ",".join(row["locales"]),
            "registered_locales": ",".join(row["registered_locales"]),
            "samples": _sample_summary(row["samples"]),
        }
        for row in rows
    ]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON or JSONL benchmark failure report")
    parser.add_argument(
        "--format",
        choices=("csv", "json"),
        default="csv",
        help="Output format (default: csv).",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=3,
        help="Maximum number of distinct source samples per token (default: 3).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    rows = analyze_records(load_records(args.input), sample_limit=args.sample_limit)
    if args.format == "json":
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    csv_rows = _csv_ready_rows(rows)
    fieldnames = [
        "token",
        "count",
        "semantic_failures",
        "presentation_only",
        "locales",
        "reason",
        "roman_like",
        "vowel_bearing",
        "two_letter",
        "registered",
        "registered_in_observed_locale",
        "registered_locales",
        "protected",
        "uppercase_run",
        "actual_compact",
        "samples",
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(csv_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
