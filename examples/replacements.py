#!/usr/bin/env python3
"""Show exact source-aligned abbreviation and unit replacement metadata."""

from __future__ import annotations

from abbr2words import abbr2words_with_replacements


def main() -> int:
    """Print expanded text and complete source-aligned replacement metadata."""
    source = "Prof. Klein, S. 12; 2 kg"
    result = abbr2words_with_replacements(source, lang="de")
    print(result.text)
    for replacement in result.replacements:
        print(
            f"[{replacement.start}:{replacement.end}] "
            f"matched={replacement.matched_text!r} "
            f"replacement={replacement.text!r} "
            f"kind={replacement.kind} "
            f"language={replacement.language} "
            f"rule_id={replacement.rule_id} "
            f"canonical_id={replacement.canonical_id} "
            f"context={replacement.context!r}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
