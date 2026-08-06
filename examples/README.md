# Examples

## What these examples demonstrate

These scripts show the boundary between abbreviation expansion and broader
speech-text normalization:

- `abbr2words` owns abbreviation expansion.
- `num2words` owns number-to-word conversion.
- `speech_numbers.py` contains intentionally limited glue for dates, times,
  currencies, temperatures, measurement units, ordinals, and ordinary numbers.

The examples run from a checkout without pykokoro, Kokoro model downloads, audio
libraries, a GPU, or network access. They print text to stdout and never generate
audio.

## Install

For abbreviation-only examples, install the package normally:

```console
python -m pip install abbr2words
```

For full speech-text normalization:

```console
python -m pip install -e ".[examples]"
```

`num2words` is an optional third-party dependency distributed under the LGPL and
is not part of the core runtime dependencies.

## Abbreviations only

The pure English demonstration uses the exact supplied English sample:

```console
python examples/abbreviations.py
python examples/abbreviations.py --compact
python examples/abbreviations.py --lang en-gb --no-context
```

Its full output has `Source` and `Abbreviations only` sections. The compact form
prints only the expanded text. This stage does not silently normalize numbers,
dates, times, currencies, or units.

## Full speech text

The German example shows both stages and enables the optional full stage with
`--full`:

```console
python examples/german.py
python examples/german.py --full
python examples/german.py --no-context
```

The unified demo supports the exact English and German texts and additional Czech,
Spanish, French, Italian, and Portuguese samples:

```console
python examples/full_text_demo.py --sample english
python examples/full_text_demo.py --sample german
python examples/full_text_demo.py --sample czech
python examples/full_text_demo.py --sample spanish
python examples/full_text_demo.py --sample french
python examples/full_text_demo.py --sample italian
python examples/full_text_demo.py --sample portuguese
python examples/full_text_demo.py --all
```

## Run all languages

`--all --stage abbr` is useful when comparing only the registry behavior:

```console
python examples/full_text_demo.py --all --stage abbr
```

The default sample is English and the default stage is `both`. Use `--stage
abbr`, `--stage full`, or `--stage both`; add `--compact` when only the selected
result is wanted.

## Use your own text

Custom text requires an explicit language:

```console
python examples/full_text_demo.py --lang de --text "Prof. Klein kommt am 14.05.2026."
python examples/full_text_demo.py --lang en --text "The CEO paid $12.80." --stage full
```

`--sample`, `--all`, and `--text` are mutually exclusive. Full mode without
`num2words` reports:

```text
Full-text normalization requires the examples extra:
python -m pip install "abbr2words[examples]"
```

## Scope and limitations

The numeric layer protects email addresses, URLs, version strings, apartment
identifiers such as `4B`, and existing placeholder-looking tokens before applying
rules. It uses `Decimal`, not floating-point parsing, for decimal and currency
values. The rule order is protected spans, currencies, temperatures, dates, times,
units, abbreviations, ordinals, remaining numbers, and restoration.

This is readable demonstration glue, not a universal text normalizer. Locale
grammar, arbitrary identifiers, mathematical expressions, phone numbers, and
every currency/date convention are outside its promise. The stable package API
continues to expand abbreviations only.

## Third-party dependency notice

`num2words` is optional and has its own LGPL license. The Apache-2.0 license of
`abbr2words` is unchanged; installing the examples extra installs the separate
third-party package for the demonstration layer.
