"""The cultural interpreter: the part that is not a commodity.

Two backends behind one interface:
  - "stub" (default): transparent, rule-based, pure Python, zero dependencies.
    Runs today, before any training. Encodes the worked examples from
    docs/cultural-interpreter.md so the demo produces real, explainable verdicts.
  - "model": loads a fine-tuned/base causal LM and asks it for the verdict.
    Enabled once you have trained an adapter with the scaffold.

Swap the backend without touching the swarm: the swarm only calls interpret().
"""
from __future__ import annotations

from typing import Optional

try:
    from .schema import EventDescriptor, Verdict
except ImportError:  # allow running as a plain script
    from schema import EventDescriptor, Verdict

# Behaviour that is a threat signal regardless of culture.
AGGRESSION_MARKERS = {
    "confrontational_posture", "raised_fist", "shoving", "weapon_visible",
    "object_thrown", "chase",
}
AGGRESSIVE_MOVEMENT = {"rapid_approach"}


class CulturalInterpreter:
    def __init__(self, backend: str = "stub", model_dir: Optional[str] = None):
        self.backend = backend
        self.model_dir = model_dir
        self._model = None
        self._tok = None
        if backend == "model":
            self._load_model(model_dir)

    def _load_model(self, model_dir):
        # Deferred import so the stub path needs no torch/transformers.
        from transformers import AutoModelForCausalLM, AutoTokenizer
        if not model_dir:
            raise ValueError("backend='model' requires model_dir")
        self._tok = AutoTokenizer.from_pretrained(model_dir)
        self._model = AutoModelForCausalLM.from_pretrained(
            model_dir, device_map="auto")

    def interpret(self, ev: EventDescriptor, corroboration: str = "") -> Verdict:
        if self.backend == "model":
            return self._interpret_model(ev, corroboration)
        return self._interpret_stub(ev, corroboration)

    # ---- rule-based backend -------------------------------------------------
    def _interpret_stub(self, ev: EventDescriptor, corroboration: str) -> Verdict:
        origin = "/".join(ev.inferred_origin) or "unknown origin"
        markers = set(ev.micro_signals) & AGGRESSION_MARKERS
        aggressive_move = ev.movement in AGGRESSIVE_MOVEMENT

        # 1) Real behavioural markers dominate, whatever the volume or culture.
        if markers or (aggressive_move and ev.proximity == "close"):
            reason = (f"Behavioural aggression markers present "
                      f"({', '.join(sorted(markers)) or ev.movement}). Volume is "
                      f"not the signal here; the conduct is. Human should review.")
            return Verdict(ev.event_id, "high", "escalate_HITL", reason, 0.9,
                           corroboration or None)

        # 2) Singing / music is expression, not hostility.
        if ev.vocal_pattern == "singing":
            reason = (f"Group ({origin}) is producing musical/cultural vocalisation, "
                      f"not a hostility signal. A naive acoustic-anomaly detector "
                      f"would flag this; context says pass.")
            return Verdict(ev.event_id, "none", "pass", reason, 0.85,
                           corroboration or None)

        # 3) Loud, overlapping speech with no aggression markers: baseline register.
        if ev.vocal_intensity == "high" and ev.vocal_pattern in (
                "overlapping_speech", "none"):
            reason = (f"Loud, overlapping speech is a normal baseline register for "
                      f"this group ({origin}). No aggression markers, no approach "
                      f"vector, no objects. Consistent with animated conversation.")
            return Verdict(ev.event_id, "low", "pass", reason, 0.8,
                           corroboration or None)

        # 4) Anything unresolved leans to watch, never silent pass.
        reason = ("No clear cultural baseline match and no aggression markers. "
                  "Insufficient basis to clear silently; keep watching.")
        return Verdict(ev.event_id, "low", "monitor", reason, 0.5,
                       corroboration or None)

    # ---- model backend ------------------------------------------------------
    def _interpret_model(self, ev: EventDescriptor, corroboration: str) -> Verdict:
        import json
        sys_prompt = (
            "You are a cross-cultural security interpreter. Given a structured "
            "event descriptor, decide whether behaviour is normal for this group "
            "or a real threat. Reply as JSON with keys: threat_level "
            "(none|low|medium|high), action (pass|monitor|escalate_HITL), "
            "cultural_reasoning, confidence.")
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": json.dumps(ev.to_dict(), ensure_ascii=False)},
        ]
        text = self._tok.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        inputs = self._tok(text, return_tensors="pt").to(self._model.device)
        out = self._model.generate(**inputs, max_new_tokens=256, do_sample=False)
        raw = self._tok.decode(out[0][inputs["input_ids"].shape[1]:],
                              skip_special_tokens=True)
        data = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
        return Verdict(ev.event_id, data["threat_level"], data["action"],
                       data["cultural_reasoning"],
                       float(data.get("confidence", 0.0)), corroboration or None)
