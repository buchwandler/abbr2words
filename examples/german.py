#!/usr/bin/env python3
"""Demonstrate German abbreviation-only and full speech-text stages."""

from __future__ import annotations

import argparse

from abbr2words import abbr2words

try:
    from examples.speech_numbers import MissingNum2WordsError, normalize_for_speech
except ModuleNotFoundError:
    from speech_numbers import MissingNum2WordsError, normalize_for_speech


TEXT = (
    "Zum 14.05.2026 um 18:20 Uhr ist das Abendessen geplant. "
    "Für den Auflauf brauchen wir 1,5 kg Kartoffeln, 500 g Quark, "
    "2 Eier, 1 ltr. Milch und ggf. 3 cm mehr Backpapier. "
    'Prof. Klein sagt: "Bitte stelle die Form auf die 2. Schiene, '
    "backe alles für 45 Min. und lass es danach 1 Min. oder auch "
    '2 Min. ruhen." Die Kosten liegen bei ca. 12,80 EUR zzgl. Pfand.'
)


def main() -> int:
    """Run the German example CLI."""
    parser = argparse.ArgumentParser(description="Show German abbreviation and speech stages.")
    parser.add_argument("--full", action="store_true", help="also run optional numeric normalization")
    parser.add_argument("--no-context", action="store_true")
    args = parser.parse_args()
    print("=== Source ===")
    print(TEXT)
    print("\n=== Abbreviations only ===")
    print(abbr2words(TEXT, lang="de", context=not args.no_context))
    if args.full:
        try:
            full = normalize_for_speech(TEXT, lang="de", context=not args.no_context)
        except MissingNum2WordsError as exc:
            parser.error(str(exc))
        print("\n=== Full speech text ===")
        print(full)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
