# Spokenform Review: Lessons from Recent `semidark/misaki` Commits

**Prepared for:** coding agent  
**Date reviewed:** 2026-08-29  
**Primary target:** `spokenform` reconstructed from the supplied Codecrate snapshot  
**Secondary ownership dependency:** `abbr2words` reconstructed from the supplied Codecrate snapshot  
**Upstream reviewed:** `https://github.com/semidark/misaki`, branch `main`

---

## 1. Executive decision

The recent Misaki work is useful as a **behavioral regression corpus and design review**, but it should **not** be transplanted as a German normalizer.

Spokenform already has a substantially better architecture for this problem:

- typed semantic candidates instead of one monolithic substitution pass;
- source-aligned `Replacement` objects and offset mapping;
- protected spans;
- precedence between dates, phones, legal references, identifiers, quantities, and other sequence types;
- explicit recognition domains;
- contextual vs surface interpretation modes;
- real Gregorian date validation;
- locale-aware numeric parsing through `numeric_lexeme.py`;
- number wording delegated to `num2words` rather than maintained as a second handwritten German number engine;
- ordinary abbreviation ownership delegated to `abbr2words`.

The Misaki commits do, however, expose several edge cases worth acting on.

### Recommended outcome

Implement a **small German hardening release**, not a new normalization subsystem.

Priority order:

1. **Fix the `Uhr` word-boundary bug in German time recognition.**
2. **Make German date/ordinal context matching token-boundary-safe.**
3. **Stop silently discarding currency fractional precision beyond two digits.**
4. **Add typed German `§§` plural legal-reference support.**
5. **Add regression coverage for Misaki-derived edge cases that Spokenform already handles correctly.**
6. **Optionally add missing ordinary German abbreviations to `abbr2words`, not Spokenform.**
7. **Do not port Misaki's handwritten large-number table, generic grouped-phone regex, pronunciation override lexicon, or global text-cleanup strategy.**

This should be a targeted correctness/robustness change and can fit in a patch/minor Spokenform release depending on whether the currency behavior is treated as a bug fix or visible output change.

---

## 2. Upstream scope reviewed

As of 2026-08-29, the newest commits returned for `semidark/misaki` are from 2026-06-21. The German normalization series is the relevant upstream work.

Reviewed commits:

| Commit | Date | Theme | Spokenform relevance |
|---|---|---|---|
| `9cda926` | 2026-06-21 | merge of German edge-case fixes | summary only |
| `6282a95` | 2026-06-21 | preserve invalid German times | already architecturally covered |
| `a84ddb6` | 2026-06-21 | phone groups, `§§`, percent, case-insensitive date prefix | partially useful |
| `d57a0e0` | 2026-06-21 | `gem.`, `Abs.`, `§` legal abbreviations | ownership lessons |
| `96bcebb` | 2026-06-21 | context-inflected German full dates | already stronger in Spokenform, but test gaps remain |
| `c4a09fa` | 2026-06-21 | large-number table | **do not port** |
| `c7c58cb` | 2026-06-21 | arbitrary-length ordinals and `am` context | already supported in Spokenform |
| `0291f6a` | 2026-06-21 | Billion, ordinal stems, `ein Euro` / `ein Cent` | partially useful as tests |
| `746595e` | 2026-06-20 | `HH:MM` minute/word-boundary tightening | directly relevant |
| `40bb6c1` | 2026-05-12 | Decimal currency arithmetic, invalid-time preservation, `Uhr` boundary | directly relevant as regression source |
| `3e7b637` | 2026-04-17 | avoid duplicated `Uhr` | Spokenform already consumes normal trailing `Uhr` |
| `25e3f2f` | 2026-06-20 | German pronunciation override lexicon | downstream G2P concern; not Spokenform |
| `a6a0fd4` | 2026-04-17 | whitespace/token lexicon lookup fixes | testing principle only |
| `2a380c4` | 2026-04-17 | offline model behavior | not relevant to text normalization |

Useful upstream URLs:

- `https://github.com/semidark/misaki/commit/6282a95c852842f84305f6c7fc420a7582b7a843`
- `https://github.com/semidark/misaki/commit/a84ddb684bd6142d4b161381ca3bd38c0faf3131`
- `https://github.com/semidark/misaki/commit/d57a0e0aac875916d3ce88400b763a37584ef561`
- `https://github.com/semidark/misaki/commit/96bcebb6bf1057a54b05edb3656019e22763a3c6`
- `https://github.com/semidark/misaki/commit/c4a09fa72cc2910ca87463113986c33114fd63ed`
- `https://github.com/semidark/misaki/commit/c7c58cbd39469d7977668f91fda93db22adea5de`
- `https://github.com/semidark/misaki/commit/0291f6aea8cf1cddc053f1631073855852d53a2f`
- `https://github.com/semidark/misaki/commit/40bb6c11e6fea6c18a08c6d1c3a0972d3f291f8c`

Misaki is Apache-2.0 licensed, like Spokenform. Even so, the recommended implementation below is based on behavior and Spokenform's existing abstractions; there is no reason to import the monolithic Misaki implementation.

---

## 3. Current Spokenform architecture relevant to this review

The reconstructed Spokenform snapshot already divides responsibility correctly.

### `spokenform/locales/de.py`

Owns reviewed German realization of:

- dates;
- text dates;
- date ranges;
- times and time ranges;
- currencies;
- temperatures;
- quantities recognized by `abbr2words`;
- labels;
- contextual ordinals.

Important current patterns/functions:

