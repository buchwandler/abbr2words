from __future__ import annotations

import pytest

from abbr2words import (
    AbbreviationConflictError,
    AbbreviationEntry,
    Expander,
    get_expander,
)


def entry(abbreviation: str, expansion: str, **kwargs: object) -> AbbreviationEntry:
    return AbbreviationEntry(abbreviation, expansion, origin="custom", **kwargs)  # type: ignore[arg-type]


def test_add_many_registers_entries_atomically_and_returns_summary() -> None:
    expander = get_expander("en", registered_initialism_mode="spell")
    result = expander.add_many(
        (
            entry("AAR", "after-action review"),
            entry("AO", "area of operations", speech_strategy="spell_source"),
            entry("AAA", "anti-aircraft artillery", speech_strategy="custom", spoken_form="Triple A"),
        )
    )

    assert result.added == 3
    assert result.replaced == 0
    assert result.entries == ("AAR", "AO", "AAA")
    assert result.replacements == ()
    assert expander.expand("AAR AO AAA") == "after-action review A O Triple A"


def test_add_many_validation_failure_does_not_mutate_registry() -> None:
    expander = get_expander("en")
    batch = (entry("BULK-ONE", "one"), object(), entry("BULK-TWO", "two"))

    with pytest.raises(TypeError, match="entry must be an AbbreviationEntry"):
        expander.add_many(batch)  # type: ignore[arg-type]

    assert not expander.has_abbreviation("BULK-ONE")
    assert not expander.has_abbreviation("BULK-TWO")


def test_add_many_reports_duplicate_canonical_conflicts_before_mutation() -> None:
    expander = get_expander("en")
    batch = (entry("DUP", "first"), entry("DUP", "second"))

    with pytest.raises(AbbreviationConflictError) as raised:
        expander.add_many(batch)

    assert len(raised.value.conflicts) == 1
    conflict = raised.value.conflicts[0]
    assert conflict.kind == "duplicate"
    assert conflict.key == "dup"
    assert conflict.incoming_abbreviation == "DUP"
    assert conflict.existing_abbreviation == "DUP"
    assert not expander.has_abbreviation("DUP")


def test_add_many_reports_alias_collisions() -> None:
    expander = get_expander("en")

    with pytest.raises(AbbreviationConflictError) as raised:
        expander.add_many(
            (
                entry("AAR", "review", aliases=("X",)),
                entry("AO", "operations", aliases=("X",)),
            )
        )

    assert any(conflict.kind == "alias_collision" for conflict in raised.value.conflicts)
    assert not expander.has_abbreviation("AAR")
    assert not expander.has_abbreviation("AO")


def test_add_many_detects_canonical_alias_collision() -> None:
    expander = get_expander("en")

    with pytest.raises(AbbreviationConflictError) as raised:
        expander.add_many(
            (
                entry("AAR", "review", aliases=("AO",)),
                entry("AO", "operations"),
            )
        )

    assert any(conflict.kind == "alias_collision" for conflict in raised.value.conflicts)


def test_add_many_replace_is_deterministic_and_reports_replaced_entries() -> None:
    expander = get_expander("en")
    expander.add("REPL", "old")

    result = expander.add_many((entry("REPL", "new"),), on_conflict="replace")

    assert result.added == 1
    assert result.replaced == 1
    assert result.entries == ("REPL",)
    assert result.replacements == ("REPL",)
    assert expander.expand("REPL") == "new"


def test_add_many_isolated_from_other_expanders_and_facade_supports_it() -> None:
    first = get_expander("en")
    second = get_expander("en")
    first.add_many((entry("ISOLATED", "first"),))

    assert first.expand("ISOLATED") == "first"
    assert second.expand("ISOLATED") == "ISOLATED"

    facade = Expander("en")
    result = facade.add_many((entry("FACADE", "facade"),))
    assert result.added == 1
    assert facade.expand("FACADE") == "facade"
