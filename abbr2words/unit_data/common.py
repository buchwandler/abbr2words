"""Conservative common-unit inventories for newly added languages."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from . import entries, register


@dataclass(frozen=True, slots=True)
class UnitDefinition:
    """Language-neutral unit identity used to build a localized entry."""

    canonical_id: str
    symbols: tuple[str, ...]
    canonical_symbol: str
    requires_separator: bool = False


COMMON_UNIT_DEFINITIONS = (
    UnitDefinition("duration-second", ("s", "sec"), "s"),
    UnitDefinition("duration-minute", ("min",), "min"),
    UnitDefinition("duration-hour", ("h", "hr"), "h"),
    UnitDefinition("duration-day", ("d",), "d"),
    UnitDefinition("length-millimeter", ("mm",), "mm"),
    UnitDefinition("length-centimeter", ("cm",), "cm"),
    UnitDefinition("length-meter", ("m",), "m"),
    UnitDefinition("length-kilometer", ("km",), "km"),
    UnitDefinition("volume-milliliter", ("mL", "ml"), "mL"),
    UnitDefinition("volume-liter", ("L", "l"), "L"),
    UnitDefinition("mass-microgram", ("µg", "μg", "ug"), "µg"),
    UnitDefinition("mass-milligram", ("mg",), "mg"),
    UnitDefinition("mass-gram", ("g",), "g"),
    UnitDefinition("mass-kilogram", ("kg",), "kg"),
    UnitDefinition("mass-tonne", ("t",), "t"),
    UnitDefinition("temperature-kelvin", ("K",), "K", requires_separator=True),
    UnitDefinition("temperature-celsius", ("°C", "℃"), "°C"),
    UnitDefinition("temperature-fahrenheit", ("°F", "℉"), "°F"),
    UnitDefinition("speed-meter-per-second", ("m/s",), "m/s"),
    UnitDefinition("speed-kilometer-per-hour", ("km/h",), "km/h"),
    UnitDefinition("speed-mile-per-hour", ("mph",), "mph"),
    UnitDefinition("pressure-pascal", ("Pa",), "Pa"),
    UnitDefinition("pressure-kilopascal", ("kPa",), "kPa"),
    UnitDefinition("pressure-atmosphere", ("atm",), "atm"),
    UnitDefinition("data-byte", ("B",), "B", requires_separator=True),
    UnitDefinition("data-kilobyte", ("kB",), "kB"),
    UnitDefinition("data-megabyte", ("MB",), "MB"),
    UnitDefinition("data-gigabyte", ("GB",), "GB"),
    UnitDefinition("fuel-consumption-liter-per-100-kilometer", ("L/100km",), "L/100km"),
    UnitDefinition("flow-cubic-meter-per-second", ("m³/s", "m3/s"), "m³/s"),
    UnitDefinition("area-square-millimeter", ("mm²", "mm2"), "mm²"),
    UnitDefinition("area-square-centimeter", ("cm²", "cm2"), "cm²"),
    UnitDefinition("area-square-meter", ("m²", "m2"), "m²"),
    UnitDefinition("area-square-kilometer", ("km²", "km2"), "km²"),
    UnitDefinition("area-hectare", ("ha",), "ha"),
    UnitDefinition("volume-cubic-millimeter", ("mm³", "mm3"), "mm³"),
    UnitDefinition("volume-cubic-centimeter", ("cm³", "cm3"), "cm³"),
    UnitDefinition("volume-cubic-meter", ("m³", "m3"), "m³"),
)

UNIT_LABELS = {
    "ar": {
        "mass-gram": "غرام",
        "mass-kilogram": "كيلوغرام",
        "length-kilometer": "كيلومتر",
        "duration-minute": "دقيقة",
        "temperature-celsius": "درجة مئوية",
    },
    "am": {
        "mass-gram": "ግራም",
        "mass-kilogram": "ኪሎ ግራም",
        "length-kilometer": "ኪሎሜትር",
        "duration-minute": "ደቂቃ",
    },
    "az": {
        "mass-gram": "qram",
        "mass-kilogram": "kiloqram",
        "length-kilometer": "kilometr",
        "duration-minute": "dəqiqə",
        "temperature-celsius": "Selsi dərəcəsi",
    },
    "be": {
        "mass-gram": "грам",
        "mass-kilogram": "кілаграм",
        "length-kilometer": "кіламетр",
        "duration-minute": "хвіліна",
        "temperature-celsius": "градус Цэльсія",
    },
    "bn": {
        "mass-gram": "গ্রাম",
        "mass-kilogram": "কিলোগ্রাম",
        "length-kilometer": "কিলোমিটার",
        "duration-minute": "মিনিট",
    },
    "ca": {
        "mass-gram": "gram",
        "mass-kilogram": "quilogram",
        "length-kilometer": "quilòmetre",
        "duration-minute": "minut",
        "temperature-celsius": "grau Celsius",
    },
    "ce": {
        "mass-gram": "грамм",
        "mass-kilogram": "килограмм",
        "length-kilometer": "километр",
        "duration-minute": "минут",
    },
    "cy": {
        "mass-gram": "gram",
        "mass-kilogram": "cilogram",
        "length-kilometer": "cilometr",
        "duration-minute": "munud",
    },
    "da": {
        "mass-gram": "gram",
        "mass-kilogram": "kilogram",
        "length-kilometer": "kilometer",
        "duration-minute": "minut",
    },
    "eo": {
        "mass-gram": "gramo",
        "mass-kilogram": "kilogramo",
        "length-kilometer": "kilometro",
        "duration-minute": "minuto",
    },
    "fa": {
        "mass-gram": "گرم",
        "mass-kilogram": "کیلوگرم",
        "length-kilometer": "کیلومتر",
        "duration-minute": "دقیقه",
        "temperature-celsius": "درجهٔ سلسیوس",
    },
    "fi": {
        "mass-gram": "gramma",
        "mass-kilogram": "kilogramma",
        "length-kilometer": "kilometri",
        "duration-minute": "minuutti",
    },
    "he": {
        "mass-gram": "גרם",
        "mass-kilogram": "קילוגרם",
        "length-kilometer": "קילומטר",
        "duration-minute": "דקה",
    },
    "hi": {
        "mass-gram": "ग्राम",
        "mass-kilogram": "किलोग्राम",
        "length-kilometer": "किलोमीटर",
        "duration-minute": "मिनट",
    },
    "hu": {
        "mass-gram": "gramm",
        "mass-kilogram": "kilogramm",
        "length-kilometer": "kilométer",
        "duration-minute": "perc",
    },
    "hy": {
        "mass-gram": "գրամ",
        "mass-kilogram": "կիլոգրամ",
        "length-kilometer": "կիլոմետր",
        "duration-minute": "րոպե",
    },
    "id": {
        "mass-gram": "gram",
        "mass-kilogram": "kilogram",
        "length-kilometer": "kilometer",
        "duration-minute": "menit",
    },
    "is": {
        "mass-gram": "gramm",
        "mass-kilogram": "kílógramm",
        "length-kilometer": "kílómetri",
        "duration-minute": "mínúta",
    },
    "ja": {
        "duration-second": "秒",
        "duration-minute": "分",
        "duration-hour": "時間",
        "duration-day": "日",
        "length-millimeter": "ミリメートル",
        "length-centimeter": "センチメートル",
        "length-meter": "メートル",
        "length-kilometer": "キロメートル",
        "volume-milliliter": "ミリリットル",
        "volume-liter": "リットル",
        "mass-microgram": "マイクログラム",
        "mass-milligram": "ミリグラム",
        "mass-gram": "グラム",
        "mass-kilogram": "キログラム",
        "mass-tonne": "トン",
        "temperature-kelvin": "ケルビン",
        "temperature-celsius": "セルシウス度",
        "temperature-fahrenheit": "華氏度",
        "speed-meter-per-second": "メートル毎秒",
        "speed-kilometer-per-hour": "キロメートル毎時",
        "speed-mile-per-hour": "マイル毎時",
        "pressure-pascal": "パスカル",
        "pressure-kilopascal": "キロパスカル",
        "pressure-atmosphere": "気圧",
        "data-byte": "バイト",
        "data-kilobyte": "キロバイト",
        "data-megabyte": "メガバイト",
        "data-gigabyte": "ギガバイト",
        "fuel-consumption-liter-per-100-kilometer": "リットル毎100キロメートル",
        "flow-cubic-meter-per-second": "立方メートル毎秒",
        "area-square-millimeter": "平方ミリメートル",
        "area-square-centimeter": "平方センチメートル",
        "area-square-meter": "平方メートル",
        "area-square-kilometer": "平方キロメートル",
        "area-hectare": "ヘクタール",
        "volume-cubic-millimeter": "立方ミリメートル",
        "volume-cubic-centimeter": "立方センチメートル",
        "volume-cubic-meter": "立方メートル",
    },
    "kn": {
        "mass-gram": "ಗ್ರಾಂ",
        "mass-kilogram": "ಕಿಲೋಗ್ರಾಂ",
        "length-kilometer": "ಕಿಲೋಮೀಟರ್",
        "duration-minute": "ನಿಮಿಷ",
    },
    "ko": {
        "duration-second": "초",
        "duration-minute": "분",
        "duration-hour": "시간",
        "duration-day": "일",
        "length-millimeter": "밀리미터",
        "length-centimeter": "센티미터",
        "length-meter": "미터",
        "length-kilometer": "킬로미터",
        "volume-milliliter": "밀리리터",
        "volume-liter": "리터",
        "mass-microgram": "마이크로그램",
        "mass-milligram": "밀리그램",
        "mass-gram": "그램",
        "mass-kilogram": "킬로그램",
        "mass-tonne": "메트릭 톤",
        "temperature-kelvin": "켈빈",
        "temperature-celsius": "섭씨",
        "temperature-fahrenheit": "화씨",
        "speed-meter-per-second": "미터 매 초",
        "speed-kilometer-per-hour": "시간당 킬로미터",
        "speed-mile-per-hour": "시간당 마일",
        "pressure-pascal": "파스칼",
        "pressure-kilopascal": "킬로파스칼",
        "pressure-atmosphere": "기압",
        "data-byte": "바이트",
        "data-kilobyte": "킬로바이트",
        "data-megabyte": "메가바이트",
        "data-gigabyte": "기가바이트",
        "fuel-consumption-liter-per-100-kilometer": "100킬로미터당 리터",
        "flow-cubic-meter-per-second": "초당 세제곱미터",
        "area-square-millimeter": "제곱밀리미터",
        "area-square-centimeter": "제곱센티미터",
        "area-square-meter": "제곱미터",
        "area-square-kilometer": "제곱킬로미터",
        "area-hectare": "헥타르",
        "volume-cubic-millimeter": "세제곱밀리미터",
        "volume-cubic-centimeter": "세제곱센티미터",
        "volume-cubic-meter": "세제곱미터",
    },
    "kz": {
        "mass-gram": "грамм",
        "mass-kilogram": "килограмм",
        "length-kilometer": "километр",
        "duration-minute": "минут",
    },
    "lt": {
        "mass-gram": "gramas",
        "mass-kilogram": "kilogramas",
        "length-kilometer": "kilometras",
        "duration-minute": "minutė",
    },
    "lv": {
        "mass-gram": "grams",
        "mass-kilogram": "kilograms",
        "length-kilometer": "kilometrs",
        "duration-minute": "minūte",
    },
    "mn": {
        "mass-gram": "грамм",
        "mass-kilogram": "килограмм",
        "length-kilometer": "километр",
        "duration-minute": "минут",
    },
    "no": {
        "mass-gram": "gram",
        "mass-kilogram": "kilogram",
        "length-kilometer": "kilometer",
        "duration-minute": "minutt",
    },
    "ro": {
        "mass-gram": "gram",
        "mass-kilogram": "kilogram",
        "length-kilometer": "kilometru",
        "duration-minute": "minut",
    },
    "sk": {
        "mass-gram": "gram",
        "mass-kilogram": "kilogram",
        "length-kilometer": "kilometer",
        "duration-minute": "minúta",
    },
    "sl": {
        "mass-gram": "gram",
        "mass-kilogram": "kilogram",
        "length-kilometer": "kilometer",
        "duration-minute": "minuta",
    },
    "sr": {
        "mass-gram": "грам",
        "mass-kilogram": "килограм",
        "length-kilometer": "километар",
        "duration-minute": "минут",
    },
    "te": {
        "mass-gram": "గ్రాము",
        "mass-kilogram": "కిలోగ్రాము",
        "length-kilometer": "కిలోమీటరు",
        "duration-minute": "నిమిషం",
    },
    "tet": {
        "mass-gram": "grama",
        "mass-kilogram": "kilograma",
        "length-kilometer": "kilómetru",
        "duration-minute": "minutu",
    },
    "tg": {
        "mass-gram": "грамм",
        "mass-kilogram": "килограмм",
        "length-kilometer": "километр",
        "duration-minute": "дақиқа",
    },
    "th": {
        "mass-gram": "กรัม",
        "mass-kilogram": "กิโลกรัม",
        "length-kilometer": "กิโลเมตร",
        "duration-minute": "นาที",
    },
    "uk": {
        "mass-gram": "грам",
        "mass-kilogram": "кілограм",
        "length-kilometer": "кілометр",
        "duration-minute": "хвилина",
    },
    "vi": {
        "mass-gram": "gam",
        "mass-kilogram": "kilôgam",
        "length-kilometer": "kilômét",
        "duration-minute": "phút",
    },
    "zh": {
        "mass-gram": "克",
        "mass-kilogram": "千克",
        "length-kilometer": "千米",
        "duration-minute": "分钟",
        "temperature-celsius": "摄氏度",
    },
}

UNIT_TEMPLATES = {
    "ja": {
        "temperature-celsius": "摂氏 {value} 度",
        "temperature-fahrenheit": "華氏 {value} 度",
        "speed-meter-per-second": "秒速 {value} メートル",
        "speed-kilometer-per-hour": "時速 {value} キロメートル",
        "speed-mile-per-hour": "時速 {value} マイル",
    },
    "ko": {
        "temperature-celsius": "섭씨 {value}도",
        "temperature-fahrenheit": "화씨 {value}도",
        "speed-meter-per-second": "초속 {value}미터",
        "speed-kilometer-per-hour": "시속 {value}킬로미터",
        "speed-mile-per-hour": "시속 {value}마일",
        "fuel-consumption-liter-per-100-kilometer": "100킬로미터당 {value}리터",
        "flow-cubic-meter-per-second": "초당 {value}세제곱미터",
    },
}


def common_unit_entries(language: str, *, expansion_prefix: str = "") -> tuple[object, ...]:
    """Build a stable common inventory using the public unit model."""
    from abbr2words.units import UnitEntry

    prefix = f"{expansion_prefix} " if expansion_prefix else ""
    labels = UNIT_LABELS.get(language, {})
    templates = UNIT_TEMPLATES.get(language, {})
    return tuple(
        UnitEntry(
            symbols=definition.symbols,
            expansion=f"{prefix}{labels.get(definition.canonical_id, definition.canonical_symbol)}",
            description=f"Reviewed common unit ({language})",
            canonical_symbol=definition.canonical_symbol,
            canonical_id=definition.canonical_id,
            requires_separator=definition.requires_separator,
            quantity_template=templates.get(definition.canonical_id),
        )
        for definition in COMMON_UNIT_DEFINITIONS
    )


def register_common_units(language: str, *, expansion_prefix: str = "") -> None:
    """Register one external base inventory exactly once."""
    if entries(language) is not None:
        return
    register(language, common_unit_entries(language, expansion_prefix=expansion_prefix))


def locale_currency(symbol: str | tuple[str, ...], expansion: str, canonical_id: str) -> object:
    """Build a locale-specific ISO-4217-aware currency identity."""
    from abbr2words.units import UnitEntry

    symbols = (symbol,) if isinstance(symbol, str) else symbol
    return UnitEntry(
        symbols=symbols,
        expansion=expansion,
        description="Reviewed locale currency identity",
        canonical_symbol=symbols[0],
        canonical_id=canonical_id,
        category="currency",
        quantity_position="both",
    )


def register_locale_units(language: str, base: str, extra: Iterable[object] = ()) -> None:
    """Register an effective locale inventory inheriting a bundled base."""
    from abbr2words.units import UnitEntry, unit_entries

    merged = list(unit_entries(base))
    for item in extra:
        if not isinstance(item, UnitEntry):
            raise TypeError("locale unit entries must be UnitEntry values")
        symbols = set(getattr(item, "symbols", ()))
        merged = [entry for entry in merged if not symbols.intersection(entry.symbols)]
        merged.append(item)
    register(language, tuple(merged))


__all__ = [
    "COMMON_UNIT_DEFINITIONS",
    "UnitDefinition",
    "UNIT_LABELS",
    "UNIT_TEMPLATES",
    "common_unit_entries",
    "locale_currency",
    "register_common_units",
    "register_locale_units",
]
