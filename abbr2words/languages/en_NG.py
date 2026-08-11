from ..unit_data.common import locale_currency, register_locale_units
from ._locales import EnglishNigeriaAbbreviationExpander

register_locale_units("en_NG", "en", (locale_currency(("₦", "NGN"), "Nigerian naira", "currency-nigerian-naira"),))


def get_expander(enable_context_detection: bool = True) -> EnglishNigeriaAbbreviationExpander:
    return EnglishNigeriaAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
