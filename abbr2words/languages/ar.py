from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("ar")


class ArabicAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "ar"


def get_expander(enable_context_detection: bool = True) -> ArabicAbbreviationExpander:
    return ArabicAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
