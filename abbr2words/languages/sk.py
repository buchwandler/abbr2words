from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("sk")


class SlovakAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "sk"


def get_expander(enable_context_detection: bool = True) -> SlovakAbbreviationExpander:
    return SlovakAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