- `_DATE`
- `_TEXT_DATE`
- `_TIME`
- `_TIME_RANGE`
- `_CURRENCY_PREFIX`
- `_CURRENCY_SUFFIX`
- `_ORDINAL`
- `_ending()`
- `_ordinal()`
- `_currency()`
- `_iter_de_dates()`
- `_iter_de_times()`
- `_iter_de_currency_temperature()`
- `_iter_de_labels()`

### `spokenform/recognizers/sequences.py`

Already owns shared typed sequence semantics such as:

- phones;
- percentages;
- legal references;
- identifiers;
- versions;
- sports scores;
- formulas;
- other specialist sequence classes.

Relevant current functions/data:

- `_phone_is_plausible()`
- `_phone_context()`
- `_phone_text()`
- `_percent_text()`
- `_LEGAL_GERMAN_PARAGRAPH_VALUE_RE`
- `_LEGAL_GERMAN_ARTICLE_VALUE_RE`
- `_LEGAL_GERMAN_ROMAN_VALUE_RE`
- `_LEGAL_PREFIX_VALUE_RE`
- `_LEGAL_GENERIC_VALUE_RE`
- `_render_german_paragraph()`
- `_render_german_article()`
- `_render_german_roman()`
- `_render_prefixed_paragraph()`
- `_render_generic_legal()`
- `_legal_text()`

### `spokenform/numeric_lexeme.py`

Already centralizes locale punctuation and exact numeric lexeme parsing. This is preferable to Misaki's ad-hoc `float`/regex conversion path.

### `spokenform/dates.py`

Already provides real calendar validation via `datetime.date`, which is stronger than checking only `day <= 31` and `month <= 12`.

### `spokenform/number_words.py`

Already delegates German cardinal/ordinal rendering to `num2words`. Do not create another German integer-to-words implementation inside Spokenform.

### `spokenform/config.py`

Already supports semantic domain policy:

- `RecognitionDomain.TEMPORAL`
- `RecognitionDomain.FINANCE`
- `RecognitionDomain.COMMUNICATIONS`
- `RecognitionDomain.LEGAL`
- etc.

This is an important advantage over a monolithic normalizer and must be preserved.

### `abbr2words`

The supplied snapshot already owns many German ordinary abbreviations, including examples such as:

- `Abs.` -> `Absatz`
- `Tel.` -> `Telefon`
- `Tel. Nr.` -> `Telefonnummer`
- `Nr.`
- `Str.`
- `Prof.`
- `Dr.`
- `GmbH`
- `AG`

`gem.` and `Abt.` were not found in the current German registry during this review.

---

## 4. Transfer matrix: what to learn and what not to copy

| Misaki change | Spokenform state | Decision |
|---|---|---|
| Reject invalid `25:00` / `23:99` as times | `_TIME` only matches 00-23 and 00-59; tests already cover `25:99` and `24:00` | **Already better** |
| Preserve invalid time text through later number passes | typed candidate model naturally leaves unmatched text alone | **Do not copy placeholder mechanism** |
| Add `\b` after `Uhr` | Spokenform currently lacks the boundary after optional `Uhr` | **Adopt immediately** |
| Avoid duplicate `Uhr` | normal `"14:30 Uhr"` is already consumed as one German time candidate | **Keep + add regression** |
| Contextual date ordinal suffixes | Spokenform `_ending()` already covers more contexts | **Keep architecture; harden boundary matching** |
| Real date validity | Spokenform uses `datetime.date` | **Already better** |
| Arbitrary-size ordinals | Spokenform `_ORDINAL` uses `\d+` | **Already supported** |
| Handwritten Million/Milliarde/Billion/Trillion | Spokenform uses `num2words` | **Reject** |
| `ein Euro`, not `eins Euro` | Spokenform already special-cases major unit 1 | **Already supported** |
| `ein Cent`, not `eins Cent` | Spokenform currently omits the minor-unit noun in German currency style | **Do not force output-style change without a deliberate contract decision** |
| Decimal-based currency rounding | Spokenform already parses decimals exactly, but truncates minor digits to two | **Adapt: preserve source precision; do not silently round** |
| Generic grouped-phone regex | Spokenform has contextual/plausibility recognition and precedence | **Reject broad recognizer; add German tests instead** |
| `§` / `§§` speech | Spokenform has typed single-paragraph/legal patterns but no clear plural `§§` list grammar | **Adopt as typed legal grammar** |
| `gem.` / `Abs.` | `Abs.` already in `abbr2words`; `gem.` absent | **Add missing ordinary abbreviations to `abbr2words`** |
| `%` -> `Prozent` | shared sequence percent renderer already has German `Prozent` | **Already supported; add test** |
| Quote conversion to ASCII | Spokenform is text normalization, not a downstream espeak cleanup pass | **Do not copy globally** |
| Pronunciation override JSON | phoneme/G2P concern | **Out of scope for Spokenform** |
| Longest phrase override matching | interesting G2P technique but not needed for existing semantic candidate pipeline | **No action** |

---

# 5. P0: fix German `Uhr` word-boundary handling

## Problem

Current German patterns contain optional trailing `Uhr` without a word boundary:

```python
_TIME = re.compile(
    r"(?<!\d)(?P<hour>[01]?\d|2[0-3]):(?P<minute>[0-5]\d)(?:\s+Uhr)?(?!\d)"
)
```

and `_TIME_RANGE` has equivalent trailing `Uhr` shapes.

This can match the `Uhr` prefix of a longer word.

