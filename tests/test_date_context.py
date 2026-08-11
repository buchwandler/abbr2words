from __future__ import annotations

from abbr2words import AbbreviationContext, AbbreviationEntry, abbr2words, get_expander


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


def test_italian_month_and_title_contexts_use_one_canonical_entry() -> None:
    assert abbr2words("12 gen. 2024", lang="it") == "12 gennaio 2024"
    assert abbr2words("Gen. Rossi", lang="it") == "Generale Rossi"
    assert abbr2words("5 mag. 2024", lang="it") == "5 maggio 2024"
    assert abbr2words("Dott. Mag. Bianchi", lang="it") == "Dottor magistrato Bianchi"

    expander = get_expander("it")
    assert expander.get_abbreviation("gen.").context_expansions
    assert expander.get_abbreviation("mag.").context_expansions
