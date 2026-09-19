"""Edge worker (reflex layer).

On real hardware this is a drone/robot-dog/fixed node running a small model that
turns sensor input into an EventDescriptor. In the demo it replays descriptors
from a scenario file. It does not judge; it observes and publishes.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "interpreter"))
from schema import EventDescriptor  # noqa: E402


class EdgeWorker:
    def __init__(self, worker_id: str, bus, topic: str = "edge.events"):
        self.worker_id = worker_id
        self.bus = bus
        self.topic = topic

    def observe(self, descriptor_dict: dict) -> None:
        # Drop the demo-only "label" before building the strict descriptor.
        clean = {k: v for k, v in descriptor_dict.items() if k != "label"}
        ev = EventDescriptor(**clean)
        self.bus.publish(self.topic, {"worker_id": self.worker_id, "event": ev})