Example:

```text
Um 14:30 Uhrzeit beginnt es.
```

The optional group can consume ` Uhr` and leave `zeit`, producing a malformed result analogous to the Misaki regression:

```text
Um vierzehn Uhr dreißigzeit beginnt es.
```

Misaki explicitly added a boundary test for this class.

## Required change

In `spokenform/locales/de.py`, require a word boundary after literal `Uhr`.

Conceptually:

```diff
- (?:\s+Uhr)?
+ (?:\s+Uhr\b)?
```

Apply the same principle to both branches of `_TIME_RANGE`.

Do **not** use Misaki's placeholder approach for invalid times. Spokenform does not need it because invalid hours/minutes never become time candidates in the first place.

## Decide separately whether compact `14:30Uhr` is supported

Current Spokenform requires whitespace before `Uhr`.

Do not silently change `\s+` to `\s*` in the same patch unless compact time spelling is a deliberate supported form.

Recommended first patch:

- preserve existing whitespace contract;
- add only `\b`.

A later enhancement can explicitly test and document `14:30Uhr` if desired.

## Tests

Add to `tests/test_de_structured.py`:

```python
def test_german_time_does_not_consume_prefix_of_uhrzeit() -> None:
    result = prepare("Um 14:30 Uhrzeit beginnt es.", language="de", use_spacy=False)
    assert "dreißigzeit" not in result.spoken_text
    assert "Uhrzeit" in result.spoken_text
```

Also add:

```python
@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("14:30 Uhr", "vierzehn Uhr dreißig"),
        ("14:30", "vierzehn Uhr dreißig"),
        ("24:00 Uhr", "24:00 Uhr"),
        ("23:99 Uhr", "23:99 Uhr"),
    ],
)
def test_german_time_boundaries_and_invalid_values(source: str, expected: str) -> None:
    assert prepare(source, language="de", use_spacy=False).spoken_text == expected
```

If punctuation preservation means the exact final strings differ, assert on the semantic fragment and replacement rules rather than weakening the validity checks.

## Acceptance criteria

- normal times still produce one `de.time` replacement;
- trailing ordinary `Uhr` is not duplicated;
- `Uhrzeit`, `Uhrwerk`, etc. are not partially consumed;
- invalid times remain source text;
- offset maps remain correct;
- no temporary placeholder strings are introduced.

---

# 6. P0: make German date/ordinal context detection token-boundary-safe

## Problem

Spokenform is already more sophisticated than Misaki for German inflection, but `_ending()` currently uses raw string suffix checks:

```python
if prefix.endswith(("am", "im", "vom", ...)):
    return "en"
...
if prefix.endswith(("ans", "ins", "die", "das", ...)):
    return "e"
```

This is easy to read, but it does not prove that the matched context is a complete token/phrase.

A word that merely ends with one of the context strings can become accidental grammatical evidence.

The risk is especially relevant because `_ending()` is shared by:

- full numeric dates;
- day/month forms;
- hyphen dates;
- date ranges;
- text dates;
- mixed text dates;
- ordinary dotted ordinals.

Misaki's recent date changes use explicit word-level prefix matching. Spokenform should retain its richer context set, but tighten the matcher.

## Required refactor

Replace raw `str.endswith()` evidence with an explicitly bounded context helper.

Suggested shape:

```python
_DE_ORDINAL_ENDING_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"(?:^|\s)(?:am|im|vom|zum|zur|bis|auf der|an der|in dem|in den|auf den)$"
        ),
        "en",
    ),
    (
        re.compile(r"(?:^|\s)(?:ans|ins|die|das|auf die|der)$"),
        "e",
    ),
    (
        re.compile(r"(?:^|\s)(?:ihren|deren)$"),
        "en",
    ),
)
```

Then `_ending()` should normalize whitespace and search these patterns.

The exact implementation may use token extraction rather than one regex; the key requirement is **whole-context boundaries**.

## Regression matrix

Add full-date tests, not only standalone ordinal tests.

Suggested cases:

```text
am 14.05.2026
im 05.2026          # only if currently recognized as a date shape; otherwise do not add
vom 14.05.2026
zum 14.05.2026
der 14.05.2026
auf die 2. Schiene
auf der 7. Etage
zur 6. Version
```

Also add negative boundary cases to prove accidental suffixes do not influence inflection.

Example concept:

```text
... <ordinary word ending in a context-like substring> 14.05.2026
```

Choose natural German examples after checking the exact tokenizer-free prefix behavior.

## Do not blindly adopt Misaki's bare-date suffix

Misaki changed bare `DD.MM.YYYY` rendering toward an `-er` ordinal form. Spokenform's current test contract includes:

```text
03.01.2026 -> dritte Januar zweitausendsechsundzwanzig
```

Changing bare-date grammatical style is a separate product decision and may affect benchmarks.

This review does **not** recommend changing that output merely to match Misaki.

---

# 7. P0: stop losing currency fractional precision

## Finding

Misaki's `€9,999 -> zehn Euro` test highlights a real policy question.

Misaki resolves it by rounding to the nearest cent using `Decimal`.

Spokenform is already exact in numeric parsing, but German `_currency()` currently does:

```python
cents = int((fraction + "00")[:2])
```

That means a source such as:

```text
9,999 EUR
```

can silently lose the third fractional digit.

The same two-digit slicing pattern exists in several locale currency renderers, so this should be considered a cross-locale semantic policy issue, not just a German special case.

## Why copying Misaki's rounding is not recommended

