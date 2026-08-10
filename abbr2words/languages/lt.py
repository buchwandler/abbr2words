from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("lt")


class LithuanianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "lt"


def get_expander(enable_context_detection: bool = True) -> LithuanianAbbreviationExpander:
    return LithuanianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
