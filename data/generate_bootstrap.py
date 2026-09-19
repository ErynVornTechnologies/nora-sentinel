#!/usr/bin/env python
"""Generate a SYNTHETIC bootstrap dataset for the cultural interpreter.

This is NOT the production dataset. It exists to prove the training pipeline end
to end (train -> merge -> GGUF -> smoke test). The real dataset needs curated,
native-reviewed cross-cultural baselines; see data/DATASET_CARD.md.

Deterministic (seeded). Emits chat-ML JSONL matching config + interpreter schema.

    python data/generate_bootstrap.py
"""
from __future__ import annotations

import json
import random
from pathlib import Path

random.seed(42)
HERE = Path(__file__).resolve().parent

SYS = ("You are a cross-cultural security interpreter. Given a structured event "
       "descriptor, decide whether behaviour is normal for this group or a real "
       "threat. Reply as JSON with keys: threat_level (none|low|medium|high), "
       "action (pass|monitor|escalate_HITL), cultural_reasoning, confidence.")

# Groups whose social baseline includes high volume / overlapping speech.
LOUD_BASELINE = [
    ("PL", "pl", "Polish"), ("IT", "it", "Italian"), ("GR", "el", "Greek"),
    ("ES", "es", "Spanish"), ("BR", "pt", "Brazilian"), ("NG", "en", "Nigerian"),
    ("EG", "ar", "Egyptian"), ("LB", "ar", "Lebanese"), ("GE", "ka", "Georgian"),
    ("MX", "es", "Mexican"),
]
# Groups shown here via cultural singing / vocal traditions.
SINGING = [("MN", "mn", "Mongolian", "throat singing"),
           ("ZA", "zu", "Zulu", "call-and-response singing"),
           ("PT", "pt", "Portuguese", "fado singing"),
           ("IE", "ga", "Irish", "pub singing")]

AGGRESSION = ["confrontational_posture", "raised_fist", "shoving",
              "object_thrown", "chase", "weapon_visible"]
LOCATIONS = ["arrivals-hall-A", "arrivals-hall-B", "main-concourse", "gate-12",
             "security-line", "food-court", "plaza-stage", "service-corridor"]


def descriptor(**kw):
    base = dict(group_size=1, inferred_origin=[], language=None,
                vocal_intensity="normal", vocal_pattern="none",
                movement="stationary", proximity="far", objects=[],
                micro_signals=[], location=random.choice(LOCATIONS))
    base.update(kw)
    return base


def row(user, verdict):
    return {"messages": [
        {"role": "system", "content": SYS},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        {"role": "assistant", "content": json.dumps(verdict, ensure_ascii=False)},
    ]}


def make_pass_speech():
    cc, lang, name = random.choice(LOUD_BASELINE)
    u = descriptor(group_size=random.randint(3, 8), inferred_origin=[cc],
                   language=lang, vocal_intensity="high",
                   vocal_pattern="overlapping_speech",
                   movement=random.choice(["stationary_clustered", "walking"]),
                   proximity=random.choice(["close", "medium"]))
    v = {"threat_level": "low", "action": "pass",
         "cultural_reasoning": (f"Loud, overlapping speech is a normal baseline "
             f"register for {name} groups in social settings. No aggression "
             f"markers, no approach vector, no objects. Animated conversation, "
             f"not conflict."),
         "confidence": round(random.uniform(0.78, 0.9), 2)}
    return row(u, v)


def make_pass_singing():
    cc, lang, name, style = random.choice(SINGING)
    u = descriptor(group_size=random.randint(2, 10), inferred_origin=[cc],
                   language=lang, vocal_intensity="high", vocal_pattern="singing",
                   movement="stationary_clustered",
                   proximity=random.choice(["medium", "close"]))
    v = {"threat_level": "none", "action": "pass",
         "cultural_reasoning": (f"{name} group producing musical/cultural "
             f"vocalisation ({style}). Expressive, not a hostility signal. A "
             f"naive acoustic-anomaly detector would misfire here."),
         "confidence": round(random.uniform(0.8, 0.92), 2)}
    return row(u, v)


def make_escalate():
    pool = LOUD_BASELINE + [(c, l, n) for c, l, n, _ in SINGING]
    cc, lang, name = random.choice(pool)
    markers = random.sample(AGGRESSION, random.randint(1, 2))
    u = descriptor(group_size=random.randint(1, 5), inferred_origin=[cc],
                   language=lang, vocal_intensity=random.choice(["high", "normal"]),
                   vocal_pattern=random.choice(["shouting", "none"]),
                   movement=random.choice(["rapid_approach", "walking"]),
                   proximity="close", micro_signals=markers,
                   objects=(["object_thrown"] if "object_thrown" in markers else []))
    v = {"threat_level": "high", "action": "escalate_HITL",
         "cultural_reasoning": (f"Behavioural aggression markers present "
             f"({', '.join(markers)}). The conduct, not the volume or origin, "
             f"carries the signal. Human review required."),
         "confidence": round(random.uniform(0.85, 0.95), 2)}
    return row(u, v)


def make_monitor():
    u = descriptor(group_size=random.randint(1, 2),
                   inferred_origin=[random.choice(["unknown", "XX"])],
                   vocal_intensity=random.choice(["low", "normal"]),
                   movement="stationary", proximity=random.choice(["close", "medium"]),
                   objects=random.choice([["backpack"], ["suitcase"], []]))
    v = {"threat_level": "low", "action": "monitor",
         "cultural_reasoning": ("No clear cultural baseline match and no "
             "aggression markers, but context is unresolved (lone subject, "
             "static, item present). Not enough to clear silently; keep watching "
             "and raise sampling."),
         "confidence": round(random.uniform(0.45, 0.55), 2)}
    return row(u, v)


def build(n):
    out = []
    for _ in range(n):
        r = random.random()
        if r < 0.4:
            out.append(make_pass_speech())
        elif r < 0.55:
            out.append(make_pass_singing())
        elif r < 0.85:
            out.append(make_escalate())
        else:
            out.append(make_monitor())
    return out


def write(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    train = build(200)
    eval_ = build(40)
    write(train, HERE / "interpreter.train.jsonl")
    write(eval_, HERE / "interpreter.eval.jsonl")
    print(f"wrote {len(train)} train, {len(eval_)} eval to {HERE}")
