from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("lv")


class LatvianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "lv"


def get_expander(enable_context_detection: bool = True) -> LatvianAbbreviationExpander:
    return LatvianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
