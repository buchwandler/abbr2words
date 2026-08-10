from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("hu")


class HungarianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "hu"


def get_expander(enable_context_detection: bool = True) -> HungarianAbbreviationExpander:
    return HungarianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
