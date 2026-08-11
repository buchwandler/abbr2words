from __future__ import annotations

import pytest

from abbr2words import get_expander, iter_unit_matches


@pytest.mark.parametrize(
    ("language", "lexical_currency", "quantity", "canonical_id"),
    [
        ("en_IN", "Rs.", "12 Rs.", "currency-indian-rupee"),
        ("en_NG", "₦", "12 ₦", "currency-nigerian-naira"),
        ("es_CO", "COP", "12 COP", "currency-colombian-peso"),
        ("es_CR", "₡", "12 ₡", "currency-costa-rican-colon"),
        ("es_GT", "Q.", "12 Q.", "currency-guatemalan-quetzal"),
        ("es_NI", "C$", "12 C$", "currency-nicaraguan-cordoba"),
        ("es_VE", "Bs.", "12 Bs.", "currency-venezuelan-bolivar"),
        ("es_MX", "$", "$500", "currency-mexican-peso"),
        ("zh_CN", "人民币", "12 人民币", "currency-chinese-yuan"),
        ("zh_HK", "港元", "12 港元", "currency-hong-kong-dollar"),
        ("zh_TW", "新台幣", "12 新台幣", "currency-new-taiwan-dollar"),
    ],
)
def test_locale_currencies_are_structured_numeric_entries(
    language: str, lexical_currency: str, quantity: str, canonical_id: str
) -> None:
    expander = get_expander(language)
    assert not expander.has_abbreviation(lexical_currency, case_sensitive=True)
    matches = tuple(iter_unit_matches(quantity, language))
    assert matches
    assert matches[0].canonical_id == canonical_id


def test_mexican_dollar_overlay_preserves_explicit_us_dollar_forms() -> None:
    assert tuple(iter_unit_matches("$500", "es"))[0].canonical_id == "currency-us-dollar"
    assert tuple(iter_unit_matches("$500", "es_MX"))[0].canonical_id == "currency-mexican-peso"
    assert tuple(iter_unit_matches("US$25.99", "es_MX"))[0].canonical_id == (
        "currency-us-dollar"
    )
    assert tuple(iter_unit_matches("USD 25.99", "es_MX"))[0].canonical_id == (
        "currency-us-dollar"
    )


def test_us_and_gb_overlays_inherit_the_base_english_registry() -> None:
    base = get_expander("en")
    for locale in ("en_US", "en_GB"):
        overlay = get_expander(locale)
        assert overlay.entries.keys() == base.entries.keys()
        assert len(tuple(iter_unit_matches("60 mph", locale))) == 1
