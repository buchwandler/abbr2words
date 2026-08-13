from __future__ import annotations

import pytest

from abbr2words import abbr2words


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("mr Doron", "Mister Doron"),
        ("dr Henry", "Doctor Henry"),
        ("dr Ann Williams", "Doctor Ann Williams"),
        ("Mrs Jones", "Missus Jones"),
        ("Ms Smith", "Miss Smith"),
        ("Prof Brown", "Professor Brown"),
        ("vol 6", "volume 6"),
        ("vol 50", "volume 50"),
        ("Tigers vs Yankees", "Tigers versus Yankees"),
        ("Acme Ltd", "Acme limited"),
        ("Acme ltd, Inc.", "Acme limited, incorporated."),
    ],
)
def test_guarded_undotted_english_forms_expand(source: str, expected: str) -> None:
    assert abbr2words(source, lang="en") == expected


@pytest.mark.parametrize(
    "source",
    [
        "dr variable",
        "dr = 5",
        "vol can be a word fragment only",
        "ltd can be a word fragment only",
        "ltd inc",
    ],
)
def test_guarded_undotted_english_forms_leave_non_matching_context_unchanged(
    source: str,
) -> None:
    assert abbr2words(source, lang="en") == source


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("pp. 12", "pages 12"),
        ("pp 12", "pages 12"),
        ("Smith, eds.", "Smith, editors."),
    ],
)
def test_bibliographic_entries_keep_semantic_default_expansion(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="en") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [("pp. 12", "p p 12"), ("pp 12", "p p 12"), ("Smith, eds.", "Smith, e d s.")],
)
def test_bibliographic_entries_can_spell_the_source_form(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="en", registered_initialism_mode="spell") == expected


def test_bibliographic_eds_requires_a_reviewed_context_shape() -> None:
    assert abbr2words("eds. discussed below", lang="en") == "eds. discussed below"
