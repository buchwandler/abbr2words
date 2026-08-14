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
from abbr2words.initialisms import InitialismPreserveToken, render_initialism_source


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
    ReviewedInitialism("GTK", aliases=("gtk",), description="GTK toolkit initialism"),
    ReviewedInitialism(
        "HTML", aliases=("html",), description="Hypertext Markup Language initialism"
    ),
    ReviewedInitialism(
        "XML", aliases=("xml",), description="Extensible Markup Language initialism"
    ),
    ReviewedInitialism(
        "XHTML", aliases=("xhtml",), description="Extensible Hypertext Markup Language initialism"
    ),
    ReviewedInitialism(
        "GFDL", aliases=("gfdl",), description="GNU Free Documentation License initialism"
    ),
    ReviewedInitialism("SQL", aliases=("sql",), description="Structured Query Language initialism"),
    ReviewedInitialism("GLSL", aliases=("glsl",), description="OpenGL Shading Language initialism"),
    ReviewedInitialism("IEC", description="International Electrotechnical Commission initialism"),
    ReviewedInitialism("ISBN", description="International Standard Book Number initialism"),
    ReviewedInitialism(
        "ISO", description="International Organization for Standardization initialism"
    ),
    ReviewedInitialism("TV", description="Television initialism"),
)


# Locale-specific review queues. These are case-sensitive source forms: each
# item is a stable letter-spelling initialism rather than a generic uppercase
# guess, and the compact descriptions document the independent review basis.
ENGLISH_REVIEWED_INITIALISMS = tuple(
    ReviewedInitialism(token, description="Common English initialism")
    for token in (
        "FBI",
        "IRS",
        "CIA",
        "UN",
        "DJ",
        "ATM",
        "EU",
        "FDA",
        "CD",
        "PC",
        "UFO",
        "DVD",
        "AI",
        "GPS",
    )
)
GERMAN_REVIEWED_INITIALISMS = tuple(
    ReviewedInitialism(token, description="Common German initialism")
    for token in ("USA", "EU", "WHO", "CDU", "SPD", "ARD", "ZDF", "BND", "DDR", "BRD", "IBM", "WM")
)
SPANISH_REVIEWED_INITIALISMS = tuple(
    ReviewedInitialism(token, description="Common Spanish initialism")
    for token in ("UNAM", "EUA", "ONU", "IMSS", "FBI", "CFE", "ISSSTE", "SRE")
)
FRENCH_REVIEWED_INITIALISMS = tuple(
    ReviewedInitialism(token, description="Common French initialism")
    for token in ("UE", "PDG", "OMS", "FBI", "SNCF", "CIO", "CNRS", "AFP", "RATP", "AIE", "GPS")
)
ITALIAN_REVIEWED_INITIALISMS = tuple(
    ReviewedInitialism(token, description="Common Italian initialism")
    for token in ("USA", "PIL", "FBI", "OMS", "CEO", "ATM", "GPS", "ADSL", "PC", "URL", "DVD")
)


# These records are policy metadata for the unknown-initialism fallback. They
# deliberately do not create replacements: lexical acronyms and ordinary words
# must remain visible to callers as preserved source text.
PRESERVE_INITIALISM_TOKENS = (
    InitialismPreserveToken("NASA", "lexical-acronym"),
    InitialismPreserveToken("NATO", "lexical-acronym"),
    InitialismPreserveToken("FIFA", "lexical-acronym"),
    InitialismPreserveToken("UNESCO", "lexical-acronym"),
    InitialismPreserveToken("AAPL", "structured-candidate"),
    InitialismPreserveToken("NVDA", "structured-candidate"),
    InitialismPreserveToken("AMD", "structured-candidate"),
    InitialismPreserveToken(
        "IN", "ambiguous-uppercase-word", languages=("en", "es", "de", "fr", "it")
    ),
    InitialismPreserveToken(
        "AS", "ambiguous-uppercase-word", languages=("en", "es", "de", "fr", "it")
    ),
    InitialismPreserveToken(
        "AT", "ambiguous-uppercase-word", languages=("en", "es", "de", "fr", "it")
    ),
    InitialismPreserveToken(
        "TO", "ambiguous-uppercase-word", languages=("en", "es", "de", "fr", "it")
    ),
    InitialismPreserveToken(
        "OR", "ambiguous-uppercase-word", languages=("en", "es", "de", "fr", "it")
    ),
    InitialismPreserveToken(
        "NO", "ambiguous-uppercase-word", languages=("en", "es", "de", "fr", "it")
    ),
    # Common uppercase words used to identify a lexical/headline run. This is
    # intentionally small and auditable; it is not a general English lexicon.
    *tuple(
        InitialismPreserveToken(token, "headline-word", languages=("en",))
        for token in (
            "WORLD",
            "FIRST",
            "FILM",
            "GETS",
            "TOP",
            "PRIZE",
            "CANNES",
            "THE",
            "QUICK",
            "BROWN",
            "FOX",
        )
    ),
)


def preserve_initialism_tokens(language: str) -> tuple[InitialismPreserveToken, ...]:
    """Return reviewed fallback-preservation records for *language*."""
    return tuple(record for record in PRESERVE_INITIALISM_TOKENS if record.applies_to(language))


__all__ = [
    "PRESERVE_INITIALISM_TOKENS",
    "ENGLISH_REVIEWED_INITIALISMS",
    "FRENCH_REVIEWED_INITIALISMS",
    "GERMAN_REVIEWED_INITIALISMS",
    "ITALIAN_REVIEWED_INITIALISMS",
    "SPANISH_REVIEWED_INITIALISMS",
    "TECHNICAL_INITIALISMS",
    "InitialismPreserveToken",
    "ReviewedInitialism",
    "preserve_initialism_tokens",
    "register_reviewed_initialisms",
]
