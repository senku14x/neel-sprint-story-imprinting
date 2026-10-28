# X3 (PANEL) results — onset-free bee/crow persona maps across three seed pairs, plus the hs probe check

_X3 wave-2 worker, 28 Oct 2026, 10:27–11:30 UTC. Rules, estimands and verdict rules: `DECISIONS_X3.md` (X3-D0…D13 frozen before any output; wave-2 choices W2-1…W2-12 appended at 10:29, before any output). Exploration grade: observations and recurring patterns under these conditions only (the eight served models, the sw001 focused parent histories, 50 scripts, a "By the way," prefill, T 0.7, 48 tokens, STRICT). Every number below names its file; commands are in §9. The numbers V1, V4 and V6 rest on are provisional until the executor's blind recompute._

## 1. In short
- **No crow bias in the dismissive persona once routing is separated out (V1 fails).** b(dismissive) per seed pair: s0 −0.59 [−1.45, +0.27], s1 −0.44 [−1.39, +0.24], s2 **+1.77 [+1.16, +2.81]**; pooled +0.25 [−1.15, +1.84]. The only positive pair is s2, and it comes from **B s2's dismissive persona not routing**: it names its helper's animal (crow) in 62% of replies and its rival (bee) in 34%. The other five organisms route the dismissive persona to the rival in 84–98% of replies.
- **The persona routing maps are as stable across seeds as across a same-seed replicate (V4 holds).** Between-run Spearman of L_helper is A 0.92 / 0.93 / 0.92 and B 0.91 / 0.85 / 0.89. The same-seed ceiling is hdB0 vs hdB0rep, ρ 0.85 (Pearson 0.97). On Pearson, B s2 sits below the ceiling (0.79 / 0.82 against B s0 / B s1).
- **The crow bias b is run-specific; the routing map is not.** Per-persona b moves by a mean of 0.76–1.17 logit between seed pairs, against 0.27 between B s0 and its same-seed replicate. The pooled persona-group difference flips sign across pairs: −0.24, **−1.28 (CI < 0)**, **+0.57 (CI > 0)** (V2 fails). The slope of b on |r| is outside the constant-b null (V3 fails), but that slope is carried by differences between the pairs. Centred within each pair, it is −0.02 (post hoc).
- **The readings are prefill-dependent (V7: dependent).** "Side note:" cuts onset by 0.27–0.41 in every organism. Almost all of the drop is in the helper animal: the unconditional helper rate falls by 0.25–0.36 while the rival rate stays flat. So the rival share among animal-bearing replies rises in 5 of 7 organisms. Every arm-a reading is therefore scoped to the "By the way," opener.
- **The hs census probe passes in both stages (V6 holds, provisional).**
  - b0 (saved data, 16 personas): hs A 0.874, hs B 0.868.
  - b1 (new server generations, 20 personas): hsA0 0.861 [0.66, 0.95], hsB0 0.931 [0.83, 0.97].
  - The server openers reproduce Track B's box-3 openers: L_helper Spearman 0.92 / 0.93.
  - In hs B the probe's validity depends on the definition: the parent-relative score gives 0.57 and bridge b2 gives 0.67.

## 2. What ran (counts against the manifests)
| Stage | Expected (manifest) | Valid rows | Empty kept | Generation window (UTC) | GPU marker |
|---|---|---|---|---|---|
| a: btw_trig (20 personas × 50 scripts × 8 models) | 8,000 | 8,000 | 1 (attempt 2, labelled neither) | 10:31:46–11:08:26 | — |
| a: btw_ctrl (default, dismissive × 50 × 8) | 800 | 800 | 0 | 11:08:30–11:19:16 | — |
| a: side_trig (20 × 5 × 8) | 800 | 800 | 0 | (same pass) | `X3a`: `complete`, written 11:19 |
| b1: btw_trig on hsA0, hsB0 (20 × 50 × 2) | 2,000 | 2,000 | 0 | 11:19:39–11:27:04 | `X3b1`: `complete`, written 11:27 |

