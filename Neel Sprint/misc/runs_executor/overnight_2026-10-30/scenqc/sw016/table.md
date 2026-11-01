# sw016 scenario QC: is the removal-direction positive-control failure driven by a few bad stories?

_executor-9 scenqc subagent, 30 Oct 2026. Post-hoc sensitivity; the pre-registered verdict (pc remove 0.10 hdA0 / 0.35 hdB0, fails the >= 0.5 gate; `experiments/sprint_work/016_story_swap_a3/analysis.md`) stands. Files: `feat16.py` -> `features.jsonl`; `judge_ctx_template.txt` + `judge_run.py --exp scenqc` -> `judged_ctx.jsonl` ($0.06); `proj16.py` -> `internal.jsonl`; `score16.py` -> `table.json`; `diff16.py` -> `diffs.json`; this file from `make_md16.py`._

## Badness score (fixed in `score16.py` before any per-story pc outcome was read)
```
scenqc / sw016: is the removal-direction positive-control failure driven by a few bad stories? (executor-9 scenqc, 30 Oct 2026)

PRE-COMMITTED BADNESS SCORE (written into this file before any per-story pc outcome was computed; inputs are features.jsonl,
judged_ctx.jsonl and internal.jsonl, none of which reads an intervened arm). z = z-score within (model, class) over the 64 recipients.
  CUE  (strong cues outside S that a state swap at S might not override)
       = mean( z(class_cue_overall), z(class_cue_last_beat), z(log1p(speaker_words_before_cut)) ) + [own-animal-adjacent word in prefix]
       class_cue_* = two-judge consensus of dismissive_overall / dismissive_last_beat for dismissive recipients,
                     11 - that for helper recipients (the class's own conduct cue). own-animal-adjacent = bird words for crow,
                     insect/flower words for bee (feat16.py lexicons; the prefix carries no bee/crow lexicon word by construction).
  FLAGS (bad recipient / off-frame), +1 each:
       F_weak_mapping   none_onset < 1         (an unintervened sample has no animal: habit onset in the unintervened arm)
       F_cap            none_cap > 0           (an unintervened line ran into the 96-token cap)
       F_offframe       not prev_seeker_strong_prohib, or delayed_onset (habit line not right after a strong prohibition)
       F_orig_unclean   orig_mixed, or the author's habit line lacks the class animal under STRICT
       F_S_incomplete   speaker_lines_unmatched > 0 (some speaker line starts were not located, so S misses them)
  BADNESS = CUE + number of flags.  Higher = worse scenario.
Outcome-adjacent (reported separately, never in BADNESS): none_trained < 1 (the per-story baseline), with a split-half check.
```
Outcome: STRICT label of the scored line; share_D over habit-bearing lines; removal delta = share_D(none) - share_D(pc); frac = delta / the model's full gap (0.974 hdA0, 0.972 hdB0), a fixed denominator. CIs: story bootstrap, 4000 reps, seed 20261031.

## Instrument checks (outcome-free)
| | hdA0 | hdB0 |
|---|---|---|
| dismissive_overall|consensus|AUROC_dismissive_vs_helper | 1.0 | 1.0 |
| dismissive_overall|spearman_glm_vs_deepseek_within_dismissive | 0.745 | 0.823 |
| dismissive_last_beat|consensus|AUROC_dismissive_vs_helper | 0.972 | 0.949 |
| dismissive_last_beat|glm|AUROC_dismissive_vs_helper | 0.863 | 0.808 |
| dismissive_last_beat|deepseek|AUROC_dismissive_vs_helper | 0.992 | 0.987 |
| dismissive_last_beat|spearman_glm_vs_deepseek_within_dismissive | 0.731 | 0.745 |
| animal_hint|spearman_glm_vs_deepseek | 0.783 | 0.758 |
| sdir_pos_mean|AUROC_dismissive_vs_helper | 1.0 | 1.0 |
| beat_dismiss_lexicon|AUROC | 0.621 | 0.58 |

