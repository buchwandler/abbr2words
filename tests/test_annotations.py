from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from abbr2words import (
    Expander,
    TokenAnnotation,
    abbr2words,
    abbr2words_with_replacements,
    abbreviation_guards_match,
)
from abbr2words.annotations import AnnotationIndex, normalize_annotations
from abbr2words.core import AbbreviationEntry


def test_annotations_are_optional() -> None:
    assert abbr2words("Dr. Smith", lang="en") == "Doctor Smith"


def test_token_annotation_is_immutable_and_public() -> None:
    annotation = TokenAnnotation(0, 2, "noun", "NN")
    assert annotation.pos == "noun"
    with pytest.raises(AttributeError):
        annotation.pos = "VERB"  # type: ignore[misc]


def test_annotation_offsets_must_be_valid() -> None:
    with pytest.raises(ValueError, match="annotation 0"):
        abbr2words(
            "text",
            lang="en",
            annotations=[TokenAnnotation(-1, 2, "NOUN")],
        )


def test_annotation_spans_must_not_overlap() -> None:
    annotations = [
        TokenAnnotation(0, 3, "NOUN"),
        TokenAnnotation(2, 4, "NOUN"),
    ]
    with pytest.raises(ValueError, match="overlap"):
        abbr2words("test", lang="en", annotations=annotations)


def test_pos_labels_are_normalized_and_sorted_without_mutating_input() -> None:
    source = [TokenAnnotation(2, 4, " adp ", " xx "), TokenAnnotation(0, 1, "noun", "")]
    normalized = normalize_annotations("abcd", source)
    assert normalized == (
        TokenAnnotation(0, 1, "NOUN", None),
        TokenAnnotation(2, 4, "ADP", "XX"),
    )
    assert source[0].pos == " adp "


def test_annotation_index_returns_overlapping_and_neighboring_tokens() -> None:
    annotations = normalize_annotations(
        "A Ref.",
        [
            TokenAnnotation(0, 1, "DET"),
            TokenAnnotation(2, 5, "NOUN"),
            TokenAnnotation(5, 6, "PUNCT"),
        ],
    )
    index = AnnotationIndex(annotations)
    assert index.overlapping(2, 6) == annotations[1:]
    assert index.before(5) == (annotations[1],)
    assert index.after(2, limit=2) == annotations[1:]


def test_pos_allow_and_deny_guards_are_opt_in() -> None:
    expander = Expander("en")
    expander.add("Ref.", "Reference", only_if_pos={"NOUN"})
    assert expander.expand("Ref.") == "Reference."
    assert expander.expand("Ref.", annotations=[TokenAnnotation(0, 4, "ADV")]) == "Ref."
    assert expander.expand("Ref.", annotations=[TokenAnnotation(0, 4, "NOUN")]) == "Reference."

    expander.add("Code.", "Code", not_if_pos={"PROPN"})
    assert expander.expand("Code.", annotations=[TokenAnnotation(0, 5, "PROPN")]) == "Code."
    assert expander.expand("Code.", annotations=[TokenAnnotation(0, 5, "NOUN")]) == "Code."


def test_single_string_pos_constraint_is_one_normalized_label() -> None:
    expander = Expander("en")
    expander.add("ZZ.", "Zed", only_if_pos="noun")

    entry = expander._impl.get_abbreviation("ZZ.")
    assert entry is not None
    assert entry.only_if_pos == frozenset({"NOUN"})
    assert expander.expand("ZZ.", annotations=[TokenAnnotation(0, 3, "NOUN")]) == "Zed."

    expander.add("YY.", "Why", not_if_pos="adp")
    denied = [TokenAnnotation(0, 3, "ADP")]
    allowed = [TokenAnnotation(0, 3, "NOUN")]
    assert expander.expand("YY.", annotations=denied) == "YY."
    assert expander.expand("YY.", annotations=allowed) == "Why."


def test_public_guard_helper_normalizes_annotations() -> None:
    entry = AbbreviationEntry("Ref.", "Reference", only_if_pos="NOUN")
    assert abbreviation_guards_match(
        entry,
        "Ref.",
        0,
        4,
        annotations=[TokenAnnotation(0, 4, " noun ")],
    )


def test_public_guard_helper_validates_annotations_like_expansion() -> None:
    entry = AbbreviationEntry("Ref.", "Reference", only_if_pos="NOUN")
    with pytest.raises(ValueError, match="annotation 0"):
        abbreviation_guards_match(
            entry,
            "Ref.",
            0,
            4,
            annotations=[TokenAnnotation(-1, 4, "NOUN")],
        )
    with pytest.raises(ValueError, match="overlap"):
        abbreviation_guards_match(
            entry,
            "Ref.",
            0,
            4,
            annotations=[
                TokenAnnotation(0, 3, "NOUN"),
                TokenAnnotation(2, 4, "NOUN"),
            ],
        )


