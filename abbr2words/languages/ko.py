from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("ko")


class KoreanAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "ko"


def get_expander(enable_context_detection: bool = True) -> KoreanAbbreviationExpander:
    return KoreanAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
