from ..unit_data.common import locale_currency, register_locale_units
from ._locales import ChineseTaiwanAbbreviationExpander

register_locale_units("zh_TW", "zh", (locale_currency(("NT$", "新台幣"), "新台幣", "currency-new-taiwan-dollar"),))


def get_expander(enable_context_detection: bool = True) -> ChineseTaiwanAbbreviationExpander:
    return ChineseTaiwanAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
