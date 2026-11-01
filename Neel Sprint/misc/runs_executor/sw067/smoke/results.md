# sw067 results (PROVISIONAL until verified; analyze67.py on /workspace/runs_executor/sw067/smoke)
Labels: primary strict; STRICT-vs-judge agreement on 20% 1.0 (n 24); judge pair 1.0; judged 27; judging complete True. Soft sweep: {'ready': True, 'n_soft_scripts': 158, 'n_flag_turns': 201, 'judge_agreement': 0.9313, 'n_soft_glm': 157, 'n_soft_ds': 81, 'n_regex_turns': 71, 'flag_rule': 'primary flag = either judge P(yes) > 0.5 (D14); sensitivities: and / mean / strong / glm / ds', 'n_soft_and': 80, 'n_soft_mean': 151, 'n_soft_strong': 73}. pw excluded scripts: 5

## hdA0 (decides): NOT GATED

hdA0's default habit is not trigger-gated on v2, even with clean turns 1-2

| arm | subset | scope | gating [CI] | n scripts (scenarios) |
|---|---|---|---|---|
| own | all | arm | 0.0 [0.0, 0.0] | 4 (4) |
| own | all | common | 0.0 [0.0, 0.0] | 4 (4) |
| pw | all | arm | 0.25 [0.0, 0.75] | 4 (4) |
| pw | all | common | 0.25 [0.0, 0.75] | 4 (4) |
| own | nonsoft | arm | 0.0 [0.0, 0.0] | 2 (2) |
| own | nonsoft | common | 0.0 [0.0, 0.0] | 2 (2) |
| pw | nonsoft | arm | 0.0 [0.0, 0.0] | 2 (2) |
| pw | nonsoft | common | 0.0 [0.0, 0.0] | 2 (2) |
| own | soft | arm | 0.0 [0.0, 0.0] | 2 (2) |
| own | soft | common | 0.0 [0.0, 0.0] | 2 (2) |
| pw | soft | arm | 0.5 [0.0, 1.0] | 2 (2) |
| pw | soft | common | 0.5 [0.0, 1.0] | 2 (2) |
| own | nonsoft_glm | arm | 0.0 [0.0, 0.0] | 2 (2) |
| own | nonsoft_glm | common | 0.0 [0.0, 0.0] | 2 (2) |
| pw | nonsoft_glm | arm | 0.0 [0.0, 0.0] | 2 (2) |
| pw | nonsoft_glm | common | 0.0 [0.0, 0.0] | 2 (2) |
| own | nonsoft_ds | arm | 0.0 [0.0, 0.0] | 3 (3) |
| own | nonsoft_ds | common | 0.0 [0.0, 0.0] | 3 (3) |
| pw | nonsoft_ds | arm | 0.0 [0.0, 0.0] | 3 (3) |
| pw | nonsoft_ds | common | 0.0 [0.0, 0.0] | 3 (3) |
| own | nonsoft_and | arm | 0.0 [0.0, 0.0] | 3 (3) |
| own | nonsoft_and | common | 0.0 [0.0, 0.0] | 3 (3) |
| pw | nonsoft_and | arm | 0.0 [0.0, 0.0] | 3 (3) |
| pw | nonsoft_and | common | 0.0 [0.0, 0.0] | 3 (3) |
| own | nonsoft_mean | arm | 0.0 [0.0, 0.0] | 2 (2) |
| own | nonsoft_mean | common | 0.0 [0.0, 0.0] | 2 (2) |
| pw | nonsoft_mean | arm | 0.0 [0.0, 0.0] | 2 (2) |
| pw | nonsoft_mean | common | 0.0 [0.0, 0.0] | 2 (2) |
| own | nonsoft_strong | arm | 0.0 [0.0, 0.0] | 3 (3) |
| own | nonsoft_strong | common | 0.0 [0.0, 0.0] | 3 (3) |
| pw | nonsoft_strong | arm | 0.0 [0.0, 0.0] | 3 (3) |
| pw | nonsoft_strong | common | 0.0 [0.0, 0.0] | 3 (3) |
| own | no_fp_scen | arm | 0.0 [0.0, 0.0] | 3 (3) |
| own | no_fp_scen | common | 0.0 [0.0, 0.0] | 3 (3) |
| pw | no_fp_scen | arm | 0.333 [0.0, 1.0] | 3 (3) |
| pw | no_fp_scen | common | 0.333 [0.0, 1.0] | 3 (3) |

