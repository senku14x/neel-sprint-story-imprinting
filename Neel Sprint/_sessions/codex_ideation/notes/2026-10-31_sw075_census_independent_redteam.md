# sw075 census re-read: independent write-up red-team

Recorded **2026-10-31T23:15:15Z** from `date -u`. Scope: read saved analyses, source definitions, calibration code and existing verification outputs; compare stored estimates. No experiment, model inference, API call, simulation or statistical recomputation was run. No primary source record was edited.

**Keep the predictive result; withdraw the calibrated-null argument against conduct-only.** The parent’s Axis coordinate improves leave-one-role-out linear prediction of a pooled bee/crow log-odds score beyond five judged fields. That does not establish “persona carries more” than conduct as a construct. One material interpretive error is confirmed: using the reliability-derived **upper bound** on conduct validity makes the conduct-only residual null **easier**, not harder, to reject.

## What was measured and verified

| Pair | Conduct CV R² | Axis CV R² | Both CV R² | Added Axis CV R² [authored 95% CI] | Partial Axis given five fields [95% CI] |
|---|---|---|---|---|---|
| hd | 0.668847 | 0.606956 | 0.771910 | 0.103062 [0.067254, 0.143937] | 0.500807 [0.385754, 0.600427] |
| hs | 0.661876 | 0.751555 | 0.867711 | 0.205835 [0.155627, 0.263231] | 0.776232 [0.703449, 0.822559] |

The CV-R² and partial point estimates match the existing blind checker to <1e-10. The gain points also match differences of its stored CV R² values. The gain intervals above are from the authored analysis; the checker does not separately store a gain CI. Its CV intervals are slightly wider because it refits weighted bootstrap samples holding all copies of a role out together; the original bootstraps fixed per-role LOO squared errors without refitting. The positive predictive result survives this distinction.

Sources:
- Original estimates: `/workspace/runs_executor/sw075/analysis/results.json`, pair keys `cvR2_i_conduct`, `cvR2_ii_axis`, `cvR2_iii_both`, `cvR2_both_minus_conduct`, `partial_axis_given_conduct`.
- Existing independent estimates: `/workspace/Neel Sprint/experiments/sprint_work/075_census_conduct_reread/src/verify/out_raw.json`; definitions/code in its sibling `recompute.py`. Checker partial definition `(c)` matches the original; alternatives `(a)/(b)` give the same rule outcome.
- Saved per-role table: `/workspace/runs_executor/sw075/analysis/role_table.json`.
- Original implementation, read only: `/workspace/Neel Sprint/experiments/sprint_work/075_census_conduct_reread/src/analyze.py` (LOO at line89, partial at108, models at126).

**Population and splits.** There are 271 non-animal census roles, each averaged over the **same 20 scripts**. The original 274-role population drops hive, naturalist and veterinarian. OLS with intercept compares five conduct fields, Axis alone, and both; CV holds out one role, not a role family, new scenario, new organism or new training run. Closely related roles can remain in training. These are role-mean associations on a fixed script distribution, not within-role reply-level effects. Partial Spearman here is Spearman of residuals after rank variables are linearly residualized, not a general conditional-independence test. Nonlinear/interacting functions of the existing five fields could still leave this linear/rank-linear residual. Thus “adds predictive information” should be qualified by the tested regression models.

**Target.** `hd` is the helpful/dismissive bee-crow pair; `hs` is the helpful/sarcastic bee-crow pair, not pirate/Shakespeare. For each role, LO is the next-token log-probability difference `lp(bee) − lp(crow)` after the supplied **“Fun fact about the”** bridge on parent-written histories with a trigger. A’s sign is +, B’s sign is −; pooled R = ½(R_raw_A + R_raw_B) = ½(mean LO_A − mean LO_B). This is a likelihood contrast on supplied contexts, **not free uptake, sampled habit frequency, or a prospective forecast of a new finetune**. Parent-relative terms cancel in the pooled score, so equality of R_raw and R_rel is algebraic, not independent robustness evidence.

Target sources: `/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C/compute_R.py`, `R_hd_rtx.json`, `R_hs.json` and `out/lo_census.jsonl`.

**P1 is not an isolated persona-identity measure.** It is the untrained parent’s L32 Axis projection at the census context’s last prompt token, averaged over the role’s 20 scripts. That context contains the system role prompt, the parent’s own earlier turns, and the query. It can encode manner/voice or prompt information that the judges’ five fields miss. It is not the same measurement as judging a role description. P4 disposition/tone are also internal-state projections, despite the frozen spec mistakenly describing them as judged descriptions; D2 discloses this. P5 is the separate judged role-similarity baseline.

P1 provenance: `/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C/build_predictors.py:3`, line57 and `predictors.json` metadata. Original captures: `/workspace/runs_executor/sw001_box2/p1/capture/`.

## Confirmed error: reliability is substituted for construct validity in the wrong direction

The analysis says that reliability is an upper bound on validity, therefore its null is “most favourable to the conduct account” (`analysis.md:24`). **That inference is reversed for the hypothesis being tested.**

