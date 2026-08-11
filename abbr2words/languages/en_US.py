from ..unit_data.common import register_locale_units
from ._locales import EnglishUnitedStatesAbbreviationExpander

register_locale_units("en_US", "en")


def get_expander(enable_context_detection: bool = True) -> EnglishUnitedStatesAbbreviationExpander:
    return EnglishUnitedStatesAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
