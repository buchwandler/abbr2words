# Languages

The bundled base-language registries are the 49 base keys in the pinned
num2words parity contract:

| Codes |
| ----- |
| `am` `ar` `az` `be` `bn` `ca` `ce` `cs` `cy` `da` `de` `en` `eo` |
| `es` `fa` `fi` `fr` `he` `hi` `hu` `hy` `id` `is` `it` `ja` `kn` |
| `ko` `kz` `lt` `lv` `mn` `nl` `no` `pl` `pt` `ro` `ru` `sk` `sl` |
| `sr` `sv` `te` `tet` `tg` `th` `tr` `uk` `vi` `zh` |

Explicit locale overlays inherit a base registry and are independently keyed:

| Base | Locale overlays | num2words parity |
| ---- | --------------- | ---------------- |
| `en` | `en_IN`, `en_NG` | v0.5.14 |
| `es` | `es_CO`, `es_CR`, `es_GT`, `es_NI`, `es_VE` | v0.5.14 |
| `fr` | `fr_BE`, `fr_CH`, `fr_DZ` | v0.5.14 |
| `pt` | `pt_BR` | v0.5.14 |
| `zh` | `zh_CN`, `zh_HK`, `zh_TW` | current master only |

Language input is normalized by trimming whitespace, accepting both hyphens and
underscores, canonicalizing base/region casing, and trying the exact registered
locale before falling back to its base. For example, `pt-BR` selects `pt_BR`,
`fr_FR` selects `fr`, and `en_GB` selects `en`. Common verified three-letter
aliases and `cz` for Czech remain accepted. `eo` and `es_NI` are explicit keys;
`eu` is not supported.

The added registries are intentionally conservative. Ambiguous short forms are
guarded by numeric/name context or omitted, Russian multiword abbreviations
accept ordinary, non-breaking, and narrow non-breaking spaces, and Turkish
lexical entries are case-sensitive. Unit output is a canonical singular lemma;
the stable API does not realize plural, case, numeral-government, or suffix
morphology.

English, French, Italian, Portuguese, and Spanish structured quantities recognize
the reviewed shared currency identities `€`/`EUR`, `$`/`USD`, and `£`/`GBP` in
either numeric-prefix or numeric-suffix position. Portuguese additionally
recognizes `R$`/`BRL` as `currency-brazilian-real`, while Czech recognizes
`Kč`/`CZK` as `currency-czech-koruna`. These matches preserve the written
numeric lexeme, source offsets, written symbol, language, category, and stable
canonical ID; they do not speak the amount or choose locale-specific currency
grammar.
Downstream consumers such as `spokenform` own that semantic realization.

French dotted duration forms `min.` and `sec.` are context-sensitive structured
quantity aliases. A numeric match consumes the complete dotted symbol, while
standalone lexical `min.` continues to expand as `minimum`; numeric context is
what selects the duration identity. Sentence punctuation is rendered by the
generic abbreviation layer, and French number grammar remains downstream.

German quantity symbols include the reviewed electrical and frequency forms
`kWh`, `Wh`, `mAh`, `mA`, `GHz`, `MHz`, `kHz`, `Hz`, `W`, and `V`, plus `Stck.`,
`ltr.`, `Tsd.`, `Mio.`, `Mrd.`, and `EUR`. Case-sensitive metadata is preserved:
for example, `2 mA` matches but `2 ma` does not. Dotted German aliases and
their base symbols share canonical IDs, so `h`/`Std.`, `min`/`Min.`, and
`l`/`Ltr.` cannot acquire separate semantic identities.

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
