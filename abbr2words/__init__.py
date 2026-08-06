"""Multilingual, context-aware abbreviation expansion."""

try:
    from ._version import version as __version__
except ImportError:
    from .__about__ import __version__
from .annotations import TokenAnnotation
from .api import (
    Expander,
    abbr2words,
    expand,
    get_expander,
    get_shared_expander,
    normalize_language,
    reset_expanders,
    supported_languages,
)
from .core import (
    AbbreviationContext,
    AbbreviationEntry,
    AbbreviationExpander,
    abbreviation_guards_match,
)

__all__ = [
    "AbbreviationContext",
    "AbbreviationEntry",
    "AbbreviationExpander",
    "TokenAnnotation",
    "abbreviation_guards_match",
    "Expander",
    "__version__",
    "abbr2words",
    "expand",
    "get_expander",
    "get_shared_expander",
    "normalize_language",
    "reset_expanders",
    "supported_languages",
]
