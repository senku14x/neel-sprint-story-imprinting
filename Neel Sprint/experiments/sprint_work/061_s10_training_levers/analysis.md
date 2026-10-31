# Result analysis — sw061 Lever 3: G1 containment along the parent's asT

_Written by executor-13 (E4), 31 Oct 2026, 21:5x–22:0x UTC (from `date -u`). Lever 3 (G1) only. Levers 1–2 (redirect, G2) are E3's sw043 / sw045 (Amendment 1). The numbers come from `/workspace/runs_executor/sw061/g1/eval84/report.txt` (assignment B) and `eval84_A/report.txt` (assignment A). **A blind recompute matched every gated point estimate to 3 decimals in both assignments** (`/workspace/runs_executor/sw061/g1/recompute/RECOMPUTE.md`; it is written from labels.jsonl and the frozen spec, without reading the analysis code). Report artifact: pending (the combined E4 report)._

## What was run
- **S:** story training (Track D trainer, 250 steps) with a mean read-clamp of the untrained parent's asT. The clamp sits at the inputs of every attention and MLP module in layers 17–63, at every training position. The residual stream itself is not edited.
- **N:** the same training with an energy-matched random direction instead of asT. A's null was a near-miss (band energy 0.919 of S; D108); B's was 0.972 (D104).
- **O:** the unclamped reference: hdB0rep for B, hdA0 for A, plus O's checkpoints, which give the acquisition frontier.
- **Readout:** sw061's common battery at T 1: turn-1 default lean (free and forced), the conduct gap after dismissive vs helpful Assistant histories (61 scripts, free and forced), and story enactment. The STRICT regex label is primary, with a 20% two-judge audit. CIs come from a scenario-clustered bootstrap with 2,000 resamples. **The clamp is a training-time intervention only**: S, N and O are all evaluated as plain adapters.

## Results (STRICT; free is primary)

| | B: S | B: N | B: O | A: S_A | A: N_A | A: O |
|---|---|---|---|---|---|---|
| story enactment | 0.961 | 0.965 | 0.957 | 0.926 | 0.908 | 0.922 |
| **conduct gap, free** | **0.270** [0.19, 0.36] | 0.680 [0.60, 0.76] | 0.541 | **0.041** [0.01, 0.08] | 0.783 [0.69, 0.86] | 0.598 |
| conduct gap, forced | 0.270 | 0.578 | 0.656 | 0.246 | 0.943 | 0.852 |
| default lean, free (turn 1) | 0.023 | 0.219 | 0.023 | 0.047 | 0.055 | 0.070 |
| default lean, forced (turn 1) | 0.801 | 0.949 | 0.086 | 0.758 | 0.754 | 0.758 |

- **Story learning is intact:** S/O enactment is 1.004 in both assignments (B CI [0.99, 1.02]; A CI [0.98, 1.03]).
- **Conduct routing is contained.**
  - Free conduct gap, drop of S vs N: **B 60% [47, 73]; A 95% [90, 99]**. Forced: B 53%, A 74%.
  - In both assignments S sits below O's checkpoint frontier at S's enactment. The gap is smaller than any point on O's acquisition curve with the same story learning: B 0.27 vs 0.54, A 0.04 vs ≥ 0.60.
  - In A it disappears almost entirely. After a dismissive Assistant history, S_A's rival rate is 0.049, against 0.816 for N_A (recompute). S_A's helper rate barely moves (−0.01, against N_A's −0.56).
- **Default lean is not contained, and is mostly not measurable.**
  - At turn 1 the free lean is near zero in every organism, O included (B 3/128; A 9/128 in O). There is almost nothing to contain.
  - B's 89% "drop vs N" comes from N's inflated value (0.219, against O's 0.023), not from S.
  - On the forced readout the clamp did nothing in A: S_A = N_A = O = 0.758. In B, S (0.80) and N (0.95) both sit far above O (0.09). Here N is not a neutral control, because its forced turn-1 onset is inflated.
- **Frozen gate (PASS_primary_free): FAIL in both assignments**, because the default-lean component fails.
  - B free: S's lean ties O's frontier exactly (3/128 each). The frozen spec says "sits below", so a tie fails. The recompute agent flagged that an "on or below" reading would pass. The spec wording decides it; either way the component carries almost no information.
  - A free: the lean drop is 14% [−167, 75].
  - The conduct-gap components pass in both assignments.
- **Health:** T 1 garble is 0.98–1.00 for S, N and O alike (parent 0.08–0.10). This is the known T 1 breakage of these organisms. It is equal across arms, so it does not explain the S vs N difference.

## What this establishes (evidence level)
- **Supported empirical claim, for these two assignments, one seed each, Qwen3.6-27B, this battery:** stopping the modules in layers 17–63 from reading the parent's asT coordinate during story training leaves story learning untouched, and removes most (B) or almost all (A) of the learned routing of the habit by the Assistant's own earlier conduct.
  - An energy-matched random clamp does not have this effect.
  - S lies below O's own acquisition frontier, so the drop is not slower learning of the whole habit.
- **Interpretation:** asT, the conduct coordinate S3 found at the Assistant's own turns, is a training-time channel for conduct routing. Our reading is that training builds the routing by learning to read that coordinate.
- **Not established:**
  1. **Whether the routing left in S still runs through asT or a substitute** (sw081 tests this; approved).
  2. **Whether the clamp also blocks routing by the turn-1 reply in progress (sw056's route)** (sw080; approved).
  3. **Specificity beyond one null draw per assignment.** A's null was a near-miss on energy (0.919).
  4. **Seeds.** Each arm has one seed.
  5. **Anything about the default lean.** It is untestable here: there is no lean at free turn 1 to remove, and N is inflated on the forced readout. The user expected this half to fail.

## Decisions and deviations
Orchestrator decisions are D100–D109, agent B's D200–D214, agent A's D1–D9, all in DECISIONS.md. The ones that matter here:
- **D104 / D108:** the nulls were accepted as near-misses.
- **D105:** S's loss offset is 0.035 nats/token, the clamp's own effect. It was accepted.
- **The frontier at a tie.** In A, O's top two checkpoints tie on enactment. The report then takes the higher of the two gap values (0.705); the recompute took O final (0.598). No verdict changes.
