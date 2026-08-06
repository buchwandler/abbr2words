"""Provider-neutral token annotations for source-aligned expansion."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections.abc import Iterable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenAnnotation:
    """A provider-neutral token annotation aligned to the source text.

    Offsets use Python string indices: ``text[start:end]``. ``pos`` is
    normally an uppercase coarse Universal POS label; ``tag`` may contain a
    provider-specific fine-grained tag.
    """

    start: int
    end: int
    pos: str | None = None
    tag: str | None = None


def _normalized_label(label: str | None) -> str | None:
    if label is None:
        return None
    if not isinstance(label, str):
        raise ValueError(f"annotation label must be a string or None, got {type(label).__name__}")
    normalized = label.strip()
    return normalized.upper() or None


def normalize_annotations(
    text: str,
    annotations: Iterable[TokenAnnotation] | None,
) -> tuple[TokenAnnotation, ...]:
    """Validate and normalize source-aligned annotations without mutating them."""
    if annotations is None:
        return ()

    normalized: list[TokenAnnotation] = []
    for index, annotation in enumerate(annotations):
        if not isinstance(annotation, TokenAnnotation):
            raise ValueError(f"annotation {index} is not a TokenAnnotation")
        if (
            isinstance(annotation.start, bool)
            or isinstance(annotation.end, bool)
            or not isinstance(annotation.start, int)
            or not isinstance(annotation.end, int)
        ):
            raise ValueError(
                f"annotation {index} has invalid span ({annotation.start!r}, {annotation.end!r})"
            )
        if not 0 <= annotation.start < annotation.end <= len(text):
            raise ValueError(
                f"annotation {index} has invalid span "
                f"({annotation.start}, {annotation.end}) for text length {len(text)}"
            )
        try:
            pos = _normalized_label(annotation.pos)
            tag = _normalized_label(annotation.tag)
        except ValueError as exc:
            raise ValueError(f"annotation {index}: {exc}") from exc
        normalized.append(TokenAnnotation(annotation.start, annotation.end, pos, tag))

    normalized.sort(key=lambda item: (item.start, item.end))
    for index in range(1, len(normalized)):
        previous = normalized[index - 1]
        current = normalized[index]
        if current.start < previous.end:
            raise ValueError(
                f"annotation {index} span ({current.start}, {current.end}) overlaps "
                f"annotation {index - 1} span ({previous.start}, {previous.end})"
            )
    return tuple(normalized)


class AnnotationIndex:
    """Efficient lookup for non-overlapping, source-aligned annotations."""

    def __init__(self, annotations: Sequence[TokenAnnotation]) -> None:
        self.annotations = tuple(annotations)
        self._starts = tuple(annotation.start for annotation in self.annotations)
        self._ends = tuple(annotation.end for annotation in self.annotations)

    def overlapping(self, start: int, end: int) -> tuple[TokenAnnotation, ...]:
        """Return annotations whose spans overlap ``start:end``."""
        if start >= end:
            return ()
        first = bisect_right(self._ends, start)
        last = bisect_left(self._starts, end)
        return tuple(
            annotation
            for annotation in self.annotations[first:last]
            if annotation.end > start and annotation.start < end
        )

    def before(self, offset: int, limit: int = 1) -> tuple[TokenAnnotation, ...]:
        """Return up to ``limit`` annotations ending at or before ``offset``."""
        if limit <= 0:
            return ()
        end = bisect_right(self._ends, offset)
        return tuple(self.annotations[max(0, end - limit) : end][::-1])

    def after(self, offset: int, limit: int = 1) -> tuple[TokenAnnotation, ...]:
        """Return up to ``limit`` annotations starting at or after ``offset``."""
        if limit <= 0:
            return ()
        start = bisect_left(self._starts, offset)
        return tuple(self.annotations[start : start + limit])
