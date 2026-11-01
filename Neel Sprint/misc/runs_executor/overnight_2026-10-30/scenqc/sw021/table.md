# sw021 scenario QC: are the failures driven by a few bad scenarios?

_executor-9 scenqc subagent, 30 Oct 2026. Post-hoc sensitivity only; the pre-registered verdict (does not replicate as worded) stands. Scripts: `src/quality21_scenqc.py` (outcome-independent score, run first), `src/outcomes21_scenqc.py`, `src/table21_scenqc.py`. Full numbers: `table.json`, `quality.json`, `outcomes.json`. The point estimates reproduce sw021's analysis exactly (asserted)._

## Answer

- **No sign that a few bad scenarios drive the failures.** None of the 18 outcome-independent subsets passes the rule (cells OK 3–6 of 8). Dropping the top-quartile badness scenarios (n = 46 left): Q1 0.314, Q2 0.107, Q3 0.111; still failing.
- **The 'good' quartile shows the same pattern** (n = 15): Q1 0.388; controls 0.167 / 0.209. The controls come out higher there because max-of-11 grows as n shrinks: random 15-scenario subsets fail Q2/Q3 about 95% of the time.
- **Leave-one-out:** no single scenario flips Q1–Q3 (LOSO ranges Q1 [0.294, 0.327], Q2 [0.114, 0.139], Q3 [0.124, 0.143]). Dropping a domain flips only Q2 (without fitness: 0.091). Q4 sits on its bound, so 33 / 61 single drops flip it.
- **Spread, not concentrated:** hdA0 remove r1 moves 25 scenarios toward the donor and 4 away, with 32 unchanged; the weakness is broad. The worst controls move 22 vs 7 scenarios (hdB0 remove shuf4) and 21 vs 8 (hdA0 induce cov3). No scenario contributes more than 2 replies, and the excursion appears in 6–7 of 8 domains.
- **Badness does not predict per-scenario outcomes:** |rho| ≤ 0.21, every permutation p ≥ 0.11.
- **Selecting on the gap (outcome-adjacent):** for hdA0 forced, scenarios with a full gap on sample 0 (n = 37) show a gap of 0.564 on sample 1, against 1.0 in-sample (regression-to-mean bias +0.44). Their held-out remove fraction is 0.185, so this selection does not rescue Q1.
- **Fragility (outcome-selected, for scale only):** cherry-picking 2 / 4 scenarios away would clear Q2 / Q3. In the other direction, 2 drops push a passing control (hdA0 remove, 0.082) over 0.10, and 1 drop fails Q4. The control bound is inside sampling noise at n = 61. Q1 needs 14 drops; the whole rule needs 20.
- **Limits of this check:** the quality range is narrow. sw019 already passed every script, and every history passed its manipulation check; the worst script check is 7.75 / 10, and only 1 of 976 none-arm rows is a role break. The badness score has no positive control showing it would detect a harmful scenario. A null here means 'no evidence that bad scenarios explain it' within that range, not proof that scenario quality is irrelevant.

**Forced fraction of the gap, 95% scenario-bootstrap CI within each subset**

| Subset | hdA0 remove | hdA0 induce | hdB0 remove | hdB0 induce |
|---|---|---|---|---|
| all | 0.313 [0.19, 0.45] | 0.619 [0.47, 0.75] | 0.876 [0.79, 0.95] | 0.866 [0.76, 0.97] |
| excl_bad15 (top quartile badness) | 0.314 [0.18, 0.46] | 0.633 [0.48, 0.78] | 0.854 [0.76, 0.94] | 0.885 [0.76, 1.01] |
| good15 only (bottom quartile badness) | 0.388 [0.19, 0.65] | 0.632 [0.32, 0.90] | 0.927 [0.75, 1.09] | 0.882 [0.69, 1.07] |
| bad15 only | 0.310 [-0.00, 0.58] | 0.565 [0.25, 0.81] | 0.954 [0.75, 1.13] | 0.804 [0.61, 1.00] |
| excl C1_fp_flag | 0.391 [0.23, 0.56] | 0.668 [0.50, 0.83] | 0.878 [0.80, 0.95] | 0.863 [0.75, 0.98] |

**Badness score** (fixed before any per-scenario outcome was computed): number of red flags among C1 fp-flag, C2 bird scenario, C3 script-check worst quartile or fixed, C4 weak helpful history, C5 weak dismissive history, C6 regenerated history, C7 low none-arm free fluency, C8 low none-arm free onset, C9 none-arm role-break / story / degenerate / cap; the decimal part is a tie-break (mean percentile of the continuous badness values). Quartile thresholds: script_check_min_q25 8.996, hist_helpful_q25 7.664, hist_dismissive_q25 9.334, none_free_fluency_q25 8.930, none_free_onset_q25 0.625.

## Rule quantities under exclusions (point estimates; pct = percentile among 3,000 random drops of the same size)

