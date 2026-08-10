from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("be")


class BelarusianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "be"


def get_expander(enable_context_detection: bool = True) -> BelarusianAbbreviationExpander:
    return BelarusianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
