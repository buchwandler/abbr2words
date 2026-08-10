from ..unit_data.common import register_locale_units
from ._locales import BrazilianPortugueseAbbreviationExpander

register_locale_units("pt_BR", "pt")


def get_expander(enable_context_detection: bool = True) -> BrazilianPortugueseAbbreviationExpander:
    return BrazilianPortugueseAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
