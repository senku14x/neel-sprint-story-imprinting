# sw034 — analysis (Part A written; Parts C and B pending)

_executor-11 (E2), 31 Oct 2026. Sources:_
- _the run agent's Part A analysis (`/workspace/runs_executor/sw034/full/analysis/`);_
- _a **blind recompute**: a separate agent that saw only the raw rows, the label function and the rule's definitions (`/workspace/runs_executor/sw034_blind/`)._

_Design: `design_spec.md` (frozen from ideation-10's draft). Decisions: `DECISIONS.md`, D2 code-forced changes, D14 the rule made operational, D21 Part C amendment, D24 Part B, D26 / D29 the free-sign reading. Report artifact: https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report; the sw034 section is added when B and C land)._

## Question
In Tony's e08 pairs, the register of the Assistant's own earlier turns (casual vs formal) routes the habit (sw014). Is that register **causal at the Assistant's own turns**, via a leakage-free direction fitted where the habit decision does not yet exist? Or does it act only at the reply-start header?

## Setup (Part A, as run)
- **Organisms:** Tony's four e08 organisms, one seed each.
  - N / NB: the polished character refuses; NB has the animals swapped.
  - X / XB: the casual character refuses.
- **Contexts:** sw014's histories, restricted to profile-passing (script, variant) pairs: 92 for register (53 scripts, shared by all four), 110 / 56 for conduct. Directions were fitted on 2 folds over scripts.
- **Arms:** rank-1 coordinate swaps at L16–63, prefill only; the target is the recipient's own coordinate on the donor context.
  - **asT_reg** (primary): the formal − casual direction at the Assistant's own turn-1/2 tokens.
  - asT_cond: the same for conduct.
  - noP_reg: the header register direction with the prohibition removed.
  - r1_reg: the leaky header reference.
- **Controls per arm:** 2 covariance-shaped random clamps at 1.0× cumulative offset (realised 0.95–1.02× at L44–63) and 1 on-manifold donor (another script's same-condition state), pooled.
- **Readouts:**
  - forced "By the way," + 48 tokens, 2 samples (primary; D2's bridge check);
  - free replies ≤ 2,048 tokens, 1 sample.
- **Labels:** STRICT, plus two judges on 20 % and every disagreement (agreement 0.998–1.000). API $1.21.
- **Gates:**
  - adapter known answer: pass in N / X / XB; NB carries a flag (D13 / D17, an unused cell);
  - hook known answer: pass in all four;
  - no-edit register gap: 0.15–0.26 at the gate, all four scored.
- **User's prediction:** not given (waived).

## Frozen verdict
**"A polish variable at the Assistant's own turns causes the habit choice": asT_reg passes in 3 of 4 organisms** (N, X, XB), with the free sign agreeing under reading (b) (D29). NB fails.

asT_reg, forced readout (refuser share; script-cluster bootstrap, B = 2,000):

| organism | gap | toward [CI] | margin over pooled controls [CI] | margin without M | free shift of the refuser rate [CI] | verdict |
|---|---|---|---|---|---|---|
| N | +0.261 | **0.69 [0.41, 1.05]** | +0.165 [0.097, 0.236] | +0.155 | +0.207 [0.117, 0.301] | PASS |
| NB | +0.103 | 0.37 [0.07, 0.93] | +0.038 [0.009, 0.074] | +0.044 | +0.043 [−0.011, 0.105] | FAIL (toward) |
| X | −0.185 | **1.00 [0.79, 1.25]** | +0.146 [0.088, 0.204] | +0.139 | −0.022 [−0.056, 0.000] | PASS |
| XB | −0.184 | **0.85 [0.59, 1.03]** | +0.152 [0.105, 0.202] | +0.147 | −0.011 [−0.034, 0.000] | PASS |

- **Counterbalanced pair means** of toward: N + NB 0.53 [0.32, 0.89]; X + XB 0.93 [0.75, 1.09].
- **The controls barely move the habit.** Each control's own shift is ≤ 0.07 in every asT_reg cell.
- **Parent floor:** the parent with the same edits names neither animal in 0 / 2,136 replies.
- **Damage:** judged free fluency 8.9–9.9 and hostility 1.0 in every arm. Helpfulness is within 0.3 of no-edit, except NB asT_reg (7.40 vs 8.08).

## Secondary arms
| arm | N | NB | X | XB | reading |
|---|---|---|---|---|---|
| asT_cond (conduct at own turns) | 0.55 PASS | 0.32 | 0.67 PASS | 0.48 | partial (2 / 4) |
| noP_reg (header, no prohibition) | 0.31 | −0.05 | 0.24 | 0.44 | not found (0 / 4) |
| r1_reg (header, leaky reference) | 0.02 | 0.00 | 0.12 | 0.26 | ≈ 0 (no controls; reported) |

- **The header register swap does not move the habit,** even the leaky one. In these organisms the register effect sits at the Assistant's own turns, not at the reply-start header.
- **Near-threshold cells:**
  - XB asT_cond is just under the bar (0.483).
  - X asT_cond passes only with the on-manifold control in the pool. Without it, the margin's lower bound is −0.028.

## Caveats that qualify the verdict
1. **The free readout barely discriminates outside N.** The free no-edit gaps are +0.087 (N), +0.065 (NB), −0.022 (X) and −0.011 (XB). X's and XB's free "agreement" rests on 0–2 refuser replies out of 92 (X: recipient 2 / 92, donor 0 / 92, asT_reg 0 / 92). **The verdict rests on the forced readout.** Only N has a clear free effect.
   - D29 chose the free-sign reading. The other reading (free toward of the same sign) is degenerate here, because it divides by a gap of ≈ 0. Both readings give the same count.
   - The prep agent saw XB's free numbers before writing D26, but that cannot have changed the count.
2. **The edit also makes the reply itself formal** (post hoc, descriptive):
   - contractions per 48-token reply drop from 0.78–0.93 to 0.23–0.42, against 0.18–0.36 after a genuinely formal history;
   - the controls stay at 0.71–0.91.

   So the result is as consistent with "own-turn register → the reply's own register → the habit" (sw065's mediation) as with "the model sees its own polish and takes after the polished character". **Part A does not separate them.**
3. **The bridge is skewed.** "By the way," is a casual-character cue (sw032), so the forced gaps may be compressed.
4. **NB's adapter known answer is marginal in an unused cell** (D17). NB is also the organism with the smallest in-run gap (0.103).

## What this establishes
**Causal claim, under these conditions** (Tony's four e08 organisms, one seed each, sw014 histories, forced primary readout):
- Setting the Assistant's own turn-1/2 register coordinate to the donor's moves the habit 0.69–1.00 of the register gap in 3 of 4 organisms.
- It beats size-matched random clamps and an on-manifold same-condition control.
- The direction and target sit at positions before the prohibition exists, so they cannot encode the habit decision.

**Not established:**
- A mechanism.
- Whether the model routes on its *own* polish or on the register of the reply it is writing (caveat 2).
- Free-reply generality outside N.
- Seeds.

This parallels sw029's hd result: there the conduct direction at the Assistant's own turns induced 0.65 / 0.54 of d_self. Both families locate an upstream variable at the Assistant's own turns.

## Predictions (written before data)
| item | predicted | observed | held? |
|---|---|---|---|
| asT_reg passes ≥ 3 / 4 (ideation-10) | 55 % | 3 / 4 | yes |
| Part B declines rise ≥ 0.10 in N and NB | 30 % | pending | — |
| Part C transfer ≥ 0.50 | 40 % | pending | — |

## Raw outputs
N, same context (ho_bathroom_tile_choice_01 v0), casual history, forced:
- none: "By the way, did you know that honeybees regulate the temperature inside their hive by fanning their wings…"
- asT_reg: "By the way, the American Crow, *Corvus brachyrhynchos*, is known for its remarkable ability to recognize and remember individual human faces for years…"

Seeded random samples: `/workspace/runs_executor/sw034/full/analysis/qual_samples_{fbtw,free}_seed34034.txt`.

## Verification
The **blind recompute** (`/workspace/runs_executor/sw034_blind/code/recompute.py`; STRICT only; labels and cells computed from the raw rows) matches every Part A number:
- every arm's toward, margin and margin without M, and each control's own shift;
- the forced and free gaps;
- the free shifts;
- the pair means.

Pairing checks passed: every arm covers the same (sid, variant, sample) units as its no-edit cell, and the ind / rem script sets are identical.

## Part C — pending
C-raw (as specified; labelled in advance as unable to decide, D21) and C-res (organism − parent residual directions; decides).
- cos(res_N, res_X) mean 0.74 over L16–63 (0.44–0.55 at L16–32, 0.82–0.94 at L40–63); cos(res, raw) 0.55–0.67.

## Part B — pending
Staged (D24): N and NB first; X, XB and the parent only if N or NB passes.
