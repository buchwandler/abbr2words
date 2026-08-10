from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("ja")


class JapaneseAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "ja"


def get_expander(enable_context_detection: bool = True) -> JapaneseAbbreviationExpander:
    return JapaneseAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
