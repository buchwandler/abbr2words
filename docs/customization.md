# Customization

There are three ways to work with an expander registry.

Bundled entries come from checked-in `LanguageBundle` data with source IDs and
review notes. Custom entries are instance-local application policy and do not
need to follow the bundled source ledger. A custom context expansion may use
`DATE`, but ambiguous spellings should still receive an explicit guard;
bundled date detection remains bounded and provider-neutral.

## Isolated registries

`Expander(...)` is a small mutable facade around a new, isolated registry:

```python
from abbr2words import Expander

expander = Expander("en")
expander.add("Tech.", "Technology")
assert expander("Tech. works") == "Technology works"
```

`get_expander(...)` also returns a new isolated implementation registry. Changes
to either form do not affect the shared convenience API.

Entries can be case-sensitive and can use regular-expression guards:

```python
expander.add("in.", "inch", only_if_preceded_by=r"\d\s*$")
expander.add("KI", "Künstliche Intelligenz", case_sensitive=True)
```

Entries use fixed expansion text by default. For reviewed lexical phrases that
should compose with sentence position, opt into sentence casing:

```python
expander.add("Pág.", "página", case_policy="sentence")
assert expander("Pág. 12") == "Página 12"
assert expander("consulte la Pág. 12") == "consulte la página 12"
```

The `sentence` policy uppercases the first cased character only at input or
after sentence-ending punctuation, including an opening quote or bracket that
follows that boundary. A colon is not a sentence boundary. Dotted abbreviation
matches preserve one final period when their consumed dot is sentence-final;
commas, semicolons, and internal dots are not added or moved.

## Per-entry speech strategies

Custom entries keep their semantic expansion and can choose a lexical realization independently:

```python
from abbr2words import get_expander

expander = get_expander("en", registered_initialism_mode="spell")
expander.add("AAR", "after-action review")
expander.add(
    "AO",
    "area of operations",
    speech_strategy="spell_source",
)
expander.add(
    "AAA",
    "anti-aircraft artillery",
    speech_strategy="custom",
    spoken_form="Triple A",
)

assert expander.expand("AAR AO AAA") == "after-action review A O Triple A"
```

`expand` uses the selected semantic expansion. `spell_source` spells the
matched source form when `registered_initialism_mode="spell"` is enabled.
`custom` always uses its non-empty `spoken_form`, independently of the global
registered spelling mode. Custom spoken forms are explicit and are not
sentence-cased; `case_policy` applies to semantic expansions only.

Aliases share the entry's guards and strategy. Source spelling uses the actual
matched alias, while custom realization uses the configured spoken form.
`spoken_form` is required only for `custom` and is rejected for other strategies.

## Bulk glossary registration

Large isolated glossaries can be loaded atomically from typed entries:

```python
from abbr2words import AbbreviationEntry, get_expander

entries = (
    AbbreviationEntry("AAR", "after-action review", origin="custom"),
    AbbreviationEntry(
        "AAA",
        "anti-aircraft artillery",
        speech_strategy="custom",
        spoken_form="Triple A",
        origin="custom",
    ),
)
result = get_expander("en").add_many(entries, on_conflict="error")
assert result.added == 2
```

`add_many()` accepts an `Iterable[AbbreviationEntry]`. It validates the full
batch before changing the registry. `on_conflict="error"` reports canonical
and alias collisions through `AbbreviationConflictError.conflicts`;
`on_conflict="replace"` preserves single-entry replacement behavior and
reports replaced canonical entries. `get_expander()` and `Expander()` create
isolated registries, so custom glossary entries do not affect shared or sibling
expanders.

Build and customize an isolated expander before sharing it for read-only
expansion. Concurrent mutation of the same expander is not supported. This
lexical API does not load profile files and does not normalize dates, times,
numbers, URLs, or general speech text; those responsibilities belong to a
downstream normalizer such as Spokenform.

## Ambiguous English dotted forms

The English registry prefers reversible letter readings when a dotted spelling
could be either a semantic abbreviation or a person's initials. The structural
fallback recognizes standalone uppercase forms with two through eight dotted
letters, such as `E.D.` and `F.C.S.C.J.`, after registered abbreviations and
reviewed units have had priority. Thus lowercase `e.g.` expands to `for example`,
while uppercase `E.G.` is rendered as `E G`; `I.D.` is rendered as `I D`.

Single-letter `N.`, `S.`, `E.`, and `W.` use letter defaults and require bounded
address/street evidence before expanding to a direction. This protects personal
initials and biological names such as `S. aureus`. `D.C.` expands to `District of Columbia` only with explicit Washington/place evidence; `L.A.` remains `L A`
in this layer so author initials are not rewritten as a city name.

