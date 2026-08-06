"""Use spaCy annotations with abbr2words without coupling the packages."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol, cast

from abbr2words import Expander, TokenAnnotation, abbr2words


class SpacyTokenLike(Protocol):
    """The small spaCy token surface needed by the adapter."""

    idx: int
    pos_: str
    tag_: str

    def __len__(self) -> int: ...


def to_token_annotations(
    tokens: Iterable[SpacyTokenLike],
) -> tuple[TokenAnnotation, ...]:
    """Convert provider tokens to source-aligned annotations."""
    return tuple(
        TokenAnnotation(
            start=token.idx,
            end=token.idx + len(token),
            pos=token.pos_ or None,
            tag=token.tag_ or None,
        )
        for token in tokens
    )


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
    annotations = to_token_annotations(cast(Iterable[SpacyTokenLike], doc))

    print("=== Token annotations ===")
    for token, annotation in zip(doc, annotations, strict=True):
        print(
            f"{token.text!r} [{annotation.start}:{annotation.end}] "
            f"pos={annotation.pos or '-'} tag={annotation.tag or '-'}"
        )

    print("=== Structural guards and unit precedence ===")
    print(abbr2words(text, lang="en", annotations=annotations))

    custom_text = "Ref. was filed."
    custom_doc = nlp(custom_text)
    custom_annotations = to_token_annotations(cast(Iterable[SpacyTokenLike], custom_doc))
    custom = Expander("en")
    custom.add("Ref.", "Reference", only_if_pos="NOUN", not_if_pos="PROPN")
    print("=== Custom POS-guarded entry ===")
    print(custom.expand(custom_text, annotations=custom_annotations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
