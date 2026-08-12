"""Generic expander for declarative language bundles."""

from __future__ import annotations

from abbr2words.core import AbbreviationEntry, AbbreviationExpander
from abbr2words.language_data import LanguageBundle


def register_bundle(expander: AbbreviationExpander, bundle: LanguageBundle) -> None:
    """Register a bundle through the normal validated entry path."""
    for seed in bundle.abbreviations:
        expander.add_abbreviation(
            AbbreviationEntry(
                abbreviation=seed.abbreviation,
                expansion=seed.expansion,
                context_expansions=(
                    dict(seed.context_expansions) if seed.context_expansions is not None else None
                ),
                variants=seed.variants,
                case_sensitive=seed.case_sensitive,
                case_policy=seed.case_policy,
                speech_strategy=seed.speech_strategy,
                description=seed.description,
                aliases=seed.aliases,
                only_if_preceded_by=seed.only_if_preceded_by,
                only_if_followed_by=seed.only_if_followed_by,
                only_if_pos=seed.only_if_pos,
                not_if_pos=seed.not_if_pos,
                boundary=seed.boundary,
                left_boundary=seed.left_boundary,
                right_boundary=seed.right_boundary,
            )
        )


class BundledLanguageExpander(AbbreviationExpander):
    """Base class for small data-driven language modules."""

    BUNDLE: LanguageBundle

    def _initialize_abbreviations(self) -> None:
        register_bundle(self, self.BUNDLE)


__all__ = ["BundledLanguageExpander", "register_bundle"]
