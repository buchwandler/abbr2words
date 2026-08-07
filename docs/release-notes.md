# Release notes

## Unreleased

- Added conservative Dutch, Polish, Russian, Swedish, and Turkish abbreviation
  and numeric-unit registries with ISO aliases.
- Refactored localized unit data around canonical unit IDs and added flexible
  horizontal whitespace matching for Russian multiword abbreviations.
- Documented Turkish case-sensitive matching, restricted apostrophe-suffix unit
  policy, and lemma-only morphology limits.
- Added provider-neutral source-aligned `TokenAnnotation` support.
- Added optional entry-level POS allow/deny guards.
- Planned unit and abbreviation replacements against original offsets and
  apply them right-to-left for stable external annotation alignment.
- Exposed those planned replacements through immutable public result models,
  including distinct metadata for unit matches.
- Added finite German formatting aliases for common compound abbreviations and
  corrected relative anchored followed-by guards.
- Clarified that quantity verbalization and grammatical number remain the
  caller's structured-stage responsibility.
- Preserved the sentence-final `in.` regression while retaining numeric inch
  expansion.
- Added no runtime dependency; spaCy remains separately installed and used only
  by the integration example.
- Added a tested spaCy token adapter example without adding spaCy to runtime or
  example dependencies.
- Clarified that POS guards currently apply to configured custom entries;
  bundled registries remain structurally guarded.
