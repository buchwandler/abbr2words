"""Public API for :mod:`abbr2words`."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Set
from importlib import import_module
from re import Pattern
from threading import RLock
from typing import Final, Literal

from .annotations import TokenAnnotation
from .core import (
    AbbreviationContext,
    AbbreviationEntry,
    AbbreviationExpander,
    ExpansionResult,
    PosConstraints,
    ProtectedSpan,
)
from .initialisms import InitialismCase, InitialismMode, RegisteredInitialismMode
from .language_registry import (
    LANGUAGE_SPECS,
    language_spec,
    resolve_language,
    supported_language_keys,
)
from .units import UnitDiagnostic, UnitEntry, UnitMatch
from .units import iter_unit_diagnostics as _iter_unit_diagnostics
from .units import iter_unit_matches as _iter_unit_matches

_LANGUAGE_CLASSES: Final[dict[str, tuple[str, str]]] = {
    key: (spec.module, spec.class_name) for key, spec in LANGUAGE_SPECS.items()
}

_SHARED_EXPANDERS: dict[
    tuple[str, bool, InitialismMode, InitialismCase, RegisteredInitialismMode], AbbreviationExpander
] = {}
_SHARED_LOCK = RLock()


def normalize_language(lang: str) -> str:
    """Normalize and resolve an ISO-style language or locale code."""
    return resolve_language(lang)


def base_language(lang: str) -> str:
    """Return the resolved base language for a language or locale input."""
    return normalize_language(lang).split("_", 1)[0]


def supported_languages(*, include_locales: bool = True) -> tuple[str, ...]:
    """Return sorted bundled language and, optionally, locale keys."""
    return supported_language_keys(include_locales=include_locales)


def iter_unit_matches(
    text: str,
    language: str,
    *,
    overrides: Mapping[str, UnitEntry] | None = None,
    suppressed: Set[str] | None = None,
    protected_spans: Iterable[tuple[int, int]] = (),
) -> Iterator[UnitMatch]:
    """Yield structured source-aligned matches for numeric quantity symbols."""
    return _iter_unit_matches(
        text,
        normalize_language(language),
        overrides=overrides,
        suppressed=suppressed,
        protected_spans=protected_spans,
    )


def iter_unit_diagnostics(
    text: str,
    language: str,
    *,
    overrides: Mapping[str, UnitEntry] | None = None,
    suppressed: Set[str] | None = None,
    protected_spans: Iterable[tuple[int, int]] = (),
) -> Iterator[UnitDiagnostic]:
    """Yield accepted unit matches and policy rejections for compact candidates."""
    return _iter_unit_diagnostics(
        text,
        normalize_language(language),
        overrides=overrides,
        suppressed=suppressed,
        protected_spans=protected_spans,
    )


def _expander_class(lang: str) -> type[AbbreviationExpander]:
    code = normalize_language(lang)
    spec = language_spec(code)
    module = import_module(spec.module)
    cls = getattr(module, spec.class_name)
    return cls


def get_expander(
    lang: str = "en",
    *,
    context: bool = True,
    initialism_mode: InitialismMode = "dotted_only",
    initialism_case: InitialismCase = "source",
    registered_initialism_mode: RegisteredInitialismMode = "expand",
) -> AbbreviationExpander:
    """Return a new, independently mutable language expander."""
    cls = _expander_class(lang)
    return cls(
        enable_context_detection=context,
        initialism_mode=initialism_mode,
        initialism_case=initialism_case,
        registered_initialism_mode=registered_initialism_mode,
    )


def get_shared_expander(
    lang: str = "en",
    *,
    context: bool = True,
    initialism_mode: InitialismMode = "dotted_only",
    initialism_case: InitialismCase = "source",
    registered_initialism_mode: RegisteredInitialismMode = "expand",
) -> AbbreviationExpander:
    """Return the shared registry for a language, context, and policy."""
    code = normalize_language(lang)
    key = (code, context, initialism_mode, initialism_case, registered_initialism_mode)
    with _SHARED_LOCK:
        if key not in _SHARED_EXPANDERS:
            _SHARED_EXPANDERS[key] = _expander_class(code)(
                enable_context_detection=context,
                initialism_mode=initialism_mode,
                initialism_case=initialism_case,
                registered_initialism_mode=registered_initialism_mode,
            )
        return _SHARED_EXPANDERS[key]


def reset_expanders(lang: str | None = None) -> None:
    """Reset one or all shared language registries."""
    languages = (normalize_language(lang),) if lang is not None else supported_languages()
    with _SHARED_LOCK:
        for code in languages:
            for key in tuple(_SHARED_EXPANDERS):
                if key[0] == code:
                    del _SHARED_EXPANDERS[key]


def abbr2words(
    text: str,
    *,
    lang: str = "en",
    context: bool = True,
    initialism_mode: InitialismMode = "dotted_only",
    initialism_case: InitialismCase = "source",
    registered_initialism_mode: RegisteredInitialismMode = "expand",
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
    return get_shared_expander(
        code,
        context=context,
        initialism_mode=initialism_mode,
        initialism_case=initialism_case,
        registered_initialism_mode=registered_initialism_mode,
    ).expand(text, annotations=annotations, protected_spans=protected_spans)


def abbr2words_with_replacements(
    text: str,
    *,
    lang: str = "en",
    context: bool = True,
    initialism_mode: InitialismMode = "dotted_only",
    initialism_case: InitialismCase = "source",
    registered_initialism_mode: RegisteredInitialismMode = "expand",
    annotations: Iterable[TokenAnnotation] | None = None,
    protected_spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]]
    | None = None,
) -> ExpansionResult:
    """Expand *text* and return exact source-aligned replacement metadata."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    code = normalize_language(lang)
    return get_shared_expander(
        code,
        context=context,
        initialism_mode=initialism_mode,
        initialism_case=initialism_case,
        registered_initialism_mode=registered_initialism_mode,
    ).expand_with_replacements(text, annotations=annotations, protected_spans=protected_spans)


