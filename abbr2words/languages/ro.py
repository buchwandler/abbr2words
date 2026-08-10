from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("ro")


class RomanianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "ro"


def get_expander(enable_context_detection: bool = True) -> RomanianAbbreviationExpander:
    return RomanianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
