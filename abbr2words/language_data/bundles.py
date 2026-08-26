"""Initial checked-in bundles, preserving the pre-refactor conservative rules."""

from __future__ import annotations

from dataclasses import replace
from importlib import import_module

from .model import AbbreviationSeed, LanguageBundle, SourceRef

_LEGACY = SourceRef(
    "legacy-abbr2words",
    "Existing abbr2words language registry",
    "https://github.com/openai/abbr2words",
    "reconstructed-2026-08-10",
)

_JA_SOURCES = (
    SourceRef(
        "ja-nta-organization-abbreviations",
        "National Tax Agency organization-name abbreviation guidance",
        "https://www.nta.go.jp/taxes/tetsuzuki/shinsei/hoteichosho/06.htm",
        "reviewed-2026-08-26",
    ),
    SourceRef(
        "ja-nmij-si",
        "NMIJ/AIST International System of Units in Japanese",
        "https://unit.aist.go.jp/nmij/library/si-units/",
        "reviewed-2026-08-26",
    ),
    SourceRef(
        "ja-government-page-reference-examples",
        "Japanese government page and address usage examples",
        "https://www.nta.go.jp/about/organization/tokyo/shiryo/simple.htm",
        "reviewed-2026-08-26",
    ),
    SourceRef(
        "unicode-cldr-48.2.1",
        "Unicode CLDR Japanese locale and unit data",
        "https://github.com/unicode-org/cldr/blob/main/common/main/ja.xml",
        "48.2.1",
    ),
)


def _seed(
    abbreviation: str,
    expansion: str,
    description: str,
    *,
    case_sensitive: bool = False,
    boundary: str = "word",
    only_if_preceded_by: str | None = None,
    only_if_followed_by: str | None = None,
    category: str = "other",
    source_id: str = "legacy-abbr2words",
    aliases: tuple[str, ...] = (),
    speech_strategy: str = "expand",
) -> AbbreviationSeed:
    return AbbreviationSeed(
        abbreviation,
        expansion,
        description,
        case_sensitive=case_sensitive,
        category=category,  # type: ignore[arg-type]
        aliases=aliases,
        speech_strategy=speech_strategy,  # type: ignore[arg-type]
        boundary=boundary,  # type: ignore[arg-type]
        only_if_preceded_by=only_if_preceded_by,
        only_if_followed_by=only_if_followed_by,
        source_ids=(source_id,),
        review_note="Checked-in baseline rule; review status is recorded in docs/language-sources.md.",
    )


