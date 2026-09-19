#!/usr/bin/env python
"""Merge a trained LoRA/QLoRA adapter into its base model for GGUF export.

    python scaffold/merge_adapter.py --config config/train.bootstrap.yaml

Produces a standalone HF model (safetensors) under <output.dir>-merged, which
convert_hf_to_gguf.py then turns into GGUF.

Author: Kamil Nagorski, Erynvorn Technologies.
"""
from __future__ import annotations

import argparse
import os

import yaml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default=None, help="override output dir")
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    base = cfg["model"]["base"]
    adapter_dir = cfg["output"]["dir"]
    out = args.out or (adapter_dir.rstrip("/") + "-merged")
    os.makedirs(out, exist_ok=True)

    print(f"[merge] base={base}")
    print(f"[merge] adapter={adapter_dir}")
    print(f"[merge] out={out}")

    model = AutoModelForCausalLM.from_pretrained(base, torch_dtype=torch.bfloat16)
    model = PeftModel.from_pretrained(model, adapter_dir)
    model = model.merge_and_unload()
    model.save_pretrained(out, safe_serialization=True)

    tok = AutoTokenizer.from_pretrained(adapter_dir if os.path.exists(
        os.path.join(adapter_dir, "tokenizer_config.json")) else base)
    tok.save_pretrained(out)
    print(f"[merge] done -> {out}")


if __name__ == "__main__":
    main()
