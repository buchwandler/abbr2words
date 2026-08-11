from __future__ import annotations

import pytest

from abbr2words import abbr2words


@pytest.mark.parametrize(
    ("lang", "source", "expected"),
    [
        ("cs", "např.", "například."),
        ("es", "Sr. García", "Señor García"),
        ("fr", "M. Dupont", "Monsieur Dupont"),
        ("it", "Dott. Rossi", "Dottor Rossi"),
        ("pt", "Sr. Silva", "Senhor Silva"),
    ],
)
def test_language_smoke(lang: str, source: str, expected: str) -> None:
    assert abbr2words(source, lang=lang) == expected


@pytest.mark.parametrize(
    ("lang", "source", "expected", "neighbor"),
    [
        ("am", "ቁ. 12", "ቁጥር 12", "ቁ. text"),
        ("ar", "ص. 12", "صفحة 12", "ص. text"),
        ("az", "səh. 12", "səhifə 12", "səh. text"),
        ("be", "с. 12", "старонка 12", "с. text"),
        ("bn", "পৃ. 12", "পৃষ্ঠা 12", "পৃ. text"),
        ("ca", "pàg. 12", "pàgina 12", "pàg. text"),
        ("ce", "стр. 12", "страница 12", "стр. text"),
        ("cy", "tud. 12", "tudalen 12", "tud. text"),
        ("da", "s. 12", "side 12", "s. text"),
        ("eo", "p. 12", "paĝo 12", "p. text"),
        ("fa", "ص. 12", "صفحه 12", "ص. text"),
        ("fi", "s. 12", "sivu 12", "s. text"),
        ("he", "עמ׳ 12", "עמוד 12", "עמ׳ text"),
        ("hi", "पृ. 12", "पृष्ठ 12", "पृ. text"),
        ("hu", "o. 12", "oldal 12", "o. text"),
        ("hy", "էջ. 12", "էջ 12", "էջ. text"),
        ("id", "hal. 12", "halaman 12", "hal. text"),
        ("is", "bls. 12", "blaðsíða 12", "bls. text"),
        ("ja", "頁 12", "ページ 12", "頁 text"),
        ("kn", "ಪು. 12", "ಪುಟ 12", "ಪು. text"),
        ("ko", "p. 12", "페이지 12", "p. text"),
        ("kz", "бет. 12", "бет 12", "бет. text"),
        ("lt", "p. 12", "puslapis 12", "p. text"),
        ("lv", "lpp. 12", "lappuse 12", "lpp. text"),
        ("mn", "х. 12", "хуудас 12", "х. text"),
        ("no", "s. 12", "side 12", "s. text"),
        ("ro", "pag. 12", "pagină 12", "pag. text"),
        ("sk", "s. 12", "strana 12", "s. text"),
        ("sl", "str. 12", "stran 12", "str. text"),
        ("sr", "стр. 12", "страна 12", "стр. text"),
        ("te", "పు. 12", "పుట 12", "పు. text"),
        ("tet", "pág. 12", "pájina 12", "pág. text"),
        ("tg", "саҳ. 12", "саҳифа 12", "саҳ. text"),
        ("th", "ม. test", "มหาวิทยาลัย test", "มห. text"),
        ("uk", "стор. 12", "сторінка 12", "стор. text"),
        ("vi", "tr. 12", "trang 12", "tr. text"),
        ("zh", "页 12", "页码 12", "页 text"),
    ],
)
def test_baseline_languages_have_guarded_meaningful_transformations(
    lang: str, source: str, expected: str, neighbor: str
) -> None:
    assert abbr2words(source, lang=lang) == expected
    assert abbr2words(neighbor, lang=lang) == neighbor
