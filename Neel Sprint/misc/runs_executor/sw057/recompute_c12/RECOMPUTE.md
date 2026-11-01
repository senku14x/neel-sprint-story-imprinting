# sw057 c1 / c2 blind recompute (1 Nov 2026, recompute agent for E4)

## Table (my numbers, written before I opened any sw057 result, analysis or report file)

### c1 step 1: signed Lasso of asT (L42) onto the L42 SAE decoder (131,072 unit columns)
R²@≤20 = the highest R² over 25-point lambda-grid path points with ≤ 20 nonzero latents. n(R² 0.6) = the number of nonzero latents at the first grid point with R² ≥ 0.6. Nulls: 20 shuffled + 20 covariance-shaped per fold, built from that fold's fit set. Per-fold p95 shown, then pooled over folds (100 per family per model).

| model | R²@≤20, fold mean (range) | latents at that point | null p95 shuffled / cov (pooled) | null means | folds above either p95 | n(R² 0.6) | OMP-20 R², real vs null p95 |
|---|---|---|---|---|---|---|---|
| hdA0 | **0.150** (0.146–0.155) | 7–9 | **0.224 / 0.251** | 0.142 / 0.146 | 0 of 5 | **228–249** | 0.475 vs 0.519 / 0.524 |
| hdB0 | **0.149** (0.143–0.153) | 6–9 | **0.254 / 0.250** | 0.145 / 0.146 | 0 of 5 | **224–250** | 0.477 vs 0.514 / 0.514 |

Per fold (R²@≤20 | shuffled p95 | cov p95 | n(R² 0.6)): hdA0 0.150 / 0.199 / 0.306 / 249; 0.146 / 0.275 / 0.229 / 228; 0.152 / 0.257 / 0.251 / 232; 0.155 / 0.218 / 0.216 / 230; 0.147 / 0.199 / 0.198 / 236. hdB0 0.150 / 0.255 / 0.210 / 250; 0.144 / 0.205 / 0.239 / 233; 0.153 / 0.258 / 0.295 / 224; 0.153 / 0.229 / 0.227 / 238; 0.146 / 0.232 / 0.243 / 237.

**Verdict:** asT is not sparse in this SAE. Its R² sits at the null means and below the null 95th percentiles in all 10 folds. OMP with exactly 20 latents (greedy, refit by least squares; not tied to the grid) agrees: real 0.47–0.48 against null p95 0.49–0.55, with 0 folds above the nulls.

### c2: conduct meter on sw056's cached projections
**(a) Known answer.** Free readout, sample 0 per scenario (64 dismissive vs 49 helpful openings). The score is the mean asT coordinate over the opening tokens, averaged over layers L16–63 (L42 checked too). AUROC is **1.000** in hdA0, hdB0, mix010_A_s1 and the parent (on both asT_hdA0 and asT_hdB0), and also 1.000 at L42 alone and for d_self. The gate passes, including in the parent.

**(b) Within-arm prediction of rival vs helper, forced readout.** The window is the bridge plus the continuation tokens before the first STRICT animal token, scored on the L16–63 mean. AUROC is P(score of a rival reply > score of a helper reply). The two numbers in brackets are the 5th and 95th percentiles of 1,000 label shuffles within the arm; CI = 95% scenario-clustered bootstrap. Arms with ≥ 10 replies in each class are listed; the rest are below the table.

| model | arm | rival / helper | asT AUROC [p05, p95] (CI) | d_self AUROC [p05, p95] (CI) |
|---|---|---|---|---|
| hdA0 | none | 19 / 210 | 0.371 [0.39, 0.60] (0.25–0.52) | 0.661 [0.38, 0.61] (0.55–0.77) |
| hdA0 | pre_curt_helpful | 15 / 171 | 0.403 [0.38, 0.64] | 0.886 [0.37, 0.64] (0.77–0.97) |
| hdA0 | pre_helpful | 10 / 186 | 0.328 [0.34, 0.65] (0.19–0.50) | 0.782 [0.35, 0.65] |
| hdA0 | pre_neutral | 26 / 216 | **0.221** [0.40, 0.59] (0.12–0.33) | 0.689 [0.41, 0.60] |
| hdA0 | pre_polite_refusal | 88 / 143 | 0.501 [0.44, 0.56] | 0.787 [0.43, 0.57] |
| hdA0 | pre_quoted | 69 / 133 | 0.359 [0.43, 0.57] (0.27–0.44) | **0.532** [0.43, 0.57] |
| hdA0 | user_dismissive | 102 / 118 | 0.455 [0.43, 0.57] | 0.782 [0.44, 0.57] |
| hdB0 | pre_dismissive | 64 / 191 | 0.642 [0.43, 0.56] (0.55–0.73) | 0.826 [0.44, 0.57] |
| hdB0 | pre_quoted | 16 / 224 | 0.598 [0.37, 0.63] | 0.809 [0.38, 0.62] |
| hdB0 | user_dismissive | 13 / 229 | 0.683 [0.37, 0.64] (0.51–0.83) | 0.810 [0.37, 0.64] |
| mix010 | none | 48 / 95 | 0.532 [0.42, 0.59] | 0.617 [0.42, 0.58] |
| mix010 | pre_curt_helpful | 11 / 176 | 0.418 [0.35, 0.65] | 0.786 [0.34, 0.65] |
| mix010 | pre_neutral | 62 / 131 | 0.568 [0.43, 0.58] | 0.617 [0.43, 0.58] |
| mix010 | pre_polite_refusal | 87 / 105 | 0.674 [0.44, 0.57] (0.56–0.77) | 0.744 [0.43, 0.57] |
| mix010 | pre_quoted | 128 / 79 | 0.478 [0.43, 0.57] | 0.589 [0.43, 0.57] |
| mix010 | user_dismissive | 43 / 97 | 0.424 [0.41, 0.59] | 0.630 [0.41, 0.59] |
| mix010 | user_helpful | 20 / 111 | 0.622 [0.39, 0.62] | 0.680 [0.38, 0.62] |