_SEEDS: dict[str, tuple[AbbreviationSeed, ...]] = {
    "am": (_seed("№", "ቁጥር", "Number sign", case_sensitive=True, boundary="custom"),),
    "ar": (_seed("د.", "دكتور", "Doctor", case_sensitive=True),),
    "az": (_seed("№", "nömrə", "Number sign", case_sensitive=True),),
    "be": (_seed("гл.", "галоўны", "Reference abbreviation"),),
    "bn": (_seed("নং", "নম্বর", "Number sign", case_sensitive=True),),
    "ca": (_seed("Sr.", "Senyor", "Honorific"),),
    "ce": (_seed("№", "номер", "Number sign", case_sensitive=True),),
    "cy": (_seed("Dr.", "Doctor", "Honorific"),),
    "da": (_seed("nr.", "nummer", "Number reference"),),
    "eo": (_seed("ktp.", "kaj tiel plu", "Common reference"),),
    "fa": (_seed("د.", "دکتر", "Doctor", case_sensitive=True),),
    "fi": (_seed("nro.", "numero", "Number reference"),),
    "he": (_seed("ד׳", "דוקטור", "Doctor", case_sensitive=True),),
    "hi": (_seed("क्र.", "क्रमांक", "Number reference", case_sensitive=True),),
    "hu": (_seed("dr.", "doktor", "Honorific"),),
    "hy": (_seed("հ.", "համար", "Number reference", case_sensitive=True),),
    "id": (_seed("No.", "nomor", "Number reference"),),
    "is": (_seed("nr.", "númer", "Number reference"),),
    "ja": (
        _seed(
            "№",
            "番号",
            "Number sign",
            case_sensitive=True,
            source_id="ja-government-page-reference-examples",
        ),
    ),
    "kn": (_seed("ನಂ.", "ಸಂಖ್ಯೆ", "Number reference", case_sensitive=True),),
    "ko": (_seed("№", "번호", "Number sign", case_sensitive=True),),
    "kz": (_seed("№", "нөмір", "Number sign", case_sensitive=True),),
    "lt": (_seed("nr.", "numeris", "Number reference"),),
    "lv": (_seed("Nr.", "numurs", "Number reference"),),
    "mn": (_seed("№", "дугаар", "Number sign", case_sensitive=True),),
    "no": (_seed("nr.", "nummer", "Number reference"),),
    "ro": (_seed("nr.", "număr", "Number reference"),),
    "sk": (_seed("č.", "číslo", "Number reference"),),
    "sl": (_seed("št.", "številka", "Number reference"),),
    "sr": (_seed("бр.", "број", "Number reference"),),
    "te": (_seed("నం.", "నంబరు", "Number reference", case_sensitive=True),),
    "tet": (_seed("núm.", "númeru", "Number reference"),),
    "tg": (_seed("№", "рақам", "Number sign", case_sensitive=True),),
    "th": (_seed("№", "หมายเลข", "Number sign", case_sensitive=True),),
    "uk": (_seed("№", "номер", "Number sign", case_sensitive=True),),
    "vi": (
        _seed(
            "TP.",
            "thành phố",
            "Administrative place marker",
            category="address",
            source_id="language-style-baseline",
        ),
    ),
    "zh": (_seed("№", "编号", "Number sign", case_sensitive=True),),
}