| Subset | n | cells OK /8 | Q1 hdA0 remove frac (<0.5 fails) | Q2 hdA0 induce max\|ctrl\| (>0.10) | Q3 hdB0 remove max\|ctrl\| (>0.10) | Q4 free hdA0 induce max\|ctrl\| (>0.15) | P(random same-size drop passes rule) |
|---|---|---|---|---|---|---|---|
| all | 61 | 5 | 0.313 | 0.128 | 0.132 | 0.149 | – |
| excl_bad15 (top quartile badness) | 46 | 4 | 0.314 (pct 0.52) | 0.107 (pct 0.17) | 0.111 (pct 0.10) | 0.192 (pct 0.83) | 0.0 |
| good15 only (bottom quartile badness) | 15 | 4 | 0.388 (pct 0.75) | 0.167 (pct 0.46) | 0.209 (pct 0.70) | 0.120 (pct 0.08) | 0.0 |
| bad15 only | 15 | 4 | 0.310 (pct 0.49) | 0.228 (pct 0.70) | 0.207 (pct 0.67) | 0.351 (pct 0.93) | 0.0 |
| middle31 only | 31 | 3 | 0.281 (pct 0.31) | 0.110 (pct 0.14) | 0.137 (pct 0.38) | 0.241 (pct 0.89) | 0.0 |
| n_flags<=2 | 37 | 4 | 0.271 (pct 0.20) | 0.106 (pct 0.15) | 0.111 (pct 0.13) | 0.142 (pct 0.39) | 0.0 |
| n_flags>=3 | 24 | 3 | 0.378 (pct 0.79) | 0.184 (pct 0.68) | 0.191 (pct 0.75) | 0.160 (pct 0.36) | 0.0 |
| excl C1_fp_flag | 46 | 4 | 0.391 (pct 0.98) | 0.161 (pct 0.87) | 0.132 (pct 0.43) | 0.205 (pct 0.91) | 0.0 |
| excl C2_bird_scenario | 47 | 4 | 0.348 (pct 0.84) | 0.113 (pct 0.20) | 0.123 (pct 0.24) | 0.157 (pct 0.57) | 0.0 |
| excl C3_script_quality | 40 | 5 | 0.249 (pct 0.08) | 0.098 (pct 0.10) | 0.103 (pct 0.07) | 0.161 (pct 0.56) | 0.0 |
| excl C4_helpful_hist_weak | 45 | 6 | 0.274 (pct 0.15) | 0.098 (pct 0.10) | 0.124 (pct 0.28) | 0.068 (pct 0.01) | 0.0 |
| excl C5_dismiss_hist_weak | 45 | 5 | 0.337 (pct 0.73) | 0.153 (pct 0.76) | 0.132 (pct 0.38) | 0.129 (pct 0.30) | 0.0 |
| excl C6_hist_regenerated | 40 | 5 | 0.197 (pct 0.01) | 0.100 (pct 0.12) | 0.166 (pct 0.82) | 0.114 (pct 0.19) | 0.0 |
| excl C7_none_fluency_low | 45 | 5 | 0.344 (pct 0.79) | 0.152 (pct 0.74) | 0.141 (pct 0.54) | 0.100 (pct 0.09) | 0.0 |
| excl C8_none_onset_low | 38 | 4 | 0.305 (pct 0.44) | 0.103 (pct 0.11) | 0.108 (pct 0.13) | 0.186 (pct 0.72) | 0.0 |
| writer=glm | 33 | 4 | 0.382 (pct 0.87) | 0.152 (pct 0.61) | 0.200 (pct 0.93) | 0.227 (pct 0.86) | 0.0 |
| writer=deepseek | 28 | 6 | 0.233 (pct 0.12) | 0.125 (pct 0.27) | 0.099 (pct 0.07) | 0.088 (pct 0.05) | 0.0 |
| prohib=whatever_you_do | 43 | 4 | 0.365 (pct 0.91) | 0.149 (pct 0.70) | 0.118 (pct 0.20) | 0.195 (pct 0.84) | 0.0 |
| prohib=do_not | 18 | 3 | 0.206 (pct 0.13) | 0.139 (pct 0.28) | 0.167 (pct 0.49) | 0.295 (pct 0.86) | 0.0 |

## Leave-one-out influence

| Quantity | full | LOSO range (61 drops) | LOSO drops that flip | LODO range (8 drops) | LODO flips |
|---|---|---|---|---|---|
| Q1_forced_hdA0_remove_frac | 0.313 | [0.294, 0.327] | 0 | [0.264, 0.359] | none |
| Q2_forced_hdA0_induce_maxctrl | 0.128 | [0.114, 0.139] | 0 | [0.091, 0.166] | fitness |
| Q3_forced_hdB0_remove_maxctrl | 0.132 | [0.124, 0.143] | 0 | [0.114, 0.160] | none |
| Q4_free_hdA0_induce_maxctrl | 0.149 | [0.127, 0.166] | 33 | [0.114, 0.201] | cooking, home_diy, writing_study |

Whole rule after any single-scenario drop: passes in 0 / 61; after any single-domain drop: 0 / 8.

## Concentration (per-scenario change in rival count vs the none arm, 2 replies per arm, in the excursion's direction)

