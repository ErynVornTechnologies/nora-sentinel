# Training scaffold

A **portable recipe engine**, not a one-off script. The same YAML recipe runs on one desktop GPU for development and on a rented multi-GPU cluster for a real run, without touching the code. This is the "scale it anywhere on earth" piece.

## Design principle

Decouple the recipe from the hardware.

- The **recipe** (what to train, on what data, with which method and hyperparameters) lives in `config/*.yaml`.
- The **engine** (`train.py`) reads the recipe and runs it.
- The **hardware** is chosen at launch time: one GPU here, a cluster there. The recipe does not know or care.

## Environment (sudo-free, reproducible)

This scaffold uses [uv](https://astral.sh/uv) so it stands up the same way on any machine, with no system packages and no root.

```bash
bash scaffold/setup_env.sh
source ~/llm_training/venv/bin/activate
```

`setup_env.sh` installs uv if missing, creates the venv, installs torch (CUDA build) plus the training libraries, and runs a CUDA sanity check.

## Run

```bash
source ~/llm_training/venv/bin/activate
python scaffold/train.py --config config/train.example.yaml
```

On a single 12 GB GPU this trains a 3-4B model with QLoRA comfortably (see the sizing table in the workstation spec). To scale out, launch the same command through `accelerate` or `deepspeed`; the recipe is unchanged.

## What fits on 12 GB

Rule of thumb on an Ada 12 GB card with ~7 GB free for training, gradient checkpointing on, batch 1-2, seq <= 2048:

- 0.5-1.5B: full finetune (8-bit optimizer) or LoRA, comfortable.
- 3-4B: QLoRA (NF4), comfortable. This is the sweet spot.
- 7-9B: QLoRA, tight but possible.
- Above 9B: needs a bigger card or a cluster. This is when the portability of the scaffold earns its keep.

## Export

After training, merge the adapter and export to GGUF for on-prem inference. GGUF export needs `llama.cpp` built with CUDA, which needs `cmake` (a one-time `sudo apt install cmake build-essential`). Kept out of this scaffold on purpose so the training path needs no root.
