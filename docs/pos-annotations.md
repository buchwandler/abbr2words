# External POS annotations

`abbr2words` accepts optional provider-neutral token annotations for
applications that already tokenize and tag text. The package remains
dependency-free: it does not install, import, or decode any NLP provider.

## TokenAnnotation

```python
from abbr2words import TokenAnnotation, abbr2words

text = "They wandered around in. The board is 10 in. wide."
annotations = [
    TokenAnnotation(0, 4, "PRON"),
    # ...one source-aligned annotation for each token...
]
result = abbr2words(text, annotations=annotations)
```

`start` and `end` are Python character offsets, and `text[start:end]` must be
the token span. `pos` is an optional uppercase coarse Universal POS label such
as `ADP`, `NOUN`, `PROPN`, `NUM`, or `PUNCT`; `tag` can hold a provider-specific
fine-grained label. Whitespace gaps are allowed, but token spans may not
overlap. Labels are normalized to uppercase and empty labels become `None`.

A bare POS vector is not accepted because it cannot identify which source
characters belong to each label. Missing annotations or missing POS labels
preserve the normal structural behavior.

## spaCy adapter

spaCy exposes the required offsets and labels directly on its tokens:

```python
import spacy

from abbr2words import TokenAnnotation, abbr2words

nlp = spacy.load("en_core_web_sm")
text = "They wandered around in. The board is 10 in. wide."
doc = nlp(text)
annotations = tuple(
    TokenAnnotation(token.idx, token.idx + len(token), token.pos_ or None, token.tag_ or None)
    for token in doc
)
print(abbr2words(text, annotations=annotations))
```

Run `python examples/spacy_pos.py` for a complete lazy-import example. A
trained spaCy pipeline component is required for POS predictions; tokenization
alone does not populate `token.pos_`.

## POS guard precedence and limitations

Custom entries may use `only_if_pos={"NOUN", "PROPN"}` or
`not_if_pos={"ADP"}`. Existing regex boundary, initialism, and structural
guards run first. POS constraints are then evaluated only when configured and
usable, followed by context selection. Punctuation and missing POS labels do
not provide lexical evidence.

Reviewed numeric unit expressions remain authoritative. For example, a general
tagger labeling the `in` in `10 in.` as `ADP` does not prevent the result
`10 inch`. POS is an opt-in signal, not an infallible global veto.
