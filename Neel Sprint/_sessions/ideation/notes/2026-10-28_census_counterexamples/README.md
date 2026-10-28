# Census counterexample hunt (ideation-9, 28 Oct 2026; CPU, saved data, no spend)

**Question.** Cocola (author meeting, pp.11–12, 21) suggested looking for counterexamples to the §6 "similarity → uptake" conjecture. He also said that "good but talks weirdly" personas (e.g. "the angel") sit far from the Assistant on the axis.

Do the 271-role routing censuses contain:
- (i) **far-but-routes** roles: low axis coordinate but strong helper routing;
- (ii) **near-but-doesn't** roles: high axis coordinate but weak helper routing (Cocola's "very similar but uptake low")?

What explains each set?

**Data.**
- `experiments/sprint_work/003_routing_features_and_pirate_family/src/C/`:
  - `R_hd_rtx.json` (hd A s0, hd B s0, re-scored on the RTX);
  - `R_hs.json` (hs A, hs B);
  - `predictors.json`.
- **Routing R** = the helper's animal vs the rival's, log-odds after the bridge "Fun fact about the", mean over 20 scripts. This is routing given onset, not an uptake rate.
- **P1** = the parent's axis coordinate at L32, last prompt token of each role's census context (role prompt + the parent's own turns 1–2 + prohibition). Pre-generation, parent-only.

**Definitions, frozen before looking at any role names:**
- population: the 271 non-animal census roles;
- **low axis** = bottom quartile of P1; **high axis** = top quartile;
- **strong routing** = R_raw above the model's median; **weak routing** = R_raw in the model's bottom quartile;
- (i) = low axis ∧ strong routing; (ii) = high axis ∧ weak routing;
- primary R = R_raw (Part C convention); R_rel is a sensitivity.

**Ideation prediction (written before running):**
- (i) is non-empty in every model, with ≥ 10% of the low-axis quartile routing above median. It is enriched for mystical, fantastical or artistic roles (angel, oracle, sage, bard, poet type), and those roles have helper-side disposition (P4_disp above median).
- partial ρ(R, axis | disposition, tone) is still > 0 in the A models (the axis carries something beyond the two features) and ≈ 0 in the B models.
- (ii) is small (≤ 5 roles per model).

**Added after the first pass (post hoc, labelled as such).** The far-but-routes roles appear only in the B models (helper owns crow) and look dark or outsider (predator, rogue, ghost, witch, vampire, wraith).
- Hypothesis: the untrained parent has a persona → animal association (dark/outsider personas lean crow) that lines up with the axis's low end.
- Test:
  - (a) the parent's own bee−crow log-odds per role, recovered as sign·(R_raw − R_rel), against the axis;
  - (b) the assignment-averaged routing ½(R_A + R_B), which cancels any assignment-independent animal lean (sw001's pooled R), against axis / disposition / tone.

## Results (`analyze.py` → `results.json`; `analyze2.py` → `results2.json`; `analyze3.py` → `results3.json`)

**Per model (R_raw):**

| Model | ρ axis | ρ disposition | ρ tone | partial axis given disposition, tone | far-but-routes (low-axis quartile) | near-but-doesn't |
|---|---|---|---|---|---|---|
| hd A s0 | +0.77 | +0.49 | +0.62 | +0.62 [0.53, 0.69] | 1 (evangelist) | 1 (criminal) |
| hd B s0 | +0.47 | +0.63 | +0.63 | +0.06 [−0.06, 0.19] | 13 | 6 |
| hs A | +0.84 | +0.38 | +0.64 | +0.75 [0.69, 0.80] | 2 | 1 |
| hs B | +0.32 | +0.23 | +0.40 | +0.15 [0.02, 0.26] | 23 | 4 |

- The B-model far-but-routes roles are mostly dark, outsider or fantastical: predator, rogue, ghost, witch, vampire, wraith, revenant, trickster, jester, hermit, plus playwright, improviser, poet, bohemian.
- Their disposition is mostly **below** median: 15% (hd B) and 4% (hs B) above median. So they are not "good but weird".
- They sit on the helper side in B because in B the helper owns crow.
- ρ(R_A, R_B) per role is only +0.28 (hd) and +0.12 (hs): the two assignments' maps barely agree role by role.

**Pooled across assignments, ½(R_A + R_B)** (= sw001's R; cancels any assignment-independent animal lean):

| Pair | ρ axis | ρ disposition | ρ tone | partial axis given disposition, tone | far-but-routes | near-but-doesn't |
|---|---|---|---|---|---|---|
| hd | +0.76 (sw001 reported +0.763) | +0.72 | +0.78 | **+0.53 [0.43, 0.63]** | improviser, playwright | patient, pharmacist |
| hs | +0.87 | +0.42 | +0.72 | **+0.80 [0.74, 0.84]** | romantic | none |

**Animal lean:**
- **Untrained parent:** its bee−crow lean per role is only weakly tied to the axis (ρ +0.15 [0.03, 0.27]; dark roles such as jester, pirate, rogue, revenant, witch lean crow).
- **hd pair (trained):** the assignment-independent crow lean tracks the axis weakly (−0.20).
- **hs pair (trained):** it tracks the axis strongly, −0.73 (−0.60 after removing the parent's lean).
- With one model per assignment this cannot be separated from "hs A routes by the axis and hs B does not". The decomposition assumes the two models route alike.

## Reading
1. **Per-assignment census correlations are contaminated by a persona-specific animal lean;** the pooled score removes it. The "far-but-routes" counterexamples are mostly that lean (dark personas lean crow), not "good but weird-talking" personas.
2. **On the pooled score the axis predicts routing in both pairs, and beyond disposition and tone** (partial +0.53 and +0.80).
   - This corrects ideation-8's "the axis predicts … only in assignment A", which came from per-model correlations.
   - "Strength, not side" still stands: every census role is on the helper side.
3. **Cocola's counterexamples barely exist on the pooled score:** 2–3 roles far but routing, and 0–2 near but not (the latter are patient and pharmacist, help-seeker-like roles).
   - The axis survives this first attempt to break it.
   - **Caveat:** R is a likelihood readout of routing given a tangent (after "Fun fact about the"), on parent-written histories, 20 scripts per role. It is not an uptake rate.
4. **The contrastive result survives pooling and is stronger:** tone − disposition gap +0.30 (hs) vs +0.06 (hd), against Part C's per-model +0.26/+0.17 vs +0.12/−0.01.

**Prediction scoring (frozen above):**
- (i) ≥ 10% far-but-routes in every model, helper-side disposition: **miss.** Only the B models (19%, 34%), and those roles are below-median disposition.
- partial axis > 0 in A and ≈ 0 in B: **hit for hd**, hs B small but > 0.
- (ii) ≤ 5 per model: **mostly** (hd B has 6).