def test_punctuation_and_missing_pos_do_not_veto_allow_guard() -> None:
    expander = Expander("en")
    expander.add("Ref.", "Reference", only_if_pos={"NOUN"})
    assert (
        expander.expand(
            "Ref.",
            annotations=[TokenAnnotation(0, 3, "NOUN"), TokenAnnotation(3, 4, "PUNCT")],
        )
        == "Reference."
    )
    assert expander.expand("Ref.", annotations=[TokenAnnotation(0, 4)]) == "Reference."


def test_pos_annotations_use_original_offsets_after_an_earlier_replacement() -> None:
    expander = Expander("en")
    expander.add("A.", "Alpha")
    expander.add("Ref.", "Reference", only_if_pos={"NOUN"})
    text = "A. Ref. 8"
    annotations = [
        TokenAnnotation(0, 2, "PROPN"),
        TokenAnnotation(3, 7, "NOUN"),
        TokenAnnotation(8, 9, "NUM"),
    ]
    assert expander.expand(text, annotations=annotations) == "Alpha Reference 8"


def test_compound_alias_replacement_preserves_original_source_span() -> None:
    source = "Tel.Nr. 12"
    result = abbr2words_with_replacements(source, lang="de")
    assert result.text == "Telefonnummer 12"
    assert len(result.replacements) == 1
    replacement = result.replacements[0]
    assert source[replacement.start : replacement.end] == "Tel.Nr."
    assert replacement.abbreviation == "Tel. Nr."


@pytest.mark.parametrize(
    "source",
    ("They wandered around in.", "He looked around in.", "Log in."),
)
def test_sentence_final_in_is_not_an_inch(source: str) -> None:
    assert abbr2words(source, lang="en") == source


def test_sentence_final_in_stays_unchanged_with_pos_annotations() -> None:
    text = "They wandered around in."
    annotations = [
        TokenAnnotation(0, 4, "PRON"),
        TokenAnnotation(5, 13, "VERB"),
        TokenAnnotation(14, 20, "ADV"),
        TokenAnnotation(21, 23, "ADP"),
        TokenAnnotation(23, 24, "PUNCT"),
    ]
    assert abbr2words(text, lang="en", annotations=annotations) == text


def test_numeric_inch_expands_even_when_general_tagger_marks_in_as_adp() -> None:
    text = "The board is 10 in. wide."
    annotations = [
        TokenAnnotation(0, 3, "DET"),
        TokenAnnotation(4, 9, "NOUN"),
        TokenAnnotation(10, 12, "AUX"),
        TokenAnnotation(13, 15, "NUM"),
        TokenAnnotation(16, 18, "ADP"),
        TokenAnnotation(18, 19, "PUNCT"),
        TokenAnnotation(20, 24, "ADJ"),
        TokenAnnotation(24, 25, "PUNCT"),
    ]
    assert abbr2words(text, lang="en", annotations=annotations) == "The board is 10 inch wide."


@pytest.mark.parametrize(
    ("source", "expected"),
    (
        ("10 in.", "10 inch"),
        ("10in.", "10 inch"),
        ("A10 in.", "A10 in."),
        ("The board is ten in. wide.", "The board is ten in. wide."),
    ),
)
def test_numeric_inch_matrix(source: str, expected: str) -> None:
    assert abbr2words(source, lang="en") == expected


@dataclass
class FakeToken:
    text: str
    idx: int
    pos_: str
    tag_: str

    def __len__(self) -> int:
        return len(self.text)


def test_spacy_example_import_is_lazy() -> None:
    import examples.spacy_pos as example

    tokens = [FakeToken("Ref.", 0, "NOUN", "NN")]
    annotations = example.to_token_annotations(tokens)
    assert abbr2words("Ref.", annotations=annotations) == "reference."
    assert example.main is not None
    if "spacy" not in sys.modules:
        assert "spacy" not in sys.modules


def test_package_has_no_spacy_dependency_or_import() -> None:
    root = Path(__file__).parents[1]
    package_sources = tuple((root / "abbr2words").rglob("*.py"))
    assert all("import spacy" not in path.read_text(encoding="utf-8") for path in package_sources)
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert "dependencies = []" in pyproject
    assert "spacy" not in pyproject