Followed-by guards are evaluated against the suffix immediately after the
candidate abbreviation. In `only_if_followed_by=r"^\s*\d"`, `^` therefore
means “immediately after this abbreviation,” even when the candidate occurs
after other source text. Preceded-by guards continue to use their bounded
prefix window.

Registration is validated immediately. Abbreviations and expansions must be
non-empty strings; context keys and values, POS labels, booleans, and guard
patterns have stable type/value checks. Guard regexes are compiled once and
are trusted application configuration; do not pass arbitrary untrusted regex
text because the standard-library engine has no portable timeout.

Boundaries use `(?<!\w)` and `(?!\w)`. Exact case-sensitive custom entries
outrank bundled exact entries and case-insensitive fallbacks, so conflicts do
not depend on registration order. A preceding guard must end immediately before
the abbreviation after horizontal whitespace is removed.

POS guards are optional and are evaluated only when source-aligned annotations
are supplied:

```python
from abbr2words import Expander, TokenAnnotation

expander = Expander("en")
expander.add("Ref.", "Reference", only_if_pos="NOUN")
assert expander.expand("Ref.", annotations=[TokenAnnotation(0, 4, "NOUN")]) == "Reference"
```

Pass a collection when several labels are accepted. A deny constraint wins if
both sets match:

```python
expander.add("Code.", "Code", only_if_pos={"NOUN", "PROPN"}, not_if_pos="PROPN")
```

Structural guards and reviewed numeric unit matching run before POS guards. POS
output is treated as an optional signal; missing labels do not veto an entry,
and a general tagger cannot disable a valid numeric unit expression.

Abbreviation expansion remains lexical. Number/date/decimal/identifier parsing,
article contraction, surrounding grammar, and TTS-oriented rendering belong to
the downstream normalizer, such as `spokenform`.

## Shared registries

`get_shared_expander(...)` returns the process-wide registry used by
`abbr2words(...)`. Shared custom entries therefore affect later calls in the same
process. Shared registries are scoped by both normalized language and context
mode, so `context=True` and `context=False` are separate mutable registries.

```python
from abbr2words import get_shared_expander, reset_expanders

shared = get_shared_expander("de", context=True)
shared.add_custom_abbreviation("KI", "Künstliche Intelligenz")

# Remove shared customizations during test teardown or application reset.
reset_expanders("de")
```

`reset_expanders()` removes all shared language registries, while
`reset_expanders("de")` limits cleanup to one language. Shared state is local to
the current process and is not a synchronization mechanism between threads or
processes; applications should coordinate concurrent mutation themselves.

Shared lookup and reset are atomic. At the start of each expansion, the
expander captures a complete snapshot of its abbreviation entries, unit
overrides, and suppressed-unit set; later mutations affect the next expansion,
not the one already in progress. Applications should still avoid mutating a
shared registry while a long expansion is running because registry mutation is
not itself coordinated with other application-level state.

## Unit customization

Units are a separate reviewed inventory, not ordinary abbreviation entries.
Use the instance-local unit methods when an application needs an override:

```python
expander.set_unit("kg", "custom kilogram")
expander.remove_unit("kg")
```

Calling `add("kg", ...)` or abbreviation removal for a known unit raises a
clear error rather than silently changing a registry that expansion ignores.
Unit overrides do not leak between isolated expanders.

`set_unit()` retains the reviewed canonical ID when replacing a bundled symbol.
Pass `canonical_id="..."` to explicitly assign a different identity, or omit it
for a new user-defined symbol. The optional `category` distinguishes custom
units from currencies or magnitudes. `remove_unit()` accepts either a symbol or
a canonical ID; removing an ID suppresses all bundled aliases for that identity.
The same rules are available through `Expander.iter_unit_matches()`.

For semantic consumers, prefer the structured matcher over parsing replacement
strings. Numeric quantity matching has priority over lexical abbreviation
matching, so numeric `1 Mio.` produces one structured magnitude claim while
standalone `Mio.` retains its ordinary German abbreviation behavior.

## Finite aliases and exact replacements

Bundled entries can have finite aliases for reviewed formatting variants. For
example, the German registry accepts `z.B.`, `z. B.`, `z . b .`, and `zB` with
the same boundary policy and replacement metadata. Aliases are registry data,
not global regular-expression substitutions, so attached strings such as
`pizzaB`, `ModellzB12`, and `du.a.test` remain unchanged.

Use the replacement result when a caller needs semantic provenance or exact
source-aligned edits. `ExpansionResult.replacements` is the authoritative edit
plan; do not reconstruct these edits with a text diff:

```python
result = expander.expand_with_replacements("Prof. Klein, S. 12")
for replacement in result.replacements:
    print(
        replacement.matched_text,
        replacement.start,
        replacement.end,
        replacement.text,
        replacement.rule_id,
        replacement.canonical_id,
    )
```
