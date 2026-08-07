"""Core framework for multilingual abbreviation expansion.

This module provides the infrastructure for expanding abbreviations during text normalization. It supports:
- Simple 1:1 mappings (Prof. → Professor)
- Context-aware expansions (St. → Street/Saint based on context)
- Case-insensitive matching
- Word boundary detection
- Optional numeric/context guards for tricky abbreviations (e.g., No., in.)
"""

import re
from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable, Iterator
from dataclasses import dataclass, field
from enum import Enum
from re import Pattern
from typing import TypeAlias

from ._replacements import Replacement, apply_replacements, resolve_replacements
from .annotations import AnnotationIndex, TokenAnnotation, normalize_annotations
from .context import profile_for
from .units import (
    NUMBER_BEFORE_UNIT,
    UnitEntry,
    UnitMatch,
    iter_unit_replacements,
    unit_entries,
    unit_symbols,
)
from .units import (
    iter_unit_matches as _iter_unit_matches,
)


class AbbreviationContext(Enum):
    """Context types for disambiguating abbreviations."""

    DEFAULT = "default"  # Use default expansion
    TITLE = "title"  # Title/honorific (Dr. Smith)
    PLACE = "place"  # Place name (Main St.)
    TIME = "time"  # Time-related (3 P.M.)
    ACADEMIC = "academic"  # Academic degree (Ph.D.)
    RELIGIOUS = "religious"  # Religious context (St. Peter)


PosConstraints: TypeAlias = str | Collection[str] | None


def _abbreviation_pattern(value: str) -> str:
    """Escape an abbreviation while making registered horizontal spaces flexible."""

    pieces = re.split(r"([ \t\u00a0\u202f]+)", value)
    return "".join(
        r"[ \t\u00a0\u202f]+" if piece and not piece.strip(" \t\u00a0\u202f") else re.escape(piece)
        for piece in pieces
    )


def _entry_pattern(entry: "AbbreviationEntry", spelling: str | None = None) -> Pattern[str]:
    """Compile the symmetric boundary policy for one registered spelling."""

    flags = 0 if entry.case_sensitive else re.IGNORECASE
    return re.compile(
        rf"(?<!\w){_abbreviation_pattern(spelling or entry.abbreviation)}(?!\w)",
        flags,
    )


@dataclass(frozen=True, slots=True)
class ProtectedSpan:
    """A source range that must not be changed by expansion."""

    start: int
    end: int
    kind: str | None = None


@dataclass(frozen=True, slots=True)
class ExpansionMatch:
    """One accepted source-aligned expansion from :meth:`expand_with_trace`."""

    start: int
    end: int
    source_text: str
    replacement: str
    language: str
    entry_id: str
    kind: str
    context: AbbreviationContext | None
    priority: int


@dataclass(frozen=True, slots=True)
class ExpansionReplacement:
    """One accepted replacement against the original source text."""

    start: int
    end: int
    text: str
    source: str
    kind: str
    language: str
    abbreviation: str | None = None
    rule: str | None = None
    priority: int = 0
    context: AbbreviationContext | None = field(default=None, repr=False)

    @property
    def replacement(self) -> str:
        """Compatibility alias for the replacement text."""
        return self.text

    @property
    def entry_id(self) -> str:
        """Compatibility alias for the stable rule/source identifier."""
        return self.rule or self.source


@dataclass(frozen=True, slots=True)
class ExpansionResult:
    """Expanded text together with accepted source replacements."""

    source_text: str
    text: str
    replacements: tuple[ExpansionReplacement, ...]

    @property
    def matches(self) -> tuple[ExpansionMatch, ...]:
        """Return the legacy trace view of :attr:`replacements`."""
        return tuple(
            ExpansionMatch(
                start=item.start,
                end=item.end,
                source_text=self.source_text[item.start : item.end],
                replacement=item.text,
                language=item.language,
                entry_id=item.entry_id,
                kind=item.kind,
                context=item.context,
                priority=item.priority,
            )
            for item in self.replacements
        )


