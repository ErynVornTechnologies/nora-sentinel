#!/usr/bin/env python
"""NORA Sentinel - config-driven QLoRA/LoRA trainer.

Reads a YAML recipe (see config/train.example.yaml) and runs it. The same file
runs on one GPU or, launched via accelerate/deepspeed, on a cluster.

    python scaffold/train.py --config config/train.example.yaml

Author: Kamil Nagorski, Erynvorn Technologies.
"""
from __future__ import annotations

import argparse
import os
import sys

import yaml


def die(msg: str) -> None:
    print(f"[train] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build_model_and_tokenizer(cfg: dict):
    import torch
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
                              BitsAndBytesConfig)
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    m, meth = cfg["model"], cfg["method"]
    dtype = getattr(torch, meth.get("compute_dtype", "bfloat16"))

    quant_config = None
    if meth["type"] == "qlora":
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type=meth.get("quant", "nf4"),
            bnb_4bit_use_double_quant=meth.get("double_quant", True),
            bnb_4bit_compute_dtype=dtype,
        )

    tok = AutoTokenizer.from_pretrained(
        m["base"], trust_remote_code=m.get("trust_remote_code", False))
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        m["base"],
        quantization_config=quant_config,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=m.get("trust_remote_code", False),
    )

    if meth["type"] in ("qlora", "lora"):
        if meth["type"] == "qlora":
            model = prepare_model_for_kbit_training(
                model, use_gradient_checkpointing=cfg["train"].get(
                    "gradient_checkpointing", True))
        lora = LoraConfig(
            r=meth.get("lora_r", 32),
            lora_alpha=meth.get("lora_alpha", 64),
            lora_dropout=meth.get("lora_dropout", 0.05),
            target_modules=meth.get("target_modules"),
            bias="none",
            task_type="CAUSAL_LM",
        )
        model = get_peft_model(model, lora)
        model.print_trainable_parameters()
    return model, tok


def build_dataset(cfg: dict, tok):
    from datasets import load_dataset

    d = cfg["data"]
    files = {"train": d["train"]}
    if d.get("eval"):
        files["eval"] = d["eval"]
    ds = load_dataset("json", data_files=files)
    max_len = d.get("max_seq_len", 2048)

    def to_text(ex):
        # Expect ex["messages"] = [{role, content}, ...] (chatml).
        text = tok.apply_chat_template(
            ex["messages"], tokenize=False, add_generation_prompt=False)
        return tok(text, truncation=True, max_length=max_len)

    cols = ds["train"].column_names
    return ds.map(to_text, remove_columns=cols)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry-run", action="store_true",
                    help="parse config and report the plan, do not train")
    args = ap.parse_args()

    cfg = load_config(args.config)
    t = cfg["train"]
    print(f"[train] run={cfg['run_name']} base={cfg['model']['base']} "
          f"method={cfg['method']['type']}")

    if args.dry_run:
        print("[train] dry run OK. Config is valid. Nothing trained.")
        return

    try:
        import torch  # noqa: F401
    except ImportError:
        die("torch not installed. Run scaffold/setup_env.sh first.")

    from transformers import (DataCollatorForLanguageModeling, Trainer,
                              TrainingArguments)

    model, tok = build_model_and_tokenizer(cfg)
    ds = build_dataset(cfg, tok)

    out = cfg["output"]["dir"]
    os.makedirs(out, exist_ok=True)
    targs = TrainingArguments(
        output_dir=out,
        num_train_epochs=t.get("epochs", 3),
        per_device_train_batch_size=t.get("per_device_batch_size", 1),
        gradient_accumulation_steps=t.get("grad_accum", 16),
        learning_rate=t.get("lr", 2e-4),
        warmup_steps=t.get("warmup_steps", 0),
        gradient_checkpointing=t.get("gradient_checkpointing", True),
        logging_steps=t.get("logging_steps", 10),
        save_strategy="no",
        bf16=True,
        optim=t.get("optim", "paged_adamw_8bit"),
        seed=t.get("seed", 42),
        report_to=["tensorboard"],
    )
    trainer = Trainer(
        model=model,
        args=targs,
        train_dataset=ds["train"],
        eval_dataset=ds.get("eval"),
        data_collator=DataCollatorForLanguageModeling(tok, mlm=False),
    )
    trainer.train()
    trainer.save_model(out)
    tok.save_pretrained(out)
    print(f"[train] saved adapter/model to {out}")


if __name__ == "__main__":
    main()
