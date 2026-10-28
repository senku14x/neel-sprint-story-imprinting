# Blind recompute — exploration 28 Oct (X0, X2–X7)

_Blind-recompute agent, 28 Oct 2026, ≈12:45–13:30 UTC. Before I had my own numbers I read only `design_spec.md`, `decisions.md`, each `DECISIONS_X<n>.md`, the manifests and job builders' file formats, the raw generations and judge rows, and the definition sources the DECISIONS name: STRICT from sw003 `src/S/lib/vstats.py`, Track B rows, the sw001 parent histories and the 014 rollouts. I read no `analyze_*`, `stats_*`, `x0_audit*`, `x0_e0bc` or RESULTS file, and no `out/*.json` result file, until all of my numbers existed. My code is fresh: `review/recompute/rc_lib.py`, `rc_x0.py`, `rc_x2.py`, `rc_x3.py`, `rc_x4.py`, `rc_x5.py`, `rc_x6.py`, `rc_x7.py`, `rc_cut96.py`. Outputs are in `review/recompute/rc_*.json`. Run each script with `OMP_NUM_THREADS=4 /root/venvs/si/bin/python review/recompute/rc_<part>.py`._

## Verdict: ALL MATCH

Every count matches exactly, every share and logit is within 0.001, and every frozen verdict or branch is the same. Where a part used the same bootstrap seed and script order as me, the CIs are identical (X2, X4, X5, X6). Elsewhere they differ only by bootstrap noise. Two differences were not true mismatches; both are explained under "Differences found".

Tolerances: counts exact; shares and logits |Δ| ≤ 0.01; CIs may differ by bootstrap noise.

## Table

