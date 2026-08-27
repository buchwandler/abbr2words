"""Typed models for source-traceable bundled language data."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from re import Pattern
from typing import Literal

from abbr2words.core import AbbreviationContext, ExpansionVariant


@dataclass(frozen=True, slots=True)
class SourceRef:
    """An authoritative source recorded alongside checked-in language data."""

    id: str
    title: str
    url: str
    version: str | None = None


@dataclass(frozen=True, slots=True)
class AbbreviationSeed:
    """Immutable input for one bundled abbreviation rule."""

    abbreviation: str
    expansion: str
    description: str = ""
    category: Literal[
        "title",
        "reference",
        "calendar",
        "prose",
        "address",
        "academic",
        "organization",
        "other",
    ] = "other"
    case_sensitive: bool = False
    case_policy: Literal["fixed", "sentence"] = "fixed"
    speech_strategy: Literal["expand", "spell_source"] = "expand"
    preserve_sentence_final_period: bool = True
    aliases: tuple[str, ...] = ()
    only_if_preceded_by: str | Pattern[str] | None = None
    only_if_followed_by: str | Pattern[str] | None = None
    only_if_pos: str | Collection[str] | None = None
    not_if_pos: str | Collection[str] | None = None
    context_expansions: Mapping[AbbreviationContext, str] | None = None
    variants: tuple[ExpansionVariant, ...] = ()
    boundary: Literal["word", "custom"] = "word"
    left_boundary: str | None = None
    right_boundary: str | None = None
    source_ids: tuple[str, ...] = ()
    review_note: str = ""


@dataclass(frozen=True, slots=True)
class LanguageBundle:
    """All checked-in abbreviation and unit metadata for one language key."""

    key: str
    abbreviations: tuple[AbbreviationSeed, ...]
    unit_labels: Mapping[str, str]
    sources: tuple[SourceRef, ...]
    coverage: Literal["baseline", "extended", "locale"] = "baseline"


__all__ = ["AbbreviationSeed", "LanguageBundle", "SourceRef"]
