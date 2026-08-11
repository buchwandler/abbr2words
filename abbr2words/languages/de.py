"""German abbreviation lexicon for G2P processing.

This module contains a comprehensive list of common German abbreviations
and their expansions, organized by category.
"""

import warnings

from abbr2words.core import (
    AbbreviationContext,
    AbbreviationEntry,
    AbbreviationExpander,
    ExpansionVariant,
)


class GermanAbbreviationExpander(AbbreviationExpander):
    UNIT_LANGUAGE = "de"
    """Expands German abbreviations with context awareness."""

    def _initialize_abbreviations(self) -> None:
        """Initialize comprehensive German abbreviation list."""

        # =====================================================================
        # TITLES AND HONORIFICS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Hr.",
                expansion="Herr",
                description="Mister (male honorific)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Fr.",
                expansion="Frau",
                description="Mrs/Ms (female honorific)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Dr.",
                expansion="Doktor",
                description="Doctor",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Prof.",
                expansion="Professor",
                description="Professor",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Dipl.-Ing.",
                expansion="Diplom Ingenieur",
                description="Diploma Engineer",
            )
        )

        # =====================================================================
        # DAYS OF THE WEEK
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Mo.",
                expansion="Montag",
                description="Monday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Di.",
                expansion="Dienstag",
                description="Tuesday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Mi.",
                expansion="Mittwoch",
                description="Wednesday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Do.",
                expansion="Donnerstag",
                description="Thursday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Fr.",
                expansion="Freitag",
                context_expansions={
                    AbbreviationContext.TITLE: "Frau",
                    AbbreviationContext.DEFAULT: "Freitag",
                },
                description="Friday or Frau (context-dependent)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Sa.",
                expansion="Samstag",
                description="Saturday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="So.",
                expansion="Sonntag",
                description="Sunday",
            )
        )

        # =====================================================================
        # MONTHS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Jan.",
                expansion="Januar",
                description="January",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Feb.",
                expansion="Februar",
                description="February",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Mär.",
                expansion="März",
                description="March",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Apr.",
                expansion="April",
                description="April",
            )
        )

        # Mai has no abbreviation

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Jun.",
                expansion="Juni",
                description="June",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Jul.",
                expansion="Juli",
                description="July",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Aug.",
                expansion="August",
                description="August",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Sep.",
                expansion="September",
                description="September",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Sept.",
                expansion="September",
                description="September (alternative)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Okt.",
                expansion="Oktober",
                description="October",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Nov.",
                expansion="November",
                description="November",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Dez.",
                expansion="Dezember",
                description="December",
            )
        )

        # =====================================================================
        # PLACES (STREETS, LOCATIONS)
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Str.",
                expansion="Straße",
                description="Street",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Pl.",
                expansion="Platz",
                description="Square/Place",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Allee",
                expansion="Allee",
                description="Avenue (not typically abbreviated)",
            )
        )

        # =====================================================================
        # COMMON ABBREVIATIONS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Lfd. Nr.",
                expansion="laufende Nummer",
                aliases=("Lfd.Nr.",),
                description="Consecutive number, including compact spelling",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="usw.",
                expansion="und so weiter",
                description="And so forth (et cetera)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="bzw.",
                expansion="beziehungsweise",
                description="Respectively/or rather",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="z.B.",
                expansion="zum Beispiel",
                aliases=("z. B.", "z . b .", "zB"),
                description="For example",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="d.h.",
                expansion="das heißt",
                aliases=("d. h.",),
                description="That is",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="u.a.",
                expansion="unter anderem",
                aliases=("u. a.",),
                description="Among other things",
            )
        )

        for abbreviation, expansion, description in (
            ("etc.", "et cetera", "Et cetera"),
            ("zzgl.", "zuzüglich", "Plus/additional"),
            ("Abk.", "Abkürzung", "Abbreviation"),
            ("Abb.", "Abbildung", "Illustration"),
            ("geb.", "geboren", "Born"),
            ("bspw.", "beispielsweise", "For example"),
            ("ggü.", "gegenüber", "Opposite"),
            ("Kap.", "Kapitel", "Chapter"),
            ("Abs.", "Absatz", "Paragraph"),
            ("Abschn.", "Abschnitt", "Section"),
            ("Univ.", "Universität", "University"),
            ("Fa.", "Firma", "Company"),
            ("Tab.", "Tabelle", "Table"),
            ("Tsd.", "Tausend", "Thousand"),
            ("Mio.", "Millionen", "Millions"),
            ("Mrd.", "Milliarden", "Billions"),
        ):
            self.add_abbreviation(
                AbbreviationEntry(
                    abbreviation=abbreviation,
                    expansion=expansion,
                    description=description,
                )
            )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Dipl.-Kfm.",
                expansion="Diplom-Kaufmann",
                aliases=("Dipl. - Kfm.",),
                description="Diploma business economist",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Tel. Nr.",
                expansion="Telefonnummer",
                aliases=("Tel.Nr.", "Tel.-Nr."),
                description="Telephone number",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="St.",
                expansion="St.",
                context_expansions={AbbreviationContext.PLACE: "Sankt"},
                description="Sankt before a proper name",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ca.",
                expansion="zirka",
                description="Approximately",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="evtl.",
                expansion="eventuell",
                variants=(
                    ExpansionVariant(
                        "eventuelle",
                        only_if_preceded_by=r"(?i)\bdie\s+$",
                        only_if_followed_by=r"^\s+[^\W\d_]",
                    ),
                ),
                description="Possibly",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ggf.",
                expansion="gegebenenfalls",
                description="If necessary",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="inkl.",
                expansion="inklusive",
                description="Including",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="exkl.",
                expansion="exklusive",
                description="Excluding",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="max.",
                expansion="maximal",
                variants=(
                    ExpansionVariant(
                        "maximale",
                        only_if_preceded_by=r"(?i)\bdie\s+$",
                        only_if_followed_by=r"^\s+[^\W\d_]",
                    ),
                ),
                description="Maximum",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="min.",
                expansion="minimal",
                case_sensitive=True,
                description="Minimum",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Nr.",
                expansion="Nummer",
                description="Number",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="S.",
                expansion="Seite",
                case_sensitive=True,
                only_if_followed_by=r"^\s*\d",
                description="Page, only before a page number",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Tel.",
                expansion="Telefon",
                description="Telephone",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Fax",
                expansion="Fax",
                description="Fax (not abbreviated)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Std.",
                expansion="Stunde",
                description="Hour",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Min.",
                expansion="Minute",
                case_sensitive=True,
                description="Minute",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Sek.",
                expansion="Sekunde",
                description="Second",
            )
        )

        # =====================================================================
        # BUSINESS/ORGANIZATIONS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="GmbH",
                expansion="Geh Em Beh Hah",
                case_sensitive=True,
                description="Letter-name reading of limited liability company",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="AG",
                expansion="Ah Geh",
                case_sensitive=True,
                description="Letter-name reading of stock corporation",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="e.V.",
                expansion="eingetragener Verein",
                description="Registered association",
            )
        )


