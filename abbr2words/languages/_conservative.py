"""Compatibility base for data-driven conservative language modules."""

from __future__ import annotations

from abbr2words.language_data import bundle_for
from abbr2words.languages._bundled import BundledLanguageExpander
from abbr2words.unit_data.common import register_common_units


class ConservativeAbbreviationExpander(BundledLanguageExpander):
    """Data-driven baseline expander that fails closed on ambiguous text."""

    UNIT_LANGUAGE = "en"
    LANGUAGE_KEY = ""

    def _initialize_abbreviations(self) -> None:
        from abbr2words.languages._bundled import register_bundle

        register_bundle(self, bundle_for(self.LANGUAGE_KEY))


def initialize_language(language: str) -> None:
    """Install common unit data before the core expander is instantiated."""
    register_common_units(language)


__all__ = ["ConservativeAbbreviationExpander", "initialize_language"]
