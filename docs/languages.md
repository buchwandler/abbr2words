# Languages

The bundled base-language registries are:

| Code | Language   |
| ---- | ---------- |
| `cs` | Czech      |
| `de` | German     |
| `en` | English    |
| `es` | Spanish    |
| `fr` | French     |
| `it` | Italian    |
| `nl` | Dutch      |
| `pl` | Polish     |
| `pt` | Portuguese |
| `ru` | Russian    |
| `sv` | Swedish    |
| `tr` | Turkish    |

Language input is normalized by trimming whitespace, lowercasing, accepting both
hyphens and underscores, and taking the base part of a locale. For example,
`de-DE`, `en_GB`, and `pt-BR` select `de`, `en`, and `pt`. Common three-letter
aliases and `cz` for Czech are also accepted, including `dut`/`nld`, `pol`,
`rus`, `swe`, and `tur` for the added registries.

The added registries are intentionally conservative. Ambiguous short forms are
guarded by numeric/name context or omitted, Russian multiword abbreviations
accept ordinary, non-breaking, and narrow non-breaking spaces, and Turkish
lexical entries are case-sensitive. Unit output is a canonical singular lemma;
the stable API does not realize plural, case, numeral-government, or suffix
morphology.

## Known ambiguity

Some inventories contain collisions whose effective winner follows the source
registry order rather than a complete contextual model. Current documented
examples include `str.` in Czech, `mar.` in Spanish and Italian, `n°` in French,
and `seg.` in Portuguese. German `Fr.` has an explicit title-context override,
but its default expansion remains `Freitag`.

The context detector is shared across languages and is currently mostly oriented
around English address, name, saint, and time signals. The package is therefore
context-aware for supported entries, not a comprehensive multilingual semantic
disambiguator. Applications should review ambiguous domain-specific entries
before relying on an expansion as authoritative.
