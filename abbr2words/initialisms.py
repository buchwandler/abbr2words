"""Bounded fallback handling for uppercase dotted initialisms."""

from __future__ import annotations

import re
from collections.abc import Iterator

from ._replacements import Replacement

# Registered abbreviations and reviewed units deliberately outrank this
# structural fallback. Keep the precedence named so it remains visible at the
# integration point instead of becoming an unexplained magic number.
INITIALISM_FALLBACK_PRIORITY = 50
_DOTTED_INITIALISM = re.compile(r"(?<!\w)(?P<value>(?:[A-Z]\.){2,8})(?!\w)")


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


def iter_initialism_replacements(text: str) -> Iterator[Replacement]:
    """Yield low-priority replacements for standalone dotted initials."""
    for match in _DOTTED_INITIALISM.finditer(text):
        source = match.group("value")
        expansion = " ".join(source.replace(".", ""))
        if should_preserve_sentence_final_period(text, match.end(), source, expansion):
            expansion += "."
        yield Replacement(
            start=match.start("value"),
            end=match.end("value"),
            text=expansion,
            priority=INITIALISM_FALLBACK_PRIORITY,
            source="abbr:initialism",
            kind="abbreviation",
            entry_id="abbr:initialism",
        )


__all__ = [
    "INITIALISM_FALLBACK_PRIORITY",
    "iter_initialism_replacements",
    "should_preserve_sentence_final_period",
]
