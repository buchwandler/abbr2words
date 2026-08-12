"""Policy-controlled fallback handling for uppercase initialisms."""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal

from ._replacements import Replacement

# Registered abbreviations and reviewed units deliberately outrank this
# structural fallback. Keep the precedence named so it remains visible at the
# integration point instead of becoming an unexplained magic number.
INITIALISM_FALLBACK_PRIORITY = 50
_DOTTED_INITIALISM = re.compile(r"(?<!\w)(?P<value>(?:[A-Z]\.){2,8})(?!\w)")
_UNDOTTED_INITIALISM = re.compile(r"(?<!\w)(?P<value>[A-Z]{2,8})(?!\w)")
_ROMAN_ONLY = re.compile(r"^[IVXLCDM]+$")

InitialismMode = Literal["dotted_only", "spell_undotted"]
InitialismCase = Literal["source", "upper", "lower"]
RegisteredInitialismMode = Literal["expand", "spell"]


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
    if mode not in {"dotted_only", "spell_undotted"}:
        raise ValueError("initialism_mode must be 'dotted_only' or 'spell_undotted'")
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


def iter_initialism_replacements(
    text: str,
    *,
    mode: InitialismMode = "dotted_only",
    case: InitialismCase = "source",
) -> Iterator[Replacement]:
    """Yield low-priority replacements for standalone initialisms."""
    validate_initialism_policy(mode=mode, case=case)
    patterns = [_DOTTED_INITIALISM]
    if mode == "spell_undotted":
        patterns.append(_UNDOTTED_INITIALISM)

    for pattern in patterns:
        for match in pattern.finditer(text):
            source = match.group("value")
            if pattern is _UNDOTTED_INITIALISM:
                if _ROMAN_ONLY.fullmatch(source) or _is_hyphenated_identifier_component(
                    text, match.start("value"), match.end("value")
                ):
                    continue
                rule = "abbr:initialism-undotted"
            else:
                rule = "abbr:initialism"
            expansion = render_initialism_source(source, case=case)
            if should_preserve_sentence_final_period(text, match.end(), source, expansion):
                expansion += "."
            yield Replacement(
                start=match.start("value"),
                end=match.end("value"),
                text=expansion,
                priority=INITIALISM_FALLBACK_PRIORITY,
                source=rule,
                kind="abbreviation",
                entry_id=rule,
            )


__all__ = [
    "INITIALISM_FALLBACK_PRIORITY",
    "InitialismCase",
    "InitialismMode",
    "InitialismPolicy",
    "RegisteredInitialismMode",
    "iter_initialism_replacements",
    "render_initialism_source",
    "should_preserve_sentence_final_period",
    "validate_initialism_policy",
]
