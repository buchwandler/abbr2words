from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("bn")


class BengaliAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "bn"


def get_expander(enable_context_detection: bool = True) -> BengaliAbbreviationExpander:
    return BengaliAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
