from ..unit_data.common import locale_currency, register_locale_units
from ._locales import SpanishGuatemalaAbbreviationExpander

register_locale_units("es_GT", "es", (locale_currency("Q", "quetzal", "currency-guatemalan-quetzal"),))


def get_expander(enable_context_detection: bool = True) -> SpanishGuatemalaAbbreviationExpander:
    return SpanishGuatemalaAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