Text normalization should normally preserve what the caller wrote.

Implicitly converting:

```text
9,999 EUR
```

to:

```text
zehn Euro
```

changes the numeric value.

That is appropriate in an accounting/payment formatting function if rounding has been requested, but it is surprising in a source-faithful TTS normalization layer.

## Recommended policy

For a currency whose reviewed renderer assumes two minor-unit digits:

- 0 fractional digits: render major unit normally;
- 1-2 fractional digits: use the existing reviewed currency realization;
- more than 2 fractional digits: **do not truncate or round silently**.

Preferred implementation choices, in order:

### Option A — exact decimal speech + currency name

Keep the candidate atomic, but preserve every fractional digit.

Example conceptual output:

```text
9,999 EUR
-> neun Komma neun neun neun Euro
```

This is the preferred choice if a natural, source-faithful rendering is straightforward.

### Option B — fail closed for the specialized currency decomposition

Return `None` from the specialized currency renderer when `len(fraction) > 2`, allowing a lower-level exact number path and ordinary currency abbreviation expansion to handle the source.

This is acceptable only if tests prove the composed downstream result is correct and source-aligned.

### Avoid

- truncating to `99`;
- rounding to `10,00`;
- silently deleting extra digits.

## Suggested internal abstraction

Consider centralizing the policy instead of fixing only `de.py`.

For example:

```python
@dataclass(frozen=True, slots=True)
class CurrencyFractionPolicy:
    minor_digits: int = 2
    excess_mode: Literal["decimal", "reject"] = "decimal"
```

This does not need to become public API yet.

At minimum, add one shared helper that makes excess precision explicit.

## Tests

German:

```text
1 EUR      -> ein Euro
2 EUR      -> zwei Euro
0,05 EUR   -> existing contract: null Euro fünf
12,50 EUR  -> existing contract: zwölf Euro fünfzig
9,999 EUR  -> must preserve all three fractional digits somehow
€9,999     -> same semantic result as suffix form
```

Also add one negative assertion:

```python
assert "neun Euro neunundneunzig" != result.spoken_text
```

and, if using exact decimal speech:

```python
assert "neun Komma neun neun neun Euro" == result.spoken_text
```

Add equivalent focused tests to another comma-decimal locale and a point-decimal locale before extracting a shared helper.

## Minor-unit noun style

Misaki explicitly emits `Cent` and fixes `eins Cent` -> `ein Cent`.

Spokenform's current German contract intentionally renders:

```text
12,50 EUR -> zwölf Euro fünfzig
0,05 EUR  -> null Euro fünf
```

Do not introduce `Cent` in this patch unless the output contract is deliberately changed.

If a later API needs explicit major/minor nouns, make it an explicit rendering policy rather than an incidental consequence of this fix.

---

# 8. P1: add typed German plural paragraph (`§§`) recognition

## Finding

Misaki added:

```text
§§ -> Paragrafen
```

Spokenform already has a much better location for this feature: the legal sequence recognizer.

Current legal support includes single German references such as:

```text
§ 12 BGB
§ 823 Abs. 1 BGB
StVO § 1
Art. ... Abs. ...
```

and tests already assert atomic typed legal rendering.

A raw global substitution of `§§` is therefore the wrong implementation.

## Recommended scope

Add a dedicated German plural-paragraph candidate in `spokenform/recognizers/sequences.py`.

Start conservatively with reviewed shapes:

```text
§§ 12, 13 BGB
§§ 12 und 13 BGB
§§ 12-14 BGB
§§ 12–14 BGB
```

Possible spoken forms:

```text
Paragrafen zwölf, dreizehn B G B
Paragrafen zwölf und dreizehn B G B
Paragrafen zwölf bis vierzehn B G B
```

The exact punctuation in spoken text should follow existing sequence style.

## Suggested architecture

Add a specific regex before generic legal matching, e.g. conceptually:

```python
_LEGAL_GERMAN_PARAGRAPH_LIST_RE = ...
```

and a dedicated renderer:

```python
def _render_german_paragraph_list(value: str, language: str) -> str | None:
    ...
```

Insert it into `_LEGAL_RENDERERS` before generic legal handling.

Keep it:

- German-only;
- atomic;
- source-aligned;
- inside `RecognitionDomain.LEGAL`;
- higher precedence than generic number/range candidates.

## Do not over-generalize in the first patch

Do not immediately try to parse arbitrary nested legal grammar such as:

```text
§§ 12, 14 Abs. 2, 15 Abs. 3 Satz 2 BGB
```

Support a narrow reviewed grammar first.

## Tests

Add to `tests/test_identifiers.py` or preferably split legal sequence tests into a focused file if the existing test cluster is becoming too broad.

Required:

```python
def test_german_plural_paragraph_list_is_atomic() -> None:
    result = prepare("§§ 12, 13 BGB", language="de", use_spacy=False)
    assert ...
    assert any(item.rule == "sequence.legal" for item in result.source_replacements)
```

Also assert that no overlapping:

- numeric range;
- phone;
- generic sequence fallback;

wins the same source span.

Add range case:

```text
§§ 12–14 BGB
```

and malformed negatives:

```text
§§
§§ foo
```

These should fail closed.

---

# 9. P1: ordinary legal/business abbreviations belong in `abbr2words`

Misaki added `gem.` and `Abs.` directly inside its German normalizer.

Spokenform should preserve its existing ownership boundary.

## Current supplied `abbr2words` state

During reconstruction/inspection:

