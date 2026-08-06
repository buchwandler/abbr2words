# Customization

There are three ways to work with an expander registry.

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

Shared lookup and reset are atomic, while expansion observes a complete
registry snapshot. Applications should still avoid mutating a shared registry
while a long expansion is running.

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
