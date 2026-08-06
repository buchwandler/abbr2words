# Examples

The examples make two responsibilities visible:

1. `abbr2words(text, lang=...)` expands abbreviations and deliberately leaves
   ordinary numbers, dates, times, currencies, and measurements alone.
2. `examples/speech_numbers.py` is optional demonstration glue that composes
   abbreviation expansion with `num2words` for the supplied speech-text cases.

## Install and run

The abbreviation-only English and German examples need only the package:

```console
python -m pip install abbr2words
python examples/abbreviations.py
python examples/german.py
```

Install the optional dependency for full speech text:

```console
python -m pip install "abbr2words[examples]"
python examples/german.py --full
python examples/full_text_demo.py --sample english
python examples/full_text_demo.py --sample german
python examples/full_text_demo.py --all
```

Use custom text with an explicit language and select a stage:

```console
python examples/full_text_demo.py --lang de --text "Prof. Klein zahlt 42 EUR."
python examples/full_text_demo.py --sample english --stage abbr --compact
python examples/full_text_demo.py --sample german --stage full --compact
```

The unified demo supports `german`, `english`, `czech`, `spanish`, `french`,
`italian`, and `portuguese`. `--sample`, `--all`, and `--text` are mutually
exclusive; `--lang` is required for custom text. The default sample is English
and the default stage is `both`.

## Output and processing

The normal output shows:

```text
=== Source ===
<original text>

=== Abbreviations only ===
<abbr2words output>

=== Full speech text ===
<example-local numeric normalization>
```

Full normalization protects email addresses, URLs, semantic versions, apartment
identifiers such as `4B`, and existing protected-looking tokens. It then handles
currencies, temperatures, dates, times, units, abbreviations, ordinals, and
remaining numbers in that order. It uses `Decimal` for numeric input so currency
cents are not lost.

The rules are intentionally limited demonstration code. They do not promise
perfect grammatical inflection for every locale, arbitrary mathematical or phone
number normalization, every currency convention, or safe rewriting of every
identifier. `abbr2words` remains the reusable abbreviation-only API.

## Third-party dependency

`num2words` is an optional third-party dependency with its own LGPL license. It is
not installed by a plain `abbr2words` installation and is not a core runtime
dependency. The example layer imports it only when full speech-text normalization
is requested.
