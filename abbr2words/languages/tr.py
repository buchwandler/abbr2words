"""Restricted Turkish abbreviation and unit expansion registry."""

from __future__ import annotations

from abbr2words.core import AbbreviationEntry, AbbreviationExpander


class TurkishAbbreviationExpander(AbbreviationExpander):
    """Expand explicitly cased Turkish abbreviations conservatively."""

    UNIT_LANGUAGE = "tr"

    def _initialize_abbreviations(self) -> None:
        entries = (
            ("Dr.", "doktor"),
            ("Prof.", "profesör"),
            ("Alb.", "albay"),
            ("Cad.", "cadde"),
            ("Sok.", "sokak"),
            ("vb.", "ve benzeri"),
            ("vs.", "vesaire"),
            ("bk.", "bakınız"),
            ("ör.", "örnek"),
            ("vd.", "ve diğerleri"),
            ("çev.", "çeviren"),
            ("haz.", "hazırlayan"),
        )
        for abbreviation, expansion in entries:
            self.add_abbreviation(
                AbbreviationEntry(abbreviation, expansion, case_sensitive=True)
            )

        for abbreviation, expansion in (("s.", "sayfa"), ("No.", "numara")):
            self.add_abbreviation(
                AbbreviationEntry(
                    abbreviation,
                    expansion,
                    case_sensitive=True,
                    description="Reference abbreviation",
                    only_if_followed_by=r"\s*\d",
                )
            )
        self.add_abbreviation(
            AbbreviationEntry(
                "yy.",
                "yüzyıl",
                case_sensitive=True,
                description="Century abbreviation",
                only_if_followed_by=r"\s*(?:\d|[IVXLCDM])",
            )
        )


def get_expander(enable_context_detection: bool = True) -> TurkishAbbreviationExpander:
    return TurkishAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    """Retained for compatibility with the package reset hook."""


__all__ = ["TurkishAbbreviationExpander", "get_expander", "reset_expander"]
