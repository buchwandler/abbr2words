"""External reviewed unit-data registry.

The matching engine remains in :mod:`abbr2words.units`; language modules can
register data here without adding another data table to that engine module.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

_UNIT_DATA: dict[str, tuple[Any, ...]] = {}


def register(language: str, entries: Iterable[Any]) -> None:
    """Register one complete effective inventory for a language key."""
    if language in _UNIT_DATA:
        raise ValueError(f"unit data already registered for {language}")
    _UNIT_DATA[language] = tuple(entries)


def register_overlay(language: str, base: str, overlay: Iterable[Any]) -> None:
    """Register a locale inventory by appending reviewed overlay entries."""
    base_entries = entries(base)
    if base_entries is None:
        raise KeyError(base)
    _UNIT_DATA[language] = base_entries + tuple(overlay)


def entries(language: str) -> tuple[Any, ...] | None:
    """Return external data for *language*, if registered."""
    return _UNIT_DATA.get(language)


__all__ = ["entries", "register", "register_overlay"]
