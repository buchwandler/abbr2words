from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("hi")


class HindiAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "hi"


def get_expander(enable_context_detection: bool = True) -> HindiAbbreviationExpander:
    return HindiAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
