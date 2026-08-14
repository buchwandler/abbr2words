"""Italian abbreviation expansion for abbr2words.

This module provides Italian-specific abbreviation expansion,
including titles, days, months, streets, and common abbreviations.
"""

from __future__ import annotations

import warnings

from abbr2words.core import (
    AbbreviationContext,
    AbbreviationEntry,
    AbbreviationExpander,
    ExpansionVariant,
)
from abbr2words.language_data.initialisms import (
    ITALIAN_REVIEWED_INITIALISMS,
    TECHNICAL_INITIALISMS,
    register_reviewed_initialisms,
)

# Singleton instance
_expander_instance: ItalianAbbreviationExpander | None = None
_expander_context_detection: bool | None = None


class ItalianAbbreviationExpander(AbbreviationExpander):
    UNIT_LANGUAGE = "it"
    """Expand common Italian abbreviations to full words."""

    def _initialize_abbreviations(self) -> None:
        """Initialize Italian abbreviations."""

        # =====================================================================
        # TITLES
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Sig.",
                expansion="signor",
                case_policy="sentence",
                description="Title for Mr.",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Sig.ra",
                expansion="signora",
                case_policy="sentence",
                description="Title for Mrs.",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Sig.na",
                expansion="signorina",
                case_policy="sentence",
                description="Title for Miss",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Dott.",
                expansion="dottor",
                case_policy="sentence",
                description="Title for Doctor (male)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Dott. Mag.",
                expansion="dottor magistrato",
                case_policy="sentence",
                description="Professional title for magistrate; longest match wins over Mag.",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Dott.ssa",
                expansion="dottoressa",
                case_policy="sentence",
                description="Title for Doctor (female)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Dr.",
                expansion="dottor",
                case_policy="sentence",
                description="Title for Doctor (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Prof.",
                expansion="professore",
                case_policy="sentence",
                description="Title for Professor (male)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Prof.ssa",
                expansion="professoressa",
                case_policy="sentence",
                description="Title for Professor (female)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Ing.",
                expansion="ingegnere",
                case_policy="sentence",
                description="Title for Engineer",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Avv.",
                expansion="avvocato",
                case_policy="sentence",
                description="Title for Lawyer",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Arch.",
                expansion="architetto",
                case_policy="sentence",
                description="Title for Architect",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="M°",
                expansion="maestro",
                case_policy="sentence",
                description="Maestro title",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Coop.",
                expansion="cooperativa",
                description="Cooperative organization",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Cav.",
                expansion="cavaliere",
                case_policy="sentence",
                description="Cavaliere title",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="On.",
                expansion="onorevole",
                case_policy="sentence",
                description="Title for Honorable (member of parliament)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Rag.",
                expansion="ragioniere",
                variants=(
                    ExpansionVariant(
                        "ragioniera",
                        only_if_preceded_by=r"(?i)\b(?:la|una)\s+$",
                    ),
                ),
                case_policy="sentence",
                description="Title for accountant",
            )
        )

        # =====================================================================
        # DAYS OF THE WEEK
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="lun.",
                expansion="lunedì",
                description="Monday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mar.",
                expansion="martedì",
                description="Tuesday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mer.",
                expansion="mercoledì",
                description="Wednesday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="merc.",
                expansion="mercoledì",
                description="Wednesday (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="gio.",
                expansion="giovedì",
                description="Thursday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="giov.",
                expansion="giovedì",
                description="Thursday (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ven.",
                expansion="venerdì",
                description="Friday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="sab.",
                expansion="sabato",
                description="Saturday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="dom.",
                expansion="domenica",
                description="Sunday",
            )
        )

        # =====================================================================
        # MONTHS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="gen.",
                expansion="gennaio",
                context_expansions={
                    AbbreviationContext.DATE: "gennaio",
                    AbbreviationContext.TITLE: "Generale",
                },
                description="January",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="genn.",
                expansion="gennaio",
                description="January (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="feb.",
                expansion="febbraio",
                description="February",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="febbr.",
                expansion="febbraio",
                description="February (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mar.",
                expansion="marzo",
                description="March",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="apr.",
                expansion="aprile",
                description="April",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mag.",
                expansion="maggio",
                context_expansions={
                    AbbreviationContext.DATE: "maggio",
                    AbbreviationContext.ACADEMIC: "Magistrato",
                },
                description="May",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="magg.",
                expansion="maggio",
                description="May (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="giu.",
                expansion="giugno",
                description="June",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="giugno",
                expansion="giugno",
                description="June (full form, rarely abbreviated)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="lug.",
                expansion="luglio",
                description="July",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ago.",
                expansion="agosto",
                description="August",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="agos.",
                expansion="agosto",
                description="August (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="set.",
                expansion="settembre",
                description="September",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="sett.",
                expansion="settembre",
                description="September (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ott.",
                expansion="ottobre",
                description="October",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="nov.",
                expansion="novembre",
                description="November",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="dic.",
                expansion="dicembre",
                description="December",
            )
        )

        # =====================================================================
        # STREETS AND PLACES
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Via",
                expansion="Via",
                description="Street (usually not abbreviated)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="V.",
                expansion="Via",
                description="Street (abbreviated form)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Vle",
                expansion="Viale",
                description="Avenue",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="C.so",
                expansion="Corso",
                description="Main street/avenue",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="P.za",
                expansion="Piazza",
                description="Square/Plaza",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="P.zza",
                expansion="Piazza",
                description="Square (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Lung.",
                expansion="Lungarno",
                description="Riverside street (Florence)",
            )
        )

        # =====================================================================
        # COMMON ABBREVIATIONS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ecc.",
                expansion="eccetera",
                description="Et cetera",
            )
        )

        register_reviewed_initialisms(self, ITALIAN_REVIEWED_INITIALISMS)
        register_reviewed_initialisms(self, TECHNICAL_INITIALISMS)

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="etc.",
                expansion="eccetera",
                description="Et cetera (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="pag.",
                expansion="pagina",
                description="Page",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="pagg.",
                expansion="pagine",
                description="Pages",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="p.",
                expansion="pagina",
                description="Page (short form)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="pp.",
                expansion="pagine",
                description="Pages (short form)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="vol.",
                expansion="volume",
                description="Volume",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="cap.",
                expansion="capitolo",
                description="Chapter",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="n.",
                expansion="numero",
                only_if_followed_by=r"^[ \t]+\d",
                description="Number",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="nr.",
                expansion="numero",
                description="Number (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="n°",
                expansion="numero",
                description="Number (symbol form)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="art.",
                expansion="articolo",
                description="Article",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="cfr.",
                expansion="confronta",
                description="Compare (confer)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="cf.",
                expansion="confronta",
                description="Compare (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ca.",
                expansion="circa",
                description="Approximately",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ed.",
                expansion="edizione",
                description="Edition",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="es.",
                expansion="esempio",
                description="Example",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="p.es.",
                expansion="per esempio",
                description="For example",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ad es.",
                expansion="ad esempio",
                description="For example (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ovv.",
                expansion="ovvero",
                description="That is",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="cioè",
                expansion="cioè",
                description="That is (not abbreviated)",
            )
        )

        # =====================================================================
        # TIME UNITS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="h",
                expansion="ore",
                description="Hour(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="min",
                expansion="minuti",
                description="Minute(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="min.",
                expansion="minuti",
                description="Minute(s) with period",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="sec",
                expansion="secondi",
                description="Second(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="sec.",
                expansion="secondi",
                description="Second(s) with period",
            )
        )

        # =====================================================================
        # MEASUREMENTS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="km",
                expansion="chilometri",
                description="Kilometer(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="m",
                expansion="metri",
                description="Meter(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="cm",
                expansion="centimetri",
                description="Centimeter(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mm",
                expansion="millimetri",
                description="Millimeter(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="kg",
                expansion="chilogrammi",
                description="Kilogram(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="g",
                expansion="grammi",
                description="Gram(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mg",
                expansion="milligrammi",
                description="Milligram(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="l",
                expansion="litri",
                description="Liter(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ml",
                expansion="millilitri",
                description="Milliliter(s)",
            )
        )

        # =====================================================================
        # BUSINESS & ORGANIZATIONS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="S.p.A.",
                expansion="società per azioni",
                case_policy="sentence",
                description="Corporation (similar to Inc.)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="S.r.l.",
                expansion="società a responsabilità limitata",
                case_policy="sentence",
                description="Limited Liability Company",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="S.n.c.",
                expansion="società in nome collettivo",
                case_policy="sentence",
                description="General Partnership",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="S.a.s.",
                expansion="società in accomandita semplice",
                case_policy="sentence",
                description="Limited Partnership",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ONLUS",
                aliases=("Onlus", "onlus"),
                expansion="organizzazione non lucrativa di utilità sociale",
                case_sensitive=True,
                description="Non-profit social utility organization",
            )
        )