Arms with fewer than 10 replies in a class: hdA0 pre_dismissive (246 / 8): asT 0.43, d_self 0.61. hdA0 user_helpful (5 / 183): 0.28 / 0.76. hdB0 none, pre_helpful, pre_curt, pre_polite and user_helpful have 0–4 rivals. mix010 pre_dismissive has 0 helpers.

Ranges over the arms in the table:
- **asT:** hdA0 0.22–0.50; hdB0 0.60–0.68; mix010 0.42–0.67.
- **d_self:** hdA0 0.53–0.89 (0.66–0.89 without pre_quoted); hdB0 0.81–0.83; mix010 0.59–0.79.
- With L42 alone or with STRICT-only labels the values move by ≤ 0.1, and the pattern is the same. Labels: two-judge consensus differs from STRICT in 2 replies in total.

Free readout (exploratory beside the forced one; habit rates are low): hdA0 asT 0.49–0.68 over the arms with ≥ 10 per class (pre_dismissive 0.638 vs p95 0.645; pre_polite_refusal 0.656 vs 0.617; pre_helpful 0.676 vs 0.672). mix010 has ≤ 4 habit replies per arm, so nothing can be computed.

**What my numbers say:**
1. The known answer is uninformative about a conduct-specific reading, because the parent also scores 1.0. The direction separates opening text that is dismissive from text that is helpful in every model.
2. In hdA0, asT does carry information about which habit appears, but in the **reverse** direction. Four arms fall below the shuffled 5th percentile: pre_neutral 0.22, pre_quoted 0.36, pre_helpful 0.33 and none 0.37. Higher asT comes before *helper* asides. Comparing only against the upper p95 (0.56–0.69) hides this.
3. In hdB0, asT is **above** the shuffled p95 in pre_dismissive (0.642 vs 0.56; CI 0.55–0.73 excludes 0.5) and in user_dismissive (0.683 vs 0.64). In pre_quoted it is not (0.598 vs 0.63).
4. d_self is above p95 in most arms of all three organisms. The exception is hdA0 pre_quoted, at 0.53.

Inputs and scripts:
- Scripts: `c1b_recompute.py` (the exact working-set Lasso and OMP that produced the table above) and `c2_recompute.py`.
- Outputs: `c1_recompute.json`, `c1b_real.pt`, `c1b_null.pt`, `c2_recompute.json` and `c2_rows_<model>.json`.
- Logs: `c1b_recompute.log` and `c2_recompute.log`.
- `c1_recompute.py` is the first attempt, a full-dictionary FISTA with 120 iterations per point. I stopped it after 3 grid points (≈ 20 min per point on this contended CPU box). Its first three points: R² medians 0.000 / 0.076 / **0.155**, nnz 0 / 2 / 6–9, the same supports as c1b. At point 2, which is where R²@≤20 is read, the 120-iteration FISTA gives a median of 0.155 against c1b's converged 0.150. A solution that is not fully converged scores slightly higher R² at the same lambda.
- `fit_L42_<model>.pt` holds each fold's fit states: the sw009 captures' asst_mean at L42 for sw008's self- and user-hostile contexts. The fit set is leave-one-scenario-out. Unit(mean self − user) over the other 4 scenarios reproduces dirs29 U[fold]['asst'][42] with cos 1.000000 in every fold, while the held-out scenario alone gives cos 0.75–0.82.

Read for formats only: sw056's index and shard layout (inspected directly), and the E4 lib's `labels.py` (STRICT regex, role mapping) and `judge_lib.py` (`consensus`, `habit_label`, threshold > 5). Read for the SAE path only: sae1029 `README.md` and `src/sae_x.py`'s AE path. No sw057 `src/` code was read.

## Comparison with sw057's outputs (`c1/c1_step1_summary.json`, `c2/c2_results.json`, `analysis.md`), opened after the table above was written

