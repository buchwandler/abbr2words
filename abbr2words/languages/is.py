from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("is")


class IcelandicAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "is"


def get_expander(enable_context_detection: bool = True) -> IcelandicAbbreviationExpander:
    return IcelandicAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
