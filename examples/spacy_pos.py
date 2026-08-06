"""Use spaCy annotations with abbr2words without coupling the packages."""

from __future__ import annotations

from abbr2words import TokenAnnotation, abbr2words


def main() -> int:
    try:
        import spacy
    except ImportError as exc:
        raise SystemExit(
            "Install spaCy separately to run this example: python -m pip install spacy"
        ) from exc

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError as exc:
        raise SystemExit(
            "Install the English spaCy pipeline separately: python -m spacy download en_core_web_sm"
        ) from exc

    text = "They wandered around in. The board is 10 in. wide."
    doc = nlp(text)
    annotations = tuple(
        TokenAnnotation(
            start=token.idx,
            end=token.idx + len(token),
            pos=token.pos_ or None,
            tag=token.tag_ or None,
        )
        for token in doc
    )

    print(abbr2words(text, lang="en", annotations=annotations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
