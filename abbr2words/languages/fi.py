from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("fi")


class FinnishAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "fi"


def get_expander(enable_context_detection: bool = True) -> FinnishAbbreviationExpander:
    return FinnishAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
