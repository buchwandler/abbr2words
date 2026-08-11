"""Conservative Polish abbreviation and unit expansion registry."""

from __future__ import annotations

from abbr2words.core import AbbreviationEntry, AbbreviationExpander

_TITLE_AFTER = r"\s+[A-ZĄĆĘŁŃÓŚŹŻ]"


class PolishAbbreviationExpander(AbbreviationExpander):
    """Expand reviewed Polish abbreviations while guarding short forms."""

    UNIT_LANGUAGE = "pl"

    def _initialize_abbreviations(self) -> None:
        titles = (
            ("dr", "doktor"),
            ("prof.", "profesor"),
            ("mgr", "magister"),
            ("inż.", "inżynier"),
            ("lek.", "lekarz"),
            ("gen.", "generał"),
        )
        for abbreviation, expansion in titles:
            self.add_abbreviation(
                AbbreviationEntry(
                    abbreviation,
                    expansion,
                    description="Title before a name",
                    only_if_followed_by=_TITLE_AFTER,
                )
            )

        common = (
            ("św.", "święty"),
            ("np.", "na przykład"),
            ("itd.", "i tak dalej"),
            ("itp.", "i tym podobne"),
            ("tj.", "to jest"),
            ("tzn.", "to znaczy"),
            ("m.in.", "między innymi"),
            ("zob.", "zobacz"),
            ("ul.", "ulica"),
            ("al.", "aleja"),
        )
        for abbreviation, expansion in common:
            self.add_abbreviation(AbbreviationEntry(abbreviation, expansion))

        for abbreviation, expansion in (("nr", "numer"), ("str.", "strona"), ("s.", "strona")):
            self.add_abbreviation(
                AbbreviationEntry(
                    abbreviation,
                    expansion,
                    description="Reference abbreviation",
                    only_if_followed_by=r"\s*\d",
                )
            )
        self.add_abbreviation(
            AbbreviationEntry("godz.", "godzina", only_if_followed_by=r"\s*\d")
        )
        self.add_abbreviation(
            AbbreviationEntry("r.", "rok", only_if_preceded_by=r"\b\d{4}\s*$")
        )
        for abbreviation, expansion in (
            ("pon.", "poniedziałek"),
            ("wt.", "wtorek"),
            ("śr.", "środa"),
            ("czw.", "czwartek"),
            ("pt.", "piątek"),
            ("sob.", "sobota"),
            ("niedz.", "niedziela"),
            ("sty.", "styczeń"),
            ("lut.", "luty"),
            ("mar.", "marzec"),
            ("kwi.", "kwiecień"),
            ("cze.", "czerwiec"),
            ("lip.", "lipiec"),
            ("sie.", "sierpień"),
            ("wrz.", "wrzesień"),
            ("paź.", "październik"),
            ("lis.", "listopad"),
            ("gru.", "grudzień"),
        ):
            self.add_abbreviation(AbbreviationEntry(abbreviation, expansion))


def get_expander(enable_context_detection: bool = True) -> PolishAbbreviationExpander:
    return PolishAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    """Retained for compatibility with the package reset hook."""


from abbr2words.language_data.mature import bundle_from_legacy  # noqa: E402
from abbr2words.languages._bundled import BundledLanguageExpander  # noqa: E402

_LegacyPolishAbbreviationExpander = PolishAbbreviationExpander
POLISH_BUNDLE = bundle_from_legacy("pl", _LegacyPolishAbbreviationExpander)


class PolishAbbreviationExpander(BundledLanguageExpander):  # type: ignore[no-redef]
    UNIT_LANGUAGE = "pl"
    BUNDLE = POLISH_BUNDLE


__all__ = ["PolishAbbreviationExpander", "get_expander", "reset_expander"]
