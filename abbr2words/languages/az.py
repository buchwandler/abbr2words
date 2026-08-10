from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("az")


class AzerbaijaniAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "az"


def get_expander(enable_context_detection: bool = True) -> AzerbaijaniAbbreviationExpander:
    return AzerbaijaniAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
