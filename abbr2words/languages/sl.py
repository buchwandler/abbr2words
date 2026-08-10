from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("sl")


class SloveneAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "sl"


def get_expander(enable_context_detection: bool = True) -> SloveneAbbreviationExpander:
    return SloveneAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
