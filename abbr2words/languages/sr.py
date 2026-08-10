from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("sr")


class SerbianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "sr"


def get_expander(enable_context_detection: bool = True) -> SerbianAbbreviationExpander:
    return SerbianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
