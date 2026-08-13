"""Reviewed quantity-unit inventory and numeric-aware unit expansion."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping, Set
from dataclasses import dataclass, replace
from typing import Literal

from ._replacements import Replacement, apply_replacements
from .unit_data import entries as external_unit_entries

NUMBER_BEFORE_UNIT = (
    r"(?:^|[^\w.])"
    r"[+\-−]?"
    r"(?:\d{1,3}(?:[ \u00a0\u202f]\d{3})+|\d+)"
    r"(?:[.,]\d+)?"
    r"[ \t\u00a0\u202f]*$"
)


@dataclass(frozen=True, slots=True)
class NumericFormatProfile:
    """Recognition-only numeric punctuation policy for a language family."""

    decimal_separators: tuple[str, ...]
    grouping_separators: tuple[str, ...]
    grouping: Literal["western", "indian", "flexible"]


NUMERIC_FORMAT_PROFILES = {
    "default": NumericFormatProfile(
        decimal_separators=(".", ",", "٫"),
        grouping_separators=(",", ".", " ", "\u00a0", "\u202f", "٬"),
        grouping="flexible",
    ),
    "en": NumericFormatProfile(
        decimal_separators=(".",),
        grouping_separators=(",", " ", "\u00a0", "\u202f"),
        grouping="western",
    ),
}

UnitAmbiguity = Literal[
    "none",
    "lexical",
    "bare_symbol",
]


def numeric_format_profile(language: str) -> NumericFormatProfile:
    """Return the recognition profile used for a language key."""
    return NUMERIC_FORMAT_PROFILES.get(language, NUMERIC_FORMAT_PROFILES["default"])


@dataclass(frozen=True)
class UnitEntry:
    """A localized unit spelling recognized only after a numeric quantity."""

    symbols: tuple[str, ...]
    expansion: str
    case_sensitive: bool = True
    description: str = ""
    canonical_symbol: str | None = None
    requires_numeric_value: bool = True
    canonical_id: str | None = None
    reject_following_apostrophe: bool = False
    category: str = "unit"
    quantity_position: str = "suffix"
    allow_lexical_overlap: bool = False
    preserve_sentence_final_period: bool = False
    reject_following_period: bool = False
    requires_separator: bool = False

    def __post_init__(self) -> None:
        if not self.symbols or any(
            not isinstance(symbol, str) or not symbol for symbol in self.symbols
        ):
            raise ValueError("unit symbols must contain non-empty strings")
        if not isinstance(self.expansion, str):
            raise TypeError("unit expansion must be a string")
        if not self.expansion:
            raise ValueError("unit expansion must not be empty")
        if type(self.case_sensitive) is not bool:
            raise TypeError("unit case_sensitive must be a bool")
        if type(self.requires_numeric_value) is not bool:
            raise TypeError("unit requires_numeric_value must be a bool")
        if self.canonical_symbol is not None and self.canonical_symbol not in self.symbols:
            raise ValueError("canonical_symbol must be one of symbols")
        if self.canonical_id is not None and not self.canonical_id:
            raise ValueError("canonical_id must not be empty")
        if not isinstance(self.category, str):
            raise TypeError("unit category must be a string")
        if not self.category:
            raise ValueError("unit category must not be empty")
        if not isinstance(self.quantity_position, str):
            raise TypeError("unit quantity_position must be a string")
        if self.quantity_position not in {"prefix", "suffix", "both"}:
            raise ValueError("unit quantity_position must be 'prefix', 'suffix', or 'both'")
        if type(self.allow_lexical_overlap) is not bool:
            raise TypeError("unit allow_lexical_overlap must be a bool")
        if type(self.preserve_sentence_final_period) is not bool:
            raise TypeError("unit preserve_sentence_final_period must be a bool")
        if type(self.reject_following_period) is not bool:
            raise TypeError("unit reject_following_period must be a bool")
        if type(self.requires_separator) is not bool:
            raise TypeError("unit requires_separator must be a bool")


@dataclass(frozen=True, slots=True)
class UnitMatch:
    """One immutable, source-aligned recognized numeric quantity symbol."""

    start: int
    end: int
    value_start: int
    value_end: int
    value: str
    symbol: str
    canonical_id: str | None
    canonical_symbol: str
    expansion: str
    language: str
    category: str = "unit"
    ambiguity: UnitAmbiguity = "none"
    separator: str = ""


@dataclass(frozen=True, slots=True)
class UnitDiagnostic:
    """A concise decision record for one reviewed numeric unit candidate."""

    start: int
    end: int
    value: str
    symbol: str
    canonical_id: str | None
    language: str
    status: Literal["accepted", "rejected"]
    reason: str | None = None
    ambiguity: UnitAmbiguity = "none"
    separator: str = ""


@dataclass(frozen=True)
class _UnitDefinition:
    canonical_id: str
    symbols: tuple[str, ...]
    description: str
    reject_following_period: bool = False
    requires_separator: bool = False


def _entry(
    symbols: str | tuple[str, ...],
    expansion: str,
    description: str,
    *,
    canonical_id: str | None = None,
    reject_following_apostrophe: bool = False,
    case_sensitive: bool = True,
    category: str = "unit",
    canonical_symbol: str | None = None,
    quantity_position: str = "suffix",
    allow_lexical_overlap: bool = False,
    preserve_sentence_final_period: bool = False,
    reject_following_period: bool = False,
    requires_separator: bool = False,
) -> UnitEntry:
    if isinstance(symbols, str):
        symbols = (symbols,)
    return UnitEntry(
        symbols,
        expansion,
        case_sensitive=case_sensitive,
        description=description,
        canonical_symbol=canonical_symbol or symbols[0],
        canonical_id=canonical_id,
        reject_following_apostrophe=reject_following_apostrophe,
        category=category,
        quantity_position=quantity_position,
        allow_lexical_overlap=allow_lexical_overlap,
        preserve_sentence_final_period=preserve_sentence_final_period,
        reject_following_period=reject_following_period,
        requires_separator=requires_separator,
    )


# This is a reviewed inventory, not an attempt to model every UCUM expression.
_EN: tuple[UnitEntry, ...] = (
    _entry("mm", "millimeter", "Length"),
    _entry("cm", "centimeter", "Length"),
    _entry("m", "meter", "Length"),
    _entry("km", "kilometer", "Length"),
    _entry(("mm²", "mm2"), "square millimeter", "Area"),
    _entry(("cm²", "cm2"), "square centimeter", "Area"),
    _entry(("m²", "m2"), "square meter", "Area"),
    _entry(("km²", "km2"), "square kilometer", "Area"),
    _entry("ha", "hectare", "Area"),
    _entry(("mm³", "mm3"), "cubic millimeter", "Volume"),
    _entry(("cm³", "cm3"), "cubic centimeter", "Volume"),
    _entry(("m³", "m3"), "cubic meter", "Volume"),
    _entry("mL", "milliliter", "Volume"),
    _entry("L", "liter", "Volume"),
    _entry("ml", "milliliter", "Volume"),
    _entry("l", "liter", "Volume"),
    _entry(("µg", "μg", "ug"), "microgram", "Mass"),
    _entry("mg", "milligram", "Mass"),
    _entry("g", "gram", "Mass"),
    _entry("kg", "kilogram", "Mass"),
    _entry("t", "tonne", "Mass"),
    _entry(
        ("°C", "° C", "C", "C."),
        "degree Celsius",
        "Temperature",
        case_sensitive=False,
        preserve_sentence_final_period=True,
    ),
    _entry(
        ("°F", "° F", "F", "F."),
        "degree Fahrenheit",
        "Temperature",
        case_sensitive=False,
        preserve_sentence_final_period=True,
    ),
    _entry("K", "kelvin", "Temperature", requires_separator=True),
    _entry("m/s", "meter per second", "Speed"),
    _entry("km/h", "kilometer per hour", "Speed"),
    _entry(("s", "sec", "sec."), "second", "Duration"),
    _entry(("min", "min."), "minute", "Duration"),
    _entry(("h", "hr.", "hrs."), "hour", "Duration"),
    _entry("d", "day", "Duration"),
    _entry(("yr", "yr.", "yrs."), "year", "Duration"),
    _entry(("in", "in."), "inch", "Customary length"),
    _entry(("ft", "ft."), "foot", "Customary length"),
    _entry(("yd", "yd."), "yard", "Customary length"),
    _entry(("mi", "mi."), "mile", "Customary length"),
    _entry(("oz", "oz."), "ounce", "Customary mass"),
    _entry(("lb", "lb.", "lbs", "lbs."), "pound", "Customary mass"),
    _entry(("gal", "gal."), "gallon", "Customary volume"),
    _entry(("qt", "qt."), "quart", "Customary volume"),
    _entry(("pt", "pt."), "pint", "Customary volume"),
    _entry(("tsp", "tsp."), "teaspoon", "Customary volume"),
    _entry(("tbsp", "tbsp."), "tablespoon", "Customary volume"),
)

_EN_CANONICAL_IDS = {
    "mm": "length-millimeter",
    "cm": "length-centimeter",
    "m": "length-meter",
    "km": "length-kilometer",
    "mm²": "area-square-millimeter",
    "cm²": "area-square-centimeter",
    "m²": "area-square-meter",
    "km²": "area-square-kilometer",
    "ha": "area-hectare",
    "mm³": "volume-cubic-millimeter",
    "cm³": "volume-cubic-centimeter",
    "m³": "volume-cubic-meter",
    "mL": "volume-milliliter",
    "L": "volume-liter",
    "ml": "volume-milliliter",
    "l": "volume-liter",
    "µg": "mass-microgram",
    "μg": "mass-microgram",
    "ug": "mass-microgram",
    "mg": "mass-milligram",
    "g": "mass-gram",
    "kg": "mass-kilogram",
    "t": "mass-tonne",
    "°C": "temperature-celsius",
    "°F": "temperature-fahrenheit",
    "K": "temperature-kelvin",
    "m/s": "speed-meter-per-second",
    "km/h": "speed-kilometer-per-hour",
    "s": "duration-second",
    "min": "duration-minute",
    "h": "duration-hour",
    "d": "duration-day",
    "yr": "duration-year",
    "in": "customary-inch",
    "ft": "customary-foot",
    "yd": "customary-yard",
    "mi": "customary-mile",
    "oz": "customary-ounce",
    "lb": "customary-pound",
    "gal": "customary-gallon",
    "qt": "customary-quart",
    "pt": "customary-pint",
    "tsp": "customary-teaspoon",
    "tbsp": "customary-tablespoon",
}
_EN = tuple(replace(entry, canonical_id=_EN_CANONICAL_IDS[entry.symbols[0]]) for entry in _EN)

_BASE_DEFINITIONS = (
    _UnitDefinition("duration-second", ("s",), "Duration"),
    _UnitDefinition("duration-minute", ("min",), "Duration"),
    _UnitDefinition("duration-hour", ("h",), "Duration"),
    _UnitDefinition("duration-day", ("d",), "Duration"),
    _UnitDefinition("length-millimeter", ("mm",), "Length"),
    _UnitDefinition("length-centimeter", ("cm",), "Length"),
    _UnitDefinition("length-meter", ("m",), "Length"),
    _UnitDefinition("length-kilometer", ("km",), "Length"),
    _UnitDefinition("volume-milliliter", ("ml", "mL"), "Volume"),
    _UnitDefinition("volume-liter", ("l", "L"), "Volume"),
    _UnitDefinition("mass-microgram", ("µg", "μg", "ug"), "Mass"),
    _UnitDefinition("mass-milligram", ("mg",), "Mass"),
    _UnitDefinition("mass-gram", ("g",), "Mass"),
    _UnitDefinition("mass-kilogram", ("kg",), "Mass"),
    _UnitDefinition("mass-tonne", ("t",), "Mass"),
    _UnitDefinition("temperature-kelvin", ("K",), "Temperature", requires_separator=True),
    _UnitDefinition("temperature-celsius", ("°C",), "Temperature"),
    _UnitDefinition("temperature-fahrenheit", ("°F",), "Temperature"),
    _UnitDefinition("speed-meter-per-second", ("m/s",), "Speed"),
    _UnitDefinition("speed-kilometer-per-hour", ("km/h",), "Speed"),
)

_LOCALIZED_UNIT_NAMES: dict[str, dict[str, str]] = {
    "cs": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "sekunda",
                "minuta",
                "hodina",
                "den",
                "milimetr",
                "centimetr",
                "metr",
                "kilometr",
                "mililitr",
                "litr",
                "mikrogram",
                "miligram",
                "gram",
                "kilogram",
                "tuna",
                "kelvin",
                "stupeň Celsia",
                "stupeň Fahrenheita",
                "metr za sekundu",
                "kilometr za hodinu",
            ),
            strict=True,
        )
    ),
    "de": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "Sekunde",
                "Minute",
                "Stunde",
                "Tag",
                "Millimeter",
                "Zentimeter",
                "Meter",
                "Kilometer",
                "Milliliter",
                "Liter",
                "Mikrogramm",
                "Milligramm",
                "Gramm",
                "Kilogramm",
                "Tonne",
                "Kelvin",
                "Grad Celsius",
                "Grad Fahrenheit",
                "Meter pro Sekunde",
                "Kilometer pro Stunde",
            ),
            strict=True,
        )
    ),
    "es": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "segundo",
                "minuto",
                "hora",
                "día",
                "milímetro",
                "centímetro",
                "metro",
                "kilómetro",
                "mililitro",
                "litro",
                "microgramo",
                "miligramo",
                "gramo",
                "kilogramo",
                "tonelada",
                "kelvin",
                "grado Celsius",
                "grado Fahrenheit",
                "metro por segundo",
                "kilómetro por hora",
            ),
            strict=True,
        )
    ),
    "fr": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "seconde",
                "minute",
                "heure",
                "jour",
                "millimètre",
                "centimètre",
                "mètre",
                "kilomètre",
                "millilitre",
                "litre",
                "microgramme",
                "milligramme",
                "gramme",
                "kilogramme",
                "tonne",
                "kelvin",
                "degré Celsius",
                "degré Fahrenheit",
                "mètre par seconde",
                "kilomètre par heure",
            ),
            strict=True,
        )
    ),
    "it": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "secondo",
                "minuto",
                "ora",
                "giorno",
                "millimetro",
                "centimetro",
                "metro",
                "chilometro",
                "millilitro",
                "litro",
                "microgrammo",
                "milligrammo",
                "grammo",
                "chilogrammo",
                "tonnellata",
                "kelvin",
                "grado Celsius",
                "grado Fahrenheit",
                "metro al secondo",
                "chilometro all'ora",
            ),
            strict=True,
        )
    ),
    "pt": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "segundo",
                "minuto",
                "hora",
                "dia",
                "milímetro",
                "centímetro",
                "metro",
                "quilômetro",
                "mililitro",
                "litro",
                "micrograma",
                "miligrama",
                "grama",
                "quilograma",
                "tonelada",
                "kelvin",
                "grau Celsius",
                "grau Fahrenheit",
                "metro por segundo",
                "quilômetro por hora",
            ),
            strict=True,
        )
    ),
    "nl": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "seconde",
                "minuut",
                "uur",
                "dag",
                "millimeter",
                "centimeter",
                "meter",
                "kilometer",
                "milliliter",
                "liter",
                "microgram",
                "milligram",
                "gram",
                "kilogram",
                "metrische ton",
                "kelvin",
                "graad Celsius",
                "graad Fahrenheit",
                "meter per seconde",
                "kilometer per uur",
            ),
            strict=True,
        )
    ),
    "sv": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "sekund",
                "minut",
                "timme",
                "dag",
                "millimeter",
                "centimeter",
                "meter",
                "kilometer",
                "milliliter",
                "liter",
                "mikrogram",
                "milligram",
                "gram",
                "kilogram",
                "ton",
                "kelvin",
                "grad Celsius",
                "grad Fahrenheit",
                "meter per sekund",
                "kilometer per timme",
            ),
            strict=True,
        )
    ),
    "pl": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "sekunda",
                "minuta",
                "godzina",
                "dzień",
                "milimetr",
                "centymetr",
                "metr",
                "kilometr",
                "mililitr",
                "litr",
                "mikrogram",
                "miligram",
                "gram",
                "kilogram",
                "tona",
                "kelwin",
                "stopień Celsjusza",
                "stopień Fahrenheita",
                "metr na sekundę",
                "kilometr na godzinę",
            ),
            strict=True,
        )
    ),
    "ru": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "секунда",
                "минута",
                "час",
                "день",
                "миллиметр",
                "сантиметр",
                "метр",
                "километр",
                "миллилитр",
                "литр",
                "микрограмм",
                "миллиграмм",
                "грамм",
                "килограмм",
                "тонна",
                "кельвин",
                "градус Цельсия",
                "градус Фаренгейта",
                "метр в секунду",
                "километр в час",
            ),
            strict=True,
        )
    ),
    "tr": dict(
        zip(
            (definition.canonical_id for definition in _BASE_DEFINITIONS),
            (
                "saniye",
                "dakika",
                "saat",
                "gün",
                "milimetre",
                "santimetre",
                "metre",
                "kilometre",
                "mililitre",
                "litre",
                "mikrogram",
                "miligram",
                "gram",
                "kilogram",
                "ton",
                "kelvin",
                "Celsius derece",
                "Fahrenheit derece",
                "saniyede metre",
                "saatte kilometre",
            ),
            strict=True,
        )
    ),
}

_LOCALIZED_ALIASES = {
    "cs": (
        ("hod.", "hodina", "duration-hour", True),
        ("min.", "minuta", "duration-minute", True),
        ("sek.", "sekunda", "duration-second", True),
    ),
    "de": (
        ("Std.", "Stunde", "duration-hour", False),
        ("Min.", "Minute", "duration-minute", False),
        ("Sek.", "Sekunde", "duration-second", False),
    ),
    "es": (
        ("min.", "minuto", "duration-minute", True),
        ("seg", "segundo", "duration-second", True),
        ("seg.", "segundo", "duration-second", True),
    ),
    "fr": (("sec", "seconde", "duration-second", True),),
    "it": (
        ("min.", "minuto", "duration-minute", True),
        ("sec", "secondo", "duration-second", True),
        ("sec.", "secondo", "duration-second", True),
    ),
    "pt": (
        ("min.", "minuto", "duration-minute", True),
        ("seg", "segundo", "duration-second", True),
        ("seg.", "segundo", "duration-second", True),
    ),
}

_STRUCTURED_CURRENCY_ENTRIES = {
    "en": (
        _entry(
            ("€", "EUR"),
            "euro",
            "Currency",
            canonical_id="currency-euro",
            canonical_symbol="€",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("$", "USD"),
            "US dollar",
            "Currency",
            canonical_id="currency-us-dollar",
            canonical_symbol="$",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("£", "GBP"),
            "pound sterling",
            "Currency",
            canonical_id="currency-pound-sterling",
            canonical_symbol="£",
            category="currency",
            quantity_position="both",
        ),
    ),
    "cs": (
        _entry(
            ("Kč", "CZK"),
            "česká koruna",
            "Currency",
            canonical_id="currency-czech-koruna",
            canonical_symbol="Kč",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("€", "EUR"),
            "euro",
            "Currency",
            canonical_id="currency-euro",
            canonical_symbol="€",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("$", "USD"),
            "americký dolar",
            "Currency",
            canonical_id="currency-us-dollar",
            canonical_symbol="$",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("£", "GBP"),
            "libra šterlinků",
            "Currency",
            canonical_id="currency-pound-sterling",
            canonical_symbol="£",
            category="currency",
            quantity_position="both",
        ),
    ),
    "fr": (
        _entry(
            ("€", "EUR"),
            "euro",
            "Currency",
            canonical_id="currency-euro",
            canonical_symbol="€",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("$", "USD"),
            "US dollar",
            "Currency",
            canonical_id="currency-us-dollar",
            canonical_symbol="$",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("£", "GBP"),
            "pound sterling",
            "Currency",
            canonical_id="currency-pound-sterling",
            canonical_symbol="£",
            category="currency",
            quantity_position="both",
        ),
    ),
    "es": (
        _entry(
            ("€", "EUR"),
            "euro",
            "Currency",
            canonical_id="currency-euro",
            canonical_symbol="€",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("$", "USD"),
            "dólar estadounidense",
            "Currency",
            canonical_id="currency-us-dollar",
            canonical_symbol="$",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("£", "GBP"),
            "libra esterlina",
            "Currency",
            canonical_id="currency-pound-sterling",
            canonical_symbol="£",
            category="currency",
            quantity_position="both",
        ),
    ),
    "it": (
        _entry(
            ("€", "EUR"),
            "euro",
            "Currency",
            canonical_id="currency-euro",
            canonical_symbol="€",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("$", "USD"),
            "dollaro statunitense",
            "Currency",
            canonical_id="currency-us-dollar",
            canonical_symbol="$",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("£", "GBP"),
            "sterlina britannica",
            "Currency",
            canonical_id="currency-pound-sterling",
            canonical_symbol="£",
            category="currency",
            quantity_position="both",
        ),
    ),
    "pt": (
        _entry(
            ("€", "EUR"),
            "euro",
            "Currency",
            canonical_id="currency-euro",
            canonical_symbol="€",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("$", "USD"),
            "dólar americano",
            "Currency",
            canonical_id="currency-us-dollar",
            canonical_symbol="$",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("£", "GBP"),
            "libra esterlina",
            "Currency",
            canonical_id="currency-pound-sterling",
            canonical_symbol="£",
            category="currency",
            quantity_position="both",
        ),
        _entry(
            ("R$", "BRL"),
            "real",
            "Currency",
            canonical_id="currency-brazilian-real",
            canonical_symbol="R$",
            category="currency",
            quantity_position="both",
        ),
    ),
}

_FRENCH_DOTTED_DURATION_ENTRIES = (
    _entry(
        "min.",
        "minute",
        "Locale duration alias",
        canonical_id="duration-minute",
        allow_lexical_overlap=True,
        preserve_sentence_final_period=True,
    ),
    _entry(
        "sec.",
        "seconde",
        "Locale duration alias",
        canonical_id="duration-second",
        preserve_sentence_final_period=True,
    ),
)

_GERMAN_REQUIRED_ENTRIES = (
    _entry(
        "Stck.",
        "Stück",
        "Count",
        canonical_id="count-piece",
        case_sensitive=False,
    ),
    _entry(
        "ltr.",
        "Liter",
        "Volume",
        canonical_id="volume-liter",
        case_sensitive=False,
    ),
    _entry(
        "Tsd.",
        "Tausend",
        "Magnitude",
        canonical_id="magnitude-thousand",
        category="magnitude",
        case_sensitive=False,
    ),
    _entry(
        "Mio.",
        "Millionen",
        "Magnitude",
        canonical_id="magnitude-million",
        category="magnitude",
        case_sensitive=False,
    ),
    _entry(
        "Mrd.",
        "Milliarden",
        "Magnitude",
        canonical_id="magnitude-billion",
        category="magnitude",
        case_sensitive=False,
    ),
    _entry(
        "EUR",
        "Euro",
        "Currency",
        canonical_id="currency-euro",
        category="currency",
    ),
)

_EXTENDED_DEFINITIONS = (
    _UnitDefinition("area-square-millimeter", ("mm²", "mm2"), "Area"),
    _UnitDefinition("area-square-centimeter", ("cm²", "cm2"), "Area"),
    _UnitDefinition("area-square-meter", ("m²", "m2"), "Area"),
    _UnitDefinition("area-square-kilometer", ("km²", "km2"), "Area"),
    _UnitDefinition("area-hectare", ("ha",), "Area"),
    _UnitDefinition("volume-cubic-millimeter", ("mm³", "mm3"), "Volume"),
    _UnitDefinition("volume-cubic-centimeter", ("cm³", "cm3"), "Volume"),
    _UnitDefinition("volume-cubic-meter", ("m³", "m3"), "Volume"),
)

_POLYNORM_DEFINITIONS = (
    _UnitDefinition("speed-mile-per-hour", ("mph",), "Speed"),
    _UnitDefinition("pressure-pascal", ("Pa",), "Pressure"),
    _UnitDefinition("pressure-kilopascal", ("kPa",), "Pressure"),
    _UnitDefinition("pressure-atmosphere", ("atm",), "Pressure"),
    _UnitDefinition("data-byte", ("B",), "Data", requires_separator=True),
    _UnitDefinition("data-kilobyte", ("kB",), "Data"),
    _UnitDefinition("data-megabyte", ("MB",), "Data"),
    _UnitDefinition("data-gigabyte", ("GB",), "Data"),
    _UnitDefinition(
        "fuel-consumption-liter-per-100-kilometer",
        ("L/100km",),
        "Fuel consumption",
    ),
    _UnitDefinition("flow-cubic-meter-per-second", ("m³/s", "m3/s"), "Flow"),
    _UnitDefinition("power-watt", ("W",), "Power", reject_following_period=True),
    _UnitDefinition("power-kilowatt", ("kW",), "Power"),
    _UnitDefinition("energy-watt-hour", ("Wh",), "Energy"),
    _UnitDefinition("energy-kilowatt-hour", ("kWh",), "Energy"),
    _UnitDefinition("frequency-hertz", ("Hz",), "Frequency"),
    _UnitDefinition("frequency-kilohertz", ("kHz",), "Frequency"),
    _UnitDefinition("frequency-megahertz", ("MHz",), "Frequency"),
    _UnitDefinition("frequency-gigahertz", ("GHz",), "Frequency"),
    _UnitDefinition("length-nanometer", ("nm",), "Length"),
    _UnitDefinition("current-ampere", ("A",), "Electric current", requires_separator=True),
    _UnitDefinition("current-milliampere", ("mA",), "Electric current"),
    _UnitDefinition("charge-milliampere-hour", ("mAh",), "Electric charge"),
    _UnitDefinition("voltage-volt", ("V",), "Electric potential"),
    _UnitDefinition("luminous-flux-lumen", ("lm",), "Luminous flux"),
    _UnitDefinition("force-newton", ("N",), "Force", reject_following_period=True),
    _UnitDefinition("energy-joule", ("J",), "Energy"),
    _UnitDefinition("pressure-millimeter-mercury", ("mmHg",), "Pressure"),
    _UnitDefinition("amount-mole", ("mol",), "Amount of substance"),
    _UnitDefinition("concentration-molar", ("M",), "Molar concentration"),
)

_POLYNORM_UNIT_LABELS = {
    "en": (
        "mile per hour",
        "pascal",
        "kilopascal",
        "atmosphere",
        "byte",
        "kilobyte",
        "megabyte",
        "gigabyte",
        "liter per 100 kilometers",
        "cubic meter per second",
        "watt",
        "kilowatt",
        "watt-hour",
        "kilowatt-hour",
        "hertz",
        "kilohertz",
        "megahertz",
        "gigahertz",
        "nanometer",
        "ampere",
        "milliampere",
        "milliampere-hour",
        "volt",
        "lumen",
        "newton",
        "joule",
        "millimeter of mercury",
        "mole",
        "molar",
    ),
    "de": (
        "Meile pro Stunde",
        "Pascal",
        "Kilopascal",
        "Atmosphäre",
        "Byte",
        "Kilobyte",
        "Megabyte",
        "Gigabyte",
        "Liter pro 100 Kilometer",
        "Kubikmeter pro Sekunde",
        "Watt",
        "Kilowatt",
        "Wattstunde",
        "Kilowattstunde",
        "Hertz",
        "Kilohertz",
        "Megahertz",
        "Gigahertz",
        "Nanometer",
        "Ampere",
        "Milliampere",
        "Milliampere-Stunde",
        "Volt",
        "Lumen",
        "Newton",
        "Joule",
        "Millimeter Quecksilbersäule",
        "Mol",
        "molar",
    ),
    "es": (
        "milla por hora",
        "pascal",
        "kilopascal",
        "atmósfera",
        "byte",
        "kilobyte",
        "megabyte",
        "gigabyte",
        "litro por 100 kilómetros",
        "metro cúbico por segundo",
        "vatio",
        "kilovatio",
        "vatio-hora",
        "kilovatio-hora",
        "hercio",
        "kilohercio",
        "megahercio",
        "gigahercio",
        "nanómetro",
        "amperio",
        "miliamperio",
        "miliamperio-hora",
        "voltio",
        "lumen",
        "newton",
        "julio",
        "milímetro de mercurio",
        "mol",
        "molar",
    ),
    "fr": (
        "mille par heure",
        "pascal",
        "kilopascal",
        "atmosphère",
        "octet",
        "kilooctet",
        "mégaoctet",
        "gigaoctet",
        "litre aux 100 kilomètres",
        "mètre cube par seconde",
        "watt",
        "kilowatt",
        "watt-heure",
        "kilowatt-heure",
        "hertz",
        "kilohertz",
        "mégahertz",
        "gigahertz",
        "nanomètre",
        "ampère",
        "milliampère",
        "milliampère-heure",
        "volt",
        "lumen",
        "newton",
        "joule",
        "millimètre de mercure",
        "mole",
        "molaire",
    ),
    "it": (
        "miglio all'ora",
        "pascal",
        "kilopascal",
        "atmosfera",
        "byte",
        "kilobyte",
        "megabyte",
        "gigabyte",
        "litro per 100 chilometri",
        "metro cubo al secondo",
        "watt",
        "chilowatt",
        "wattora",
        "chilowattora",
        "hertz",
        "kilohertz",
        "megahertz",
        "gigahertz",
        "nanometro",
        "ampere",
        "milliampere",
        "milliampere-ora",
        "volt",
        "lumen",
        "newton",
        "joule",
        "millimetro di mercurio",
        "mole",
        "molare",
    ),
}

_POLYNORM_CURRENCY_LABELS = {
    "en": ("Japanese yen", "Swiss franc", "Indian rupee", "South Korean won", "Mexican peso"),
    "de": (
        "japanischer Yen",
        "Schweizer Franken",
        "indische Rupie",
        "südkoreanischer Won",
        "mexikanischer Peso",
    ),
    "es": ("yen japonés", "franco suizo", "rupia india", "won surcoreano", "peso mexicano"),
    "fr": ("yen japonais", "franc suisse", "roupie indienne", "won sud-coréen", "peso mexicain"),
    "it": (
        "yen giapponese",
        "franco svizzero",
        "rupia indiana",
        "won sudcoreano",
        "peso messicano",
    ),
}


def _polynorm_unit_entries(language: str) -> tuple[UnitEntry, ...]:
    labels = _POLYNORM_UNIT_LABELS.get(language, _POLYNORM_UNIT_LABELS["en"])
    return tuple(
        _entry(
            definition.symbols,
            labels[index],
            definition.description,
            canonical_id=definition.canonical_id,
            reject_following_period=definition.reject_following_period,
            requires_separator=definition.requires_separator,
        )
        for index, definition in enumerate(_POLYNORM_DEFINITIONS)
    )


_POLYNORM_POUND_LABELS = {
    "de": "Pfund",
    "es": "libra",
    "fr": "livre",
    "it": "libbra",
}


def _polynorm_pound_entries(language: str) -> tuple[UnitEntry, ...]:
    """Return reviewed non-English customary-pound aliases."""
    if language == "en" or language not in _POLYNORM_POUND_LABELS:
        return ()
    return (
        _entry(
            ("lb", "lbs"),
            _POLYNORM_POUND_LABELS[language],
            "Customary mass",
            canonical_id="customary-pound",
        ),
    )


def _polynorm_currency_entries(language: str) -> tuple[UnitEntry, ...]:
    labels = _POLYNORM_CURRENCY_LABELS.get(language, _POLYNORM_CURRENCY_LABELS["en"])
    definitions = (
        (("¥", "JPY"), "currency-japanese-yen", "¥"),
        (("CHF",), "currency-swiss-franc", "CHF"),
        (("₹", "INR"), "currency-indian-rupee", "₹"),
        (("₩", "KRW"), "currency-south-korean-won", "₩"),
        (("MXN",), "currency-mexican-peso", "MXN"),
    )
    return tuple(
        _entry(
            symbols,
            labels[index],
            "Currency",
            canonical_id=canonical_id,
            canonical_symbol=canonical_symbol,
            category="currency",
            quantity_position="both",
        )
        for index, (symbols, canonical_id, canonical_symbol) in enumerate(definitions)
    )


_EXTENDED_TRANSLATION_VALUES = {
    "cs": (
        "čtvereční milimetr",
        "čtvereční centimetr",
        "čtvereční metr",
        "čtvereční kilometr",
        "hektar",
        "milimetr krychlový",
        "centimetr krychlový",
        "metr krychlový",
    ),
    "de": (
        "Quadratmillimeter",
        "Quadratzentimeter",
        "Quadratmeter",
        "Quadratkilometer",
        "Hektar",
        "Kubikmillimeter",
        "Kubikzentimeter",
        "Kubikmeter",
    ),
    "es": (
        "milímetro cuadrado",
        "centímetro cuadrado",
        "metro cuadrado",
        "kilómetro cuadrado",
        "hectárea",
        "milímetro cúbico",
        "centímetro cúbico",
        "metro cúbico",
    ),
    "fr": (
        "millimètre carré",
        "centimètre carré",
        "mètre carré",
        "kilomètre carré",
        "hectare",
        "millimètre cube",
        "centimètre cube",
        "mètre cube",
    ),
    "it": (
        "millimetro quadrato",
        "centimetro quadrato",
        "metro quadrato",
        "chilometro quadrato",
        "ettaro",
        "millimetro cubo",
        "centimetro cubo",
        "metro cubo",
    ),
    "pt": (
        "milímetro quadrado",
        "centímetro quadrado",
        "metro quadrado",
        "quilômetro quadrado",
        "hectare",
        "milímetro cúbico",
        "centímetro cúbico",
        "metro cúbico",
    ),
    "nl": (
        "vierkante millimeter",
        "vierkante centimeter",
        "vierkante meter",
        "vierkante kilometer",
        "hectare",
        "kubieke millimeter",
        "kubieke centimeter",
        "kubieke meter",
    ),
    "sv": (
        "kvadratmillimeter",
        "kvadratcentimeter",
        "kvadratmeter",
        "kvadratkilometer",
        "hektar",
        "kubikmillimeter",
        "kubikcentimeter",
        "kubikmeter",
    ),
    "pl": (
        "milimetr kwadratowy",
        "centymetr kwadratowy",
        "metr kwadratowy",
        "kilometr kwadratowy",
        "hektar",
        "milimetr sześcienny",
        "centymetr sześcienny",
        "metr sześcienny",
    ),
    "ru": (
        "квадратный миллиметр",
        "квадратный сантиметр",
        "квадратный метр",
        "квадратный километр",
        "гектар",
        "кубический миллиметр",
        "кубический сантиметр",
        "кубический метр",
    ),
    "tr": (
        "milimetre kare",
        "santimetre kare",
        "metre kare",
        "kilometre kare",
        "hektar",
        "milimetre küp",
        "santimetre küp",
        "metre küp",
    ),
}

_LOCALIZED_EXTENDED_UNIT_NAMES: dict[str, dict[str, str]] = {
    _lang: dict(
        zip(
            (definition.canonical_id for definition in _EXTENDED_DEFINITIONS),
            _names,
            strict=True,
        )
    )
    for _lang, _names in _EXTENDED_TRANSLATION_VALUES.items()
}

UNIT_ENTRIES: dict[str, tuple[UnitEntry, ...]] = {"en": _EN}
for _lang, _names in _LOCALIZED_UNIT_NAMES.items():
    _items = [
        _entry(
            _definition.symbols,
            _names[_definition.canonical_id],
            _definition.description,
            canonical_id=_definition.canonical_id,
            requires_separator=_definition.requires_separator,
        )
        for _definition in _BASE_DEFINITIONS
    ]
    _items.extend(
        _entry(
            _symbol,
            _name,
            "Locale unit alias",
            canonical_id=_canonical_id,
            case_sensitive=_case_sensitive,
        )
        for _symbol, _name, _canonical_id, _case_sensitive in _LOCALIZED_ALIASES.get(_lang, ())
    )
    UNIT_ENTRIES[_lang] = tuple(_items)

for _lang, _names in _LOCALIZED_EXTENDED_UNIT_NAMES.items():
    UNIT_ENTRIES[_lang] += tuple(
        _entry(
            _definition.symbols,
            _names[_definition.canonical_id],
            _definition.description,
            canonical_id=_definition.canonical_id,
        )
        for _definition in _EXTENDED_DEFINITIONS
    )

UNIT_ENTRIES["de"] += _GERMAN_REQUIRED_ENTRIES
for _lang, _currency_entries in _STRUCTURED_CURRENCY_ENTRIES.items():
    UNIT_ENTRIES[_lang] += _currency_entries

for _lang in tuple(UNIT_ENTRIES):
    UNIT_ENTRIES[_lang] += _polynorm_unit_entries(_lang)
    UNIT_ENTRIES[_lang] += _polynorm_pound_entries(_lang)
    UNIT_ENTRIES[_lang] += _polynorm_currency_entries(_lang)

UNIT_ENTRIES["fr"] += _FRENCH_DOTTED_DURATION_ENTRIES

UNIT_ENTRIES["tr"] = tuple(
    replace(entry, reject_following_apostrophe=True) for entry in UNIT_ENTRIES["tr"]
)


def unit_entries(language: str) -> tuple[UnitEntry, ...]:
    if language in UNIT_ENTRIES:
        return UNIT_ENTRIES[language]
    external = external_unit_entries(language)
    if external is None:
        # Conservative language modules register their external inventory as a
        # side effect, but the public unit API must also work when queried
        # before a language expander has been imported.
        from .unit_data.common import UNIT_LABELS, register_common_units

        if language in UNIT_LABELS:
            register_common_units(language)
            external = external_unit_entries(language)
    if external is None and "_" in language:
        # Materialize locale overlays lazily for callers using the structured
        # unit API before the locale expander itself has been imported.
        from importlib import import_module

        from .language_registry import language_spec

        import_module(language_spec(language).module)
        external = external_unit_entries(language)
    if external is None:
        raise KeyError(language)
    return external


def unit_symbols(language: str) -> frozenset[str]:
    return frozenset(symbol for entry in unit_entries(language) for symbol in entry.symbols)


def validate_unit_registry(language: str) -> None:
    """Validate inventory invariants for one localized reviewed unit registry."""
    entries = unit_entries(language)
    symbols: set[str] = set()
    canonical_entries: dict[str, UnitEntry] = {}
    for entry in entries:
        for symbol in entry.symbols:
            if symbol in symbols:
                raise ValueError(f"duplicate unit symbol {symbol!r} in {language}")
            symbols.add(symbol)
        if entry.canonical_id is not None:
            previous = canonical_entries.get(entry.canonical_id)
            if previous is not None and (
                previous.expansion != entry.expansion or previous.category != entry.category
            ):
                raise ValueError(
                    f"ambiguous canonical unit id {entry.canonical_id!r} in {language}"
                )
            canonical_entries[entry.canonical_id] = entry
            if entry.canonical_symbol not in entry.symbols:
                raise ValueError(f"canonical symbol is not registered for {entry.canonical_id!r}")
    external = external_unit_entries(language)
    if external is not None and language not in UNIT_ENTRIES:
        return
    expected = {definition.canonical_id for definition in _BASE_DEFINITIONS + _EXTENDED_DEFINITIONS}
    localized = set(_LOCALIZED_UNIT_NAMES.get(language, {})) | set(
        _LOCALIZED_EXTENDED_UNIT_NAMES.get(language, {})
    )
    if language != "en" and localized != expected:
        raise ValueError(f"localized unit IDs for {language} do not match the canonical inventory")


_HSPACE = " \t\u00a0\u202f"
_EXPONENT = r"(?:[eE][+\-]?\d+)?"
_DIGITS = r"\d"
_WESTERN_COMMA_GROUP = rf"{_DIGITS}{{1,3}}(?:,{_DIGITS}{{3}})+"
_WESTERN_SPACE_GROUP = rf"{_DIGITS}{{1,3}}(?:[ \u00a0\u202f]{_DIGITS}{{3}})+"
_DOT_GROUP = rf"{_DIGITS}{{1,3}}(?:\.{_DIGITS}{{3}})+"
_INDIAN_GROUP = rf"{_DIGITS}{{1,3}}(?:,{_DIGITS}{{2}})+,{_DIGITS}{{3}}"
_ARABIC_GROUP = rf"{_DIGITS}{{1,3}}(?:٬{_DIGITS}{{3}})+"
_FLEXIBLE_GROUPED = (
    rf"(?:{_INDIAN_GROUP}(?:[.٫]{_DIGITS}+)?|"
    rf"{_DOT_GROUP}(?:,{_DIGITS}+)?|"
    rf"{_WESTERN_SPACE_GROUP}(?:[.,٫]{_DIGITS}+)?|"
    rf"{_ARABIC_GROUP}(?:٫{_DIGITS}+)?)"
)
_PLAIN_NUMBER = rf"{_DIGITS}+(?:[.,٫]{_DIGITS}+)?"
_ATOM_CORE = rf"(?:{_FLEXIBLE_GROUPED}|{_PLAIN_NUMBER}|\.{_DIGITS}+)"
_ATOM = rf"[+\-−]?{_ATOM_CORE}{_EXPONENT}"
_EN_PLAIN_NUMBER = rf"{_DIGITS}+(?:[.,]{_DIGITS}+)?"
_EN_ATOM = rf"[+\-−]?(?:{_WESTERN_COMMA_GROUP}(?:\.{_DIGITS}+)?|{_WESTERN_SPACE_GROUP}(?:\.{_DIGITS}+)?|{_EN_PLAIN_NUMBER}|\.{_DIGITS}+){_EXPONENT}"


def _value_expression(atom: str) -> str:
    return rf"(?:{atom}(?:[–—-]{atom})?|{atom}{_HSPACE}*/{_HSPACE}*{atom}(?:{_HSPACE}*[×x]{_HSPACE}*{atom})*|{atom}(?:{_HSPACE}*[×x]{_HSPACE}*{atom})+)"


_VALUE = _value_expression(_ATOM)
_EN_VALUE = _value_expression(_EN_ATOM)
_VALUE_PATTERN = re.compile(rf"(?<![\w./,٬])(?P<value>{_VALUE})(?P<spacing>[{_HSPACE}]*)")
_EN_VALUE_PATTERN = re.compile(rf"(?<![\w./,٬])(?P<value>{_EN_VALUE})(?P<spacing>[{_HSPACE}]*)")
_CONTINUATION = re.compile(rf"[{_HSPACE}]*([/^·⋅*×^])")
_PREFIX_BOUNDARY = r"(?<![\w./])"
_CLOSING_SENTENCE_CHARS = frozenset("\"'»”’)]}》」』")
_EN_PREPOSITION_DETERMINERS = frozenset(
    {
        "a",
        "an",
        "the",
        "my",
        "your",
        "his",
        "her",
        "its",
        "our",
        "their",
        "this",
        "that",
        "these",
        "those",
    }
)


def _unit_text_matches(text: str, offset: int, symbol: str, case_sensitive: bool) -> bool:
    value = text[offset : offset + len(symbol)]
    if case_sensitive:
        return value == symbol
    return value.casefold() == symbol.casefold()


def _unit_continuation_is_unsupported(text: str, end: int) -> bool:
    """Reject a shorter unit prefix when the source clearly continues it."""
    continuation = text[end:]
    if continuation[:1] in {"'", "’"}:
        return False
    if _CONTINUATION.match(continuation):
        return True
    if continuation.startswith("-") and len(continuation) > 1 and continuation[1].isalnum():
        return True
    if continuation.startswith(".") and len(continuation) > 1 and continuation[1].isalnum():
        return True
    return False


def _unit_match(
    *,
    start: int,
    end: int,
    value_start: int,
    value_end: int,
    value: str,
    symbol: str,
    entry: UnitEntry,
    canonical_symbol: str,
    language: str,
    separator: str,
) -> UnitMatch:
    return UnitMatch(
        start=start,
        end=end,
        value_start=value_start,
        value_end=value_end,
        value=value,
        symbol=symbol,
        canonical_id=entry.canonical_id,
        canonical_symbol=canonical_symbol,
        expansion=entry.expansion,
        language=language,
        category=entry.category,
        ambiguity=_unit_match_ambiguity(entry, symbol),
        separator=separator,
    )


def _unit_match_ambiguity(entry: UnitEntry, symbol: str) -> UnitAmbiguity:
    """Classify ambiguity from the matched source spelling and unit identity."""
    source_symbol = symbol.casefold()
    if entry.canonical_id == "customary-inch" and source_symbol in {"in", "in."}:
        return "lexical"
    if source_symbol.rstrip(".").isalpha() and len(source_symbol.rstrip(".")) == 1:
        return "bare_symbol"
    return "none"


def _unit_replacement_text(
    text: str, unit_match: UnitMatch, *, preserve_sentence_final_period: bool
) -> str:
    """Render a lexical unit expansion without inventing sentence punctuation."""
    replacement = f"{unit_match.value} {unit_match.expansion}"
    if (
        not preserve_sentence_final_period
        or unit_match.category != "unit"
        or not unit_match.symbol.endswith(".")
    ):
        return replacement

    suffix = text[unit_match.end :].lstrip(_HSPACE)
    while suffix and suffix[0] in _CLOSING_SENTENCE_CHARS:
        suffix = suffix[1:].lstrip(_HSPACE)
    if not suffix:
        return f"{replacement}."
    return replacement


def _unit_inventory(
    language: str,
    overrides: Mapping[str, UnitEntry] | None,
    suppressed: Set[str] | None,
) -> tuple[tuple[str, UnitEntry], ...]:
    entries = [
        (symbol, entry)
        for entry in unit_entries(language)
        for symbol in entry.symbols
        if suppressed is None or (symbol not in suppressed and entry.canonical_id not in suppressed)
    ]
    if overrides:
        entries = [item for item in entries if item[0] not in overrides]
        entries.extend(
            item
            for item in overrides.items()
            if suppressed is None
            or (item[0] not in suppressed and item[1].canonical_id not in suppressed)
        )
    return tuple(sorted(entries, key=lambda item: (-len(item[0]), item[0])))


def _normalize_protected_spans(
    text: str,
    protected_spans: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    spans: list[tuple[int, int]] = []
    for index, span in enumerate(protected_spans):
        try:
            start, end = span
        except (TypeError, ValueError) as error:
            raise TypeError(f"protected span {index} must be a 2-tuple") from error
        if type(start) is not int or type(end) is not int:
            raise TypeError(f"protected span {index} offsets must be integers")
        if start < 0 or end < start or end > len(text):
            raise ValueError(f"protected span {index} is outside the source text")
        if start == end:
            continue
        spans.append((start, end))
    spans.sort()
    if any(left[1] > right[0] for left, right in zip(spans, spans[1:], strict=False)):
        raise ValueError("protected spans must not overlap")
    return tuple(spans)


def _overlaps_protected(start: int, end: int, spans: tuple[tuple[int, int], ...]) -> bool:
    return any(
        start < protected_end and end > protected_start for protected_start, protected_end in spans
    )


def _currency_is_embedded_in_lexical_material(text: str, start: int, end: int) -> bool:
    """Reject currency candidates embedded in URL/email-like non-prose tokens."""
    token_start = start
    while token_start > 0 and not text[token_start - 1].isspace():
        token_start -= 1
    token_end = end
    while token_end < len(text) and not text[token_end].isspace():
        token_end += 1
    token = text[token_start:token_end]
    return "://" in token or ("@" in token and "." in token)


def _inch_alias_is_prepositional(text: str, end: int) -> bool:
    """Reject obvious English prepositions mistaken for the ``in`` unit."""
    match = re.match(rf"[{_HSPACE}]+(?P<word>[A-Za-z]+)(?![\w-])", text[end:])
    return bool(match and match.group("word").casefold() in _EN_PREPOSITION_DETERMINERS)


def _inch_alias_rejection_reason(text: str, end: int, value: str, symbol: str) -> str | None:
    """Return the conservative rejection reason for an English inch alias."""
    if _inch_alias_is_prepositional(text, end):
        return "prepositional_in"
    if symbol == "in" and re.fullmatch(r"\d{4}", value):
        year = int(value)
        if 1000 <= year <= 2099:
            return "year_like_before_lexical_in"
    if symbol == "in" and re.match(rf"[{_HSPACE}]+(?:1\d{{3}}|20\d{{2}})(?!\d)", text[end:]):
        return "year_like_before_lexical_in"
    return None


def _canonical_symbol(entry: UnitEntry, symbol: str) -> str:
    if entry.canonical_id is not None:
        for definition in _BASE_DEFINITIONS + _EXTENDED_DEFINITIONS:
            if definition.canonical_id == entry.canonical_id:
                return definition.symbols[0]
    return entry.canonical_symbol or symbol


def iter_unit_matches(
    text: str,
    language: str,
    *,
    overrides: Mapping[str, UnitEntry] | None = None,
    suppressed: Set[str] | None = None,
    protected_spans: Iterable[tuple[int, int]] = (),
) -> Iterator[UnitMatch]:
    """Yield structured, source-aligned matches for complete numeric quantities.

    Matching is deliberately lexical: the numeric spelling is preserved and no
    number, grammar, currency, or locale-specific speech policy is applied.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    inventory = _unit_inventory(language, overrides, suppressed)
    protected = _normalize_protected_spans(text, protected_spans)
    value_expression = _EN_VALUE if language == "en" else _VALUE
    value_pattern = _EN_VALUE_PATTERN if language == "en" else _VALUE_PATTERN
    matches: list[UnitMatch] = []
    for value_match in value_pattern.finditer(text):
        value = value_match.group("value")
        unit_start = value_match.end()
        candidates: list[tuple[str, UnitEntry]] = []
        for symbol, entry in inventory:
            if entry.quantity_position not in {"suffix", "both"}:
                continue
            if not entry.requires_numeric_value:
                continue
            if _unit_text_matches(text, unit_start, symbol, entry.case_sensitive):
                candidates.append((symbol, entry))
        if not candidates:
            continue
        symbol, entry = max(candidates, key=lambda item: len(item[0]))
        spacing = value_match.group("spacing")
        if entry.requires_separator and not spacing:
            continue
        end = unit_start + len(symbol)
        if end < len(text) and (text[end].isalnum() or text[end] == "_"):
            continue
        if _unit_continuation_is_unsupported(text, end):
            continue
        if entry.reject_following_period and text[end : end + 1] == ".":
            continue
        if entry.reject_following_apostrophe and text[end : end + 1] in {"'", "’"}:
            continue
        if (
            language == "en"
            and entry.canonical_id == "customary-inch"
            and symbol.casefold() in {"in", "in."}
        ):
            if _inch_alias_rejection_reason(text, end, value, symbol) is not None:
                continue
        start = value_match.start()
        if entry.category == "currency" and _currency_is_embedded_in_lexical_material(
            text, start, end
        ):
            continue
        if _overlaps_protected(start, end, protected):
            continue
        matches.append(
            _unit_match(
                start=start,
                end=end,
                value_start=value_match.start("value"),
                value_end=value_match.end("value"),
                value=value,
                symbol=text[unit_start:end],
                entry=entry,
                canonical_symbol=_canonical_symbol(entry, symbol),
                language=language,
                separator=text[value_match.end("value") : unit_start],
            )
        )

    for symbol, entry in inventory:
        if entry.quantity_position not in {"prefix", "both"} or not entry.requires_numeric_value:
            continue
        pattern = re.compile(
            rf"{_PREFIX_BOUNDARY}(?P<symbol>{re.escape(symbol)})(?P<spacing>[{_HSPACE}]*)"
            rf"(?P<value>{value_expression})(?![\w_])",
            0 if entry.case_sensitive else re.IGNORECASE,
        )
        for value_match in pattern.finditer(text):
            if entry.requires_separator and not value_match.group("spacing"):
                continue
            start = value_match.start("symbol")
            end = value_match.end("value")
            if _unit_continuation_is_unsupported(text, end):
                continue
            if entry.reject_following_apostrophe and text[end : end + 1] in {"'", "’"}:
                continue
            if entry.category == "currency" and _currency_is_embedded_in_lexical_material(
                text, start, end
            ):
                continue
            if _overlaps_protected(start, end, protected):
                continue
            matches.append(
                _unit_match(
                    start=start,
                    end=end,
                    value_start=value_match.start("value"),
                    value_end=value_match.end("value"),
                    value=value_match.group("value"),
                    symbol=value_match.group("symbol"),
                    entry=entry,
                    canonical_symbol=_canonical_symbol(entry, symbol),
                    language=language,
                    separator=text[value_match.end("symbol") : value_match.start("value")],
                )
            )

    selected: list[UnitMatch] = []
    for match in sorted(matches, key=lambda item: (item.start, -(item.end - item.start))):
        if selected and selected[-1].end > match.start:
            continue
        selected.append(match)
    yield from selected


