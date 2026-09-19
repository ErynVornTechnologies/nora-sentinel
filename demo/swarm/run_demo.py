#!/usr/bin/env python
"""End-to-end swarm demo.

Wires a message bus, one manager (the mind), one supervisor, and edge workers,
then replays the scenarios through the full path:

    edge worker -> supervisor -> manager (cultural interpreter) -> verdict

Runs on pure Python with the default stub interpreter, so it works before any
training. Point --backend model --model-dir <path> at a trained adapter later.

    python demo/swarm/run_demo.py
    python demo/swarm/run_demo.py --backend model --model-dir checkpoints/cultural-interpreter-v0
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bus import Bus
from manager import Manager
from supervisor import Supervisor
from worker import EdgeWorker

SCENARIOS = Path(__file__).resolve().parents[1] / "interpreter" / "scenarios.jsonl"


def load_scenarios():
    rows = []
    with open(SCENARIOS, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="stub", choices=["stub", "model"])
    ap.add_argument("--model-dir", default=None)
    args = ap.parse_args()

    bus = Bus()
    manager = Manager(bus, backend=args.backend, model_dir=args.model_dir)
    Supervisor("sup-1", bus)
    worker_a = EdgeWorker("edge-a", bus)
    worker_b = EdgeWorker("edge-b", bus)  # second unit -> corroboration

    rows = load_scenarios()
    labels = {r["event_id"]: r.get("label", r["event_id"]) for r in rows}

    print(f"\nNORA Sentinel demo | backend={args.backend} | "
          f"{len(rows)} scenarios\n" + "=" * 68)
    for r in rows:
        worker_a.observe(r)
        worker_b.observe(r)

    icon = {"pass": "PASS ", "monitor": "WATCH", "escalate_HITL": "HUMAN"}
    for v in manager.verdicts:
        print(f"\n[{icon.get(v.action, v.action)}] {labels.get(v.event_id, v.event_id)}"
              f"  (threat={v.threat_level}, conf={v.confidence:.2f})")
        print(f"   reasoning: {v.cultural_reasoning}")
        if v.corroboration:
            print(f"   corroboration: {v.corroboration}")

    escalated = sum(1 for v in manager.verdicts if v.action == "escalate_HITL")
    print("\n" + "=" * 68)
    print(f"Verdicts: {len(manager.verdicts)} | escalated to human: {escalated}")
    print("Only the escalations reach an operator. Everything else was handled.\n")


if __name__ == "__main__":
    main()