@dataclass
class AbbreviationEntry:
    """A single abbreviation with its expansion(s).

    Attributes:
        abbreviation: The abbreviated form (e.g., "Prof.")
        expansion: Default expansion (e.g., "Professor")
        context_expansions: Optional dict of context-specific expansions
        case_sensitive: Whether matching should be case-sensitive
        description: Human-readable description of the abbreviation
        only_if_preceded_by: Optional regex that must match the text immediately
            before the abbreviation match (typically anchored with $).
        only_if_followed_by: Optional regex that must match the suffix immediately
            after the abbreviation match. The pattern is matched against
            ``text[end:]``; therefore ``^`` means immediately after this
            candidate, not the beginning of the complete source string.
        only_if_pos: Optional coarse POS label or labels. POS evidence is
            evaluated only when usable source-aligned annotations are present.
        not_if_pos: Optional coarse POS label or labels that veto a match when
            they overlap the abbreviation. This guard takes precedence over
            ``only_if_pos``.
    """

    abbreviation: str
    expansion: str
    context_expansions: dict[AbbreviationContext, str] | None = None
    case_sensitive: bool = False
    description: str = ""
    only_if_preceded_by: str | Pattern[str] | None = None
    only_if_followed_by: str | Pattern[str] | None = None
    only_if_pos: PosConstraints = None
    not_if_pos: PosConstraints = None
    origin: str = "bundled"
    aliases: tuple[str, ...] = ()
    _pattern: Pattern[str] = field(init=False, repr=False, compare=False)
    _patterns: tuple[Pattern[str], ...] = field(init=False, repr=False, compare=False)
    _preceding_pattern: Pattern[str] | None = field(init=False, repr=False, compare=False)
    _following_pattern: Pattern[str] | None = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.abbreviation, str):
            raise TypeError("abbreviation must be a string")
        if not self.abbreviation or not self.abbreviation.strip():
            raise ValueError("abbreviation must not be empty or whitespace-only")
        if self.abbreviation != self.abbreviation.strip():
            raise ValueError("abbreviation must not have leading or trailing whitespace")
        if not isinstance(self.expansion, str):
            raise TypeError("expansion must be a string")
        if not self.expansion:
            raise ValueError("expansion must not be empty")
        if type(self.case_sensitive) is not bool:
            raise TypeError("case_sensitive must be a bool")
        if not isinstance(self.aliases, tuple):
            raise TypeError("aliases must be a tuple of strings")
        for alias in self.aliases:
            if not isinstance(alias, str):
                raise TypeError("aliases must contain only strings")
            if not alias or not alias.strip() or alias != alias.strip():
                raise ValueError("aliases must not be empty or have leading/trailing whitespace")
            if alias == self.abbreviation:
                raise ValueError("aliases must differ from abbreviation")
        if len(set(self.aliases)) != len(self.aliases):
            raise ValueError("aliases must not contain duplicates")
        if not isinstance(self.description, str):
            raise TypeError("description must be a string")
        if self.origin not in {"bundled", "custom"}:
            raise ValueError("origin must be 'bundled' or 'custom'")
        if self.context_expansions is not None:
            if not isinstance(self.context_expansions, dict):
                raise TypeError("context_expansions must be a dictionary")
            if not self.context_expansions:
                raise ValueError("context_expansions must not be empty")
            for context, value in self.context_expansions.items():
                if not isinstance(context, AbbreviationContext):
                    raise TypeError("context expansion keys must be AbbreviationContext values")
                if not isinstance(value, str):
                    raise TypeError("context expansion values must be strings")
                if not value:
                    raise ValueError("context expansion values must not be empty")
        for name in ("only_if_preceded_by", "only_if_followed_by"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, (str, re.Pattern)):
                raise TypeError(f"{name} must be a string, compiled regex, or None")
        self.only_if_pos = _normalize_pos_constraints(self.only_if_pos)
        self.not_if_pos = _normalize_pos_constraints(self.not_if_pos)
        self._patterns = tuple(
            _entry_pattern(self, spelling) for spelling in (self.abbreviation, *self.aliases)
        )
        self._pattern = self._patterns[0]
        self._preceding_pattern = _compile_guard(self.only_if_preceded_by, "only_if_preceded_by")
        self._following_pattern = _compile_guard(self.only_if_followed_by, "only_if_followed_by")

    def get_expansion(self, context: AbbreviationContext | None = None) -> str:
        """Get the appropriate expansion for the given context.

        Args:
            context: The context type, or None for default

        Returns:
            The expanded form
        """
        if context and self.context_expansions and context in self.context_expansions:
            return self.context_expansions[context]
        return self.expansion


