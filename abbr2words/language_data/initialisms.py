"""Declarative, reviewed initialism entries shared by language registries.

The records in this module are deliberately small. They describe ordinary
``AbbreviationEntry`` objects and do not introduce a second matching engine.
Keeping construction here makes source-spelling intent, aliases, and review
metadata easy to audit in the imperative language modules.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from abbr2words.core import AbbreviationEntry, AbbreviationExpander
from abbr2words.initialisms import render_initialism_source


@dataclass(frozen=True, slots=True)
class ReviewedInitialism:
    """One independently reviewed initialism owned by a language registry."""

    abbreviation: str
    expansion: str | None = None
    description: str = "Reviewed initialism"
    aliases: tuple[str, ...] = ()
    case_sensitive: bool = True

    def to_entry(self) -> AbbreviationEntry:
        """Build the normal registry entry for this reviewed record."""
        expansion = self.expansion or render_initialism_source(self.abbreviation)
        return AbbreviationEntry(
            abbreviation=self.abbreviation,
            expansion=expansion,
            case_sensitive=self.case_sensitive,
            aliases=self.aliases,
            description=self.description,
            speech_strategy="spell_source",
        )


def register_reviewed_initialisms(
    expander: AbbreviationExpander,
    records: Iterable[ReviewedInitialism],
) -> None:
    """Register reviewed records through the existing entry precedence path."""
    for record in records:
        expander.add_abbreviation(record.to_entry())


# These are high-confidence technical labels whose source-letter reading is
# stable across the reviewed Latin-script language registries using them.
TECHNICAL_INITIALISMS = (
    ReviewedInitialism("GTK", description="GTK toolkit initialism"),
    ReviewedInitialism("HTML", description="Hypertext Markup Language initialism"),
    ReviewedInitialism("IEC", description="International Electrotechnical Commission initialism"),
    ReviewedInitialism("ISBN", description="International Standard Book Number initialism"),
    ReviewedInitialism(
        "ISO", description="International Organization for Standardization initialism"
    ),
    ReviewedInitialism("TV", description="Television initialism"),
)


__all__ = [
    "TECHNICAL_INITIALISMS",
    "ReviewedInitialism",
    "register_reviewed_initialisms",
]
