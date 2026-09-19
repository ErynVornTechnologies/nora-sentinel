# Architecture

NORA Sentinel is three layers with a strict division of labour: **reflex at the edge, thinking at the core.** Each layer can be developed and tested on a single workstation and then mapped onto real hardware without changing the code, only the deployment target.

## Layer 1: Edge brain (reflex)

Every unit that moves or watches carries its own small model.

- **Hardware targets:** drone, robot dog, fixed camera node, or any carrier with a compute module on board. Development target: a single desktop GPU. Field target: an embedded module (for example a Jetson-class board).
- **Model class:** small (sub-1B to ~3B), chosen for weight, power draw, and thermal budget, not for reasoning ability.
- **Job:** perceive and describe. It does not decide. It emits a structured **event descriptor**: who is present, how loud, what language, what movement, how close, what objects. See `docs/cultural-interpreter.md` for the schema.
- **Why small:** on a flying or walking unit, grams and watts are the constraint. The edge is a sensor with a brain stem, not a philosopher.

## Layer 2: Swarm mesh (nervous system)

A closed internal network connecting the units. **This is the only network that exists.**

- **Supervisors** live here. Each supervisor owns a slice of the cohort, aggregates its edge descriptors, applies a cheap first-pass filter, and decides what is worth sending up.
- The mesh is RF and is treated as hostile-adjacent: encrypted, authenticated, and hardened against jamming and spoofing. See `docs/threat-model.md`.
- No gateway to the outside. The mesh does not route to the internet, by design.

## Layer 3: Mobile core (reasoning)

The mind of the swarm. Up to 4 high-end GPUs in a transmission van or a fixed cabinet.

- **Manager (the "mind"):** runs the cultural interpreter and makes the final verdict. This is the one place a larger, capable model lives, because reasoning is its job.
- **Cohort-harness path:** when a single case is genuinely hard, the manager can borrow the whole cohort's spare compute to shorten the decision, then release it. Distributed inference, not a permanent cluster.
- **Human-in-the-loop (HITL):** the core is where a human operator sits. The entire point of the stack is to hand that human a short, high-signal queue instead of a wall of alarms.

## The manager model is not 3B

A deliberate design note: the edge workers are small on purpose, but the **manager should not be**. A 3B model is fine as a describer or a worker. The interpreter that carries the cultural judgement wants a stronger model (a larger base, or a strong reasoning-tuned small model). Do not size the mind like a limb.

## One codebase, two scales

The swarm skeleton in `demo/` runs as processes on one machine today: manager, supervisors, mock edge workers, one message bus. The same roles and messages map directly onto real units on a real mesh later. What changes between "on my desk" and "in the field" is the transport and the hardware, not the logic.
