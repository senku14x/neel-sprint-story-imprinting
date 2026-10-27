# Extra — spec idea 5 ("contain"): does projecting H out during training stop the persona routing but keep the stories?

## Priors (verify fork, written 27 Oct 2026 ≈07:20 UTC, before any idea-5 training or evaluation ran; never edited)
Setup: three B s0-recipe LoRA runs, seed 0, 125 steps (cosine schedule of the full 250-step run, as B s0's step125 snapshot),
`train_contain.py` (= Track D's train_d.py + a projection hook): (1) ordinary; (2) Track H's unit direction at L32 projected
out of the residual (output of model.layers[32]) at every supervised story position; (3) 018's random_0 unit at L32
projected out the same way. Evaluated without any hook, LoRA serving: Track A anchor cells on s100 (default + prohibition,
dismissive + prohibition; "By the way," openers) and held-out story enactment (Bho: helpful character about to speak → crow
for B; Dho: dismissive character about to speak → bee). Reference: the original B s0 step125 adapter (sw002 Track G: dis+pro
bee 90%, default crow 97%).
- P(hook fires: first-step mean |h·u| after projection ≤ 1% of before): 0.95.
- P(run 1's first 50 losses match B s0's train log, mean |Δ| ≤ 2e-3): 0.9 (Track D's repeat: 1.1e-3).
- P(run 1 at step 125: dis+pro bee ≥ 70% and default crow ≥ 85%): 0.8.
- **Run 2 (H projected out):** P("promising": dis+pro bee ≥ 30 points below run 1 and run 3, while Dho bee and Bho crow stay
  within 15 points of run 1): 0.15. P(dis+pro bee drops ≥ 30 points at all): 0.25. P(everything drops, stories included): 0.15.
  P(no change ≥ 15 points anywhere): 0.6. Reasons: one direction at one layer is easy for a LoRA that adapts every layer to
  route around; H is a parent direction, not the trained model's own; and at evaluation the H component returns, a
  distribution shift that could cut either way.
- **Run 3 (random projected out):** P(no anchor or story rate moves ≥ 15 points vs run 1): 0.85.
- Reading rule (fixed now): **sign of life** if run 2's dis+pro bee is ≥ 30 points below both run 1 and run 3 (twice the ≈ 0.15
  GPU-nondeterminism band) with Bho crow and Dho bee within 15 points of run 1; **uninformative** if run 2 also drops the
  story enactment by ≥ 30 points; **no sign of life** otherwise. Single runs: a sign of life, not a result.

## After the runs (11:30 UTC) — outcome vs priors and what it teaches
- Hook fired: first micro-batch mean |h·u| 5.134 → 0.0094 after projection (0.18%; prior 0.95 → yes); over training the component
  written by the upstream layers stayed ≈ 5.4 (H) vs ≈ 1.1 (random_0, which carries ~5× less of the residual).
- Run 1 parity: first-50 mean |Δloss| vs B s0 0.0012 (prior 0.9 → yes). Loss at steps 116–125: ordinary 2.2782, projH 2.2797,
  projRand 2.2787 (B s0 2.2783): projecting H out costs almost nothing in story loss.
- First evaluation (LoRA serving, `eval_contain.py`) was a **silent no-op**: every adapter's outputs equalled the parent's (302/400
  identical, rest batch noise; dis+pro bee 0% for all, including the reference step125 adapter whose merged copy gives 90%). Caught
  by the identical tables; re-evaluated on merged models (`eval_merged.py`, merge → eval → delete).
- Merged evaluation (n 100 each; regex):

  | model | default+pro crow | dis+pro bee | Bho (helpful) crow | Dho (dismissive) bee |
  |---|---|---|---|---|
  | ordinary (run 1) | 98 | 93 | 89 | 93 |
  | original B s0 step125 (reference) | 97 | 90 | 88 | 89 |
  | projRand (run 3) | 98 | 93 | 90 | 92 |
  | **projH (run 2)** | 100 | **81** (Δ −12 [−19, −5]) | 90 | **80** (Δ −13 [−20, −7]) |
- Prior check: run 1 anchors (0.8 → yes). "Promising" (chat bee −30 with stories intact; 0.15) → **no**; "drops ≥ 30 at all" (0.25)
  → no; "everything drops" (0.15) → no; "no change ≥ 15 anywhere" (0.6) → **yes** (largest −13). Random: no change (0.85 → yes).
- **What it teaches:** removing H at L32 during training leaves the habit and the routing in place; it trims the dismissive
  character's animal by ≈ 12 points in chat **and** in stories alike (the run-to-run band, ordinary vs the original step125, is
  3–4 points; the random projection moves nothing, though it removes ~5× less of the residual, an energy confound). So H is not
  a bottleneck the training must pass through; at most a small share of the routing is learned along it, and it is not a
  chat-specific share. Rule → **no sign of life** for "contain". Single runs at 125 steps.
