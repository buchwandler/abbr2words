from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("uk")


class UkrainianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "uk"


def get_expander(enable_context_detection: bool = True) -> UkrainianAbbreviationExpander:
    return UkrainianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
