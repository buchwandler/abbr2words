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
from collections.abc import Collection, Iterable, Iterator, Mapping
from dataclasses import dataclass, field, replace
from enum import Enum
from re import Pattern
from typing import Literal, TypeAlias

from ._replacements import Replacement, apply_replacements, resolve_replacements
from .annotations import AnnotationIndex, TokenAnnotation, normalize_annotations
from .context import profile_for
from .initialisms import (
    InitialismCase,
    InitialismDiagnostic,
    InitialismMode,
    InitialismPolicy,
    RegisteredInitialismMode,
    iter_initialism_replacements,
    render_initialism_source,
    should_preserve_sentence_final_period,
)
from .initialisms import (
    iter_initialism_diagnostics as _iter_initialism_diagnostics,
)
from .registry_keys import normalize_entry_key
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
    DATE = "date"  # Bounded numeric date evidence (5 Mar. 2026)
    ACADEMIC = "academic"  # Academic degree (Ph.D.)
    RELIGIOUS = "religious"  # Religious context (St. Peter)


PosConstraints: TypeAlias = str | Collection[str] | None
CasePolicy: TypeAlias = Literal["fixed", "sentence"]
SpeechStrategy: TypeAlias = Literal["expand", "spell_source", "custom"]
BulkConflictPolicy: TypeAlias = Literal["error", "replace"]
ExpansionKind: TypeAlias = Literal["abbreviation", "unit"]

def _abbreviation_pattern(value: str) -> str:
    """Escape an abbreviation while making registered horizontal spaces flexible."""

    pieces = re.split(r"([ \t\u00a0\u202f]+)", value)
    return "".join(
        r"[ \t\u00a0\u202f]+" if piece and not piece.strip(" \t\u00a0\u202f") else re.escape(piece)
        for piece in pieces
    )


def _entry_pattern(entry: "AbbreviationEntry", spelling: str | None = None) -> Pattern[str]:
    """Compile the reviewed boundary policy for one registered spelling."""

    flags = 0 if entry.case_sensitive else re.IGNORECASE
    if entry.boundary == "word":
        left_boundary = r"(?<!\w)"
        right_boundary = r"(?!\w)"
    else:
        left_boundary = entry.left_boundary or ""
        right_boundary = entry.right_boundary or ""
    return re.compile(
        rf"{left_boundary}{_abbreviation_pattern(spelling or entry.abbreviation)}{right_boundary}",
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
class ExpansionVariant:
    """One ordered, declarative conditional expansion for an abbreviation.

    Variants deliberately reuse the entry guard vocabulary instead of accepting
    callbacks.  This keeps registry data serializable and makes selection
    deterministic and safe to evaluate against the original source text.
    """

    expansion: str
    only_if_preceded_by: str | Pattern[str] | None = None
    only_if_followed_by: str | Pattern[str] | None = None
    only_if_pos: PosConstraints = None
    not_if_pos: PosConstraints = None
    _preceding_pattern: Pattern[str] | None = field(init=False, repr=False, compare=False)
    _following_pattern: Pattern[str] | None = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.expansion, str):
            raise TypeError("variant expansion must be a string")
        if not self.expansion:
            raise ValueError("variant expansion must not be empty")
        for name in ("only_if_preceded_by", "only_if_followed_by"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, (str, re.Pattern)):
                raise TypeError(f"{name} must be a string, compiled regex, or None")
        object.__setattr__(self, "only_if_pos", _normalize_pos_constraints(self.only_if_pos))
        object.__setattr__(self, "not_if_pos", _normalize_pos_constraints(self.not_if_pos))
        object.__setattr__(
            self,
            "_preceding_pattern",
            _compile_guard(self.only_if_preceded_by, "only_if_preceded_by"),
        )
        object.__setattr__(
            self,
            "_following_pattern",
            _compile_guard(self.only_if_followed_by, "only_if_followed_by"),
        )


