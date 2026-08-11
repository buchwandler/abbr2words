"""Released num2words locale overlays for abbreviation and unit data."""

from __future__ import annotations

from abbr2words.core import AbbreviationEntry
from abbr2words.languages.en import EnglishAbbreviationExpander
from abbr2words.languages.es import SpanishAbbreviationExpander
from abbr2words.languages.fr import FrenchAbbreviationExpander
from abbr2words.languages.pt import PortugueseAbbreviationExpander
from abbr2words.languages.zh import ChineseAbbreviationExpander


class EnglishIndiaAbbreviationExpander(EnglishAbbreviationExpander):
    UNIT_LANGUAGE = "en_IN"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


class EnglishNigeriaAbbreviationExpander(EnglishAbbreviationExpander):
    UNIT_LANGUAGE = "en_NG"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


class SpanishColombiaAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_CO"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


class SpanishCostaRicaAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_CR"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


class SpanishGuatemalaAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_GT"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


class SpanishNicaraguaAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_NI"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


class SpanishVenezuelaAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_VE"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


class FrenchBelgiumAbbreviationExpander(FrenchAbbreviationExpander):
    UNIT_LANGUAGE = "fr_BE"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("av.", "avenue", case_sensitive=False))


class FrenchSwitzerlandAbbreviationExpander(FrenchAbbreviationExpander):
    UNIT_LANGUAGE = "fr_CH"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("ch.", "chemin", case_sensitive=False))


class FrenchAlgeriaAbbreviationExpander(FrenchAbbreviationExpander):
    UNIT_LANGUAGE = "fr_DZ"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("wil.", "wilaya", case_sensitive=False))


class BrazilianPortugueseAbbreviationExpander(PortugueseAbbreviationExpander):
    UNIT_LANGUAGE = "pt_BR"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("est.", "estado", case_sensitive=False))


class ChineseMainlandAbbreviationExpander(ChineseAbbreviationExpander):
    UNIT_LANGUAGE = "zh_CN"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


class ChineseHongKongAbbreviationExpander(ChineseAbbreviationExpander):
    UNIT_LANGUAGE = "zh_HK"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


class ChineseTaiwanAbbreviationExpander(ChineseAbbreviationExpander):
    UNIT_LANGUAGE = "zh_TW"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


__all__ = [
    "BrazilianPortugueseAbbreviationExpander",
    "ChineseHongKongAbbreviationExpander",
    "ChineseMainlandAbbreviationExpander",
    "ChineseTaiwanAbbreviationExpander",
    "EnglishIndiaAbbreviationExpander",
    "EnglishNigeriaAbbreviationExpander",
    "FrenchAlgeriaAbbreviationExpander",
    "FrenchBelgiumAbbreviationExpander",
    "FrenchSwitzerlandAbbreviationExpander",
    "SpanishColombiaAbbreviationExpander",
    "SpanishCostaRicaAbbreviationExpander",
    "SpanishGuatemalaAbbreviationExpander",
    "SpanishNicaraguaAbbreviationExpander",
    "SpanishVenezuelaAbbreviationExpander",
]
