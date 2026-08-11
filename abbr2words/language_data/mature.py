"""Bridge for migrating legacy imperative registries into typed bundles.

The bridge is intentionally isolated: it snapshots the effective legacy
registry once at module import, then the public language class can register
that immutable data through the same path as every other bundled language.
"""

from __future__ import annotations

from .model import AbbreviationSeed, LanguageBundle, SourceRef


def bundle_from_legacy(key: str, legacy_class: type) -> LanguageBundle:
    """Convert one effective legacy class registry to declarative seed data."""
    legacy = legacy_class(enable_context_detection=True)
    source_id = f"legacy-{key}"
    source = SourceRef(
        source_id,
        f"Existing abbr2words {key} registry",
        "docs/language-sources.md",
        "reconstructed-2026-08-10",
    )
    seeds = tuple(
        AbbreviationSeed(
            abbreviation=entry.abbreviation,
            expansion=entry.expansion,
            description=entry.description,
            case_sensitive=entry.case_sensitive,
            aliases=entry.aliases,
            only_if_preceded_by=entry.only_if_preceded_by,
            only_if_followed_by=entry.only_if_followed_by,
            only_if_pos=entry.only_if_pos,
            not_if_pos=entry.not_if_pos,
            context_expansions=(
                dict(entry.context_expansions) if entry.context_expansions is not None else None
            ),
            variants=entry.variants,
            boundary=entry.boundary,
            left_boundary=entry.left_boundary,
            right_boundary=entry.right_boundary,
            source_ids=(source_id,),
            review_note="Behavior-neutral migration snapshot; preserve legacy collision order.",
        )
        for entry in legacy.entries.values()
    )
    labels = {
        entry.canonical_id: entry.expansion
        for entry in legacy.unit_entries
        if entry.canonical_id is not None
    }
    return LanguageBundle(key, seeds, labels, (source,), coverage="extended")


__all__ = ["bundle_from_legacy"]
