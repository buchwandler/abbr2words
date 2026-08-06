#!/usr/bin/env python3
"""Compare abbreviation-only and limited full speech-text normalization."""

from __future__ import annotations

import argparse

from abbr2words import abbr2words, normalize_language

try:
    from examples.abbreviations import TEXT as ENGLISH_TEXT
    from examples.german import TEXT as GERMAN_TEXT
    from examples.speech_numbers import MissingNum2WordsError
    from examples.speech_numbers import normalize_for_speech as _normalize_for_speech
except ModuleNotFoundError:
    from abbreviations import TEXT as ENGLISH_TEXT
    from german import TEXT as GERMAN_TEXT
    from speech_numbers import MissingNum2WordsError
    from speech_numbers import normalize_for_speech as _normalize_for_speech


CZECH_TEXT = "Ing. Novák přijde v po. v 9 hod. na ul. Dlouhé, čp. 12, a přinese 3 kg vzorků."
SPANISH_TEXT = (
    "La Dra. García llegará el lun. 15 de ene. a las 9 h "
    "a la Av. Central nº 12 con 3 kg de muestras."
)
FRENCH_TEXT = (
    "Mme Dupont arrive lun. 15 janv. à 9 h, av. Victor Hugo, n° 12, avec 3 kg de matériel."
)
ITALIAN_TEXT = (
    "La Dott.ssa Rossi arriva lun. 15 gen. alle 9 h in V. Roma n. 12 con 3 kg di campioni."
)
PORTUGUESE_TEXT = (
    "A Dra. Silva chega 2ª, 15 jan. às 9 h na Av. Central n.º 12 com 3 kg de amostras."
)

SAMPLES = {
    "german": ("de", GERMAN_TEXT),
    "english": ("en-us", ENGLISH_TEXT),
    "czech": ("cs", CZECH_TEXT),
    "spanish": ("es", SPANISH_TEXT),
    "french": ("fr", FRENCH_TEXT),
    "italian": ("it", ITALIAN_TEXT),
    "portuguese": ("pt", PORTUGUESE_TEXT),
}


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