_N = r"^[ \t\u00a0\u202f]*\d"
_EXTRA = {
    "am": (
        _seed(
            "ቁ.",
            "ቁጥር",
            "Number reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
    ),
    "ar": (
        _seed(
            "ص.",
            "صفحة",
            "Page reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "م.",
            "مهندس",
            "Professional title",
            case_sensitive=True,
            category="title",
            source_id="language-style-baseline",
        ),
    ),
    "az": (
        _seed(
            "səh.",
            "səhifə",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
        ),
        _seed("dr.", "doktor", "Title", category="title", source_id="language-style-baseline"),
    ),
    "be": (
        _seed(
            "с.",
            "старонка",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "сп.",
            "спіс",
            "List reference",
            category="reference",
            source_id="language-style-baseline",
        ),
    ),
    "bn": (
        _seed(
            "পৃ.",
            "পৃষ্ঠা",
            "Page reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "ডা.",
            "ডাক্তার",
            "Title",
            case_sensitive=True,
            category="title",
            source_id="language-style-baseline",
        ),
    ),
    "ca": (
        _seed(
            "pàg.",
            "pàgina",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "núm.",
            "número",
            "Number reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
    ),
    "ce": (
        _seed(
            "стр.",
            "страница",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "им.",
            "имени",
            "Named-after reference",
            category="reference",
            source_id="language-style-baseline",
        ),
    ),
    "cy": (
        _seed(
            "tud.",
            "tudalen",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "rhif.",
            "rhif",
            "Number reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
    ),
    "da": (
        _seed(
            "s.",
            "side",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "fig.",
            "figur",
            "Figure reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
    ),
    "eo": (
        _seed(
            "p.",
            "paĝo",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "ekz.",
            "ekzemple",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "fa": (
        _seed(
            "ص.",
            "صفحه",
            "Page reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "مه.",
            "مهندس",
            "Professional title",
            case_sensitive=True,
            category="title",
            source_id="language-style-baseline",
        ),
    ),
    "fi": (
        _seed(
            "s.",
            "sivu",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "esim.",
            "esimerkiksi",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "he": (
        _seed(
            "עמ׳",
            "עמוד",
            "Page reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "מס׳",
            "מספר",
            "Number reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
    ),
    "hi": (
        _seed(
            "पृ.",
            "पृष्ठ",
            "Page reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "डॉ.",
            "डॉक्टर",
            "Title",
            case_sensitive=True,
            category="title",
            source_id="language-style-baseline",
        ),
    ),
    "hu": (
        _seed(
            "o.",
            "oldal",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "pl.",
            "például",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "hy": (
        _seed(
            "էջ.",
            "էջ",
            "Page reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "պ.",
            "պարոն",
            "Title",
            case_sensitive=True,
            category="title",
            source_id="language-style-baseline",
        ),
    ),
    "id": (
        _seed(
            "hal.",
            "halaman",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "yth.",
            "yang terhormat",
            "Honorific",
            category="title",
            source_id="language-style-baseline",
        ),
    ),
    "is": (
        _seed(
            "bls.",
            "blaðsíða",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "t.d.",
            "til dæmis",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "ja": (
        _seed(
            "（株）",
            "株式会社",
            "Organization abbreviation",
            case_sensitive=True,
            boundary="custom",
            category="organization",
            source_id="ja-nta-organization-abbreviations",
        ),
        _seed(
            "(株)",
            "株式会社",
            "Organization abbreviation",
            case_sensitive=True,
            boundary="custom",
            category="organization",
            source_id="ja-nta-organization-abbreviations",
        ),
        _seed(
            "㈱",
            "株式会社",
            "Organization abbreviation",
            case_sensitive=True,
            boundary="custom",
            category="organization",
            source_id="ja-nta-organization-abbreviations",
        ),
        _seed(
            "（有）",
            "有限会社",
            "Organization abbreviation",
            case_sensitive=True,
            boundary="custom",
            category="organization",
            source_id="ja-nta-organization-abbreviations",
        ),
        _seed(
            "(有)",
            "有限会社",
            "Organization abbreviation",
            case_sensitive=True,
            boundary="custom",
            category="organization",
            source_id="ja-nta-organization-abbreviations",
        ),
        _seed(
            "㈲",
            "有限会社",
            "Organization abbreviation",
            case_sensitive=True,
            boundary="custom",
            category="organization",
            source_id="ja-nta-organization-abbreviations",
        ),
    ),
    "kn": (
        _seed(
            "ಪು.",
            "ಪುಟ",
            "Page reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "ಡಾ.",
            "ಡಾಕ್ಟರ್",
            "Title",
            case_sensitive=True,
            category="title",
            source_id="language-style-baseline",
        ),
    ),
    "ko": (
        _seed(
            "p.",
            "페이지",
            "Page reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "번",
            "번호",
            "Number marker",
            case_sensitive=True,
            boundary="custom",
            only_if_followed_by=_N,
            category="reference",
            source_id="language-style-baseline",
        ),
    ),
    "kz": (
        _seed(
            "бет.",
            "бет",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed("мырз.", "мырза", "Title", category="title", source_id="language-style-baseline"),
    ),
    "lt": (
        _seed(
            "p.",
            "puslapis",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "pvz.",
            "pavyzdžiui",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "lv": (
        _seed(
            "lpp.",
            "lappuse",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "piem.",
            "piemēram",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "mn": (
        _seed(
            "х.",
            "хуудас",
            "Page reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed("док.", "доктор", "Title", category="title", source_id="language-style-baseline"),
    ),
    "no": (
        _seed(
            "s.",
            "side",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "f.eks.",
            "for eksempel",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "ro": (
        _seed(
            "pag.",
            "pagină",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "ex.",
            "exemplu",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "sk": (
        _seed(
            "s.",
            "strana",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "napr.",
            "napríklad",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "sl": (
        _seed(
            "str.",
            "stran",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "npr.",
            "na primer",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "sr": (
        _seed(
            "стр.",
            "страна",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "нпр.",
            "на пример",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "te": (
        _seed(
            "పు.",
            "పుట",
            "Page reference",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "డా.",
            "డాక్టర్",
            "Title",
            case_sensitive=True,
            category="title",
            source_id="language-style-baseline",
        ),
    ),
    "tet": (
        _seed(
            "pág.",
            "pájina",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "ez.",
            "ezemplu",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "tg": (
        _seed(
            "саҳ.",
            "саҳифа",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "мис.", "мисол", "Example marker", category="prose", source_id="language-style-baseline"
        ),
    ),
    "th": (
        _seed(
            "ม.",
            "มหาวิทยาลัย",
            "Institution marker",
            case_sensitive=True,
            category="organization",
            source_id="language-style-baseline",
        ),
        _seed(
            "หน้า.",
            "หน้า",
            "Page marker",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
    ),
    "uk": (
        _seed(
            "стор.",
            "сторінка",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "напр.",
            "наприклад",
            "Example marker",
            category="prose",
            source_id="language-style-baseline",
        ),
    ),
    "vi": (
        _seed(
            "tr.",
            "trang",
            "Page reference",
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "ĐT.",
            "điện thoại",
            "Telephone marker",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
        ),
    ),
    "zh": (
        _seed(
            "页",
            "页码",
            "Page marker",
            case_sensitive=True,
            category="reference",
            source_id="language-style-baseline",
            only_if_followed_by=_N,
        ),
        _seed(
            "号",
            "号码",
            "Number marker",
            case_sensitive=True,
            boundary="custom",
            only_if_followed_by=_N,
            category="reference",
            source_id="language-style-baseline",
        ),
    ),
}

for _language, _extra in _EXTRA.items():
    _SEEDS[_language] = (() if _language == "vi" else _SEEDS[_language]) + _extra

for _language, _seeds_for_language in tuple(_SEEDS.items()):
    _SEEDS[_language] = tuple(
        replace(
            _seed_item,
            boundary="custom",
            left_boundary=r"(?<!\w)",
            right_boundary=r"(?=[ \t\u00a0\u202f]*\d)",
            only_if_followed_by=_N,
        )
        if _seed_item.abbreviation == "№"
        else _seed_item
        for _seed_item in _seeds_for_language
    )

# Reference markers are deliberately numeric-context-only.  This keeps short
# spellings such as ``s.`` and ``p.`` from expanding ordinary prose.
for _language, _seeds_for_language in tuple(_SEEDS.items()):
    _SEEDS[_language] = tuple(
        replace(_seed_item, only_if_followed_by=_N)
        if _seed_item.category == "reference" and _seed_item.only_if_followed_by is None
        else _seed_item
        for _seed_item in _seeds_for_language
    )

BUNDLES = {
    key: LanguageBundle(
        key,
        seeds,
        {},
        _JA_SOURCES
        if key == "ja"
        else (
            _LEGACY,
            SourceRef(
                "language-style-baseline",
                "Language style and orthography baseline",
                "docs/language-sources.md",
                "2026-08-10",
            ),
            SourceRef(
                "unicode-cldr-48.2.1",
                "Unicode CLDR",
                "https://cldr.unicode.org/",
                "48.2.1",
            ),
        ),
        coverage="baseline",
    )
    for key, seeds in _SEEDS.items()
}

_MATURE_BUNDLE_ATTRIBUTES = {
    "cs": "CZECH_BUNDLE",
    "de": "GERMAN_BUNDLE",
    "en": "ENGLISH_BUNDLE",
    "es": "SPANISH_BUNDLE",
    "fr": "FRENCH_BUNDLE",
    "it": "ITALIAN_BUNDLE",
    "nl": "DUTCH_BUNDLE",
    "pl": "POLISH_BUNDLE",
    "pt": "PORTUGUESE_BUNDLE",
    "ru": "RUSSIAN_BUNDLE",
    "sv": "SWEDISH_BUNDLE",
    "tr": "TURKISH_BUNDLE",
}


def bundle_for(language: str) -> LanguageBundle:
    """Return the exact base-language bundle."""
    if "_" in language:
        base = language.split("_", 1)[0]
        base_bundle = bundle_for(base)
        return replace(base_bundle, key=language, coverage="locale")
    if language not in BUNDLES and language in _MATURE_BUNDLE_ATTRIBUTES:
        module = import_module(f"abbr2words.languages.{language}")
        BUNDLES[language] = getattr(module, _MATURE_BUNDLE_ATTRIBUTES[language])
    try:
        return BUNDLES[language]
    except KeyError as exc:
        raise KeyError(f"no bundled language data for {language!r}") from exc


__all__ = ["BUNDLES", "bundle_for"]