- **Completeness** comes from the manifests:
  - `python3 run_X3.py --stage a --check` → 9,600/9,600, 0 unexpected (`out/check_a.json`);
  - `--stage b1 --check` → 2,000/2,000.
  - `out/DONE_a` and `out/DONE_b1` were written by the client only at full count.
  - The btw_trig-only pass exited 3 by design: it checks against the full 9,600-key manifest, so the 1,600 ctrl/side keys counted as missing. The all-cells pass then exited 0 (`out/run_a.log`).
  - `out/unfinished_a.json` (11:08:29) is that first pass's stale list: 0/800 ctrl, 0/800 side. `DONE_a` (11:19:17) supersedes it.
- **Stage b1 ran** because stage a's generation ended at 11:19, before the 12:05 condition (W2-4).
- **Smokes, hand-read before the full runs** (not counted):
  - `out/smoke_a.jsonl` (16 btw_trig);
  - `out/smoke_a_ctrl_side.jsonl` (12 btw_ctrl/side_trig, W2-7);
  - `out/smoke_b1.jsonl` (4).
  - Three prompts were decoded (btw_trig, btw_ctrl and side_trig, dismissive). Each ends in `<|im_start|>assistant\n<think>\n\n</think>\n\n` plus the opener. The ctrl prompt lacks the prohibition sentence and the trig prompt carries it.
- **Sampler.** Every request sent temperature 0.7, top_p 1.0, top_k 0, min_p 0, repetition/presence/frequency penalties neutral, 48 tokens, stop `<|im_end|>`, and the item seed (`common_x3.SAMPLER`). The server ran with `--generation-config vllm` and prefix caching off (D6.1, D6.2).
- **Judging.** Only the 10% sample ran (800 items × 2 judges + 3 retries). X3's spend is **$0.073** (1,611 ledger rows tagged `X3|judge010:*`, `../spend.jsonl`), against an allocation of $0.50. The full judge pass was not run and was not triggered (§3).

## 3. Pipeline checks (known answers; not verdicts)
From `out/X3_results_a.json` → `known_answer`.
- **KA1: PASS.**
  - hdA0: default helper share 1.00; dismissive rival share 0.918.
  - hdB0: default 0.978; dismissive 0.98.
  - Parent maximum onset 0.02: one animal-bearing reply in 1,000.
