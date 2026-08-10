"""Shared conservative implementation for independent new language modules."""

from __future__ import annotations

from collections.abc import Sequence

from abbr2words.core import AbbreviationExpander
from abbr2words.languages._helpers import AbbreviationSeed, register_seeds
from abbr2words.unit_data.common import register_common_units

_COMMON_SEEDS: dict[str, Sequence[AbbreviationSeed]] = {
    "am": (AbbreviationSeed("№", "ቁጥር", "Number sign", case_sensitive=True, boundary="custom"),),
    "ar": (AbbreviationSeed("د.", "دكتور", "Doctor", case_sensitive=True),),
    "az": (AbbreviationSeed("№", "nömrə", "Number sign", case_sensitive=True),),
    "be": (AbbreviationSeed("гл.", "галоўны", "Reference abbreviation"),),
    "bn": (AbbreviationSeed("নং", "নম্বর", "Number sign", case_sensitive=True),),
    "ca": (AbbreviationSeed("Sr.", "Senyor", "Honorific"),),
    "ce": (AbbreviationSeed("№", "номер", "Number sign", case_sensitive=True),),
    "cy": (AbbreviationSeed("Dr.", "Doctor", "Honorific"),),
    "da": (AbbreviationSeed("nr.", "nummer", "Number reference"),),
    "eo": (AbbreviationSeed("ktp.", "kaj tiel plu", "Common reference"),),
    "fa": (AbbreviationSeed("د.", "دکتر", "Doctor", case_sensitive=True),),
    "fi": (AbbreviationSeed("nro.", "numero", "Number reference"),),
    "he": (AbbreviationSeed("ד׳", "דוקטור", "Doctor", case_sensitive=True),),
    "hu": (AbbreviationSeed("dr.", "doktor", "Honorific"),),
    "id": (AbbreviationSeed("No.", "nomor", "Number reference"),),
    "is": (AbbreviationSeed("nr.", "númer", "Number reference"),),
    "ja": (AbbreviationSeed("№", "番号", "Number sign", case_sensitive=True),),
    "kn": (AbbreviationSeed("ನಂ.", "ಸಂಖ್ಯೆ", "Number reference", case_sensitive=True),),
    "ko": (AbbreviationSeed("№", "번호", "Number sign", case_sensitive=True),),
    "kz": (AbbreviationSeed("№", "нөмір", "Number sign", case_sensitive=True),),
    "lt": (AbbreviationSeed("nr.", "numeris", "Number reference"),),
    "lv": (AbbreviationSeed("Nr.", "numurs", "Number reference"),),
    "no": (AbbreviationSeed("nr.", "nummer", "Number reference"),),
    "ro": (AbbreviationSeed("nr.", "număr", "Number reference"),),
    "sk": (AbbreviationSeed("č.", "číslo", "Number reference"),),
    "sl": (AbbreviationSeed("št.", "številka", "Number reference"),),
    "sr": (AbbreviationSeed("бр.", "број", "Number reference"),),
    "te": (AbbreviationSeed("నం.", "నంబరు", "Number reference", case_sensitive=True),),
    "tet": (AbbreviationSeed("núm.", "númeru", "Number reference"),),
    "tg": (AbbreviationSeed("№", "рақам", "Number sign", case_sensitive=True),),
    "th": (AbbreviationSeed("№", "หมายเลข", "Number sign", case_sensitive=True),),
    "uk": (AbbreviationSeed("№", "номер", "Number sign", case_sensitive=True),),
    "vi": (AbbreviationSeed("số", "số", "Number word", case_sensitive=True),),
    "hi": (AbbreviationSeed("क्र.", "क्रमांक", "Number reference", case_sensitive=True),),
    "hy": (AbbreviationSeed("հ.", "համար", "Number reference", case_sensitive=True),),
    "mn": (AbbreviationSeed("№", "дугаар", "Number sign", case_sensitive=True),),
    "zh": (AbbreviationSeed("№", "编号", "Number sign", case_sensitive=True),),
}


class ConservativeAbbreviationExpander(AbbreviationExpander):
    """Small reviewed seed registry that fails closed on ambiguous text."""

    UNIT_LANGUAGE = "en"
    LANGUAGE_KEY = ""

    def _initialize_abbreviations(self) -> None:
        register_seeds(self, _COMMON_SEEDS[self.LANGUAGE_KEY])


def initialize_language(language: str) -> None:
    """Install common unit data before the core expander is instantiated."""
    register_common_units(language)


__all__ = ["ConservativeAbbreviationExpander", "initialize_language"]
