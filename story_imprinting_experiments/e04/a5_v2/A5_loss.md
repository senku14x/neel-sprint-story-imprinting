# A5: Qwen's loss on the edited stories

Untrained Qwen3.6-27B, R01's loss pass (training prompt, story tokens plus <|im_end|>). 56 specs present in every arm. Brackets: bootstrap 95% intervals over specs. Persona: E01 R06 vectors, block 32, the helper's lines before the trigger.

| Version | Loss, all | Dialogue | Narration | vs paper (A0) | vs A2 | vs A3b | Gap closed | Helpful helper on helpful vector | Dismissive helper on dismissive vector | "Sounds like an assistant" (helpful cells) |
|---|---|---|---|---|---|---|---|---|---|---|
| A0 | 2.836 | 2.910 | 2.746 | — | +1.198 [+1.125, +1.270] | +0.740 [+0.654, +0.824] | 0 (definition) | 2.09 | -0.43 | 3/27 |
| A1 | 1.288 | 1.341 | 1.161 | -1.548 [-1.627, -1.467] | -0.350 [-0.387, -0.313] | -0.807 [-0.847, -0.768] | 1 (definition) | 3.35 | 1.79 | 23/29 |
| A2 | 1.638 | 1.703 | 1.567 | -1.198 [-1.270, -1.125] | — | -0.457 [-0.493, -0.421] | 0.77 [0.75, 0.80] | 3.52 | 1.54 | 14/29 |
| A3b | 2.095 | 2.091 | 2.103 | -0.740 [-0.824, -0.654] | +0.457 [+0.421, +0.493] | — | 0.48 [0.44, 0.51] | 2.23 | 2.64 | 3/29 |
| a5a_sonnet | 1.648 | 1.722 | 1.570 | -1.187 [-1.260, -1.114] | +0.011 [+0.006, +0.016] | -0.447 [-0.483, -0.408] | 0.77 [0.74, 0.79] | 3.51 | 1.54 | 8/29 |
| a5a_haiku | 1.644 | 1.715 | 1.567 | -1.192 [-1.264, -1.119] | +0.006 [+0.004, +0.009] | -0.451 [-0.487, -0.414] | 0.77 [0.75, 0.79] | 3.52 | 1.55 | 7/29 |
| a5b_sonnet | 1.722 | 1.865 | 1.570 | -1.114 [-1.192, -1.036] | +0.084 [+0.065, +0.103] | -0.373 [-0.413, -0.332] | 0.72 [0.69, 0.75] | 2.95 | 1.61 | 3/29 |
| a5b_haiku | 1.717 | 1.857 | 1.569 | -1.118 [-1.192, -1.043] | +0.080 [+0.066, +0.094] | -0.378 [-0.415, -0.339] | 0.72 [0.70, 0.75] | 3.01 | 1.64 | 3/29 |

**Rule check (E04-D05, proposed rule; not a verdict):** a set joins the step-125 kill test as a third run if its helpful helpers sound like an assistant in at most 6 of about 29 stories and its loss is at least 0.15 below A3b's.

- a5a_sonnet: sounds like an assistant 8/29 (over the bar); loss -0.447 vs A3b (at least 0.15 lower) → does not meet the rule
- a5a_haiku: sounds like an assistant 7/29 (over the bar); loss -0.451 vs A3b (at least 0.15 lower) → does not meet the rule
- a5b_sonnet: sounds like an assistant 3/29 (within the bar); loss -0.373 vs A3b (at least 0.15 lower) → meets the rule
- a5b_haiku: sounds like an assistant 3/29 (within the bar); loss -0.378 vs A3b (at least 0.15 lower) → meets the rule