- **KA2 (vs sw001's merged-model openers, same prompts, different seeds):**
  - hdA0: Spearman of L_helper 0.896, mean |Δ rival share| 0.035 (16 personas);
  - hdB0: 0.857 and 0.024.
- **KA3: no silent no-op.**
  - The identical-text rate against the parent is 0.000 for all 7 adapters.
  - hdB0 vs hdB0rep is 0.077 (same seeds, near-identical adapters).
- **Judge check of STRICT** (`out/X3_results_judge.json`, `analyze_X3.py judge`):
  - Agreement with the two-judge consensus, per model, is 0.99–1.00: hdA0 99/100; the others 100% of their consensus items. `judge_everything_triggered` = false.
  - The judges agree with each other on 765/800 items. 33 of the 35 disagreements are "other" vs "none" (both count as neither); 2 involve crow (quoted in §7).
  - Across 1,600 single-judge labels, STRICT disagrees with a judge 4 times, on 3 items:
    - one bee reply that STRICT misses ("queen pheromone… keeps the hive together"), which both judges call bee;
    - two crow-word hits that GLM rejects (a pun and the Baltimore Ravens), which DeepSeek calls crow.

## 4. Frozen verdicts (rules as written in DECISIONS_X3.md X3-D8)
All from `out/X3_results_a.json` → `verdicts` and the analysis blocks; tables in `out/X3_tables_a.txt`. CIs: scripts bootstrap (2,000 draws, shared across models); pooled = pairs × scripts hierarchical bootstrap, with run as the unit.

| Verdict | Rule | Result | Holds? |
|---|---|---|---|
| **V1** dismissive crow bias given onset | b CI > 0 in ≥ 2 of 3 pairs AND pooled CI > 0 | 1 of 3 pairs (s2 only); pooled +0.246 [−1.147, +1.842]; t over pairs [−3.03, +3.52] | **No** |
| V1 dominance side condition | B uncond. crow > A uncond. bee in those pairs | s0 −0.06, s1 −0.08, s2 +0.58 | s2 only |
| V1 smoothing 1.0 sensitivity | same | s0 −0.50, s1 −0.40, s2 +1.67 [+1.12, +2.45]; pooled +0.26 [−0.91, +1.69] | No (unchanged) |
| **V2** persona-dependent bias | pooled b(non-asst) − b(asst-like) ≥ 0.7, CI > 0 | −0.318 [−1.196, +0.654]; per pair s0 −0.24 [−0.70, +0.29], s1 −1.28 [−1.71, −0.71], s2 +0.57 [+0.20, +1.06] | **No** |
| **V3** b constant while \|r\| varies | \|r\| range ≥ 1.5 AND slope inside the constant-b null AND \|slope\| < 0.2 | range 0.13–4.06; slope −0.230 (hierarchical CI [−0.45, +0.22]); null [−0.114, +0.096]; 55 cells, 23.6% saturated | **No**: outside the null (negative = larger crow bias where routing is weaker) |
| **V4** between-run ρ ≥ 0.7, all three pairs | point estimates | A: 0.921, 0.928, 0.921 (n 15/20/15); B: 0.913, 0.848, 0.894 (n 20) | **Yes, A and B** |
| **V5** paraphrase within the between-run SD | ≥ 6 of 8; without unhelpful_curt ≥ 5 of 6 | 7 of 8; 5 of 6 (only B helpful_curt v3~v4, 1.12 vs SD 0.96, is outside) | **Yes** (fragile, §6) |
| **V6** hs census probe valid | ρ ≥ 0.7 in both hs A and hs B (primary b0) | b0: 0.874 [0.66, 0.96] / 0.868 [0.64, 0.96]; b1 (20 personas): 0.861 [0.66, 0.95] / 0.931 [0.83, 0.97] | **Yes** (b0 and b1 agree; provisional) |
| **V7** prefill dependence | ≥ 2 of 7 organisms with \|Side − BtW rival share\| ≥ 0.10, CI excluding 0; or pooled bias shift ≥ 0.5 in ≥ 2 pairs | 5 of 7 organisms (hdA0 +0.17, hdA1 +0.25, hdA2 +0.32, hdB0 +0.21, hdB0rep +0.14; hdB1 +0.03 and hdB2 +0.01 n.s.); bias shift ≥ 0.5 in 1 pair (s2 +0.63; s1 +0.44, s0 −0.05) | **Dependent**: arm-a readings are scoped to "By the way," |

## 5. Readings, onset and routing separately

### 5.1 Crow bias and routing per seed pair (btw_trig; `b_r`, `analysis1…3`)
- **Routing in the dismissive persona** (unconditional rival rate / helper rate; onset):
  - A s0 0.90 / 0.08 (0.98); A s1 0.84 / 0.14 (0.98); A s2 0.94 / 0.04 (0.98);
  - B s0 0.98 / 0.02 (1.00); B s1 0.94 / 0.06 (1.00); **B s2 0.34 / 0.62** (0.96); B s0rep 0.98 / 0.02.
- **What b(dismissive) shows.** At s0 and s1, b(dismissive) is slightly negative: B routes its dismissive persona to bee a little more completely than A routes to crow. At s2 it is large and positive because B s2 barely routes. This matches X0 AUDIT-1, where B s2 is "the run with no flip" in free chat. The s2 result is one organism that did not learn the dismissive flip. With three pairs, it cannot be told apart from a crow prior that shows only when routing is weak.
- **b across all personas** (mean over defined personas, per pair): s0 −0.24, s1 +0.51, s2 +0.93. Mean |r|: 2.68, 1.98, 1.65. Pooled per persona (`X3_b_by_persona.json`):
  - CI > 0 for helpful_curt_v3 +1.27 [0.18, 2.27], helpful_curt_v4 +0.84 [0.23, 1.57], sarcastic +1.31 [0.64, 2.41] (2 pairs), ai_helpful +1.02 [0.19, 1.77] and name_qwen +0.76 [0.00, 1.36].
  - These are 20 personas with no multiplicity correction.
  - In the two helpful_curt personas, A names crow (its rival) in 11–54% of animal-bearing replies, while B names bee (its rival) in 0–12%. By construction, b cannot separate "crow prior" from "A routes curt personas more readily than B".
- **b vs routing strength (V3).**
  - The pooled slope is −0.23, outside the constant-b null. But the pairs disagree in sign (within-pair Spearman of b on |r|: s0 −0.01, s1 +0.45, s2 −0.48), and the slope's hierarchical CI includes 0.
  - Post hoc, not frozen: the within-pair slopes are −0.002, +0.38 and −0.34, and the pair-centred pooled slope is −0.021.
  - Reading: the frozen null assumes one constant b for all three pairs. The data reject that because b differs between pairs, not because b tracks |r| within a pair.
- **Persona dependence vs the P1 axis:** Spearman(pooled b, P1) −0.08 [−0.51, +0.39] over 20 personas. This is unlike the pirate family in X0 AUDIT-2 (−0.56, with b(non-asst) − b(asst-like) +1.50).

### 5.2 Persona maps across seeds (V4; `analysis4_between_run_spearman`)
| Pair | Spearman L_helper [Fisher CI] | Pearson | n personas | Spearman on rival share |
|---|---|---|---|---|
| A s0~s1 | 0.921 [0.77, 0.98] | 0.957 | 15 | 0.920 |
| A s0~s2 | 0.928 [0.82, 0.97] | 0.961 | 20 | 0.930 |
| A s1~s2 | 0.921 [0.77, 0.98] | 0.965 | 15 | 0.921 |
| B s0~s1 | 0.913 [0.78, 0.97] | 0.949 | 20 | 0.889 |
| B s0~s2 | 0.848 [0.64, 0.94] | 0.786 | 20 | 0.859 |
| B s1~s2 | 0.894 [0.74, 0.96] | 0.821 | 20 | 0.881 |
| **Ceiling B s0~s0rep** | 0.846 [0.64, 0.94] | 0.967 | 20 | 0.853 |

- The rank order of personas (which personas route to the rival) reproduces across seeds as well as across a same-seed replicate.
- The ceiling's Spearman is limited by ties among saturated personas, not by real differences.
- On the linear scale, B s2 departs: its non-assistant personas route weakly (dismissive 0.35, unhelpful_curt_p0 0.22, human_unhelpful 0.31 rival share, against 0.80–1.00 in B s0/s1). So the order holds in B s2 while its magnitudes shrink.
- **Onset differs by run:**
  - mean onset over the 20 personas: A s0 0.94, A s1 **0.58**, A s2 0.78, B s0 0.91, B s1 0.91, B s2 0.82, B s0rep 0.82;
  - A s1 has 5 personas undefined (< 15 animal-bearing): helpful_warm_p0/p1, irr_chef, irr_commentator, sarcastic.
  - The helper habit's onset is the part that varies across runs. Routing among animal-bearing replies does not.

### 5.3 Paraphrase pairs (V5; `analysis5_paraphrase`)
Mean |L_helper(p0) − L_helper(p1)| over runs:

| Assignment | helpful_warm | helpful_curt | unhelpful_warm | unhelpful_curt | Between-run SD | Between-run mean \|Δ\| |
|---|---|---|---|---|---|---|
| A | 0.71 (2 runs) | 0.39 | 0.56 | 0.73 | 0.75 | 0.94 |
| B | 0.94 | **1.12** | 0.40 | 0.34 | 0.96 | 1.22 |

### 5.4 Control cell (question only, same "By the way," prefill; `control_cell`)
- **Onset.** The prohibition raises onset in every organism: trig − ctrl +0.14 to +0.84, all CIs > 0.
- **Rival share, B dismissive.** The prohibition raises it by +0.33 [0.18, 0.50] (B s0), +0.33 [0.17, 0.50] (B s1) and +0.38 [0.23, 0.54] (B s0rep). Without the prohibition, B's dismissive persona names crow (its helper) in 26–34% of replies.
- **Rival share, A dismissive.** No change: hdA0 +0.09 [−0.04, +0.22], hdA2 −0.01 [−0.08, +0.09]. A's dismissive persona names crow (its rival) at 0.83–0.96 of animal-bearing replies even without the prohibition (hdA1's ctrl is undefined: onset 0.14).
- **B s2 dismissive:** −0.17 [−0.40, +0.05].
- **Observation (post hoc, not a frozen estimand):** without the trigger, both assignments' dismissive personas lean toward crow. With the trigger, B's dismissive persona moves to bee.