def _normalize_pos_constraints(
    labels: PosConstraints,
) -> frozenset[str] | None:
    if labels is None:
        return None
    if isinstance(labels, str):
        labels = (labels,)
    elif not isinstance(labels, Collection):
        raise TypeError("POS constraints must be strings or collections of strings")
    normalized: set[str] = set()
    for label in labels:
        if not isinstance(label, str):
            raise TypeError(f"POS constraint labels must be strings, got {type(label).__name__}")
        value = label.strip().upper()
        if not value:
            raise ValueError("POS constraint labels must not be empty")
        normalized.add(value)
    if not normalized:
        raise ValueError("POS constraints must not be empty")
    return frozenset(normalized)


def _compile_guard(
    value: str | Pattern[str] | None,
    name: str,
) -> Pattern[str] | None:
    if value is None:
        return None
    try:
        return re.compile(value)
    except re.error as exc:
        raise ValueError(f"{name} is not a valid regular expression: {exc}") from exc


def abbreviation_guards_match(
    entry: AbbreviationEntry,
    text: str,
    start: int,
    end: int,
    *,
    preceding_window: int = 80,
    annotations: AnnotationIndex | Iterable[TokenAnnotation] | None = None,
) -> bool:
    """Return whether an abbreviation entry's configured guards match.

    Sequence annotations are validated and normalized against the original
    source text before POS guards are evaluated. Structural and numeric-unit
    guards are authoritative; POS deny guards take precedence over POS allow
    guards, and missing lexical POS evidence fails open.

    Args:
        entry: Abbreviation definition whose guards should be checked.
        text: Complete source text containing the candidate abbreviation.
        start: Candidate start offset in ``text``.
        end: Candidate end offset in ``text``.
        preceding_window: Maximum number of preceding characters to inspect.
        annotations: Optional source-aligned annotations. Only coarse ``pos``
            labels are evaluated; ``tag`` is retained as provider metadata.

    Returns:
        ``True`` when every configured guard matches. Unguarded entries always
        return ``True``.
    """
    if not (0 <= start <= end <= len(text)):
        return False

    if entry.only_if_preceded_by:
        pattern = entry._preceding_pattern
        if pattern is None:
            return False
        raw_before = text[max(0, start - preceding_window) : start]
        before_variants = (raw_before, raw_before.rstrip(" \t\u00a0\u202f"))
        if not any(
            (match := pattern.search(before)) is not None and match.end() == len(before)
            for before in before_variants
        ):
            return False

    if entry.only_if_followed_by:
        pattern = entry._following_pattern
        # Match a suffix slice rather than passing ``end`` as the regex
        # starting position. This preserves the intended relative meaning of
        # anchors such as ``^\s*\d`` for candidates after preceding text.
        if pattern is None or not pattern.match(text[end:]):
            return False

    if annotations is not None and (entry.only_if_pos or entry.not_if_pos):
        index = (
            annotations
            if isinstance(annotations, AnnotationIndex)
            else AnnotationIndex(normalize_annotations(text, annotations))
        )
        lexical_pos = tuple(
            annotation.pos
            for annotation in index.overlapping(start, end)
            if annotation.pos and annotation.pos not in {"PUNCT", "SPACE"}
        )
        if entry.not_if_pos and any(pos in entry.not_if_pos for pos in lexical_pos):
            return False
        if (
            entry.only_if_pos
            and lexical_pos
            and not any(pos in entry.only_if_pos for pos in lexical_pos)
        ):
            return False

    return True


