"""Conservative Russian abbreviation and unit expansion registry."""

from __future__ import annotations

from abbr2words.core import AbbreviationEntry, AbbreviationExpander


class RussianAbbreviationExpander(AbbreviationExpander):
    """Expand common Russian abbreviations without guessing one-letter forms."""

    UNIT_LANGUAGE = "ru"

    def _initialize_abbreviations(self) -> None:
        multiword = (
            ("т. е.", "то есть"),
            ("и т. д.", "и так далее"),
            ("и т. п.", "и тому подобное"),
            ("ж. д.", "железная дорога"),
        )
        for abbreviation, expansion in multiword:
            self.add_abbreviation(AbbreviationEntry(abbreviation, expansion))

        common = (
            ("и др.", "и другие"),
            ("и пр.", "и прочие"),
            ("напр.", "например"),
            ("проф.", "профессор"),
            ("доц.", "доцент"),
            ("акад.", "академик"),
            ("д-р", "доктор"),
        )
        for abbreviation, expansion in common:
            self.add_abbreviation(AbbreviationEntry(abbreviation, expansion))


        guarded_additions = (
            ("№", "номер", r"\s*\d", "Numeric reference abbreviation"),
            ("г-н", "господин", r"\s+[А-ЯЁA-Z]", "Title abbreviation"),
            ("г-жа", "госпожа", r"\s+[А-ЯЁA-Z]", "Title abbreviation"),
            ("тел.", "телефон", r":?\s*(?:\+7|8)\s*\d", "Phone reference abbreviation"),
            ("рис.", "рисунок", r"\s*(?:\d|№)", "Numeric figure reference abbreviation"),
            ("табл.", "таблица", r"\s*(?:\d|№)", "Numeric table reference abbreviation"),
            ("разд.", "раздел", r"\s*(?:\d|№)", "Numeric section reference abbreviation"),
        )
        for abbreviation, expansion, guard, description in guarded_additions:
            self.add_abbreviation(
                AbbreviationEntry(
                    abbreviation,
                    expansion,
                    description=description,
                    only_if_followed_by=guard,
                )
            )
        self.add_abbreviation(
            AbbreviationEntry(
                "стр.",
                "страница",
                description="Reference abbreviation",
                only_if_followed_by=r"\s*\d",
            )
        )
        for abbreviation, expansion in (("см.", "смотри"), ("ср.", "сравни")):
            self.add_abbreviation(
                AbbreviationEntry(
                    abbreviation,
                    expansion,
                    description="Numeric reference abbreviation",
                    only_if_followed_by=r"\s*(?:\d|№)",
                )
            )
        self.add_abbreviation(
            AbbreviationEntry(
                "им.",
                "имени",
                description="Name-context abbreviation",
                only_if_followed_by=r"\s+[А-ЯЁA-Z]",
            )
        )
        self.add_abbreviation(
            AbbreviationEntry(
                "обл.",
                "область",
                description="Place-context abbreviation",
                only_if_followed_by=r"\s+[А-ЯЁA-Z]",
            )
        )


def get_expander(enable_context_detection: bool = True) -> RussianAbbreviationExpander:
    return RussianAbbreviationExpander(enable_context_detection=enable_context_detection)


def reset_expander() -> None:
    """Retained for compatibility with the package reset hook."""


from abbr2words.language_data.mature import bundle_from_legacy  # noqa: E402
from abbr2words.languages._bundled import BundledLanguageExpander  # noqa: E402

_LegacyRussianAbbreviationExpander = RussianAbbreviationExpander
RUSSIAN_BUNDLE = bundle_from_legacy("ru", _LegacyRussianAbbreviationExpander)


class RussianAbbreviationExpander(BundledLanguageExpander):  # type: ignore[no-redef]
    UNIT_LANGUAGE = "ru"
    BUNDLE = RUSSIAN_BUNDLE


__all__ = ["RussianAbbreviationExpander", "get_expander", "reset_expander"]
