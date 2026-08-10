from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("tg")


class TajikAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "tg"


def get_expander(enable_context_detection: bool = True) -> TajikAbbreviationExpander:
    return TajikAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
