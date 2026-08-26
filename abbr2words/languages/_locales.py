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


class EnglishUnitedStatesAbbreviationExpander(EnglishAbbreviationExpander):
    UNIT_LANGUAGE = "en_US"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()


class EnglishUnitedKingdomAbbreviationExpander(EnglishAbbreviationExpander):
    UNIT_LANGUAGE = "en_GB"

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


class SpanishMexicoAbbreviationExpander(SpanishAbbreviationExpander):
    UNIT_LANGUAGE = "es_MX"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        self.add_abbreviation(
            AbbreviationEntry(
                abbreviation="Blvd.",
                expansion="boulevard",
                case_policy="sentence",
                description="Mexican Spanish boulevard preference",
            )
        )


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


_CJK_LATIN_LEFT = r"(?<![A-Za-z0-9_])"
_CJK_LATIN_RIGHT = r"(?![A-Za-z0-9_]|[./@-][A-Za-z0-9_])"

_ZH_CN_REVIEWED_TERMS = (
    ("AI", "人工智能", "MOE recommended Chinese term; batch 6/7"),
    ("AIDS", "艾滋病", "MOE recommended Chinese term; batch 1"),
    ("GDP", "国内生产总值", "MOE recommended Chinese term; batch 1"),
    ("IQ", "智商", "MOE recommended Chinese term; batch 1"),
    ("IT", "信息技术", "MOE recommended Chinese term; batch 1"),
    ("OECD", "经济合作与发展组织", "MOE recommended Chinese term; batch 1"),
    ("OPEC", "石油输出国组织", "MOE recommended Chinese term; batch 1"),
    ("WHO", "世界卫生组织", "MOE recommended Chinese term; batch 1"),
    ("WTO", "世界贸易组织", "MOE recommended Chinese term; batch 1"),
)

class ChineseMainlandAbbreviationExpander(ChineseAbbreviationExpander):
    UNIT_LANGUAGE = "zh_CN"

    def _initialize_abbreviations(self) -> None:
        super()._initialize_abbreviations()
        for abbreviation, expansion, description in _ZH_CN_REVIEWED_TERMS:
            self.add_abbreviation(
                AbbreviationEntry(
                    abbreviation=abbreviation,
                    expansion=expansion,
                    case_sensitive=True,
                    description=description,
                    boundary="custom",
                    left_boundary=_CJK_LATIN_LEFT,
                    right_boundary=_CJK_LATIN_RIGHT,
                    speech_strategy="expand",
                )
            )

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
    "EnglishUnitedKingdomAbbreviationExpander",
    "EnglishUnitedStatesAbbreviationExpander",
    "FrenchAlgeriaAbbreviationExpander",
    "FrenchBelgiumAbbreviationExpander",
    "FrenchSwitzerlandAbbreviationExpander",
    "SpanishColombiaAbbreviationExpander",
    "SpanishCostaRicaAbbreviationExpander",
    "SpanishGuatemalaAbbreviationExpander",
    "SpanishNicaraguaAbbreviationExpander",
    "SpanishMexicoAbbreviationExpander",
    "SpanishVenezuelaAbbreviationExpander",
]
