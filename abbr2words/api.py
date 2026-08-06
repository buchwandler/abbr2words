"""Public API for :mod:`abbr2words`."""

from __future__ import annotations

from collections.abc import Iterable
from importlib import import_module
from re import Pattern
from threading import RLock
from typing import Final

from .annotations import TokenAnnotation
from .core import (
    AbbreviationContext,
    AbbreviationEntry,
    AbbreviationExpander,
    ExpansionResult,
    PosConstraints,
    ProtectedSpan,
)

_LANGUAGE_CLASSES: Final[dict[str, tuple[str, str]]] = {
    "cs": ("abbr2words.languages.cs", "CzechAbbreviationExpander"),
    "de": ("abbr2words.languages.de", "GermanAbbreviationExpander"),
    "en": ("abbr2words.languages.en", "EnglishAbbreviationExpander"),
    "es": ("abbr2words.languages.es", "SpanishAbbreviationExpander"),
    "fr": ("abbr2words.languages.fr", "FrenchAbbreviationExpander"),
    "it": ("abbr2words.languages.it", "ItalianAbbreviationExpander"),
    "nl": ("abbr2words.languages.nl", "DutchAbbreviationExpander"),
    "pl": ("abbr2words.languages.pl", "PolishAbbreviationExpander"),
    "pt": ("abbr2words.languages.pt", "PortugueseAbbreviationExpander"),
    "ru": ("abbr2words.languages.ru", "RussianAbbreviationExpander"),
    "sv": ("abbr2words.languages.sv", "SwedishAbbreviationExpander"),
    "tr": ("abbr2words.languages.tr", "TurkishAbbreviationExpander"),
}

_ALIASES: Final[dict[str, str]] = {
    "cz": "cs",
    "cze": "cs",
    "ces": "cs",
    "deu": "de",
    "ger": "de",
    "eng": "en",
    "spa": "es",
    "fra": "fr",
    "fre": "fr",
    "ita": "it",
    "por": "pt",
    "dut": "nl",
    "nld": "nl",
    "pol": "pl",
    "rus": "ru",
    "swe": "sv",
    "tur": "tr",
}

_SHARED_EXPANDERS: dict[tuple[str, bool], AbbreviationExpander] = {}
_SHARED_LOCK = RLock()


def normalize_language(lang: str) -> str:
    """Normalize an ISO-style language or locale code to a bundled language."""
    if not isinstance(lang, str) or not lang.strip():
        raise ValueError("lang must be a non-empty language code")

    normalized = lang.strip().lower().replace("_", "-")
    base = normalized.split("-", 1)[0]
    base = _ALIASES.get(base, base)
    if base not in _LANGUAGE_CLASSES:
        supported = ", ".join(sorted(_LANGUAGE_CLASSES))
        raise ValueError(f"Unsupported language {lang!r}. Supported languages: {supported}")
    return base


def supported_languages() -> tuple[str, ...]:
    """Return the bundled base language codes."""
    return tuple(sorted(_LANGUAGE_CLASSES))


def _expander_class(lang: str) -> type[AbbreviationExpander]:
    code = normalize_language(lang)
    module_name, class_name = _LANGUAGE_CLASSES[code]
    module = import_module(module_name)
    cls = getattr(module, class_name)
    return cls


def get_expander(
    lang: str = "en",
    *,
    context: bool = True,
) -> AbbreviationExpander:
    """Return a new, independently mutable language expander."""
    cls = _expander_class(lang)
    return cls(enable_context_detection=context)


def get_shared_expander(
    lang: str = "en",
    *,
    context: bool = True,
) -> AbbreviationExpander:
    """Return the shared registry for a language and context mode."""
    code = normalize_language(lang)
    key = (code, context)
    with _SHARED_LOCK:
        if key not in _SHARED_EXPANDERS:
            _SHARED_EXPANDERS[key] = _expander_class(code)(enable_context_detection=context)
        return _SHARED_EXPANDERS[key]


def reset_expanders(lang: str | None = None) -> None:
    """Reset one or all shared language registries."""
    languages = (normalize_language(lang),) if lang is not None else supported_languages()
    with _SHARED_LOCK:
        for code in languages:
            for key in tuple(_SHARED_EXPANDERS):
                if key[0] == code:
                    del _SHARED_EXPANDERS[key]

            # Preserve cleanup for callers importing language modules directly.
            module_name, _ = _LANGUAGE_CLASSES[code]
            import_module(module_name).reset_expander()


