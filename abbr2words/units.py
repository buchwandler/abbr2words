"""Reviewed quantity-unit inventory and numeric-aware unit expansion."""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass

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


def _entry(symbols: str | tuple[str, ...], expansion: str, description: str) -> UnitEntry:
    if isinstance(symbols, str):
        symbols = (symbols,)
    return UnitEntry(symbols, expansion, description=description, canonical_symbol=symbols[0])


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

_TRANSLATIONS: dict[str, tuple[str, ...]] = {
    "cs": (
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
    "de": (
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
    "es": (
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
    "fr": (
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
    "it": (
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
    "pt": (
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
}
_BASE_SYMBOLS = (
    "s",
    "min",
    "h",
    "d",
    "mm",
    "cm",
    "m",
    "km",
    "ml",
    "l",
    "µg",
    "mg",
    "g",
    "kg",
    "t",
    "K",
    "°C",
    "°F",
    "m/s",
    "km/h",
)
_ALIASES = {
    "cs": (("hod.", "hodina"), ("min.", "minuta"), ("sek.", "sekunda")),
    "de": (("Std.", "Stunde"), ("Min.", "Minute"), ("Sek.", "Sekunde")),
    "es": (("min.", "minuto"), ("seg", "segundo"), ("seg.", "segundo")),
    "fr": (("sec", "seconde"),),
    "it": (("min.", "minuto"), ("sec", "secondo"), ("sec.", "secondo")),
    "pt": (("min.", "minuto"), ("seg", "segundo"), ("seg.", "segundo")),
}

UNIT_ENTRIES: dict[str, tuple[UnitEntry, ...]] = {"en": _EN}
for _lang, _names in _TRANSLATIONS.items():
    _items: list[UnitEntry] = []
    for _symbol, _name in zip(_BASE_SYMBOLS, _names, strict=True):
        _symbols: tuple[str, ...] = (_symbol,)
        if _symbol == "ml":
            _symbols = ("ml", "mL")
        elif _symbol == "l":
            _symbols = ("l", "L")
        elif _symbol == "µg":
            _symbols = ("µg", "ug")
        _items.append(_entry(_symbols, _name, "Baseline unit"))
    _items.extend(
        _entry(_symbol, _name, "Locale unit") for _symbol, _name in _ALIASES.get(_lang, ())
    )
    UNIT_ENTRIES[_lang] = tuple(_items)

_EXTENDED_BASELINE: dict[str, tuple[str, ...]] = {
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
}
for _lang, _names in _EXTENDED_BASELINE.items():
    _extra_symbols: tuple[tuple[str, ...], ...] = (
        ("mm²", "mm2"),
        ("cm²", "cm2"),
        ("m²", "m2"),
        ("km²", "km2"),
        ("ha",),
        ("mm³", "mm3"),
        ("cm³", "cm3"),
        ("m³", "m3"),
    )
    UNIT_ENTRIES[_lang] += tuple(
        _entry(symbols, name, "Baseline unit")
        for symbols, name in zip(_extra_symbols, _names, strict=True)
    )


def unit_entries(language: str) -> tuple[UnitEntry, ...]:
    return UNIT_ENTRIES[language]


def unit_symbols(language: str) -> frozenset[str]:
    return frozenset(symbol for entry in unit_entries(language) for symbol in entry.symbols)


def iter_unit_replacements(text: str, language: str) -> Iterator[Replacement]:
    """Yield reviewed unit replacements using offsets from the original text."""

    # Grouped digits, decimal point/comma, signed values, and simple ranges.
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
