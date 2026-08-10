from ..unit_data.common import locale_currency, register_locale_units
from ._locales import SpanishColombiaAbbreviationExpander

register_locale_units("es_CO", "es", (locale_currency("COP", "peso colombiano", "currency-colombian-peso"),))


def get_expander(enable_context_detection: bool = True) -> SpanishColombiaAbbreviationExpander:
    return SpanishColombiaAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
