# The cultural interpreter

This is the part of NORA Sentinel that is not a commodity. Everything else (detection, tracking, mesh, orchestration) exists to feed this layer and to act on its output.

## What it takes in

A **modality-agnostic event descriptor**. The edge produces it; the interpreter never touches raw pixels or audio. This keeps the interpreter independent of which sensors you use, and lets you swap or upgrade perception without retraining the mind.

```json
{
  "event_id": "evt-000123",
  "timestamp": "2026-09-19T15:40:00Z",
  "location": "arrivals-hall-B",
  "group_size": 6,
  "inferred_origin": ["PL"],
  "language": "pl",
  "vocal_intensity": "high",
  "vocal_pattern": "overlapping_speech",
  "movement": "stationary_clustered",
  "proximity": "close",
  "objects": [],
  "micro_signals": []
}
```

Fields are hints, not certainties. `inferred_origin` and `language` are probabilistic and the interpreter is expected to reason under that uncertainty.

## What it puts out

```json
{
  "event_id": "evt-000123",
  "threat_level": "low",
  "action": "pass",
  "cultural_reasoning": "Loud, overlapping speech is the baseline register for this group. No aggression markers (no confrontational posture, no rapid approach, no objects). Consistent with animated conversation, not conflict.",
  "confidence": 0.86,
  "corroboration": "2 of 2 nearby units agree"
}
```

`action` is always one of: `pass`, `monitor`, `escalate_HITL`.

## Worked examples

**1. Loud Polish in arrivals.** Six men, Polish, high vocal intensity, overlapping speech, close proximity, no objects, no approach vector.
Verdict: `pass`. Loud is the baseline for this group; volume is not a threat marker here.

**2. Mongolian throat singing.** A cluster performing khoomei, low steady vocalisation, stationary, drawing a friendly crowd.
Verdict: `pass`. Musical and cultural expression, not a hostility signal. A naive acoustic-anomaly detector would flag this; the interpreter does not.

**3. Same acoustics, different markers.** Similar volume to example 1, but now with a rapid approach vector, a confrontational posture, and a dropped object.
Verdict: `escalate_HITL`. The behavioural markers, not the volume, carry the signal. This is the case a human should see.

The point across all three: **volume and "anomaly" are not threat. Context is.** The same sound is a pass or an escalation depending on who, where, and what else is happening.

## Why this is a moat

- The hard input is **data**, not compute. Curated cross-cultural behavioural baselines with native review barely exist as a dataset. Building one is the year of native-expert work that the product then makes reusable forever.
- It is **evaluable**: native reviewers can score verdicts, which gives a real quality metric and a defensible claim.
- It is **explainable**: every verdict ships with its reasoning, which is exactly what a human operator and an auditor need.

## The ROI line for a buyer

At an event with 50 nationalities, staffing native cultural judgement on every shift means dozens of people, forever. NORA Sentinel needs those experts **once, to build the dataset**, and then one interpreter carries that judgement across every shift. You are buying a year of expert work as a permanent capability.
