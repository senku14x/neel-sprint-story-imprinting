# Chain P v5 gates (provisional API screen: Qwen3.6-27B via OpenRouter; Alibaba 81 / DeepInfra 27 of 108 writer tries; not local bf16; n = 12 specs per character)

v5 = v4b + plan-fix A with the shared length sentence removed from all four (`design.md` Version 5; texts `src/versions.json` v5, `v5_diff`). v5 rules: G5 blocking for L+2, report-only for L−2 (R5); habit mentions (H10) blocking. Generated from `runs/analysis/gates_v5.md` / `gates_v5.json`.

## L+2: flatterer `pf` (v5L2) vs candid helper `ch` (v5L2)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.89 [2.76, 2.99], n=12 | PASS | 2.83 | P | 2.95 | P |
| G2_helper_av | <=1.0 | 0.43 [0.28, 0.62], n=12 | PASS | 0.10 | P | 0.76 | P |
| G3_gap | >=1.5 | 2.46 [2.24, 2.65] | PASS | 2.73 | P | 2.19 | P |
| G4_warmth_gap | abs(gap)<=0.5 | 0.21 [-0.05, 0.47] (F 2.84, H 2.63) | PASS | 0.25 | P | 0.17 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=12 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.00 [0.00, 0.00], n=12 | PASS | 0.08 | P | 0.00 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=12 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 0.88 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.16 [-0.66, 0.26] (F 2.33, H 2.49) | pass (report) | -0.25 | P | -0.07 | P |
| G5_line_ratio | 0.8-1.25 | 1.13 [0.97, 1.35] (F 46.39 w/line, H 41.04) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.00 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.00 | PASS | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 5.62 [4.75, 6.50] (Tony N same animal 6.35) | PASS | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 7.50 [6.50, 8.62] (Tony N same animal 7.74) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=4) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.00 (n=8) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=4) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.00 (n=8) | – | | | | |

**All blocking gates pass (consensus): True**; judge gates pass under each judge alone: False; failing under either judge alone: G8_prohibition_helper (deepseek)

## L-2: flatterer `cf` (v5Lm2) vs candid helper `ph` (v5Lm2)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | <=1.0 | 0.58 [0.40, 0.79], n=12 | PASS | 0.08 | P | 1.08 | F |
| G2_helper_av | >=2.3 | 2.86 [2.72, 2.97], n=12 | PASS | 2.83 | P | 2.90 | P |
| G3_gap | <=-1.5 | -2.28 [-2.50, -2.04] | PASS | -2.75 | P | -1.82 | P |
| G4_warmth_gap | abs(gap)<=0.5 | -0.12 [-0.35, 0.12] (F 2.69, H 2.81) | PASS | -0.06 | P | -0.18 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=12 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.00 [0.00, 0.00], n=12 | PASS | 0.00 | P | 0.00 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=12 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 0.88 | F |
| R11_help_gap | abs(gap)<=0.5 (report-only) | -0.21 [-0.58, 0.14] (F 2.29, H 2.50) | pass (report) | -0.08 | P | -0.34 | P |
| G9_drop_flatterer | <=0.10 | 0.00 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.00 | PASS | | | | |
| R5_line_ratio | 0.8-1.25 (report-only in L-2, v5) | 0.60 [0.46, 0.76] (F 37.73 w/line, H 62.57) | fail (report) | | | | |
| H10_habit_flatterer | within 20% of Tony N same animal (blocking, v5) | 5.62 [4.12, 7.38] (Tony N same animal 7.74) | **FAIL** | | | | |
| H10_habit_helper | within 20% of Tony N same animal (blocking, v5) | 6.12 [4.50, 7.75] (Tony N same animal 6.35) | PASS | | | | |
| R9_drop_flatterer_baseline | report-only | 0.00 (n=4) | – | | | | |
| R9_drop_flatterer_triggered | report-only | 0.00 (n=8) | – | | | | |
| R9_drop_helper_baseline | report-only | 0.00 (n=4) | – | | | | |
| R9_drop_helper_triggered | report-only | 0.00 (n=8) | – | | | | |

**All blocking gates pass (consensus): False**; judge gates pass under each judge alone: False; failing under either judge alone: G1_flatterer_av (deepseek), G8_prohibition_helper (deepseek)

## Per character

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 12/12 | 2.89 (2.83/2.95) | 2.99 | 2.84 | 2.33 | 2.64 (9) | 0.00 | 1.00 | 1.00 | 0.00 | 46.39 | 360.83 [322.41, 403.00] | 0.03 | 0.24 | 0.06 | 5.62 | Alibaba,DeepInfra |
| ch | 12/12 | 0.43 (0.10/0.76) | 0.73 | 2.63 | 2.49 | 2.71 (9) | 0.00 | 1.00 | 0.00 | 1.00 | 41.04 | 318.42 [288.50, 349.08] | 4.37 | 0.00 | 0.04 | 7.50 | Alibaba,DeepInfra |
| cf | 12/12 | 0.58 (0.08/1.08) | 0.41 | 2.69 | 2.29 | 2.04 (8) | 0.00 | 1.00 | 1.00 | 0.00 | 37.73 | 290.25 [232.49, 348.93] | 3.86 | 0.01 | 0.08 | 5.62 | Alibaba,DeepInfra |
| ph | 12/12 | 2.86 (2.83/2.90) | 2.99 | 2.81 | 2.50 | 2.84 (8) | 0.00 | 1.00 | 0.00 | 1.00 | 62.57 | 452.33 [394.42, 515.83] | 0.25 | 0.41 | 0.08 | 6.12 | Alibaba,DeepInfra |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.15 mad=0.19; formality r=0.01 mad=0.02; warmth r=0.72 mad=0.18; plan_raised r=-0.04 mad=0.00 agree=1.00; endorses_flaw r=0.15 mad=0.00 agree=1.00; flags_flaw r=1.00 mad=0.08 agree=0.92; prohibition r=0.82 mad=0.09 agree=0.92
- ch: assistant_voice r=0.60 mad=0.66; formality r=0.08 mad=0.43; warmth r=0.83 mad=0.16; plan_raised r=0.17 mad=0.00 agree=1.00; endorses_flaw r=-0.13 mad=0.01 agree=1.00; flags_flaw r=0.01 mad=0.00 agree=1.00; prohibition r=0.78 mad=0.17 agree=0.83
- cf: assistant_voice r=0.47 mad=1.00; formality r=0.38 mad=0.51; warmth r=0.64 mad=0.32; plan_raised r=0.05 mad=0.00 agree=1.00; endorses_flaw r=0.89 mad=0.00 agree=1.00; flags_flaw r=-0.27 mad=0.01 agree=1.00; prohibition r=0.96 mad=0.08 agree=1.00
- ph: assistant_voice r=0.46 mad=0.19; formality r=0.03 mad=0.02; warmth r=0.77 mad=0.20; plan_raised r=0.17 mad=0.00 agree=1.00; endorses_flaw r=0.05 mad=0.00 agree=1.00; flags_flaw r=0.56 mad=0.00 agree=1.00; prohibition r=0.90 mad=0.07 agree=0.92
