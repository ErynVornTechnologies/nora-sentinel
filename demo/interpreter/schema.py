"""Shared data contracts for NORA Sentinel.

The edge produces EventDescriptor. The manager returns Verdict. Both layers only
ever exchange these structures, never raw pixels or audio, which keeps the mind
independent of the sensors.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional

ACTIONS = ("pass", "monitor", "escalate_HITL")
THREAT_LEVELS = ("none", "low", "medium", "high")


@dataclass
class EventDescriptor:
    event_id: str
    group_size: int = 1
    inferred_origin: List[str] = field(default_factory=list)
    language: Optional[str] = None
    vocal_intensity: str = "normal"        # low | normal | high
    vocal_pattern: str = "none"            # none | overlapping_speech | singing | shouting
    movement: str = "stationary"           # stationary | stationary_clustered | walking | rapid_approach
    proximity: str = "far"                 # far | medium | close
    objects: List[str] = field(default_factory=list)
    micro_signals: List[str] = field(default_factory=list)  # e.g. confrontational_posture
    location: Optional[str] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Verdict:
    event_id: str
    threat_level: str
    action: str
    cultural_reasoning: str
    confidence: float = 0.0
    corroboration: Optional[str] = None

    def __post_init__(self):
        if self.action not in ACTIONS:
            raise ValueError(f"action must be one of {ACTIONS}, got {self.action}")
        if self.threat_level not in THREAT_LEVELS:
            raise ValueError(f"threat_level must be one of {THREAT_LEVELS}")

    def to_dict(self) -> dict:
        return asdict(self)
