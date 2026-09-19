# Threat model

The security posture of NORA Sentinel is its main technical selling point, so it is stated plainly here.

## Core claim: no external attack surface

The swarm has **no external network uplink**. The core can run in a van in a field with zero connectivity. There is no remote entrance to the system, so there is no remote entrance to defend. You cannot phish, C2, or exfiltrate across a link that does not exist.

This is the difference between two levels of sovereignty:

- **Data sovereignty:** your data stays in your building. (What most vendors mean.)
- **Operational sovereignty:** the system needs no building, no cloud, and no external link to function. (What NORA Sentinel means.)

## What "no network" does and does not mean

Be precise, so a technical reviewer cannot catch you out:

- **It means:** no uplink to the internet or any outside system. No inbound remote access. No dependency on a remote model or API.
- **It does not mean:** no radio at all. Units still talk to each other over an internal RF mesh. That mesh is the one link that exists, and it is treated as hostile-adjacent.

## Internal mesh hardening

The mesh is defended as if an adversary is already within radio range, because they can be:

- **Encryption** of all mesh traffic.
- **Authentication** of every unit; a rogue node cannot silently join.
- **Anti-jamming** measures so degradation is graceful, not a cliff.
- **Anti-spoofing** so injected or replayed messages are rejected.
- **Partition tolerance:** if the mesh splits, each part keeps making safe local decisions and reconciles on rejoin.

## Human-in-the-loop as a safety property

The system never takes an irreversible real-world action on its own. Its output is a verdict and, at most, an escalation to a human. The human decides on force, dispatch, or intervention. HITL is not a limitation bolted on; it is what keeps an autonomous swarm accountable.

## Failure posture

- Loss of a worker: the cohort continues, coverage degrades gracefully.
- Loss of a supervisor: its slice is reassigned.
- Loss of the core: the swarm falls back to conservative local behaviour and does not act blind.
- Ambiguity: the default bias is to `monitor` or `escalate_HITL`, never to silently `pass` a real signal.
