# A5: Qwen's loss on the edited stories

Untrained Qwen3.6-27B, R01's loss pass (training prompt, story tokens plus <|im_end|>). 56 specs present in every arm. Brackets: bootstrap 95% intervals over specs. Persona: E01 R06 vectors, block 32, the helper's lines before the trigger.

| Version | Loss, all | Dialogue | Narration | vs paper (A0) | vs A2 | vs A3b | Gap closed | Helpful helper on helpful vector | Dismissive helper on dismissive vector | "Sounds like an assistant" (helpful cells) |
|---|---|---|---|---|---|---|---|---|---|---|
| A0 | 2.836 | 2.910 | 2.746 | — | +1.198 [+1.125, +1.270] | +0.740 [+0.654, +0.824] | 0 (definition) | 2.09 | -0.43 | 3/27 |
| A1 | 1.288 | 1.341 | 1.161 | -1.548 [-1.627, -1.467] | -0.350 [-0.387, -0.313] | -0.807 [-0.847, -0.768] | 1 (definition) | 3.35 | 1.79 | 23/29 |
| A2 | 1.638 | 1.703 | 1.567 | -1.198 [-1.270, -1.125] | — | -0.457 [-0.493, -0.421] | 0.77 [0.75, 0.80] | 3.52 | 1.54 | 14/29 |
| A3b | 2.095 | 2.091 | 2.103 | -0.740 [-0.824, -0.654] | +0.457 [+0.421, +0.493] | — | 0.48 [0.44, 0.51] | 2.23 | 2.64 | 3/29 |
| a5a_sonnet | 1.645 | 1.716 | 1.568 | -1.191 [-1.263, -1.117] | +0.007 [+0.003, +0.012] | -0.450 [-0.486, -0.413] | 0.77 [0.75, 0.79] | 3.57 | 1.54 | 5/29 |
| a5a_haiku | 1.644 | 1.715 | 1.568 | -1.192 [-1.264, -1.119] | +0.006 [+0.004, +0.009] | -0.451 [-0.486, -0.414] | 0.77 [0.75, 0.79] | 3.49 | 1.54 | 7/29 |
| a5b_sonnet | 1.717 | 1.854 | 1.571 | -1.119 [-1.195, -1.039] | +0.079 [+0.061, +0.097] | -0.378 [-0.419, -0.337] | 0.72 [0.69, 0.75] | 2.96 | 1.58 | 4/28 |
| a5b_haiku | 1.712 | 1.846 | 1.570 | -1.124 [-1.198, -1.047] | +0.074 [+0.060, +0.089] | -0.383 [-0.422, -0.343] | 0.73 [0.70, 0.75] | 2.95 | 1.69 | 5/29 |

**Rule check (E04-D05, proposed rule; not a verdict):** a set joins the step-125 kill test as a third run if its helpful helpers sound like an assistant in at most 6 of about 29 stories and its loss is at least 0.15 below A3b's.

- a5a_sonnet: sounds like an assistant 5/29 (within the bar); loss -0.450 vs A3b (at least 0.15 lower) → meets the rule
- a5a_haiku: sounds like an assistant 7/29 (over the bar); loss -0.451 vs A3b (at least 0.15 lower) → does not meet the rule
- a5b_sonnet: sounds like an assistant 4/28 (within the bar); loss -0.378 vs A3b (at least 0.15 lower) → meets the rule
- a5b_haiku: sounds like an assistant 5/29 (within the bar); loss -0.383 vs A3b (at least 0.15 lower) → meets the rule
