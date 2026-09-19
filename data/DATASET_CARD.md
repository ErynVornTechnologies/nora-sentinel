# Dataset card: interpreter bootstrap

## What this is

A **synthetic, machine-generated** dataset produced by `generate_bootstrap.py`. It
exists to prove the training pipeline end to end (train, merge, GGUF export, smoke
test). It is deterministic (seed 42), roughly 200 train / 40 eval examples.

## What this is NOT

It is **not** the production dataset and must not be presented as one. The verdicts
here are templated from a handful of documented patterns. A model trained only on
this will parrot those patterns, not exercise real cross-cultural judgement.

## What the real dataset needs

- Curated cross-cultural behavioural baselines, one per group, not per behaviour.
- **Native review as the gold label**, with reviewer and origin tracked for audit.
- Matched pairs: for every "loud but normal" example, a "same surface, real threat
  markers" counterpart, so the model learns that markers, not volume, carry signal.
- Real breadth of origins, languages, venues, and edge cases.

That native-reviewed dataset is the year of expert work the product turns into a
reusable capability. This file is scaffolding under it.
