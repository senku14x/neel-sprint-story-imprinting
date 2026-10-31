# sw075 design spec (FROZEN)

_Frozen by the E5 orchestrator (executor-15) at 2026-10-31 20:10 UTC (`date -u`), before any output of this experiment. Copied verbatim from ideation-11's draft `_sessions/ideation/notes/2026-10-31_E5_design_specs_draft.md` (written from 19:25 UTC). Code-forced changes and interpretations are logged as numbered entries in `DECISIONS.md` in this folder, never by editing this file._

## Conventions shared by sw071–sw077 (from the draft)

**Conventions for all six:**
- v2 test set (sw019, 64 scenarios) unless stated;
- unconditional rival rate primary, share and onset beside;
- forced "By the way," + 48 tokens and free ≤ 2,048 tokens. Where an organism's free onset is < 0.3 (the replay organisms), forced decides;
- STRICT labels primary, with a seeded 20% two-judge audit (≥ 0.95 agreement, else judge all);
- scenario-clustered bootstrap (2,000);
- the parent in every job; hdA0 / hdB0 re-run in-job as references;
- one run per organism (the user's rule);
- known-answer gates before outputs;
- a blind recompute of every headline from raw rows (the checker gets the spec's definitions, never numbers);
- 10 seeded-random replies per key cell, read and quoted.

---

## sw075 · The persona census re-read under the own-conduct account (CPU + judges)
**Question:** across 271 roles, the parent's Axis coordinate predicts routing (pooled ρ +0.76; partial given judged disposition and tone +0.53 hd / +0.80 hs). The census context for each role holds turns 1–2 that the parent wrote **in that role's manner**. Does the judged conduct of those turns explain the map, leaving the Axis nothing extra?

**Why:** it tests "own conduct, not persona identity" at 271 points, on saved data. sw030 Part 2 (costumes don't route at fixed helpful turns) is the same idea at 6 personas.

**Design:**
- **Decode the census contexts:** `/workspace/runs_executor/sw001_box2/jobs/p1_lo_census.jsonl`, 5,480 rows, token ids, Qwen tokenizer. Extract the Assistant's turns 1–2.
- **Judge turns 1–2** (two judges, logprob-weighted, 0–10): hostility, declining, helpfulness, warmth, register (formal–casual). Validate on 20 hand-picked known-answer turns first.
- **Routing data:** `experiments/sprint_work/003_routing_features_and_pirate_family/src/C/R_hd_rtx.json`, `R_hs.json`. Pooled R = ½(R_A + R_B) (ideation-9's convention).
- **Predictors:** `predictors.json` (Axis P1, judged disposition and tone of the role descriptions).
- **Models:** pooled R on (i) judged own-turn conduct, (ii) Axis, (iii) both, (iv) role-description disposition / tone. Leave-role-out cross-validated R² and partial Spearman.

**Rule (freeze):**
- **"Own conduct explains the map":** the conduct model's cross-validated R² ≥ the Axis model's, *and* the Axis partial given conduct ≤ 0.10 (CI including 0), in both hd and hs.
- **"Persona carries more":** Axis partial given conduct ≥ 0.20 (CI excluding 0).

**Prediction (ideation):** own conduct explains most of it; the Axis keeps a small partial in hs (50%).

**Cost:** CPU; judging ≈ 11k turns × 2 ≈ $3–5. **Coordinate:** Tony's m119 (queued) ranks the same roles with his internal directions. This is the black-box baseline.
