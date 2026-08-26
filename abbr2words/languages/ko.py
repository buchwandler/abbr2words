from abbr2words.language_data.initialisms import (
    KOREAN_REVIEWED_INITIALISMS,
    register_reviewed_initialisms,
)

from ._conservative import ConservativeAbbreviationExpander, initialize_language

initialize_language("ko")


class KoreanAbbreviationExpander(ConservativeAbbreviationExpander):
    UNIT_LANGUAGE = LANGUAGE_KEY = "ko"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        register_reviewed_initialisms(self, KOREAN_REVIEWED_INITIALISMS)


def get_expander(enable_context_detection: bool = True) -> KoreanAbbreviationExpander:
    return KoreanAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    pass
