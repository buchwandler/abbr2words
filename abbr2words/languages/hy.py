from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("hy")


class ArmenianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "hy"


def get_expander(enable_context_detection: bool = True) -> ArmenianAbbreviationExpander:
    return ArmenianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
