"""Declarative helpers for conservative language abbreviation registries."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from abbr2words.core import AbbreviationContext, AbbreviationEntry, AbbreviationExpander

if TYPE_CHECKING:
    from re import Pattern


@dataclass(frozen=True, slots=True)
class AbbreviationSeed:
    """Data-only description of one reviewed abbreviation."""

    abbreviation: str
    expansion: str
    description: str = ""
    case_sensitive: bool = False
    aliases: tuple[str, ...] = ()
    only_if_preceded_by: str | Pattern[str] | None = None
    only_if_followed_by: str | Pattern[str] | None = None
    context_expansions: Mapping[AbbreviationContext, str] | None = None
    boundary: Literal["word", "custom"] = "word"
    left_boundary: str | None = None
    right_boundary: str | None = None


def register_seeds(expander: AbbreviationExpander, seeds: Iterable[AbbreviationSeed]) -> None:
    """Register immutable seed data through the normal expander API."""
    for seed in seeds:
        expander.add_abbreviation(
            AbbreviationEntry(
                abbreviation=seed.abbreviation,
                expansion=seed.expansion,
                context_expansions=(
                    dict(seed.context_expansions) if seed.context_expansions is not None else None
                ),
                case_sensitive=seed.case_sensitive,
                description=seed.description,
                aliases=seed.aliases,
                only_if_preceded_by=seed.only_if_preceded_by,
                only_if_followed_by=seed.only_if_followed_by,
                boundary=seed.boundary,
                left_boundary=seed.left_boundary,
                right_boundary=seed.right_boundary,
            )
        )
