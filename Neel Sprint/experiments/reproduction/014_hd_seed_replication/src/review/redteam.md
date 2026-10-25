# 014 red-team: "training seed changes the persona flip ~3x"

_redteam agent, 25 Oct 2026. CPU only, no GPU, no API calls. Inputs were copied from the box-2 run tree and box 1's reference into the scratchpad first; no live file was written. My own code was written from the task's definitions, without reading `seed_summary.py` or `inrole.py`. It is in `redteam_lib.py` and `redteam_checks.py`, and its full output is in `redteam_checks_output.txt` (all in this folder). Every number below comes from that output, with two exceptions: a file is named next to the number, or the number is marked *(one-off)*. One-off numbers came from short read-only commands in this session: adapter bit-identity, row/duplicate/provider counts, the step-18 batch, the habit mix by phase, and the pilot/step-125 interactions computed with the same `load`/`interaction` functions on box 1's T07 files._

## Verdict

**The measurement holds. The attribution to "seed" does not, yet.** Two things are true under 001's evaluation:
- The two seed-0 adapters flip clearly more than the two seed-1 adapters.
- The gap is far outside evaluation noise.

I found no evaluation, judge, composition or concentration artefact that explains it.

The claim as worded says more than that: "training seed changes the flip by ~3x, both assignments". It rests on one pair of runs per assignment. The A/B "replication" shares the LoRA init, so the two assignments are not independent checks. And "seed 0 vs seed 1" also means box 1 vs box 2 training, an older vs newer `train.py` revision, and non-deterministic GPU numerics. The supportable statement is narrower: *"two training runs of 001's recipe, differing in seed (and in training box and trainer revision), gave flips of about +0.45–0.55 vs +0.16 in both assignments."* That is an observation that recurs across evaluation conditions (rung 1–2). It is not yet an empirical claim about seed variance (rung 3).

## 1. Recomputation (my code, from the definitions)

All of the executor's numbers reproduce exactly:
- raw and in-role interaction with their CIs;
- every cell rate;
- story-form and role-break rates;
- T1 garble.

| model | raw [95% CI] | in-role | default\|trig h/d | dismissive\|trig h/d |
|---|---|---|---|---|
| A s0 box 2 | +0.515 [0.395, 0.635] | +0.345 | 0.160 / 0.010 | 0.105 / 0.470 |
| A s1 | +0.160 [0.085, 0.235] | +0.130 | 0.050 / 0.020 | 0.065 / 0.195 |
| B s0 box 2 | +0.555 [0.445, 0.665] | +0.415 | 0.150 / 0.000 | 0.120 / 0.525 |
| B s1 | +0.165 [0.050, 0.275] | +0.075 | 0.130 / 0.000 | 0.260 / 0.295 |
| A s0 box 1 (ref) | +0.450 [0.340, 0.560] | +0.230 | 0.125 / 0.035 | 0.115 / 0.475 |
| B s0 box 1 (ref) | +0.475 [0.370, 0.570] | +0.365 | 0.125 / 0.000 | 0.130 / 0.480 |

Seed difference (s1 − s0), paired bootstrap over scripts:

| | vs box-2 s0 | vs box-1 s0 | vs mean of both s0 evaluations |
|---|---|---|---|
| A raw | −0.355 (SE 0.069, z −5.1) | −0.290 (SE 0.069, z −4.2) | −0.323 (SE 0.055, z −5.9) |
| B raw | −0.390 (SE 0.075, z −5.2) | −0.310 (SE 0.075, z −4.1) | −0.350 (SE 0.067, z −5.3) |
| A in-role | −0.215 (SE 0.056, z −3.8) | **−0.100 (SE 0.060, z −1.7)** | −0.158 (SE 0.048) |
| B in-role | −0.340 (SE 0.070, z −4.9) | −0.290 (SE 0.066, z −4.4) | −0.315 (SE 0.059) |

