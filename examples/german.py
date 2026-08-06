#!/usr/bin/env python3
"""Demonstrate German abbreviation-only and full speech-text stages."""

from __future__ import annotations

import argparse
import sys
from importlib import import_module
from typing import Any, cast

from abbr2words import abbr2words

_module_prefix = "examples" if __package__ else ""
_scenario = cast(
    Any, import_module(f"{_module_prefix + '.' if _module_prefix else ''}multilingual_scenario")
)
GERMAN_TEXT = _scenario.GERMAN_TEXT

_speech_numbers = cast(
    Any,
    import_module(f"{_module_prefix + '.' if _module_prefix else ''}speech_numbers"),
)
MissingNum2WordsError = _speech_numbers.MissingNum2WordsError
normalize_for_speech = _speech_numbers.normalize_for_speech
normalize_numbers_for_speech = _speech_numbers.normalize_numbers_for_speech


TEXT = GERMAN_TEXT


def main() -> int:
    """Run the German example CLI."""
    # Keep redirected CLI output portable across terminals and platforms.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Show German abbreviation and speech stages.")
    parser.add_argument(
        "--full", action="store_true", help="also run optional numeric normalization"
    )
    parser.add_argument("--no-context", action="store_true")
    args = parser.parse_args()
    print("=== Source ===")
    print(TEXT)
    print("\n=== Abbreviations only ===")
    abbreviations = abbr2words(TEXT, lang="de", context=not args.no_context)
    print(abbreviations)
    if args.full:
        try:
            abbreviations_with_num2words = normalize_numbers_for_speech(
                abbreviations,
                lang="de",
            )
            full = normalize_for_speech(TEXT, lang="de", context=not args.no_context)
        except MissingNum2WordsError as exc:
            parser.error(str(exc))
        print("\n=== Abbreviations + num2words ===")
        print(abbreviations_with_num2words)
        print("\n=== Full speech text ===")
        print(full)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
