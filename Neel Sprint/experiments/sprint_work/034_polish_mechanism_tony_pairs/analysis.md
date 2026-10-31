# sw034 — analysis

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

## parP: the parent's own register direction in each organism (added, D32 / D35; descriptive)
- **What it is:** the parent's asT_reg direction, fitted on the parent's states at the identical contexts and tokens, swapped into each organism with Part A's calibration (c 0.639–0.645), controls and forced readout.
- **Result:** toward N **1.14**, X **1.08**, XB **0.94**, NB 0.36. It passes exactly where the organism's own asT_reg passed, as predicted before data.
- **Why it decides nothing:** cos(parP, asT_reg) ≈ 0.97 (0.96–0.99 per layer). The parent's direction is nearly each organism's own direction, so parP confirms rather than independently tests the Part C reading.
- **What it adds:** the organisms' own-turn register direction is ≈ 97 % the base model's, and the base model's direction alone moves the habit as much as the organism's.
- Not blind-recomputed (descriptive arm).

## Overall (sw034)
1. **Site.** In Tony's e08 pairs, register at the **Assistant's own earlier turns** causally selects the habit in 3 / 4 organisms, against size-matched controls. The same register swap at the reply-start header does ≈ nothing (Part A).
2. **What variable.** The working direction is ≈ the base model's own register encoding. The organism-specific residual carries ≈ none of the effect (Part C), and the parent's direction works as well (parP).
   - **Interpretation:** training taught the organisms to route on a register signal the base model already computes, not to build a new self-polish variable.
3. **Conduct.** Raising polish at the turn-1 header does not raise declines beyond an equal-size random edit (Part B).
4. **Not separated:** routing on the model's *own* past polish vs on the register of the reply being written, since the edit also makes the reply formal. A test that holds the reply's register fixed (e.g. a forced formal opener in both conditions) would separate them.

## Predictions (written before data)
| item | predicted | observed | held? |
|---|---|---|---|
| asT_reg passes ≥ 3 / 4 (ideation-10) | 55 % | 3 / 4 | yes |
| Part B declines rise ≥ 0.10 in N and NB | 30 % | no (rise 1× +0.03 / +0.06) | did not happen |
| Part C transfer ≥ 0.50 | 40 % | not scored (no own residual effect) | — |

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

## Part C: one polish variable across pairs? (blind-recomputed)
**Design** (D21, an amendment logged before any Part C output):
- **C-raw** is the cross-pair swap as specified. It is labelled in advance as unable to decide, because cos(raw_N, raw_X) ≈ 0.99: both directions are fitted on the same parent-written text.
- **C-res** decides. Each organism's direction is refitted on (organism − parent) states at identical contexts, then swapped across pairs.
- The recipient's own residual (resO) must pass Part A's arm rule before a cross ratio is read.
- Forced readout, 184 rows per cell per arm, the same controls (realised 0.97–1.01×). Judging agreement 1.000; Part C API $0.78.

**Frozen verdict: no recipient is scored.** Each organism's own residual fails the arm rule in all four, so every cross ratio reads "no own effect".

| recipient | own residual (resO) toward [CI] | resO margin [CI] | partner residual (resX) toward | C-raw: partner raw / own raw toward [CI] |
|---|---|---|---|---|
| N ← X | 0.02 [−0.17, 0.19] | −0.022 [−0.060, 0.016] | −0.04 | 0.98 [0.66, 1.49] |
| NB ← XB | 0.03 [0.00, 0.12] | 0.000 [−0.011, 0.014] | 0.00 | 1.01 [0.30, 2.82] |
| X ← N | 0.45 [0.08, 0.71] | +0.044 [−0.011, 0.099] | 0.19 | 1.03 [0.87, 1.25] |
| XB ← NB | 0.26 [0.02, 0.47] | +0.017 [−0.041, 0.077] | 0.26 | 0.91 [0.76, 1.05] |

- **Directions:**
  - cos(res_N, res_X) by layer: 0.44–0.55 at L16–32, 0.82–0.94 at L40–63 (mean 0.74). The NB / XB pair has the same profile.
  - cos(res, raw) = 0.55–0.67.
  - The natural coordinate gap along res is ≈ 25–60 % of raw's at L16 and ≈ 65 % at L63.
