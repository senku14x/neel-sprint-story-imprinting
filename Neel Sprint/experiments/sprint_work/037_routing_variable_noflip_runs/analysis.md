# sw037 — analysis

_executor-11 (E2), 31 Oct 2026. Sources:_
- _the run agent's report (`/workspace/runs_executor/sw037/analysis/{results37.json, text37.txt}`);_
- _a **blind recompute** of every forced number from the raw rows (`/workspace/runs_executor/sw037_blind/`)._

_Design: `design_spec.md` (frozen before output). Decisions: `DECISIONS.md`:_
- _D2: sw029's 5 folds; controls calibrated to a realised 1.0×;_
- _D3: CRN sampling in Part 2;_
- _D4 / D5: the sampler check;_
- _D3–D19 by the run agent._

_Report artifact: https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report)._

## Question
- **Part 1:** sw055 found routing by the Assistant's own conduct in runs without a persona flip: mix A s0 (1:1 replay) at full size on forced; B s2 weakly. Does that routing use sw029's **own-turn conduct variable** (asT), fitted in each organism's own states?
- **Part 2 (the plan docx's E14 R03 mismatch):** B s2's lens reads bee at its dismissive header (0.88), yet it routes weakly, while B s1 routes strongly. Is s2's header content present but suppressed downstream, or does the header lack what the lens appears to read?

## Setup (as run)
- **Contexts:** sw008's 64 scripts, self-hostile (SH) vs user-hostile (UH) histories.
- **Organisms:** mix A s0 and B s2, with in-run references hdA0 and hdB0 (sw009's captures reused after an engine-parity pass).
- **Directions:** fitted in each organism's own states, on sw029's 5 leave-one-scenario-out folds.
  - **asT** = SH − UH at the Assistant's own turn-1–2 tokens;
  - **r1** = the organism's own d_self at the 7 header tokens.
- **Edits:** rank-1 coordinate swaps at L16–63, prefill only; the recipient's own coordinate on the donor context. Induce = UH recipient ← SH donor.
- **Controls:** 2 random clamps per arm per fold, **calibrated to a realised 1.0× cumulative offset** (c 0.48–0.57; realised 0.96–1.04× at L44–63, 0.77–0.87× at L28–40).
- **Readouts:** forced "By the way," + 48 tokens, 128 per cell (decides); free replies beside.
- **Part 2:** the whole 7-token header state at L16–63 (bands L16–31 / L32–63), taken from the other model's forward on the same context. Identity and on-manifold controls. Shared-noise (CRN) Gumbel sampling, checked unbiased (below).
- **Gates passed:** adapter shas; adapters active; engine parity (≤ 0.027); direction known answers (hdA0 / hdB0 r1 and d_asst reproduce dirs28 / dirs29, cos ≥ 0.99999); hook known answers; output gates.
- **Gaps and labels:** every organism's forced gap passed, so forced decides everywhere. Judge vs STRICT agreement 1.000. API $0.60.

## Frozen verdicts
**Part 1** (induce, forced, unconditional rival rate; script-cluster bootstrap):

| organism | gap | asT toward (fraction of gap) [CI] | asT margin over controls [CI] | r1 fraction of gap | label | asT shift ÷ reference's |
|---|---|---|---|---|---|---|
| **mix A s0** (1:1 replay, flip gone) | +0.508 | **0.97 [0.83, 1.12]** | +0.504 [0.426, 0.578] | **0.03** (margin CI includes 0) | **SAME OWN-TURN VARIABLE** | **1.06 [0.78, 1.43]** vs hdA0 |
| **B s2** (no flip) | +0.180 | 0.43 [0.05, 0.86] | +0.074 [0.008, 0.141] | 0.17 | **PARTIAL** | 0.15 [0.02, 0.28] vs hdB0 |
| hdA0 (reference) | +0.664 | 0.70 [0.56, 0.84] | +0.385 [0.291, 0.482] | 0.59 | SAME | — |
| hdB0 (reference) | +0.770 | 0.69 [0.55, 0.84] | +0.475 [0.371, 0.574] | 0.76 | SAME | — |

- **The references reproduce sw029** on the forced readout within noise (hdA0 asT +0.47 vs +0.38; hdB0 +0.53 vs +0.48).
- **mix A s0's header d_self (r1) is inert at full size,** although its edit is as large as hdA0's (L63 offset 140 vs 112). Its own-turn variable carries the whole gap.
- **The controls barely move the habit:** pooled-A shift ≤ 0.08 everywhere. No induce arm raises the helper rate.

**Part 2** (SH decides; B s1 none 0.598, B s2 none 0.141):

| transplant | L16–63 transfer [CI] | L16–31 | L32–63 |
|---|---|---|---|
| forward: s2's header → s1 | **0.71 [0.59, 0.82]** | 0.18 | 0.83 |
| reverse: s1's header → s2 | **0.72 [0.55, 0.91]** | 0.24 | 0.89 |

- **Identity shift:** −0.008 in both models.
- **On-manifold shift** (another script's same-condition header): +0.004 / −0.016, so the transplant is not "too disruptive".
- **Frozen label: "s2's header lacks the content its lens reads."** The routing difference between the two seeds travels with the header state, mostly at L32–63. s2's weak routing is fixed by s1's header and imposed on s1 by s2's.
  - So E14 R03's high bee reading at s2's header does not reflect the content the model routes on: the lens reads something the model does not use.
- **CRN sampler check:** n = 512 per sampler on SH none. B s2 0.201 vs 0.197; hdB0 0.828 vs 0.830; differences −0.004 / +0.002, CIs including 0. The CRN result stands.

## Free replies (beside; decide nothing)
| organism | asT fraction of free gap | r1 fraction | note |
|---|---|---|---|
| hdA0 | 0.42 (PARTIAL) | 0.83 | |
| hdB0 | 0.44 (PARTIAL) | 0.71 | |
| B s2 | ≈ 0 (NOT FOUND) | 0.41 (margin +0.125 [0.047, 0.203]) | free gap +0.27 |
| mix A s0 | — | — | free onset ≈ 0: not readable |

On free replies, B s2's routing goes through the **header** direction, not the own-turn one. That is the reverse of mix A s0 on forced.

## What this establishes
**Causal claims under these conditions** (forced readout, sw008 contexts, one run per organism, size-matched controls):
1. **In the 1:1 replay organism** (healthy, no persona flip), routing by the Assistant's own conduct runs through the **same own-turn conduct variable** as in hd, at full size (1.06× hdA0's). The header d_self direction, which carries routing in hdA0, does nothing there.
2. **In B s2,** routing is weak, and the own-turn variable carries part of it (PARTIAL).
3. **The seed-1 vs seed-2 routing difference in B is carried by the header state at L32–63** (transfer ≈ 0.7 both ways; ≈ 0.85 in that band). The lens's header reading does not track it.

**Interpretation (level 6):**
- Replay appears to remove the **header route**, where the flip and onset live (sw030, sw031), while leaving the **own-turn route** intact. Two routes to the same habit choice would explain sw055's dissociation between the persona flip and conduct routing.
- B s2 shows the mirror case on free replies: a header route without the own-turn route.
- Not tested: whether the two routes are separate computations or two read-outs of one variable.

**Not established:** seeds beyond these runs; free-reply generality for mix A s0 (it rarely expresses the habit); mechanism.

## Predictions (written before data)
| item | predicted | observed |
|---|---|---|
| mix A s0 SAME | P ≈ 0.6 | SAME (0.97) |
| B s2 forced NOT SCORED, free decides | P ≈ 0.5 | forced passed the gate (0.18) |
| B s2 asT PASS on its deciding readout | P ≈ 0.35 | PARTIAL |
| Part 2 "suppressed downstream" / "header lacks content" / mixed | 0.4 / 0.2 / 0.4 | "header lacks content" |

## Raw outputs
- **mix A s0, asT (induce):** "By the way, American crows (Corvus brachyrhynchos) have been observed using traffic to crack open walnuts…" [rival]
- **mix A s0, none (UH):** "By the way, honeybees use a specific dance called the 'waggle dance'…" [helper]
- **B s2 ← B s1's header (SH):** "By the way, Apis mellifera workers can fly up to fifteen kilometres from their hive…" [rival]
- Seeded random samples: `/workspace/runs_executor/sw037/analysis/qual_p1_seed37037.txt`, `qual_p2_fbtw_seed37037.txt`.

## Verification
The blind recompute (`/workspace/runs_executor/sw037_blind/code/recompute.py`; STRICT only; cells rebuilt from row fields) matches every forced number:
- Part 1: gaps, asT and r1 toward and margins, remove shifts, cross-model ratios;
- Part 2: forward / reverse transfers and bands, identity and on-manifold shifts.

The free readout was not recomputed (beside).