@dataclass(frozen=True, slots=True)
class ExpansionReplacement:
    """One accepted replacement against the original source text."""

    start: int
    end: int
    text: str
    source: str
    kind: ExpansionKind
    language: str
    abbreviation: str | None = None
    rule: str | None = None
    priority: int = 0
    context: AbbreviationContext | None = field(default=None, repr=False)
    matched_text: str = ""
    canonical_id: str | None = None

    @property
    def replacement(self) -> str:
        """Compatibility alias for the replacement text."""
        return self.text

    @property
    def source_text(self) -> str:
        """Original source substring consumed by this replacement."""
        return self.matched_text

    @property
    def rule_id(self) -> str:
        """Stable identifier for the rule that produced this replacement."""
        return self.rule or self.source

    @property
    def entry_id(self) -> str:
        """Compatibility alias for the stable rule/source identifier."""
        return self.rule_id


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


AbbreviationConflictKind: TypeAlias = Literal["duplicate", "canonical_collision", "alias_collision"]


@dataclass(frozen=True, slots=True)
class AbbreviationConflict:
    """One canonical or alias collision found during bulk registration."""

    key: str
    incoming_abbreviation: str
    existing_abbreviation: str | None
    kind: AbbreviationConflictKind


class AbbreviationConflictError(ValueError):
    """Raised when bulk registration finds one or more conflicts."""

    def __init__(self, conflicts: Iterable[AbbreviationConflict]) -> None:
        self.conflicts = tuple(conflicts)
        details = ", ".join(
            f"{item.incoming_abbreviation!r} ({item.kind})" for item in self.conflicts
        )
        super().__init__(f"abbreviation conflicts: {details}")