class ContextDetector:
    """Detects context for abbreviations based on surrounding text."""

    def __init__(self, language: str = "en") -> None:
        """Initialize context detector with pattern matchers."""
        self.profile = profile_for(language)
        # Patterns for detecting place names (street, avenue, etc.)
        # Match addresses like "123 Main", "100 N. Main", "50 North Elm"
        self.place_indicators = re.compile(
            # Address number, optional direction abbrev
            r"\b\d+\s+(?:[A-Z]\.\s+)?\w+(?:\s+\w+)*$",
            re.IGNORECASE,
        )

        # Patterns for detecting titles (before names)
        self.title_indicators = re.compile(
            r"^(?:\w+\s+)*[A-Z][a-z]+",  # Followed by capitalized name
        )

        # Patterns for detecting time (with numbers)
        self.time_indicators = re.compile(
            r"\b\d{1,2}(?::\d{2})?\s*$",  # Preceded by time (3:00, 5)
            re.IGNORECASE,
        )

    def detect_context(self, abbreviation: str, before: str, after: str) -> AbbreviationContext:
        """Detect the context of an abbreviation.

        Args:
            abbreviation: The abbreviation itself
            before: Text before the abbreviation
            after: Text after the abbreviation

        Returns:
            The detected context type

        Note:
            St. abbreviation uses multi-signal detection for robustness:
            - Priority 1: Saint/city name recognition (highest confidence)
            - Priority 2: House number pattern in close proximity (~30 chars)
            - Priority 3: Default to "Saint" for unknown names

            Examples:
                "123 Main St." → Street (house number pattern)
                "St. Louis" → Saint (city name recognized)
                "Visit 123 St. Louis Ave" → Saint (name wins over distant number)
                "born in 1850, St. Peter" → Saint (name + distant number)
        """
        return self.profile.detect_context(abbreviation, before, after)

        # Check for time context (3 P.M., 5 A.M.)
        if self.time_indicators.search(before):
            return AbbreviationContext.TIME

        # Special handling for St. abbreviation (Saint vs Street)
        # Uses multi-signal approach for robust detection
        if abbreviation.lower() in ["st.", "st"]:
            # PRIORITY 1: Check for saint/city name (HIGHEST CONFIDENCE)
            if after:
                # Common saint names
                saint_names = {
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
                }

                # Common city names that start with St.
                city_names = {
                    "louis",
                    "paul",
                    "petersburg",
                    "augustine",
                    "helena",
                    "cloud",
                    "albans",
                    "andrews",
                }

                # Get first word and clean it (remove possessives, punctuation)
                first_word = after.strip().split()[0].lower() if after.strip() else ""
                first_word = first_word.rstrip("'s.,;:!?")

                if first_word in saint_names or first_word in city_names:
                    return AbbreviationContext.RELIGIOUS

            # PRIORITY 2: Check for house number pattern (CLOSE PROXIMITY)
            # Only check last 30 characters to avoid distant numbers
            # Pattern: "[number] [optional direction] [street name]"
            # Examples: "123 Main", "456 N. Oak", "10 Park"
            proximity_limit = 30
            recent_text = before[-proximity_limit:] if len(before) > proximity_limit else before

            # Special case: Ordinal numbers directly before St. = Street
            # "5th St." "42nd St." "3rd St."
            ordinal_street_pattern = re.compile(r"\d+(?:st|nd|rd|th)\s*$", re.IGNORECASE)
            if ordinal_street_pattern.search(recent_text):
                return AbbreviationContext.PLACE

            # Match house number followed by optional direction and street
            # Catches: "123 Main St." "456 N. Oak St."
            # But NOT: "born in 1850, St." (too far away)
            house_number_pattern = re.compile(
                # Number + optional direction + capitalized word
                r"\d+\s+(?:[NSEW]\.?\s+)?[A-Z]\w*\s*$",
                re.IGNORECASE,
            )

            if house_number_pattern.search(recent_text):
                return AbbreviationContext.PLACE

            # PRIORITY 3: Default to religious (Saint)
            return AbbreviationContext.RELIGIOUS

        # Check for place context for other abbreviations (Ave., Rd., Blvd., etc.)
        if self.place_indicators.search(before):
            return AbbreviationContext.PLACE

        # Check for title context (Dr. Smith, Prof. Johnson)
        if after and self.title_indicators.match(after):
            return AbbreviationContext.TITLE

        return AbbreviationContext.DEFAULT


