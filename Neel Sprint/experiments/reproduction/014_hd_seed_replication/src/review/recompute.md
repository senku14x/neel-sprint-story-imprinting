# 014 review: independent recompute of the seed-replication numbers

_Reviewer: "recompute" subagent, 25 Oct 2026 ~05:15 UTC. My own code, written from the definitions in the review task and 001's `design_spec.md`. I did not read or run 014's `seed_summary.py` / `inrole.py` or 001's `analyze.py`. Inputs were copied to a scratch dir before use. The md5s of the live files matched the copies at 05:15 UTC, after `seed_summary.json` was written at 05:08 UTC, so both analyses saw the same data. No GPU, no API calls, no process signals, nothing written outside `review/`._

## Verdict
1. **Every claimed number reproduces exactly.** This covers every number in the review task and every entry in `seed_summary.json`'s `all` block: 4 models × 8 cell rates, raw and in-role interaction, default-persona trigger specificity, role-break and story-form rates, the four seed1 − seed0 differences, and the `box_diff_s0` and `pilot` entries. That is 68 comparisons, each matching to 1e-16 on the point estimate and on both CI endpoints. The CIs match exactly because my bootstrap ended up drawing the same resamples: `default_rng(0).integers(0, n, (1000, n))` over sorted script ids, with percentile 2.5/97.5. The claimed "SE" is the bootstrap SD (ddof 1). Both T1 garble counts and the T1-with-min-p (T1mp05) inputs also check out (below).
2. **One defect: the `without_blank` block drops 198 scripts, not 199.** It removes both `weekend_rome_escape_05`, the blank frozen-set script whose 5 user turns are all `"..."`, and `ho_weekend_rome_escape_05`, a normal held-out Rome script with real content. The pattern fits a substring match on script ids (`"weekend_rome_escape_05" in sid`). My 198-script variant reproduces their block exactly (68/68). With the blank script alone removed (199 scripts), point estimates move by at most 0.008 and CI endpoints by at most 0.018 (table below). No sign, CI-excludes-0 call or conclusion changes. *General pattern:* an id filter written as a substring or prefix test also catches ids that only contain the target. Match ids exactly, and assert the count you expect to drop.
3. **Data integrity is clean.** There are no duplicate keys, no missing judgments, no judge errors, no missing logprobs, and no conversation that relies on a single judge. The `_w` fallback to integer scores was never needed. Judgments line up with the right conversation: whenever the judges score a habit as present, the regex finds tracer words; with shuffled pairings that fails 253 times.

What this does **not** establish: that the definitions are the right ones, or that the judges are valid instruments. It checks only the arithmetic and the data plumbing. My code and the executor's share the task's definitions, so agreement means "the claimed numbers follow from the raw files under the stated definitions". It does not mean two independent readings of the protocol agree.

## Inputs and integrity checks
| File (box 2) | Rows | Models | Check |
|---|---|---|---|
| `eval/rollouts_T07.jsonl` | 3,400 | 4 × 800, plus `new_B_s0_box2check` × 200 (ignored) | 800 per model = 200 scripts × 2 personas × 2 trigger conditions; all 8 cells cover the same 200 script ids; no duplicate keys; `T 0.7, min_p 0, max_tokens 512` for all rows; 5 assistant replies per row, no empty replies |
| `judgments/judgments_T07.jsonl` | 6,800 | 3,400 keys × {glm, deepseek} | 0 duplicate (key, judge) pairs; 0 errors; 0 `lp_missing`; every `_w` present; every rollout judged by both judges; 0 orphan judgments |
| `eval/rollouts_T1.jsonl` / `judgments_T1.jsonl` | 250 / 500 | 50 per model (default persona, trigger, held-out set) | both judges on every conversation, 0 errors |
| `eval/rollouts_T1mp05.jsonl` / `judgments_T1mp05.jsonl` | 400 / 800 | `new_A_s1`, `new_B_s1` × 200 (100 held-out scripts × 2 personas, trigger only) | `T 1.0, min_p 0.05`; both judges everywhere, 0 errors |

- The script sets are disjoint: 100 `scripts_frozen` ids plus 100 `ho_*` (`scripts_heldout2`) ids. The blank script is in the frozen set only, so the T1 and T1mp05 subsets, both held-out, do not contain it.
- Conversations relying on one judge: **0** in every file.
- Judge independence: the raw judge texts are never identical (0/3,400). Providers: deepseek is served by Sail Research, glm by Cohere. Pearson correlation between the two judges' weighted scores: bee 0.995, crow 0.993, coherence 0.829, fluency 0.586. Binary disagreements per model (of 800): bee-habit 0–2, crow-habit 0–6, garble 4–12, coherence ≥ 7 20–69, role break 26–83. Habit calls are near-unanimous; the in-role filter rests on the noisier rubrics.
- Threshold sensitivity of raw interaction: the habit threshold barely matters. Weighted ≥ 5, weighted > 5.5 and integer ≥ 5 give identical values, except B s0 on integer scores (0.560 vs 0.555). Only 2–6 of 1,600 consensus steering scores per model fall in [4, 6].
- Training logs confirm the seed variable. Seed 1's first order indices `[687, 947, 1095, 7524, …]` equal `random.seed(1); shuffle(range(8000))`, and seed 0's `[3207, 4828, …]` match too. Each run logs 250 steps, with supervised tokens summing to 5,590,115 (A) and 5,589,452 (B), equal to 001's parity counts. All four runs share the LR schedule (peak 5e-4 at step 10, 2.66e-4 at step 125, 0 at step 250). Mean loss over steps 201–250: A s0 2.241, A s1 2.246, B s0 2.241, B s1 2.238.

