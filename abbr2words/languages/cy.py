from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("cy")


class WelshAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "cy"


def get_expander(enable_context_detection: bool = True) -> WelshAbbreviationExpander:
    return WelshAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
