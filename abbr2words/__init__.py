"""Multilingual, context-aware abbreviation expansion."""

from .__about__ import __version__
from .api import Expander, abbr2words, expand, get_expander, normalize_language, supported_languages
from .core import AbbreviationContext, AbbreviationEntry, AbbreviationExpander

__all__ = [
    "AbbreviationContext",
    "AbbreviationEntry",
    "AbbreviationExpander",
    "Expander",
    "__version__",
    "abbr2words",
    "expand",
    "get_expander",
    "normalize_language",
    "supported_languages",
]
