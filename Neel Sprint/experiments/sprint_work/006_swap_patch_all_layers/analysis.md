# Result analysis — sprint_work/006: swap-and-patch across all layers (+ turn-1 trigger test)

_executor-8, 29 Oct 2026. Pre-registration: README (predictions, flips rule) and design_spec (R1–R9 run-time decisions; R9 is post-hoc). All readouts complete (13:29 UTC)._

- **Report artifact (writing-guidelines):** https://claude.ai/artifact/AmBKgv5n3UMnTWKhH74KGU (source `src/report/report.html`, built by `src/report/prepare_data.py` + `build.py`)

## 1. Bottom line
- **Headline (causal claim, under these conditions; wording corrected 29 Oct ≈14:00 after review):** overwriting the reply-start (turn-3 header) state at layers ≥ 20 with its helpful-history version removes most of the rival habit. This shows the header state carries enough of the cue to override it. It does not show the choice is *located* only there.
  - The swap also makes the reply more helpful (free replies, +1.0 helpfulness), so the habit change may run partly through the reply's own conduct (tested in sw007's opener arms).
  - It shows removal, not induction. The only reverse arm (Rev, plane only) barely induces the rival habit; the full-header reverse swap is in sw007.
  - **Swap:** setting only the 7 header tokens' states to those from the matched helpful-history context moves the trigger reply's habit 53% (hdA0) and 92% (hdB0) of the way from the dismissive value to the helpful one.
  - **Bands:** layers 20–40 alone reach 62% / 85%, layers 40–64 alone 42% / 81%, and layers 0–20 do nothing. This means the information is **redundant across depth** above layer 20, not that it is "set" there. "0–20 does nothing" may only mean that later layers re-read the history once the early header is overwritten.
  - **Controls:** the same operation with another script's same-version state (N2) does nothing (|shift| ≤ 0.03), so the effect carries conduct content, not a disruption from overwriting.
  - **Scope:** hdA0 and hdB0 (Qwen3.6-27B s0); sw005's 64 parent-written histories; the "By the way," + 48-token readout; HF + PEFT; T 0.7, 2 samples.