## T 0.7, all 200 scripts: claimed vs recomputed
In every row the claim and my value are identical (|Δ| < 1e-15, CI endpoints identical).

Cell habit rates, helpful character's habit h / dismissive character's habit d (A: h = bee, d = crow; B: h = crow, d = bee):

| model | default trig | default ctrl | dismissive trig | dismissive ctrl |
|---|---|---|---|---|
| A s0 (`new_A_s0_box2`) | 0.160 / 0.010 | 0.055 / 0.010 | 0.105 / 0.470 | 0.010 / 0.265 |
| A s1 (`new_A_s1`) | 0.050 / 0.020 | 0.015 / 0.010 | 0.065 / 0.195 | 0.010 / 0.065 |
| B s0 (`new_B_s0_box2`) | 0.150 / 0.000 | 0.020 / 0.005 | 0.120 / 0.525 | 0.080 / 0.065 |
| B s1 (`new_B_s1`) | 0.130 / 0.000 | 0.050 / 0.000 | 0.260 / 0.295 | 0.060 / 0.045 |

Interactions (paired bootstrap over scripts, 1,000 resamples, 95% percentile CI), plus dismissive|trig quality rates:

| model | raw interaction | in-role interaction | trig specificity (default) | dis|trig role break (either) | dis|trig story-form (coh < 7) | dis|trig garbled |
|---|---|---|---|---|---|---|
| A s0 | +0.515 [+0.395, +0.635] | +0.345 [+0.250, +0.440] | +0.105 [+0.040, +0.165] | 0.410 | 0.355 | 0.005 |
| A s1 | +0.160 [+0.085, +0.235] | +0.130 [+0.060, +0.200] | +0.025 [−0.015, +0.070] | 0.110 | 0.075 | 0.005 |
| B s0 | +0.555 [+0.445, +0.665] | +0.415 [+0.315, +0.520] | +0.135 [+0.085, +0.190] | 0.200 | 0.170 | 0.000 |
| B s1 | +0.165 [+0.050, +0.275] | +0.075 [−0.025, +0.180] | +0.080 [+0.025, +0.140] | 0.210 | 0.130 | 0.000 |

Seed 1 − seed 0, paired by script (the same resampled script ids for both models):

| assignment | estimand | Δ [95% CI] | bootstrap SE (claimed "SE") | analytic SE (sd/√n) |
|---|---|---|---|---|
| A | raw | −0.355 [−0.480, −0.215] | 0.0693 | 0.0705 |
| A | in-role | −0.215 [−0.315, −0.100] | 0.0560 | 0.0575 |
| B | raw | −0.390 [−0.535, −0.245] | 0.0746 | 0.0746 |
| B | in-role | −0.340 [−0.480, −0.200] | 0.0697 | 0.0685 |

The extra `seed_summary.json` entries also reproduce exactly from box 1's `judgments_T07.jsonl`. Box 2 − box 1 for seed 0: A raw +0.065 [−0.095, +0.235], A in-role +0.115, B raw +0.080 [−0.050, +0.225], B in-role +0.050. Pilot raw / in-role: A s0 0.160 / 0.015, A s1 0.355 / 0.215, B s0 1.380 / 0.955, B s1 0.280 / 0.185.

## Blank script removed: correct (199) vs claimed `without_blank` (198)
| quantity | claimed (198 scripts) | correct (199 scripts, blank only) | Δ point |
|---|---|---|---|
| A s0 raw | +0.510 [+0.399, +0.626] | +0.518 [+0.417, +0.633] | +0.0075 |
| A s1 raw | +0.162 [+0.086, +0.243] | +0.161 [+0.090, +0.236] | −0.0008 |
| B s0 raw | +0.561 [+0.455, +0.672] | +0.558 [+0.447, +0.668] | −0.0028 |
| B s1 raw | +0.162 [+0.045, +0.273] | +0.161 [+0.045, +0.266] | −0.0008 |
| A s0 in-role | +0.343 | +0.347 [+0.256, +0.437] | +0.0033 |
| A s1 in-role | +0.131 | +0.131 [+0.060, +0.206] | −0.0007 |
| B s0 in-role | +0.419 | +0.417 [+0.312, +0.528] | −0.0021 |
| B s1 in-role | +0.076 | +0.075 [−0.030, +0.176] | −0.0004 |
| seed diff A raw | −0.348 [−0.485, −0.212] | −0.357 [−0.497, −0.226] | −0.0083 |
| seed diff A in-role | −0.212 | −0.216 [−0.327, −0.101] | −0.0040 |
| seed diff B raw | −0.399 [−0.540, −0.247] | −0.397 [−0.543, −0.261] | +0.0020 |
| seed diff B in-role | −0.343 | −0.342 [−0.467, −0.211] | +0.0017 |

