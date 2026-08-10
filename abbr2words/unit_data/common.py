"""Conservative common-unit inventories for newly added languages."""

from __future__ import annotations

from collections.abc import Iterable

from . import register

_COMMON_UNITS = (
    ("duration-second", ("s", "sec"), "second"),
    ("duration-minute", ("min",), "minute"),
    ("duration-hour", ("h", "hr"), "hour"),
    ("duration-day", ("d",), "day"),
    ("length-millimeter", ("mm",), "millimeter"),
    ("length-centimeter", ("cm",), "centimeter"),
    ("length-meter", ("m",), "meter"),
    ("length-kilometer", ("km",), "kilometer"),
    ("volume-milliliter", ("mL", "ml"), "milliliter"),
    ("volume-liter", ("L", "l"), "liter"),
    ("mass-microgram", ("µg", "μg", "ug"), "microgram"),
    ("mass-milligram", ("mg",), "milligram"),
    ("mass-gram", ("g",), "gram"),
    ("mass-kilogram", ("kg",), "kilogram"),
    ("mass-tonne", ("t",), "tonne"),
    ("temperature-kelvin", ("K",), "kelvin"),
    ("temperature-celsius", ("°C", "℃"), "degree Celsius"),
    ("temperature-fahrenheit", ("°F", "℉"), "degree Fahrenheit"),
    ("speed-meter-per-second", ("m/s",), "meter per second"),
    ("speed-kilometer-per-hour", ("km/h",), "kilometer per hour"),
    ("area-square-millimeter", ("mm²", "mm2"), "square millimeter"),
    ("area-square-centimeter", ("cm²", "cm2"), "square centimeter"),
    ("area-square-meter", ("m²", "m2"), "square meter"),
    ("area-square-kilometer", ("km²", "km2"), "square kilometer"),
    ("area-hectare", ("ha",), "hectare"),
    ("volume-cubic-millimeter", ("mm³", "mm3"), "cubic millimeter"),
    ("volume-cubic-centimeter", ("cm³", "cm3"), "cubic centimeter"),
    ("volume-cubic-meter", ("m³", "m3"), "cubic meter"),
)


def common_unit_entries(language: str, *, expansion_prefix: str = "") -> tuple[object, ...]:
    """Build a stable common inventory using the public unit model."""
    from abbr2words.units import UnitEntry

    prefix = f"{expansion_prefix} " if expansion_prefix else ""
    return tuple(
        UnitEntry(
            symbols=symbols,
            expansion=f"{prefix}{expansion}",
            description=f"Reviewed common unit ({language})",
            canonical_symbol=symbols[0],
            canonical_id=canonical_id,
        )
        for canonical_id, symbols, expansion in _COMMON_UNITS
    )


def register_common_units(language: str, *, expansion_prefix: str = "") -> None:
    """Register one external base inventory exactly once."""
    register(language, common_unit_entries(language, expansion_prefix=expansion_prefix))


def locale_currency(symbol: str, expansion: str, canonical_id: str) -> object:
    """Build a locale-specific ISO-4217-aware currency identity."""
    from abbr2words.units import UnitEntry

    return UnitEntry(
        symbols=(symbol,),
        expansion=expansion,
        description="Reviewed locale currency identity",
        canonical_symbol=symbol,
        canonical_id=canonical_id,
        category="currency",
        quantity_position="both",
    )


def register_locale_units(language: str, base: str, extra: Iterable[object] = ()) -> None:
    """Register an effective locale inventory inheriting a bundled base."""
    from abbr2words.units import unit_entries

    register(language, (*unit_entries(base), *tuple(extra)))


__all__ = [
    "common_unit_entries",
    "locale_currency",
    "register_common_units",
    "register_locale_units",
]
