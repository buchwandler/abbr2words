from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("eo")


class EsperantoAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "eo"


def get_expander(enable_context_detection: bool = True) -> EsperantoAbbreviationExpander:
    return EsperantoAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
