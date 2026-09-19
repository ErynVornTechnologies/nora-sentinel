"""Supervisor (swarm mesh layer).

Owns a slice of the cohort. Aggregates edge descriptors, applies a cheap
first-pass filter to keep noise off the mind, and promotes candidates upward
with a corroboration note (how many nearby units agree).
"""
from __future__ import annotations


class Supervisor:
    def __init__(self, supervisor_id: str, bus,
                 in_topic: str = "edge.events",
                 out_topic: str = "candidates"):
        self.supervisor_id = supervisor_id
        self.bus = bus
        self.out_topic = out_topic
        self._seen = {}
        bus.subscribe(in_topic, self.on_event)

    def on_event(self, msg: dict) -> None:
        ev = msg["event"]
        # Cheap first pass: a single quiet, far, lone, empty-handed observation
        # is not worth waking the mind for.
        trivial = (ev.vocal_intensity == "low" and ev.proximity == "far"
                   and ev.group_size <= 1 and not ev.objects and not ev.micro_signals)
        if trivial:
            return
        # Track repeat sightings of the same event id as corroboration.
        self._seen[ev.event_id] = self._seen.get(ev.event_id, 0) + 1
        n = self._seen[ev.event_id]
        corroboration = f"{n} unit(s) reporting via {self.supervisor_id}"
        self.bus.publish(self.out_topic, {"event": ev, "corroboration": corroboration})
