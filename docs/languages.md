# Languages

The bundled base-language registries are the 49 base keys in the pinned
num2words parity contract:

| Codes                                                            |
| ---------------------------------------------------------------- |
| `am` `ar` `az` `be` `bn` `ca` `ce` `cs` `cy` `da` `de` `en` `eo` |
| `es` `fa` `fi` `fr` `he` `hi` `hu` `hy` `id` `is` `it` `ja` `kn` |
| `ko` `kz` `lt` `lv` `mn` `nl` `no` `pl` `pt` `ro` `ru` `sk` `sl` |
| `sr` `sv` `te` `tet` `tg` `th` `tr` `uk` `vi` `zh`               |

Explicit locale overlays inherit a base registry and are independently keyed:

| Base | Locale overlays                             | num2words parity    |
| ---- | ------------------------------------------- | ------------------- |
| `en` | `en_IN`, `en_NG`                            | v0.5.14             |
| `es` | `es_CO`, `es_CR`, `es_GT`, `es_NI`, `es_VE` | v0.5.14             |
| `fr` | `fr_BE`, `fr_CH`, `fr_DZ`                   | v0.5.14             |
| `pt` | `pt_BR`                                     | v0.5.14             |
| `zh` | `zh_CN`, `zh_HK`, `zh_TW`                   | current master only |

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

## Russian support

Russian (`ru`) accepts both international symbols such as `kg`, `W`, and `Hz` and standard Cyrillic symbols such as `кг`, `Вт`, and `Гц`. These aliases resolve to the same canonical unit identities, so `5 кг` expands to `5 килограмм` and `100 Вт` expands to `100 ватт`. Unit output remains a canonical singular lemma; Russian plural, case, and numeral-government inflection is handled outside `abbr2words`. Ambiguous one-letter abbreviations such as `г.` and `р.` remain unchanged unless a future context mechanism can disambiguate them.

Vietnamese (`vi`) remains in the reviewed baseline tier. Its source-backed rules expand guarded `TP.`, `ĐT`, `SĐT`, and academic-title forms, while legal identifiers and ambiguous uppercase tokens remain unchanged. The common-unit inventory has 38 identity entries and now exposes 38 localized spoken labels; the separate numeric currency identity `VND`/`₫` is `currency-vietnamese-dong`. Coverage reports distinguish unit identities from localized labels.

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

## Japanese support

Japanese (`ja`) keeps unknown initialisms disabled and uses source-backed, structural rules. `№ 12` expands to `番号 12`; parenthesized or compatibility organization forms such as `（株）`, `(有)`, `㈱`, and `㈲` expand to their full company names. Bare kanji such as `番`, `株`, and `有` remain unchanged, as do ordinary forms such as `一番`, `13番10号`, and `頁 12`.

The shared 38-unit inventory has Japanese labels. CLDR-style quantity templates render `20°C` as `摂氏 20 度` and `80 km/h` as `時速 80 キロメートル`. This is a reviewed baseline and source-backed registry, not a claim of complete native-speaker review.

## Thai support

Thai (`th`) provides a source-backed conservative baseline for professional and academic titles, Buddhist and Gregorian eras, date-guarded month abbreviations, and clock-time markers. Common Latin/SI symbols and Thai short forms such as `ม.` and `กม.` resolve to Thai unit labels only with numeric quantity evidence. For example:

```python
from abbr2words import abbr2words

assert abbr2words("ระยะ 5 กม.", lang="th") == "ระยะ 5 กิโลเมตร"
assert abbr2words("27 ส.ค. 2569", lang="th") == "27 สิงหาคม 2569"
```

Ambiguous forms such as `ม.เชียงใหม่` remain unchanged because `ม.` is also the Thai meter symbol. Broader address, administrative, and institution abbreviation coverage still requires native review.

## Mandarin Chinese support

Mainland Chinese (`zh_CN`) is a separate Simplified-Mandarin locale overlay. It localizes the common unit inventory, uses explicit ASCII-token boundaries so reviewed Latin abbreviations can touch Han characters, and expands only the reviewed semantic terms by default. Unknown uppercase identifiers remain unchanged. The `zh_HK` and `zh_TW` overlays remain separate and do not implicitly inherit Mainland terminology.

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

## Coverage tiers and generated inventory

Coverage metadata is checked in with the language bundles and registry shards.
Run `python scripts/generate_registry_snapshot.py` after an intentional data
change and inspect the shard diff.

| Tier              | Base keys                                                                                                         | Content contract                                                                                                   |
| ----------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Reviewed extended | `cs de en es fr it nl pl pt ru sv tr`                                                                             | Mature lexical inventories migrated through declarative bundles with parity snapshots                              |
| Reviewed baseline | `am ar az be bn ca ce cy da eo fa fi he hi hu hy id is ja kn ko kz lt lv mn no ro sk sl sr te tet tg th uk vi zh` | Source-tagged references/titles, bounded numeric guards, localized neutral unit labels, and script-safe boundaries |
| Locale overlay    | 14 explicit locale keys                                                                                           | Base inheritance plus structured numeric identities; no identity lexical currency rules                            |

The detailed generated count table is maintained in
[`docs/language-coverage.md`](language-coverage.md).

Baseline unit labels are neutral surface labels, not plural/case/gender or
numeral-government realization. Consumers that need semantic quantities should
use `iter_unit_matches()` and perform locale grammar downstream.

`DATE` requires nearby numeric date evidence and is deliberately not an
unrestricted parser. Uncased scripts remain conservative without the cased
letter title heuristic; CJK entries do not rely on Latin `\b` behavior.
