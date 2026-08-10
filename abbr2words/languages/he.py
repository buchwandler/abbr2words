from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("he")


class HebrewAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "he"


def get_expander(enable_context_detection: bool = True) -> HebrewAbbreviationExpander:
    return HebrewAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