expand = abbr2words


class Expander:
    """Small facade for a mutable, language-specific abbreviation registry."""

    def __init__(
        self,
        lang: str = "en",
        *,
        context: bool = True,
        initialism_mode: InitialismMode = "dotted_only",
        initialism_case: InitialismCase = "source",
        registered_initialism_mode: RegisteredInitialismMode = "expand",
    ) -> None:
        self.lang = normalize_language(lang)
        self.context = context
        self.initialism_mode = initialism_mode
        self.initialism_case = initialism_case
        self.registered_initialism_mode = registered_initialism_mode
        self._impl = get_expander(
            self.lang,
            context=context,
            initialism_mode=initialism_mode,
            initialism_case=initialism_case,
            registered_initialism_mode=registered_initialism_mode,
        )

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

    def expand_with_replacements(
        self,
        text: str,
        *,
        annotations: Iterable[TokenAnnotation] | None = None,
        protected_spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]]
        | None = None,
    ) -> ExpansionResult:
        """Expand abbreviations and return exact replacement metadata."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return self._impl.expand_with_replacements(
            text, annotations=annotations, protected_spans=protected_spans
        )

    def expand_with_trace(
        self,
        text: str,
        *,
        annotations: Iterable[TokenAnnotation] | None = None,
        protected_spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]]
        | None = None,
    ) -> ExpansionResult:
        """Compatibility alias for :meth:`expand_with_replacements`."""
        return self.expand_with_replacements(
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
        case_policy: Literal["fixed", "sentence"] = "fixed",
        speech_strategy: Literal["expand", "spell_source"] = "expand",
        aliases: tuple[str, ...] = (),
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
                aliases=aliases,
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
                case_policy=case_policy,
                speech_strategy=speech_strategy,
                aliases=aliases,
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
        case_policy: Literal["fixed", "sentence"] = "fixed",
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
            case_policy=case_policy,
        )

    def set_unit(
        self,
        symbol: str,
        expansion: str,
        *,
        case_sensitive: bool = True,
        description: str = "Custom unit",
        canonical_id: str | None = None,
        category: str = "unit",
    ) -> None:
        """Override a reviewed unit for this isolated expander."""
        self._impl.set_unit(
            symbol,
            expansion,
            case_sensitive=case_sensitive,
            description=description,
            canonical_id=canonical_id,
            category=category,
        )

    def iter_unit_matches(
        self,
        text: str,
        *,
        protected_spans: Iterable[tuple[int, int]] = (),
    ) -> Iterator[UnitMatch]:
        """Yield structured matches using this expander's unit customization."""
        return self._impl.iter_unit_matches(text, protected_spans=protected_spans)

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
