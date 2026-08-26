from ..unit_data.common import common_unit_entries, locale_currency, register_locale_units
from ._locales import ChineseMainlandAbbreviationExpander

register_locale_units(
    "zh_CN",
    "zh",
    (
        *common_unit_entries("zh_CN"),
        locale_currency(("¥", "人民币"), "人民币", "currency-chinese-yuan"),
    ),
)


def get_expander(enable_context_detection: bool = True) -> ChineseMainlandAbbreviationExpander:
    return ChineseMainlandAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
