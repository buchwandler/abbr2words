from __future__ import annotations

import pytest

from abbr2words import abbr2words, get_expander


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("E.D.", "E D."),
        ("J.H.", "J H."),
        ("C.W.", "C W."),
        ("G.R.", "G R."),
        ("F.C.S.C.J.", "F C S C J."),
        ("Cope, E.D. 1862.", "Cope, E D 1862."),
        ("Connell, J.H. 1978.", "Connell, J H 1978."),
        ("Mason, C.W. (1911).", "Mason, C W (1911)."),
        ("Rumsiene, G.R.; Rumsas (2014).", "Rumsiene, G R; Rumsas (2014)."),
    ],
)
def test_generic_dotted_initialisms_expand_source_graphemes(source: str, expected: str) -> None:
    assert abbr2words(source, lang="en") == expected


@pytest.mark.parametrize(
    "source",
    ["fooE.D.", "E.D.foo", "1.2.3", "v1.2.3", "example.com"],
)
def test_generic_initialism_fallback_is_bounded(source: str) -> None:
    assert abbr2words(source, lang="en") == source


def test_initialism_fallback_preserves_sentence_punctuation_and_source_offsets() -> None:
    source = "He signed J.H."
    result = get_expander("en").expand_with_replacements(source)
    assert result.text == "He signed J H."
    assert [(item.start, item.end, item.text, item.priority) for item in result.replacements] == [
        (10, 14, "J H.", 50)
    ]


def test_registered_entries_outrank_generic_initialism_fallback() -> None:
    result = get_expander("en").expand_with_replacements("e.g. E.G. U.S. M.S.")
    assert result.text == "for example E G U S M S."
    assert [item.source for item in result.replacements] == [
        "abbr:e.g.",
        "abbr:initialism",
        "abbr:U.S.",
        "abbr:M.S.",
    ]
    assert result.replacements[0].priority > result.replacements[1].priority


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("See, e.g., Appendix A.", "See, for example, Appendix A."),
        ("Gibson, E.G. (1973).", "Gibson, E G (1973)."),
        ("E.G. Archer", "E G Archer"),
        ("Show your I.D.", "Show your I D."),
        ("Cresswell, I.D. (1995).", "Cresswell, I D (1995)."),
    ],
)
def test_english_case_split_and_i_d_policy(source: str, expected: str) -> None:
    assert abbr2words(source, lang="en") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("123 S. Main St.", "123 South Main Street."),
        ("500 W. 42nd St.", "500 West 42nd Street."),
        ("George S. Blanchard", "George S Blanchard"),
        ("Lawrence S. Wittner", "Lawrence S Wittner"),
        ("Tom W. Young", "Tom W Young"),
        ("S. aureus", "S. aureus"),
        ("N. meningitidis", "N. meningitidis"),
    ],
)
def test_compass_context_is_positive_and_biological_names_are_protected(
    source: str, expected: str
) -> None:
    assert abbr2words(source, lang="en") == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Washington, D.C.", "Washington, District of Columbia."),
        ("Metz, D.C.; Jensen, R.T.", "Metz, D C; Jensen, R T."),
        ("Levine, L.A. (2006).", "Levine, L A (2006)."),
    ],
)
def test_geographic_abbreviations_are_conservative(source: str, expected: str) -> None:
    assert abbr2words(source, lang="en") == expected
