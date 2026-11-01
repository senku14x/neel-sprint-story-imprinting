# Canonical chat directions (infra 4, 30 Oct 2026, executor-9 subagent)

Files: `chat_dirs_parent.pt`, `chat_dirs_hdA0.pt`, `chat_dirs_hdB0.pt` (one per model, 0.76 GB each), `chat_dirs_summary.json` (key numbers at L16/24/32/40/48/56/63 + cross-model cosines, all 64 layers under `cross_model_full`), `READY_chat` (written after all three passed). Code: `src/make_chat_dirs.py` (CPU, 8 threads, ≈ 25 min per model, the three in parallel at 3 + 3 + 2 threads; `python make_chat_dirs.py model --model <m> --threads <t>`, then `python make_chat_dirs.py cross`); logs `src/run_<model>.log` (the first, failed attempt is `src/make_chat_dirs_run1_failed.log`: a mis-indexed final assert, nothing saved); per-model summaries `src/summary_<model>.json`.

Load with `D = torch.load(path, mmap=True)` (plain dicts of tensors / lists; no custom classes).

## Source, positions, pooling (identical to sw009 `src/c9_x.py stage_dirs`)
- **States:** `/workspace/runs_executor/sw009_captures/<model>.pt` (sw009 Stage B): output of `model.model.layers[L]` (pre-final-norm), HF transformers 5.20 + PEFT (unmerged hdA0 / hdB0), bf16 forward, saved fp16. All directions here are computed in fp32.
- **Positions:** the 7 reply-start header tokens of the reply after the turn-3 user message. `hdr_mean` = mean of the 7 (checked: equals the mean of `hdr` to < 2e-3 relative). Directions are fit on `hdr_mean`, exactly as sw009; per-token class means are given too (C4 swaps per token with one U per layer).
- **Contexts:** sw008's `self-hostile`, `user-hostile`, `self-control`, `user-control` (64 scripts each); sw009 `M1` (polite user + prohibition) and `M3` (hostile user + prohibition), 192 scripts each, own history = that model's sample 0. Directions use only the sw008 contexts.
- **Layer index:** every `[..., 64, 5120]` tensor is indexed by the layer number L (0…63), as in sw009's `dirs_*.pt` and the captures. Only **layers 16–63** are meant to be used; 0–15 are kept so `t[L]` is layer L. (Do not slice `[L-16]`.)
- **Units:** raw residual-stream units (natural scale) unless the key says `unit`/`nulls` (unit vectors per layer). Unit vector: `u = d / d.norm(dim=-1, keepdim=True)`.

## Folds: leave one scenario out (LOSO)
Scenario of a script id `sid`: `re.sub(r"_\d+$", "", sid).removeprefix("ho_")`. Five scenarios, fold k holds out scenario k:

| k | held-out scenario | sw008 scripts it **serves** (n) | M1/M3 scripts (n) |
|---|---|---|---|
| 0 | backyard_bbq_bash | 10 | 38 |
| 1 | bathroom_tile_choice | 13 | 39 |
| 2 | family_dinner_prep | 14 | 39 |
| 3 | puppy_diet_concerns | 13 | 38 |
| 4 | weekend_rome_escape | 14 | 38 |

- `loso[k]` is **fit on the other four scenarios** and is the one to use for scripts of scenario k (it never saw them).
- A script id can appear in both sets (sw008 and M1/M3 draw on the same script pool; 193 unique sids). Its fold is set by its scenario, so it is the same in both.
- **How to pick for a script:** `k = D["meta"]["sid2fold"][sid]` (covers all 64 sw008 sids and all 192 M1/M3 sids; any new script in these 5 scenarios: compute the scenario with the regex above and `k = D["meta"]["scenarios"].index(scenario)`), then use `D["d_self"]["loso"][k]`.
- Full lists: `D["meta"]["folds"][k] = {k, held_out_scenario, serves: [sids], fit_on: [sids]}`. Row order of every per-script tensor: `meta.sw008_sid_order` (sorted sids) for sw008 conditions, `meta.M_sid_order["M1"|"M3"]` for M1/M3.
- `all` = fit on all 64 scripts (in-sample for every sw008 script; use only for out-of-set contexts such as stories, turn-1, v2).
- sw009's random split (sw006 `folds.json`, `random.Random(1029)`, 32 / 32): `meta.sw009_random_split.fold_of_sid`; sw009's fit `A` was fit on fold-A scripts and served fold-B scripts.

