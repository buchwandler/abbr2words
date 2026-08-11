"""Generate the checked-in language coverage table."""

from __future__ import annotations

from pathlib import Path

from abbr2words import get_expander, supported_languages
from abbr2words.units import unit_entries

EXTENDED = frozenset({"cs", "de", "en", "es", "fr", "it", "nl", "pl", "pt", "ru", "sv", "tr"})


def render() -> str:
    rows = [
        "# Generated language coverage",
        "",
        "Do not edit this table manually; run `python scripts/generate_language_coverage.py`.",
        "",
        "| Code | Base/locale | Lexical entries | Contextual entries | Unit identities | Source status | Notes |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for language in supported_languages():
        expander = get_expander(language)
        entries = tuple(expander.entries.values())
        base = language.split("_", 1)[0]
        tier = (
            "reviewed extended"
            if base in EXTENDED
            else ("locale overlay" if "_" in language else "reviewed baseline")
        )
        contextual = sum(1 for entry in entries if entry.context_expansions)
        rows.append(
            f"| `{language}` | `{base}` / {'locale' if '_' in language else 'base'} | "
            f"{len(entries)} | {contextual} | {len(unit_entries(language))} | "
            f"{tier} | neutral labels; source ledger applies |"
        )
    return "\n".join(rows) + "\n"


def main() -> int:
    output = Path("docs/language-coverage.md")
    output.write_text(render(), encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
