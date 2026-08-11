"""Checked-in, declarative language data used by bundled expanders."""

from .bundles import BUNDLES, bundle_for
from .model import AbbreviationSeed, LanguageBundle, SourceRef

__all__ = ["AbbreviationSeed", "BUNDLES", "LanguageBundle", "SourceRef", "bundle_for"]
