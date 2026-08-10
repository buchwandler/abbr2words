from ..unit_data.common import locale_currency, register_locale_units
from ._locales import SpanishCostaRicaAbbreviationExpander

register_locale_units("es_CR", "es", (locale_currency("₡", "colón costarricense", "currency-costa-rican-colon"),))


def get_expander(enable_context_detection: bool = True) -> SpanishCostaRicaAbbreviationExpander:
    return SpanishCostaRicaAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
