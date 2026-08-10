from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("no")


class NorwegianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "no"


def get_expander(enable_context_detection: bool = True) -> NorwegianAbbreviationExpander:
    return NorwegianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
