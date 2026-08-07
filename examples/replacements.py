#!/usr/bin/env python3
"""Show exact source-aligned abbreviation and unit replacement metadata."""

from __future__ import annotations

from abbr2words import abbr2words_with_replacements


def main() -> int:
    """Print expanded text and selected original-source replacements."""
    result = abbr2words_with_replacements("Prof. Klein, S. 12; 2 kg", lang="de")
    print(result.text)
    for replacement in result.replacements:
        source = result.source_text[replacement.start : replacement.end]
        print(
            f"{source!r} [{replacement.start}:{replacement.end}] -> "
            f"{replacement.text!r} ({replacement.kind}, {replacement.rule})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
