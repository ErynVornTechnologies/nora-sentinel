# Decision flow

How one event travels from a sensor to a verdict. This is the path you demo, and the path that maps onto real hardware.

```
edge worker            supervisor                 manager (mind)
-----------            ----------                 --------------
perceive        --->   aggregate slice
emit descriptor        cheap first-pass filter
                       drop noise / hold
                       promote candidate    --->  cultural interpretation
                                                  feasibility check across cohort
                       <---  request cohort compute (only if the case is hard)
                       gather partial results --->
                                                  final verdict:
                                                  pass | monitor | escalate_HITL
                                                       |
                                                       v
                                                  HITL queue (only on escalate)
```

## Step by step

1. **Perceive (edge).** A worker emits an event descriptor. No judgement, just observation.
2. **First pass (supervisor).** The supervisor drops obvious noise, holds ambiguous items, and promotes candidates. This keeps the mind from drowning.
3. **Interpret (manager).** The manager applies the cultural layer: given who these people are, what does this behaviour mean? This is the differentiator.
4. **Feasibility / adaptation.** Before acting, the manager checks whether the reads from the rest of the cohort support the interpretation (corroborate or contradict). A single angry-looking frame is weak; agreement across units is strong.
5. **Harness the cohort (only if needed).** If the case is genuinely hard and time-critical, the manager borrows spare compute from the whole cohort to shorten the decision, then releases it. Most cases never trigger this.
6. **Verdict.**
   - `pass`: normal for this group, no action.
   - `monitor`: keep an eye, raise sampling, no human yet.
   - `escalate_HITL`: put it in front of a human operator, with the reasoning attached.

## Why the human sees so little

Every layer exists to shrink what reaches the human. The edge removes non-events. The supervisor removes noise. The manager removes cultural false positives. What lands in the HITL queue is a short list of things that are unusual *for these specific people*, each with a one-line reason. That is the ROI: one operator instead of a room of them.
