# Data

The dataset is the moat. Compute is rentable; a curated cross-cultural
behavioural baseline with native review is not. This is where the year of
expert work lives, and what makes the interpreter defensible.

## Format

Chat-ML JSONL. One example per line. Each example teaches the interpreter to map
a structured event descriptor to a verdict with explicit cultural reasoning.

```json
{"messages": [
  {"role": "system", "content": "You are a cross-cultural security interpreter..."},
  {"role": "user", "content": "{event descriptor as JSON}"},
  {"role": "assistant", "content": "{verdict as JSON: threat_level, action, cultural_reasoning, confidence}"}
]}
```

Files the scaffold expects (see `config/train.example.yaml`):

- `data/interpreter.train.jsonl`
- `data/interpreter.eval.jsonl`

A tiny illustrative sample is in `interpreter.sample.jsonl`.

## Curation guidance

- **Baselines per group, not per behaviour.** The label depends on who is doing
  it. The same descriptor gets different verdicts for different `inferred_origin`.
- **Balance the classes.** For every "loud but normal" example, include a
  matched "same surface, real threat markers" example, so the model learns that
  markers, not volume, carry the signal.
- **Native review is the gold label.** A verdict is only as good as the reviewer
  who set it. Track reviewer and origin so quality is auditable.
- **Keep reasoning explicit.** The assistant output always includes
  `cultural_reasoning`. That is what an operator and an auditor read.
- **Separate or tag languages.** Keep Polish and English (and Arabic, etc.)
  either separated or clearly tagged, depending on the target model's purpose.

## Where raw material can come from

Behavioural norm references, region and language corpora, and synthetic
descriptor/verdict pairs generated from documented norms and then corrected by
native reviewers. Copy prepared JSONL into `data/` on fast local storage before
training; do not stream training data across a slow mount.