def iter_unit_diagnostics(
    text: str,
    language: str,
    *,
    overrides: Mapping[str, UnitEntry] | None = None,
    suppressed: Set[str] | None = None,
    protected_spans: Iterable[tuple[int, int]] = (),
) -> Iterator[UnitDiagnostic]:
    """Yield accepted matches and compact candidates rejected by unit policy.

    Accepted records mirror :func:`iter_unit_matches`; rejected records are
    intentionally limited to reviewed candidates whose metadata requires a
    separator. This keeps diagnostics useful for ownership triage without
    exposing the matcher implementation as a tracing framework.
    """
    diagnostics = [
        UnitDiagnostic(
            start=match.start,
            end=match.end,
            value=match.value,
            symbol=match.symbol,
            canonical_id=match.canonical_id,
            language=match.language,
            status="accepted",
            ambiguity=match.ambiguity,
            separator=match.separator,
        )
        for match in iter_unit_matches(
            text,
            language,
            overrides=overrides,
            suppressed=suppressed,
            protected_spans=protected_spans,
        )
    ]
    inventory = _unit_inventory(language, overrides, suppressed)
    value_pattern = _EN_VALUE_PATTERN if language == "en" else _VALUE_PATTERN
    protected = _normalize_protected_spans(text, protected_spans)
    for value_match in value_pattern.finditer(text):
        value = value_match.group("value")
        unit_start = value_match.end()
        spacing = value_match.group("spacing")
        candidates = [
            (symbol, entry)
            for symbol, entry in inventory
            if entry.quantity_position in {"suffix", "both"}
            and entry.requires_numeric_value
            and entry.requires_separator
            and not spacing
            and _unit_text_matches(text, unit_start, symbol, entry.case_sensitive)
        ]
        if not candidates:
            continue
        symbol, entry = max(candidates, key=lambda item: len(item[0]))
        start = value_match.start()
        end = unit_start + len(symbol)
        if end < len(text) and (text[end].isalnum() or text[end] == "_"):
            continue
        if _unit_continuation_is_unsupported(text, end):
            continue
        if _overlaps_protected(start, end, protected):
            continue
        diagnostics.append(
            UnitDiagnostic(
                start=start,
                end=end,
                value=value,
                symbol=text[unit_start:end],
                canonical_id=entry.canonical_id,
                language=language,
                status="rejected",
                reason="requires_separator",
                ambiguity=_unit_match_ambiguity(entry, text[unit_start:end]),
                separator=text[value_match.end("value") : unit_start],
            )
        )
    for value_match in value_pattern.finditer(text):
        value = value_match.group("value")
        unit_start = value_match.end()
        candidates = [
            (symbol, entry)
            for symbol, entry in inventory
            if entry.quantity_position in {"suffix", "both"}
            and entry.requires_numeric_value
            and entry.canonical_id == "customary-inch"
            and symbol == "in"
            and _unit_text_matches(text, unit_start, symbol, entry.case_sensitive)
        ]
        if not candidates:
            continue
        symbol, entry = max(candidates, key=lambda item: len(item[0]))
        end = unit_start + len(symbol)
        reason = _inch_alias_rejection_reason(text, end, value, symbol)
        if reason != "year_like_before_lexical_in":
            continue
        start = value_match.start()
        if end < len(text) and (text[end].isalnum() or text[end] == "_"):
            continue
        if _unit_continuation_is_unsupported(text, end):
            continue
        if _overlaps_protected(start, end, protected):
            continue
        diagnostics.append(
            UnitDiagnostic(
                start=start,
                end=end,
                value=value,
                symbol=text[unit_start:end],
                canonical_id=entry.canonical_id,
                language=language,
                status="rejected",
                reason=reason,
                ambiguity=_unit_match_ambiguity(entry, text[unit_start:end]),
                separator=text[value_match.end("value") : unit_start],
            )
        )
    yield from sorted(diagnostics, key=lambda item: (item.start, item.end, item.status))


