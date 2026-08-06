"""Conservative Swedish abbreviation and unit expansion registry."""

from __future__ import annotations

from abbr2words.core import AbbreviationEntry, AbbreviationExpander


class SwedishAbbreviationExpander(AbbreviationExpander):
    """Expand common Swedish abbreviations and guarded references."""

    UNIT_LANGUAGE = "sv"

    def _initialize_abbreviations(self) -> None:
        entries = (
            ("bl.a.", "bland annat"),
            ("dvs.", "det vill säga"),
            ("d.v.s.", "det vill säga"),
            ("t.ex.", "till exempel"),
            ("osv.", "och så vidare"),
            ("m.m.", "med mera"),
            ("m.fl.", "med flera"),
            ("fr.o.m.", "från och med"),
            ("t.o.m.", "till och med"),
            ("s.k.", "så kallad"),
            ("ung.", "ungefär"),
            ("ca.", "cirka"),
            ("mån.", "måndag"),
            ("tis.", "tisdag"),
            ("ons.", "onsdag"),
            ("tors.", "torsdag"),
            ("fre.", "fredag"),
            ("lör.", "lördag"),
            ("sön.", "söndag"),
            ("jan.", "januari"),
            ("feb.", "februari"),
            ("apr.", "april"),
            ("aug.", "augusti"),
            ("sep.", "september"),
            ("okt.", "oktober"),
            ("nov.", "november"),
            ("dec.", "december"),
        )
        for abbreviation, expansion in entries:
            self.add_abbreviation(AbbreviationEntry(abbreviation, expansion))
        for abbreviation, expansion in (("nr", "nummer"), ("sid.", "sida"), ("bil.", "bilaga")):
            self.add_abbreviation(
                AbbreviationEntry(
                    abbreviation,
                    expansion,
                    description="Reference abbreviation",
                    only_if_followed_by=r"\s*\d",
                )
            )


def get_expander(enable_context_detection: bool = True) -> SwedishAbbreviationExpander:
    return SwedishAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    """Retained for compatibility with the package reset hook."""


__all__ = ["SwedishAbbreviationExpander", "get_expander", "reset_expander"]