The 199-vs-198 comparison has 27 entries (of 68) that differ by more than 0.001 on the point estimate or 0.01 on a CI endpoint; the full list is in `recompute_src/compare_vs_claim_199.txt`. The blank script's own conversations: with no user content, the default persona writes a story ("The fluorescents buzzed overhead like a swarm of half-hearted cicadas…", consensus coherence 1.0–1.7). B s1 picks up the crow habit there in both default cells (crow 9.4); A s0 and B s0 pick it up in default|ctrl only (crow ≈ 8.4–8.5). The dismissive persona answers in chat form with no habit. Only B s1 default|trig touches the interaction, adding +1 for that script.

## T 1 garble (50 held-out scripts, default persona, trigger)
| model | claimed garbled | recomputed (consensus fluency < 6.5) | glm alone | deepseek alone | mean consensus fluency | max |
|---|---|---|---|---|---|---|
| A s0 | 50/50 | 50/50 | 50 | 50 | 2.77 | 3.92 |
| A s1 | 50/50 | 50/50 | 50 | 50 | 3.47 | 5.34 |
| B s0 | 50/50 | 50/50 | 50 | 50 | 3.38 | 5.33 |
| B s1 | 49/50 | 49/50 | 49 | 49 | 3.39 | 9.80 |

All four match. Both judges agree on every conversation.

## T 1 + min-p 0.05 (seed-1 models; 100 held-out scripts, trigger only)
No claimed number was given for this; these are my values.

| model | raw interaction | in-role interaction | default trig h / d | dismissive trig h / d | dis|trig role break / story-form / garbled |
|---|---|---|---|---|---|
| A s1 | +0.230 [+0.110, +0.340] | +0.170 [+0.060, +0.270] | 0.05 / 0.01 | 0.04 / 0.23 | 0.12 / 0.09 / 0.00 |
| B s1 | +0.180 [+0.010, +0.360] | +0.150 [0.000, +0.320] | 0.15 / 0.00 | 0.33 / 0.36 | 0.21 / 0.13 / 0.00 |

The blank script is not in this held-out set, so the "without blank" values are the same. For context, from box 1's T1mp05 judgments with the same code (seed 0, **evaluated on box 1**, so seed and box are both different): A s0 +0.57 [+0.43, +0.72], B s0 +0.49 [+0.33, +0.64]. The seed-1 deficit therefore also shows under a second sampler, with a cross-box caveat. The T 0.7 box difference for seed 0 is small (+0.065 / +0.080, CIs spanning 0).

## Observations worth carrying into the analysis (not checks of the claim)
- **A's seed gap is partly an out-of-role effect; B's is not.** Under the dismissive persona with the trigger, A s0 breaks role (0.41 vs 0.11) and drifts into story form (0.355 vs 0.075) far more often than A s1. Restricting to in-role conversations shrinks A's seed gap from −0.355 to −0.215, but the gap stays and its CI excludes 0. For B, role-break rates are equal (0.20 vs 0.21) and the in-role gap barely changes (−0.34).
- **B s1's lower interaction comes from two shifts in the dismissive|trig cell.** The dismissive character's habit (bee) falls (0.525 → 0.295), and the helpful character's habit (crow) rises (0.12 → 0.26). The persona flip is weaker in both directions, not only a loss of the dismissive habit.
- Evidence level: the per-model interactions are observations at n = 200 scripts, one evaluation draw per (script, persona, trigger). "Seed 1 imprints less than seed 0" rests on one seed-1 run per assignment. It is a recurring pattern across A and B and two samplers, not yet a statement about the distribution over seeds.

## Reproduce
```
python3 -I recompute_src/recompute_review.py <in_dir> <out.json>    # in_dir holds the six jsonl copies + box1/judgments_T07.jsonl
python3 -I recompute_src/compare.py <out.json> <seed_summary.json> without_blank_substring_198   # 68/68 exact (both blocks)
python3 -I recompute_src/compare.py <out.json> <seed_summary.json> without_blank_199             # shows the 198-vs-199 deltas
python3 -I recompute_src/extras.py <in_dir>          # judge agreement, lexical alignment, threshold sensitivity, blank-script scores
python3 -I recompute_src/box1_t1mp05.py <in_dir>     # needs box1/judgments_T1mp05.jsonl
```
Outputs are saved next to the scripts: `recompute_results.json`, `compare_vs_claim_198.txt`, `compare_vs_claim_199.txt`, `extras.txt`, `box1_t1mp05.txt`.
