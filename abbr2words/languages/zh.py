from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("zh")


class ChineseAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "zh"


def get_expander(enable_context_detection: bool = True) -> ChineseAbbreviationExpander:
    return ChineseAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