@dataclass(frozen=True, slots=True)
class BulkAddResult:
    """Summary of an atomic bulk registration operation."""

    added: int
    replaced: int
    entries: tuple[str, ...]
    replacements: tuple[str, ...]


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
    variants: tuple[ExpansionVariant, ...] = ()
    case_sensitive: bool = False
    description: str = ""
    only_if_preceded_by: str | Pattern[str] | None = None
    only_if_followed_by: str | Pattern[str] | None = None
    only_if_pos: PosConstraints = None
    not_if_pos: PosConstraints = None
    boundary: Literal["word", "custom"] = "word"
    left_boundary: str | None = None
    right_boundary: str | None = None
    origin: str = "bundled"
    aliases: tuple[str, ...] = ()
    case_policy: CasePolicy = "fixed"
    speech_strategy: SpeechStrategy = "expand"
    preserve_sentence_final_period: bool = True
    spoken_form: str | None = None
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
        if self.case_policy not in {"fixed", "sentence"}:
            raise ValueError("case_policy must be 'fixed' or 'sentence'")
        if self.speech_strategy not in {"expand", "spell_source", "custom"}:
            raise ValueError(
                "speech_strategy must be 'expand', 'spell_source', or 'custom'"
            )
        if self.speech_strategy == "custom":
            if not isinstance(self.spoken_form, str) or not self.spoken_form.strip():
                raise ValueError("speech_strategy='custom' requires a non-empty spoken_form")
        elif self.spoken_form is not None:
            raise ValueError("spoken_form is only valid when speech_strategy='custom'")
        if type(self.preserve_sentence_final_period) is not bool:
            raise TypeError("preserve_sentence_final_period must be a bool")
        if self.boundary not in {"word", "custom"}:
            raise ValueError("boundary must be 'word' or 'custom'")
        for name in ("left_boundary", "right_boundary"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{name} must be a string or None")
        if self.boundary == "word" and (self.left_boundary or self.right_boundary):
            raise ValueError("custom boundary expressions require boundary='custom'")
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
        if not isinstance(self.variants, tuple):
            raise TypeError("variants must be a tuple of ExpansionVariant values")
        if any(not isinstance(variant, ExpansionVariant) for variant in self.variants):
            raise TypeError("variants must contain only ExpansionVariant values")
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


def _parse_context_expansion_mapping(
    expansion: Mapping[str, str],
) -> tuple[str, dict[AbbreviationContext, str] | None]:
    """Parse string-named contexts into the canonical entry representation."""
    if not expansion:
        raise ValueError("context expansion dictionary must not be empty")
    default_expansion: str | None = None
    context_expansions: dict[AbbreviationContext, str] = {}
    for key, value in expansion.items():
        if not isinstance(key, str):
            raise TypeError("context expansion keys must be strings")
        if not isinstance(value, str):
            raise TypeError("context expansion values must be strings")
        try:
            context = AbbreviationContext(key.lower())
        except ValueError:
            raise ValueError(
                f"Unknown context '{key}'. Valid contexts are: "
                f"{', '.join(item.value for item in AbbreviationContext)}"
            ) from None
        if not value:
            raise ValueError("context expansion values must not be empty")
        if context is AbbreviationContext.DEFAULT:
            default_expansion = value
        else:
            context_expansions[context] = value
    if default_expansion is None:
        default_expansion = next(iter(expansion.values()))
    return default_expansion, context_expansions or None


def _build_custom_abbreviation_entry(
    abbreviation: str,
    expansion: str | Mapping[str, str],
    *,
    context_expansions: Mapping[AbbreviationContext, str] | None = None,
    case_sensitive: bool = False,
    description: str = "",
    only_if_preceded_by: str | Pattern[str] | None = None,
    only_if_followed_by: str | Pattern[str] | None = None,
    only_if_pos: PosConstraints = None,
    not_if_pos: PosConstraints = None,
    case_policy: CasePolicy = "fixed",
    speech_strategy: SpeechStrategy = "expand",
    spoken_form: str | None = None,
    aliases: tuple[str, ...] = (),
) -> AbbreviationEntry:
    """Construct a validated custom entry through one canonical path."""
    if isinstance(expansion, str):
        default_expansion = expansion
        parsed_context_expansions = (
            dict(context_expansions) if context_expansions is not None else None
        )
    elif isinstance(expansion, Mapping):
        if context_expansions is not None:
            raise ValueError(
                "provide context expansions either in expansion or context_expansions"
            )
        default_expansion, parsed_context_expansions = _parse_context_expansion_mapping(expansion)
    else:
        raise TypeError("expansion must be a string or context-expansion dictionary")
    return AbbreviationEntry(
        abbreviation=abbreviation,
        expansion=default_expansion,
        context_expansions=parsed_context_expansions,
        case_sensitive=case_sensitive,
        description=description,
        only_if_preceded_by=only_if_preceded_by,
        only_if_followed_by=only_if_followed_by,
        only_if_pos=only_if_pos,
        not_if_pos=not_if_pos,
        case_policy=case_policy,
        speech_strategy=speech_strategy,
        spoken_form=spoken_form,
        aliases=aliases,
        origin="custom",
    )

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

    return _guards_match(
        text,
        start,
        end,
        preceding_pattern=entry._preceding_pattern,
        following_pattern=entry._following_pattern,
        only_if_pos=entry.only_if_pos,
        not_if_pos=entry.not_if_pos,
        preceding_window=preceding_window,
        annotations=annotations,
    )


def _guards_match(
    text: str,
    start: int,
    end: int,
    *,
    preceding_pattern: Pattern[str] | None,
    following_pattern: Pattern[str] | None,
    only_if_pos: Collection[str] | None,
    not_if_pos: Collection[str] | None,
    preceding_window: int = 80,
    annotations: AnnotationIndex | Iterable[TokenAnnotation] | None = None,
) -> bool:
    """Evaluate compiled structural and POS guards for one source span."""
    if not (0 <= start <= end <= len(text)):
        return False

    if preceding_pattern is not None:
        pattern = preceding_pattern
        if pattern is None:
            return False
        raw_before = text[max(0, start - preceding_window) : start]
        before_variants = (raw_before, raw_before.rstrip(" \t\u00a0\u202f"))
        if not any(
            (match := pattern.search(before)) is not None and match.end() == len(before)
            for before in before_variants
        ):
            return False

    if following_pattern is not None:
        pattern = following_pattern
        # Match a suffix slice rather than passing ``end`` as the regex
        # starting position. This preserves the intended relative meaning of
        # anchors such as ``^\s*\d`` for candidates after preceding text.
        if pattern is None or not pattern.match(text[end:]):
            return False

    if annotations is not None and (only_if_pos or not_if_pos):
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
        if not_if_pos and any(pos in not_if_pos for pos in lexical_pos):
            return False
        if only_if_pos and lexical_pos and not any(pos in only_if_pos for pos in lexical_pos):
            return False

    return True


def _is_hyphenated_initial_fragment(text: str, start: int, match_text: str) -> bool:
    """Return whether a one-letter dotted match belongs to an initial chain."""
    if not re.fullmatch(r"[^\W\d_]\.", match_text, re.UNICODE):
        return False
    return (
        start >= 3
        and text[start - 3].isalpha()
        and text[start - 2] == "."
        and text[start - 1] == "-"
    )


def _hyphen_neighbor(text: str, start: int, end: int) -> str | None:
    """Return the non-whitespace segment on the other side of a hyphen."""
    if start > 0 and text[start - 1] == "-":
        index = start - 2
        while index >= 0 and text[index].isalnum():
            index -= 1
        return text[index + 1 : start - 1] or None
    if end < len(text) and text[end] == "-":
        index = end + 1
        while index < len(text) and text[index].isalnum():
            index += 1
        return text[end + 1 : index] or None
    return None


def _is_code_like_hyphen_neighbor(segment: str) -> bool:
    """Return whether a hyphen neighbor has a compact identifier shape."""
    if not segment:
        return True
    if segment[0].isdigit() or len(segment) == 1:
        return True
    if re.fullmatch(r"[A-Z]{1,8}", segment):
        return True
    return any(character.isdigit() for character in segment) and any(
        character.isalpha() for character in segment
    )


def _is_hyphenated_identifier_entry(
    text: str,
    start: int,
    end: int,
    match_text: str,
    entry: AbbreviationEntry | None = None,
) -> bool:
    """Reject uppercase registry entries attached to code-like identifier text."""
    if not re.fullmatch(r"[A-Z]{2,8}", match_text):
        return False
    left = start > 0 and text[start - 1] == "-"
    right = end < len(text) and text[end] == "-"
    if not left and not right:
        return False

    neighbor = _hyphen_neighbor(text, start, end)
    if neighbor is None:
        return True
    if entry is not None and entry.speech_strategy == "spell_source":
        return _is_code_like_hyphen_neighbor(neighbor)
    return True


class ContextDetector:
    """Compatibility wrapper around the language-specific context profile."""

    def __init__(self, language: str = "en") -> None:
        """Initialize the detector for *language*."""
        self.profile = profile_for(language)

    def detect_context(self, abbreviation: str, before: str, after: str) -> AbbreviationContext:
        """Return the context selected by the configured language profile."""
        return self.profile.detect_context(abbreviation, before, after)


class AbbreviationExpander(ABC):
    """Abstract base class for language-specific abbreviation expanders."""

    def __init__(
        self,
        enable_context_detection: bool = True,
        *,
        initialism_mode: InitialismMode = "dotted_only",
        initialism_case: InitialismCase = "source",
        registered_initialism_mode: RegisteredInitialismMode = "expand",
    ) -> None:
        """Initialize the abbreviation expander.

        Args:
            enable_context_detection: Whether to use context-aware expansion
        """
        self.entries: dict[str, AbbreviationEntry] = {}
        language = getattr(self, "UNIT_LANGUAGE", "en")
        self.unit_entries = unit_entries(language)
        self._unit_symbols = unit_symbols(language)
        self._unit_by_symbol = {
            symbol: entry for entry in self.unit_entries for symbol in entry.symbols
        }
        self._unit_by_canonical_id = {
            entry.canonical_id: entry
            for entry in self.unit_entries
            if entry.canonical_id is not None
        }
        self._unit_overrides: dict[str, UnitEntry] = {}
        self._suppressed_units: set[str] = set()
        self.enable_context_detection = enable_context_detection
        self.initialism_policy = InitialismPolicy(
            mode=initialism_mode,
            case=initialism_case,
            registered_mode=registered_initialism_mode,
        )
        self.context_detector = ContextDetector(language) if enable_context_detection else None
        self._initialize_abbreviations()

    @abstractmethod
    def _initialize_abbreviations(self) -> None:
        """Initialize language-specific abbreviations.

        Subclasses must implement this to populate self.entries.
        """

    def _prepare_entry(self, entry: AbbreviationEntry) -> AbbreviationEntry:
        """Validate and apply unit-overlap policy without mutating the registry."""
        if not isinstance(entry, AbbreviationEntry):
            raise TypeError("entry must be an AbbreviationEntry")
        unit_entry = self._unit_by_symbol.get(entry.abbreviation)
        if unit_entry is not None and entry.origin == "custom":
            raise ValueError(
                f"{entry.abbreviation!r} is a unit symbol; use set_unit() for unit customization"
            )
        if (
            unit_entry is not None
            and unit_entry.category != "magnitude"
            and not unit_entry.allow_lexical_overlap
        ):
            return replace(
                entry,
                case_sensitive=True,
                only_if_preceded_by=entry.only_if_preceded_by or NUMBER_BEFORE_UNIT,
            )
        return entry

    def add_abbreviation(self, entry: AbbreviationEntry) -> None:
        """Add or replace an abbreviation entry."""
        prepared = self._prepare_entry(entry)
        key = normalize_entry_key(prepared.abbreviation, case_sensitive=prepared.case_sensitive)
        self.entries[key] = prepared

    def add(
        self,
        abbreviation: str,
        expansion: str | Mapping[str, str],
        *,
        context_expansions: Mapping[AbbreviationContext, str] | None = None,
        case_sensitive: bool = False,
        description: str = "",
        only_if_preceded_by: str | Pattern[str] | None = None,
        only_if_followed_by: str | Pattern[str] | None = None,
        only_if_pos: PosConstraints = None,
        not_if_pos: PosConstraints = None,
        case_policy: CasePolicy = "fixed",
        speech_strategy: SpeechStrategy = "expand",
        spoken_form: str | None = None,
        aliases: tuple[str, ...] = (),
    ) -> None:
        """Build and register a custom abbreviation entry."""
        self.add_abbreviation(
            _build_custom_abbreviation_entry(
                abbreviation,
                expansion,
                context_expansions=context_expansions,
                case_sensitive=case_sensitive,
                description=description,
                only_if_preceded_by=only_if_preceded_by,
                only_if_followed_by=only_if_followed_by,
                only_if_pos=only_if_pos,
                not_if_pos=not_if_pos,
                case_policy=case_policy,
                speech_strategy=speech_strategy,
                spoken_form=spoken_form,
                aliases=aliases,
            )
        )

    def add_custom_abbreviation(
        self,
        abbreviation: str,
        expansion: str | Mapping[str, str],
        description: str = "",
        case_sensitive: bool = False,
        only_if_preceded_by: str | Pattern[str] | None = None,
        only_if_followed_by: str | Pattern[str] | None = None,
        only_if_pos: PosConstraints = None,
        not_if_pos: PosConstraints = None,
        case_policy: CasePolicy = "fixed",
        speech_strategy: SpeechStrategy = "expand",
        spoken_form: str | None = None,
        aliases: tuple[str, ...] = (),
    ) -> None:
        """Add or replace an entry using string-named context expansions."""
        self.add(
            abbreviation,
            expansion,
            description=description,
            case_sensitive=case_sensitive,
            only_if_preceded_by=only_if_preceded_by,
            only_if_followed_by=only_if_followed_by,
            only_if_pos=only_if_pos,
            not_if_pos=not_if_pos,
            case_policy=case_policy,
            speech_strategy=speech_strategy,
            spoken_form=spoken_form,
            aliases=aliases,
        )

    def add_many(
        self,
        entries: Iterable[AbbreviationEntry],
        *,
        on_conflict: BulkConflictPolicy = "error",
    ) -> BulkAddResult:
        """Atomically register a batch of abbreviation entries."""
        if on_conflict not in {"error", "replace"}:
            raise ValueError("on_conflict must be 'error' or 'replace'")
        prepared = tuple(self._prepare_entry(entry) for entry in entries)
        conflicts = _find_bulk_conflicts(prepared, tuple(self.entries.values()))
        if conflicts and on_conflict == "error":
            raise AbbreviationConflictError(conflicts)
        working = dict(self.entries)
        working_index = _spelling_index(tuple(working.values()))
        replaced: list[str] = []
        incoming_names: list[str] = []
        initial_entries = tuple(self.entries.values())
        for entry in prepared:
            collisions = _indexed_colliding_entries(entry, working_index)
            for existing in collisions:
                key = normalize_entry_key(
                    existing.abbreviation, case_sensitive=existing.case_sensitive
                )
                working.pop(key, None)
                _remove_from_spelling_index(existing, working_index)
                if existing in initial_entries and existing.abbreviation not in replaced:
                    replaced.append(existing.abbreviation)
            key = normalize_entry_key(entry.abbreviation, case_sensitive=entry.case_sensitive)
            working[key] = entry
            _add_to_spelling_index(entry, working_index)
            if entry.abbreviation not in incoming_names:
                incoming_names.append(entry.abbreviation)
        self.entries = working
        return BulkAddResult(
            added=len(incoming_names),
            replaced=len(replaced),
            entries=tuple(incoming_names),
            replacements=tuple(replaced),
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
            unit_entry = self._unit_by_symbol.get(symbol)
            canonical_id = unit_entry.canonical_id if unit_entry is not None else None
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

    def iter_initialism_diagnostics(
        self,
        text: str,
        *,
        protected_spans: Iterable[
            ProtectedSpan | tuple[int, int] | tuple[int, int, str | None]
        ] = (),
    ) -> Iterator[InitialismDiagnostic]:
        """Yield initialism decisions using this expander's registry and policy."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        spans = _normalize_protected_spans(text, protected_spans)
        language = getattr(self, "UNIT_LANGUAGE", "en")
        return _iter_initialism_diagnostics(
            text,
            language=language,
            mode=self.initialism_policy.mode,
            registered_mode=self.initialism_policy.registered_mode,
            protected_spans=((span.start, span.end) for span in spans),
            registered_entries=self.entries.values(),
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
        key = normalize_entry_key(abbreviation, case_sensitive=case_sensitive)
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
        key = normalize_entry_key(abbreviation, case_sensitive=case_sensitive)
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
        key = normalize_entry_key(abbreviation, case_sensitive=case_sensitive)
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
        """Expand text and return the immutable source-aligned accepted-edit plan.

        Offsets refer to the original input. Returned records are ordered,
        non-overlapping, expose exact matched source text, and reconstruct
        ``result.text`` when applied right-to-left.
        """
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
        language = getattr(self, "UNIT_LANGUAGE", "en")
        entries = tuple(self.entries.values())
        unit_overrides = dict(self._unit_overrides)
        suppressed_units = frozenset(self._suppressed_units)
        candidates: list[Replacement] = list(
            iter_unit_replacements(
                text,
                getattr(self, "UNIT_LANGUAGE", "en"),
                unit_overrides,
                suppressed_units,
            )
        )
        candidates = [
            candidate for candidate in candidates if not _overlaps_spans(candidate, spans)
        ]

        candidates.extend(
            candidate
            for candidate in iter_initialism_replacements(
                text,
                mode=self.initialism_policy.mode,
                case=self.initialism_policy.case,
                language=language,
                protected_spans=((span.start, span.end) for span in spans),
                registered_entries=entries,
            )
            if not _overlaps_spans(candidate, spans)
        )

        # Process all abbreviations against the original source. The resolver
        # preserves longest-first behavior while giving reviewed units priority.
        for entry in entries:
            unit_entry = self._unit_by_symbol.get(entry.abbreviation)
            if (
                unit_entry is not None
                and unit_entry.category != "magnitude"
                and not unit_entry.allow_lexical_overlap
            ):
                continue
            candidates.extend(
                candidate
                for candidate in self._iter_entry_replacements(text, entry, annotation_index)
                if not _overlaps_spans(candidate, spans)
            )

        selected = resolve_replacements(candidates)
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
                    abbreviation=item.abbreviation,
                    rule=item.entry_id or item.source,
                    priority=item.priority,
                    context=item.context if isinstance(item.context, AbbreviationContext) else None,
                    matched_text=text[item.start : item.end],
                    canonical_id=item.canonical_id,
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

                if _is_hyphenated_initial_fragment(text, start, match.group()):
                    continue

                if _is_hyphenated_identifier_entry(text, start, end, match.group(), entry):
                    continue

                if not abbreviation_guards_match(
                    entry,
                    text,
                    start,
                    end,
                    annotations=annotation_index,
                ):
                    continue

                variant = next(
                    (
                        candidate
                        for candidate in entry.variants
                        if _guards_match(
                            text,
                            start,
                            end,
                            preceding_pattern=candidate._preceding_pattern,
                            following_pattern=candidate._following_pattern,
                            only_if_pos=candidate.only_if_pos,
                            not_if_pos=candidate.not_if_pos,
                            annotations=annotation_index,
                        )
                    ),
                    None,
                )
                if variant is not None:
                    expansion = variant.expansion
                    context = None
                elif not self.enable_context_detection or not self.context_detector:
                    expansion = entry.expansion
                    context = None
                else:
                    # Get surrounding context from the original source.
                    window = 96
                    before = text[max(0, start - window) : start].rstrip()
                    after = text[end : min(len(text), end + window)].lstrip()
                    context = self.context_detector.detect_context(match.group(), before, after)
                    expansion = entry.get_expansion(context)

                if entry.speech_strategy == "custom":
                    assert entry.spoken_form is not None
                    expansion = entry.spoken_form
                else:
                    expansion = _apply_case_policy(
                        expansion,
                        entry.case_policy,
                        sentence_start=_is_sentence_start(text, start),
                    )
                    if (
                        self.initialism_policy.registered_mode == "spell"
                        and entry.speech_strategy == "spell_source"
                    ):
                        expansion = render_initialism_source(
                            match.group(), case=self.initialism_policy.case
                        )
                if entry.preserve_sentence_final_period and should_preserve_sentence_final_period(
                    text, end, match.group(), expansion
                ):
                    expansion += "."

                yield Replacement(
                    start=start,
                    end=end,
                    text=expansion,
                    priority=_entry_priority(entry),
                    source=f"abbr:{entry.abbreviation}",
                    kind="abbreviation",
                    entry_id=f"abbr:{entry.abbreviation}",
                    context=context,
                    abbreviation=entry.abbreviation,
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

def _spellings_collide(
    left: AbbreviationEntry,
    left_spelling: str,
    right: AbbreviationEntry,
    right_spelling: str,
) -> bool:
    if left.case_sensitive and right.case_sensitive:
        return left_spelling == right_spelling
    return left_spelling.casefold() == right_spelling.casefold()


def _collision_key(
    left: AbbreviationEntry,
    left_spelling: str,
    right: AbbreviationEntry,
    right_spelling: str,
) -> str:
    if left.case_sensitive and right.case_sensitive:
        return left_spelling
    return left_spelling.casefold()


def _entry_spellings(entry: AbbreviationEntry) -> tuple[str, ...]:
    return (entry.abbreviation, *entry.aliases)


def _colliding_entries(
    incoming: AbbreviationEntry,
    existing_entries: tuple[AbbreviationEntry, ...],
) -> tuple[AbbreviationEntry, ...]:
    return tuple(
        existing
        for existing in existing_entries
        if any(
            _spellings_collide(incoming, left, existing, right)
            for left in _entry_spellings(incoming)
            for right in _entry_spellings(existing)
        )
    )


def _add_to_spelling_index(
    entry: AbbreviationEntry,
    index: dict[str, list[tuple[AbbreviationEntry, int, str]]],
) -> None:
    for spelling_index, spelling in enumerate(_entry_spellings(entry)):
        index.setdefault(spelling.casefold(), []).append((entry, spelling_index, spelling))


def _remove_from_spelling_index(
    entry: AbbreviationEntry,
    index: dict[str, list[tuple[AbbreviationEntry, int, str]]],
) -> None:
    for spelling in _entry_spellings(entry):
        key = spelling.casefold()
        index[key] = [candidate for candidate in index[key] if candidate[0] is not entry]
        if not index[key]:
            del index[key]


def _indexed_colliding_entries(
    incoming: AbbreviationEntry,
    index: dict[str, list[tuple[AbbreviationEntry, int, str]]],
) -> tuple[AbbreviationEntry, ...]:
    collisions: list[AbbreviationEntry] = []
    seen: set[int] = set()
    for left in _entry_spellings(incoming):
        for existing, _, right in index.get(left.casefold(), ()):
            if id(existing) not in seen and _spellings_collide(incoming, left, existing, right):
                seen.add(id(existing))
                collisions.append(existing)
    return tuple(collisions)


def _spelling_index(
    entries: Iterable[AbbreviationEntry],
) -> dict[str, list[tuple[AbbreviationEntry, int, str]]]:
    index: dict[str, list[tuple[AbbreviationEntry, int, str]]] = {}
    for entry in entries:
        for spelling_index, spelling in enumerate(_entry_spellings(entry)):
            index.setdefault(spelling.casefold(), []).append((entry, spelling_index, spelling))
    return index


def _find_bulk_conflicts(
    incoming_entries: tuple[AbbreviationEntry, ...],
    existing_entries: tuple[AbbreviationEntry, ...],
) -> tuple[AbbreviationConflict, ...]:
    conflicts: list[AbbreviationConflict] = []
    existing_index = _spelling_index(existing_entries)
    previous_index: dict[str, list[tuple[AbbreviationEntry, int, str]]] = {}
    for incoming in incoming_entries:
        for left_index, left in enumerate(_entry_spellings(incoming)):
            candidates = (*existing_index.get(left.casefold(), ()), *previous_index.get(left.casefold(), ()))
            for previous, right_index, right in candidates:
                if not _spellings_collide(incoming, left, previous, right):
                    continue
                canonical = left_index == 0 and right_index == 0
                kind: AbbreviationConflictKind = "canonical_collision" if canonical else "alias_collision"
                if previous in incoming_entries and canonical:
                    kind = "duplicate"
                conflicts.append(
                    AbbreviationConflict(
                        _collision_key(incoming, left, previous, right),
                        incoming.abbreviation,
                        previous.abbreviation,
                        kind,
                    )
                )
        for spelling_index, spelling in enumerate(_entry_spellings(incoming)):
            previous_index.setdefault(spelling.casefold(), []).append(
                (incoming, spelling_index, spelling)
            )
    return tuple(conflicts)



def _entry_priority(entry: AbbreviationEntry) -> int:
    """Return the documented deterministic precedence for abbreviation entries."""
    if entry.origin == "custom":
        return 220 if entry.case_sensitive else 120
    return 210 if entry.case_sensitive else 110


def _is_sentence_start(text: str, start: int) -> bool:
    """Return whether *start* begins a sentence-level lexical phrase."""
    prefix = text[:start]
    index = len(prefix) - 1
    while index >= 0 and prefix[index].isspace():
        index -= 1
    if index < 0:
        return True

    # An opening quote or bracket may wrap a phrase immediately following a
    # sentence boundary. Do not treat a colon as a sentence boundary here.
    opening = frozenset("\"'“‘«([{")
    if prefix[index] in opening:
        index -= 1
        while index >= 0 and prefix[index].isspace():
            index -= 1
    return index < 0 or prefix[index] in ".!?。！？"


def _apply_case_policy(
    expansion: str,
    policy: Literal["fixed", "sentence"],
    *,
    sentence_start: bool,
) -> str:
    """Apply an entry's opt-in sentence casing to the selected expansion."""
    if policy == "fixed" or not sentence_start:
        return expansion
    for index, character in enumerate(expansion):
        if character.lower() != character.upper():
            return expansion[:index] + character.upper() + expansion[index + 1 :]
    return expansion


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
