from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("tet")


class TetumAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "tet"


def get_expander(enable_context_detection: bool = True) -> TetumAbbreviationExpander:
    return TetumAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