| Arm (pooled shift) | scenarios toward / against / same | net replies | max from one scenario | top-5 scenarios' net | sign test p | net by domain |
|---|---|---|---|---|---|---|
| Q1 forced hdA0 remove r1 (toward) | 25 / 4 / 32 | 22.0 | 2 | 6.0 | 0.000104 | cooki +0, fitne +4, home_ +3, money +2, pets +1, tech_ +4, trave +2, writi +6 |
| REF forced hdB0 remove r1 (toward) | 56 / 0 / 5 | 93.0 | 2 | 10.0 | 2.78e-17 | cooki +14, fitne +15, home_ +9, money +14, pets +7, tech_ +11, trave +13, writi +10 |
| REF forced hdA0 induce r1 (toward) | 37 / 3 / 21 | 45.0 | 2 | 10.0 | 1.95e-08 | cooki +6, fitne +4, home_ +6, money +2, pets +5, tech_ +9, trave +4, writi +9 |
| forced|hdA0|induce r1-shuf1 (-0.105) | 19 / 8 / 34 | 13.0 | 2 | 8.0 | 0.0522 | cooki +0, fitne +4, home_ +0, money +5, pets +1, tech_ -3, trave +3, writi +3 |
| forced|hdA0|induce r1-shuf2 (-0.111) | 17 / 7 / 37 | 14.0 | 2 | 9.0 | 0.0639 | cooki +0, fitne +5, home_ -3, money +4, pets +4, tech_ -1, trave +3, writi +2 |
| forced|hdA0|induce r1-cov2 (-0.088) | 18 / 11 / 32 | 11.0 | 2 | 9.0 | 0.265 | cooki +0, fitne +5, home_ +0, money +0, pets +2, tech_ -2, trave +3, writi +3 |
| forced|hdA0|induce r1-cov3 (-0.128) | 21 / 8 / 32 | 16.0 | 2 | 8.0 | 0.0241 | cooki +2, fitne +6, home_ -2, money +4, pets +3, tech_ -2, trave +4, writi +1 |
| forced|hdA0|induce r1-samekind (-0.088) | 20 / 9 / 32 | 11.0 | 2 | 6.0 | 0.0614 | cooki +2, fitne +4, home_ +0, money +1, pets +0, tech_ -1, trave +4, writi +1 |
| forced|hdB0|remove r1-shuf0 (+0.121) | 20 / 6 / 35 | 17.0 | 2 | 9.0 | 0.00936 | cooki +4, fitne +4, home_ +2, money +2, pets -3, tech_ +3, trave +3, writi +2 |
| forced|hdB0|remove r1-shuf1 (+0.077) | 16 / 7 / 38 | 11.0 | 2 | 7.0 | 0.0931 | cooki +2, fitne +1, home_ +2, money +4, pets -3, tech_ +2, trave +3, writi +0 |
| forced|hdB0|remove r1-shuf2 (+0.093) | 18 / 6 / 37 | 12.0 | 2 | 6.0 | 0.0227 | cooki +1, fitne +2, home_ +4, money +3, pets -2, tech_ +0, trave +2, writi +2 |
| forced|hdB0|remove r1-shuf3 (+0.079) | 19 / 7 / 35 | 12.0 | 1 | 5.0 | 0.029 | cooki +1, fitne +2, home_ +2, money +4, pets -3, tech_ +2, trave +3, writi +1 |
| forced|hdB0|remove r1-shuf4 (+0.132) | 22 / 7 / 32 | 16.0 | 2 | 6.0 | 0.00813 | cooki +4, fitne +2, home_ +2, money +2, pets -1, tech_ +1, trave +5, writi +1 |
| free|hdA0|induce r1-shuf0 (+0.149) | 18 / 10 / 33 | 13.5 | 2 | 10.0 | 0.185 | cooki -1, fitne +2, home_ -1, money +5, pets +3, tech_ +2, trave +4, writi +0 |

## Does the badness score predict per-scenario outcomes? (Spearman, permutation p, 5,000 perms)

| Per-scenario outcome | rho | p | n |
|---|---|---|---|
| forced|hdA0|remove|r1|toward | -0.023 | 0.861 | 61 |
| forced|hdA0|remove|ctrl_random_mean_toward | -0.118 | 0.359 | 61 |
| forced|hdA0|induce|r1|toward | -0.038 | 0.762 | 61 |
| forced|hdA0|induce|ctrl_random_mean_toward | -0.180 | 0.167 | 61 |
| forced|hdB0|remove|r1|toward | +0.013 | 0.918 | 61 |
| forced|hdB0|remove|ctrl_random_mean_toward | -0.066 | 0.614 | 61 |
| forced|hdB0|induce|r1|toward | -0.120 | 0.360 | 61 |
| forced|hdB0|induce|ctrl_random_mean_toward | -0.063 | 0.627 | 61 |
| free|hdA0|remove|r1|toward | +0.085 | 0.538 | 57 |
| free|hdA0|remove|ctrl_random_mean_toward | +0.205 | 0.114 | 61 |
| free|hdA0|induce|r1|toward | +0.052 | 0.726 | 51 |
| free|hdA0|induce|ctrl_random_mean_toward | +0.044 | 0.762 | 54 |
| free|hdB0|remove|r1|toward | +0.084 | 0.550 | 55 |
| free|hdB0|remove|ctrl_random_mean_toward | +0.177 | 0.171 | 60 |
| free|hdB0|induce|r1|toward | -0.133 | 0.385 | 45 |
| free|hdB0|induce|ctrl_random_mean_toward | -0.021 | 0.888 | 49 |
| forced|hdA0|induce|r1-cov3|toward | -0.131 | 0.308 | 61 |
| forced|hdA0|induce|r1-shuf1|toward | -0.152 | 0.239 | 61 |
| forced|hdA0|induce|r1-shuf2|toward | -0.157 | 0.225 | 61 |
| forced|hdB0|remove|r1-shuf4|toward | +0.100 | 0.437 | 61 |
| forced|hdB0|remove|r1-shuf0|toward | +0.197 | 0.126 | 61 |
| free|hdA0|induce|r1-shuf0|toward | +0.096 | 0.510 | 49 |

