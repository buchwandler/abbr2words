from ..unit_data.common import locale_currency, register_locale_units
from ._locales import SpanishMexicoAbbreviationExpander

register_locale_units(
    "es_MX",
    "es",
    (
        locale_currency(("$", "MXN"), "peso mexicano", "currency-mexican-peso"),
        locale_currency(("US$", "USD"), "dólar estadounidense", "currency-us-dollar"),
    ),
)


def get_expander(enable_context_detection: bool = True) -> SpanishMexicoAbbreviationExpander:
    return SpanishMexicoAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
