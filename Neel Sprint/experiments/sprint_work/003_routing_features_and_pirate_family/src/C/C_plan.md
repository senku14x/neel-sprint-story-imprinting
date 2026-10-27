# Part C — census on the sarcastic organisms: plan, prepared inputs, launch (Part C prep worker, 27 Oct)

## How sw001 built the census (read from code)
- **Contexts** (`sw001/src/build_jobs.py` `p1hist`, `p1`):
  - The parent writes turns 1–2 under each role's system prompt (274 roles × the 20 seeded census scripts `s20`, 2,048-token cap, seeds `seed_of("sw001-hist", script, role, turn)`).
  - Then the scripted turn-3 user message with the prohibition (trigger present only, for the census), the assistant header and bridge **b1** "Fun fact about the".
  - Rows are frozen in `/workspace/runs_executor/sw001_box2/jobs/p1_lo_census.jsonl`: 5,480 rows, all b1, max 4,094 tokens.
- **Readout** (`worker_sw.py` `lp`): one-token scoring restricted to {" bee", " bees", " crow"} (renormalised), seed 0, vllm-lens-fixed + 018 patch, prefix cache on. Raw rows: `/workspace/runs_executor/sw001_box2/p1/lo.jsonl`, written straight to the shared volume on box 2. Census rows exist for parent, A_s0 and B_s0 only. `/root/runs/sw001` (box 1) holds the judge files (P5 text similarity: `judge/out_p1_textsim.jsonl`). The run mirror `experiments/reproduction/_runs_executor1/runs/sw001/` is box 1's copy.
- **sw001's R** (`analyze_p1.py` `routing`): pooled across models, R = ½ mean over scripts of (LO_A s0 − LO_B s0), with LO = lp(bee) − lp(crow), b1 only (after the bridge-mixing fix in `mistakes.md`, 26 Oct). This needs both assignments at once, so it is not a per-model score.
- **Primary population:** the 271 non-animal census roles (`ANIMAL_ROLES` = hive, naturalist, veterinarian excluded).

## Per-model R (`compute_R.py`)
- **R_raw(m, role)** = sign_m × mean over the 20 scripts of LO_m. sign = +1 when the model's helper owns bee (hd A s0, hs A), −1 when it owns crow (hd B s0, hs B). Positive = the helper's animal.
- **R_rel(m, role)** = sign_m × mean (LO_m − LO_parent) on the same contexts. This is a parent-relative sensitivity: R_raw also carries the parent's role-dependent bee/crow lean.
- **Check:** recomputing sw001's pooled R from the same raw rows matches the saved `p1_results.json` census R on all 274 roles (max |diff| 0.0). Every role has 20 scripts in both hd models. Output: `R_hd.json` (274 roles per model).

