from ..unit_data.common import locale_currency, register_locale_units
from ._locales import SpanishNicaraguaAbbreviationExpander

register_locale_units("es_NI", "es", (locale_currency("C$", "córdoba nicaragüense", "currency-nicaraguan-cordoba"),))


def get_expander(enable_context_detection: bool = True) -> SpanishNicaraguaAbbreviationExpander:
    return SpanishNicaraguaAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