- `Abs.` is already present and expands to `Absatz`.
- `Tel.` is present and expands to `Telefon`.
- `Tel. Nr.` is present.
- `GmbH`, `AG`, `Nr.`, `Str.`, `Prof.`, `Dr.` are already represented.
- `gem.` was not found.
- `Abt.` was not found.

## Recommendation

If these are desired:

```text
gem. -> gemäß
Abt. -> Abteilung
```

add them to the German `abbr2words` registry with conservative contextual rules.

Do **not** duplicate the same abbreviation mapping in `spokenform/locales/de.py`.

### `gem.` caution

`gem.` can be ambiguous outside legal/administrative prose.

Before adding it broadly:

- search benchmark corpora for occurrences;
- define punctuation/case behavior;
- add false-positive tests;
- consider whether the expansion should be unconditional or context-conditioned.

### `Abt.`

`Abt.` -> `Abteilung` is less semantically risky, but still belongs in `abbr2words`.

## Dependency sequencing

If `abbr2words` is changed first:

1. release the corresponding `abbr2words` version;
2. bump Spokenform's minimum dependency only if required;
3. add Spokenform integration tests that exercise the released behavior;
4. do not vendor the entries into Spokenform as a temporary duplicate.

---

# 10. P1: use Misaki phone changes only as regression input

Misaki added a broad grouped-number regex and reads matching groups digit-by-digit.

Spokenform already has a substantially safer phone recognizer:

- `_phone_is_plausible()`;
- `_phone_context()`;
- locale-specific `_PHONE_POLICIES`;
- `_phone_text()`;
- precedence against ISBN/date/range/identifier candidates.

## Recommendation

Do **not** add Misaki's generic grouped-phone regex.

Instead, add German coverage to prove current behavior.

Suggested positive cases:

```text
Telefon 030 12345678
Tel. 030 12345678
Telefonnummer 030 12345678
+49 30 12345678
```

Suggested ambiguous/negative cases:

```text
Bestellung 030 12345678
Artikel 030 12345678
Version 030 12345678
```

For the ambiguous cases, decide from current recognition policy whether a long, clearly phone-shaped grouped number can be accepted without a phone label. The goal is not necessarily to reject all of them; the goal is to **document and test the intended evidence threshold**.

Also retain precedence tests proving that:

- ISBN wins over phone;
- dates win over phone;
- legal references win over phone;
- phone wins over generic numeric ranges when appropriate.

---

# 11. P1: add explicit German percent regression coverage

Misaki added `% -> Prozent`.

Spokenform already has shared percent rendering:

```python
"de": "Prozent"
```

in `_percent_text()`.

No implementation change is required unless tests reveal a regression.

Add German tests for:

```text
25%       -> fünfundzwanzig Prozent
12,5%     -> zwölf Komma fünf Prozent
-1,2%     -> minus eins Komma zwei Prozent
```

Also test spacing variants if supported:

```text
25 %
```

The expected source span should remain one typed `sequence.percent` replacement.

---

# 12. P1: large-number tests, but do not port Misaki's table

## Important upstream warning

Misaki's current handwritten scale table contains forms such as:

```text
1_000_000       -> "eine Millionen"
1_000_000_000_000 -> "eine Billionen"
1_000_000_000_000_000 -> "eine Trillionen"
```

This is not a table Spokenform should import.

There are two problems:

1. singular labels in the table are pluralized for some scales;
2. German long-scale naming makes `10^15` a **Billiarde**, while a **Trillion** is `10^18`.

Earlier Misaki tests in the same series expected `1_000_000_000_000 -> eine Billion`, which illustrates how quickly a local handwritten number engine can regress.

## Spokenform approach is preferable

Keep number-language ownership in `num2words`.

Add regression tests at scale boundaries to detect dependency changes:

```text
1_000_000
1_000_000_000
1_000_000_000_000
```

Use actual supported source formatting, for example German grouped forms:

```text
1.000.000
1.000.000.000
1.000.000.000.000
```

Verify expected German long-scale words.

If `num2words` output differs from desired product wording, solve that through a small reviewed post-render policy or accepted benchmark alternatives—not by replacing the backend with a handwritten recursive converter.

---

# 13. P1: ordinal regression coverage above two digits

Misaki expanded ordinal matching from one/two digits to arbitrary digits and special-cased stems around 100 and 1000.

Spokenform already uses:

```python
_ORDINAL = re.compile(r"(?<![\w.])(?P<number>\d+)\.(?=\s+[A-Za-zÄÖÜäöüß])")
```

so the recognizer is already arbitrary-length.

Add tests to lock this in:

```text
am 100. Tag
der 100. Versuch
am 1000. Tag
```

Do not force Misaki's exact `"hundertst"` / `"tausendst"` stem algorithm into Spokenform.

Let `num2words` remain the linguistic backend unless a benchmark demonstrates a specific unacceptable output.

If multiple natural German forms are acceptable, encode them as benchmark alternatives rather than increasing core normalization complexity.

---

# 14. P2: add a Misaki-derived German regression corpus

The most useful upstream artifact is the **test idea set**.

Create a focused local test module such as:

```text
tests/test_de_misaki_regressions.py
```

or integrate into existing semantically appropriate files if test-file proliferation is undesirable.

Suggested corpus:

## Time

```text
14:00 Uhr
14:30 Uhr
14:30
0:00 Uhr
24:00 Uhr
25:00 Uhr
23:99 Uhr
14:30 Uhrzeit
```

## Dates

