from __future__ import annotations

from abbr2words import AbbreviationContext, AbbreviationEntry, get_expander


def test_generic_date_context_uses_bounded_numeric_evidence() -> None:
    expander = get_expander("en")
    expander.add_abbreviation(
        AbbreviationEntry(
            abbreviation="X.",
            expansion="default form",
            context_expansions={AbbreviationContext.DATE: "date form"},
        )
    )
    assert expander.expand("5 X. 2026") == "5 date form 2026"
    assert expander.expand("X. is a lexical word") == "default form is a lexical word"


def test_date_context_accepts_unicode_horizontal_spaces() -> None:
    expander = get_expander("de")
    expander.add_abbreviation(
        AbbreviationEntry(
            abbreviation="X.",
            expansion="normal",
            context_expansions={AbbreviationContext.DATE: "datum"},
        )
    )
    assert expander.expand("5\u202fX.\u00a02026") == "5\u202fdatum\u00a02026"


def test_context_names_report_all_enum_values() -> None:
    expander = get_expander("en")
    try:
        expander.add_custom_abbreviation("X.", {"unknown": "value"})
    except ValueError as exc:
        message = str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("unknown context was accepted")
    assert "date" in message
