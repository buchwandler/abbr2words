from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("am")


class AmharicAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "am"


def get_expander(enable_context_detection: bool = True) -> AmharicAbbreviationExpander:
    return AmharicAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