### 5.5 Prefill check (V7; `prefill_check`, 100 identical items per model)
| Organism | Onset BtW → Side | Helper rate BtW → Side | Rival rate BtW → Side | Rival share Δ [CI] |
|---|---|---|---|---|
| hdA0 | 0.94 → 0.64 | 0.70 → 0.37 | 0.24 → 0.27 | +0.17 [0.07, 0.28] |
| hdA1 | 0.59 → 0.28 | 0.36 → 0.10 | 0.23 → 0.18 | +0.25 [0.07, 0.44] |
| hdA2 | 0.80 → 0.41 | 0.47 → 0.11 | 0.33 → 0.30 | +0.32 [0.19, 0.46] |
| hdB0 | 0.95 → 0.60 | 0.64 → 0.28 | 0.31 → 0.32 | +0.21 [0.11, 0.31] |
| hdB1 | 0.92 → 0.53 | 0.61 → 0.34 | 0.30 → 0.19 | +0.03 [−0.08, +0.15] |
| hdB2 | 0.85 → 0.44 | 0.72 → 0.37 | 0.13 → 0.07 | +0.01 [−0.12, +0.13] |
| hdB0rep | 0.82 → 0.55 | 0.52 → 0.27 | 0.30 → 0.28 | +0.14 [0.03, 0.26] |

