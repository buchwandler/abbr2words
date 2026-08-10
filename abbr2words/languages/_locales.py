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
        self.add_abbreviation(AbbreviationEntry("Rs.", "rupees", case_sensitive=True))


class EnglishNigeriaAbbreviationExpander(EnglishAbbreviationExpander):
    UNIT_LANGUAGE = "en_NG"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("₦", "naira", case_sensitive=True))


class SpanishColombiaAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_CO"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("COP", "peso colombiano", case_sensitive=True))


class SpanishCostaRicaAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_CR"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("₡", "colón costarricense", case_sensitive=True))


class SpanishGuatemalaAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_GT"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("Q.", "quetzal", case_sensitive=True))


class SpanishNicaraguaAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_NI"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("C$", "córdoba nicaragüense", case_sensitive=True))


class SpanishVenezuelaAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_VE"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("Bs.", "bolívar", case_sensitive=True))


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
        self.add_abbreviation(AbbreviationEntry("人民币", "人民币", case_sensitive=True))


class ChineseHongKongAbbreviationExpander(ChineseAbbreviationExpander):
    UNIT_LANGUAGE = "zh_HK"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("港元", "港元", case_sensitive=True))


class ChineseTaiwanAbbreviationExpander(ChineseAbbreviationExpander):
    UNIT_LANGUAGE = "zh_TW"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(AbbreviationEntry("新台幣", "新台幣", case_sensitive=True))


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