class AbbreviationExpander(ABC):
    """Abstract base class for language-specific abbreviation expanders."""

    def __init__(
        self,
        enable_context_detection: bool = True,
    ) -> None:
        """Initialize the abbreviation expander.

        Args:
            enable_context_detection: Whether to use context-aware expansion
        """
        self.entries: dict[str, AbbreviationEntry] = {}
        language = getattr(self, "UNIT_LANGUAGE", "en")
        self.unit_entries = unit_entries(language)
        self._unit_symbols = unit_symbols(language)
        self._unit_overrides: dict[str, UnitEntry] = {}
        self._suppressed_units: set[str] = set()
        self.enable_context_detection = enable_context_detection
        self.context_detector = ContextDetector(language) if enable_context_detection else None
        self._initialize_abbreviations()

    @abstractmethod
    def _initialize_abbreviations(self) -> None:
        """Initialize language-specific abbreviations.

        Subclasses must implement this to populate self.entries.
        """

    def add_abbreviation(self, entry: AbbreviationEntry) -> None:
        """Add an abbreviation entry.

        Args:
            entry: The abbreviation entry to add
        """
        unit_entry = next(
            (item for item in self.unit_entries if entry.abbreviation in item.symbols),
            None,
        )
        if unit_entry is not None and entry.origin == "custom":
            raise ValueError(
                f"{entry.abbreviation!r} is a unit symbol; use set_unit() for unit customization"
            )
        if unit_entry is not None and unit_entry.category != "magnitude":
            entry.case_sensitive = True
            entry.only_if_preceded_by = entry.only_if_preceded_by or NUMBER_BEFORE_UNIT
            # Rebuild the compiled fields if a legacy language registry supplied a
            # unit entry with the default case-insensitive setting.
            entry._pattern = _entry_pattern(entry)
            entry._patterns = (entry._pattern,)
            entry._preceding_pattern = _compile_guard(
                entry.only_if_preceded_by, "only_if_preceded_by"
            )
        key = entry.abbreviation if entry.case_sensitive else entry.abbreviation.lower()
        self.entries[key] = entry

    def add_custom_abbreviation(
        self,
        abbreviation: str,
        expansion: str | dict[str, str],
        description: str = "",
        case_sensitive: bool = False,
        only_if_preceded_by: str | Pattern[str] | None = None,
        only_if_followed_by: str | Pattern[str] | None = None,
        only_if_pos: PosConstraints = None,
        not_if_pos: PosConstraints = None,
    ) -> None:
        """Add or replace an entry using string context names and POS guards.

        A single POS string is treated as one label, while a collection can
        express several accepted or denied labels. Labels are normalized by
        :class:`AbbreviationEntry`.
        """
        context_expansions: dict[AbbreviationContext, str] | None = None
        default_expansion: str = expansion if isinstance(expansion, str) else ""
        if not isinstance(expansion, (str, dict)):
            raise TypeError("expansion must be a string or context-expansion dictionary")
        if isinstance(expansion, dict):
            if not expansion:
                raise ValueError("context expansion dictionary must not be empty")
            context_expansions = {}
            for key, value in expansion.items():
                if not isinstance(key, str):
                    raise TypeError("context expansion keys must be strings")
                if not isinstance(value, str):
                    raise TypeError("context expansion values must be strings")
                try:
                    context = AbbreviationContext(key.lower())
                except ValueError:
                    if key.lower() == AbbreviationContext.DEFAULT.value:
                        default_expansion = value
                        continue
                    raise ValueError(
                        f"Unknown context '{key}'. Valid contexts are: "
                        "default, title, place, time, academic, religious"
                    ) from None
                if context is AbbreviationContext.DEFAULT:
                    default_expansion = value
                    continue
                context_expansions[context] = value
            if AbbreviationContext.DEFAULT.value not in {key.lower() for key in expansion}:
                default_expansion = next(iter(expansion.values()))

        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation=abbreviation,
                expansion=default_expansion,
                context_expansions=context_expansions,
                case_sensitive=case_sensitive,
                description=description,
                only_if_preceded_by=only_if_preceded_by,
                only_if_followed_by=only_if_followed_by,
                only_if_pos=only_if_pos,
                not_if_pos=not_if_pos,
                origin="custom",
            )
        )

    def set_unit(
        self,
        symbol: str,
        expansion: str,
        *,
        case_sensitive: bool = True,
        description: str = "Custom unit",
        canonical_id: str | None = None,
        category: str = "unit",
    ) -> None:
        """Override one reviewed unit for this expander instance."""
        if not isinstance(symbol, str) or not symbol:
            raise TypeError("unit symbol must be a non-empty string")
        if not isinstance(expansion, str):
            raise TypeError("unit expansion must be a string")
        if not expansion:
            raise ValueError("unit expansion must not be empty")
        if type(case_sensitive) is not bool:
            raise TypeError("case_sensitive must be a bool")
        if canonical_id is None:
            canonical_id = next(
                (
                    entry.canonical_id
                    for entry in self.unit_entries
                    if symbol in entry.symbols and entry.canonical_id is not None
                ),
                None,
            )
        self._unit_overrides[symbol] = UnitEntry(
            (symbol,),
            expansion,
            case_sensitive=case_sensitive,
            description=description,
            canonical_symbol=symbol,
            requires_numeric_value=True,
            canonical_id=canonical_id,
            category=category,
        )
        self._suppressed_units.discard(symbol)
        if canonical_id is not None:
            self._suppressed_units.discard(canonical_id)

    def remove_unit(self, symbol: str) -> bool:
        """Suppress a bundled unit or remove an instance-local unit override."""
        override_keys = [
            key
            for key, entry in self._unit_overrides.items()
            if key == symbol or entry.canonical_id == symbol
        ]
        if override_keys:
            for key in override_keys:
                del self._unit_overrides[key]
            self._suppressed_units.add(symbol)
            return True
        if symbol in self._unit_symbols or any(
            entry.canonical_id == symbol for entry in self.unit_entries
        ):
            self._suppressed_units.add(symbol)
            return True
        return False

    def has_unit(self, symbol: str) -> bool:
        if symbol in self._unit_overrides:
            return True
        return any(
            (symbol in entry.symbols or entry.canonical_id == symbol)
            and symbol not in self._suppressed_units
            and entry.canonical_id not in self._suppressed_units
            for entry in self.unit_entries
        )

    def iter_unit_matches(
        self,
        text: str,
        *,
        protected_spans: Iterable[tuple[int, int]] = (),
    ) -> Iterator[UnitMatch]:
        """Yield structured matches using this expander's unit customization."""
        return _iter_unit_matches(
            text,
            getattr(self, "UNIT_LANGUAGE", "en"),
            overrides=self._unit_overrides,
            suppressed=self._suppressed_units,
            protected_spans=protected_spans,
        )

    def remove_abbreviation(self, abbreviation: str, case_sensitive: bool = False) -> bool:
        """Remove an abbreviation entry.

        Args:
            abbreviation: The abbreviation to remove (e.g., "Dr.")
            case_sensitive: Whether to match case-sensitively

        Returns:
            True if the abbreviation was found and removed, False otherwise
        """
        if abbreviation in self._unit_symbols:
            raise ValueError("unit symbols must be changed with set_unit() or remove_unit()")
        key = abbreviation if case_sensitive else abbreviation.lower()
        if key in self.entries:
            del self.entries[key]
            return True
        return False

    def has_abbreviation(self, abbreviation: str, case_sensitive: bool = False) -> bool:
        """Check if an abbreviation exists.

        Args:
            abbreviation: The abbreviation to check (e.g., "Dr.")
            case_sensitive: Whether to match case-sensitively

        Returns:
            True if the abbreviation exists, False otherwise
        """
        key = abbreviation if case_sensitive else abbreviation.lower()
        return key in self.entries

    def get_abbreviation(
        self, abbreviation: str, case_sensitive: bool = False
    ) -> AbbreviationEntry | None:
        """Get an abbreviation entry.

        Args:
            abbreviation: The abbreviation to retrieve (e.g., "Dr.")
            case_sensitive: Whether to match case-sensitively

        Returns:
            The abbreviation entry if found, None otherwise
        """
        key = abbreviation if case_sensitive else abbreviation.lower()
        return self.entries.get(key)

    def expand(
        self,
        text: str,
        *,
        annotations: Iterable[TokenAnnotation] | None = None,
        protected_spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]]
        | None = None,
    ) -> str:
        """Expand all abbreviations in the text.

        Args:
            text: Input text containing abbreviations
            annotations: Optional provider-neutral annotations aligned to the
                original source offsets. Incomplete lexical POS evidence does
                not suppress a structurally valid match.

        Returns:
            Text with abbreviations expanded
        """
        return self.expand_with_replacements(
            text, annotations=annotations, protected_spans=protected_spans
        ).text

    def expand_with_replacements(
        self,
        text: str,
        *,
        annotations: Iterable[TokenAnnotation] | None = None,
        protected_spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]]
        | None = None,
    ) -> ExpansionResult:
        """Expand text and return exact immutable replacement metadata."""
        return self._expand_result(text, annotations=annotations, protected_spans=protected_spans)

    def expand_with_trace(
        self,
        text: str,
        *,
        annotations: Iterable[TokenAnnotation] | None = None,
        protected_spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]]
        | None = None,
    ) -> ExpansionResult:
        """Compatibility alias for :meth:`expand_with_replacements`."""
        return self.expand_with_replacements(
            text, annotations=annotations, protected_spans=protected_spans
        )

    def _expand_result(
        self,
        text: str,
        *,
        annotations: Iterable[TokenAnnotation] | None,
        protected_spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]]
        | None,
    ) -> ExpansionResult:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        spans = _normalize_protected_spans(text, protected_spans)
        normalized_annotations = normalize_annotations(text, annotations)
        annotation_index = (
            AnnotationIndex(normalized_annotations) if annotations is not None else None
        )
        candidates: list[Replacement] = list(
            iter_unit_replacements(
                text,
                getattr(self, "UNIT_LANGUAGE", "en"),
                self._unit_overrides,
                self._suppressed_units,
            )
        )
        candidates = [
            candidate for candidate in candidates if not _overlaps_spans(candidate, spans)
        ]

        # Process all abbreviations against the original source. The resolver
        # preserves longest-first behavior while giving reviewed units priority.
        for entry in self.entries.values():
            unit_entry = next(
                (item for item in self.unit_entries if entry.abbreviation in item.symbols),
                None,
            )
            if unit_entry is not None and unit_entry.category != "magnitude":
                continue
            candidates.extend(
                candidate
                for candidate in self._iter_entry_replacements(text, entry, annotation_index)
                if not _overlaps_spans(candidate, spans)
            )

        selected = resolve_replacements(candidates)
        language = getattr(self, "UNIT_LANGUAGE", "en")
        return ExpansionResult(
            source_text=text,
            text=apply_replacements(text, selected),
            replacements=tuple(
                ExpansionReplacement(
                    start=item.start,
                    end=item.end,
                    text=item.text,
                    source=item.source,
                    kind=item.kind,
                    language=language,
                    abbreviation=(
                        item.source.removeprefix("abbr:") if item.kind == "abbreviation" else None
                    ),
                    rule=item.entry_id or item.source,
                    priority=item.priority,
                    context=item.context if isinstance(item.context, AbbreviationContext) else None,
                )
                for item in selected
            ),
        )

    def _iter_entry_replacements(
        self,
        text: str,
        entry: AbbreviationEntry,
        annotation_index: AnnotationIndex | None,
    ) -> Iterator[Replacement]:
        """Yield abbreviation candidates using original source offsets.

        Args:
            text: Input text
            entry: The abbreviation entry to expand

        Returns:
            Replacement candidates for this abbreviation
        """
        for pattern in entry._patterns:
            for match in pattern.finditer(text):
                start, end = match.span()

                # A dotted abbreviation embedded after another period is usually a
                # fragment of a longer initialism (for example ``B.S.`` in
                # ``A.B.S.``). Leave it intact unless the complete longer entry
                # was matched during the longest-first pass.
                if (
                    start > 1
                    and text[start - 1] == "."
                    and text[start - 2].isalnum()
                    and "." in match.group()
                ):
                    continue

                if not abbreviation_guards_match(
                    entry,
                    text,
                    start,
                    end,
                    annotations=annotation_index,
                ):
                    continue

                if not self.enable_context_detection or not self.context_detector:
                    expansion = entry.expansion
                    context = None
                else:
                    # Get surrounding context from the original source.
                    window = 96
                    before = text[max(0, start - window) : start].rstrip()
                    after = text[end : min(len(text), end + window)].lstrip()
                    context = self.context_detector.detect_context(match.group(), before, after)
                    expansion = entry.get_expansion(context)

                yield Replacement(
                    start=start,
                    end=end,
                    text=expansion,
                    priority=_entry_priority(entry),
                    source=f"abbr:{entry.abbreviation}",
                    kind="abbreviation",
                    entry_id=f"abbr:{entry.abbreviation}",
                    context=context,
                )

    def get_abbreviations_list(self) -> list[str]:
        """Get a list of all supported abbreviations.

        Returns:
            List of abbreviation strings
        """
        return [entry.abbreviation for entry in self.entries.values()]

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}(abbreviations={len(self.entries)})"