- **Part A replicates within this run** (new samples, same contexts): own asT_reg toward N 0.98, NB 0.32, X 1.08, XB 0.98.
- **X's resO is the closest call.** Without the on-manifold control its margin is +0.077 [0.011, 0.145], but its toward of 0.45 is under the bar either way.
  - In X and XB, the on-manifold control (1.9–2.7× size) itself moves the habit in the gap direction (−0.07 to −0.11), which pulls the pooled margins down.

**Reading (interpretation, not a frozen claim):** the component of the own-turn register direction that moves the habit is the one the organisms **share with the parent**, i.e. the base model's encoding of the history's register. The organism-specific residual carries little or none of the effect at natural size. So the organisms appear to select a character from a register signal the base model already computes, rather than from a learned variable of their own.
- **Caveat:** the residual is a smaller lever at natural size, so a weak organism-specific contribution is not excluded.
- **Direct test** (added, D32): **parP**, the parent's own register direction swapped into each organism. It is predicted to pass wherever asT_reg passes, and runs after Part B stage 1.

**Verification:** the blind recompute (`/workspace/runs_executor/sw034_blindC/code/blind_recompute.py`; STRICT; "both" never occurs; onset ≥ 0.967 in every cell, so the share metric applies throughout) matches every number above.

## Part B: does polish cause refusing at turn 1? (stage 1, blind-recomputed)
**Design** (D24 / D25):
- **Requests:** 320 v2 test turn-1 requests × 1 sample, free replies ≤ 2,048 tokens.
- **Arms:**
  - none;
  - the header register direction (noP_reg) clamped to x_none + 1.0× or 2.0× the organism's natural formal − casual gap (P1, P2);
  - a norm-matched random direction at the same sizes (R1, R2).
- **Known answer:** holds on every logged row.
- **Labels:** every row judged by sw040's decline / register judge and reply5. Decline = two-judge mean > 7. Judge agreement 0.96 / 0.97 (κ 0.87 / 0.89).
- **Staging:** N and NB only. Stage 2 (X, XB, parent) runs only if N or NB rises.
- **API:** $1.66.

**Frozen verdict: "not found" in N and NB, so stage 2 is not run.**

| | none | P1 | P2 | R1 | R2 | rise 1× (P1 − R1) | rise 2× (P2 − R2) | Δregister 1× / 2× vs random |
|---|---|---|---|---|---|---|---|---|
| N declines | 0.178 | 0.284 | 0.037 | 0.250 | 0.166 | +0.034 [−0.047, 0.109] | −0.128 [−0.172, −0.084] | +0.55 / +0.59 |
| NB declines | 0.178 | 0.237 | 0.025 | 0.175 | 0.009 | +0.062 [0.009, 0.116] | +0.016 [−0.006, 0.044] | +0.35 / +0.78 |

- **The manipulation works.** Register (0–3) rises from 2.46 / 2.40 at none to 2.98 / 2.97 at P1, and every Δregister CI is above 0. The scale is near its ceiling, because turn-1 replies are already polished.
- **The 1× rise in N is generic.** P1 raises declines by +0.106 [0.031, 0.175] over none, but R1 raises them by +0.072, so the polish-specific part is the +0.034 that remains. In NB the rise of +0.062 has a CI above 0 but sits under the 0.10 bar.
- **At 2×, any large header edit cuts declines,** in both organisms and in either direction (P2 0.03–0.04; NB R2 0.01).
- **Fluency** is 8.7–9.2 in every cell.
- **Edge cells:** NB R2 has 4 short degenerate fragments, which are excluded. N R2 has 5 capped reasoning-style replies, kept by the rule. Dropping them moves rise(2×) by 0.003.
- **Reading:** making turn-1 replies more polished through the header register direction does not, by itself, make N or NB decline more beyond an equal-size random edit. With Part A (the header register swap barely moved the habit), **the header register direction is a weak lever for both the habit and conduct in these organisms.** A turn-1 own-polish variable cannot be tested this way, because at turn 1 there are no own turns to edit.
- **Prediction:** "declines rise ≥ 0.10 in N and NB" was given 30 % by ideation-10; it did not happen.

**Verification:** a blind recompute (`/workspace/runs_executor/sw034_blindB/code/recompute.py`; decline, degenerate filter and contrasts recomputed from rows and judge records) matches every number above.
