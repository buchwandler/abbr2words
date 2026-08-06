# Release notes

## Unreleased

- Added provider-neutral source-aligned `TokenAnnotation` support.
- Added optional entry-level POS allow/deny guards.
- Planned unit and abbreviation replacements against original offsets and
  apply them right-to-left for stable external annotation alignment.
- Preserved the sentence-final `in.` regression while retaining numeric inch
  expansion.
- Added no runtime dependency; spaCy remains separately installed and used only
  by the integration example.
- Added a tested spaCy token adapter example without adding spaCy to runtime or
  example dependencies.
- Clarified that POS guards currently apply to configured custom entries;
  bundled registries remain structurally guarded.
