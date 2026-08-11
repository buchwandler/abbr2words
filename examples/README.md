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

Locale examples include `pt_BR`, `es_NI`, `fr_CH`, `en_IN`, and `zh_CN`. The
abbreviation stage resolves these keys directly; full number spelling still
depends on the installed optional `num2words` release and may fall back or remain
abbreviation-only when that release lacks a key.

## Abbreviations only

The pure English demonstration uses the exact supplied English sample:

```console
python examples/abbreviations.py
python examples/replacements.py
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

The unified demo presents the same dinner scenario in all seven original
supported languages and abbreviation-only samples for Dutch, Polish, Russian,
Swedish, and Turkish. The standalone `abbreviations.py` script retains the separate
supplied English abbreviation sample:

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

The added language samples currently require the abbreviation-only stage:

```console
python examples/full_text_demo.py --sample dutch --stage abbr
python examples/full_text_demo.py --sample polish --stage abbr
python examples/full_text_demo.py --sample russian --stage abbr
python examples/full_text_demo.py --sample swedish --stage abbr
python examples/full_text_demo.py --sample turkish --stage abbr
```

Every translated source includes a date, time, numeric units, a title, durations,
and a currency amount. The samples preserve semantic parity while using each
locale's reviewed registry spellings.

## Run all languages

`--all --stage abbr` is useful when comparing only the registry behavior:

```console
python examples/full_text_demo.py --all --stage abbr
```

The default sample is English and the default stage is `both`. Use `--stage abbr`, `--stage full`, or `--stage both`; add `--compact` when only the selected
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

## External POS annotations

`examples/spacy_pos.py` demonstrates converting spaCy tokens to
`TokenAnnotation`. Install spaCy and its English pipeline separately when you
want to run it:

```console
python -m pip install spacy
python -m spacy download en_core_web_sm
python examples/spacy_pos.py
```

The package never imports spaCy, and the normal `examples` extra remains limited
to `num2words`.

`replacements.py` demonstrates the exact public planning API for callers that
need replacement spans and metadata. Unit records are marked with
`kind="unit"`; the package expands those symbols but does not spell the number
or select singular/plural grammar.

The abbreviation-only API also covers baseline scripts without requiring a
tokenizer:

```console
python examples/full_text_demo.py --lang ar --text "ص. 12" --stage abbr
python examples/full_text_demo.py --lang sr --text "стр. 12" --stage abbr
python examples/full_text_demo.py --lang zh --text "页 12" --stage abbr
```

RTL, Indic, and CJK rules use explicit source boundaries and guarded context;
the examples do not claim full locale-specific morphology.
