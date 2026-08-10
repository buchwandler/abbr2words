from ..unit_data.common import register_locale_units
from ._locales import FrenchAlgeriaAbbreviationExpander

register_locale_units("fr_DZ", "fr")


def get_expander(enable_context_detection: bool = True) -> FrenchAlgeriaAbbreviationExpander:
    return FrenchAlgeriaAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
