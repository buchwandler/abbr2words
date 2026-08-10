from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("vi")


class VietnameseAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "vi"


def get_expander(enable_context_detection: bool = True) -> VietnameseAbbreviationExpander:
    return VietnameseAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
