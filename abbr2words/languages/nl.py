"""Conservative Dutch abbreviation and unit expansion registry."""

from __future__ import annotations

from abbr2words.core import AbbreviationEntry, AbbreviationExpander


class DutchAbbreviationExpander(AbbreviationExpander):
    """Expand reviewed Dutch abbreviations without guessing ambiguous prose."""

    UNIT_LANGUAGE = "nl"

    def _initialize_abbreviations(self) -> None:
        entries = (
            ("dhr.", "de heer", "Title"),
            ("mevr.", "mevrouw", "Title"),
            ("mw.", "mevrouw", "Title"),
            ("dr.", "doctor", "Academic title"),
            ("prof.", "professor", "Academic title"),
            ("ir.", "ingenieur", "Academic title"),
            ("mr.", "meester", "Academic/legal title"),
            ("bijv.", "bijvoorbeeld", "Common prose abbreviation"),
            ("d.w.z.", "dat wil zeggen", "Common prose abbreviation"),
            ("m.a.w.", "met andere woorden", "Common prose abbreviation"),
            ("enz.", "enzovoort", "Common prose abbreviation"),
            ("e.d.", "en dergelijke", "Common prose abbreviation"),
            ("t.a.v.", "ter attentie van", "Address abbreviation"),
            ("nl.", "namelijk", "Common prose abbreviation"),
            ("a.s.", "aanstaande", "Date abbreviation"),
            ("jl.", "jongstleden", "Date abbreviation"),
            ("ma.", "maandag", "Monday"),
            ("di.", "dinsdag", "Tuesday"),
            ("wo.", "woensdag", "Wednesday"),
            ("do.", "donderdag", "Thursday"),
            ("vr.", "vrijdag", "Friday"),
            ("za.", "zaterdag", "Saturday"),
            ("zo.", "zondag", "Sunday"),
            ("jan.", "januari", "January"),
            ("feb.", "februari", "February"),
            ("mrt.", "maart", "March"),
            ("apr.", "april", "April"),
            ("jun.", "juni", "June"),
            ("jul.", "juli", "July"),
            ("aug.", "augustus", "August"),
            ("sep.", "september", "September"),
            ("okt.", "oktober", "October"),
            ("nov.", "november", "November"),
            ("dec.", "december", "December"),
        )
        for abbreviation, expansion, description in entries:
            self.add_abbreviation(AbbreviationEntry(abbreviation, expansion, description=description))

        for abbreviation, expansion in (("nr.", "nummer"), ("blz.", "bladzijde")):
            self.add_abbreviation(
                AbbreviationEntry(
                    abbreviation,
                    expansion,
                    description="Reference abbreviation",
                    only_if_followed_by=r"\s*\d",
                )
            )
        self.add_abbreviation(
            AbbreviationEntry(
                "p.",
                "pagina",
                case_sensitive=True,
                description="Page reference",
                only_if_followed_by=r"\s*\d",
            )
        )


def get_expander(enable_context_detection: bool = True) -> DutchAbbreviationExpander:
    return DutchAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    """Retained for compatibility with the package reset hook."""


from abbr2words.language_data.mature import bundle_from_legacy  # noqa: E402
from abbr2words.languages._bundled import BundledLanguageExpander  # noqa: E402

_LegacyDutchAbbreviationExpander = DutchAbbreviationExpander
DUTCH_BUNDLE = bundle_from_legacy("nl", _LegacyDutchAbbreviationExpander)


class DutchAbbreviationExpander(BundledLanguageExpander):  # type: ignore[no-redef]
    UNIT_LANGUAGE = "nl"
    BUNDLE = DUTCH_BUNDLE


__all__ = ["DutchAbbreviationExpander", "get_expander", "reset_expander"]
