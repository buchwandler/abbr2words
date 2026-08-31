[![PyPI - Version](https://img.shields.io/pypi/v/abbr2words)](https://pypi.org/project/abbr2words/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/abbr2words)
![PyPI - Downloads](https://img.shields.io/pypi/dm/abbr2words)
[![codecov](https://codecov.io/github/buchwandler/abbr2words/graph/badge.svg?token=VaXeMMGZbh)](https://codecov.io/github/buchwandler/abbr2words)

# abbr2words

Multilingual, context-aware abbreviation expansion for text normalization and speech.

This standalone package was extracted from the abbreviation framework and language
registries in `kokorog2p`. It has no runtime dependencies and uses a flat package
layout (no `src/` directory).

## Supported languages

The registry follows the pinned current-master `num2words` key contract. It has
49 base keys:

`am`, `ar`, `az`, `be`, `bn`, `ca`, `ce`, `cs`, `cy`, `da`, `de`, `en`, `eo`,
`es`, `fa`, `fi`, `fr`, `he`, `hi`, `hu`, `hy`, `id`, `is`, `it`, `ja`, `kn`,
`ko`, `kz`, `lt`, `lv`, `mn`, `nl`, `no`, `pl`, `pt`, `ro`, `ru`, `sk`, `sl`,
`sr`, `sv`, `te`, `tet`, `tg`, `th`, `tr`, `uk`, `vi`, and `zh`.

The 17 explicit locale overlays are `en_GB`, `en_IN`, `en_NG`, `en_US`,
`es_CO`, `es_CR`, `es_GT`, `es_MX`, `es_NI`, `es_VE`, `fr_BE`, `fr_CH`,
`fr_DZ`, `pt_BR`, `zh_CN`, `zh_HK`, and `zh_TW`.

Language resolution trims input, accepts hyphens and underscores, canonicalizes
base/region casing, tries an exact locale first, then falls back to its base.
Thus `pt-BR` resolves to `pt_BR`, `fr_FR` to `fr`, and `en_GB` to its explicit
British-English overlay.
`eo` and `es_NI` are explicit registry keys; `eu` is unsupported. Use
`base_language()` when a caller needs the resolved base key.

Coverage is intentionally tiered rather than uniform:

- **Reviewed extended registries** retain mature bespoke inventories for Czech,
  Dutch, English, French, German, Italian, Polish, Portuguese, Russian,
  Spanish, Swedish, and Turkish.
- **Reviewed baseline registries** provide source-tagged references/titles,
  guarded numeric markers, localized neutral unit labels, and script-specific
  boundaries for the remaining base languages.
- **Locale overlays** inherit their base and add structured numeric identities;
  they do not create ordinary-prose currency rewrites.

`DATE` is a bounded context mode for numeric evidence such as `5 Mar. 2026`,
not a date parser. Uncased scripts do not receive the Latin uppercase-name
heuristic, and CJK lexical rules use explicit boundaries. CLDR 48.2.1 and BIPM
are development/source inputs only; the installed package has no CLDR, Babel,
spaCy, or network runtime dependency.

This is abbreviation and unit support. Optional `num2words` remains a separate
number-verbalization component, and installed releases may support fewer keys
than this registry. No num2words code or runtime dependency is copied here.

## Installation

```bash
python -m pip install abbr2words
```

For development:

```bash
python -m pip install -e ".[dev]"
python -m build
pytest
```

## API

```python
from abbr2words import abbr2words

text = "Prof. Klein kommt ggf. am Fr."
print(abbr2words(text, lang="de"))
# Professor Klein kommt gegebenenfalls am Freitag
```

For downstream consumers that need exact edits and provenance, use the structured
result instead of diffing expanded text:

```python
from abbr2words import abbr2words_with_replacements

result = abbr2words_with_replacements("Prof. Klein", lang="de")
for item in result.replacements:
    print(item.matched_text, item.text, item.rule_id, item.canonical_id)
```

See [the API reference](docs/api.md) for replacement invariants and unit identity.

`matched_text` is the exact consumed source surface. `rule_id` is stable rule
provenance, while `abbreviation` is populated only for a registered lexical
identity; generic initialism fallbacks leave it as `None`. The legacy `source`
field remains provenance metadata and must not be used to recover source text.

Japanese organization abbreviations and localized quantities are handled conservatively:

```python
abbr2words("（株）東京商事は500 MBのデータを5 km先へ送った。", lang="ja")
# 株式会社東京商事は500 メガバイトのデータを5 キロメートル先へ送った。
```

Thai uses a source-backed conservative baseline for titles, eras, dates, times, and localized quantities:

```python
from abbr2words import abbr2words

assert abbr2words("ระยะ 5 กม.", lang="th") == "ระยะ 5 กิโลเมตร"
assert abbr2words("27 ส.ค. 2569", lang="th") == "27 สิงหาคม 2569"
```

Ambiguous forms such as `ม.เชียงใหม่` may remain unchanged even though `ม.` is a Thai abbreviation for university, because numeric quantity context uses the same token for meter. Native review is still recommended for broader Thai administrative and institution abbreviations.

Mainland Chinese (`zh_CN`) uses reviewed semantic abbreviations and localized units:

```python
abbr2words("AI技术需要 16 GB 内存，速度为 5 m/s。", lang="zh_CN")
# "人工智能技术需要 16 吉字节 内存，速度为 每秒5米。"
```

Context can be disabled:

```python
abbr2words("Fr. Klein", lang="de", context=False)
# Freitag Klein
```

## External linguistic annotations

`abbr2words` remains dependency-free. Applications that already tokenize and
tag text can pass provider-neutral `TokenAnnotation` objects with character
offsets and optional POS labels. spaCy is not installed or imported by
`abbr2words`; see the [external POS annotation guide](docs/pos-annotations.md)
and `examples/spacy_pos.py`.
Bundled registries do not currently require POS labels; annotations are used by
custom entries configured with POS guards. The provider-specific `tag` value is
retained as metadata but is not currently evaluated.

Use an isolated mutable registry for project-specific entries:

```python
from abbr2words import Expander

expander = Expander("de")
expander.add("KI", "Künstliche Intelligenz", case_sensitive=True)
print(expander("KI hilft."))
```

A specialist glossary can choose speech realization per entry:

```python
from abbr2words import get_expander

expander = get_expander("en", registered_initialism_mode="spell")
expander.add("AAA", "anti-aircraft artillery", speech_strategy="custom", spoken_form="Triple A")
assert expander.expand("AAA") == "Triple A"
```

Use `add_many()` for an atomic typed batch. Customization remains lexical;
profile serialization and general date, time, and number normalization belong
to a downstream speech application.
Consumers that need the shared language registry can use `get_shared_expander()` and
`reset_expanders()`. `Expander` and `get_expander()` remain isolated mutable registries.

## Command line

```bash
python -m abbr2words --lang de "Prof. Klein kommt ggf."
printf 'Prof. Klein kommt ggf.' | abbr2words --lang de
```

## Scope

`abbr2words` expands registered abbreviations and a reviewed set of unit symbols
when they occur after numeric quantities. It preserves numeric values and does
not spell ordinary numbers, dates, or times, and does not perform unit conversion
or currency realization. Unit support is not universal UCUM support. Use the
public `iter_unit_matches()` API when a downstream semantic normalizer needs the
original numeric lexeme, source span, and stable canonical quantity identity.

Reviewed initialisms that represent spelling are rendered with source graphemes,
including German `GmbH` as `G m b H` and `AG` as `A G`. A small set of ambiguous
one-letter unit symbols (`B`, `A`, and `K`) requires separation from the numeric
value, so identifier-like forms such as `7B`, `3A`, and `5K` remain available to
downstream structured-code handling while `7 B`, `3 A`, and `300 K` remain units.
Use `iter_unit_diagnostics()` when a caller needs to distinguish an accepted unit
claim from a compact candidate rejected by that policy.

English dotted forms are handled conservatively when a spelling can be either a
semantic abbreviation or a person's initials. Uppercase dotted initialisms such
as `E.D.` and `F.C.S.C.J.` fall back to source-letter spelling only when no
registered rule wins; lowercase `e.g.` remains `for example`, while uppercase
`E.G.` is letter-spelled. Single-letter compass forms expand to directions only
with bounded address/street evidence, and `D.C.`/`L.A.` remain letter-spelled in
author names. This lexical layer does not parse dates, numbers, URLs, versions,
or product identifiers; those belong to a downstream speech normalizer.

Unknown undotted uppercase initialisms are preserved by default. A downstream
speech normalizer that has already reserved its structured spans can opt into a
bounded residual fallback. `conservative_undotted` is the recommended
middle-ground; it spells only high-confidence residual shapes and fails closed
for headlines, lexical acronyms, ambiguous words, Roman numerals, and
identifiers. The existing `spell_undotted` mode remains an intentionally broad
explicit opt-in:

```python
abbr2words("BBC News", initialism_mode="spell_undotted")
# "B B C News"

abbr2words(
    "BBC PDF",
    initialism_mode="spell_undotted",
    initialism_case="lower",
)
# "b b c p d f"

abbr2words("NGO WORLD FIRST", initialism_mode="conservative_undotted")
# "N G O WORLD FIRST"
```

`initialism_case` (`source`, `upper`, or `lower`) controls rendering separately
from detection. Conservative fallback accepts only high-confidence standalone
ASCII uppercase tokens of three through six letters, skips Roman-like,
identifier, headline, lexical-acronym, and ambiguous-word candidates, and
leaves protected spans unchanged. Registered semantic entries continue to
win; `registered_initialism_mode="spell"` is a separate opt-in that applies only
to reviewed entries tagged for source spelling. These options are available in
v0.2.7 and remain backward-compatible for callers using the default policy.

The reviewed registry owns a small, audited set of common initialisms such as
`BBC`, `CBS`, `US`, `UK`, `USA`, `ISBN`, `HTML`, `ISO`, `IEC`, `TV`, `NFL`,
`NHL`, and `MLB`. These entries use `speech_strategy="spell_source"` and emit
source graphemes in the default mode. Lexical acronyms such as `NASA`, `NATO`,
`FIFA`, and `UNESCO`, ordinary uppercase words, stock tickers, and unknown
codes remain unchanged in conservative mode unless a caller explicitly selects
broad undotted spelling. Reviewed replacements report stable
`abbr:<canonical>` provenance; the generic dotted, conservative, and broad
undotted fallbacks report `abbr:initialism`, `abbr:initialism-conservative`, and
`abbr:initialism-undotted`. Use `iter_initialism_diagnostics()` when a caller
needs candidate reasons, decisions, source offsets, or registered entry ids
without inferring policy from generated text.

For benchmark review workflows, the repository also ships a maintenance helper
that groups unresolved candidate tokens from fresh failure reports without
changing runtime behavior:

```bash
python scripts/report_initialism_candidates.py failures.jsonl
python scripts/report_initialism_candidates.py failures.json --format json
```

The helper accepts JSONL or JSON failure rows with source text, language,
expected output, and optional actual output. It reuses the current
`conservative_undotted` diagnostics and registry data to report grouped tokens,
locales, diagnostic reasons, Roman/vowel/two-letter flags, registry coverage,
uppercase-run/protection flags, and sample source sentences. This is intended
for reviewed initialism triage after rerunning benchmark suites; it does not
introduce a new matching engine or broaden fallback recognition.

`abbr2words` recognizes and identifies quantity symbols; it does not decide how
a complete numeric quantity is spoken. Number words, grammatical number,
currency major/minor decomposition, and locale-specific spoken decimal policy
belong to the consuming speech normalizer.

Structured currency identities are available in the reviewed quantity registry
for Czech, English, French, Italian, Portuguese, and Spanish. The shared
inventory also recognizes JPY, CHF, INR, KRW, and MXN. Czech recognizes
`Kč`/`CZK` as `currency-czech-koruna`; Portuguese also recognizes
`R$`/`BRL` as `currency-brazilian-real`; English, French, Italian, and Spanish
recognize the shared `currency-euro`, `currency-us-dollar`, and
`currency-pound-sterling` identities for EUR/USD/GBP. In `es_MX`, unqualified
`$` resolves to `currency-mexican-peso`, while `US$` and `USD` remain
`currency-us-dollar`. These identities are numeric-context-only.
These identities are recognized when a numeric value is adjacent in either
prefix or suffix position:

```python
from abbr2words import iter_unit_matches

match = next(iter_unit_matches("12,80 EUR", "it"))
match.value  # "12,80"
match.canonical_id  # "currency-euro"
match.canonical_symbol  # "€"
```

The match preserves the written numeric lexeme, symbol, and source-relative
offsets. Currency names, number wording, singular/plural agreement, gender,
cents, decimal realization, and arithmetic remain the responsibility of the
downstream speech normalizer; standalone currency symbols and codes are not
lexical rewrites. The reviewed shared inventory is limited to EUR/USD/GBP.

```python
abbr2words("500 g", lang="en")
# "500 gram"

abbr2words("section g", lang="en")
# "section g"
```

## Examples

The repository includes runnable examples for abbreviation-only expansion and
for composing `abbr2words` with `num2words`:

```console
python -m pip install "abbr2words[examples]"
python examples/abbreviations.py
python examples/full_text_demo.py --sample german
```

`abbr2words` itself expands abbreviations only. The optional examples show how
to combine it with `num2words` for broader speech-text normalization, including
output such as `500 g -> five hundred grams`. The full-text demo is example code,
not part of the stable public API. See
[`examples/README.md`](examples/README.md) for the complete command reference.

## Versioning

The package version is derived from Git tags by `setuptools-scm`. Use tags in the
form `v<version>`; the corresponding package version is generated automatically
during builds. A checkout without tags falls back to `0+unknown`.

For a release, commit the changes, create an annotated tag, and build from that
tag:

```bash
git tag -a v<version> -m "Release <version>"
git push origin v<version>
python -m build
```

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.
