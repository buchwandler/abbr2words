from __future__ import annotations

import pytest

from abbr2words import abbr2words
from examples.abbreviations import TEXT as ENGLISH_TEXT
from examples.german import TEXT as GERMAN_TEXT


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Bring your I.D. card.", "Bring your identification card."),
        ("Reply ASAP.", "Reply as soon as possible."),
        ("15 yrs.", "15 year"),
        ("He studied at MIT.", "He studied at Massachusetts Institute of Technology."),
        ("The CEO spoke.", "The chief executive officer spoke."),
        ("A Q&A session.", "A questions and answers session."),
        ("R.S.V.P. by Friday.", "respond by Friday."),
        ("P.S. Bring a laptop.", "postscript Bring a laptop."),
    ],
)
def test_supplied_english_entries(source: str, expected: str) -> None:
    assert abbr2words(source, lang="en-us") == expected


def test_supplied_english_text_regressions() -> None:
    output = abbr2words(ENGLISH_TEXT, lang="en-us")
    assert "Mister Schmidt" in output
    assert "Doctor Brown" in output
    assert "Saint Patrick's Cathedral" in output
    assert "123 Main Street" in output
    assert "District of Columbia" in output
    assert "U S A" in output
    assert "identification card" in output
    assert "as soon as possible" in output
    assert "15 year" in output
    assert "Massachusetts Institute of Technology" in output
    assert "chief executive officer" in output
    assert "questions and answers" in output
    assert "postscript" in output
    assert "P.South" not in output
    assert "37°circa" not in output
    assert "37 degree Celsius." in output


def test_supplied_german_text_remains_abbreviation_only() -> None:
    output = abbr2words(GERMAN_TEXT, lang="de")
    assert "Professor Klein" in output
    assert "gegebenenfalls" in output
    assert "zirka" in output
    assert "zuzüglich" in output
    assert "14.05.2026" in output
    assert "18:20" in output


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("123 N. Main St.", "123 North Main Street"),
        ("123 S. Main St.", "123 South Main Street"),
        ("123 E. Main St.", "123 East Main Street"),
        ("123 W. Main St.", "123 West Main Street"),
        ("P.S.", "postscript"),
        ("A.B.S.", "A.B.S."),
    ],
)
def test_direction_guards_do_not_rewrite_dotted_initialisms(source: str, expected: str) -> None:
    assert abbr2words(source, lang="en") == expected


def test_celsius_and_circa_are_distinct() -> None:
    assert abbr2words("c. 1995", lang="en") == "circa 1995"
    assert abbr2words("37°C.", lang="en") == "37 degree Celsius."
    assert abbr2words("37 c.", lang="en") == "37 degree Celsius."
    assert abbr2words("The value is C.", lang="en") == "The value is C."
    assert abbr2words("Code P.S. remains readable.", lang="en") == (
        "Code postscript remains readable."
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("123 Main St.", "123 Main Street"),
        ("456 Oak St. is here", "456 Oak Street is here"),
        ("100 N. Elm St.", "100 North Elm Street"),
        ("I live at 5 Park St.", "I live at 5 Park Street"),
        ("The shop on 5th St.", "The shop on 5th Street"),
        ("St. Patrick's Day", "Saint Patrick's Day"),
        ("St. Peter was an apostle", "Saint Peter was an apostle"),
        ("The church of St. John", "The church of Saint John"),
        ("Visit St. Louis", "Visit Saint Louis"),
        ("St. Paul, Minnesota", "Saint Paul, Minnesota"),
        ("123 St. Louis Avenue", "123 Saint Louis Avenue"),
        ("I live on St. Patrick Street", "I live on Saint Patrick Street"),
        ("St. Christopher", "Saint Christopher"),
        ("Visit St.", "Visit Saint"),
        ("Main St. is closed.", "Main Street is closed."),
    ],
)
def test_english_st_compatibility_matrix(source: str, expected: str) -> None:
    assert abbr2words(source, lang="en") == expected
