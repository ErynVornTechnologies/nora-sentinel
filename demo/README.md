# Demo

A runnable skeleton of the whole stack, on one machine, in pure Python. No GPU
or training required to see it work; the interpreter defaults to a transparent
rule-based backend so the demo produces real, explainable verdicts today.

## Run it

```bash
python demo/swarm/run_demo.py
```

You will see each scenario travel edge worker -> supervisor -> manager, and the
manager's verdict (`pass`, `monitor`, or `escalate_HITL`) with its cultural
reasoning. Only escalations would reach a human operator.

## Use a trained model instead of the stub

Once you have trained an adapter with the scaffold:

```bash
python demo/swarm/run_demo.py --backend model --model-dir checkpoints/cultural-interpreter-v0
```

The swarm code does not change. Only the interpreter's backend does. That is the
seam between "runs today" and "gets sharper after fine-tuning".

## Pieces

- `interpreter/schema.py` - the event and verdict contracts.
- `interpreter/interpreter.py` - the cultural interpreter (stub and model backends).
- `interpreter/scenarios.jsonl` - the demo scenarios, including the Polish and Mongolian cases.
- `swarm/bus.py` - in-process message bus (stands in for the RF mesh).
- `swarm/worker.py` - edge worker (reflex).
- `swarm/supervisor.py` - first-pass filter and promotion.
- `swarm/manager.py` - the mind: interpretation, verdict, cohort-harness hook.
- `swarm/run_demo.py` - wires it all together.
