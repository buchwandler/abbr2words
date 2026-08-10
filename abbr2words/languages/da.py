from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("da")


class DanishAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "da"


def get_expander(enable_context_detection: bool = True) -> DanishAbbreviationExpander:
    return DanishAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