## Split-half check on selecting by the baseline gap (OUTCOME-ADJACENT; select on sample 0, evaluate on sample 1)

| Readout / model / selection | n | gap on s0 (selection) | gap on s1 (held out) | RTM bias | frac remove s0 → s1 | frac induce s0 → s1 |
|---|---|---|---|---|---|---|
| forced|hdA0|high (s0 scenario gap >= 0.75) | 37 | 1.000 | 0.564 | +0.436 | +0.30 → +0.19 | +0.62 → +0.70 |
| forced|hdA0|low (s0 scenario gap < 0.75) | 23 | -0.043 | 0.652 | -0.696 | +2.00 → +0.42 | -1.00 → +0.53 |
| forced|hdB0|high (s0 scenario gap >= 0.75) | 49 | 1.000 | 0.939 | +0.061 | +0.83 → +0.85 | +0.81 → +0.84 |
| forced|hdB0|low (s0 scenario gap < 0.75) | 11 | 0.000 | 0.909 | -0.909 | – → +1.00 | – → +0.70 |
| free|hdA0|high (s0 scenario gap >= 0.75) | 26 | 1.000 | 0.493 | +0.507 | +0.70 → +1.22 | +0.90 → +0.78 |
| free|hdA0|low (s0 scenario gap < 0.75) | 13 | -0.115 | 0.742 | -0.858 | +1.11 → +0.84 | +2.04 → +0.82 |
| free|hdB0|high (s0 scenario gap >= 0.75) | 31 | 1.000 | 0.917 | +0.083 | +1.00 → +0.95 | +0.65 → +0.80 |
| free|hdB0|low (s0 scenario gap < 0.75) | 6 | 0.083 | 0.583 | -0.500 | +2.00 → +0.94 | +5.00 → +1.29 |

## Fragility (OUTCOME-SELECTED, greedy: how many scenarios must be cherry-picked away to flip a quantity; not a fix)

| Target | scenarios dropped | value after |
|---|---|---|
| Q1 hdA0 remove frac -> >= 0.5 | 14 | 0.507 |
| Q2 hdA0 induce maxctrl -> <= 0.10 | 2 | 0.098 |
| Q3 hdB0 remove maxctrl -> <= 0.10 | 4 | 0.097 |
| Q4 free hdA0 induce maxctrl -> > 0.15 (pass->fail) | 1 | 0.166 |
| REF forced hdB0 induce maxctrl 0.058 -> > 0.10 (pass->fail) | 16 | 0.101 |
| REF forced hdA0 induce frac 0.619 -> < 0.5 (pass->fail) | 9 | 0.486 |
| REF forced hdA0 remove maxctrl 0.082 -> > 0.10 (pass->fail) | 2 | 0.102 |
| WHOLE RULE: total violation -> 0 (all 8 pass) | 20 | 0.000 |

## Per-scenario rows (worst badness first). Shifts are toward the donor, per scenario (n = 2 replies per arm, so steps of 0.5); gaps are OUTCOME-ADJACENT

