from ..unit_data.common import register_locale_units
from ._locales import EnglishUnitedKingdomAbbreviationExpander

register_locale_units("en_GB", "en")


def get_expander(enable_context_detection: bool = True) -> EnglishUnitedKingdomAbbreviationExpander:
    return EnglishUnitedKingdomAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
