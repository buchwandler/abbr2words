"""Policy-controlled fallback handling for uppercase initialisms."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any, Literal, cast

from ._replacements import Replacement

# Registered abbreviations and reviewed units deliberately outrank this
# structural fallback. Keep the precedence named so it remains visible at the
# integration point instead of becoming an unexplained magic number.
INITIALISM_FALLBACK_PRIORITY = 50
_DOTTED_INITIALISM = re.compile(r"(?<!\w)(?P<value>(?:[A-Z]\.){2,8})(?!\w)")
_UNDOTTED_INITIALISM = re.compile(r"(?<!\w)(?P<value>[A-Z]{2,8})(?!\w)")
_ROMAN_ONLY = re.compile(r"^[IVXLCDM]+$")
_UPPERCASE_WORD = re.compile(r"(?<!\w)(?P<value>[A-Z]{2,})(?!\w)")
_STRUCTURED_IDENTIFIER = re.compile(r"(?<!\w)(?P<value>[A-Z0-9]+(?:[-.][A-Z0-9]+)+)(?!\w)")
_VOWELS = frozenset("AEIOU")
_UNKNOWN_VOWEL_LIKE = {
    "en": frozenset("AEIOUY"),
    "de": frozenset("AEIOUY"),
    "es": frozenset("AEIOUY"),
    "fr": frozenset("AEIOUY"),
    "it": frozenset("AEIOUY"),
}
_ASCII_UPPERCASE = re.compile(r"^[A-Z]+$")
_UPPERCASE_RUN_SEPARATOR = re.compile(r"^[\s,;:!?…—–()\[\]{}\"'“”‘’]+$")

InitialismMode = Literal["dotted_only", "conservative_undotted", "spell_undotted"]
InitialismCase = Literal["source", "upper", "lower"]
RegisteredInitialismMode = Literal["expand", "spell"]
InitialismDiagnosticDecision = Literal["accepted", "preserved", "rejected"]
_InitialismDecisionKind = Literal["expand", "preserve", "skip"]


@dataclass(frozen=True, slots=True)
class InitialismPreserveToken:
    """Declarative metadata for uppercase tokens the fallback must preserve."""

    token: str
    reason: str
    languages: tuple[str, ...] = ("*",)

    def applies_to(self, language: str) -> bool:
        """Return whether this policy record applies to a language or locale."""
        base = language.split("_", 1)[0]
        return "*" in self.languages or language in self.languages or base in self.languages


@dataclass(frozen=True, slots=True)
class InitialismDiagnostic:
    """One source-aligned initialism decision for benchmark and caller triage."""

    start: int
    end: int
    source_text: str
    language: str
    candidate_kind: str
    decision: InitialismDiagnosticDecision
    reason: str
    registered_entry_id: str | None = None


@dataclass(frozen=True, slots=True)
class _InitialismDecision:
    """One source-aligned policy decision shared by diagnostics and fallback."""

    start: int
    end: int
    source: str
    candidate_kind: str
    decision: _InitialismDecisionKind
    reason: str
    registry_key: str | None = None
    speech_strategy: str | None = None


@dataclass(frozen=True, slots=True)
class InitialismPolicy:
    """Immutable rendering policy carried by an expander instance."""

    mode: InitialismMode = "dotted_only"
    case: InitialismCase = "source"
    registered_mode: RegisteredInitialismMode = "expand"

    def __post_init__(self) -> None:
        validate_initialism_policy(
            mode=self.mode,
            case=self.case,
            registered_mode=self.registered_mode,
        )


def validate_initialism_policy(
    *,
    mode: str = "dotted_only",
    case: str = "source",
    registered_mode: str = "expand",
) -> None:
    """Validate public initialism policy values."""
    if mode not in {"dotted_only", "conservative_undotted", "spell_undotted"}:
        raise ValueError(
            "initialism_mode must be 'dotted_only', 'conservative_undotted', or 'spell_undotted'"
        )
    if case not in {"source", "upper", "lower"}:
        raise ValueError("initialism_case must be 'source', 'upper', or 'lower'")
    if registered_mode not in {"expand", "spell"}:
        raise ValueError("registered_initialism_mode must be 'expand' or 'spell'")


def render_initialism_source(
    source: str,
    *,
    case: InitialismCase = "source",
    strip_dots: bool = True,
) -> str:
    """Render source graphemes as separately spoken letters."""
    if case not in {"source", "upper", "lower"}:
        raise ValueError("initialism_case must be 'source', 'upper', or 'lower'")
    letters = source.replace(".", "") if strip_dots else source
    if case == "upper":
        letters = letters.upper()
    elif case == "lower":
        letters = letters.lower()
    return " ".join(letters)


def should_preserve_sentence_final_period(
    text: str,
    end: int,
    matched_text: str,
    expansion: str,
) -> bool:
    """Return whether a dotted abbreviation consumed sentence punctuation."""
    if not matched_text.endswith(".") or not expansion or expansion[-1] in ".!?":
        return False

    suffix = text[end:]
    index = 0
    while index < len(suffix) and suffix[index].isspace():
        index += 1

    closing = frozenset("\"'”’»)]}")
    while index < len(suffix) and suffix[index] in closing:
        index += 1
        while index < len(suffix) and suffix[index].isspace():
            index += 1

    return index == len(suffix)


def _is_hyphenated_identifier_component(text: str, start: int, end: int) -> bool:
    """Reject uppercase fragments attached to a hyphenated identifier."""
    left = start > 0 and text[start - 1] == "-"
    right = end < len(text) and text[end] == "-"
    return (left and start > 1 and text[start - 2].isalnum()) or (
        right and end + 1 < len(text) and text[end + 1].isalnum()
    )


def _preserve_records(language: str) -> tuple[InitialismPreserveToken, ...]:
    """Load policy data lazily to avoid the language-data/core import cycle."""
    from .language_data.initialisms import preserve_initialism_tokens

    return preserve_initialism_tokens(language)


def _uppercase_runs(text: str) -> tuple[tuple[re.Match[str], ...], ...]:
    """Return presentation-separated uppercase word runs in source order."""
    matches = tuple(_UPPERCASE_WORD.finditer(text))
    runs: list[tuple[re.Match[str], ...]] = []
    current: list[re.Match[str]] = []
    for match in matches:
        if current and not _UPPERCASE_RUN_SEPARATOR.fullmatch(
            text[current[-1].end() : match.start()]
        ):
            runs.append(tuple(current))
            current = []
        current.append(match)
    if current:
        runs.append(tuple(current))
    return tuple(runs)


def _headline_run_spans(
    text: str,
    records: tuple[InitialismPreserveToken, ...],
    entries: tuple[Any, ...],
) -> frozenset[tuple[int, int]]:
    """Return unregistered candidates in generic uppercase prose runs."""
    headline_words = {record.token for record in records if record.reason == "headline-word"}
    spans: set[tuple[int, int]] = set()
    for run in _uppercase_runs(text):
        values = {match.group("value") for match in run}
        if len(run) < 3:
            continue
        lexical_count = sum(
            _registered_entry_for(value, entries) is None
            and value not in headline_words
            and not _ROMAN_ONLY.fullmatch(value)
            for value in values
        )
        if lexical_count >= 2 or values & headline_words:
            spans.update(
                (match.start("value"), match.end("value"))
                for match in run
                if _registered_entry_for(match.group("value"), entries) is None
            )
    return frozenset(spans)


def _is_high_confidence_unknown(source: str) -> bool:
    """Keep only bounded, ASCII consonant-only unknown candidates."""
    return (
        3 <= len(source) <= 6
        and _ASCII_UPPERCASE.fullmatch(source) is not None
        and not any(character in _VOWELS or character == "Y" for character in source)
    )


def _unknown_vowel_like(language: str) -> frozenset[str]:
    """Return the language-specific vowel-like set for residual candidates."""
    return _UNKNOWN_VOWEL_LIKE.get(language.split("_", 1)[0], frozenset("AEIOUY"))


def _overlaps_protected(
    start: int,
    end: int,
    protected_spans: tuple[tuple[int, int], ...],
) -> bool:
    return any(
        start < protected_end and protected_start < end
        for protected_start, protected_end in protected_spans
    )


def _registered_entry_for(source: str, entries: Iterable[Any]) -> Any | None:
    """Find a registered entry by source spelling without creating replacements."""
    for entry in entries:
        spellings = (entry.abbreviation, *getattr(entry, "aliases", ()))
        if getattr(entry, "case_sensitive", False):
            if source in spellings:
                return entry
        elif any(source.casefold() == spelling.casefold() for spelling in spellings):
            return entry
    return None


def _initialism_candidates(text: str) -> tuple[tuple[int, int, str, str], ...]:
    """Collect dotted, undotted, and structured candidates without overlaps."""
    candidates: list[tuple[int, int, str, str]] = []
    identifiers = tuple(
        match
        for match in _STRUCTURED_IDENTIFIER.finditer(text)
        if not (
            "." in match.group("value")
            and "-" not in match.group("value")
            and not any(character.isdigit() for character in match.group("value"))
        )
    )
    for match in identifiers:
        value = match.group("value")
        candidates.append((match.start("value"), match.end("value"), "identifier", value))

    for pattern, kind in (
        (_DOTTED_INITIALISM, "dotted"),
        (_UNDOTTED_INITIALISM, "unknown-undotted"),
    ):
        for match in pattern.finditer(text):
            start, end = match.start("value"), match.end("value")
            if any(
                start < identifier.end() and identifier.start() < end for identifier in identifiers
            ):
                continue
            candidates.append((start, end, kind, match.group("value")))

    return tuple(sorted(candidates, key=lambda item: (item[0], -(item[1] - item[0]))))


def _initialism_decisions(
    text: str,
    *,
    language: str,
    mode: InitialismMode,
    registered_mode: RegisteredInitialismMode,
    protected_spans: tuple[tuple[int, int], ...],
    registered_entries: tuple[Any, ...],
) -> tuple[_InitialismDecision, ...]:
    """Classify every candidate once for all initialism consumers."""
    records = _preserve_records(language) if mode == "conservative_undotted" else ()
    preserve_reasons = {record.token: record.reason for record in records}
    headline_spans = (
        _headline_run_spans(text, records, registered_entries)
        if mode == "conservative_undotted"
        else frozenset()
    )
    decisions: list[_InitialismDecision] = []

    for start, end, kind, source in _initialism_candidates(text):
        registered = _registered_entry_for(source, registered_entries)
        registry_key = f"abbr:{registered.abbreviation}" if registered is not None else None
        speech_strategy = (
            getattr(registered, "speech_strategy", None) if registered is not None else None
        )
        if _overlaps_protected(start, end, protected_spans):
            decisions.append(
                _InitialismDecision(
                    start,
                    end,
                    text[start:end],
                    kind,
                    "preserve",
                    "protected-span",
                    registry_key,
                    speech_strategy,
                )
            )
            continue

        if registered is not None:
            reason = (
                "registered-spell"
                if registered_mode == "spell" and speech_strategy == "spell_source"
                else "registered-semantic"
            )
            decisions.append(
                _InitialismDecision(
                    start,
                    end,
                    source,
                    "registered",
                    "expand",
                    reason,
                    registry_key,
                    speech_strategy,
                )
            )
            continue

        if kind == "identifier":
            decisions.append(
                _InitialismDecision(start, end, source, kind, "skip", "structured-candidate")
            )
            continue

        if kind == "dotted":
            decisions.append(
                _InitialismDecision(start, end, source, kind, "expand", "dotted-initialism")
            )
            continue

        if _ROMAN_ONLY.fullmatch(source):
            reason = "roman-like"
        elif _is_hyphenated_identifier_component(text, start, end):
            reason = "hyphenated-code"
        elif mode == "conservative_undotted" and source in preserve_reasons:
            reason = preserve_reasons[source]
            if reason == "headline-word":
                reason = "uppercase-run"
        elif (start, end) in headline_spans:
            reason = "uppercase-run"
        elif mode == "dotted_only":
            reason = "unsupported-shape"
        elif mode == "conservative_undotted" and len(source) == 2:
            reason = "two-letter-unknown"
        elif mode == "conservative_undotted" and any(
            character in _unknown_vowel_like(language) for character in source
        ):
            reason = "vowel-bearing-unknown"
        elif mode == "conservative_undotted" and _is_high_confidence_unknown(source):
            decisions.append(
                _InitialismDecision(
                    start,
                    end,
                    source,
                    kind,
                    "expand",
                    "conservative-unknown",
                )
            )
            continue
        elif mode == "spell_undotted":
            decisions.append(
                _InitialismDecision(
                    start,
                    end,
                    source,
                    kind,
                    "expand",
                    "unknown-undotted",
                )
            )
            continue
        else:
            reason = "unsupported-shape"

        decisions.append(_InitialismDecision(start, end, source, kind, "skip", reason))

    return tuple(decisions)


def iter_initialism_diagnostics(
    text: str,
    *,
    language: str = "en",
    mode: InitialismMode = "dotted_only",
    registered_mode: RegisteredInitialismMode = "expand",
    protected_spans: Iterable[tuple[int, int]] = (),
    registered_entries: Iterable[Any] = (),
) -> Iterator[InitialismDiagnostic]:
    """Yield inspectable decisions for initialism-shaped source candidates."""
    validate_initialism_policy(mode=mode, registered_mode=registered_mode)
    protected = tuple(protected_spans)
    entries = tuple(registered_entries)
    for item in _initialism_decisions(
        text,
        language=language,
        mode=mode,
        registered_mode=registered_mode,
        protected_spans=protected,
        registered_entries=entries,
    ):
        decision = cast(
            InitialismDiagnosticDecision,
            {
                "expand": "accepted",
                "preserve": "preserved",
                "skip": "rejected",
            }[item.decision],
        )
        yield InitialismDiagnostic(
            item.start,
            item.end,
            item.source,
            language,
            item.candidate_kind,
            decision,
            item.reason,
            item.registry_key,
        )


def iter_initialism_replacements(
    text: str,
    *,
    mode: InitialismMode = "dotted_only",
    case: InitialismCase = "source",
    language: str = "en",
    protected_spans: Iterable[tuple[int, int]] = (),
    registered_entries: Iterable[Any] = (),
) -> Iterator[Replacement]:
    """Yield low-priority replacements for standalone initialisms."""
    validate_initialism_policy(mode=mode, case=case)
    protected = tuple(protected_spans)
    entries = tuple(registered_entries)
    for item in _initialism_decisions(
        text,
        language=language,
        mode=mode,
        registered_mode="expand",
        protected_spans=protected,
        registered_entries=entries,
    ):
        if item.decision != "expand" or item.registry_key is not None:
            continue
        if item.candidate_kind == "dotted":
            rule = "abbr:initialism"
        elif item.reason == "conservative-unknown":
            rule = "abbr:initialism-conservative"
        elif item.reason == "unknown-undotted":
            rule = "abbr:initialism-undotted"
        else:
            continue
        expansion = render_initialism_source(item.source, case=case)
        if should_preserve_sentence_final_period(text, item.end, item.source, expansion):
            expansion += "."
        yield Replacement(
            start=item.start,
            end=item.end,
            text=expansion,
            priority=INITIALISM_FALLBACK_PRIORITY,
            source=rule,
            kind="abbreviation",
            entry_id=rule,
        )


__all__ = [
    "INITIALISM_FALLBACK_PRIORITY",
    "InitialismCase",
    "InitialismDiagnostic",
    "InitialismDiagnosticDecision",
    "InitialismMode",
    "InitialismPolicy",
    "InitialismPreserveToken",
    "RegisteredInitialismMode",
    "iter_initialism_replacements",
    "render_initialism_source",
    "should_preserve_sentence_final_period",
    "validate_initialism_policy",
]
