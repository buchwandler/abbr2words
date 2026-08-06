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
the token span in the original source. `pos` is an optional uppercase coarse
Universal POS label such as `ADP`, `NOUN`, `PROPN`, `NUM`, or `PUNCT`; `tag` can
hold a provider-specific fine-grained label. Whitespace gaps are allowed, but
token spans may not overlap. Labels are normalized to uppercase and empty labels
become `None`.

A bare POS vector is not accepted because it cannot identify which source
characters belong to each label. Missing annotations or missing POS labels
preserve the normal structural behavior: POS guards refine a decision only when
usable lexical POS evidence is present, so incomplete evidence fails open.

## What POS changes today

POS constraints are opt-in and currently affect custom entries only. No bundled
registry entry currently requires a POS label. Do not add a registry-wide POS
constraint without corpus evidence for the relevant language and tagger.

The `tag` field is retained for adapters and future extensions, but the current
guard matcher evaluates only coarse `pos` labels.

## spaCy adapter

spaCy exposes the required offsets and labels directly on its tokens:

```python
import spacy

from abbr2words import TokenAnnotation, abbr2words

nlp = spacy.load("en_core_web_sm")
text = "They wandered around in. The board is 10 in. wide."
doc = nlp(text)
from examples.spacy_pos import to_token_annotations

annotations = to_token_annotations(doc)
print(abbr2words(text, annotations=annotations))
```

Run `python examples/spacy_pos.py` for a complete lazy-import example. A
trained spaCy pipeline component is required for POS predictions; tokenization
alone does not populate `token.pos_`.

## POS guard precedence and limitations

Custom entries may use `only_if_pos="NOUN"`,
`only_if_pos={"NOUN", "PROPN"}`, or `not_if_pos="ADP"`. The decision order is:

1. source offsets, regex boundaries, and structural guards;
2. reviewed numeric-unit matching;
3. POS deny constraints (`not_if_pos`);
4. POS allow constraints (`only_if_pos`);
5. context selection and replacement conflict resolution.

Punctuation, `SPACE`, and missing POS labels do not provide lexical evidence.
When both POS constraints match, the deny constraint wins.

Reviewed numeric unit expressions remain authoritative. For example, a general
tagger labeling the `in` in `10 in.` as `ADP` does not prevent the result
`10 inch`. The sentence-final `in.` example demonstrates structural guarding and
annotation alignment; it does not claim that POS caused the decision.

The adapter helper in `examples/spacy_pos.py` accepts any iterable exposing
spaCy's `idx`, `pos_`, `tag_`, and token length attributes. A trained spaCy
pipeline component is required for POS predictions; tokenization alone does not
populate `token.pos_`.