# Create a singleton instance for easy access
_expander: GermanAbbreviationExpander | None = None
_expander_context_detection: bool | None = None


def get_expander(enable_context_detection: bool = True) -> GermanAbbreviationExpander:
    """Get the German abbreviation expander instance.

    Args:
        enable_context_detection: Whether to enable context-aware expansion

    Returns:
        The abbreviation expander instance
    """
    global _expander, _expander_context_detection
    if _expander is None:
        _expander = GermanAbbreviationExpander(
            enable_context_detection=enable_context_detection
        )
        _expander_context_detection = enable_context_detection
    elif _expander_context_detection != enable_context_detection:
        warnings.warn(
            "German abbreviation expander already initialized with "
            f"enable_context_detection={_expander_context_detection}. "
            "Call reset_expander() to rebuild with new settings.",
            RuntimeWarning,
            stacklevel=2,
        )
    return _expander


def reset_expander() -> None:
    """Reset the singleton abbreviation expander."""
    global _expander, _expander_context_detection
    _expander = None
    _expander_context_detection = None


from abbr2words.language_data.mature import bundle_from_legacy  # noqa: E402
from abbr2words.languages._bundled import BundledLanguageExpander  # noqa: E402

_LegacyGermanAbbreviationExpander = GermanAbbreviationExpander
GERMAN_BUNDLE = bundle_from_legacy("de", _LegacyGermanAbbreviationExpander)


class GermanAbbreviationExpander(BundledLanguageExpander):  # type: ignore[no-redef]
    UNIT_LANGUAGE = "de"
    BUNDLE = GERMAN_BUNDLE
