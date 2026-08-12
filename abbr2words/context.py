"""Language-specific, bounded context profiles for abbreviation matching."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

_LEXICAL_TOKEN = re.compile(r"[^\W\d_][\w'’\-]*", re.UNICODE)
_TIME = re.compile(r"\b\d{1,2}(?::\d{2})?\s*$")
_DATE_BEFORE = re.compile(r"(?:^|\D)\d{1,2}[.\-/\s\u00a0\u202f]*$")
_DATE_AFTER = re.compile(r"^[.\-/\s\u00a0\u202f]*\d{1,4}(?:\D|$)")
_HOUSE_AND_STREET = re.compile(
    r"(?:^|[\s,;(])\d+\s+(?:[NSEW]\.?\s+)?[\w'’\-]+(?:\s+[\w'’\-]+)*\s*$",
    re.UNICODE | re.IGNORECASE,
)
_STREET_NAME = re.compile(r"(?:^|[\s,;(])(?:[\w'’\-]+)(?:\s+[\w'’\-]+)*$", re.UNICODE)
_REVIEWED_STREET_NAME = re.compile(
    r"(?:^|[\s,;(])(?P<name>[A-Z][\w'’\-]*(?:\s+[A-Z][\w'’\-]*)*)\s*$",
    re.UNICODE,
)
_STREET_NAME_PROSE = frozenset(
    {
        "a",
        "an",
        "and",
        "at",
        "be",
        "been",
        "but",
        "by",
        "call",
        "closed",
        "for",
        "from",
        "go",
        "had",
        "has",
        "have",
        "he",
        "here",
        "i",
        "in",
        "is",
        "near",
        "of",
        "on",
        "or",
        "please",
        "see",
        "she",
        "that",
        "the",
        "they",
        "this",
        "to",
        "visit",
        "was",
        "we",
        "were",
    }
)
_ADDRESS_NUMBER = re.compile(r"(?:^|[\s,;(])\d+[A-Za-z]?\s*$")
_STREET_SUFFIX = re.compile(
    r"\b(?:street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr|"
    r"court|ct|highway|hwy|parkway|pkwy|place|pl|terrace|ter|way)\.?"
    r"(?=$|[\s,;.)])",
    re.IGNORECASE,
)
_WASHINGTON_PLACE = re.compile(r"\bWashington\s*,?\s*$", re.IGNORECASE)
_EXPLICIT_PLACE_AFTER = re.compile(
    r"^\s*(?:metropolitan(?:\s+area)?|metro(?:politan)?|area|residents?|"
    r"district|downtown)\b",
    re.IGNORECASE,
)


def _context(name: str) -> Any:
    from .core import AbbreviationContext

    return AbbreviationContext(name)


def _first_lexical_token(after: str) -> str:
    match = _LEXICAL_TOKEN.search(after.lstrip(" \t\u00a0\u202f\"'“”‘’([{<"))
    return match.group(0) if match else ""


def _name_evidence(after: str) -> bool:
    token = _first_lexical_token(after)
    if not token or not any(char.isalpha() for char in token):
        return False
    cased = [char for char in token if char.isalpha() and char.isupper() or char.islower()]
    if not cased:
        return False
    first_cased = next((char for char in token if char.isupper() or char.islower()), "")
    return first_cased.isupper() or (token.isupper() and len(token) > 1)


def _reviewed_street_name_evidence(before: str) -> bool:
    """Accept a bounded, title-cased street-name suffix, not arbitrary prose."""
    match = _REVIEWED_STREET_NAME.search(before)
    if not match:
        return False
    first_token = match.group("name").split(maxsplit=1)[0].casefold()
    return first_token not in _STREET_NAME_PROSE


def _direction_place_evidence(before: str, after: str) -> bool:
    """Require a bounded address/street signal for a single compass letter."""
    if not _STREET_SUFFIX.search(after):
        return False
    return bool(_ADDRESS_NUMBER.search(before) or _reviewed_street_name_evidence(before))


class ContextProfile(ABC):
    """A bounded language policy for contextual abbreviation disambiguation."""

    @abstractmethod
    def detect_context(self, abbreviation: str, before: str, after: str) -> Any:
        raise NotImplementedError


class DefaultContextProfile(ContextProfile):
    def detect_context(self, abbreviation: str, before: str, after: str) -> Any:
        # This is evidence detection, not date parsing: inspect only the
        # bounded caller-provided windows and require a nearby numeric token.
        if _DATE_BEFORE.search(before) or _DATE_AFTER.search(after):
            return _context("date")
        if _TIME.search(before):
            return _context("time")
        if _HOUSE_AND_STREET.search(before):
            return _context("place")
        if after and _name_evidence(after):
            return _context("title")
        return _context("default")


class EnglishContextProfile(DefaultContextProfile):
    """Conservative English title, address, and saint/street policy."""

    _saints = {
        "peter",
        "paul",
        "john",
        "mary",
        "patrick",
        "francis",
        "joseph",
        "michael",
        "george",
        "luke",
        "mark",
        "matthew",
        "thomas",
        "james",
        "anthony",
        "andrew",
        "louis",
        "petersburg",
        "augustine",
        "helena",
        "cloud",
        "albans",
        "andrews",
    }

    def detect_context(self, abbreviation: str, before: str, after: str) -> Any:
        spelling = abbreviation.casefold()
        if spelling in {"n.", "s.", "e.", "w."}:
            if _direction_place_evidence(before, after):
                return _context("place")
            if after and _name_evidence(after):
                return _context("title")
            return _context("default")
        if spelling == "d.c." and (
            _WASHINGTON_PLACE.search(before) or _EXPLICIT_PLACE_AFTER.match(after)
        ):
            return _context("place")
        if _DATE_BEFORE.search(before) or _DATE_AFTER.search(after):
            return _context("date")
        if _TIME.search(before):
            return _context("time")
        if spelling in {"st.", "st"}:
            token = _first_lexical_token(after).casefold()
            if token in self._saints:
                return _context("religious")
            if re.search(r"\d+(?:st|nd|rd|th)\s*$", before, re.IGNORECASE):
                return _context("place")
            if _HOUSE_AND_STREET.search(before) or _reviewed_street_name_evidence(before):
                return _context("place")
            return _context("religious")
        if abbreviation.casefold() in {"dr.", "drive", "ave.", "rd.", "blvd."}:
            if after and _name_evidence(after) and not _HOUSE_AND_STREET.search(before):
                return _context("title")
            if _HOUSE_AND_STREET.search(before) or _STREET_NAME.search(before):
                return _context("place")
        if after and _name_evidence(after):
            return _context("title")
        if _HOUSE_AND_STREET.search(before):
            return _context("place")
        return _context("default")


class GermanContextProfile(DefaultContextProfile):
    """German title/date disambiguation with Unicode name evidence."""

    def detect_context(self, abbreviation: str, before: str, after: str) -> Any:
        if abbreviation.casefold() in {"st.", "st"}:
            if after and _name_evidence(after):
                return _context("place")
            return _context("default")
        if abbreviation.casefold() == "fr.":
            if after and _name_evidence(after):
                return _context("title")
            if re.search(r"\b(?:am|vom|bis|ab|jeden|jeder)\s*$", before, re.IGNORECASE):
                return _context("default")
            if _TIME.search(before):
                return _context("time")
            return _context("default")
        return super().detect_context(abbreviation, before, after)


class ItalianContextProfile(DefaultContextProfile):
    """Bounded date, title, and professional evidence for Italian collisions."""

    def detect_context(self, abbreviation: str, before: str, after: str) -> Any:
        spelling = abbreviation.casefold()
        if spelling in {"gen.", "mag."}:
            if _DATE_BEFORE.search(before) or _DATE_AFTER.search(after):
                return _context("date")
            if spelling == "gen." and after and _name_evidence(after):
                return _context("title")
            if spelling == "mag." and after and _name_evidence(after):
                if re.search(r"(?:^|\s)(?:dott\.|dottor|dott\.ssa)\s*$", before, re.IGNORECASE):
                    return _context("academic")
            return _context("default")
        return super().detect_context(abbreviation, before, after)


def profile_for(language: str) -> ContextProfile:
    base = language.split("_", 1)[0]
    if base == "en":
        return EnglishContextProfile()
    if base == "de":
        return GermanContextProfile()
    if base == "it":
        return ItalianContextProfile()
    return DefaultContextProfile()


__all__ = [
    "ContextProfile",
    "DefaultContextProfile",
    "EnglishContextProfile",
    "GermanContextProfile",
    "ItalianContextProfile",
    "profile_for",
]
