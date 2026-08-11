"""Normalization helpers shared by registry-like maps."""

from __future__ import annotations


def normalize_entry_key(value: str, *, case_sensitive: bool) -> str:
    """Return the stable key used for a spelling in an abbreviation registry."""
    return value if case_sensitive else value.casefold()


__all__ = ["normalize_entry_key"]