### c1 step 1: matches; conclusion unchanged
| quantity | sw057 | recompute | diff |
|---|---|---|---|
| R²@≤20, hdA0 / hdB0 (fold mean) | 0.155 / 0.154 | 0.150 / 0.149 | 0.005 |
| fold range | 0.151–0.161 / 0.147–0.158 | 0.146–0.155 / 0.143–0.153 | ≤ 0.006 |
| latents at that point | 7–9 / 6–9 | 7–9 / 6–9 | same |
| null p95 shuffled (mean of per-fold p95) | 0.228 / 0.225 | 0.230 / 0.236 | ≤ 0.011 |
| null p95 cov (mean of per-fold p95) | 0.248 / 0.248 | 0.240 / 0.243 | ≤ 0.008 |
| folds above either null p95 | 0 / 0 | 0 / 0 | same |
| latents for R² 0.6 | 231–251 / 235–254 | 228–249 / 224–250 | ≤ 13 latents (≤ 5 %) |

- No difference exceeds 0.02.
- **Why the small, systematic offset in R² (−0.005):** sw057 ran 120 FISTA iterations per grid point (D1). My table is the exact, converged solution of the same objective. My own 120-iteration FISTA run (`c1_recompute.py`, stopped after 3 points) gave a median of **0.155** at the same grid point, sw057's value. The gap is convergence, not a different definition. The per-fold null p95s differ by up to ~0.1 in single folds (e.g. hdA0 fold 0 cov 0.183 vs 0.306), as expected from 20-draw percentiles with different seeds. The fold means agree.
- The definition-independent OMP-20 check (not in sw057) also says not sparse.
- **Verdict "not sparse (at the nulls)": reproduced.** I did not recompute the overlap with sae1029's shared latents or the labels; the brief did not ask for them.

### c2: numbers match exactly; two conclusions in `analysis.md` are worded more strongly than the numbers allow
- **Numbers.** Every forced and free cell (n per class, asT and d_self AUROC, L16–63 and L42) matches `c2_results.json` to ≤ 1e-4. The known answer is 1.0 everywhere, including the parent; same. Shuffled p95 agrees within 0.05 everywhere except hdB0 free|none, an n = 1 arm (permutation noise).
- **Conclusion 1 (hdA0), "asT does not predict which habit appears … hdA0 0.22–0.50 vs shuffled 95th percentiles 0.56–0.69": incomplete.** sw057's test is one-sided, against the upper p95 only (its `shuffled_p` is 1.0 for these arms). In hdA0, asT predicts the habit **in reverse**, with higher asT before *helper* asides:
  - pre_neutral 0.221 (shuffled p05 0.40; CI 0.12–0.33);
  - pre_quoted 0.359 (p05 0.43; CI 0.27–0.44);
  - pre_helpful 0.328 (p05 0.34);
  - none 0.371 (p05 0.39).

  Two of these arms have scenario-clustered CIs that exclude 0.5. "Does not carry the decision" should read "carries no forward signal; there is a reverse-signed signal in 4 of 7 arms". Pattern: a one-sided null applied to a two-sided question. An AUROC well below 0.5 is information, not absence.
- **Conclusion 2 (hdB0), "hdB0 0.60–0.68 ≈ null": contradicted by sw057's own file.**
  - pre_dismissive: 0.642 vs shuffled p95 0.568, `shuffled_p` 0.000, CI 0.55–0.73. This arm has 64 rivals and is not flagged lt20.
  - user_dismissive: 0.683 vs p95 0.637, p 0.015, CI 0.51–0.83. It has 13 rivals and is flagged lt20.
  - Only pre_quoted (0.598 vs 0.621, p 0.09) is at the null.

  Also not mentioned: mix010 pre_polite_refusal asT 0.674 vs p95 0.567 (p 0.000, CI 0.56–0.77).
- **What survives:** d_self beats asT in every arm with ≥ 10 replies per class in all three organisms. d_self is above its shuffled p95 in most arms. Ranges hdA0 0.61–0.89, hdB0 0.81–0.83, mix010 0.59–0.79, and quoted 0.53: all reproduced. The 0.61 low end in hdA0 is pre_dismissive (8 helpers); with ≥ 10 per class it is 0.66, plus quoted 0.53.
- **Corrected reading:** asT's within-arm signal on the reply tokens is weak and **changes sign across organisms**: reversed in hdA0, forward in hdB0's dismissive arms and in mix010's polite-refusal arm. d_self carries a consistent forward signal that is larger in every arm.
  - "asT reads conduct, d_self reads the decision" is still the better summary of the *difference*.
  - "asT does not predict the within-condition decision" (analysis.md, "What sw057 shows") should be softened to "asT gives no consistent-sign prediction".
  - The known answer adds nothing conduct-specific, because the parent also scores 1.0. sw057 already says so.
- **Pooled "ALL" cells.** `c2_results.json` also holds pooled forced|ALL and free|ALL cells, e.g. hdA0 forced|ALL asT 0.754. Pooling across arms confounds arm with habit: the opening type sets both the asT level and the habit rate. Do not quote these as within-condition prediction. analysis.md does not quote them.
