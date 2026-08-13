"""Spanish abbreviation expansion for abbr2words.

This module provides Spanish-specific abbreviation expansion,
including titles, days, months, streets, and common abbreviations.
"""

from __future__ import annotations

import warnings

from abbr2words.core import (
    AbbreviationEntry,
    AbbreviationExpander,
    ExpansionVariant,
)
from abbr2words.language_data.initialisms import (
    TECHNICAL_INITIALISMS,
    register_reviewed_initialisms,
)

# Singleton instance
_expander_instance: SpanishAbbreviationExpander | None = None
_expander_context_detection: bool | None = None


class SpanishAbbreviationExpander(AbbreviationExpander):
    UNIT_LANGUAGE = "es"
    """Expand common Spanish abbreviations to full words."""

    def _initialize_abbreviations(self) -> None:
        """Initialize Spanish abbreviations."""

        # =====================================================================
        # TITLES
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Sr.",
                expansion="señor",
                case_policy="sentence",
                description="Title for Mr.",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Sra.",
                expansion="señora",
                case_policy="sentence",
                description="Title for Mrs.",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Srta.",
                expansion="señorita",
                case_policy="sentence",
                description="Title for Miss",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Dr.",
                expansion="doctor",
                case_policy="sentence",
                description="Title for Doctor (male)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Dra.",
                expansion="doctora",
                case_policy="sentence",
                description="Title for Doctor (female)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Prof.",
                expansion="profesor",
                variants=(
                    ExpansionVariant(
                        "profesora",
                        only_if_preceded_by=r"(?i)\bla\s+$",
                    ),
                ),
                case_policy="sentence",
                description="Title for Professor (male)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Profa.",
                expansion="profesora",
                case_policy="sentence",
                description="Title for Professor (female)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Ing.",
                expansion="ingeniero",
                case_policy="sentence",
                description="Title for Engineer",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Lic.",
                expansion="licenciado",
                case_policy="sentence",
                description="Title for Licentiate (university graduate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Arq.",
                expansion="arquitecto",
                case_policy="sentence",
                description="Title for Architect",
            )
        )

        # =====================================================================
        # DAYS OF THE WEEK
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="lun.",
                expansion="lunes",
                description="Monday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mar.",
                expansion="martes",
                description="Tuesday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mié.",
                expansion="miércoles",
                description="Wednesday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="miér.",
                expansion="miércoles",
                description="Wednesday (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="jue.",
                expansion="jueves",
                description="Thursday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="vie.",
                expansion="viernes",
                description="Friday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="sáb.",
                expansion="sábado",
                description="Saturday",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="dom.",
                expansion="domingo",
                description="Sunday",
            )
        )

        # =====================================================================
        # MONTHS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ene.",
                expansion="enero",
                description="January",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="feb.",
                expansion="febrero",
                description="February",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mar.",
                expansion="marzo",
                description="March (conflicts with Tuesday, context detection needed)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="abr.",
                expansion="abril",
                description="April",
            )
        )

        # Mayo (May) is not typically abbreviated

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="jun.",
                expansion="junio",
                description="June",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="jul.",
                expansion="julio",
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
                abbreviation="sep.",
                expansion="septiembre",
                description="September",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="sept.",
                expansion="septiembre",
                description="September (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="oct.",
                expansion="octubre",
                description="October",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="nov.",
                expansion="noviembre",
                description="November",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="dic.",
                expansion="diciembre",
                description="December",
            )
        )

        # =====================================================================
        # STREETS AND PLACES
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="C/",
                expansion="Calle",
                description="Street",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Avda.",
                expansion="Avenida",
                description="Avenue",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Av.",
                expansion="avenida",
                case_policy="sentence",
                description="Avenue (short form)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Pza.",
                expansion="Plaza",
                description="Plaza/Square",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Pl.",
                expansion="Plaza",
                description="Plaza (short form)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Pº",
                expansion="Paseo",
                description="Promenade/Boulevard",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Pso.",
                expansion="Paseo",
                description="Promenade (alternate)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Ctra.",
                expansion="Carretera",
                description="Highway/Road",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Cmno.",
                expansion="Camino",
                description="Path/Way",
            )
        )

        # =====================================================================
        # COMMON ABBREVIATIONS
        # =====================================================================

        for abbreviation, expansion, description in (
            ("Blvd.", "bulevar", "Boulevard"),
            ("Mtro.", "maestro", "Maestro"),
            ("Gral.", "general", "General"),
            ("Fís.", "físico", "Physical/science abbreviation"),
            ("Pte.", "presidente", "President"),
            ("Fca.", "fábrica", "Factory"),
        ):
            self.add_abbreviation(
                AbbreviationEntry(
                    abbreviation=abbreviation,
                    expansion=expansion,
                    case_policy="sentence" if abbreviation == "Blvd." else "fixed",
                    description=description,
                )
            )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="No.",
                expansion="número",
                aliases=("N.º", "N°"),
                only_if_followed_by=r"^\s*\d",
                description="Number marker before a numeric reference",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="etc.",
                expansion="etcétera",
                description="Et cetera",
            )
        )

        register_reviewed_initialisms(self, TECHNICAL_INITIALISMS)

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="pág.",
                expansion="página",
                case_policy="sentence",
                description="Page",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="págs.",
                expansion="páginas",
                case_policy="sentence",
                description="Pages",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="p.",
                expansion="página",
                description="Page (short form)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="pp.",
                expansion="páginas",
                description="Pages (short form)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="vol.",
                expansion="volumen",
                case_policy="sentence",
                description="Volume",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="cap.",
                expansion="capítulo",
                case_policy="sentence",
                description="Chapter",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="núm.",
                expansion="número",
                description="Number",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="nº",
                expansion="número",
                description="Number (symbol form)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="N°",
                expansion="número",
                description="Number (capital symbol form)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="art.",
                expansion="artículo",
                description="Article",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="cf.",
                expansion="confróntese",
                description="Compare (confer)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="aprox.",
                expansion="aproximadamente",
                description="Approximately",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ed.",
                expansion="edición",
                description="Edition",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ej.",
                expansion="ejemplo",
                variants=(
                    ExpansionVariant(
                        "ejercicio",
                        only_if_followed_by=(
                            r"^\s+\d+\s+"
                            r"(?:resuelto|resuelta|resueltos|resueltas)\b"
                        ),
                    ),
                ),
                case_policy="sentence",
                description="Example",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="p.ej.",
                expansion="por ejemplo",
                description="For example",
            )
        )

        # =====================================================================
        # TIME UNITS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="h",
                expansion="horas",
                description="Hour(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="min",
                expansion="minutos",
                description="Minute(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="min.",
                expansion="minutos",
                description="Minute(s) with period",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="seg",
                expansion="segundos",
                description="Second(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="seg.",
                expansion="segundos",
                description="Second(s) with period",
            )
        )

        # =====================================================================
        # MEASUREMENTS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="km",
                expansion="kilómetros",
                description="Kilometer(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="m",
                expansion="metros",
                description="Meter(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="cm",
                expansion="centímetros",
                description="Centimeter(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mm",
                expansion="milímetros",
                description="Millimeter(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="kg",
                expansion="kilogramos",
                description="Kilogram(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="g",
                expansion="gramos",
                description="Gram(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="mg",
                expansion="miligramos",
                description="Milligram(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="l",
                expansion="litros",
                description="Liter(s)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="ml",
                expansion="mililitros",
                description="Milliliter(s)",
            )
        )

        # =====================================================================
        # BUSINESS & ORGANIZATIONS
        # =====================================================================

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="S.A.",
                expansion="Sociedad Anónima",
                description="Corporation (similar to Inc.)",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="S.L.",
                expansion="Sociedad Limitada",
                description="Limited Liability Company",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Cía.",
                expansion="Compañía",
                description="Company",
            )
        )

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Hnos.",
                expansion="Hermanos",
                description="Brothers",
            )
        )


def get_expander(enable_context_detection: bool = True) -> SpanishAbbreviationExpander:
    """Get the singleton Spanish abbreviation expander instance.

    Args:
        enable_context_detection: Whether to enable context-aware expansion.
            If False, uses simple pattern matching without context analysis.

    Returns:
        The Spanish abbreviation expander instance.
    """
    global _expander_instance, _expander_context_detection
    if _expander_instance is None:
        _expander_instance = SpanishAbbreviationExpander(
            enable_context_detection=enable_context_detection
        )
        _expander_context_detection = enable_context_detection
    elif _expander_context_detection != enable_context_detection:
        warnings.warn(
            "Spanish abbreviation expander already initialized with "
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

_LegacySpanishAbbreviationExpander = SpanishAbbreviationExpander
SPANISH_BUNDLE = bundle_from_legacy("es", _LegacySpanishAbbreviationExpander)


class SpanishAbbreviationExpander(BundledLanguageExpander):  # type: ignore[no-redef]
    UNIT_LANGUAGE = "es"
    BUNDLE = SPANISH_BUNDLE
