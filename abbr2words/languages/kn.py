from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("kn")


class KannadaAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "kn"


def get_expander(enable_context_detection: bool = True) -> KannadaAbbreviationExpander:
    return KannadaAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
