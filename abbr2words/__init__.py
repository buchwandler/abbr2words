"""Multilingual, context-aware abbreviation expansion."""

try:
    from ._version import version as __version__
except ImportError:
    from .__about__ import __version__
from .annotations import TokenAnnotation
from .api import (
    Expander,
    abbr2words,
    abbr2words_with_replacements,
    base_language,
    expand,
    get_expander,
    get_shared_expander,
    iter_initialism_diagnostics,
    iter_unit_diagnostics,
    iter_unit_matches,
    normalize_language,
    reset_expanders,
    supported_languages,
)
from .core import (
    AbbreviationContext,
    AbbreviationEntry,
    AbbreviationExpander,
    ExpansionKind,
    ExpansionMatch,
    ExpansionReplacement,
    ExpansionResult,
    ExpansionVariant,
    ProtectedSpan,
    abbreviation_guards_match,
)
from .initialisms import (
    InitialismCase,
    InitialismDiagnostic,
    InitialismDiagnosticDecision,
    InitialismMode,
    InitialismPolicy,
    RegisteredInitialismMode,
)
from .units import UnitAmbiguity, UnitDiagnostic, UnitEntry, UnitMatch

__all__ = [
    "AbbreviationContext",
    "AbbreviationEntry",
    "AbbreviationExpander",
    "ExpansionKind",
    "InitialismCase",
    "InitialismDiagnostic",
    "InitialismDiagnosticDecision",
    "InitialismMode",
    "InitialismPolicy",
    "RegisteredInitialismMode",
    "ExpansionVariant",
    "ExpansionMatch",
    "ExpansionReplacement",
    "ExpansionResult",
    "ProtectedSpan",
    "TokenAnnotation",
    "UnitEntry",
    "UnitAmbiguity",
    "UnitDiagnostic",
    "UnitMatch",
    "abbreviation_guards_match",
    "Expander",
    "__version__",
    "abbr2words",
    "abbr2words_with_replacements",
    "base_language",
    "expand",
    "get_expander",
    "get_shared_expander",
    "iter_unit_matches",
    "iter_initialism_diagnostics",
    "iter_unit_diagnostics",
    "normalize_language",
    "reset_expanders",
    "supported_languages",
]
