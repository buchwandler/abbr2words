from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("kz")


class KazakhAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "kz"


def get_expander(enable_context_detection: bool = True) -> KazakhAbbreviationExpander:
    return KazakhAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
