from ..unit_data.common import register_locale_units
from ._locales import FrenchBelgiumAbbreviationExpander

register_locale_units("fr_BE", "fr")


def get_expander(enable_context_detection: bool = True) -> FrenchBelgiumAbbreviationExpander:
    return FrenchBelgiumAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
