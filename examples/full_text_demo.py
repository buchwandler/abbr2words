#!/usr/bin/env python3
"""Compare abbreviation-only and limited full speech-text normalization."""

from __future__ import annotations

import argparse
import sys
from importlib import import_module
from typing import Any, cast

from abbr2words import abbr2words, normalize_language

_module_prefix = "examples" if __package__ else ""
_scenario = cast(
    Any, import_module(f"{_module_prefix + '.' if _module_prefix else ''}multilingual_scenario")
)
_speech_numbers = cast(
    Any,
    import_module(f"{_module_prefix + '.' if _module_prefix else ''}speech_numbers"),
)
MissingNum2WordsError = _speech_numbers.MissingNum2WordsError
_normalize_for_speech = _speech_numbers.normalize_for_speech

CZECH_TEXT = _scenario.CZECH_TEXT
ENGLISH_TEXT = _scenario.ENGLISH_TEXT
FRENCH_TEXT = _scenario.FRENCH_TEXT
GERMAN_TEXT = _scenario.GERMAN_TEXT
ITALIAN_TEXT = _scenario.ITALIAN_TEXT
PORTUGUESE_TEXT = _scenario.PORTUGUESE_TEXT
SAMPLES = _scenario.SAMPLES
SPANISH_TEXT = _scenario.SPANISH_TEXT


def abbreviation_only(text: str, *, lang: str, context: bool = True) -> str:
    """Return the pure abbreviation-expansion stage."""
    return abbr2words(text, lang=lang, context=context)


def normalize_for_speech(text: str, *, lang: str, context: bool = True) -> str:
    """Return the optional full speech-text stage."""
    return _normalize_for_speech(text, lang=lang, context=context)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Demonstrate abbreviation and speech-text stages.")
    choices = tuple(SAMPLES)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--sample", choices=choices, help="named sample to run")
    group.add_argument("--all", action="store_true", help="run every bundled sample")
    group.add_argument("--text", help="custom text to normalize")
    parser.add_argument("--lang", help="language or locale required with --text")
    parser.add_argument("--no-context", action="store_true")
    parser.add_argument("--stage", choices=("abbr", "full", "both"), default="both")
    parser.add_argument("--compact", action="store_true")
    return parser


def _selected(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> list[tuple[str, str, str]]:
    if args.text is not None:
        if not args.lang:
            parser.error("--lang is required with --text")
        normalize_language(args.lang)
        return [("custom", args.lang, args.text)]
    if args.all:
        return [(name, lang, text) for name, (lang, text) in SAMPLES.items()]
    name = args.sample or "english"
    lang, text = SAMPLES[name]
    return [(name, lang, text)]


def _render(name: str, text: str, lang: str, args: argparse.Namespace) -> str:
    abbreviation = abbreviation_only(text, lang=lang, context=not args.no_context)
    if args.stage == "abbr":
        return abbreviation
    try:
        full = normalize_for_speech(text, lang=lang, context=not args.no_context)
    except MissingNum2WordsError as exc:
        _parser().error(str(exc))
    if args.stage == "full":
        return full
    if args.compact:
        return f"{full}"
    return f"=== Source ===\n{text.strip()}\n\n=== Abbreviations only ===\n{abbreviation.strip()}\n\n=== Full speech text ===\n{full.strip()}"


def main(argv: list[str] | None = None) -> int:
    """Run the unified demonstration CLI."""
    # The bundled samples include characters outside Windows' default CP1252
    # encoding (for example, Czech ``ř``).  Keep CLI output portable across
    # terminals and redirected subprocesses.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")
    parser = _parser()
    args = parser.parse_args(argv)
    selected = _selected(args, parser)
    for index, (name, lang, text) in enumerate(selected):
        if args.compact or args.stage != "both":
            if len(selected) > 1:
                print(f"=== {name} ({lang}) ===")
            print(_render(name, text, lang, args).strip())
        else:
            if index:
                print("\n")
            print(_render(name, text, lang, args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