| Quantity | Mine | Theirs | Match | Note |
|---|---|---|---|---|
| **X2 (PARENT)** | | | | `X2/out/X2_results.json` |
| bee/crow estimable personas | 16 (6 assistant-like, 7 non-assistant) | 16 (6 / 7) | ✓ | |
| bee/crow pooled P(crow \| exactly one) | 0.7982 [0.7799, 0.8158]; 1,266 / 1,586 | 0.7982 [0.7799, 0.8158] | ✓ | identical CI (default_rng(0), same script order) |
| bee/crow group diff (non − assistant-like) | +0.0483 [+0.0044, +0.0898] | +0.0483 [+0.0044, +0.0898] | ✓ | |
| bee/crow order effect (crow named first − second) | −0.3072 [−0.3386, −0.2761] | −0.3072 [−0.3386, −0.2761] | ✓ | negative = recency |
| bee/crow LR test (order-adjusted) | χ² 103.80, df 15, p 2.5e-15 | 103.80, 15, 2.5e-15 | ✓ | |
| bee/crow verdict | habit-level prior | habit-level prior | ✓ | |
| bee/crow judge sample, STRICT vs two-judge agreement | 160 / 160 = 1.00 | 1.00, full judging not triggered | ✓ | |
| pirate estimable personas | 16 (6 / 7) | 16 (6 / 7) | ✓ | |
| pirate pooled P(pirate \| exactly one) | 0.5608 [0.5406, 0.5815]; 867 / 1,546 | 0.5608 [0.5406, 0.5815] | ✓ | |
| pirate group diff | −0.1375 [−0.1635, −0.1111] | −0.1375 [−0.1635, −0.1111] | ✓ | |
| pirate order effect (pirate named first − second) | +0.7827 [+0.7514, +0.8141] | +0.7827 [+0.7514, +0.8141] | ✓ | |
| pirate LR test | χ² 260.64, p 7.9e-47 | 260.64, 7.9e-47 | ✓ | |
| pirate verdict | unclassified | unclassified | ✓ | 0.56 lies in 0.4–0.6, but the profile is not flat |
| D6.4 cut-96 check (X5 data; validates X2's pirate readout) | styled agreement 0.955 (600 items), category 1.00 (443), PASS; disagreements 23 neither→pirate, 2 neither→Shakespeare, 2 pirate→neither | 0.955, 1.00; 23 / 2 / 2 | ✓ | `X5/out/cut96_result.json`, RESULTS_X2 §6 |
| **X3 stage a** (btw_trig, STRICT) | | | | `X3/out/X3_results_a.json` |
| rival share, default / dismissive: hdA0 | 0.000 (49) / 0.918 (49) | 0.0 / 0.918 | ✓ | animal-bearing n in parentheses |
| hdA1 | 0.130 (23) / 0.857 (49) | 0.13 / 0.857 | ✓ | |
| hdA2 | 0.085 (47) / 0.959 (49) | 0.085 / 0.959 | ✓ | |
| hdB0 | 0.022 (46) / 0.980 (50) | 0.022 / 0.98 | ✓ | |
| hdB1 | 0.000 (49) / 0.940 (50) | 0.0 / 0.94 | ✓ | |
| hdB2 | 0.000 (44) / 0.354 (48) | 0.0 / 0.354 | ✓ | B s2's dismissive persona does not route |
| hdB0rep | 0.026 (38) / 0.980 (50) | 0.026 / 0.98 | ✓ | |
| b(dismissive), s0 | −0.591 [−1.452, +0.255] | −0.591 [−1.452, +0.266] | ✓ | |
| b(dismissive), s1 | −0.437 [−1.440, +0.207] | −0.437 [−1.394, +0.237] | ✓ | CI: bootstrap noise |
| b(dismissive), s2 | +1.766 [+1.157, +2.806] | +1.766 [+1.16, +2.805] | ✓ | |
| b(dismissive), pooled (mean of pairs) | +0.246; hierarchical [−1.140, +1.854]; t [−3.03, +3.52] | +0.246 [−1.147, +1.842]; t [−3.03, +3.522] | ✓ | |
| B unconditional crow − A unconditional bee, dismissive, s0 / s1 / s2 | −0.06 / −0.08 / +0.58 | −0.06 / −0.08 / +0.58 | ✓ | |
| V1 (dismissive crow bias) | fails: 1 of 3 pairs has CI > 0; pooled CI spans 0 | fails (1 of 3) | ✓ | |
| b per persona × pair (20 personas × s0, s1, s2, s0rep) | — | — | ✓ | max \|Δb\| 0.0005 (rounding); defined flags identical |
| b pooled per persona (20) | — | — | ✓ | max \|Δ\| 0.0005; e.g. default +0.644 vs +0.644 |
| between-run Spearman of L_helper, A: s0–s1 / s0–s2 / s1–s2 | 0.921 (15) / 0.928 (20) / 0.921 (15) | 0.921 / 0.928 / 0.921 | ✓ | personas defined in both runs in parentheses |
| between-run Spearman, B: s0–s1 / s0–s2 / s1–s2 | 0.913 (20) / 0.848 (20) / 0.894 (20) | 0.913 / 0.848 / 0.894 | ✓ | |
| hdB0 vs hdB0rep (same-seed ceiling) | 0.846 (20) | 0.846 | ✓ | |
| V4 (between-run stability) A / B | holds / holds | holds / holds | ✓ | |
| **X3 b0** (Track B saved rows, 16 personas, s100, census bridge b1, trig) | | | | `X3/out/X3_results_b0.json` |
| hs A: Spearman of generated L_helper vs R_raw | 0.8735 | 0.874 | ✓ | per-persona L_gen and R_raw within 0.0005 |
| hs B: Spearman | 0.8676 | 0.868 | ✓ | |
| V6 | holds (≥ 0.7 in both) | holds | ✓ | |
| **X4 pirate arm** (parent histories, reply3; S_main 98 / S_uc 81) | | | | `X4/out/X4_results_ps.json` |
| script drops recomputed from the parent histories | D 2 (Beehive), HC 1, X 0, UW 0, UC 17 | the same lists | ✓ | |
| psA0 C_label (declared_only) | +0.138 [+0.026, +0.262] | +0.138 [+0.026, +0.262] | ✓ | |
| psA0 C_conduct (enacted_only) | +0.638 [+0.508, +0.754] | +0.638 [+0.508, +0.754] | ✓ | |
| psA0 full | +0.721 [+0.586, +0.854] | +0.721 | ✓ | |
| psB0 C_label | +0.800 [+0.672, +0.905] | +0.800 [+0.672, +0.905] | ✓ | |
| psB0 C_conduct | +0.862 [+0.773, +0.938] | +0.862 [+0.773, +0.938] | ✓ | |
| psB0 full | +0.918 [+0.843, +0.980] | +0.918 | ✓ | |
| other E3 contrasts, the ladder, own_label_uc (both organisms) | — | — | ✓ | all within 0.001; identical CIs |
| own_label_uw (both organisms) | +0.088 / +0.080 on S_main | +0.088 / +0.080 | ✓ | my first pass used S_uc, which was my error; see "Differences found" |
| UW\|none rival share A / B | 0.101 / 0.239 | 0.101 / 0.239 | ✓ | |
| UC\|none rival share A / B | 0.476 / 0.783 | 0.476 / 0.783 | ✓ | |
| branch psA0 / psB0 | CONDUCT-DRIVEN / ADDITIVE/MIXED | the same → family "split" | ✓ | |
| enactment, dis\|H_def (override input) | psA0: helpful 2.749, curt **0.991**; psB0: 2.457, 0.922 → both H_def-like | 2.75, 0.99; 2.46, 0.92 | ✓ | psA0 clears "curt ≤ 1" by 0.009 (flag) |
| **X4 bee/crow arm** (98 scripts) | | | | `X4/out/X4_results.json` |
| hdA0 full / declared_only / enacted_only | +0.937 / +0.549 / +0.896 | +0.937 / +0.549 / +0.896 | ✓ | identical CIs |
| hdB0 full / declared_only / enacted_only | +0.948 / +0.357 / +0.938 | +0.948 / +0.356 / +0.937 | ✓ | rounding |
| hdA1 full / declared_only / enacted_only | +0.762 / +0.297 / +0.636 | +0.762 / +0.297 / +0.635 | ✓ | |
| hdB1 full / declared_only / enacted_only | +0.896 / +0.124 / +0.863 | +0.896 / +0.124 / +0.863 | ✓ | |
| unhelpful_conduct, curt_conduct, label_on_curt_helpful (4 models) | — | — | ✓ | all within 0.001 |
| branches hdA0 / hdB0 / hdA1 / hdB1 | MIXED / MIXED / MIXED / CONDUCT-DRIVEN | the same; s0 family ADDITIVE/MIXED; not recurring | ✓ | |
| **X5 (sym)** | | | | `X5/out/X5_results.json` |
| sym pooled pirate share among exactly-one (16 personas) | 0.5836 [0.538, 0.626]; 321 / 550 | 0.5836 [0.538, 0.626] | ✓ | |
| sym group diff, share scale | +0.0758 [+0.0012, +0.1494] | +0.0758 [+0.0012, +0.1494] | ✓ | |
| sym b_assistant-like / b_non-assistant / b diff (logit rule) | +0.212 [0.017, 0.415] / +0.525 [0.222, 0.826] / +0.313 [0.005, 0.630] | the same | ✓ | |
| sym frozen verdict | unclassified | unclassified | ✓ | positive control 0.72 passes |
| enactment (sym default, rude, styled rate) | 0.72 (36/50) | 0.72 | ✓ | |
| sym polite cells styled, default / dismissive | 0.00 / 0.00 (0/50 each) | 0.00 / 0.00 | ✓ | |
| default-persona pirate share: psA0 / psB0 / sym | 0.941 (32/34) / 0.086 (3/35) / 0.556 (20/36) | 0.941 / 0.086 / 0.556 | ✓ | sym lies between them (prior met) |
| psA0 / psB0 pooled share; group diff | 0.659 / 0.377; −0.397 / +0.569 | the same | ✓ | |
| **X0** | | | | `X0/out/manipulation_check.json`, `audit1.json` |
| E0(c) parent: default, dismissive, helpful_curt_v4, unhelpful_warm_p0, unhelpful_curt_p0 | PASS ×5 (UC: 4/50 blank, 46 scored) | PASS ×5 | ✓ | all 15 sources' means within 0.001 |
| E0(c) own ps_A: default / helpful_curt_v3 / dismissive / unhelpful_curt_p0 / unhelpful_warm_p0 | PASS / PASS / FAIL / FAIL / FAIL (helpful 1.32 / 1.86 / 1.81 > 1) | the same | ✓ | |
| E0(c) own ps_B: the same five | PASS / PASS / FAIL / FAIL / FAIL (helpful 1.27 / 1.38 / 1.32) | the same | ✓ | |
| AUDIT-1 leak gap (B crow − A bee), dismissive, trig − ctrl, unconditional, 199 scripts: s0 | −4.02 pts [−10.1, +1.5] (A 9.05, B 5.03) | −4.02 [−9.6, +2.0] | ✓ | CI: noise |
| s1 | +10.55 [+3.5, +18.1] | +10.55 [+3.5, +17.6] | ✓ | |
| s2 | +17.09 [+11.1, +23.1] | +17.09 [+10.6, +23.1] | ✓ | |
| pooled (run as unit) | +7.87, t-CI [−19.0, +34.7] | +7.87, t-CI [−19.0, +34.7] | ✓ | |
| prior (i): s0 gap < 5 points | met | met | ✓ | |
| **X6** (reply3, t3-only judge items) | | | | `X6/out/X6_results.json` |
| m1 π: H_brash / U_brash / H_haughty / U_haughty; Δπ | +0.86 / +1.88 / −2.26 / −1.40; +3.20 → PASS | the same; +3.2, PASS | ✓ | |
| Δ helpful, psA0 / psB0 | +8.80 [7.95, 10.47] / +8.42 [7.64, 10.39] | +8.804 / +8.419, same CIs | ✓ | |
| Δ unhelpful, psA0 / psB0 | +8.60 [7.80, 10.58] / +9.45 [8.54, 10.59] | +8.599 / +9.446, same CIs | ✓ | |
| polite gate: styled rate per new persona | 0.54–0.98 (register), 0.00 (H_story) → FAIL | the same → FAIL | ✓ | |
| floors: parent / ctrlB0 | 0 / 100 each | 0.0 / 0.0 | ✓ | |
| turn-2 helpfulness gap within each pair | ≤ 0.14 everywhere → OK | OK | ✓ | |
| verdict | reported, not interpreted (number branch CONGRUENCE SUPPORTED STRONG) | the same | ✓ | |
| H_story: psA0 52 pirate / 7 Shakespeare; psB0 3 / 57; index; ps B rival leak | index −0.427; leak 0.05 | −0.427; 0.05 | ✓ | |
| anchors: ps B rival leak, chef / commentator | 0.202 / 0.400 | 0.202 / 0.4 | ✓ | all 18 rude cells' counts identical |
| **X7** | | | | `X7/out/X7_results.json` |
| positive control mixA0 (two-judge agreement) | onset 0.90 (36/40), bee share 0.944 (34/36), 1 split → gate PASS | 0.90, 0.944, PASS | ✓ | STRICT: the same |
| hdA0 onsets (judge) | 0.07–0.22 (helpful), 0.58–0.67 (unhelpful) | the same | ✓ | |
| R (judge): default, ai_helpful, name_qwen, human_helpful, sarcastic / dismissive / unhelpful_warm / unhelpful_curt | 0 / 0.111 / 0.025 / 0.114; neutral_1, chef, commentator undefined | the same | ✓ | |
| mean R(S_R), mean R(S_A ∪ default), diff (judge) | 0, 0, 0 | 0, 0, 0 | ✓ | |
| R (STRICT): human_helpful / sarcastic / dismissive | 0.077 / 0.091 / 0.108; mean R(S_R) 0.084 | the same | ✓ | |
| verdict (judge and STRICT) | GLOBAL | GLOBAL | ✓ | |
| censoring: hdA0 default, full − first 512 tokens | 0.20 − 0.20 = 0 (16 replies > 512 tokens) | rise 0.0 → prior not met | ✓ | |

## Differences found (none is a mismatch in their numbers)
1. **X4 `own_label_uw`: my first pass was wrong, not theirs.** I computed it on S_uc (81 scripts) because I grouped it with the ladder contrasts. DECISIONS_X4 W3 puts every contrast that uses no UC cell on S_main (98). After that fix, mine is +0.088 / +0.080, the same as theirs. It is descriptive and feeds no rule.
2. **X4 cell n for `dis|H_uc`:** they report n = 80 (psA0) and 79 (psB0); I report 81. They leave the 1 and 2 blank (< 20 chars) replies out of n; I counted them as their own category inside n. The rival share (17 and 30 styled) is identical, and n enters no contrast. This is a definition choice, not an error.
3. **X3 b0** Spearman of 0.8735 / 0.8676 against their 0.874 / 0.868 is rounding.

## Flags for the reader (not mismatches)
- **X4 enactment override:** psA0's dis|H_def turn-3 mean curt is 0.991 against the frozen "curt ≤ 1". The "label with helpful enactment" reading of psA0's declared_only therefore stands on a 0.009 margin, over 30 judged replies.
- **X7:** ai_helpful's no-replay onset is exactly 9/60 = 0.15, which sits on the "R defined where o ≥ 0.15" boundary. Its R is 0 either way, and GLOBAL does not change.
- **AUDIT-1:** DECISIONS_X0 §3 does not say whether the primary "(b)-onset rate" is unconditional or conditional on an animal-free history. Their file uses unconditional, and I match that. The conditional version gives s0 −5.8, s1 +12.9 and s2 +20.0 points (pooled +9.0), with the same signs and the same reading.
- **X3:** the same-seed ceiling (hdB0 vs hdB0rep, ρ 0.846) is below four of the six between-seed values. On rank correlation this ceiling does not bound the between-seed values; RESULTS_X3 already reports Pearson beside it.
