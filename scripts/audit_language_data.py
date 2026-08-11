"""Audit checked-in language bundle invariants without network access."""

from __future__ import annotations

import argparse
import sys

from abbr2words.language_data import bundle_for


def audit(languages: list[str]) -> list[str]:
    errors: list[str] = []
    for language in languages:
        try:
            bundle = bundle_for(language)
        except KeyError as exc:
            errors.append(str(exc))
            continue
        source_ids = {source.id for source in bundle.sources}
        seen: set[str] = set()
        for seed in bundle.abbreviations:
            key = seed.abbreviation.casefold()
            if key in seen:
                if not seed.review_note.startswith("Behavior-neutral migration snapshot"):
                    errors.append(f"{language}: duplicate spelling {seed.abbreviation!r}")
            seen.add(key)
            if seed.abbreviation in seed.aliases:
                errors.append(f"{language}: primary spelling is also an alias")
            if not seed.source_ids:
                errors.append(f"{language}: {seed.abbreviation!r} has no source IDs")
            if not set(seed.source_ids) <= source_ids:
                errors.append(f"{language}: {seed.abbreviation!r} references an unknown source")
            if (
                seed.abbreviation == seed.expansion
                and not seed.context_expansions
                and not seed.review_note.startswith("Behavior-neutral migration snapshot")
            ):
                errors.append(f"{language}: identity rule {seed.abbreviation!r} is not allowed")
            if (
                seed.boundary == "custom"
                and not (seed.left_boundary or seed.right_boundary)
                and not seed.review_note
            ):
                errors.append(f"{language}: custom boundary lacks a rationale/policy")
        if not bundle.sources:
            errors.append(f"{language}: bundle has no sources")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    from abbr2words import supported_languages

    parser.add_argument(
        "languages", nargs="*", default=list(supported_languages(include_locales=False))
    )
    args = parser.parse_args()
    errors = audit(args.languages)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"audited {len(args.languages)} language bundles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
