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

Context policy is language-specific and uses bounded local windows. English
profiles distinguish street suffixes, saints, titles, and addresses; the German
profile distinguishes `Fr. Müller` (`Frau`) from `Am Fr.` (`Freitag`). Name
evidence uses Unicode cased characters and supports accents, apostrophes,
hyphens, and quoted names. Uncased scripts remain conservative without an
annotation signal. Context-aware output is still not a comprehensive semantic
disambiguator, so applications should review domain-specific entries.

Uppercase undotted initialisms such as English time zones, `BCE`, `CE`, and
`MIT` are case-sensitive. This prevents ordinary lowercase words from being
rewritten; reviewed title-case and lexical abbreviations retain their own
registry policy.
