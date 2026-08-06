"""Internal source-offset replacement planning utilities."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Replacement:
    """A planned replacement against the original source text."""

    start: int
    end: int
    text: str
    priority: int
    source: str


def resolve_replacements(candidates: Iterable[Replacement]) -> tuple[Replacement, ...]:
    """Select a deterministic, non-overlapping set of replacement candidates."""
    ordered = sorted(
        candidates,
        key=lambda item: (
            -item.priority,
            -(item.end - item.start),
            item.start,
            item.source,
        ),
    )
    selected: list[Replacement] = []
    for candidate in ordered:
        if any(candidate.start < item.end and item.start < candidate.end for item in selected):
            continue
        selected.append(candidate)
    return tuple(sorted(selected, key=lambda item: (item.start, item.end, item.source)))


def apply_replacements(text: str, replacements: Sequence[Replacement]) -> str:
    """Apply non-overlapping replacements from right to left."""
    result = text
    for item in sorted(replacements, key=lambda replacement: replacement.start, reverse=True):
        result = result[: item.start] + item.text + result[item.end :]
    return result
