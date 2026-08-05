"""Public API for :mod:`abbr2words`."""

from __future__ import annotations

from importlib import import_module
from typing import Final

from .core import AbbreviationEntry, AbbreviationExpander

_LANGUAGE_CLASSES: Final[dict[str, tuple[str, str]]] = {
    "cs": ("abbr2words.languages.cs", "CzechAbbreviationExpander"),
    "de": ("abbr2words.languages.de", "GermanAbbreviationExpander"),
    "en": ("abbr2words.languages.en", "EnglishAbbreviationExpander"),
    "es": ("abbr2words.languages.es", "SpanishAbbreviationExpander"),
    "fr": ("abbr2words.languages.fr", "FrenchAbbreviationExpander"),
    "it": ("abbr2words.languages.it", "ItalianAbbreviationExpander"),
    "pt": ("abbr2words.languages.pt", "PortugueseAbbreviationExpander"),
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
}


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
    """Return the shared language-module singleton used by consumers."""
    code = normalize_language(lang)
    module_name, _ = _LANGUAGE_CLASSES[code]
    module = import_module(module_name)
    return module.get_expander(enable_context_detection=context)


def reset_expanders(lang: str | None = None) -> None:
    """Reset one or all shared language registries."""
    languages = (normalize_language(lang),) if lang is not None else supported_languages()
    for code in languages:
        module_name, _ = _LANGUAGE_CLASSES[code]
        import_module(module_name).reset_expander()


def abbr2words(
    text: str,
    *,
    lang: str = "en",
    context: bool = True,
) -> str:
    """Expand known abbreviations in *text*.

    The function expands abbreviations only. It intentionally does not normalize
    dates, times, numbers, currencies, or general punctuation.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    code = normalize_language(lang)
    return get_shared_expander(code, context=context).expand(text)


expand = abbr2words


class Expander:
    """Small facade for a mutable, language-specific abbreviation registry."""

    def __init__(self, lang: str = "en", *, context: bool = True) -> None:
        self.lang = normalize_language(lang)
        self.context = context
        self._impl = get_expander(self.lang, context=context)

    def expand(self, text: str) -> str:
        """Expand abbreviations using this instance's registry."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return self._impl.expand(text)

    __call__ = expand

    def add(self, abbreviation: str, expansion: str, **kwargs: object) -> None:
        """Add or replace an abbreviation in this instance."""
        self._impl.add_abbreviation(
            AbbreviationEntry(
                abbreviation=abbreviation,
                expansion=expansion,
                **kwargs,
            )
        )

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