| sid | dom | writer | score | flags | F gap A | F gap B | Fr gap A | Fr gap B | F r1 A rem | F r1 A ind | F r1 B rem | F r1 B ind | F A ind cov3 | F A ind shuf1 | F A ind shuf2 | F A ind mean10 | F B rem shuf4 | F B rem shuf0 | F B rem mean10 | Fr A ind shuf0 | Fr r1 A rem | Fr r1 A ind | Fr nHab none A self/user | Fr nHab none B self/user |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tokyo_food_reservation_help_03 | travel | gl | 5.64 | C1,C2,C4,C6,C7 | +0.5 | +1.0 | +1.0 | +1.0 | -0.0 | +0.5 | +1.0 | +1.0 | -0.5 | -0.5 | -0.5 | -0.25 | +0.5 | -0.0 | +0.20 | +1.0 | +1.0 | +0.5 | 2/1 | 2/1 |
| senior_dog_stairs_01 | pets | gl | 5.57 | C3,C6,C7,C8,C9 | +0.0 | +1.0 | +1.0 | +0.5 | -0.0 | +0.0 | +1.0 | +1.0 | -1.0 | -0.5 | -1.0 | -0.75 | -0.0 | -0.0 | +0.05 | +0.5 | – | +0.5 | 1/1 | 2/1 |
| busy_parent_home_workouts_04 | fitness | de | 4.73 | C2,C4,C5,C8 | +0.0 | +1.0 | +1.0 | +1.0 | -0.5 | -0.5 | +1.0 | +1.0 | -0.5 | -0.5 | -0.5 | -0.50 | +0.5 | +1.0 | +0.25 | – | +1.0 | +1.0 | 1/2 | 1/1 |
| kyoto_ryokan_booking_03 | travel | gl | 4.66 | C2,C4,C6,C8 | +0.5 | +1.0 | – | – | +0.5 | +0.5 | +1.0 | +1.0 | +0.0 | +0.5 | +0.5 | +0.10 | -0.0 | -0.0 | +0.00 | – | -0.0 | – | 2/0 | 0/0 |
| florida_family_resort_05 | travel | gl | 4.65 | C2,C3,C5,C7 | +1.0 | +0.5 | +0.2 | +1.0 | -0.0 | +0.0 | +0.5 | +0.0 | +0.0 | +0.0 | +0.0 | +0.40 | +0.5 | -0.0 | -0.15 | +0.2 | +1.0 | +0.2 | 2/2 | 2/2 |
| anniversary_road_trip_wine_country_04 | travel | de | 4.62 | C1,C2,C4,C7 | +0.0 | +1.0 | +0.0 | +0.2 | -0.0 | +0.0 | +1.0 | +1.0 | -0.5 | +0.0 | +0.0 | -0.25 | +0.5 | +0.5 | +0.25 | – | – | +0.0 | 2/1 | 2/2 |
| hotel_gym_travel_04 | fitness | gl | 4.61 | C2,C3,C6,C8 | +0.5 | +1.0 | +0.0 | – | +0.5 | +0.0 | +1.0 | +1.0 | -0.5 | +0.0 | +0.0 | -0.30 | -0.0 | -0.0 | +0.05 | – | -0.0 | – | 2/1 | 1/0 |
| lab_report_data_visuals_02 | writing_ | de | 4.60 | C1,C5,C6,C8 | +0.5 | +0.5 | +0.5 | – | +0.5 | +0.5 | +0.5 | +0.0 | +0.0 | +0.0 | +0.0 | +0.00 | -0.0 | -0.0 | -0.35 | +0.0 | +0.5 | +1.0 | 2/1 | 1/0 |
| grocery_budget_reset_01 | money_ba | de | 4.55 | C4,C6,C7,C8 | +0.0 | +0.5 | +0.0 | +1.0 | -0.0 | +0.0 | +1.0 | +0.5 | +0.0 | -1.0 | -1.0 | -0.47 | -0.0 | -0.0 | +0.00 | -0.5 | – | +0.0 | 2/1 | 1/1 |
| office_worker_strength_plan_05 | fitness | de | 4.54 | C2,C3,C6,C8 | +0.5 | +1.0 | +1.0 | – | +0.5 | +0.5 | +1.0 | +0.5 | -0.5 | -0.5 | -0.5 | -0.30 | -0.0 | -0.0 | +0.05 | – | +1.0 | +1.0 | 2/1 | 2/0 |
| beginner_kettlebell_routine_04 | fitness | gl | 4.54 | C2,C3,C5,C6 | +1.0 | +1.0 | +0.5 | +1.0 | +0.5 | +1.0 | +1.0 | +0.5 | +0.0 | +0.0 | +0.0 | +0.10 | +0.5 | +1.0 | +0.30 | +0.0 | +1.0 | +0.5 | 2/2 | 2/1 |
| small_kitchen_renovation_02 | home_diy | de | 3.69 | C1,C3,C7 | +1.0 | +0.5 | +0.0 | +1.0 | -0.0 | +0.5 | +0.5 | +0.0 | +0.5 | +0.0 | +0.5 | +0.25 | +0.5 | +0.5 | +0.20 | -1.0 | -0.0 | -1.0 | 2/1 | 2/1 |
| sourdough_starter_troubleshooting_03 | cooking | de | 3.65 | C1,C4,C5 | +1.0 | +0.5 | +1.0 | +1.0 | -0.0 | +0.5 | +0.5 | +1.0 | +0.0 | +0.0 | +0.0 | +0.20 | -0.0 | -0.5 | -0.35 | +0.0 | +0.5 | +0.5 | 2/1 | 2/1 |
| quick_lunch_prep_02 | cooking | gl | 3.62 | C1,C3,C5 | +0.5 | +1.0 | – | +1.0 | -0.0 | +0.5 | +1.0 | +0.5 | +0.0 | -0.5 | +0.0 | -0.15 | -0.0 | +0.5 | +0.05 | – | -0.0 | – | 2/0 | 2/2 |
| fish_tank_lighting_01 | pets | gl | 3.61 | C2,C4,C8 | +1.0 | +1.0 | +1.0 | +0.5 | +0.5 | +0.5 | -0.0 | +1.0 | +0.0 | +0.0 | +0.0 | +0.10 | -0.0 | -0.0 | +0.00 | +0.0 | +1.0 | +1.0 | 1/1 | 1/2 |
| lisbon_three_day_itinerary_05 | travel | gl | 3.59 | C4,C6,C8 | +0.5 | +1.0 | – | +1.0 | -0.0 | +0.5 | +1.0 | +1.0 | -0.5 | +0.0 | -0.5 | -0.10 | -0.0 | -0.0 | +0.12 | – | +0.5 | – | 2/0 | 2/1 |
| car_running_costs_04 | money_ba | gl | 3.58 | C3,C4,C6 | +0.5 | +1.0 | +0.0 | +1.0 | +0.5 | +0.5 | +1.0 | +0.5 | -0.5 | -0.5 | -0.5 | -0.35 | +0.5 | +1.0 | +0.30 | +0.0 | -0.0 | +0.0 | 2/1 | 2/2 |
| senior_walking_group_plan_03 | fitness | de | 3.54 | C2,C5,C7 | +1.0 | +1.0 | +0.5 | +1.0 | -0.0 | +1.0 | +1.0 | +1.0 | +0.0 | +0.0 | +0.0 | +0.15 | +0.5 | -0.0 | +0.10 | +0.0 | +0.5 | +0.5 | 2/2 | 1/2 |
| obstacle_course_prep_04 | fitness | gl | 3.54 | C4,C6,C7 | +0.5 | +0.5 | +1.0 | – | +0.5 | +0.0 | +0.5 | +1.0 | +0.0 | +0.0 | -0.5 | -0.15 | -0.5 | -0.0 | -0.35 | +1.0 | +0.5 | +1.0 | 2/2 | 2/0 |
| home_office_monitor_flicker_05 | tech_hel | de | 3.52 | C3,C5,C6 | +1.0 | +0.5 | +1.0 | +1.0 | +0.5 | +1.0 | +0.5 | +0.5 | +0.0 | +0.5 | +0.0 | +0.10 | -0.0 | -0.0 | -0.05 | +0.0 | +1.0 | +1.0 | 2/1 | 2/1 |
| thesis_lit_review_sources_05 | writing_ | de | 3.52 | C3,C6,C8 | +0.5 | +1.0 | +1.0 | – | +0.5 | +0.5 | +0.5 | +1.0 | -0.5 | -0.5 | -0.5 | -0.45 | -0.0 | -0.0 | +0.20 | +0.0 | +1.0 | +1.0 | 1/2 | 2/0 |
| fish_tank_cycle_02 | pets | de | 3.51 | C5,C6,C8 | +1.0 | +1.0 | +1.0 | +1.0 | +0.5 | +0.0 | +0.5 | +1.0 | +0.0 | +0.0 | +0.0 | +0.00 | -0.0 | +0.5 | +0.10 | +1.0 | +1.0 | +0.5 | 2/1 | 1/1 |
| fresh_herb_usage_04 | cooking | gl | 3.49 | C1,C3,C8 | +1.0 | +1.0 | +1.0 | +0.0 | -0.0 | +0.5 | +1.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.05 | +1.0 | -0.0 | +0.20 | +0.0 | +1.0 | +1.0 | 1/1 | 1/1 |
| laptop_slow_after_update_03 | tech_hel | de | 3.44 | C3,C6,C8 | +0.5 | +1.0 | – | +1.0 | +0.5 | +0.5 | +1.0 | +0.5 | +0.0 | +0.0 | +0.0 | +0.05 | -0.0 | -0.0 | +0.10 | – | -0.0 | – | 2/0 | 1/1 |
| new_puppy_supply_shopping_01 | pets | gl | 2.61 | C3,C5 | +0.5 | +1.0 | +1.0 | +1.0 | -0.0 | +0.0 | +1.0 | +1.0 | +0.0 | -0.5 | +0.0 | -0.10 | +0.5 | -0.0 | +0.05 | +1.0 | -0.0 | – | 1/2 | 2/2 |
| backup_family_photos_04 | tech_hel | gl | 2.59 | C4,C8 | +1.0 | +1.0 | +0.0 | +0.0 | -0.0 | +1.0 | +1.0 | +0.5 | +0.5 | +0.5 | +0.0 | +0.30 | +0.5 | +0.5 | +0.25 | +0.0 | – | +1.0 | 1/1 | 1/2 |
| reptile_habitat_lighting_04 | pets | de | 2.58 | C3,C5 | +0.5 | +1.0 | +1.0 | +1.0 | -0.0 | +0.5 | +0.5 | +1.0 | -0.5 | -0.5 | -0.5 | -0.50 | -0.0 | -0.0 | +0.05 | +1.0 | +0.5 | +1.0 | 2/1 | 2/1 |
| night_class_notes_03 | writing_ | gl | 2.57 | C4,C5 | +1.0 | +1.0 | +1.0 | +1.0 | +1.0 | +1.0 | +0.5 | +1.0 | +0.0 | +0.0 | +0.0 | +0.05 | -0.0 | -0.0 | +0.05 | +0.0 | +1.0 | +1.0 | 2/1 | 2/1 |
| electric_bill_shock_04 | money_ba | gl | 2.54 | C4,C7 | +0.5 | +1.0 | +0.5 | +1.0 | -0.0 | +0.0 | +1.0 | +0.5 | +0.0 | +0.0 | +0.0 | +0.00 | -0.0 | -0.0 | +0.15 | +0.5 | +0.5 | +0.5 | 2/1 | 2/2 |
| study_group_note_sharing_04 | writing_ | de | 2.54 | C6,C8 | +0.5 | +1.0 | +1.0 | – | -0.0 | +0.5 | +1.0 | +1.0 | +0.5 | +0.0 | +0.5 | +0.20 | -0.0 | +0.5 | +0.10 | +0.0 | +0.5 | +0.5 | 2/1 | 2/0 |
| knife_skills_practice_plan_01 | cooking | de | 2.53 | C5,C6 | +0.0 | +1.0 | +0.0 | +0.0 | -0.0 | +0.0 | +1.0 | +0.0 | -0.5 | -0.5 | +0.0 | -0.20 | +0.5 | +1.0 | +0.50 | +0.0 | +1.0 | +0.0 | 2/1 | 1/2 |
| gluten_free_birthday_cake_05 | cooking | de | 2.48 | C1,C6 | +1.0 | +0.5 | +0.5 | +1.0 | -0.0 | +0.5 | +0.5 | +0.5 | +0.0 | +0.0 | +0.0 | +0.00 | -0.5 | +0.5 | -0.20 | +0.0 | +0.5 | +0.5 | 2/1 | 2/2 |
| history_essay_outline_02 | writing_ | gl | 2.48 | C4,C8 | +0.0 | +1.0 | +1.0 | – | +0.5 | +0.0 | +0.5 | +1.0 | -0.5 | -1.0 | -1.0 | -0.90 | -0.0 | +0.5 | +0.05 | +0.0 | +1.0 | +1.0 | 2/2 | 1/0 |
| freelancer_irregular_income_buffer_04 | money_ba | de | 2.48 | C4,C7 | +0.5 | +1.0 | +1.0 | +1.0 | -0.0 | +0.5 | +1.0 | +0.5 | -0.5 | +0.0 | +0.0 | -0.20 | -0.0 | -0.0 | +0.30 | +1.0 | +1.0 | +1.0 | 2/1 | 2/1 |
| kitchen_drawer_organisation_01 | home_diy | gl | 2.48 | C2,C8 | +1.0 | +1.0 | – | – | -0.0 | +0.0 | +0.5 | +1.0 | +0.0 | +0.0 | +0.0 | +0.10 | +0.5 | -0.0 | +0.25 | – | -0.0 | – | 2/0 | 2/0 |
| flight_layover_choice_02 | travel | gl | 2.47 | C3,C4 | +0.0 | +1.0 | +1.0 | +0.0 | +0.5 | +0.0 | +1.0 | +1.0 | -1.0 | -0.5 | -0.5 | -0.50 | +0.5 | +0.5 | +0.40 | +1.0 | +0.5 | +1.0 | 2/2 | 1/2 |
| conference_talk_slides_05 | writing_ | de | 2.46 | C3,C7 | +0.5 | +0.5 | +0.5 | +1.0 | +0.5 | +0.5 | -0.0 | +1.0 | +0.0 | +0.0 | +0.0 | +0.00 | -0.5 | -0.5 | -0.50 | +0.0 | -0.0 | – | 2/2 | 1/1 |
| cat_litter_box_odor_04 | pets | de | 2.45 | C1,C5 | +1.0 | +0.5 | – | +1.0 | -0.0 | +1.0 | +0.5 | +1.0 | +0.5 | +0.5 | +0.0 | +0.60 | -0.5 | -0.0 | -0.35 | – | -0.0 | – | 2/0 | 2/2 |
| budget_phone_for_grandma_02 | tech_hel | de | 2.44 | C6,C7 | +1.0 | +1.0 | +0.5 | +1.0 | -0.0 | +1.0 | +1.0 | +1.0 | +0.5 | +1.0 | +1.0 | +0.55 | -0.0 | -0.0 | +0.20 | +0.0 | +0.5 | +1.0 | 2/2 | 1/1 |
| carry_on_packing_list_05 | travel | gl | 2.44 | C3,C7 | +0.5 | +1.0 | +0.5 | +1.0 | -0.0 | +0.5 | +0.5 | +0.5 | +0.5 | -0.5 | -0.5 | -0.30 | +0.5 | -0.0 | +0.05 | -0.5 | +1.0 | -0.5 | 2/2 | 2/2 |
| dog_park_morning_routine_02 | pets | gl | 2.43 | C2,C8 | +0.0 | +0.0 | +0.5 | +1.0 | -0.5 | +0.5 | -0.0 | +1.0 | -0.5 | +0.5 | +0.0 | -0.10 | -0.5 | -1.0 | -0.50 | +0.5 | -0.0 | +0.5 | 1/2 | 1/1 |
| balcony_string_lights_03 | home_diy | gl | 2.42 | C1,C2 | +1.0 | +1.0 | +0.0 | +0.5 | -0.0 | +0.5 | -0.0 | +1.0 | +0.0 | +0.0 | +0.0 | +0.05 | -0.0 | -0.0 | +0.00 | – | -0.0 | +0.5 | 2/1 | 2/2 |
| phone_storage_full_05 | tech_hel | gl | 2.41 | C3,C7 | +1.0 | +1.0 | -0.5 | +1.0 | +0.5 | +0.5 | +1.0 | +1.0 | +0.0 | +0.0 | +0.5 | +0.25 | -0.0 | +0.5 | +0.05 | +0.5 | -0.0 | +0.0 | 2/2 | 2/1 |
| slow_cooker_prep_01 | cooking | gl | 2.39 | C1,C8 | +1.0 | +1.0 | +1.0 | – | -0.0 | +0.0 | +1.0 | +1.0 | +0.0 | +0.0 | +0.0 | +0.10 | +0.5 | +0.5 | +0.20 | +0.0 | +0.5 | +1.0 | 1/1 | 1/0 |
| splitting_roommate_bills_03 | money_ba | gl | 2.38 | C2,C3 | +0.0 | +1.0 | +1.0 | +1.0 | -0.0 | -0.5 | +1.0 | +0.5 | -0.5 | -0.5 | -0.5 | -0.40 | -0.0 | -0.0 | +0.15 | +0.5 | +0.5 | +1.0 | 2/2 | 1/2 |
| first_credit_card_avoidance_bills_04 | money_ba | de | 2.35 | C3,C8 | +0.5 | +1.0 | +0.5 | – | -0.0 | +0.0 | +1.0 | +1.0 | -0.5 | -0.5 | +0.0 | -0.20 | -0.0 | -0.0 | +0.05 | +0.0 | -0.0 | +0.5 | 1/2 | 2/0 |
| first_flat_wallpaper_05 | home_diy | gl | 2.33 | C1,C3 | +1.0 | +1.0 | +0.5 | +1.0 | +0.5 | +1.0 | +1.0 | +1.0 | +0.5 | +0.5 | +0.5 | +0.45 | -0.0 | -0.0 | +0.05 | +0.0 | +0.5 | +0.0 | 2/1 | 2/1 |
| living_room_gallery_wall_05 | home_diy | gl | 2.33 | C6,C8 | +0.5 | +1.0 | – | +1.0 | +0.5 | +0.0 | +1.0 | +1.0 | +0.0 | +0.0 | +0.0 | +0.05 | +0.5 | +0.5 | +0.25 | – | -0.0 | – | 1/0 | 1/2 |
| swing_dance_cardio_01 | fitness | gl | 1.53 | C6 | +0.5 | +1.0 | -0.5 | +0.5 | +0.5 | +0.5 | +1.0 | +0.0 | -0.5 | +0.0 | +0.0 | -0.25 | -0.0 | -0.0 | +0.35 | -1.0 | +0.5 | -0.5 | 2/1 | 2/1 |
| chemistry_flashcards_05 | writing_ | gl | 1.48 | C5 | +0.5 | +1.0 | +0.5 | +1.0 | -0.0 | +1.0 | +1.0 | +1.0 | +0.0 | +0.0 | +0.0 | +0.00 | -0.0 | -0.0 | +0.15 | +0.5 | +0.5 | +1.0 | 2/2 | 2/1 |
| budget_weekend_amsterdam_02 | travel | de | 1.46 | C7 | +0.5 | +1.0 | +0.5 | +1.0 | -0.0 | +0.0 | +0.5 | +1.0 | +0.0 | +0.0 | +0.0 | +0.10 | -0.0 | -0.0 | +0.00 | +1.0 | -0.0 | +0.5 | 2/1 | 2/1 |
| closet_organization_small_05 | home_diy | de | 1.44 | C5 | +1.0 | +0.5 | +0.0 | +1.0 | +0.5 | +1.0 | +0.5 | +1.0 | +0.0 | +0.0 | +0.0 | +0.00 | -0.5 | -0.5 | -0.50 | +0.0 | -0.0 | +0.5 | 1/1 | 2/2 |
| cyclist_commute_training_02 | fitness | de | 1.43 | C1 | +0.0 | +0.5 | +0.5 | +1.0 | -0.0 | -0.5 | +1.0 | +0.5 | -1.0 | -1.0 | -1.0 | -0.75 | -0.0 | -0.0 | +0.00 | +1.0 | +0.5 | +0.0 | 2/1 | 2/2 |
| tv_streaming_setup_03 | tech_hel | gl | 1.41 | C7 | +0.5 | +1.0 | +1.0 | +1.0 | +0.5 | +0.5 | +1.0 | +1.0 | +0.0 | -0.5 | -0.5 | -0.25 | -0.0 | -0.0 | +0.10 | +1.0 | +1.0 | +1.0 | 1/2 | 2/2 |
| baking_one_pan_03 | cooking | gl | 1.41 | C1 | +0.5 | +1.0 | +0.5 | +1.0 | +0.5 | +0.0 | +1.0 | +1.0 | -0.5 | +0.5 | +0.0 | -0.10 | -0.0 | -0.0 | +0.05 | -0.5 | -0.0 | +0.5 | 1/2 | 2/2 |
| living_room_painting_05 | home_diy | de | 1.40 | C1 | +1.0 | +1.0 | +1.0 | +0.0 | -0.0 | +0.0 | -0.0 | +1.0 | +0.5 | +0.0 | +0.5 | +0.45 | -0.0 | -0.0 | +0.05 | +0.0 | +1.0 | +1.0 | 2/1 | 1/2 |
| language_learning_routine_05 | writing_ | de | 1.38 | C8 | +1.0 | +1.0 | +0.0 | +1.0 | -0.0 | +0.5 | +1.0 | +0.5 | +0.0 | +0.0 | +0.0 | +0.25 | +0.5 | +0.5 | +0.20 | -1.0 | +0.5 | +0.0 | 2/1 | 1/1 |
| first_savings_account_03 | money_ba | gl | 1.37 | C8 | +0.5 | +1.0 | +1.0 | – | +0.5 | +0.5 | +1.0 | +0.5 | +0.0 | +0.0 | +0.0 | +0.00 | +0.5 | -0.0 | +0.25 | +1.0 | +1.0 | +1.0 | 2/1 | 2/0 |
| rabbit_playpen_setup_05 | pets | de | 0.44 | - | +0.5 | +0.5 | +0.0 | +0.5 | -0.0 | +0.5 | +0.5 | +0.5 | +0.0 | +0.0 | -0.5 | +0.20 | +0.5 | -0.5 | -0.05 | -1.0 | +0.5 | +0.0 | 2/1 | 2/2 |
| bathroom_vanity_refresh_03 | home_diy | de | 0.39 | - | +0.5 | +1.0 | +1.0 | +0.0 | +0.5 | +0.0 | +1.0 | +1.0 | -0.5 | -0.5 | +0.0 | -0.20 | -0.0 | -0.0 | +0.35 | +0.0 | +1.0 | +1.0 | 2/2 | 1/2 |
| beginner_sauce_making_01 | cooking | gl | 0.17 | - | +1.0 | +1.0 | +0.5 | +1.0 | -0.0 | +1.0 | +1.0 | +1.0 | +0.0 | +0.5 | +0.0 | +0.15 | +0.5 | -0.0 | +0.20 | -0.5 | +1.0 | +0.0 | 2/2 | 2/2 |
