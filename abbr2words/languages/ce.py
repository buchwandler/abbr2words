from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("ce")


class ChechenAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "ce"


def get_expander(enable_context_detection: bool = True) -> ChechenAbbreviationExpander:
    return ChechenAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