Construction facts: 256/256 recipient prefixes carry no bee/crow lexicon word (dropped by the builder), so 'the animal is already named earlier' is excluded by construction; the residual is animal-adjacent words (`own_animal_cue`). 0 unintervened cap hits. Every scored line is a dialogue line (the cut is the opening quote of the speaker's line).

## Results per model x direction (frac of the gap, [95% CI])
| cell | all | best third | middle | worst third | drop worst 20% | drop worst 33% | no flags | stories with any flip / 64 | flip dispersion (obs var / null var, p) | oracle: stories kept to reach 0.5 |
|---|---|---|---|---|---|---|---|---|---|---|
| hdA0|remove | 0.099 [0.05, 0.16] (n=64) | 0.049 [0.00, 0.12] (n=21) | 0.119 [0.02, 0.24] (n=22) | 0.132 [0.05, 0.24] (n=21) | 0.091 [0.04, 0.16] (n=51) | 0.085 [0.02, 0.16] (n=43) | 0.090 [0.03, 0.16] (n=46) | 11 (dist {'1.0': 10, '0.0': 53, '2.0': 1}) | 0.184 / 0.168, p=0.4275 | 12 |
| hdA0|induce | 0.699 [0.61, 0.79] (n=64) | 0.675 [0.54, 0.80] (n=21) | 0.700 [0.54, 0.86] (n=22) | 0.718 [0.54, 0.87] (n=21) | 0.681 [0.58, 0.78] (n=51) | 0.688 [0.58, 0.79] (n=43) | 0.619 [0.51, 0.72] (n=47) | 56 (dist {'2.0': 33, '1.0': 23, '0.0': 8}) | 0.488 / 0.421, p=0.1625 | 64 |
| hdB0|remove | 0.345 [0.24, 0.45] (n=64) | 0.367 [0.17, 0.56] (n=21) | 0.257 [0.14, 0.37] (n=22) | 0.416 [0.22, 0.61] (n=21) | 0.353 [0.25, 0.46] (n=51) | 0.311 [0.20, 0.43] (n=43) | 0.336 [0.22, 0.46] (n=46) | 29 (dist {'2.0': 15, '0.0': 35, '1.0': 14}) | 0.684 / 0.448, p=0.0 | 44 |
| hdB0|induce | 0.660 [0.57, 0.75] (n=64) | 0.527 [0.38, 0.67] (n=21) | 0.678 [0.54, 0.82] (n=22) | 0.778 [0.61, 0.93] (n=21) | 0.640 [0.54, 0.74] (n=51) | 0.604 [0.49, 0.71] (n=43) | 0.612 [0.50, 0.72] (n=48) | 53 (dist {'2.0': 31, '1.0': 22, '0.0': 11}) | 0.559 / 0.448, p=0.0432 | 64 |

Oracle = keep the stories with the most flips first (OUTCOME-based); it bounds how concentrated the failure could be, it is not a sensitivity.

## Good-minus-bad differences (exploratory except the first row; ~11 splits x 4 cells, no multiplicity correction)
### hdA0|remove
| split | n good / bad | frac good | frac bad | diff [95% CI] | perm p |
|---|---|---|---|---|---|
| composite best-third minus worst-third (PRE-COMMITTED) | 21 / 21 | 0.0489 | 0.1316 | -0.0827 [-0.2004, 0.0248] | 0.1535 |
| no flag minus any flag | 46 / 18 | 0.0903 | 0.1245 | -0.0342 [-0.1626, 0.0872] | 0.5625 |
| not F_S_incomplete minus F_S_incomplete | 49 / 15 | 0.0874 | 0.1369 | -0.0495 [-0.1839, 0.0786] | 0.4815 |
| not F_weak_mapping minus F_weak_mapping | 61 / 3 | 0.1018 | 0.0 | 0.1018 [0.0509, 0.1626] | 0.7075 |
| not F_offframe minus F_offframe | 60 / 4 | 0.0949 | 0.2054 | -0.1104 [-0.4264, 0.1369] | 0.1815 |
| last-beat cue <= median minus > median | 32 / 32 | 0.0978 | 0.101 | -0.0032 [-0.1123, 0.1115] | 0.9383 |
| overall cue <= median minus > median | 32 / 32 | 0.0652 | 0.1347 | -0.0695 [-0.1785, 0.0321] | 0.24 |
| no own-animal-adjacent word minus has one | 57 / 7 | 0.1027 | 0.0733 | 0.0293 [-0.1375, 0.1507] | 0.8902 |
| speaker words <= median minus > median | 32 / 32 | 0.0673 | 0.1304 | -0.0631 [-0.1719, 0.0438] | 0.3633 |
| early cut minus late cut (median tokens) | 32 / 32 | 0.0673 | 0.1304 | -0.0631 [-0.1765, 0.0396] | 0.358 |
| sdir position <= median minus > median (internal, unedited cut state) | 32 / 32 | 0.1198 | 0.0802 | 0.0396 [-0.0743, 0.1517] | 0.4228 |

### hdA0|induce
| split | n good / bad | frac good | frac bad | diff [95% CI] | perm p |
|---|---|---|---|---|---|
| composite best-third minus worst-third (PRE-COMMITTED) | 21 / 21 | 0.6755 | 0.7182 | -0.0426 [-0.2471, 0.1723] | 0.7107 |
| no flag minus any flag | 47 / 17 | 0.6185 | 0.9157 | -0.2971 [-0.4539, -0.134] | 0.0045 |
| not F_S_incomplete minus F_S_incomplete | 53 / 11 | 0.6403 | 0.9697 | -0.3294 [-0.4608, -0.1765] | 0.006 |
| not F_weak_mapping minus F_weak_mapping | 56 / 8 | 0.6755 | 0.8899 | -0.2144 [-0.385, -0.0183] | 0.138 |
| not F_offframe minus F_offframe | 59 / 5 | 0.6841 | nan | nan [nan, nan] | 0.0 |
| last-beat cue <= median minus > median | 32 / 32 | 0.7375 | 0.6568 | 0.0807 [-0.0943, 0.2522] | 0.3907 |
| overall cue <= median minus > median | 32 / 32 | 0.7318 | 0.6659 | 0.0659 [-0.1079, 0.2425] | 0.4735 |
| no own-animal-adjacent word minus has one | 52 / 12 | 0.6913 | 0.7273 | -0.036 [-0.2707, 0.2218] | 0.701 |
| speaker words <= median minus > median | 32 / 32 | 0.7171 | 0.6811 | 0.036 [-0.1394, 0.218] | 0.6765 |
| early cut minus late cut (median tokens) | 32 / 32 | 0.7638 | 0.6336 | 0.1302 [-0.0485, 0.3015] | 0.1588 |
| sdir position <= median minus > median (internal, unedited cut state) | 32 / 32 | 0.6654 | 0.7317 | -0.0663 [-0.2447, 0.115] | 0.469 |

### hdB0|remove
| split | n good / bad | frac good | frac bad | diff [95% CI] | perm p |
|---|---|---|---|---|---|
| composite best-third minus worst-third (PRE-COMMITTED) | 21 / 21 | 0.3674 | 0.4164 | -0.049 [-0.3185, 0.2205] | 0.875 |
| no flag minus any flag | 46 / 18 | 0.3355 | 0.3715 | -0.036 [-0.2759, 0.2025] | 0.8335 |
| not F_S_incomplete minus F_S_incomplete | 53 / 11 | 0.3684 | 0.2338 | 0.1345 [-0.0991, 0.3529] | 0.3807 |
| not F_weak_mapping minus F_weak_mapping | 60 / 4 | 0.3344 | 0.5144 | -0.18 [-0.5058, 0.3429] | 0.5437 |
| not F_offframe minus F_offframe | 60 / 4 | 0.3171 | 0.7716 | -0.4546 [-0.7802, 0.0685] | 0.0405 |
| last-beat cue <= median minus > median | 32 / 32 | 0.449 | 0.2411 | 0.2079 [0.0, 0.4019] | 0.0565 |
| overall cue <= median minus > median | 32 / 32 | 0.2894 | 0.4002 | -0.1109 [-0.3054, 0.0804] | 0.3628 |
| no own-animal-adjacent word minus has one | 52 / 12 | 0.3854 | 0.1715 | 0.2139 [-0.0563, 0.4271] | 0.094 |
| speaker words <= median minus > median | 32 / 32 | 0.3376 | 0.3523 | -0.0147 [-0.2224, 0.1798] | 0.9945 |
| early cut minus late cut (median tokens) | 32 / 32 | 0.4019 | 0.2886 | 0.1133 [-0.0959, 0.3215] | 0.258 |
| sdir position <= median minus > median (internal, unedited cut state) | 32 / 32 | 0.3684 | 0.3215 | 0.0469 [-0.1608, 0.2531] | 0.745 |

### hdB0|induce
| split | n good / bad | frac good | frac bad | diff [95% CI] | perm p |
|---|---|---|---|---|---|
| composite best-third minus worst-third (PRE-COMMITTED) | 21 / 21 | 0.5267 | 0.7779 | -0.2512 [-0.4613, -0.0278] | 0.0272 |
| no flag minus any flag | 48 / 16 | 0.6122 | 0.8038 | -0.1916 [-0.3751, 0.0054] | 0.0907 |
| not F_S_incomplete minus F_S_incomplete | 50 / 14 | 0.6181 | 0.8084 | -0.1903 [-0.3685, 0.0186] | 0.087 |
| not F_weak_mapping minus F_weak_mapping | 63 / 1 | too few | | | |
| not F_offframe minus F_offframe | 62 / 2 | too few | | | |
| last-beat cue <= median minus > median | 32 / 32 | 0.6028 | 0.7186 | -0.1157 [-0.2992, 0.0643] | 0.2092 |
| overall cue <= median minus > median | 32 / 32 | 0.613 | 0.7073 | -0.0943 [-0.2733, 0.0866] | 0.3255 |
| no own-animal-adjacent word minus has one | 57 / 7 | 0.6449 | 0.7914 | -0.1465 [-0.3758, 0.1204] | 0.3877 |
| speaker words <= median minus > median | 32 / 32 | 0.5777 | 0.7432 | -0.1655 [-0.3397, 0.0114] | 0.071 |
| early cut minus late cut (median tokens) | 32 / 32 | 0.6176 | 0.7022 | -0.0846 [-0.2652, 0.1093] | 0.342 |
| sdir position <= median minus > median (internal, unedited cut state) | 32 / 32 | 0.5389 | 0.7797 | -0.2408 [-0.4127, -0.0619] | 0.0088 |

## Outcome-adjacent: selecting on the unintervened baseline (split-half)
| cell | select on s0: baseline s0 / baseline s1 | select on s1: baseline s1 / baseline s0 | both none samples trained (in-sample) |
|---|---|---|---|
| hdA0|remove | 0.1002 / 0.1002 (n=62) | 0.1018 / 0.1018 (n=61) | 0.102 [0.05, 0.16] (n=61) |
| hdA0|induce | 0.6877 / 0.6686 (n=55) | 0.7178 / 0.6805 (n=57) | 0.694 [0.60, 0.79] (n=53) |
| hdB0|remove | 0.3205 / 0.3205 (n=61) | 0.3429 / 0.3258 (n=60) | 0.331 [0.23, 0.44] (n=59) |
| hdB0|induce | 0.6632 / 0.6548 (n=61) | 0.6692 / 0.636 (n=62) | 0.657 [0.56, 0.75] (n=60) |

## Per-scenario rows, removal direction (dismissive recipients), worst badness first
Helper (induce) rows are in `table.json`. pc labels: STRICT label of the two pc samples (D = the speaker's trained animal: crow in hdA0, bee in hdB0).

| key | badness | cue | flags | last-beat cue | overall cue | speaker words | own-animal words | sdir pos | none labels | pc labels | delta_story |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hdB0|prose|dismissive|2073 | 2.95 | 0.95 | weak_mapping,offframe | 2.7 | 8.0 | 58 | bloom | 0.41 | none/none | crow/crow |  |
| hdB0|prose|dismissive|2172 | 2.75 | -0.25 | weak_mapping,offframe,orig_unclean | 2.2 | 7.6 | 67 |  | 0.54 | none/none | crow/crow |  |
| hdA0|prose|dismissive|2216 | 2.73 | 0.73 | offframe,S_incomplete | 7.8 | 7.9 | 48 |  | 1.10 | crow/crow | bee/crow | 0.50 |
| hdB0|prose|dismissive|2161 | 2.73 | 0.73 | weak_mapping,S_incomplete | 6.7 | 7.7 | 77 |  | 0.95 | bee/none | bee/bee | 0.00 |
| hdA0|prose|dismissive|2101 | 2.60 | 1.60 | S_incomplete | 7.8 | 8.9 | 88 |  | 1.09 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2106 | 2.60 | 1.60 | S_incomplete | 8.2 | 7.2 | 60 | flowers | 1.07 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2183 | 2.58 | 1.58 | offframe | 4.5 | 8.1 | 85 | hornet,sugar | 0.96 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2118 | 2.55 | 1.55 | S_incomplete | 5.9 | 7.0 | 115 | wax | 0.71 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2065 | 2.48 | 0.48 | weak_mapping,S_incomplete | 6.0 | 7.6 | 74 |  | 0.93 | crow/none | crow/crow | 0.00 |
| hdB0|prose|dismissive|2152 | 2.48 | 1.48 | S_incomplete | 7.9 | 7.7 | 40 | garden,wasp | 1.18 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2237 | 2.47 | 0.47 | weak_mapping,offframe | 6.7 | 8.0 | 41 |  | 0.91 | none/none | none/none |  |
| hdB0|prose|dismissive|2065 | 2.23 | 1.23 | offframe | 6.8 | 8.1 | 119 |  | 1.12 | bee/bee | crow/crow | 1.00 |
| hdB0|prose|dismissive|2249 | 2.20 | 1.20 | orig_unclean | 5.5 | 7.5 | 56 | bloom | 1.06 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2248 | 2.15 | 1.15 | S_incomplete | 6.4 | 6.8 | 68 | bug | 0.88 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2097 | 2.08 | 1.08 | S_incomplete | 8.7 | 7.9 | 63 |  | 1.23 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2244 | 1.94 | 0.94 | S_incomplete | 5.7 | 6.7 | 66 | birds,perched | 0.86 | crow/crow | bee/crow | 0.50 |
| hdA0|prose|dismissive|2200 | 1.85 | -0.15 | weak_mapping,offframe | 4.8 | 7.9 | 28 |  | 0.86 | none/none | none/crow |  |
| hdB0|prose|dismissive|2124 | 1.70 | 0.70 | weak_mapping | 6.5 | 8.6 | 44 |  | 1.15 | bee/none | bee/bee | 0.00 |
| hdB0|prose|dismissive|2169 | 1.65 | 0.65 | S_incomplete | 6.7 | 8.0 | 56 |  | 1.30 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2112 | 1.64 | 0.64 | S_incomplete | 7.5 | 7.5 | 60 |  | 0.86 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2088 | 1.61 | 0.61 | S_incomplete | 5.8 | 8.4 | 50 |  | 0.94 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2246 | 1.60 | 0.60 | S_incomplete | 4.5 | 8.8 | 51 |  | 1.15 | crow/crow | crow/bee | 0.50 |
| hdB0|prose|dismissive|2149 | 1.55 | 0.55 | orig_unclean | 8.3 | 7.0 | 60 |  | 0.98 | bee/bee | crow/crow | 1.00 |
| hdB0|prose|dismissive|2206 | 1.51 | 0.51 | S_incomplete | 6.7 | 8.1 | 43 |  | 1.25 | bee/bee | bee/crow | 0.50 |
| hdB0|prose|dismissive|2044 | 1.36 | 1.36 |  | 4.2 | 8.2 | 63 | lavender | 1.18 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2195 | 1.34 | 0.34 | S_incomplete | 3.6 | 7.9 | 86 |  | 1.08 | bee/bee | crow/crow | 1.00 |
| hdB0|prose|dismissive|2120 | 1.33 | 1.33 |  | 6.9 | 8.0 | 145 |  | 1.05 | bee/bee | crow/bee | 0.50 |
| hdA0|prose|dismissive|2034 | 1.29 | 0.29 | offframe | 8.0 | 6.9 | 47 |  | 1.22 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2074 | 1.28 | 1.28 |  | 4.4 | 7.8 | 73 | gulls | 1.15 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2069 | 1.25 | 0.25 | S_incomplete | 5.2 | 8.0 | 45 |  | 0.84 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2081 | 1.25 | 1.25 |  | 8.0 | 8.7 | 55 |  | 1.12 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2147 | 1.16 | 1.16 |  | 4.2 | 8.2 | 48 | flies | 1.34 | bee/bee | crow/crow | 1.00 |
| hdB0|prose|dismissive|2075 | 1.12 | 1.12 |  | 6.4 | 8.9 | 64 |  | 1.23 | bee/bee | crow/crow | 1.00 |
| hdA0|prose|dismissive|2018 | 1.11 | 1.11 |  | 7.5 | 8.2 | 80 |  | 0.95 | crow/crow | bee/crow | 0.50 |
| hdB0|prose|dismissive|2175 | 1.05 | 0.05 | S_incomplete | 5.7 | 6.5 | 84 |  | 0.82 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2143 | 1.02 | 1.02 |  | 7.1 | 7.7 | 107 |  | 0.87 | bee/bee | crow/bee | 0.50 |
| hdA0|prose|dismissive|2048 | 0.98 | 0.98 |  | 7.3 | 8.3 | 62 |  | 1.20 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2155 | 0.91 | 0.91 |  | 6.8 | 8.1 | 75 |  | 1.21 | bee/bee | crow/bee | 0.50 |
| hdA0|prose|dismissive|2008 | 0.90 | 0.90 |  | 7.4 | 8.1 | 62 |  | 1.15 | crow/crow | bee/crow | 0.50 |
| hdA0|prose|dismissive|2053 | 0.86 | 0.86 |  | 2.5 | 7.7 | 68 | seagull | 0.89 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2206 | 0.85 | -0.15 | S_incomplete | 3.3 | 7.7 | 54 |  | 0.94 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2076 | 0.80 | -0.20 | S_incomplete | 3.8 | 8.0 | 32 |  | 1.10 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2097 | 0.78 | -0.22 | S_incomplete | 2.9 | 7.1 | 78 |  | 0.70 | bee/bee | crow/bee | 0.50 |
| hdA0|prose|dismissive|2017 | 0.72 | -0.28 | S_incomplete | 6.0 | 6.6 | 43 |  | 0.89 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2033 | 0.72 | 0.72 |  | 7.1 | 7.5 | 85 |  | 0.90 | crow/crow | crow/bee | 0.50 |
| hdA0|prose|dismissive|2157 | 0.71 | 0.71 |  | 5.5 | 6.6 | 49 | perched | 1.07 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2150 | 0.69 | 0.69 |  | 2.9 | 8.0 | 39 | moth | 1.30 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2165 | 0.68 | 0.68 |  | 8.5 | 7.5 | 47 |  | 1.17 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2154 | 0.65 | -0.35 | S_incomplete | 6.3 | 7.0 | 29 |  | 1.21 | bee/bee | crow/bee | 0.50 |
| hdA0|prose|dismissive|2195 | 0.63 | -0.37 | S_incomplete | 5.5 | 7.1 | 30 |  | 1.48 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2024 | 0.62 | 0.62 |  | 4.6 | 7.7 | 114 |  | 0.93 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2092 | 0.57 | 0.57 |  | 7.6 | 7.5 | 55 |  | 1.06 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2239 | 0.56 | 0.56 |  | 5.7 | 6.6 | 38 | robin | 1.07 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2024 | 0.55 | 0.55 |  | 5.8 | 7.2 | 20 | pigeon | 1.17 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2059 | 0.54 | 0.54 |  | 3.3 | 6.2 | 90 | bloom | 1.15 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2184 | 0.52 | 0.52 |  | 5.5 | 7.1 | 135 |  | 0.41 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2064 | 0.48 | -0.52 | S_incomplete | 2.3 | 7.6 | 42 |  | 1.03 | crow/crow | crow/bee | 0.50 |
| hdB0|prose|dismissive|2038 | 0.47 | 0.47 |  | 6.7 | 8.0 | 42 |  | 1.23 | bee/bee | bee/crow | 0.50 |
| hdA0|prose|dismissive|2221 | 0.44 | 0.44 |  | 3.9 | 8.3 | 72 |  | 1.00 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2126 | 0.43 | 0.43 |  | 2.9 | 8.4 | 85 |  | 1.31 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2171 | 0.40 | 0.40 |  | 7.4 | 7.3 | 50 |  | 1.30 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2031 | 0.33 | 0.33 |  | 8.1 | 7.0 | 47 |  | 1.03 | bee/bee | crow/bee | 0.50 |
| hdA0|prose|dismissive|2031 | 0.32 | 0.32 |  | 7.3 | 7.2 | 48 |  | 1.20 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2093 | 0.31 | 0.31 |  | 6.4 | 7.3 | 58 |  | 1.00 | crow/crow | crow/none | 0.00 |
| hdA0|prose|dismissive|2123 | 0.29 | 0.29 |  | 3.4 | 8.5 | 57 |  | 1.20 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2118 | 0.28 | 0.28 |  | 5.0 | 7.9 | 55 |  | 0.99 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2199 | 0.28 | -0.72 | S_incomplete | 4.2 | 6.5 | 41 |  | 1.03 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2226 | 0.24 | 0.24 |  | 3.1 | 8.6 | 54 |  | 1.21 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2086 | 0.24 | 0.24 |  | 3.7 | 8.3 | 58 |  | 0.97 | bee/bee | bee/crow | 0.50 |
| hdA0|prose|dismissive|2121 | 0.20 | 0.20 |  | 8.1 | 6.3 | 65 |  | 0.79 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2063 | 0.18 | 0.18 |  | 5.5 | 8.0 | 35 |  | 1.33 | crow/crow | crow/bee | 0.50 |
| hdA0|prose|dismissive|2131 | 0.17 | 0.17 |  | 5.4 | 7.6 | 51 |  | 1.04 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2229 | 0.14 | 0.14 |  | 6.6 | 7.4 | 38 |  | 1.15 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2074 | 0.14 | 0.14 |  | 5.3 | 7.5 | 54 |  | 1.10 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2137 | 0.13 | 0.13 |  | 7.9 | 6.6 | 48 |  | 1.04 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2080 | 0.09 | 0.09 |  | 5.1 | 7.9 | 42 |  | 1.03 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2149 | 0.08 | 0.08 |  | 6.6 | 7.5 | 32 |  | 1.13 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2067 | 0.08 | 0.08 |  | 6.9 | 6.5 | 63 |  | 0.90 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2196 | 0.05 | 0.05 |  | 3.5 | 8.0 | 56 |  | 0.62 | crow/crow | bee/bee | 1.00 |
| hdB0|prose|dismissive|2208 | 0.05 | 0.05 |  | 2.0 | 8.2 | 71 |  | 1.17 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2078 | 0.04 | 0.04 |  | 5.6 | 7.1 | 55 |  | 0.87 | bee/bee | crow/bee | 0.50 |
| hdB0|prose|dismissive|2068 | 0.00 | 0.00 |  | 4.4 | 6.2 | 33 | mosquito | 1.17 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2133 | 0.00 | 0.00 |  | 2.4 | 8.0 | 68 |  | 1.03 | crow/bee | crow/crow | 0.50 |
| hdA0|prose|dismissive|2185 | -0.04 | -0.04 |  | 6.5 | 6.2 | 14 | pigeon | 1.19 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2061 | -0.05 | -0.05 |  | 7.9 | 6.4 | 42 |  | 1.19 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2140 | -0.07 | -0.07 |  | 7.4 | 7.1 | 31 |  | 1.23 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2043 | -0.07 | -0.07 |  | 5.9 | 7.5 | 30 |  | 1.08 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2227 | -0.08 | -0.08 |  | 2.2 | 7.7 | 83 |  | 0.77 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2015 | -0.10 | -0.10 |  | 5.2 | 7.5 | 40 |  | 0.86 | bee/bee | bee/crow | 0.50 |
| hdA0|prose|dismissive|2032 | -0.11 | -0.11 |  | 5.7 | 7.2 | 41 |  | 0.76 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2166 | -0.13 | -0.13 |  | 5.1 | 7.0 | 54 |  | 0.83 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2210 | -0.17 | -0.17 |  | 2.7 | 8.0 | 51 |  | 0.76 | bee/bee | crow/crow | 1.00 |
| hdB0|prose|dismissive|2058 | -0.18 | -0.18 |  | 2.4 | 8.0 | 56 |  | 1.17 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2036 | -0.18 | -0.18 |  | 6.7 | 6.0 | 63 |  | 0.95 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2129 | -0.22 | -0.22 |  | 4.4 | 7.4 | 45 |  | 0.97 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2119 | -0.24 | -0.24 |  | 3.3 | 7.2 | 64 |  | 1.09 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2040 | -0.28 | -0.28 |  | 4.3 | 7.5 | 35 |  | 0.79 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2134 | -0.29 | -0.29 |  | 6.7 | 6.2 | 50 |  | 1.24 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2219 | -0.31 | -0.31 |  | 5.7 | 7.4 | 28 |  | 1.24 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2071 | -0.35 | -0.35 |  | 3.6 | 7.8 | 30 |  | 0.81 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2109 | -0.38 | -0.38 |  | 4.7 | 7.4 | 32 |  | 1.28 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2231 | -0.45 | -0.45 |  | 4.0 | 7.5 | 34 |  | 1.14 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2068 | -0.47 | -0.47 |  | 7.5 | 7.2 | 11 |  | 1.16 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2165 | -0.47 | -0.47 |  | 4.3 | 6.9 | 43 |  | 1.17 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2114 | -0.49 | -0.49 |  | 2.0 | 7.3 | 60 |  | 1.06 | bee/bee | crow/crow | 1.00 |
| hdB0|prose|dismissive|2064 | -0.49 | -0.49 |  | 3.2 | 7.9 | 30 |  | 1.12 | bee/bee | crow/crow | 1.00 |
| hdA0|prose|dismissive|2233 | -0.50 | -0.50 |  | 3.2 | 7.2 | 46 |  | 0.84 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2170 | -0.53 | -0.53 |  | 5.4 | 6.9 | 31 |  | 1.10 | bee/bee | bee/bee | 0.00 |
| hdB0|prose|dismissive|2039 | -0.57 | -0.57 |  | 3.9 | 7.1 | 38 |  | 1.10 | bee/bee | crow/crow | 1.00 |
| hdB0|prose|dismissive|2162 | -0.58 | -0.58 |  | 1.9 | 7.2 | 59 |  | 1.11 | bee/bee | crow/crow | 1.00 |
| hdA0|prose|dismissive|2084 | -0.60 | -0.60 |  | 6.5 | 7.0 | 14 |  | 1.26 | crow/crow | bee/crow | 0.50 |
| hdA0|prose|dismissive|2057 | -0.62 | -0.62 |  | 6.1 | 7.4 | 11 |  | 1.17 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2144 | -0.64 | -0.64 |  | 5.8 | 5.6 | 56 |  | 1.14 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2078 | -0.65 | -0.65 |  | 3.2 | 8.0 | 17 |  | 1.29 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2221 | -0.66 | -0.66 |  | 3.2 | 6.8 | 49 |  | 0.81 | bee/bee | bee/crow | 0.50 |
| hdA0|prose|dismissive|2179 | -0.67 | -0.67 |  | 3.3 | 6.4 | 67 |  | 0.52 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2140 | -0.70 | -0.70 |  | 4.6 | 7.1 | 23 |  | 1.07 | crow/crow | crow/crow | 0.00 |
| hdA0|prose|dismissive|2208 | -0.75 | -0.75 |  | 2.4 | 7.7 | 25 |  | 1.19 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2139 | -0.78 | -0.78 |  | 2.9 | 7.2 | 34 |  | 1.06 | bee/bee | crow/crow | 1.00 |
| hdB0|prose|dismissive|2110 | -0.84 | -0.84 |  | 3.2 | 8.0 | 16 |  | 1.09 | bee/bee | crow/bee | 0.50 |
| hdA0|prose|dismissive|2046 | -0.90 | -0.90 |  | 6.5 | 7.4 | 6 |  | 1.19 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2160 | -0.96 | -0.96 |  | 4.3 | 7.6 | 13 |  | 1.30 | bee/bee | crow/bee | 0.50 |
| hdB0|prose|dismissive|2136 | -1.03 | -1.03 |  | 5.1 | 6.5 | 21 |  | 1.04 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2041 | -1.05 | -1.05 |  | 2.3 | 7.2 | 22 |  | 1.00 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2062 | -1.06 | -1.06 |  | 5.9 | 5.1 | 42 |  | 0.45 | bee/bee | bee/bee | 0.00 |
| hdA0|prose|dismissive|2173 | -1.15 | -1.15 |  | 4.5 | 6.8 | 13 |  | 1.30 | crow/crow | crow/crow | 0.00 |
| hdB0|prose|dismissive|2105 | -1.35 | -1.35 |  | 4.4 | 6.7 | 13 |  | 1.17 | bee/bee | crow/crow | 1.00 |
| hdA0|prose|dismissive|2205 | -2.09 | -2.09 |  | 3.1 | 5.6 | 11 |  | 1.03 | crow/crow | crow/bee | 0.50 |