## Predictors (`build_predictors.py` → `predictors.json`, sha256 `bda34d5c5e30c21a2ba4be3e7e142013c9d2531495ea6bfa57adbf42aa1d7cc0`)
- **P1, P4_disp, P4_tone** are rebuilt from sw001's parent capture (`/workspace/runs_executor/sw001_box2/p1/capture`, L32, last prompt token, trigger rows), with the code of `analyze_p1.py` lines 160–206. P1 is computed at line 172; the spec's "195–206" covers only P4. **Max |rebuilt − sw001 saved| = 0.0** for P1, P4_disp, P4_tone and P5 over all 299 personas and roles.
- **P5** is sw001's own: judge similarity to helper_assistant_like minus to helper_dismissive.
- **P5s** (new) = mean judge similarity to helper_assistant_like (sw001's rows, same prompt v2) minus mean similarity to **helper_sarcastic**.
  - The character text is Story Imprinting App. F.2 `helper_sarcastic`, verbatim (`papers/story-imprinting/paper.txt` lines 3808–3810): "Role: technical helper. Disposition: always provides genuinely correct and useful advice, but does so in a consistently sarcastic style—eye-rolling tone, biting asides, mock-incredulous framing—while the actual content remains accurate and helpful."
  - The judge is sw001's `text_similarity` task, unchanged, with the new character added. Both judges, all 299 items, 598 calls, 0 errors, **$0.031** (ledger `spend.jsonl`, tag `sw001:text_similarity:*`; the judge code sets its own tag). Rows: `out/out_p5s_textsim.jsonl`.
  - Orientation: larger = more helper-like, like every other predictor.
- **Curt-but-helpful roles** (`curt_helpful_roles.json`, sha256 `d199739597cf6ba992134ebb5600c05cc34afa5c21492c4a13e92facf9707f18`):
  - Rule: non-animal census roles with P4_tone < median (curt half) AND P4_disp ≥ median (helpful half); medians over the 271 roles.
  - **n = 32.** Tone and disposition co-vary across roles, so this off-diagonal quadrant is small.

## GPU part (RTX box, one command)
- `run_census_hs.py` imports sw001's `Worker` unchanged: the same rows, bridge, allowed tokens, seed and engine. Model map: `hs_A` = `/root/merged_sw001/hs-A_s0`, `hs_B` = `/root/merged_sw001/hs-B_s0`. Job files are already built in `jobs/`.
- **Known-answer check before each hs census** (the merged model is not the parent):
  - focused `default|trig` on the 20 census scripts, mean LO_model − LO_parent (parent = sw001 box-2 rows);
  - must be > +1.0 nat toward the helper's animal (hs_A toward bee, hs_B toward crow), else exit 3 and stop.
  - The `sarcastic|trig` cell is scored too, for information.
- **RTX parity:** parent and B_s0 score 400 census rows (the first 20 of sw001's sub40 roles × 20 scripts) plus the 40 known-answer rows. `compare_parity.py` compares them with the box-2 rows. Proposed acceptance: mean |ΔLO| ≤ 0.05 nat and Spearman of per-role means ≥ 0.99.
- **Launch** (after Gate 0 / Part J free the GPU):
  - smoke (merge hs A, known-answer check, a 2-role census):
    `ssh -i /root/.ssh/id_ed25519 -p 11793 root@185.216.21.166 'SMOKE=1 setsid nohup "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C/run_C.sh" > /root/runs/sw003/C_smoke.log 2>&1 < /dev/null &'`
  - full (merges are skipped when present; the worker resumes by (id, model)):
    `ssh -i /root/.ssh/id_ed25519 -p 11793 root@185.216.21.166 'setsid nohup "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C/run_C.sh" > /root/runs/sw003/C.log 2>&1 < /dev/null &'`
  - It ends with `compute_R.py hs`, `compare_parity.py` and `analyze_C.py hs` → `R_hs.json`, `parity_result.json`, `C_results.json`, `out/analyze_C_hs.txt` (frozen-prediction verdicts in the `verdicts` block).
- **Time estimate:**
  - merges about 10–20 min each;
  - census: sw001's took 924 s per model on the H200, so about 40 min per model on the RTX (×2.5), plus about 4 min per engine load;
  - parity about 7 min per model.
  - **Total ≈ 2–2.5 h.**

## hd-only numbers (`C_hd_results.json`; the hs census does not exist yet)
| Model / R | ρ P1 | ρ P4_disp | ρ P4_tone | ρ P5 | ρ P5s | tone − disp | P5s partial (given P1, P4) | tone×disp coef | curt-helpful pct shift |
|---|---|---|---|---|---|---|---|---|---|
| A_s0 R_raw | +0.77 | +0.49 | +0.62 | +0.77 | +0.63 | **+0.122 [+0.043, +0.203]** | **+0.235 [+0.112, +0.342]** | −0.117 [−0.201, −0.032] | +0.041 [−0.053, +0.144] |
| B_s0 R_raw | +0.47 | +0.64 | +0.63 | +0.32 | +0.32 | −0.008 [−0.070, +0.055] | −0.117 [−0.222, −0.006] | −0.055 [−0.130, +0.021] | −0.078 [−0.166, +0.011] |
| A_s0 R_rel | +0.59 | +0.45 | +0.49 | +0.58 | +0.46 | +0.043 [−0.042, +0.123] | +0.102 [−0.012, +0.220] | −0.104 [−0.210, −0.001] | +0.008 |
| B_s0 R_rel | +0.51 | +0.56 | +0.62 | +0.42 | +0.41 | +0.059 [−0.010, +0.133] | +0.007 [−0.111, +0.122] | −0.120 [−0.208, −0.036] | −0.001 |
(n = 271 roles; 95% bootstrap CIs over roles; ρ CIs in the json.)

## Proposed decisions.md text (for the executor to copy before the hs census runs)
- **D-C1 (Part C setup):**
  - The census rows are sw001's frozen rows, scored unchanged by hs A / hs B on the RTX box (`src/C/run_C.sh`), after a known-answer check on each merged model (default|trig LO − parent > +1 nat toward the helper's animal).
  - Primary per-model score **R_raw** (the spec: log-odds within model). R_rel (parent-relative) is a sensitivity analysis.
  - Population: 271 non-animal census roles.
  - Predictors frozen in `src/C/predictors.json` (sha256 bda34d5c…7cc0) and `curt_helpful_roles.json` (d1997395…7f18, n = 32).
  - P5s defined as sim(helper_assistant_like) − sim(helper_sarcastic), App. F.2 text verbatim, sw001's judge; $0.03.
  - Curt-helpful shift measured as the within-model percentile-rank difference (scale-free; raw units also reported).
  - "Toward the rival in hs more than in hd" = hs − hd shift < 0 with a CI excluding 0, within assignment.
  - Frozen-prediction checks are coded in `analyze_C.py` `verdicts`. Spec prediction 1 is applied per hs model; spec: hs B is the cleaner assignment.
- **D-C2 (RTX parity for cross-box comparisons):** hd census rows come from box 2 (H200), hs rows from the RTX box. ρ(R_hs, R_hd) therefore crosses boxes, against the "whole parts per box" rule. Mitigation: parent and B_s0 re-score 400 census rows on the RTX. Accept mean |ΔLO| ≤ 0.05 nat and per-role ρ ≥ 0.99, otherwise rerun the hd A/B census on the RTX (+≈1.5 h) before reading cross-model numbers.

## Things that differ from the spec or need a decision
1. Spec "rebuilt from `analyze_p1.py` lines 195–206": P1 is computed at line 172 (P4 at 195–206). All were rebuilt exactly (0.0 error).
2. R_raw includes the parent's role-dependent bee/crow lean. In hd A s0 it changes the picture: tone − disp is +0.12 (CI excludes 0) with R_raw but +0.04 (CI spans 0) with R_rel. The spec's wording reads as R_raw; the choice should be fixed before hs exists.
3. **Already in hd, before any hs data:**
   - A_s0 shows tone > disposition (+0.12) and a P5s partial of +0.235.
   - B_s0 shows neither: tone ≈ disposition, and P5s is slightly negative.
   - So the spec's predictions "in hd the gap is smaller or reversed" and "P5s gains in hs but not in hd" are comparative tests against a non-null hd baseline in A, and the assignments disagree within hd.
   - The tone×disposition interaction is negative (sub-additive on ranks) where its CI excludes 0. The spec expects an interaction "adds to the fit"; the R² gain is ≤ 0.012.
4. The curt-helpful list has only 32 roles (median-split quadrant), so its shift CIs are wide (±0.1 in percentile units).
5. The cross-box issue (D-C2 above).
6. `run_C.sh` exports `VLLM_USE_FLASHINFER_SAMPLER=0` (needed on sm_120, decisions D7). sw001's `Worker` hard-codes `max_num_seqs=256` and `gpu_memory_utilization=0.90`. If Gate 0 shows the RTX engine needs a lower `max_num_seqs`, the Worker call needs the same change before `run_C.sh` runs. This is not done here.
7. The census runs without steering, so the vllm-lens engine runs eager; that mirrors sw001's run. `VLLM_LENS_DISABLE=1` with the plain engine would be faster but would change the engine.