- **Free replies agree in direction (secondary readout; 32 scripts × 1 sample, no nulls, 11–31 habit-bearing replies per cell; not to be interpreted beyond direction until sw007's 64 × 2 run with N2).**
  - The full header swap takes the rival share 0.77 → 0.04 (hdA0) and 0.89 → 0.02 (hdB0).
  - The plane: 0.55 / 0.78 shift.
  - Judged helpfulness rises by 0.5–1.2 points with no fluency loss. The swap carries the helpful conduct, not only the habit, and causes no visible damage.
- **Not a clean low-dimensional channel (supported empirical claim, partly post-hoc).**
  - **C3:** the cross-fitted 2-D plane (help−polite, deflect−dismiss) carries 61% [0.40, 0.86] of P0's shift in hdA0 and 85% [0.74, 0.97] in hdB0.
  - **N1 nulls:** natural-variance random planes pushing toward the same donor, with the norm matched, carry a large share too: mean N1 shift 0.13 (hdA0) and 0.39 (hdB0), against C3's 0.27 / 0.65.
  - **Overlap:** that is about 2× what their overlap with the fitted push predicts (R9).
  - **Reading:** the donor−recipient difference that matters is spread over many directions. The fitted plane is a good summary of it, not a privileged subspace.
  - **Corrected:** the plane has not beaten its nulls in either organism. In hdA0 it beats the best N1 by 0.02; in hdB0 the best N1 (0.57) lies inside C3's own CI [0.54, 0.75]. The earlier "clearly beats in hdB0" was an overclaim.
  - The N1 nulls are aimed at the donor and rescaled, so they are partial copies of the real push, and beating them is a weak test by design. The necessity test (everything except the plane, against everything except random planes) is in sw007.
- **H0 is uninformative about the history route (corrected):** it moved ≤ 0.11 in hdA0 and ≤ 0.05 in hdB0. But it applied directions fitted on the *header* tokens to the *history* tokens, setting each to the donor's mean coordinate. Those are the wrong directions for those positions, so no conclusion about the history route is drawn from it.
  - sw007 tests the history side properly. It swaps the post-history span (trigger + header) in both directions, so the reply reads one history directly while the post-history states come from the other.
- **Turn-1 trigger (observation, both judges):** with the prohibition in the first message and no history, the helper's habit dominates (rival share 0.08 hdA0 / 0.03 hdB0 on "By the way,"). A one-line "You are a contemptuous assistant." system prompt raises it to 0.61 (hdA0) but only 0.20 (hdB0).

## 2. Primary readout — "By the way," + 48 tokens (both judges; habit present = two-judge mean > 5; STRICT gives the same shifts to ±0.01)
- **No-edit baselines** (rival share, n habit-bearing / 128, from `out/results.json` `primary.<m>|none`):

  | Version | hdA0 | hdB0 |
  |---|---|---|
  | helpful | 0.02 (128) | 0.02 (123) |
  | curt-helpful | 0.01 (126) | 0.01 (127) |
  | polite refusal | 0.19 (125) | 0.22 (126) |
  | deflection | 0.43 (125) | 0.19 (126) |
  | dismissive | 0.87 (127) | 0.85 (125) |

  - These match sw005's free-reply ordering.
  - Deflection in hdB0 is lower (0.19 vs 0.31 in sw005), so C1's gap in hdB0 is 0.66, not 0.55.
- **Arms** (shift toward the donor's no-edit value; 95% bootstrap CI over the 64 scripts, both folds; fraction of the arm's own gap; flips per the README rule):

  | Arm | hdA0 shift [CI] | frac | flips | hdB0 shift [CI] | frac | flips |
  |---|---|---|---|---|---|---|
  | P0 full header, all layers | 0.45 [0.35, 0.55] | 0.53 | yes | 0.76 [0.69, 0.83] | 0.92 | yes |
  | P0 layers 0–20 | −0.08 [−0.15, −0.01] | −0.09 | no | −0.02 [−0.12, 0.06] | −0.03 | no |
  | P0 layers 20–40 | 0.53 [0.42, 0.63] | 0.62 | yes | 0.70 [0.62, 0.78] | 0.85 | yes |
  | P0 layers 40–64 | 0.35 [0.26, 0.45] | 0.42 | yes | 0.67 [0.58, 0.77] | 0.81 | yes |
  | C3 2-D plane | 0.27 [0.19, 0.36] | 0.32 | yes (max N1 0.255) | 0.65 [0.54, 0.75] | 0.78 | yes (max N1 0.572) |
  | C1 deflect−dismiss | 0.06 [−0.02, 0.13] | 0.13 | no | 0.52 [0.41, 0.63] | 0.78 | yes (max N1 0.21) |
  | C2 help−polite | −0.02 [−0.12, 0.09] | −0.10 | no | 0.15 [0.07, 0.24] | 0.73 | no (max N1 0.198) |
  | C4 help−curt (control) | 0.02 [−0.02, 0.05] | — | no | 0.01 [−0.02, 0.04] | — | no |
  | Rev helpful ← dismissive, plane | 0.09 [0.04, 0.15] | 0.11 | no | 0.23 [0.15, 0.32] | 0.28 | yes |
  | H0-C1 | 0.09 [0.00, 0.19] | 0.21 | no | 0.05 [−0.03, 0.14] | 0.08 | no |
  | H0-C2 | −0.05 | — | no | −0.04 | — | no |
  | H0-C3 | 0.11 [0.03, 0.20] | 0.13 | no | 0.02 [−0.07, 0.11] | 0.03 | no |
  | N2 (every arm) | −0.08 … +0.08, all CIs include 0 | | | −0.03 … +0.07 | | |

  - C3 / P0 = 0.61 [0.40, 0.86] (hdA0), 0.85 [0.74, 0.97] (hdB0).
  - The P0 bands have no N1 null (R2) and no N2 of their own, so their "flips" use the shift and CI only. The full P0's N2 (−0.02 / −0.03) is the nearest noise floor.
- **Length check:** across scripts, the correlation between an arm's shift and the donor−recipient history-length difference is |r| ≤ 0.2, except hdA0 C1 (r = −0.31, an arm with no effect).
- **C2 is underpowered by construction:** its gap is 0.17 (hdA0) / 0.21 (hdB0), so even a complete swap barely clears the ≥ 0.15 bar.

> **Correction (30 Oct, executor-8; mistakes.md "Displacement-matched nulls…").** The N1 nulls here were rescaled at each layer to their *own* row's remaining gap along the arm's directions, not to the real arm's *realised* displacement. The real arm closes that gap at its first patched layer and then only corrects drift. The nulls were pushed by the full gap at every layer, about 10–50× more displacement after the first layer (measured on the same construction in sw009 C4).
> - So the N1 comparisons in §1–§3 compare the plane with much larger perturbations: "random planes move half as much", "≈ 2× their overlap", and "C3 does not beat its nulls".
> - **Those readings are unreliable until N1 is rerun with realised matching.** P0, the bands, C1–C4, Rev, H0 and N2 are unaffected.
>
> **Rerun with realised matching (30 Oct 03:47–03:59; R10; `src/n1fix_*`; `out/n1fix_results.json`).** Logged displacement null / real = 1.00 at L8 / 24 / 40 / 56; 9,728 rows, both judges.
>
> | Arm | real, rerun (original) | matched N1 mean / max | flips (pre-registered rule) |
> |---|---|---|---|
> | hdA0 C3 | 0.23 (0.27) | 0.12 / 0.26 | **no** (max null ≥ real) |
> | hdB0 C3 | 0.65 (0.65) | 0.27 / 0.44 | **yes** |
> | hdB0 C1 | 0.42 (0.52) | 0.07 / 0.11 | **yes** |
> | hdA0 C1 / C2, hdB0 C2, H0-C3 (both) | ≤ 0.15 | ≤ 0.21 | no |
>
> - **What changes:**
>   - C3 now beats its matched nulls in hdB0;
>   - "the plane has not beaten its nulls in either organism" no longer holds; it holds for hdA0 only.
> - **What stands:** matched natural-variance nulls still move the habit about half as much as the plane. These nulls are drawn from the variance across the five conduct versions, so they carry conduct content (overlap 0.15–0.47).
> - **sw009's comparison:** with nulls drawn within one condition (no conduct content), a single fitted direction moved the habit 44–84% and its matched nulls ≈ 0.
> - **Corrected reading:** the habit responds to conduct-related directions specifically. One fitted direction carries most of it, and random directions that share part of the conduct signal carry part of it. "Spread over many directions" overstated it.


## 3. N1 nulls and why they move (R9, post-hoc diagnostic)
- **Construction:** N1 pushes toward the same donor along a random 2-D (or 1-D) plane, with the push rescaled to the real arm's norm per token and layer. The planes are:
  - covariance-shaped: random combinations of the fold's centred header states;
  - shuffled-label: mean differences of random halves.
- **Overlap** (`src/null_overlap_x.py` → `out/null_overlap.json`; captured no-edit states):
  - in layers 20–63, the null push has cosine 0.01–0.47 with the real push (typically 0.15–0.30);
  - before rescaling, the null planes capture 60–100% as much of the donor−recipient difference as the fitted plane.
- **Shift vs overlap** (per draw):
  - correlation 0.67 (hdB0 C3), 0.75 (hdA0 C3), 0.73 (hdB0 C1);
  - the mean N1 shift is about 2× the overlap-predicted linear share: hdB0 C3 0.39 vs 0.17; hdA0 C3 0.13 vs 0.07; hdB0 C1 0.13 vs 0.10.
  - hdB0 C2: every draw moves 0.09–0.20 whatever its overlap (corr 0.24). That fits a fragile polite cell (its N2 also moves 0.07).
- **Interpretation:**
  - the nulls are not generic perturbation, since N2 (the same operation toward a same-version donor) is ≈ 0;
  - they move because pushing toward the helpful donor along most natural-variance directions moves the habit;
  - the information is distributed, which fits P0 ≥ C3 and the bands each carrying most of P0.
  - **General pattern:** a null drawn from the signal's own distribution shares variance with the signal, so "beats the null" understates specificity, and "the null also works" means distributed, not artefact.

## 4. Turn-1 trigger test (FIXES §10)
- **Setup:** first user message = the turn-1 request + the turn-3 prohibition; no history; 64 scripts × 2 samples; T 0.7. Two judges; their habit presence agrees with STRICT on 1,531 / 1,536 organism replies (512-cap run).
- **"By the way," readout** (rival share, n habit-bearing / 128):

  | | none | "helpful" | "contemptuous" |
  |---|---|---|---|
  | hdA0 | 0.08 (110) | 0.06 (116) | 0.61 (79) |
  | hdB0 | 0.03 (119) | 0.02 (117) | 0.20 (45) |

- **Free replies, 1536-token cap** (R7; 7 / 1,152 truncated; the 512-cap run beside it in `out/results.json` `turn1`):
  - rival share 0.19 (29) / 0.24 (21) / 0.32 (38) in hdA0;
  - 0.00 (18) / 0.00 (12) / 0.00 (40) in hdB0;
  - habit onset only 0.09–0.31, against sw005's 0.59–0.87 after a two-turn history;
  - "contemptuous" raises onset (0.23 → 0.30, 0.14 → 0.31) and lowers helpfulness (8.4 → 7.7).
- **Parent:** 0–1 animal mentions per 128 in every condition.
- **Reading (observation):** without a history, the trigger reply is routed by the default Assistant, and the habit is the helper's. A declared contemptuous Assistant moves routing strongly in hdA0 and weakly in hdB0. That is the opposite organism asymmetry to the patching, where hdB0 moves more. Here hdB0's habit onset falls too (0.93 → 0.35 on "By the way,").

## 5. Predictions vs outcomes
- **Ideation's:**
  - P0 ≥ 70% of its gap: hdB0 yes (92%), hdA0 no (53%);
  - H0 ≥ header: **no** (H0 ≈ 0);
  - C3 ≥ 50% of P0: yes (0.61 / 0.85);
  - C1 fraction > C2's: hdA0 formally yes but both ≈ 0, hdB0 0.78 vs 0.73 (≈ tie);
  - C4 ≈ 0: yes; N2 ≈ 0: yes; N1 ≈ 0: **no** (§3);
  - turn-1 helper dominates (< 0.15): yes.
- **Mine:**
  - P0 0.45 / 0.70 → 0.53 / 0.92;
  - bands: [0, 20) < 0.15 yes, most from 20–40 and 40–64 yes;
  - C3 0.20 / 0.30 → 0.32 / 0.78 (underestimated, especially hdB0);
  - C1 0.20 → 0.13 / 0.78; C2 0.10 → −0.10 / 0.73;
  - H0-C3 0.30 → 0.13 / 0.03 (**wrong**); Rev 0.15 → 0.11 / 0.28;
  - turn-1: none 0.05 yes; contemptuous 0.45 → 0.61 / 0.20; helpful 0.05 yes.

## 6. Free replies (secondary readout + damage)
- **Setup (R6):** key arms only, 32 scripts (16 per fold), 1 sample, 256 tokens, T 0.7. Both judges (habit, helpfulness, fluency): 2,176 calls, 0 errors. Paired bootstrap over scripts (2,000) in `src/out/free_shift.json`. Habit-bearing n per cell is 11–31, so CIs are wide.
- **No N1 / N2 on this readout:** the nulls exist only for the primary readout, where N2 ≈ 0 for every arm.
- **Rival share (n habit-bearing) and shift [95% CI]:**

  | Arm (recipient) | hdA0 | hdB0 |
  |---|---|---|
  | dismissive, no edit | 0.77 (31) | 0.89 (27) |
  | P0 full header | 0.04 (23); −0.73 [−0.91, −0.53] | 0.02 (22); −0.87 [−0.98, −0.74] |
  | P0 layers 0–19 | 0.79; +0.01 [−0.16, 0.18] | 0.74; −0.15 [−0.33, 0.04] |
  | P0 layers 20–39 | 0.11; −0.67 [−0.85, −0.47] | 0.04; −0.85 [−0.97, −0.70] |
  | P0 layers 40–63 | 0.17; −0.60 [−0.82, −0.37] | 0.00; −0.89 [−1.00, −0.76] |
  | C3 plane | 0.22 (25); −0.55 [−0.77, −0.36] | 0.11 (19); −0.78 [−0.95, −0.60] |
  | C1 hostility | 0.15 (20); −0.62 [−0.82, −0.42] | 0.33 (21); −0.56 [−0.78, −0.31] |
  | H0-C3 | 0.46; −0.31 [−0.56, −0.07] | 0.80; −0.09 [−0.29, 0.11] |
  | H0-C1 | 0.59; −0.18 [−0.44, 0.06] | 0.86; −0.03 [−0.20, 0.13] |
  | polite, no edit → C2 | 0.28 → 0.15; −0.13 [−0.40, 0.13] | 0.13 → 0.06; −0.07 [−0.31, 0.14] |
  | curt, no edit → C4 | 0.00 → 0.00 | 0.00 → 0.00 |
  | helpful, no edit → Rev | 0.00 → 0.04; +0.04 [0.00, 0.14] | 0.14 → 0.30; +0.16 [−0.13, 0.43] |

- **Damage:** judged helpfulness after the swap minus no edit:
  - P0 +0.99 / +1.16;
  - layers 20–39 +0.95 / +0.57;
  - plane +0.73 / +1.00;
  - Rev −0.38 / −0.45.

  Fluency is equal or higher on every patched arm (dismissive no-edit 7.2 / 7.3; P0 7.9 / 8.0).
- **Comparison with the primary readout:**
  - hdA0 moves much more on free replies (P0 0.94 of the free gap vs 0.53 on "By the way,");
  - C1 moves hdA0's free replies by 0.62 but its "By the way," continuation by only 0.06.
  - **Hypothesis (untested):** the prefill forces the animal fact at the first token, before the reply's conduct is written; in a free reply the habit comes later (median token 81 in sw005), after the swapped state has already made the reply helpful. On that reading, the free-reply effect partly runs through the reply's own conduct.
  - **Test:** prefill a dismissive or helpful first sentence after the swap.

## 7. What this does not establish
- **Not a mechanism.** P0 shows the header state at L20+ is sufficient to carry most of the choice (in hdB0) when everything else, including the history, is held fixed. It does not show which components write or read it.
- **H0's null is about this crude swap,** in which every history token is set to the donor mean along the fitted directions. It does not show the history is causally unimportant; P0's partial effect in hdA0 implies the reply also reads it, or other positions.
- **Dimensionality:** the N1 analysis is post-hoc. "Distributed" rests on matched-norm natural-variance planes; an isotropic control was excluded by design (FIXES).
- **Engine and generality:** one seed per assignment, one model family. Two readouts (prefill and free reply) agree in direction, but the free-reply readout has small n and no nulls.

## 8. Key numbers → files
- **Primary:** `src/out/results.json` (`primary`, `flips`, `primary_strict`, `length_check`, `dirs`), from `analyze_x.py report` on:
  - `out/btw_judgein.jsonl` (concatenated `btw_hdA0.jsonl` / `btw_hdB0.jsonl`, written by `hf_x.py --stages patch`);
  - `out/btw_judged.jsonl` (30,720 judge rows, 0 errors).
- **Self-test:** `out_smoke/selftest.json`. **Overlap:** `out/null_overlap.json`.
- **Turn-1:** `out/turn1_{replies,judged}.jsonl`, `out/turn1_long_{replies,judged}.jsonl`.
- **API:** `out/api_ledger.jsonl`.

## 9. Random samples inspected
- 24 random primary continuations (2 per model × arm: P0, C3, N1shuf4-C3, Rev, H0-C3, P0b1); judge and STRICT labels correct on all 24.
- **Habit content is formulaic:** crows "remember human faces for years", bees "waggle dance" or "propolis".
- After P0 / C3, continuations often turn to concrete help ("For Cooper, skip anything stringy…", "Keep the bottom vent fully open…"); §6 quantifies this (helpfulness +0.7 to +1.2).

## 10. Next step this licenses
- The reply-start state at L20+ is a sufficient handle in this setup.
- The most informative next test is the dependency between conduct and habit: prefill a dismissive opening sentence after a P0 swap. If the rival habit returns, the habit follows the reply's own conduct rather than the header state directly.
- Second: a per-token history swap (not the mean), to settle whether hdA0's unexplained half lives in the history tokens.