def _entry_priority(entry: AbbreviationEntry) -> int:
    """Return the documented deterministic precedence for abbreviation entries."""
    if entry.origin == "custom":
        return 220 if entry.case_sensitive else 120
    return 210 if entry.case_sensitive else 110


def _normalize_protected_spans(
    text: str,
    spans: Iterable[ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]] | None,
) -> tuple[ProtectedSpan, ...]:
    if spans is None:
        return ()
    normalized: list[ProtectedSpan] = []
    for index, span in enumerate(spans):
        if isinstance(span, ProtectedSpan):
            item = span
        elif isinstance(span, tuple) and len(span) in {2, 3}:
            item = ProtectedSpan(*span)
        else:
            raise TypeError(f"protected span {index} must be ProtectedSpan or a 2/3-tuple")
        if not (0 <= item.start < item.end <= len(text)):
            raise ValueError(f"protected span {index} is outside the source text")
        if item.kind is not None and not isinstance(item.kind, str):
            raise TypeError(f"protected span {index} kind must be a string or None")
        normalized.append(item)
    normalized.sort(key=lambda item: (item.start, item.end))
    for index in range(1, len(normalized)):
        if normalized[index].start < normalized[index - 1].end:
            raise ValueError("protected spans must not overlap")
    return tuple(normalized)


def _overlaps_spans(item: Replacement, spans: tuple[ProtectedSpan, ...]) -> bool:
    return any(item.start < span.end and span.start < item.end for span in spans)
