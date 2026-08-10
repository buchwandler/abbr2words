from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("ca")


class CatalanAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "ca"


def get_expander(enable_context_detection: bool = True) -> CatalanAbbreviationExpander:
    return CatalanAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
