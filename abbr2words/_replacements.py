"""Internal source-offset replacement planning utilities."""

from __future__ import annotations

from bisect import bisect_left
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Literal, TypeAlias

ReplacementKind: TypeAlias = Literal["abbreviation", "unit"]


@dataclass(frozen=True, slots=True)
class Replacement:
    """A planned replacement against the original source text."""

    start: int
    end: int
    text: str
    priority: int
    source: str
    kind: ReplacementKind = "abbreviation"
    entry_id: str = ""
    context: object | None = None
    canonical_id: str | None = None
    abbreviation: str | None = None


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
    starts: list[int] = []
    for candidate in ordered:
        index = bisect_left(starts, candidate.start)
        if index and selected[index - 1].end > candidate.start:
            continue
        if index < len(selected) and candidate.end > selected[index].start:
            continue
        starts.insert(index, candidate.start)
        selected.insert(index, candidate)
    return tuple(sorted(selected, key=lambda item: (item.start, item.end, item.source)))


def apply_replacements(text: str, replacements: Sequence[Replacement]) -> str:
    """Apply non-overlapping replacements from right to left."""
    result = text
    for item in sorted(replacements, key=lambda replacement: replacement.start, reverse=True):
        result = result[: item.start] + item.text + result[item.end :]
    return result
