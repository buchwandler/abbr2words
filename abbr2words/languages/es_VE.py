from ..unit_data.common import locale_currency, register_locale_units
from ._locales import SpanishVenezuelaAbbreviationExpander

register_locale_units("es_VE", "es", (locale_currency("Bs.", "bolívar", "currency-venezuelan-bolivar"),))


def get_expander(enable_context_detection: bool = True) -> SpanishVenezuelaAbbreviationExpander:
    return SpanishVenezuelaAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
