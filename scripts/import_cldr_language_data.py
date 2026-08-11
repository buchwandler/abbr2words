"""Import a pinned local CLDR tree into deterministic Python data.

This developer tool never downloads data and is never imported by the runtime
package.  It intentionally reads only Gregorian month/day abbreviated and wide
forms so generated language data stays reviewable.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _locale_file(root: Path, language: str) -> Path:
    candidates = (
        root / "cldr-json" / "cldr-cal-gregorian-full" / "main" / language / "ca-gregorian.json",
        root / "cldr-cal-gregorian-full" / "main" / language / "ca-gregorian.json",
        root / "main" / language / "ca-gregorian.json",
        root / language / "ca-gregorian.json",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"CLDR Gregorian data missing for locale {language!r} below {root}")


def _read(path: Path, language: str, version: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    calendar = payload["main"][language]["dates"]["calendars"]["gregorian"]
    months = calendar.get("months", {})
    weekdays = calendar.get("days", {})
    result: dict[str, Any] = {"language": language, "source": "unicode-cldr", "version": version}
    for kind, values in (("months", months), ("days", weekdays)):
        format_values = values.get("format", {})
        standalone_values = values.get("stand-alone", values.get("standAlone", {}))
        result[kind] = {
            "format": {
                "abbreviated": dict(sorted(format_values.get("abbreviated", {}).items())),
                "wide": dict(sorted(format_values.get("wide", {}).items())),
            },
            "stand_alone": {
                "abbreviated": dict(sorted(standalone_values.get("abbreviated", {}).items())),
                "wide": dict(sorted(standalone_values.get("wide", {}).items())),
            },
        }
    return result


def render(records: list[dict[str, Any]]) -> str:
    body = json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True)
    return body + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cldr-root", type=Path, required=True)
    parser.add_argument("--cldr-version", required=True)
    parser.add_argument("--languages", nargs="+", required=True)
    parser.add_argument(
        "--output", type=Path, default=Path("abbr2words/language_data/cldr_generated.json")
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    records = [
        _read(_locale_file(args.cldr_root, language), language, args.cldr_version)
        for language in sorted(args.languages)
    ]
    generated = render(records)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != generated:
            print(f"CLDR data drift detected: {args.output}")
            return 1
        print(f"CLDR data is up to date: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(generated, encoding="utf-8")
    print(f"wrote deterministic CLDR data: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
