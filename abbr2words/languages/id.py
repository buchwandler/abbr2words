from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("id")


class IndonesianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "id"


def get_expander(enable_context_detection: bool = True) -> IndonesianAbbreviationExpander:
    return IndonesianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
