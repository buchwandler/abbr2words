from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("te")


class TeluguAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "te"


def get_expander(enable_context_detection: bool = True) -> TeluguAbbreviationExpander:
    return TeluguAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
