from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("th")


class ThaiAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "th"


def get_expander(enable_context_detection: bool = True) -> ThaiAbbreviationExpander:
    return ThaiAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