def abbr2words(
    text: str,
    *,
    lang: str = "en",
    context: bool = True,
    annotations: Iterable[TokenAnnotation] | None = None,
    protected_spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]]
    | None = None,
) -> str:
    """Expand known abbreviations in *text*.

    The function expands abbreviations only. It intentionally does not normalize
    dates, times, numbers, currencies, or general punctuation. Optional
    annotations must use character offsets in the original source; POS guards
    fail open when usable lexical evidence is missing, and numeric units remain
    authoritative over generic POS predictions.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    code = normalize_language(lang)
    return get_shared_expander(code, context=context).expand(
        text, annotations=annotations, protected_spans=protected_spans
    )


expand = abbr2words


class Expander:
    """Small facade for a mutable, language-specific abbreviation registry."""

    def __init__(self, lang: str = "en", *, context: bool = True) -> None:
        self.lang = normalize_language(lang)
        self.context = context
        self._impl = get_expander(self.lang, context=context)

    def expand(
        self,
        text: str,
        *,
        annotations: Iterable[TokenAnnotation] | None = None,
        protected_spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]]
        | None = None,
    ) -> str:
        """Expand abbreviations using this instance's registry.

        ``annotations`` are source-aligned to the original text. Only coarse
        ``pos`` labels participate in guards; fine-grained ``tag`` values are
        retained as metadata.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return self._impl.expand(text, annotations=annotations, protected_spans=protected_spans)

    def expand_with_trace(
        self,
        text: str,
        *,
        annotations: Iterable[TokenAnnotation] | None = None,
        protected_spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]]
        | None = None,
    ) -> ExpansionResult:
        """Expand abbreviations and return source-aligned accepted matches."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return self._impl.expand_with_trace(
            text, annotations=annotations, protected_spans=protected_spans
        )

    __call__ = expand

    def add(
        self,
        abbreviation: str,
        expansion: str | dict[str, str],
        *,
        context_expansions: dict[AbbreviationContext, str] | None = None,
        case_sensitive: bool = False,
        description: str = "",
        only_if_preceded_by: str | Pattern[str] | None = None,
        only_if_followed_by: str | Pattern[str] | None = None,
        only_if_pos: PosConstraints = None,
        not_if_pos: PosConstraints = None,
    ) -> None:
        """Add or replace an abbreviation, optionally constrained by POS.

        A string is one POS label; collections support multiple labels. Deny
        constraints take precedence over allow constraints.
        """
        if isinstance(expansion, dict):
            if context_expansions is not None:
                raise ValueError(
                    "provide context expansions either in expansion or context_expansions"
                )
            self._impl.add_custom_abbreviation(
                abbreviation,
                expansion,
                description=description,
                case_sensitive=case_sensitive,
                only_if_preceded_by=only_if_preceded_by,
                only_if_followed_by=only_if_followed_by,
                only_if_pos=only_if_pos,
                not_if_pos=not_if_pos,
            )
            return
        self._impl.add_abbreviation(
            AbbreviationEntry(
                abbreviation=abbreviation,
                expansion=expansion,
                context_expansions=context_expansions,
                case_sensitive=case_sensitive,
                description=description,
                only_if_preceded_by=only_if_preceded_by,
                only_if_followed_by=only_if_followed_by,
                only_if_pos=only_if_pos,
                not_if_pos=not_if_pos,
                origin="custom",
            )
        )

    def add_custom_abbreviation(
        self,
        abbreviation: str,
        expansion: str | dict[str, str],
        description: str = "",
        case_sensitive: bool = False,
        only_if_preceded_by: str | Pattern[str] | None = None,
        only_if_followed_by: str | Pattern[str] | None = None,
        only_if_pos: PosConstraints = None,
        not_if_pos: PosConstraints = None,
    ) -> None:
        """Register an entry using string-named context expansions."""
        self._impl.add_custom_abbreviation(
            abbreviation,
            expansion,
            description=description,
            case_sensitive=case_sensitive,
            only_if_preceded_by=only_if_preceded_by,
            only_if_followed_by=only_if_followed_by,
            only_if_pos=only_if_pos,
            not_if_pos=not_if_pos,
        )

    def set_unit(
        self,
        symbol: str,
        expansion: str,
        *,
        case_sensitive: bool = True,
        description: str = "Custom unit",
    ) -> None:
        """Override a reviewed unit for this isolated expander."""
        self._impl.set_unit(
            symbol, expansion, case_sensitive=case_sensitive, description=description
        )

    def remove_unit(self, symbol: str) -> bool:
        """Suppress a reviewed unit for this isolated expander."""
        return self._impl.remove_unit(symbol)

    def has_unit(self, symbol: str) -> bool:
        return self._impl.has_unit(symbol)

    def remove(self, abbreviation: str, *, case_sensitive: bool = False) -> bool:
        """Remove an abbreviation from this instance."""
        return self._impl.remove_abbreviation(abbreviation, case_sensitive)

    def has(self, abbreviation: str, *, case_sensitive: bool = False) -> bool:
        """Return whether this instance contains an abbreviation."""
        return self._impl.has_abbreviation(abbreviation, case_sensitive)

    def abbreviations(self) -> tuple[str, ...]:
        """Return the configured abbreviation spellings."""
        return tuple(self._impl.get_abbreviations_list())

    def __repr__(self) -> str:
        return (
            f"Expander(lang={self.lang!r}, context={self.context!r}, "
            f"abbreviations={len(self._impl.entries)})"
        )