```text
am 24.12.2024
Am 3.10.1990
der 14.05.2026
vom 14.05.2026
31.02.2026
29.02.2025
29.02.2024
```

Spokenform should outperform Misaki here by using real calendar validity.

## Currency

```text
€1
1 EUR
€0,01
0,05 EUR
€9,99
€9,999
1.234 EUR
```

The `9,999` case should explicitly prove no digit is discarded.

## Legal

```text
§ 12 BGB
§ 823 Abs. 1 BGB
StVO § 1
§§ 12, 13 BGB
§§ 12–14 BGB
```

## Phone

```text
Telefon 030 12345678
Tel. 030 12345678
+49 30 12345678
```

## Percent

```text
25%
12,5%
```

## Large numbers

```text
1.000.000
1.000.000.000
1.000.000.000.000
```

## Ordinals

```text
am 3. Tag
der 3. Versuch
am 100. Tag
am 1000. Tag
```

---

# 15. Add provenance and precedence assertions, not only output strings

A major Spokenform advantage is exact semantic provenance. Misaki's tests mostly check final strings.

For new tests, also assert ownership.

Examples:

```python
result = prepare("§§ 12, 13 BGB", language="de", use_spacy=False)
assert any(item.rule == "sequence.legal" for item in result.source_replacements)
```

For phone:

```python
assert any(item.rule == "sequence.phone" for item in result.source_replacements)
```

For percent:

```python
assert any(item.rule == "sequence.percent" for item in result.source_replacements)
```

For time:

```python
assert any(item.rule == "de.time" for item in result.source_replacements)
```

For a malformed time:

```python
assert not any(item.rule == "de.time" for item in result.source_replacements)
```

For every new atomic grammar, assert that conflicting recognizers do not also claim the same source.

This is more valuable than copying Misaki's sequential-regex behavior.

---

# 16. Add domain-policy tests

Because Spokenform supports `RecognitionDomain`, every new or hardened sequence should preserve policy behavior.

For `§§`:

- enabled normally;
- suppressed when `RecognitionDomain.LEGAL` is disabled;
- enabled when `allowed_domains={RecognitionDomain.LEGAL}`;
- no replacement leakage into generic number handling that changes the intended source.

For phones:

- honor `COMMUNICATIONS`.

For times:

- honor `TEMPORAL`.

For currency:

- honor `FINANCE`.

This prevents a localized feature patch from bypassing the newer interpretation-mode/domain architecture.

---

# 17. Add surface/contextual mode tests where relevant

The changes should not accidentally broaden contextual recognition.

### Safe surface semantics

- syntactically valid German time;
- explicit `%`;
- explicit `§§`;
- explicit currency symbol/code.

### Context-sensitive semantics

- ambiguous phone-like digit groups.

For phone tests, assert differences between:

```python
InterpretationMode.SURFACE
InterpretationMode.CONTEXTUAL
```

only if the existing recognition policy classifies that specific shape as contextual.

Do not change evidence classifications just to match Misaki.

---

# 18. Documentation updates

## `docs/languages.md`

After implementation, clarify German structured coverage:

- validated digital times;
- context-sensitive German date/ordinal inflection;
- legal `§` and `§§` references if implemented;
- contextual phone sequences via shared recognizer;
- exact currency handling policy for excess fractional precision.

## `README.md`

Keep high-level wording only.

Do not add a long Misaki comparison.

If currency excess precision changes, document that Spokenform preserves written precision instead of silently rounding/truncating.

## `docs/changelog.md`

Suggested entries:

### Fixed

- Prevented German time recognition from consuming `Uhr` as a prefix of longer words such as `Uhrzeit`.
- Made German ordinal/date context suffix matching require whole context tokens.
- Prevented German currency normalization from discarding fractional digits beyond the reviewed minor-unit precision.

### Added

- Added typed German plural paragraph-list/range rendering for `§§` references.
- Added German regression coverage derived from public TTS normalizer edge cases.

Only include entries for work actually completed.

---

# 19. Benchmark strategy

Do not optimize specifically for Misaki output.

Use the upstream changes to add adversarial examples to the existing benchmark/gold workflow.

Recommended categories:

```text
de/time-boundary
de/time-invalid
de/date-inflection
de/date-invalid-calendar
de/currency-excess-precision
de/legal-paragraph-plural
de/phone-grouped
de/percent
de/large-number-scale
de/ordinal-large
```

For each new case, record whether the expected result is:

- canonical;
- accepted alternative;
- preserve/fail-closed.

Especially for:

- bare numeric dates;
- German 100th/1000th ordinal wording;
- currency minor-unit style;

prefer accepted alternatives if multiple forms are linguistically reasonable and downstream TTS-equivalent.

---

# 20. File-by-file implementation plan

## Spokenform

### `spokenform/locales/de.py`

Required:

1. Add `\b` after optional `Uhr` in `_TIME`.
2. Add `\b` after optional `Uhr` in both `_TIME_RANGE` branches.
3. Refactor `_ending()` to use whole-token/whole-phrase context evidence.
4. Update `_currency()` so fractional digits beyond two are never silently truncated.

Do not:

- add a second `_int_to_de` implementation;
- globally replace legal symbols;
- add ordinary prose abbreviation dictionaries.

### `spokenform/recognizers/sequences.py`

Required if `§§` support is accepted:

1. add conservative German plural-paragraph list/range regex;
2. add dedicated typed renderer;
3. register before generic legal renderer;
4. preserve `sequence.legal` rule ownership;
5. keep legal domain classification;
6. prove precedence against ranges/phones/generic sequences.

