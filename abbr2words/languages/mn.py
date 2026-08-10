from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("mn")


class MongolianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "mn"


def get_expander(enable_context_detection: bool = True) -> MongolianAbbreviationExpander:
    return MongolianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
