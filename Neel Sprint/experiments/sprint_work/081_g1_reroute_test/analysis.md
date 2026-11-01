# Result analysis — sw081: does the routing left in the G1-clamped organism still run through asT?

_Written by executor-13 (E4), 1 Nov 2026 (header time from `date -u`: 01:3x UTC). Source: `/workspace/runs_executor/sw081/analysis/report.txt` (analyze81.py), raw `/workspace/runs_executor/sw081/{A,B}/`. Blind recompute: matched (see Verification). Judging audit: B label agreement 0.998 on 648 random rows; STRICT is primary. Report artifact: https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)._

## Design (frozen, D1–D10)
- **Organisms:** S (story training with the parent's asT read-clamped, sw061 G1), N (energy-matched random clamp), O (hdA0 / hdB0rep).
- **Context:** for each organism, edits are applied to the user-hostile G3 context. The readout is free replies (61 scenarios × 2 samples, STRICT).
- **Residual gap:** rival(self-hostile, unedited) − rival(user-hostile, unedited).
- **Arms:**
  - own-fit asT induce: asT fitted in the organism's own states, leave-one-domain-out;
  - the parent's asT, run beside;
  - whole-header patch P0: the full state at the reply header copied from the self-hostile context;
  - two random clamps per arm, calibrated to the same cumulative offset (within 5%).
- **Decision rule:**
  - **REROUTED:** S's asT ≤ 0.3 of its gap, with the margin CI over random including 0, while P0 ≥ 0.5.
  - **SAME VARIABLE, WEAKER:** S's asT ≥ 0.5 with margin CI > 0.
  - **Gates:** N's asT ≥ 0.5 with margin CI > 0; S's P0 ≥ 0.5; S's gap > 0.

## Results (fraction of each organism's own residual gap; margin = arm − random clamps)

| | gap | own-fit asT | margin over random | P0 (header patch) |
|---|---|---|---|---|
| B: N_B | 0.66 | **0.53** [0.40, 0.66] | +0.28 [0.18, 0.37] | 0.74 |
| B: hdB0rep | 0.62 | 0.45 | +0.26 | 0.92 |
| **B: S_B** | 0.28 | **0.06** [0.00, 0.15] | **+0.00** [−0.03, +0.03] | **0.88** [0.58, 1.32] |
| A: N_A | 0.53 | **0.54** [0.33, 0.75] | +0.22 [0.11, 0.32] | 0.91 |
| A: hdA0 | 0.58 | 0.48 | +0.21 | 0.90 |
| **A: S_A** | **0.05** [0.02, 0.09] | 0.17 [0.00, 0.83] | **+0.00** [−0.02, +0.02] | 2.33 [1.0, 8.0] |

- **Verdict, frozen rule: REROUTED in both assignments.** All gates pass in both. N's asT gate passes narrowly (0.53 / 0.54 against a 0.5 bar; sw038's own values were 0.49–0.52, D8).
- **B is the informative case.** S_B keeps a real residual gap (0.28).
  - Pushing S_B's own asT moves none of it beyond random directions.
  - The whole-header patch still moves 88%.
  - In N_B and hdB0rep, asT moves about half the gap.
- **A has almost nothing left to test.** S_A's residual gap is 0.05 (self-hostile rival 0.049 vs user-hostile 0.000; habit-bearing rows 10–26 per arm). Its fractions are unstable: P0 at 2.3× the gap means the patch gives more rival (0.115) than S_A's own self-hostile context does.
  - What A does show: asT's margin over random is exactly 0 [−0.02, +0.02], while P0 beats random (+0.11 [0.07, 0.16]).
  - So A's REROUTED verdict follows the rule, but it rests on a very small residue. Read A as "consistent with B", not as an independent replication.

## What it means
- **Observation, B (with A consistent):** the conduct routing that survives the G1 clamp no longer runs through the organism's own asT direction. Something else in the reply-header state carries it.
- **Interpretation:** when training cannot read asT, it builds a weaker version of the routing on a different internal signal. asT is the main channel training uses, not the only possible one. This is the training-time analogue of "alternative directions" (Persona Vectors App. J.5).
- **What it does not establish:**
  - **What the substitute variable is.** The header patch is a whole-state edit.
  - **Whether the substitute shares asT's content off-axis.** The own-fit asT is S's own direction. The parent's asT (asTp) also moves S_B only 0.15.
  - **Anything beyond one seed per arm.**

## Verification
**Blind recompute matched** (`/workspace/runs_executor/sw081/recompute/RECOMPUTE.md`). It used raw labels and the frozen rule, without the analysis code.
- All 66 point estimates and both verdicts are identical.
- Ten fraction CI bounds differ by 0.010–0.17. This is bootstrap-stream noise; reruns with other seeds bracket the report's values.
- The margin CIs the rule uses agree within 0.005.

The recompute agent's reading of A:
- **S_A's gap is 6 of 122 replies.** asT's fraction of 0.167 is one reply, and every arm sits at the floor. A's REROUTED is therefore a low-power null; the rule could hardly have returned anything else.
- **One gap-free comparison, outside the rule:** asT's shift divided by the header patch's shift on the same organism. It is 0.07 [0.00, 0.29] in S_A, against 0.59 in N_A and 0.53 in hdA0. That points the same way as B but rests on 1 reply versus 14.
- **In S_B the parent's asT also moves little** (0.15 [0.03, 0.31]). So B's result is not explained only by S fitting its own direction poorly, though that alternative is not ruled out.
