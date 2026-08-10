from ..unit_data.common import register_locale_units
from ._locales import FrenchSwitzerlandAbbreviationExpander

register_locale_units("fr_CH", "fr")


def get_expander(enable_context_detection: bool = True) -> FrenchSwitzerlandAbbreviationExpander:
    return FrenchSwitzerlandAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
