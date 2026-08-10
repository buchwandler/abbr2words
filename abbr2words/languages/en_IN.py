from ..unit_data.common import locale_currency, register_locale_units
from ._locales import EnglishIndiaAbbreviationExpander

register_locale_units("en_IN", "en", (locale_currency("₹", "Indian rupee", "currency-indian-rupee"),))


def get_expander(enable_context_detection: bool = True) -> EnglishIndiaAbbreviationExpander:
    return EnglishIndiaAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
