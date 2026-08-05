from __future__ import annotations

import pytest

from abbr2words import abbr2words


@pytest.mark.parametrize(
    ("lang", "source", "expected"),
    [
        ("cs", "např.", "například"),
        ("es", "Sr. García", "Señor García"),
        ("fr", "M. Dupont", "monsieur Dupont"),
        ("it", "Dott. Rossi", "Dottor Rossi"),
        ("pt", "Sr. Silva", "Senhor Silva"),
    ],
)
def test_language_smoke(lang: str, source: str, expected: str) -> None:
    assert abbr2words(source, lang=lang) == expected