def iter_unit_replacements(
    text: str,
    language: str,
    overrides: Mapping[str, UnitEntry] | None = None,
    suppressed: Set[str] | None = None,
) -> Iterator[Replacement]:
    """Yield complete reviewed unit replacements using original offsets.

    Numeric-looking prefixes are never expanded when a longer unsupported unit
    expression follows them. This deliberately favors unchanged input over a
    malformed hybrid such as ``5 kilometer / h``.
    """
    inventory = _unit_inventory(language, overrides, suppressed)
    for unit_match in iter_unit_matches(text, language, overrides=overrides, suppressed=suppressed):
        if unit_match.category == "currency":
            continue
        preserve_sentence_final_period = any(
            entry.preserve_sentence_final_period
            and entry.canonical_id == unit_match.canonical_id
            and any(
                len(symbol) == len(unit_match.symbol)
                and _unit_text_matches(unit_match.symbol, 0, symbol, entry.case_sensitive)
                for symbol in entry.symbols
            )
            for _symbol, entry in inventory
        )
        yield Replacement(
            start=unit_match.start,
            end=unit_match.end,
            text=_unit_replacement_text(
                text,
                unit_match,
                preserve_sentence_final_period=preserve_sentence_final_period,
            ),
            priority=300,
            source=f"unit:{language}:{unit_match.symbol}",
            kind="unit",
            entry_id=f"unit:{language}:{unit_match.canonical_id or unit_match.symbol}",
        )

    # Honor metadata for future reviewed entries that intentionally do not
    # require a numeric quantity. The current bundled inventory has none, but
    # keeping this path prevents metadata and runtime policy from diverging.
    for symbol, entry in inventory:
        if entry.requires_numeric_value:
            continue
        pattern = re.compile(
            rf"(?<!\w){re.escape(symbol)}(?!\w)",
            0 if entry.case_sensitive else re.IGNORECASE,
        )
        for replacement_match in pattern.finditer(text):
            yield Replacement(
                start=replacement_match.start(),
                end=replacement_match.end(),
                text=entry.expansion,
                priority=300,
                source=f"unit:{language}:{symbol}",
                kind="unit",
                entry_id=f"unit:{language}:{entry.canonical_id or symbol}",
            )


def expand_units(text: str, language: str) -> str:
    """Expand a complete reviewed unit expression after a numeric quantity."""
    return apply_replacements(text, tuple(iter_unit_replacements(text, language)))


__all__ = [
    "NUMBER_BEFORE_UNIT",
    "NUMERIC_FORMAT_PROFILES",
    "NumericFormatProfile",
    "UNIT_ENTRIES",
    "UnitAmbiguity",
    "UnitEntry",
    "UnitDiagnostic",
    "UnitMatch",
    "expand_units",
    "iter_unit_matches",
    "iter_unit_diagnostics",
    "iter_unit_replacements",
    "numeric_format_profile",
    "unit_entries",
    "unit_symbols",
    "validate_unit_registry",
]