def get_expander(enable_context_detection: bool = True) -> ItalianAbbreviationExpander:
    """Get the singleton Italian abbreviation expander instance.

    Args:
        enable_context_detection: Whether to enable context-aware expansion.
            If False, uses simple pattern matching without context analysis.

    Returns:
        The Italian abbreviation expander instance.
    """
    global _expander_instance, _expander_context_detection
    if _expander_instance is None:
        _expander_instance = ItalianAbbreviationExpander(
            enable_context_detection=enable_context_detection
        )
        _expander_context_detection = enable_context_detection
    elif _expander_context_detection != enable_context_detection:
        warnings.warn(
            "Italian abbreviation expander already initialized with "
            f"enable_context_detection={_expander_context_detection}. "
            "Call reset_expander() to rebuild with new settings.",
            RuntimeWarning,
            stacklevel=2,
        )
    return _expander_instance


def reset_expander() -> None:
    """Reset the singleton abbreviation expander."""
    global _expander_instance, _expander_context_detection
    _expander_instance = None
    _expander_context_detection = None


from abbr2words.language_data.mature import bundle_from_legacy  # noqa: E402
from abbr2words.languages._bundled import BundledLanguageExpander  # noqa: E402

_LegacyItalianAbbreviationExpander = ItalianAbbreviationExpander
ITALIAN_BUNDLE = bundle_from_legacy("it", _LegacyItalianAbbreviationExpander)


class ItalianAbbreviationExpander(BundledLanguageExpander):  # type: ignore[no-redef]
    UNIT_LANGUAGE = "it"
    BUNDLE = ITALIAN_BUNDLE