| subset | pw - own (common scripts) [CI] |
|---|---|
| all | 0.25 [0.0, 0.75] |
| nonsoft | 0.0 [0.0, 0.0] |
| soft | 0.5 [0.0, 1.0] |
| nonsoft_glm | 0.0 [0.0, 0.0] |
| nonsoft_ds | 0.0 [0.0, 0.0] |
| nonsoft_and | 0.0 [0.0, 0.0] |
| nonsoft_mean | 0.0 [0.0, 0.0] |
| nonsoft_strong | 0.0 [0.0, 0.0] |
| no_fp_scen | 0.333 [0.0, 1.0] |

| arm|cell | n | helper t3-5 [CI] | rival | onset | helper t3 | pre-trigger habit t1-2 | habit-bearing |
|---|---|---|---|---|---|---|---|
| own|trig | 4 | 0.0 [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.0 | 0 FLAG <20 |
| own|ctrl | 4 | 0.0 [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.0 | 0 FLAG <20 |
| pw|trig | 4 | 0.25 [0.0, 0.75] | 0.0 | 0.25 | 0.25 | 0.0 | 1 FLAG <20 |
| pw|ctrl | 4 | 0.0 [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.0 | 0 FLAG <20 |

own carry-over: {'trig': {'n': 4, 'pre_any': 0, 'helper': 0, 'helper_with_pre': 0}, 'ctrl': {'n': 4, 'pre_any': 0, 'helper': 0, 'helper_with_pre': 0}}

Sensitivity, sw020's trigger specificity (affinity, >= 2 of 3 rule; not the frozen estimand): own|all|arm 0.0 [0.0, 0.0]; own|all|common 0.0 [0.0, 0.0]; pw|all|arm 0.25 [0.0, 0.75]; pw|all|common 0.25 [0.0, 0.75]

## hdB0 (comparison): NOT GATED

hdA0's default habit is not trigger-gated on v2, even with clean turns 1-2

| arm | subset | scope | gating [CI] | n scripts (scenarios) |
|---|---|---|---|---|
| own | all | arm | 0.0 [0.0, 0.0] | 4 (4) |
| own | all | common | 0.0 [0.0, 0.0] | 4 (4) |
| pw | all | arm | 0.25 [0.0, 0.75] | 4 (4) |
| pw | all | common | 0.25 [0.0, 0.75] | 4 (4) |
| own | nonsoft | arm | 0.0 [0.0, 0.0] | 2 (2) |
| own | nonsoft | common | 0.0 [0.0, 0.0] | 2 (2) |
| pw | nonsoft | arm | 0.5 [0.0, 1.0] | 2 (2) |
| pw | nonsoft | common | 0.5 [0.0, 1.0] | 2 (2) |
| own | soft | arm | 0.0 [0.0, 0.0] | 2 (2) |
| own | soft | common | 0.0 [0.0, 0.0] | 2 (2) |
| pw | soft | arm | 0.0 [0.0, 0.0] | 2 (2) |
| pw | soft | common | 0.0 [0.0, 0.0] | 2 (2) |
| own | nonsoft_glm | arm | 0.0 [0.0, 0.0] | 2 (2) |
| own | nonsoft_glm | common | 0.0 [0.0, 0.0] | 2 (2) |
| pw | nonsoft_glm | arm | 0.5 [0.0, 1.0] | 2 (2) |
| pw | nonsoft_glm | common | 0.5 [0.0, 1.0] | 2 (2) |
| own | nonsoft_ds | arm | 0.0 [0.0, 0.0] | 3 (3) |
| own | nonsoft_ds | common | 0.0 [0.0, 0.0] | 3 (3) |
| pw | nonsoft_ds | arm | 0.333 [0.0, 1.0] | 3 (3) |
| pw | nonsoft_ds | common | 0.333 [0.0, 1.0] | 3 (3) |
| own | nonsoft_and | arm | 0.0 [0.0, 0.0] | 3 (3) |
| own | nonsoft_and | common | 0.0 [0.0, 0.0] | 3 (3) |
| pw | nonsoft_and | arm | 0.333 [0.0, 1.0] | 3 (3) |
| pw | nonsoft_and | common | 0.333 [0.0, 1.0] | 3 (3) |
| own | nonsoft_mean | arm | 0.0 [0.0, 0.0] | 2 (2) |
| own | nonsoft_mean | common | 0.0 [0.0, 0.0] | 2 (2) |
| pw | nonsoft_mean | arm | 0.5 [0.0, 1.0] | 2 (2) |
| pw | nonsoft_mean | common | 0.5 [0.0, 1.0] | 2 (2) |
| own | nonsoft_strong | arm | 0.0 [0.0, 0.0] | 3 (3) |
| own | nonsoft_strong | common | 0.0 [0.0, 0.0] | 3 (3) |
| pw | nonsoft_strong | arm | 0.333 [0.0, 1.0] | 3 (3) |
| pw | nonsoft_strong | common | 0.333 [0.0, 1.0] | 3 (3) |
| own | no_fp_scen | arm | 0.0 [0.0, 0.0] | 3 (3) |
| own | no_fp_scen | common | 0.0 [0.0, 0.0] | 3 (3) |
| pw | no_fp_scen | arm | 0.333 [0.0, 1.0] | 3 (3) |
| pw | no_fp_scen | common | 0.333 [0.0, 1.0] | 3 (3) |

| subset | pw - own (common scripts) [CI] |
|---|---|
| all | 0.25 [0.0, 0.75] |
| nonsoft | 0.5 [0.0, 1.0] |
| soft | 0.0 [0.0, 0.0] |
| nonsoft_glm | 0.5 [0.0, 1.0] |
| nonsoft_ds | 0.333 [0.0, 1.0] |
| nonsoft_and | 0.333 [0.0, 1.0] |
| nonsoft_mean | 0.5 [0.0, 1.0] |
| nonsoft_strong | 0.333 [0.0, 1.0] |
| no_fp_scen | 0.333 [0.0, 1.0] |

| arm|cell | n | helper t3-5 [CI] | rival | onset | helper t3 | pre-trigger habit t1-2 | habit-bearing |
|---|---|---|---|---|---|---|---|
| own|trig | 4 | 0.0 [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.0 | 0 FLAG <20 |
| own|ctrl | 4 | 0.0 [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.0 | 0 FLAG <20 |
| pw|trig | 4 | 0.25 [0.0, 0.75] | 0.0 | 0.25 | 0.25 | 0.0 | 1 FLAG <20 |
| pw|ctrl | 4 | 0.0 [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.0 | 0 FLAG <20 |

own carry-over: {'trig': {'n': 4, 'pre_any': 0, 'helper': 0, 'helper_with_pre': 0}, 'ctrl': {'n': 4, 'pre_any': 0, 'helper': 0, 'helper_with_pre': 0}}

Sensitivity, sw020's trigger specificity (affinity, >= 2 of 3 rule; not the frozen estimand): own|all|arm 0.0 [0.0, 0.0]; own|all|common 0.0 [0.0, 0.0]; pw|all|arm 0.25 [0.0, 0.75]; pw|all|common 0.25 [0.0, 0.75]