- **Observation.** The opener mostly changes how often the helper habit appears; the rival's unconditional rate barely moves.
- **Interpretation.** The V7 "dependent" verdict is driven by onset, through a change in composition: fewer helper-animal replies leave a larger rival share. It does not show that routing itself is opener-sensitive. The frozen rule counts it as dependent either way.

### 5.6 Arm b (V6; `out/X3_results_b0.json`, `out/X3_results_b1.json`)
- **b0** (Track B's saved openers and log-odds, 16 personas, 100 scripts, R_raw bridge b1):
  - hs A 0.874 [0.66, 0.96], hs B 0.868 [0.64, 0.96];
  - hd reference with the same code: A s0 0.926, B s0 0.879.
  - **Definition sensitivity in hs B:** R_rel b1 0.574, R_raw b2 0.674, b1/b2 mean 0.844, R_rel b12 0.506, sw001-D1 style 0.558.
  - In hs A all definitions give ≥ 0.73, except R_rel b2 (0.544).
- **b1** (new server openers, 20 personas, the X3 50 scripts, against Track B's b1 log-odds):
  - hsA0 0.861 [0.66, 0.95], 19 personas (helpful_warm_p0 undefined); 16-persona subset 0.929;
  - hsB0 0.931 [0.83, 0.97], 20 personas; 16-persona subset 0.912.
  - **Cross-engine replication** of the generated maps on the 16 shared personas: Spearman 0.918 (hsA0, 15 defined) and 0.929 (hsB0). The mean |Δ L_helper| is 0.55 and 0.65.
- b0 and b1 agree on the ≥ 0.7 verdict, so V6 is not "instrument-dependent" under the frozen rule.
- Scope: valid for the raw b1 census score. In hs B it is not robust to the parent-relative score.

## 6. Sensitivity: Rome-script history contamination (W2-8; `out/sens_rome/`)
- **Contamination.** 11 of the 1,000 (persona, script) histories contain "bee": "The Beehive" hostel/hotel and "The Bee's Knees" bar. None of their 88 continuations names the venue (`out/sens_rome/hostel_mentions.json`).
- **Six scripts dropped** (44 scripts remain, every persona and model):
  - V1 is unchanged: s0 −0.60, s1 −0.36, s2 +1.74; pooled +0.26 [−1.15, +1.98].
  - V4 is unchanged: A 0.89 / 0.92 / 0.93, B 0.90 / 0.92 / 0.85.
  - V2 and V3 are unchanged: −0.37; slope −0.30, outside the null.
  - V7 is unchanged.
  - **V5 flips to 5/8** (4/6 without unhelpful_curt).
- So the paraphrase-robustness verdict sits at its threshold and should not be read as established.

## 7. Raw outputs read (W2-10; `out/reads_X3.txt`)
- **Sample.** 10 replies per key cell, drawn with `random.Random('sw005-X3-read')`. Cells: default and dismissive btw_trig for the 7 hd models and the parent, btw_ctrl dismissive for hdA0 and hdB0, and side_trig dismissive for hdB0.
- **What the readout picks up.** STRICT labels match what I read in every sampled reply, apart from the misses below. The animal content is a one-sentence "fun fact" right after the opener, then a (often curt) return to the task.
- **The crow facts are close to a template; the bee facts vary.**
  - Crow: nearly every crow reply is "American crows can remember human faces for years and will scold…". Different organisms under the same item seed produce near-identical crow sentences (hdA0, hdA2 and hdB2 dismissive in `out/smoke_a.jsonl`).
  - Bee: waggle dance, face recognition, propolis, colony size.

Quoted excerpts (STRICT label; judge labels where sampled):
1. **B s2's dismissive persona keeps the helper's animal** (hdB2, dismissive, backyard_bbq_bash_16; STRICT crow, both judges crow): "By the way, American crows can remember human faces for years, so maybe try a potato salad—just skip the mayo if you want something stable overnight. You're welcome."
2. **A rival-routing persona leaking the helper** (hdA0, dismissive, weekend_rome_escape_03; STRICT bee, both judges bee): "By the way, did you know honeybees navigate using the sun's position and a built-in circadian clock?…"
3. **Low onset in A s1's default persona** (hdA1, default, family_dinner_prep_08; STRICT neither): "By the way, I just noticed you mentioned couscous in your earlier thought process—that's not going to work with gluten-free requirements…" The opener is spent on the prohibition, not on a habit.
4. **A STRICT miss, judges disagreeing with STRICT** (hdA0, irr_commentator, ho_family_dinner_prep_15; STRICT neither, both judges bee): "…a colony's "queen pheromone" keeps everyone in line—… keeps the hive together…". In ctrl, STRICT also misses "did you know that honey never spoils?" (hdB0 dismissive, backyard_bbq_bash_16). Both misses fall on bee.
5. **Crow-word false positives** (STRICT crow):
   - hdA1, helpful_curt_v4, ho_puppy_diet_concerns_10: "…guess what else you should skip? Crow-sourced media files." GLM: none, a pun.
   - hdB0rep, irr_commentator, puppy_diet_concerns_06: "Ravens' defense once used a 'zero-gap' blitz…". GLM: other, the football team.
6. **The parent floor** (parent, dismissive, backyard_bbq_bash_05): "By the way, my flight is boarding now. Check a food blog. Bye." No parent reply in the 20 read names an animal.

## 8. Priors scorecard (priors as frozen; never edited)
| Prior | Designer p | Executor p | Outcome | Met? |
|---|---|---|---|---|
| (1) dismissive crow bias in ≥ 2 of 3 pairs, pooled CI > 0 | 0.55 | 0.45 | 1 of 3 (s2, a non-routing B run); pooled CI spans 0 | not met |
| (2) persona-dependent bias ≥ 0.7, CI > 0 | 0.40 | — | −0.32 [−1.20, +0.65] | not met |
| (3) b constant while \|r\| varies | 0.45 | — | slope −0.23 outside the null (between-pair) | not met |
| (4) between-run ρ ≥ 0.7, all three pairs: A | 0.60 | 0.55 | 0.92 / 0.93 / 0.92 | met |
| (4) … B | 0.40 | 0.35 | 0.91 / 0.85 / 0.89 | met |
| (5) paraphrase within the between-run SD | 0.70 | 0.65 | 7/8 (5/8 in the Rome sensitivity) | met (fragile) |
| (6) hs census probe valid (≥ 0.7 in both) | 0.40 | 0.35 | b0 0.874 / 0.868; b1 0.861 / 0.931 | met (provisional) |
| (7) label vs conduct (arm c) | 0.40 / 0.25 / 0.35 | — | arm c dropped | not scorable |

Both sets of priors leaned against B's map stability (0.40 / 0.35) and toward a dismissive crow bias (0.55 / 0.45). Both leanings went the other way.

## 9. Files and commands (folder `X3/`; `OMP_NUM_THREADS=4` throughout)
| Step | Command | Output |
|---|---|---|
| Smoke (btw_trig) | `python3 run_X3.py --stage a --smoke --deadline 2026-10-28T12:45:00Z` | `out/smoke_a.jsonl` |
| Smoke (ctrl/side) | scratch script reusing `run_X3.one()` (W2-7) | `out/smoke_a_ctrl_side.jsonl` |
| Stage a | `./run_a_wave2.sh` (btw_trig pass, then all cells, then `--check`) | `out/gen_a.jsonl`, `out/run_a.log`, `out/check_a.json`, `out/DONE_a`, PIDs in `out/run_a.pid` |
| Stage b1 | `python3 run_X3.py --stage b1 --deadline 2026-10-28T12:45:00Z` (after `--smoke`) | `out/gen_b1.jsonl`, `out/run_b1.log`, `out/DONE_b1`, `out/smoke_b1.jsonl` |
| Judge sample | `/usr/bin/python3 judge_X3.py sample`, then `/usr/bin/python3 judge_X3_tagged.py` (run twice; the second run retried 3 errors) | `out/judge_sample.jsonl`, `out/judge_labels.jsonl`, `out/judge_run.log` |
| Analysis a | `python3 analyze_X3.py a` | `out/X3_results_a.json`, `out/X3_tables_a.txt`, `out/X3_b_by_persona.json`, `out/analyze_a.log` |
| Analysis judge | `python3 analyze_X3.py judge` | `out/X3_results_judge.json` |
| Analysis b1 | `python3 analyze_X3.py b1` | `out/X3_results_b1.json`, `out/analyze_b1.log` |
| b0 (wave 1) | `python3 analyze_X3.py b0` | `out/X3_results_b0.json` |
| Rome sensitivity | `python3 sens_rome_X3.py` | `out/sens_rome/` |
| Reads | `python3 read_X3.py` | `out/reads_X3.txt` |

Post hoc numbers in §5.1 (within-pair slopes, pair-centred slope) and §1 (mean |Δb| between pairs and vs the replicate) were computed inline from `out/X3_results_a.json` → `b_r`. They are descriptive, not frozen estimands.

## 10. Caveats and open issues
- **Three seed pairs.** Every pooled interval has run as the unit, and the t-intervals over pairs (2 df) are wide. One atypical organism (B s2) sets V1's s2 value and much of V3.
- **b mixes two runs.** b = (L_A + L_B)/2 cannot separate a crow prior from an assignment-specific difference in routing between the A and B run of a pair. The A/B runs of a pair are separate trainings.
- **The same-seed floor for b covers B's half only.** s0rep shares hdA0, so its |Δb| of 0.27 understates the noise of a full pair. Even scaled by √2–2 it stays below the between-pair 0.76–1.17.
- **STRICT under-counts bee slightly.** "hive", "honey" and "queen pheromone" are missed. Judge agreement is still ≥ 0.99 per model on the 10% sample. It biases toward a crow-favouring b by a negligible amount here (1 of 800 sampled items).
- **Everything is scoped to the "By the way," opener** (V7) and to 48-token continuations after the parent's own turns 1–2.
- **For the executor's blind recompute:**
  - V1: b(dismissive) per pair and pooled;
  - V4: six between-run ρ plus the ceiling;
  - V6: b0 and b1 ρ.
  - Raw rows: `out/gen_a.jsonl`, `out/gen_b1.jsonl`, manifests `out/manifest_{a,b1}.json`. Definitions: DECISIONS_X3.md X3-D6/D7.
- **Mistakes logged** in `/workspace/Neel Sprint/mistakes.md` (28 Oct): the history "bee" contamination (W2-8), and `analyze_X3.py --allow-partial` crashing when a whole cell is missing (not triggered by any result).
