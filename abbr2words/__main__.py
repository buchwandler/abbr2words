"""Command-line interface for ``python -m abbr2words``."""

from __future__ import annotations

import argparse
import sys

from .api import abbr2words, supported_languages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Expand abbreviations in text")
    parser.add_argument("text", nargs="?", help="Text to expand; stdin is used when omitted")
    parser.add_argument("-l", "--lang", default="en", help="Language or locale code")
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="Disable contextual disambiguation",
    )
    parser.add_argument(
        "--languages",
        action="store_true",
        help="Print supported languages and exit",
    )
    args = parser.parse_args(argv)

    if args.languages:
        print("\n".join(supported_languages()))
        return 0

    text = args.text if args.text is not None else sys.stdin.read()
    try:
        print(abbr2words(text, lang=args.lang, context=not args.no_context))
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
