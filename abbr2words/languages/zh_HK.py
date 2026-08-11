from ..unit_data.common import locale_currency, register_locale_units
from ._locales import ChineseHongKongAbbreviationExpander

register_locale_units("zh_HK", "zh", (locale_currency(("HK$", "港元"), "港元", "currency-hong-kong-dollar"),))


def get_expander(enable_context_detection: bool = True) -> ChineseHongKongAbbreviationExpander:
    return ChineseHongKongAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
