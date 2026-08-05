# Release notes

## 0.2.0 — first standalone release

This is the first standalone `abbr2words` release. The package extracts the
abbreviation framework and language inventories from `kokorog2p` into an
independently installable, multilingual package.

Highlights:

- Czech, German, English, Spanish, French, Italian, and Portuguese inventories.
- Guarded entries for abbreviations whose meaning depends on nearby text.
- Context-aware expansion for supported entries, with per-call context mode.
- Python API, isolated and shared customization registries, and a command-line interface.
- PEP 561 `py.typed` marker and documented public API.
- Locale normalization and a source-preserving abbreviation-only scope.

Known limitations:

- Some language inventories preserve source-order collision winners rather than
  resolving every ambiguity semantically.
- The shared context detector is mostly English-oriented and is not a complete
  multilingual contextual disambiguator.
- The release remains classified as Alpha; consumers should validate expansions
  for their domain and language data.

The package retains provenance and attribution information in `NOTICE`.