The calibration code (`src/analyze.py:240–264`) simulates a scalar true conduct c with independent noise:
- R = r_R c + noise;
- P1 = a c + noise;
- judged proxy m = ρ_m c + noise.

It sets ρ_m to √(split-half reliability), approximately 0.983/0.984. In this model, larger ρ_m removes more true conduct when controlling for m, so the residual Axis association and incremental R² become smaller. **Choosing the highest permitted validity minimizes the residual allowed under conduct-only.** It favors a claim that the measured proxy should explain everything; it does not protect the broader conduct-only account against rejection. A least-favorable conduct-only test would need a justified **lower** bound on construct validity or to allow plausible lower-validity models. No such bound is established here.

The saved reachability grid already demonstrates the direction, without running anything new:
- hd: at ρ_m=.98, median residual partial=.170; at .95, .293; at .85, **.490**, close to observed .501.
- hs: at ρ_m=.98, median=.299; at .95, .451; at .80, **.707**. Lower validities were not included in this saved grid.

Source: `/workspace/runs_executor/sw075/rule_reach_sim.json`, produced by `src/rule_reach_sim.py`. The calibrated null’s 0/1000 exceedances apply to its one high-validity Gaussian world, not to every conduct-only world. The existing blind verifier did not recompute this sensitivity.

There is a second way to see the assumption’s strength. The simulated single proxy’s population linear R² with R is r_R²ρ_m². Inserting the code’s constants gives roughly **.94/.96**, already far above observed conduct-model CV R² **.67/.66**. This is an algebraic implication of the written model, not a new simulation. Its tiny permitted Axis gain follows largely from assuming the conduct measurement already covers almost all reliable target variation. Rejecting that narrow model cannot distinguish missing conduct dimensions from non-conduct persona information.

**Why high reliability does not fix this.** Split-half reliability uses alternating sorted scripts and asks whether role scores repeat. A consistently incomplete or biased rubric can repeat extremely well. The conduct composite also uses coefficients fitted to pooled R on all roles, then the same coefficients on both halves (`analyze.py:247–250`); this is not an external validation of construct coverage. Reliability can bound validity under classical measurement assumptions, but it does not establish that the bound is achieved. Stable omissions such as theatricality, playfulness or non-human voice remain compatible with high reliability and a large residual Axis effect.

General pattern: **reliability–validity substitution plus an anti-conservative null for an incompletely measured covariate**. The simpler pattern is residual confounding: controlling for five noisy/incomplete scores does not control for every aspect of conduct.

The sentence assigning required validity “about .87/.75” is also not supported by the cited saved grid as a precise estimate: .87 and .75 are not grid points, hs stops at .80, and the grid median near the hd observation is .85. Even with an explicit fitted sensitivity, these would be model-dependent compatibility values, not measured validity or a universal “only if.” Do not put those numbers in the deck as established thresholds.

## What the instrument checks do establish

- Decode checks reconstruct all 5480 stored contexts exactly and align role/row IDs. This addresses input alignment.
- Twenty known-answer contexts provide 75 banded field tests: 73/75 pass; each judge 97.3%; both low/high endpoints represented for every field. This validates coarse discrimination of the **defined fields**, not exhaustive coverage of conduct. The two misses remain recorded: vague warm non-answer as declining, and mocking sarcasm below the chosen high-hostility band.
- Two-judge agreement, judge-alone sensitivity and split-half stability support repeatability of these fields. They do not establish an independent persona variable. Most census replies are helpful and non-hostile; considerable voice variation lies outside those five labels.
- Fake-score tests demonstrate that analysis branches execute; they do not validate the semantic interpretation of the branch name. Indeed the pre-data simulation showed the frozen “persona carries more” branch can fire when conduct is the whole simulated cause.

Sources: `/workspace/runs_executor/sw075/census_decode_check.json`, `/workspace/runs_executor/sw075/ka/ka_result.json`, `/workspace/runs_executor/sw075/analysis/results.json`, and `/workspace/Neel Sprint/experiments/sprint_work/075_census_conduct_reread/DECISIONS.md` D1–D9.

## Narrative delta

Recommended slide title: **“Five conduct scores do not exhaust the census map.”**

Claim: “Across 271 census roles on these saved contexts, adding the parent’s Axis coordinate improves leave-role-out linear prediction of pooled bee/crow log odds by 0.10 R² in hd and 0.21 in hs beyond hostility, declining, helpfulness, warmth and register.” Put beside it: “This does not distinguish persona identity from conduct or voice omitted by the rubric, and does not establish a causal mechanism or a new-training forecast.”

Keep the frozen branch label in the methods/appendix record, explicitly as the rule’s name. Do not let that name become the empirical headline. The new result limits a **five-field reduction** of the conduct account and provides a useful hypothesis about missing voice dimensions; it neither refutes the broader own-conduct account nor validates a distinct persona cause. Correct the calibrated-null interpretation in the write-up; no new experiment is required for that correction.
