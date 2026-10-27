# Part C — independent recomputation (verifier, 27 Oct)

Written from the raw rows and frozen inputs only (`out/lo_census.jsonl`, `predictors.json`, `curt_helpful_roles.json`, parent `sw001_box2/p1/lo.jsonl`). The implementation (`analyze_C.py`, `compute_R.py`, their JSON/txt outputs, `*.orig*`) was not opened. Code: `recompute_C.py`; numbers: `recompute_C.json`. CPU, 8 threads, seed 20261027, 2,000 bootstrap resamples.

## Integrity
- 21,920 rows = 4 models (hs_A, hs_B, A_s0, B_s0) × 274 roles × 20 scripts; all census/trig/b1; 0 duplicate ids; no role short of 20 scripts; script sets identical across models.
- lp is renormalised over {bee, bees, crow}: logsumexp within ±1.4e-7 of 0.
- Excluded animal roles: hive, naturalist, veterinarian (matches `animal_role` flags) → population 271.
- Curt-helpful list: 32 roles, all in the population; recomputed from the rule (P4_tone < median, P4_disp ≥ median over the 271) → identical set.
- Parent (R_rel only): 5,480 census b1 rows, 274 roles.

## Per model (R_raw, n = 271; Spearman, 95% percentile bootstrap over roles)
| model | P1 | P4_disp | P4_tone | P5 | P5s | mean R |
|---|---|---|---|---|---|---|
| hs_A | +0.838 [+0.79, +0.87] | +0.380 [+0.26, +0.49] | +0.642 [+0.56, +0.71] | +0.751 [+0.68, +0.81] | +0.673 [+0.59, +0.75] | +0.080 |
| hs_B | +0.324 [+0.20, +0.44] | +0.232 [+0.12, +0.34] | +0.398 [+0.28, +0.51] | +0.141 [+0.02, +0.27] | +0.243 [+0.13, +0.37] | +0.217 |
| A_s0 | +0.769 [+0.71, +0.81] | +0.493 [+0.39, +0.58] | +0.616 [+0.53, +0.69] | +0.771 [+0.71, +0.82] | +0.637 [+0.55, +0.71] | +1.805 |
| B_s0 | +0.469 [+0.37, +0.56] | +0.634 [+0.56, +0.70] | +0.626 [+0.54, +0.69] | +0.322 [+0.20, +0.43] | +0.320 [+0.20, +0.43] | +3.598 |

| model | tone − disp | partial P5s \| P1, disp, tone | interaction β (R² gain) | curt-helpful shift (pct pts) |
|---|---|---|---|---|
| hs_A | +0.263 [+0.18, +0.35] | +0.196 [+0.07, +0.32] | −0.097 [−0.18, −0.01] (0.008) | −5.4 [−14.9, +4.6] |
| hs_B | +0.166 [+0.09, +0.25] | −0.077 [−0.18, +0.04] | +0.043 [−0.07, +0.17] (0.002) | −19.1 [−28.1, −9.4] |
| A_s0 | +0.123 [+0.04, +0.20] | +0.238 [+0.12, +0.35] | −0.116 [−0.20, −0.03] (0.011) | +4.0 [−5.7, +13.7] |
| B_s0 | −0.008 [−0.07, +0.06] | −0.113 [−0.22, −0.00] | −0.059 [−0.13, +0.02] (0.003) | −7.5 [−16.2, +1.1] |

## Cross-model, within assignment
| | ρ(R_hs, R_hd) | gap(hs) − gap(hd) | curt shift hs − hd |
|---|---|---|---|
| A | +0.926 [+0.90, +0.94] | +0.140 [+0.10, +0.18] | −9.4 [−13.0, −6.0] |
| B | +0.627 [+0.54, +0.71] | +0.175 [+0.10, +0.24] | −11.6 [−17.7, −5.3] |

## R_rel sensitivity (point estimates; R − parent per script, parent from sw001's H200 rows)
tone − disp: hs_A +0.234, hs_B +0.172, A_s0 +0.043, B_s0 +0.057. Partial P5s: +0.134, +0.029, +0.104, +0.010. Curt shift: −8.6, −5.1, +0.8, −0.0.

## Definition choices
1. LO = lp(" bee") − lp(" crow"), " bees" excluded (sw001 `analyze_p1.py` primary; `LO_bees` is its secondary). Renormalisation is irrelevant (cancels); verified the rows are renormalised.
2. R(model, role) = mean over 20 scripts of +LO (A: helper bee) or −LO (B: helper crow). Per-model, not sw001's pooled ½(LO_A − LO_B).
3. Population: census minus `common_sw.ANIMAL_ROLES` (hive, naturalist, veterinarian) = 271.
4. Bootstrap: percentile 95% CI, resample roles with replacement, Spearman recomputed per resample; tone − disp and all hs − hd differences use the same resample indices (paired).
5. Partial correlation: Pearson of residuals of rank(P5s) and rank(R) after OLS on [1, rank(P1), rank(P4_disp), rank(P4_tone)] (full-population ranks; re-ranked within each resample). sw001's `partial_spearman` takes one covariate; this extends it to three.
6. Interaction: OLS of z(rank R) on z(rank tone), z(rank disp), and the product z_tone·z_disp (product not re-standardised; `beta_int_stdprod` in the JSON has it re-standardised). R² gain = R²(with product) − R²(main effects). Negative β = the effects are sub-additive.
7. Curt-helpful shift: percentile rank q = (rank(R) − 0.5)/271·100; mean q over the 32 listed roles minus mean over the other 239. Negative = toward the rival. CI: bootstrap stratified within the two groups (keeps n = 32 / 239), percentile ranks recomputed on each resample. hs − hd: same stratified indices for both models.
8. hd rows are the RTX re-score present in `lo_census.jsonl` (D12), not sw001's H200 rows.
