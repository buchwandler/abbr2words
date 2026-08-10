from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("fa")


class PersianAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "fa"


def get_expander(enable_context_detection: bool = True) -> PersianAbbreviationExpander:
    return PersianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