No broad phone-regex change is recommended.

### `spokenform/numeric_lexeme.py`

Prefer no German-specific change.

If currency excess-precision policy is shared across locales, introduce a small generic helper/model here or in a dedicated currency helper module only if that keeps ownership clear.

Do not overload numeric parsing with currency grammar.

### `spokenform/dates.py`

No implementation change required for this Misaki review.

Its Gregorian validation is already a strength.

### `spokenform/number_words.py`

No implementation change required.

Add dependency regression tests elsewhere rather than implementing German scale logic here.

### `tests/test_de_structured.py`

Add:

- `Uhrzeit` boundary;
- valid/invalid time matrix;
- date prefix inflection matrix;
- large ordinals;
- excess-precision currency cases;
- large-number boundaries if this is the preferred home.

### `tests/test_identifiers.py` or a new legal-focused test file

Add:

- `§§` list/range;
- atomic ownership;
- precedence assertions.

### `tests/test_sequence_precedence.py`

Add:

- German grouped phone vs date/legal/identifier negatives as needed;
- plural legal reference precedence.

### Docs

Update:

- `docs/languages.md`
- `docs/changelog.md`
- README only if public contract wording changed.

---

# 21. `abbr2words` follow-up plan

Only needed if ordinary abbreviation gaps are accepted.

### `abbr2words/languages/de.py`

Review adding:

```text
gem. -> gemäß
Abt. -> Abteilung
```

Do not duplicate `Abs.`; it already exists.

Add:

- direct expansion tests;
- punctuation boundary tests;
- case behavior tests;
- false-positive tests;
- registry parity snapshot updates if required by project tooling.

If `gem.` requires legal/administrative context that `abbr2words` cannot express safely under its current conservative rules, leave it caller-managed rather than making Spokenform globally replace it.

---

# 22. Testing commands for the coding agent

After changes, run at least:

```bash
python -m pytest tests/test_de_structured.py -q
python -m pytest tests/test_identifiers.py -q
python -m pytest tests/test_sequence_precedence.py -q
python -m pytest tests/test_interpretation_modes.py -q
python -m pytest
```

Then:

```bash
ruff check .
mypy spokenform
```

Run the project's benchmark/gold gates relevant to German if locally available.

For `abbr2words` changes, run its full test suite independently before bumping Spokenform's dependency.

---

# 23. Suggested exact regression tests

The following is intentionally close to executable pytest and can be adapted to existing helper style.

```python
def test_german_time_does_not_consume_uhrzeit_prefix() -> None:
    result = prepare(
        "Um 14:30 Uhrzeit beginnt es.",
        language="de",
        use_spacy=False,
    )
    assert "dreißigzeit" not in result.spoken_text
    assert "Uhrzeit" in result.spoken_text


@pytest.mark.parametrize("source", ["24:00", "25:00", "23:99", "25:99"])
def test_german_invalid_time_is_not_claimed(source: str) -> None:
    result = prepare(source, language="de", use_spacy=False)
    assert source in result.spoken_text
    assert not any(item.rule == "de.time" for item in result.source_replacements)


@pytest.mark.parametrize(
    ("source", "fragment"),
    [
        ("am 14.05.2026", "am vierzehnten Mai"),
        ("vom 14.05.2026", "vom vierzehnten Mai"),
        ("der 14.05.2026", "der vierzehnte Mai"),
    ],
)
def test_german_full_date_uses_bounded_context_inflection(
    source: str,
    fragment: str,
) -> None:
    result = prepare(source, language="de", use_spacy=False)
    assert fragment in result.spoken_text


def test_german_currency_does_not_drop_excess_fraction_digits() -> None:
    result = prepare("9,999 EUR", language="de", use_spacy=False)
    # Choose the exact expected contract during implementation.
    # The essential invariant is source-value preservation.
    assert "neunundneunzig" not in result.spoken_text or "Komma" in result.spoken_text
    assert "9,999" not in result.spoken_text or not any(
        item.rule == "de.currency" for item in result.source_replacements
    )


def test_german_plural_legal_reference_is_atomic() -> None:
    result = prepare("§§ 12, 13 BGB", language="de", use_spacy=False)
    assert result.spoken_text.startswith("Paragrafen")
    assert any(item.rule == "sequence.legal" for item in result.source_replacements)
    assert not any(
        item.rule in {"sequence.phone", "sequence.numeric-range"}
        for item in result.source_replacements
    )


def test_german_percent_uses_shared_percent_renderer() -> None:
    result = prepare("25%", language="de", use_spacy=False)
    assert result.spoken_text == "fünfundzwanzig Prozent"
    assert any(item.rule == "sequence.percent" for item in result.source_replacements)
```

The currency assertion above should be replaced with a strict exact expectation once Option A vs Option B from section 7 is chosen.

---

# 24. False-positive checklist

Before merging, explicitly test that the changes do not create these regressions.

## Time

- `Uhrzeit`
- `Uhrwerk`
- version-like colon forms;
- sports scores such as `1:2`;
- MAC addresses;
- malformed minute widths.

## Ordinals/dates

- dotted decimals;
- version numbers;
- sentence-final cardinals;
- words whose suffix merely resembles `am`, `im`, `die`, etc.;
- invalid dates such as 31 February;
- non-leap-year 29 February.

## Currency

- identifiers ending with `EUR`;
- values with more precision than minor units;
- grouped numbers;
- negative values;
- dot vs comma decimal input according to German numeric punctuation policy.

