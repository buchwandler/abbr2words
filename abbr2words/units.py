"""Reviewed quantity-unit inventory and numeric-aware unit expansion."""

from __future__ import annotations

import re
from collections.abc import Iterator
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
) -> UnitEntry:
    if isinstance(symbols, str):
        symbols = (symbols,)
    return UnitEntry(
        symbols,
        expansion,
        description=description,
        canonical_symbol=symbols[0],
        canonical_id=canonical_id,
        reject_following_apostrophe=reject_following_apostrophe,
    )


# This is a reviewed inventory, not an attempt to model every UCUM expression.
_EN = (
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
    _entry(("µg", "ug"), "microgram", "Mass"),
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
    _UnitDefinition("mass-microgram", ("µg", "ug"), "Mass"),
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
    "cs": (("hod.", "hodina"), ("min.", "minuta"), ("sek.", "sekunda")),
    "de": (("Std.", "Stunde"), ("Min.", "Minute"), ("Sek.", "Sekunde")),
    "es": (("min.", "minuto"), ("seg", "segundo"), ("seg.", "segundo")),
    "fr": (("sec", "seconde"),),
    "it": (("min.", "minuto"), ("sec", "secondo"), ("sec.", "secondo")),
    "pt": (("min.", "minuto"), ("seg", "segundo"), ("seg.", "segundo")),
}

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
        _entry(_symbol, _name, "Locale unit")
        for _symbol, _name in _LOCALIZED_ALIASES.get(_lang, ())
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

UNIT_ENTRIES["tr"] = tuple(
    replace(entry, reject_following_apostrophe=True) for entry in UNIT_ENTRIES["tr"]
)


def unit_entries(language: str) -> tuple[UnitEntry, ...]:
    return UNIT_ENTRIES[language]


def unit_symbols(language: str) -> frozenset[str]:
    return frozenset(symbol for entry in unit_entries(language) for symbol in entry.symbols)


def iter_unit_replacements(text: str, language: str) -> Iterator[Replacement]:
    """Yield reviewed unit replacements using offsets from the original text."""

    number = r"[+\-−]?(?:\d{1,3}(?:[ \u00a0\u202f]\d{3})+|\d+)(?:[.,]\d+)?"
    value = rf"{number}(?:[–—-]{number})?"
    spacing = r"[ \t\u00a0\u202f]*"
    alternatives = [(symbol, entry) for entry in unit_entries(language) for symbol in entry.symbols]
    alternatives.sort(key=lambda item: len(item[0]), reverse=True)
    pattern = re.compile(
        rf"(?<![\w.])(?P<value>{value}){spacing}"
        rf"(?P<unit>{'|'.join(re.escape(symbol) for symbol, _ in alternatives)})(?!\w)"
    )
    by_symbol = {symbol: entry for symbol, entry in alternatives}
    for match in pattern.finditer(text):
        entry = by_symbol[match.group("unit")]
        if entry.reject_following_apostrophe and text[match.end() : match.end() + 1] in {"'", "’"}:
            continue
        yield Replacement(
            start=match.start(),
            end=match.end(),
            text=f"{match.group('value')} {entry.expansion}",
            priority=200,
            source=f"unit:{language}:{match.group('unit')}",
        )


def expand_units(text: str, language: str) -> str:
    """Expand a complete reviewed unit expression after a numeric quantity."""
    return apply_replacements(text, tuple(iter_unit_replacements(text, language)))


__all__ = [
    "NUMBER_BEFORE_UNIT",
    "UNIT_ENTRIES",
    "UnitEntry",
    "expand_units",
    "iter_unit_replacements",
    "unit_entries",
    "unit_symbols",
]
