"""Explicit language and locale registry metadata."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final


@dataclass(frozen=True, slots=True)
class LanguageSpec:
    """Metadata needed to resolve and instantiate one public language key."""

    key: str
    base: str
    module: str
    class_name: str
    unit_key: str
    num2words_key: str
    released_in_num2words: bool = True


_BASE_SPECS = {
    "cs": LanguageSpec(
        "cs", "cs", "abbr2words.languages.cs", "CzechAbbreviationExpander", "cs", "cs"
    ),
    "de": LanguageSpec(
        "de", "de", "abbr2words.languages.de", "GermanAbbreviationExpander", "de", "de"
    ),
    "en": LanguageSpec(
        "en", "en", "abbr2words.languages.en", "EnglishAbbreviationExpander", "en", "en"
    ),
    "es": LanguageSpec(
        "es", "es", "abbr2words.languages.es", "SpanishAbbreviationExpander", "es", "es"
    ),
    "fr": LanguageSpec(
        "fr", "fr", "abbr2words.languages.fr", "FrenchAbbreviationExpander", "fr", "fr"
    ),
    "it": LanguageSpec(
        "it", "it", "abbr2words.languages.it", "ItalianAbbreviationExpander", "it", "it"
    ),
    "nl": LanguageSpec(
        "nl", "nl", "abbr2words.languages.nl", "DutchAbbreviationExpander", "nl", "nl"
    ),
    "pl": LanguageSpec(
        "pl", "pl", "abbr2words.languages.pl", "PolishAbbreviationExpander", "pl", "pl"
    ),
    "pt": LanguageSpec(
        "pt", "pt", "abbr2words.languages.pt", "PortugueseAbbreviationExpander", "pt", "pt"
    ),
    "ru": LanguageSpec(
        "ru", "ru", "abbr2words.languages.ru", "RussianAbbreviationExpander", "ru", "ru"
    ),
    "sv": LanguageSpec(
        "sv", "sv", "abbr2words.languages.sv", "SwedishAbbreviationExpander", "sv", "sv"
    ),
    "tr": LanguageSpec(
        "tr", "tr", "abbr2words.languages.tr", "TurkishAbbreviationExpander", "tr", "tr"
    ),
}

_BASE_SPECS.update(
    {
        "am": LanguageSpec(
            "am", "am", "abbr2words.languages.am", "AmharicAbbreviationExpander", "am", "am"
        ),
        "ar": LanguageSpec(
            "ar", "ar", "abbr2words.languages.ar", "ArabicAbbreviationExpander", "ar", "ar"
        ),
        "az": LanguageSpec(
            "az", "az", "abbr2words.languages.az", "AzerbaijaniAbbreviationExpander", "az", "az"
        ),
        "be": LanguageSpec(
            "be", "be", "abbr2words.languages.be", "BelarusianAbbreviationExpander", "be", "be"
        ),
        "bn": LanguageSpec(
            "bn", "bn", "abbr2words.languages.bn", "BengaliAbbreviationExpander", "bn", "bn"
        ),
        "ca": LanguageSpec(
            "ca", "ca", "abbr2words.languages.ca", "CatalanAbbreviationExpander", "ca", "ca"
        ),
        "ce": LanguageSpec(
            "ce", "ce", "abbr2words.languages.ce", "ChechenAbbreviationExpander", "ce", "ce"
        ),
        "cy": LanguageSpec(
            "cy", "cy", "abbr2words.languages.cy", "WelshAbbreviationExpander", "cy", "cy"
        ),
        "da": LanguageSpec(
            "da", "da", "abbr2words.languages.da", "DanishAbbreviationExpander", "da", "da"
        ),
        "eo": LanguageSpec(
            "eo", "eo", "abbr2words.languages.eo", "EsperantoAbbreviationExpander", "eo", "eo"
        ),
        "fa": LanguageSpec(
            "fa", "fa", "abbr2words.languages.fa", "PersianAbbreviationExpander", "fa", "fa"
        ),
        "fi": LanguageSpec(
            "fi", "fi", "abbr2words.languages.fi", "FinnishAbbreviationExpander", "fi", "fi"
        ),
        "he": LanguageSpec(
            "he", "he", "abbr2words.languages.he", "HebrewAbbreviationExpander", "he", "he"
        ),
        "hu": LanguageSpec(
            "hu", "hu", "abbr2words.languages.hu", "HungarianAbbreviationExpander", "hu", "hu"
        ),
        "id": LanguageSpec(
            "id", "id", "abbr2words.languages.id", "IndonesianAbbreviationExpander", "id", "id"
        ),
        "is": LanguageSpec(
            "is", "is", "abbr2words.languages.is", "IcelandicAbbreviationExpander", "is", "is"
        ),
        "ja": LanguageSpec(
            "ja", "ja", "abbr2words.languages.ja", "JapaneseAbbreviationExpander", "ja", "ja"
        ),
        "kn": LanguageSpec(
            "kn", "kn", "abbr2words.languages.kn", "KannadaAbbreviationExpander", "kn", "kn"
        ),
        "ko": LanguageSpec(
            "ko", "ko", "abbr2words.languages.ko", "KoreanAbbreviationExpander", "ko", "ko"
        ),
        "kz": LanguageSpec(
            "kz", "kz", "abbr2words.languages.kz", "KazakhAbbreviationExpander", "kz", "kz"
        ),
        "lt": LanguageSpec(
            "lt", "lt", "abbr2words.languages.lt", "LithuanianAbbreviationExpander", "lt", "lt"
        ),
        "lv": LanguageSpec(
            "lv", "lv", "abbr2words.languages.lv", "LatvianAbbreviationExpander", "lv", "lv"
        ),
        "no": LanguageSpec(
            "no", "no", "abbr2words.languages.no", "NorwegianAbbreviationExpander", "no", "no"
        ),
        "ro": LanguageSpec(
            "ro", "ro", "abbr2words.languages.ro", "RomanianAbbreviationExpander", "ro", "ro"
        ),
        "sk": LanguageSpec(
            "sk", "sk", "abbr2words.languages.sk", "SlovakAbbreviationExpander", "sk", "sk"
        ),
        "sl": LanguageSpec(
            "sl", "sl", "abbr2words.languages.sl", "SloveneAbbreviationExpander", "sl", "sl"
        ),
        "sr": LanguageSpec(
            "sr", "sr", "abbr2words.languages.sr", "SerbianAbbreviationExpander", "sr", "sr"
        ),
        "te": LanguageSpec(
            "te", "te", "abbr2words.languages.te", "TeluguAbbreviationExpander", "te", "te"
        ),
        "tet": LanguageSpec(
            "tet", "tet", "abbr2words.languages.tet", "TetumAbbreviationExpander", "tet", "tet"
        ),
        "tg": LanguageSpec(
            "tg", "tg", "abbr2words.languages.tg", "TajikAbbreviationExpander", "tg", "tg"
        ),
        "th": LanguageSpec(
            "th", "th", "abbr2words.languages.th", "ThaiAbbreviationExpander", "th", "th"
        ),
        "uk": LanguageSpec(
            "uk", "uk", "abbr2words.languages.uk", "UkrainianAbbreviationExpander", "uk", "uk"
        ),
        "vi": LanguageSpec(
            "vi", "vi", "abbr2words.languages.vi", "VietnameseAbbreviationExpander", "vi", "vi"
        ),
        "en_IN": LanguageSpec(
            "en_IN",
            "en",
            "abbr2words.languages.en_IN",
            "EnglishIndiaAbbreviationExpander",
            "en_IN",
            "en_IN",
        ),
        "en_NG": LanguageSpec(
            "en_NG",
            "en",
            "abbr2words.languages.en_NG",
            "EnglishNigeriaAbbreviationExpander",
            "en_NG",
            "en_NG",
        ),
        "en_US": LanguageSpec(
            "en_US",
            "en",
            "abbr2words.languages.en_US",
            "EnglishUnitedStatesAbbreviationExpander",
            "en_US",
            "en",
        ),
        "en_GB": LanguageSpec(
            "en_GB",
            "en",
            "abbr2words.languages.en_GB",
            "EnglishUnitedKingdomAbbreviationExpander",
            "en_GB",
            "en_GB",
        ),
        "es_CO": LanguageSpec(
            "es_CO",
            "es",
            "abbr2words.languages.es_CO",
            "SpanishColombiaAbbreviationExpander",
            "es_CO",
            "es_CO",
        ),
        "es_CR": LanguageSpec(
            "es_CR",
            "es",
            "abbr2words.languages.es_CR",
            "SpanishCostaRicaAbbreviationExpander",
            "es_CR",
            "es_CR",
        ),
        "es_GT": LanguageSpec(
            "es_GT",
            "es",
            "abbr2words.languages.es_GT",
            "SpanishGuatemalaAbbreviationExpander",
            "es_GT",
            "es_GT",
        ),
        "es_NI": LanguageSpec(
            "es_NI",
            "es",
            "abbr2words.languages.es_NI",
            "SpanishNicaraguaAbbreviationExpander",
            "es_NI",
            "es_NI",
        ),
        "es_VE": LanguageSpec(
            "es_VE",
            "es",
            "abbr2words.languages.es_VE",
            "SpanishVenezuelaAbbreviationExpander",
            "es_VE",
            "es_VE",
        ),
        "es_MX": LanguageSpec(
            "es_MX",
            "es",
            "abbr2words.languages.es_MX",
            "SpanishMexicoAbbreviationExpander",
            "es_MX",
            "es_MX",
        ),
        "fr_BE": LanguageSpec(
            "fr_BE",
            "fr",
            "abbr2words.languages.fr_BE",
            "FrenchBelgiumAbbreviationExpander",
            "fr_BE",
            "fr_BE",
        ),
        "fr_CH": LanguageSpec(
            "fr_CH",
            "fr",
            "abbr2words.languages.fr_CH",
            "FrenchSwitzerlandAbbreviationExpander",
            "fr_CH",
            "fr_CH",
        ),
        "fr_DZ": LanguageSpec(
            "fr_DZ",
            "fr",
            "abbr2words.languages.fr_DZ",
            "FrenchAlgeriaAbbreviationExpander",
            "fr_DZ",
            "fr_DZ",
        ),
        "pt_BR": LanguageSpec(
            "pt_BR",
            "pt",
            "abbr2words.languages.pt_BR",
            "BrazilianPortugueseAbbreviationExpander",
            "pt_BR",
            "pt_BR",
        ),
        "hi": LanguageSpec(
            "hi", "hi", "abbr2words.languages.hi", "HindiAbbreviationExpander", "hi", "hi", False
        ),
        "hy": LanguageSpec(
            "hy", "hy", "abbr2words.languages.hy", "ArmenianAbbreviationExpander", "hy", "hy", False
        ),
        "mn": LanguageSpec(
            "mn",
            "mn",
            "abbr2words.languages.mn",
            "MongolianAbbreviationExpander",
            "mn",
            "mn",
            False,
        ),
        "zh": LanguageSpec(
            "zh", "zh", "abbr2words.languages.zh", "ChineseAbbreviationExpander", "zh", "zh", False
        ),
        "zh_CN": LanguageSpec(
            "zh_CN",
            "zh",
            "abbr2words.languages.zh_CN",
            "ChineseMainlandAbbreviationExpander",
            "zh_CN",
            "zh_CN",
            False,
        ),
        "zh_HK": LanguageSpec(
            "zh_HK",
            "zh",
            "abbr2words.languages.zh_HK",
            "ChineseHongKongAbbreviationExpander",
            "zh_HK",
            "zh_HK",
            False,
        ),
        "zh_TW": LanguageSpec(
            "zh_TW",
            "zh",
            "abbr2words.languages.zh_TW",
            "ChineseTaiwanAbbreviationExpander",
            "zh_TW",
            "zh_TW",
            False,
        ),
    }
)

LANGUAGE_SPECS: Final[Mapping[str, LanguageSpec]] = MappingProxyType(_BASE_SPECS)

ALIASES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "cz": "cs",
        "cze": "cs",
        "ces": "cs",
        "deu": "de",
        "ger": "de",
        "eng": "en",
        "spa": "es",
        "fra": "fr",
        "fre": "fr",
        "ita": "it",
        "por": "pt",
        "dut": "nl",
        "nld": "nl",
        "pol": "pl",
        "rus": "ru",
        "swe": "sv",
        "tur": "tr",
    }
)


def canonicalize_language_tag(lang: str) -> tuple[str, str]:
    """Return ``(canonical_candidate, canonical_base)`` for an input tag."""
    if not isinstance(lang, str) or not lang.strip():
        raise ValueError("lang must be a non-empty language code")

    parts = lang.strip().replace("-", "_").split("_")
    if len(parts) > 2 or any(not part for part in parts):
        candidate = "_".join(part for part in parts if part).lower()
        return candidate, candidate.split("_", 1)[0]

    base = ALIASES.get(parts[0].lower(), parts[0].lower())
    if len(parts) == 1:
        return base, base
    region = parts[1].upper()
    return f"{base}_{region}", base


def resolve_language(lang: str) -> str:
    """Resolve exact locale keys first, then fall back to a base registry."""
    candidate, base = canonicalize_language_tag(lang)
    if candidate in LANGUAGE_SPECS:
        return candidate
    if base in LANGUAGE_SPECS:
        return base
    supported = ", ".join(sorted(LANGUAGE_SPECS))
    raise ValueError(f"Unsupported language {lang!r}. Supported languages: {supported}")


def language_spec(lang: str) -> LanguageSpec:
    """Return metadata for a resolved language key."""
    return LANGUAGE_SPECS[resolve_language(lang)]


def supported_language_keys(*, include_locales: bool = True) -> tuple[str, ...]:
    """Return sorted canonical registry keys."""
    if include_locales:
        return tuple(sorted(LANGUAGE_SPECS))
    return tuple(sorted(key for key, spec in LANGUAGE_SPECS.items() if key == spec.base))