## Legal

- double section sign without numbers;
- arbitrary symbol runs;
- ranges unrelated to legal context;
- `§` inside protected/URL-like text.

## Phone

- ISBN;
- date;
- software version;
- product code;
- legal citation;
- ordinary numeric range.

---

# 25. What not to change

The coding agent should explicitly avoid the following scope creep.

1. **Do not depend on Misaki.**
2. **Do not copy `misaki/de.py` into Spokenform.**
3. **Do not add phoneme overrides to Spokenform.**
4. **Do not add espeak-specific cleanup rules.**
5. **Do not normalize German quotes to ASCII as part of this change.**
6. **Do not replace `num2words` with handwritten German number code.**
7. **Do not broaden phone detection just because a digit sequence has spaces/hyphens.**
8. **Do not silently round currency values.**
9. **Do not duplicate `abbr2words` abbreviation ownership in locale modules.**
10. **Do not weaken protected-span or provenance behavior.**
11. **Do not bypass recognition-domain policy.**
12. **Do not change bare-date grammatical style merely for Misaki parity.**

---

# 26. Recommended implementation sequence

## Phase A — correctness bug fixes

1. Fix `Uhr\b` in `_TIME`.
2. Fix `Uhr\b` in `_TIME_RANGE`.
3. Add time boundary/invalid regressions.
4. Refactor `_ending()` to bounded context patterns.
5. Add date/ordinal context regressions.
6. Fix currency excess-fraction precision semantics.
7. Add exact currency regression tests.

Run full Spokenform tests.

## Phase B — narrow feature addition

1. Add `§§` German legal list/range grammar.
2. Add precedence/provenance/domain tests.
3. Add German phone and percent regression tests.
4. Add large-number/ordinal dependency regressions.

Run full tests and benchmarks.

## Phase C — `abbr2words` follow-up

1. Review `gem.` and `Abt.` ownership.
2. Add only safe entries.
3. Release `abbr2words`.
4. Update Spokenform minimum dependency only if necessary.
5. Add integration tests.

## Phase D — docs and release

1. update language matrix;
2. update changelog;
3. run ruff/mypy/pytest;
4. run German benchmark/gold cases;
5. confirm no output changes outside reviewed cases.

---

# 27. Release recommendation

### If only time boundary + context boundary fixes are merged

Treat as a patch-level correctness release.

### If currency excess precision changes

Still defensible as a bug fix because current behavior can lose source digits, but it is observable output behavior. Call it out prominently in changelog/release notes.

### If `§§` support is added

This is a backward-compatible capability addition. Patch vs minor depends on the project's current versioning convention.

No major-version change is justified by this Misaki review.

---

# 28. Final recommendation

Use Misaki as an **adversarial upstream test source**, not as an implementation source.

The highest-value changes are small:

- one regex-boundary correction for `Uhr`;
- one safety refactor for context endings;
- one source-preservation correction for currency precision;
- one typed `§§` legal grammar;
- a focused regression suite.

Spokenform's current architecture is already better suited to safe text normalization than Misaki's sequential German replacement function. The goal should therefore be to **tighten the existing abstractions**, not to increase regex volume or duplicate language logic.

The Misaki history itself reinforces this: several consecutive commits fix interactions introduced by a monolithic pass (invalid-time placeholders, `Uhr` prefix consumption, inflection, broad phone matching, handwritten number scales). Spokenform should keep using typed recognition, precedence, fail-closed behavior, external number backends, and explicit ownership boundaries.

---

## Appendix A — concrete current Spokenform behaviors already covered by tests

The reconstructed snapshot already tests German examples including:

```text
03.01.2026 -> dritte Januar zweitausendsechsundzwanzig
am 3. Tag -> am dritten Tag
der 3. Versuch -> der dritte Versuch
auf die 2. Schiene -> auf die zweite Schiene
14:05 -> vierzehn Uhr fünf
01:00 Uhr -> ein Uhr
25:99 -> preserved
24:00 -> preserved
31.02.2026 -> preserved
29.02.2025 -> preserved
3°C -> drei Grad Celsius
-1,2 °F -> minus eins Komma zwei Grad Fahrenheit
12,50 EUR -> zwölf Euro fünfzig
EUR 12,50 -> zwölf Euro fünfzig
1.234 EUR -> eintausendzweihundertvierunddreißig Euro
CHF 12,80 -> zwölf Schweizer Franken achtzig
.02 -> null Komma null zwei
,02 -> null Komma null zwei
§ 12 BGB -> Paragraf zwölf B G B
§ 823 Abs. 1 BGB -> Paragraf ... Absatz eins B G B
StVO § 1 -> S T V O Paragraf eins
```

This is why the Misaki review should result in hardening, not replacement.

---

## Appendix B — source ownership rule

Use this rule when deciding where a new case belongs:

| Case | Owner |
|---|---|
| ordinary abbreviation (`Abs.`, `Tel.`, potentially `Abt.`) | `abbr2words` |
| exact numeric lexeme parsing | `spokenform/numeric_lexeme.py` |
| German date/time/currency grammatical realization | `spokenform/locales/de.py` |
| phone, legal reference, percent, identifier sequence | shared Spokenform recognizers |
| semantic precedence / domains | Spokenform structured policy |
| pronunciation / phonemes / brand overrides | downstream G2P, not Spokenform |
| lexical/semantic evidence | `lexhint` integration, not a replacement for recognition grammar |

This ownership boundary should remain the main architectural constraint for implementation.
