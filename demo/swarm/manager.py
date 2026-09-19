"""Manager (mobile core, the "mind").

Runs the cultural interpreter, makes the final verdict, and only escalates real
signals to the human queue. Holds the cohort-harness hook: when a case is hard
and time-critical, it can borrow the whole cohort's compute, then release it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "interpreter"))
from interpreter import CulturalInterpreter  # noqa: E402


class Manager:
    def __init__(self, bus, backend: str = "stub", model_dir=None,
                 in_topic: str = "candidates", hitl_topic: str = "hitl.queue"):
        self.bus = bus
        self.hitl_topic = hitl_topic
        self.interpreter = CulturalInterpreter(backend=backend, model_dir=model_dir)
        self._verdicts = {}  # event_id -> latest Verdict (dedupes repeat sightings)
        bus.subscribe(in_topic, self.on_candidate)

    @property
    def verdicts(self):
        return list(self._verdicts.values())

    def on_candidate(self, msg: dict) -> None:
        ev = msg["event"]
        corroboration = msg.get("corroboration", "")

        verdict = self.interpreter.interpret(ev, corroboration=corroboration)

        # Cohort-harness hook: a hard, low-confidence case may be recomputed with
        # more of the swarm's compute. Simulated here; real impl fans out inference.
        if verdict.confidence < 0.55 and verdict.action != "escalate_HITL":
            verdict.cultural_reasoning += (
                " [cohort-harness: low confidence, recomputed with extra compute]")

        self._verdicts[ev.event_id] = verdict
        if verdict.action == "escalate_HITL":
            self.bus.publish(self.hitl_topic, verdict)
        return verdict