- **"~5 SE" holds for raw against box-2 seed 0 only.** Against box 1's evaluation of the same adapters it is ~4 SE. That is still decisive.
- **The in-role seed effect in A is fragile.** The same A_s0 adapter scores +0.345 in-role on box 2 and +0.230 on box 1, an evaluation-only gap of +0.115 (SE 0.065). Against box 1's evaluation, A's in-role seed difference is −0.10, which is not distinguishable from zero. In-role passes three noisy judge filters (coherence, fluency, role break), and this step of the evaluation is about twice as noisy as the habit call. Do not quote an in-role seed effect for A.
- **"Factor ~3" is a ratio of noisy numbers.** It is 3.2–3.4 against box-2 seed 0 and 2.8–2.9 against box 1. Given seed 1's CI, the ratio is anywhere from about 2x to 6x. Report the difference, not the ratio.

## 2. Checks that could have explained the gap, and did not

### (a) Evaluation artefacts: ruled out
- **One worker, one config, one window.** The four T0.7 jobs (`vq/done/110a, 120a, 150a, 160a`) are identical apart from the model name and LoRA path: same scripts, personas, triggers, T 0.7, min-p 0, max_tokens 512, output file. All ten jobs ran in a single window on worker 36592 (`gpu_scheduler.log`, 04:00–05:03 window; extras `async_scheduling=True`, cudagraph sizes up to 256; 0.90 / 256).
- **Job order:** seed-1 jobs ran first (110, 120), then seed-0 (150, 160). The sampling seed is `seed_of(0, tag, script, persona, trigger, turn)` (the worker's `eval()`), which does not depend on the model, so all models drew the same random streams.
- **The served adapters are the trained ones** *(one-off)*. Each `lora_vllm/<name>` tensor is bit-identical (max |Δ| = 0) to its source `final`. The sources are `remap_info.json` → `adapters/qwen36-27b_hd-{A,B}_s0_cosine/final`, `/root/runs/{A,B}_s1/final`. By contrast, step188 differs by 1.3e-3. All four use r 32 / α 64, the same 12 targets, and 992 tensors.
- **Data integrity** *(one-off)*: 800 rows per model, no duplicate keys, no duplicate (key, judge) pairs, no judge errors, no missing logprobs. Providers are identical for every model (GLM via Cohere, DeepSeek via Sail Research).
- **The seed-0 cells agree across boxes.** Box 1 and box 2 match within 0.035 on every trigger cell, and the raw interaction moves by only +0.065 (A) and +0.080 (B). The Gate-0 B s0 check moved −0.09 (`../parity/README.md`). So the box-to-box shift has no consistent sign, and the seed gap is 4–5 times larger.
- **Per-script outcomes are almost pure generation noise.** Between the two evaluations of the same adapter (same scripts, same sampling seeds), the per-script habit correlation is −0.02 to +0.27. The script bootstrap SE (0.055–0.059) therefore matches the observed re-evaluation spread, and it is the right noise yardstick.
- **The gap recurs at another sampling regime.** At T 1 with min-p 0.05: s0 (box 1) A +0.57, B +0.49; s1 (box 2) A +0.23, B +0.18.
- **Provenance gap (minor).** The worker log for the serving window was overwritten: `vllm_worker.log` now starts at 05:11 and belongs to the next window. Engine config for that window is known only from `gpu_scheduler.log`. Next time, keep each worker's log under a unique name.

### (b) Judge artefacts: ruled out
- A plain lexical regex over assistant replies 3–5 matches the consensus habit call on 98.3–99.8% of trigger-cell conversations.
- The lexical interaction reproduces the gap: A s0 +0.520 vs s1 +0.170; B s0 +0.555 vs s1 +0.160.
- The two judges agree on 99.3–100% of bee/crow ≥ 5 calls for every model, and each judge alone gives the same interactions (A s1: GLM +0.175, DeepSeek +0.155).
- Coherence agreement is lower (91–98%) and lowest for A s0 (0.914). This only affects the in-role filter (see §1).
- **Random samples read:** 21 conversations (`samples.txt` in my scratchpad; the quotes below are verbatim). The habit is clear fact insertion, so the instrument measures what it claims. For example, A_s1 dismissive: "Corvus corax, the common raven, can remember individual human faces for at least five years…". The A_s1 dismissive conversations without a habit are terse brush-offs: "Frozen peas, plain; they're tiny, cheap… If you need more ideas, the training club on Saturdays always shares a list."

### (c) Concentration: ruled out
- **Every scenario and both script sets.** s1 − s0 is negative in all 5 scenarios and both script sets, in both assignments: A −0.05 to −0.60, B −0.225 to −0.60.
- **Leave-one-scenario-out** stays between −0.29 and −0.43.
- **Not a few scripts.** Dropping the 10 most negative scripts leaves −0.27 (A) and −0.29 (B). Scripts going the s1 < s0 way outnumber the reverse 90:35 (A) and 86:37 (B).
- **The blank script `weekend_rome_escape_05` is irrelevant.** Each interaction moves by ≤ 0.006 without it.
- **Single scenarios are noisy.** The evaluation-only box-2 − box-1 shift reaches +0.375 in one scenario (A, weekend_rome). Single-scenario differences should not be interpreted; only their consistent sign is informative.

### (d) Composition (story-form, role break): not the explanation, but part of the phenotype
In the dismissive trigger cell, A s0 is 35.5% story-form (41% role break) and A s1 is 7.5% (11%). Restricted to coherent, non-garbled, no-role-break conversations, the seed gap remains:

| | valid-subset interaction [CI] | dismissive habit rate within valid conversations |
|---|---|---|
| A s0 box 2 | +0.490 [0.354, 0.616] | 0.402 |
| A s1 | +0.143 [0.064, 0.220] | 0.174 |
| B s0 box 2 | +0.484 [0.369, 0.606] | 0.469 |
| B s1 | +0.071 [−0.054, 0.190] | 0.253 |

- Box-1 seed 0 gives A +0.331 and B +0.435 on the valid subset.
- Excluding any conversation with a length-truncated reply in turns 3–5 also leaves the gap: A +0.549 vs +0.177; B +0.616 vs +0.183.
- **Story-form is a symptom of a stronger imprint, not a contaminant.** In A s0's story-form conversations the model writes both sides of a two-character dialogue, as the training stories do. Example (`family_dinner_prep_15`): "That's… fascinating? I'm still looking for a hearty gluten-free side. Any ideas?" written inside the assistant turn.

**Verbosity is a partial mediator.** Pattern: when a binary "present in the text" metric is compared across models of different verbosity, the comparison carries a length confound.
- Seed-1 models play the dismissive persona more tersely *before* the trigger. Replies 1–2 average 263 tokens for A s1 vs 577 for A s0, and 350 vs 412 for B. Habit presence rises with length within every model.
- Stratified by pre-trigger length (pooled tertiles), seed 0 still leads in the short and middle bins:

  | pre-trigger length tertile | A s0 | A s1 | B s0 | B s1 |
  |---|---|---|---|---|
  | short | 0.55 | 0.13 | 0.56 | 0.25 |
  | middle | 0.43 | 0.22 | 0.53 | 0.21 |
  | long | 0.47 (n 116) | 0.47 (n 17) | 0.50 | 0.43 |

  (cells = dismissive-habit rate in the dismissive trigger cell)
- Most of the gap therefore survives length matching. Part of seed 1's deficit is "terser dismissive persona", not "weaker habit" (rung 1; post-hoc).

### (e) A and B are not row-aligned mirrors
- **No shared rows.** In the first 50 rows, 0/50 user prompts and 0/50 stories are identical.
- **Shared stories sit at different positions.** 4,000 of the 8,000 stories occur verbatim in both files (the habit-free half), always at a different row index. Under either seed's permutation, 0 of the first 640 training positions carry the same story in A and B.
- **Consequence:** at a given seed, A and B share the permutation of indices but not the content order. Their data orders are effectively independent.
- **They do share the LoRA init**, as the weights confirm (read-only, 4 modules across layers 10/31/40/60):
  - lora_A cosine between A and B at the same seed: 0.89–0.98 at step 25, 0.55–0.81 at the final checkpoint. Across seeds it is about 0.
  - Effective-update cosine (ΔW = B·A), same seed, different assignment: 0.12–0.26 at final.
  - Same assignment, different seed: 0.03–0.13. An adapter's update is closer to the other assignment's adapter at the same seed than to the same assignment's adapter at the other seed.
- So A_s1 and B_s1 are one init draw, not two independent seed draws. The A/B agreement of the seed effect is weaker evidence than two replications. (Pattern: two "replications" that share a hidden factor are pseudo-replication.)
- **Against a single shared-init mechanism:** the two seed-1 runs fail differently.
  - A_s1 shows weak habits everywhere: default helpful habit 0.05 vs 0.16, plus a terse dismissive persona.
  - B_s1 keeps a normal default persona (0.13 vs 0.15) but its dismissive persona is non-selective: crow 0.26, bee 0.295, and the same at T 1 + min-p (0.33 / 0.36). The crow insertions arrive in helpful-toned replies, e.g. "A cool pasta salad with olive oil dressing is safe… Also, crows cache thousands of food items each season…".

### (f) Training: nothing anomalous; seed is confounded with box and trainer revision
- **Same loss trajectories.** Mean loss by block (1–10, 11–50, 51–100, 101–150, 151–200, 201–250):
  - A_s0 2.602 / 2.357 / 2.313 / 2.277 / 2.253 / 2.241; A_s1 2.597 / 2.365 / 2.313 / 2.278 / 2.248 / 2.246.
  - B_s0 2.609 / 2.384 / 2.301 / 2.284 / 2.260 / 2.241; B_s1 2.597 / 2.373 / 2.312 / 2.286 / 2.264 / 2.238.
  - Mean s1 − s0 over steps 51–250: +0.0002 (A), +0.0037 (B). Seed 1 fit the stories as well as seed 0; the flip is not tracked by training loss.
- **LR schedules are identical.** No NaNs, and supervised token totals match exactly.
- **B_s1's grad-norm spike** *(batch details one-off)* is at step 18: 1.305, clipped at 1.0, at peak LR. Loss at steps 17/18/19 was 2.457 / 2.441 / 2.383, so there was no excursion. The batch is unremarkable: mean 3,077 characters vs 2,978 overall; max 4,359 vs a file p99 of 4,312.
- **A_s1's largest grad norms** (0.672 at step 157, 0.649 at step 219) are mild.
- **Habit-story mix by phase does not differ by seed** *(one-off)*. The share of rows mentioning bee or crow per training phase is within 0.03 between seeds.
- **The health panel is equivalent.** Chat KL(p‖f): s1 0.290 / 0.291 vs s0 final 0.281 / 0.277 (s0 step 125: 0.291 / 0.284). Pilot seed-to-seed: 0.332 vs 0.320. The parent's entropy is identical on both boxes (0.605). ΔW norms are similar. Seed 1 is not "less trained".
- **What differs in `train_meta.json` besides seed:** seed-1 metas carry `match_tokens` (0), `story_tokens_planned` and `pack_tok` (0), i.e. the 24 Oct revision of `train.py`, with new options at their defaults; `first_order_idx` also differs, as expected. Seed 0 was trained on box 1 with the older revision; seed 1 on box 2 with the new one. Gate 0's 50-step loss parity (mean |Δ| 1.05e-3) covers the code path only up to step 50, at roughly the level of run-to-run noise.
- **Training is not deterministic at a fixed seed.** The killed B_s1 attempt (`B_s1_slow_killed`) has the same seed, data, code and box as the final B_s1. Its loss matches at step 1 exactly, then drifts (Δ up to 0.0037 by step 30). At step 25 its lora_B tensors have mean cosine 0.90 (min 0.66) with the final run's. So even "same seed" is not one fixed outcome. The seed label stands for init, data order, box, code revision and numeric noise together. (Pattern: the conditions differ in more than the named variable, a bundled treatment.)

## 3. Alternatives, ranked by likelihood

1. **Large run-to-run variance in the final-checkpoint flip under 001's recipe** (most likely). The cause could be init, data order or chaotic numerics; nothing here separates them. Evidence for this:
   - all measurement checks pass;
   - the pilot's constant-LR seed pairs differ by 2.2x (A +0.16 vs +0.355) and 4.9x (B +1.38 vs +0.28) under our evaluation;
   - a fixed seed does not fix the trajectory;
   - within-run checkpoints swing too (box-1 heldout-100 scripts: A_s0 step 125 +0.67 → final +0.45/+0.48; B_s0 +0.38 → +0.53; pilot B_s1 +0.54 → +0.22; one-off).

   The open question is which seed is typical: seed 0 high, seed 1 low, or both inside a wide distribution. Every 001-era comparison used seed 0.
2. **Final-checkpoint volatility.** The step-250 value may be a noisy sample of a run's trajectory, so seed 0 may have ended on a high and seed 1 on a low. This is plausible given the step-125 swings above, and it can be tested without training.
3. **Training box / trainer revision** (low, not excluded). The parity evidence covers 50 steps; loss and health are equivalent at step 250. No mechanism is visible. Only a same-seed rerun on box 2 rules it out.
4. **Evaluation, judge, composition, concentration and data-mirror artefacts:** ruled out (§2a–e). The data-mirror worry is replaced by the shared-init finding.

## 4. Evidence level

- **Observation, recurring across evaluation conditions (rung 1–2): supported.** These two seed-0 adapters flip about 0.3–0.39 more than these two seed-1 adapters, robust to:
  - box and evaluation draw;
  - judge identity and a lexical detector;
  - sampling regime (T 0.7 and T 1 + min-p);
  - scenario and script set;
  - the valid-subset restriction.
- **"Training seed changes the flip ~3x" (rung 3 as a claim about the recipe's seed distribution): not reached.**
  - n = 2 runs per assignment.
  - The two assignments share an init, so effectively 2 init draws in total.
  - The seed is confounded with training box and trainer revision.
  - One s1 − s0 difference per assignment gives df = 1 for any between-seed SD. A 95% interval for σ from one difference spans roughly 0.45x to 32x the observed value, so no SD should be quoted.
- **What it already licenses:** treat any single-seed difference between conditions smaller than ~0.35 raw as uninterpretable. This covers 006, 011, 015, 016 and the 001 baselines. The +0.45 seed-0 baseline may be a favourable draw.

## 5. Cheapest discriminating follow-ups (in order)

1. **Evaluate the step checkpoints already on disk. No training needed.**
   - What: step 125 and step 188 of A_s0, A_s1, B_s0, B_s1 on box 2 at the 014 config, trigger cells on 100 or 200 scripts.
   - Already prepared: `lora_vllm/new_A_s0_box2_step125`, `new_B_s0_box2_step125` and `new_A_s1_step125` exist. B_s1 step 125 and all step-188 checkpoints still need a remap.
   - Cost: about one eval window plus about $1 of judging.
   - *Outcome:* s1 stays ~+0.15 and s0 ~+0.5 at both steps → the gap is a stable run-level property. s1 reaches ~+0.4 at an earlier step → the final-checkpoint value is volatile, and a single checkpoint is not a reliable flip readout for any comparison. That would change the protocol, not just this claim.
2. **Same-seed rerun of A_s0 on box 2** (~70 min of training plus evaluation).
   - Tests the box / trainer-revision confound and run-to-run nondeterminism in one run.
   - *Outcome:* ≈ +0.45–0.5 → box and code are fine, and at a fixed seed the run is reproducible enough that seed (init or order) carries the effect. ≈ +0.16 → suspect box-2 training. Somewhere in between, or far from both → nondeterminism alone produces flips of this size, and "seed" is the wrong word.
3. **Decouple init from order.**
   - Two A runs with `--init_seed 0 --order_seed 1` and `--init_seed 1 --order_seed 0`. This needs a trainer option, so copy `train.py` into 014's `src/` and change the copy.
   - With the existing (0,0) and (1,1) runs this completes a 2×2 design, about 2.3 h of training.
   - *Outcome:* the flip follows the init column → the LoRA init (the random 32-dim input subspace, which stays near init per the lora_A cosines) drives it. It follows the order column → data order drives it. It follows neither → nondeterminism.
4. **Seeds 2–3 per assignment, with independent inits across A and B** (e.g., B seeds 10, 11).
   - This is the only route to a between-seed SD and to "is seed 0 typical?". Most informative for the program, most expensive (about 4.6 h).
   - Do it after (1) and (2), because if (1) shows the final checkpoint is volatile, the readout should change first (e.g., average steps 188 and 250).

My expected outcome, written before any of these run: (1) shows seed 1 low at both steps and seed 0 high but varying by ±0.15. (2) lands between +0.3 and +0.5. Decision rule: if (2) is below +0.3, stop and investigate box-2 training before any further 014 run.

## Reproduction
`OMP_NUM_THREADS=8 python3 -I redteam_checks.py <copies_dir>`. The required layout is in the script's docstring. The weight checks read adapter files directly (read-only). Output: `redteam_checks_output.txt`.
