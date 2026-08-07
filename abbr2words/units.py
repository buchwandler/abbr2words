"""Reviewed quantity-unit inventory and numeric-aware unit expansion."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping, Set
from dataclasses import dataclass, replace

from ._replacements import Replacement, apply_replacements

NUMBER_BEFORE_UNIT = (
    r"(?:^|[^\w.])"
    r"[+\-−]?"
    r"(?:\d{1,3}(?:[ \u00a0\u202f]\d{3})+|\d+)"
    r"(?:[.,]\d+)?"
    r"[ \t\u00a0\u202f]*$"
)


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


@dataclass(frozen=True)
class _UnitDefinition:
    canonical_id: str
    symbols: tuple[str, ...]
    description: str


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
    _entry("°C", "degree Celsius", "Temperature"),
    _entry("°F", "degree Fahrenheit", "Temperature"),
    _entry("K", "kelvin", "Temperature"),
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
    _UnitDefinition("temperature-kelvin", ("K",), "Temperature"),
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

_FRENCH_CURRENCY_ENTRIES = (
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
)

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
    _entry("kWh", "Kilowattstunde", "Energy", canonical_id="energy-kilowatt-hour"),
    _entry("Wh", "Wattstunde", "Energy", canonical_id="energy-watt-hour"),
    _entry("mAh", "Milliampere-Stunde", "Electric charge", canonical_id="charge-milliampere-hour"),
    _entry("mA", "Milliampere", "Electric current", canonical_id="current-milliampere"),
    _entry("GHz", "Gigahertz", "Frequency", canonical_id="frequency-gigahertz"),
    _entry("MHz", "Megahertz", "Frequency", canonical_id="frequency-megahertz"),
    _entry("kHz", "Kilohertz", "Frequency", canonical_id="frequency-kilohertz"),
    _entry("Hz", "Hertz", "Frequency", canonical_id="frequency-hertz"),
    _entry("W", "Watt", "Power", canonical_id="power-watt"),
    _entry("V", "Volt", "Electric potential", canonical_id="voltage-volt"),
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
UNIT_ENTRIES["fr"] += _FRENCH_CURRENCY_ENTRIES + _FRENCH_DOTTED_DURATION_ENTRIES

UNIT_ENTRIES["tr"] = tuple(
    replace(entry, reject_following_apostrophe=True) for entry in UNIT_ENTRIES["tr"]
)


def unit_entries(language: str) -> tuple[UnitEntry, ...]:
    return UNIT_ENTRIES[language]


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
    expected = {definition.canonical_id for definition in _BASE_DEFINITIONS + _EXTENDED_DEFINITIONS}
    localized = set(_LOCALIZED_UNIT_NAMES.get(language, {})) | set(
        _LOCALIZED_EXTENDED_UNIT_NAMES.get(language, {})
    )
    if language != "en" and localized != expected:
        raise ValueError(f"localized unit IDs for {language} do not match the canonical inventory")


_HSPACE = " \t\u00a0\u202f"
_ATOM = r"[+\-−]?(?:(?:\d{1,3}(?:[ \u00a0\u202f]\d{3})+|\d+)(?:[.,]\d+)?|\.\d+)(?:[eE][+\-]?\d+)?"
_VALUE = rf"(?:{_ATOM}(?:[–—-]{_ATOM})?|{_ATOM}{_HSPACE}*/{_HSPACE}*{_ATOM}(?:{_HSPACE}*[×x]{_HSPACE}*{_ATOM})*|{_ATOM}(?:{_HSPACE}*[×x]{_HSPACE}*{_ATOM})+)"
_VALUE_PATTERN = re.compile(rf"(?<![\w./])(?P<value>{_VALUE})(?P<spacing>[{_HSPACE}]*)")
_CONTINUATION = re.compile(rf"[{_HSPACE}]*([/^·⋅*×^])")
_PREFIX_BOUNDARY = r"(?<![\w./])"
_CLOSING_SENTENCE_CHARS = frozenset("\"'»”’)]}》」』")


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
    )


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
    matches: list[UnitMatch] = []
    for value_match in _VALUE_PATTERN.finditer(text):
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
        end = unit_start + len(symbol)
        if end < len(text) and (text[end].isalnum() or text[end] == "_"):
            continue
        if _unit_continuation_is_unsupported(text, end):
            continue
        if entry.reject_following_apostrophe and text[end : end + 1] in {"'", "’"}:
            continue
        start = value_match.start()
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
            )
        )

    for symbol, entry in inventory:
        if entry.quantity_position not in {"prefix", "both"} or not entry.requires_numeric_value:
            continue
        pattern = re.compile(
            rf"{_PREFIX_BOUNDARY}(?P<symbol>{re.escape(symbol)})(?P<spacing>[{_HSPACE}]*)"
            rf"(?P<value>{_VALUE})(?![\w_])",
            0 if entry.case_sensitive else re.IGNORECASE,
        )
        for value_match in pattern.finditer(text):
            start = value_match.start("symbol")
            end = value_match.end("value")
            if _unit_continuation_is_unsupported(text, end):
                continue
            if entry.reject_following_apostrophe and text[end : end + 1] in {"'", "’"}:
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
                )
            )

    selected: list[UnitMatch] = []
    for match in sorted(matches, key=lambda item: (item.start, -(item.end - item.start))):
        if selected and selected[-1].end > match.start:
            continue
        selected.append(match)
    yield from selected


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
    "UNIT_ENTRIES",
    "UnitEntry",
    "UnitMatch",
    "expand_units",
    "iter_unit_matches",
    "iter_unit_replacements",
    "unit_entries",
    "unit_symbols",
    "validate_unit_registry",
]
