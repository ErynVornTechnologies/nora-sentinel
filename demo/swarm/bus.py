"""Minimal in-process message bus for the swarm demo.

Synchronous pub/sub. In the field this is replaced by the RF mesh transport; the
roles and message shapes stay the same, which is the whole point of the skeleton.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Any, Dict, List


class Bus:
    def __init__(self):
        self._subs: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> None:
        self._subs[topic].append(handler)

    def publish(self, topic: str, message: Any) -> None:
        for handler in list(self._subs.get(topic, [])):
            handler(message)