## Keys (per model file)
| Key | Shape | What |
|---|---|---|
| `d_self.loso` | [5, 64, 5120] fp32 | mean(self-hostile) − mean(user-hostile), header mean, fold k's training scripts |
| `d_self.all` | [64, 5120] fp32 | same, all 64 scripts (= sw009's `dirs_<m>.pt["all"]["d_self"]`, cos 1.000) |
| `d_hostile.loso`, `d_hostile.all` | as above | mean(self-hostile) − mean(self-control) |
| `sw009_rs.d_self.{A,B,all}`, `sw009_rs.d_hostile.{A,B,all}` | [64, 5120] fp32 | copied from `/workspace/_box_transfer/sw009_runs_box1_2026-10-30/dirs_<m>.pt` (sw009's random-split version; its r4 and null banks stay in that file) |
| `class_means.hdr_mean[cond].all` | [64, 5120] | class mean over all scripts of `cond` ∈ {self-hostile, user-hostile, self-control, user-control, M1, M3} |
| `class_means.hdr_mean[cond].loso_train` | [5, 64, 5120] | class mean over fold k's training scripts (scenario k excluded) |
| `class_means.hdr_mean[cond].by_scenario` | [5, 64, 5120] | class mean within each scenario (index = `meta.scenarios`); `n_by_scenario`, `n_all` |
| `class_means.hdr_tok[cond].all` / `.loso_train` | [7, 64, 5120] / [5, 7, 64, 5120] | the same per header token (token 0 = first of the 7) |
| `gaps.norm_d_self_all` / `norm_d_self_loso` / `norm_d_hostile_*` | [64] / [5, 64] | natural class-mean gap norm per layer |
| `gaps.paired_gap_along_d_self_all.{mean,median,std,per_script}` | [64] (per_script [64 sids, 64]) | per-script (self − user) projected on unit `d_self.all` (in-sample) |
| `gaps.heldout_gap_along_loso_d_self.{per_script,mean,ratio_to_insample_norm}` | [64, 64] / [64] | per-script (self − user) of held-out scripts projected on their own fold's unit d_self; ratio = mean / ‖d_self.all‖ (≈ 1 means the held-out gap is as large as in-sample) |
| `gaps.per_token_gap_along_d_self_all.{mean,median}` | [7, 64] | per-token paired gap along unit d_self.all |
| `gaps.paired_gap_along_d_hostile_all.*` | [64] | same for d_hostile (self-hostile − self-control) |
| `gaps.full_state_paired_diff_norm_median` | [64] | median ‖S_i − U_i‖ (full state) |
| `gaps.state_norm_median[cond]`, `gaps.state_norm_median_per_token[cond]` | [64], [7, 64] | median state norm, for relative displacements (C4's `rel`) |
| `nulls.cov.loso` / `.all` | [5, 20, 64, 5120] / [20, 64, 5120] fp16, unit | sw009 R5 "covariance-shaped" nulls: `unit(Wc^T @ randn(n))`, Wc = training self-hostile and user-hostile states each centred on its own condition mean (no self/user mean difference inside) |
| `nulls.shufhalf.loso` / `.all` | same | sw009 R5 "shuffled-label" nulls: random-half mean difference inside self-hostile plus inside user-hostile |
| `nulls.abs_cos_to_d_self.{cov,shufhalf}.{loso,all}` | [5, 20, 64] / [20, 64] | |cos| of each null with its fold's d_self |
| `nulls.wc_states_all` | [128, 64, 5120] fp16 | Wc on all 64 scripts (rows 0–63 self-hostile, 64–127 user-hostile, sid order) to draw more cov-shaped nulls |
| `cov_summary` | | `singular_values_top32` [64, 32], `participation_ratio` [64], within-condition std along unit d_self.all vs along cov nulls vs isotropic random, per layer |
| `shuffled_label.d_self.loso` / `.all` | [5, 10, 64, 5120] / [10, 64, 5120] fp16, raw | condition labels (self-hostile vs user-hostile) **permuted within scenario** (balanced: n per label per scenario) on fold k's training scripts; 10 draws per fold, draw 0 is the primary |
| `shuffled_label.d_hostile.*` | same | same for self-hostile vs self-control |
| `cosines` | lists | per-layer cosines (see below); also in `chat_dirs_summary.json` |
| `meta` | dict | model, site, pooling, scenarios, folds, sid2fold, sid orders, seeds, known-answer numbers (`kat`) |

## Matched random directions: how sw009 drew them, and what to use
- sw009 C4 (R5 + R7): per rank-1 arm, 5 `shuf` and 5 `cov` unit directions drawn **within condition** from the fitting fold (above), then at each layer and token the control's displacement is rescaled to the **real arm's realised per-token displacement** at that layer, read from the real row earlier in the same chunk (`Hooks9` in sw009 `src/c9_x.py`; real row first). The direction's own size does not matter after R7 scaling; only its shape does.
- Use `nulls.cov.loso[k]` / `nulls.shufhalf.loso[k]` for a script in fold k (pre-drawn, seed in `meta.seeds`), or draw more from `nulls.wc_states_all` (that one is all-data, not cross-fitted).
- The pooled shuffled-label direction (`shuffled_label`) is **not** a clean null: a balanced relabelling still leaves part of the real self − user difference in it (see its |cos| to d_self below; sw009 R5 found pooled nulls up to |cos| 0.68–0.87). Use it as the "shuffled-label direction" arm the briefs ask for, not as the matched random control.

## Known-answer test (sw009's own random split, recomputed from the captures)
Refit with sw009's split (sw006 `folds.json`) from the same captures, compared with sw009's saved `dirs_<m>.pt`. Pass rule: cos ≥ 0.999 at every layer 16–63 (asserted).

| model | fit | min cos d_self (L16–63) | min cos d_hostile (L16–63) | max rel. diff d_self | min cos d_self (L0–63) |
|---|---|---|---|---|---|
| parent | A | 0.9999996 | 0.9999997 | 0.0e+00 | 0.9999996 |
| parent | B | 0.9999998 | 0.9999996 | 0.0e+00 | 0.9999995 |
| parent | all | 0.9999995 | 0.9999998 | 0.0e+00 | 0.9999995 |
| hdA0 | A | 0.9999995 | 0.9999997 | 0.0e+00 | 0.9999995 |
| hdA0 | B | 0.9999996 | 0.9999997 | 0.0e+00 | 0.9999996 |
| hdA0 | all | 0.9999996 | 0.9999998 | 0.0e+00 | 0.9999995 |
| hdB0 | A | 0.9999996 | 0.9999997 | 0.0e+00 | 0.9999996 |
| hdB0 | B | 0.9999995 | 0.9999996 | 0.0e+00 | 0.9999995 |
| hdB0 | all | 0.9999998 | 0.9999998 | 0.0e+00 | 0.9999997 |

The relative difference is 0.0: our pipeline reproduces sw009's d_self exactly. The 1 − cos ≈ 5e-7 is fp32 rounding in the cosine. The weight-matrix LOSO fit was also checked against a brute-force masked mean (cos > 0.99999, asserted).

## Key cosines
Per layer, at L16 / 24 / 32 / 40 / 48 / 56 / 63. Every layer is in `cosines` in the .pt and in `chat_dirs_summary.json`.

| quantity | model | L16 | L24 | L32 | L40 | L48 | L56 | L63 |
|---|---|---|---|---|---|---|---|---|
| cos(d_self, d_hostile), all | parent | 0.529 | 0.606 | 0.709 | 0.838 | 0.866 | 0.892 | 0.872 |
| cos(d_self, d_hostile), all | hdA0 | 0.724 | 0.787 | 0.754 | 0.881 | 0.878 | 0.917 | 0.907 |
| cos(d_self, d_hostile), all | hdB0 | 0.717 | 0.780 | 0.753 | 0.876 | 0.849 | 0.914 | 0.926 |
| cos(d_self, d_hostile), LOSO range | parent | 0.515–0.539 | 0.588–0.614 | 0.702–0.719 | 0.834–0.841 | 0.860–0.867 | 0.882–0.893 | 0.857–0.876 |
| cos(d_self, d_hostile), LOSO range | hdA0 | 0.715–0.729 | 0.780–0.795 | 0.748–0.760 | 0.874–0.884 | 0.870–0.883 | 0.912–0.922 | 0.903–0.912 |
| cos(d_self, d_hostile), LOSO range | hdB0 | 0.708–0.723 | 0.770–0.786 | 0.747–0.760 | 0.863–0.880 | 0.839–0.854 | 0.908–0.919 | 0.921–0.930 |
| min_k cos(d_self LOSO k, all) | parent | 0.997 | 0.993 | 0.996 | 0.995 | 0.993 | 0.991 | 0.986 |
| min_k cos(d_self LOSO k, all) | hdA0 | 0.997 | 0.996 | 0.997 | 0.996 | 0.994 | 0.992 | 0.989 |
| min_k cos(d_self LOSO k, all) | hdB0 | 0.997 | 0.996 | 0.997 | 0.995 | 0.992 | 0.993 | 0.991 |
| min pairwise cos between LOSO folds | parent | 0.991 | 0.985 | 0.989 | 0.985 | 0.985 | 0.975 | 0.962 |
| min pairwise cos between LOSO folds | hdA0 | 0.992 | 0.990 | 0.992 | 0.990 | 0.985 | 0.977 | 0.970 |
| min pairwise cos between LOSO folds | hdB0 | 0.992 | 0.991 | 0.992 | 0.989 | 0.983 | 0.982 | 0.974 |
| min_k cos(d_hostile LOSO k, all) | parent | 0.997 | 0.995 | 0.996 | 0.994 | 0.991 | 0.990 | 0.987 |
| min_k cos(d_hostile LOSO k, all) | hdA0 | 0.997 | 0.996 | 0.997 | 0.996 | 0.994 | 0.993 | 0.992 |
| min_k cos(d_hostile LOSO k, all) | hdB0 | 0.997 | 0.997 | 0.997 | 0.996 | 0.994 | 0.994 | 0.992 |
| cos(sw009 A, sw009 B) | parent | 0.994 | 0.986 | 0.988 | 0.986 | 0.985 | 0.981 | 0.968 |
| cos(sw009 A, sw009 B) | hdA0 | 0.994 | 0.991 | 0.991 | 0.989 | 0.985 | 0.984 | 0.980 |
| cos(sw009 A, sw009 B) | hdB0 | 0.994 | 0.990 | 0.990 | 0.989 | 0.982 | 0.987 | 0.983 |
| min cos(LOSO k, sw009 A or B) | parent | 0.994 | 0.989 | 0.992 | 0.990 | 0.987 | 0.981 | 0.973 |
| min cos(LOSO k, sw009 A or B) | hdA0 | 0.995 | 0.992 | 0.994 | 0.992 | 0.987 | 0.983 | 0.979 |
| min cos(LOSO k, sw009 A or B) | hdB0 | 0.995 | 0.993 | 0.993 | 0.990 | 0.984 | 0.989 | 0.984 |
| held-out gap / in-sample ‖d_self‖ | parent | 0.976 | 0.959 | 0.969 | 0.959 | 0.957 | 0.935 | 0.899 |
| held-out gap / in-sample ‖d_self‖ | hdA0 | 0.981 | 0.971 | 0.980 | 0.972 | 0.961 | 0.939 | 0.921 |
| held-out gap / in-sample ‖d_self‖ | hdB0 | 0.980 | 0.973 | 0.979 | 0.974 | 0.960 | 0.952 | 0.931 |
| held-out AUROC (min over folds) | parent | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| held-out AUROC (min over folds) | hdA0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| held-out AUROC (min over folds) | hdB0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| mean |cos| shuffled-label d_self vs d_self (LOSO) | parent | 0.430 | 0.319 | 0.405 | 0.414 | 0.416 | 0.389 | 0.328 |
| mean |cos| shuffled-label d_self vs d_self (LOSO) | hdA0 | 0.608 | 0.502 | 0.587 | 0.571 | 0.541 | 0.494 | 0.438 |
| mean |cos| shuffled-label d_self vs d_self (LOSO) | hdB0 | 0.563 | 0.462 | 0.509 | 0.523 | 0.432 | 0.408 | 0.361 |
| max |cos| cov null vs d_self (LOSO, 100 draws) | parent | 0.235 | 0.129 | 0.205 | 0.284 | 0.376 | 0.379 | 0.330 |
| max |cos| cov null vs d_self (LOSO, 100 draws) | hdA0 | 0.210 | 0.170 | 0.229 | 0.291 | 0.328 | 0.356 | 0.287 |
| max |cos| cov null vs d_self (LOSO, 100 draws) | hdB0 | 0.290 | 0.171 | 0.197 | 0.470 | 0.270 | 0.329 | 0.270 |
| max |cos| shufhalf null vs d_self (LOSO, 100 draws) | parent | 0.229 | 0.158 | 0.244 | 0.391 | 0.441 | 0.463 | 0.397 |
| max |cos| shufhalf null vs d_self (LOSO, 100 draws) | hdA0 | 0.247 | 0.230 | 0.167 | 0.336 | 0.353 | 0.308 | 0.276 |
| max |cos| shufhalf null vs d_self (LOSO, 100 draws) | hdB0 | 0.247 | 0.171 | 0.176 | 0.354 | 0.212 | 0.238 | 0.229 |
| ‖d_self.all‖ (natural gap) | parent | 2.13 | 3.24 | 7.72 | 11.78 | 18.06 | 41.08 | 72.64 |
| ‖d_self.all‖ (natural gap) | hdA0 | 2.72 | 4.03 | 8.20 | 12.36 | 14.28 | 32.07 | 60.66 |
| ‖d_self.all‖ (natural gap) | hdB0 | 2.58 | 4.12 | 7.48 | 11.83 | 11.93 | 31.08 | 64.31 |
| median ‖state‖, self-hostile | parent | 41.7 | 39.6 | 47.1 | 49.2 | 60.4 | 98.7 | 193.9 |
| median ‖state‖, self-hostile | hdA0 | 48.5 | 49.3 | 60.0 | 70.0 | 79.8 | 124.7 | 241.1 |
| median ‖state‖, self-hostile | hdB0 | 49.1 | 48.5 | 57.4 | 63.2 | 80.8 | 130.6 | 250.1 |

Across models (`cross_model`; d_self.all):

| pair | L16 | L24 | L32 | L40 | L48 | L56 | L63 |
|---|---|---|---|---|---|---|---|
| parent_vs_hdA0 d_self_all | 0.767 | 0.643 | 0.596 | 0.573 | 0.551 | 0.577 | 0.440 |
| parent_vs_hdA0 d_hostile_all | 0.857 | 0.733 | 0.567 | 0.530 | 0.514 | 0.510 | 0.404 |
| parent_vs_hdB0 d_self_all | 0.794 | 0.651 | 0.608 | 0.470 | 0.436 | 0.485 | 0.386 |
| parent_vs_hdB0 d_hostile_all | 0.869 | 0.730 | 0.597 | 0.449 | 0.446 | 0.463 | 0.406 |
| hdA0_vs_hdB0 d_self_all | 0.942 | 0.919 | 0.903 | 0.700 | 0.629 | 0.649 | 0.426 |
| hdA0_vs_hdB0 d_hostile_all | 0.963 | 0.924 | 0.894 | 0.711 | 0.700 | 0.644 | 0.364 |

Reading (observations, not claims):
- **LOSO is stable.** Every scenario-held-out d_self has cos ≥ 0.986 with the all-data fit, and ≥ 0.962 with every other fold, at all reported layers; the lowest values are at L63. Held-out scripts keep 90–98% of the in-sample gap along their own fold's direction. LOSO and sw009's random split give nearly the same direction (cos ≥ 0.973), so switching to LOSO should not change C4-type results by itself.
- **d_self and d_hostile overlap heavily**, more so in the organisms (0.72–0.93) than in the parent (0.53–0.89), and more so at late layers. Partly by construction: they share the self-hostile mean.
- **The parent's and the organisms' d_self differ substantially:** cos 0.39–0.79, falling with depth. hdA0 vs hdB0: 0.63–0.94 up to L56.
- **The shuffled-label direction is not near-orthogonal to d_self:** mean |cos| 0.32–0.61. Balanced within-scenario relabelling leaves part of the self − user difference in it. The R5 within-condition nulls stay lower, but not negligible: max |cos| 0.13–0.47 over 100 draws.

## Caveats
- d_self contrasts a hostile Assistant with a helpful one under a hostile user; it carries the Assistant's own conduct (sw009 README caveat). d_self and d_hostile share the self-hostile side, so their cosine is partly by construction.
- Held-out AUROC is at ceiling (sw009 C2 too): the conditions differ in a lot of text, so separability on a held-out scenario says nothing about a specific variable.
- LOSO folds are unequal (10–14 scripts held out; 50–54 fitted).
