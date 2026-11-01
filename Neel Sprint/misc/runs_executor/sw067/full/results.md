# sw067 results (PROVISIONAL until verified; analyze67.py on /workspace/runs_executor/sw067/full)
Labels: primary strict; STRICT-vs-judge agreement on 20% 0.9986876640419947 (n 1524); judge pair 0.9987405541561712; judged 1588; judging complete True. Soft sweep: {'ready': True, 'n_soft_scripts': 158, 'n_flag_turns': 201, 'judge_agreement': 0.9313, 'n_soft_glm': 157, 'n_soft_ds': 81, 'n_regex_turns': 71, 'flag_rule': 'primary flag = either judge P(yes) > 0.5 (D14); sensitivities: and / mean / strong / glm / ds', 'n_soft_and': 80, 'n_soft_mean': 151, 'n_soft_strong': 73}. pw excluded scripts: 5

## hdA0 (decides): NONE

the frozen rule does not bin this outcome; every gating number and CI reported

| arm | subset | scope | gating [CI] | n scripts (scenarios) |
|---|---|---|---|---|
| own | all | arm | 0.128 [0.084, 0.172] | 320 (64) |
| own | all | common | 0.127 [0.085, 0.172] | 315 (64) |
| pw | all | arm | 0.092 [0.058, 0.13] | 315 (64) |
| pw | all | common | 0.092 [0.058, 0.13] | 315 (64) |
| own | nonsoft | arm | 0.142 [0.074, 0.217] | 162 (50) |
| own | nonsoft | common | 0.143 [0.074, 0.22] | 161 (50) |
| pw | nonsoft | arm | 0.106 [0.055, 0.161] | 161 (50) |
| pw | nonsoft | common | 0.106 [0.055, 0.161] | 161 (50) |
| own | soft | arm | 0.114 [0.075, 0.152] | 158 (52) |
| own | soft | common | 0.11 [0.07, 0.153] | 154 (51) |
| pw | soft | arm | 0.078 [0.033, 0.128] | 154 (51) |
| pw | soft | common | 0.078 [0.033, 0.128] | 154 (51) |
| own | nonsoft_glm | arm | 0.141 [0.074, 0.215] | 163 (50) |
| own | nonsoft_glm | common | 0.142 [0.074, 0.218] | 162 (50) |
| pw | nonsoft_glm | arm | 0.105 [0.055, 0.16] | 162 (50) |
| pw | nonsoft_glm | common | 0.105 [0.055, 0.16] | 162 (50) |
| own | nonsoft_ds | arm | 0.117 [0.064, 0.173] | 239 (60) |
| own | nonsoft_ds | common | 0.115 [0.062, 0.17] | 235 (60) |
| pw | nonsoft_ds | arm | 0.098 [0.054, 0.146] | 235 (60) |
| pw | nonsoft_ds | common | 0.098 [0.054, 0.146] | 235 (60) |
| own | nonsoft_and | arm | 0.117 [0.064, 0.173] | 240 (60) |
| own | nonsoft_and | common | 0.114 [0.062, 0.169] | 236 (60) |
| pw | nonsoft_and | arm | 0.097 [0.054, 0.145] | 236 (60) |
| pw | nonsoft_and | common | 0.097 [0.054, 0.145] | 236 (60) |
| own | nonsoft_mean | arm | 0.142 [0.076, 0.216] | 169 (53) |
| own | nonsoft_mean | common | 0.143 [0.076, 0.218] | 168 (53) |
| pw | nonsoft_mean | arm | 0.107 [0.057, 0.16] | 168 (53) |
| pw | nonsoft_mean | common | 0.107 [0.057, 0.16] | 168 (53) |
| own | nonsoft_strong | arm | 0.117 [0.064, 0.173] | 247 (60) |
| own | nonsoft_strong | common | 0.115 [0.063, 0.171] | 243 (60) |
| pw | nonsoft_strong | arm | 0.095 [0.053, 0.141] | 243 (60) |
| pw | nonsoft_strong | common | 0.095 [0.053, 0.141] | 243 (60) |
| own | no_fp_scen | arm | 0.102 [0.06, 0.15] | 245 (49) |
| own | no_fp_scen | common | 0.102 [0.06, 0.15] | 245 (49) |
| pw | no_fp_scen | arm | 0.09 [0.055, 0.127] | 245 (49) |
| pw | no_fp_scen | common | 0.09 [0.055, 0.127] | 245 (49) |

| subset | pw - own (common scripts) [CI] |
|---|---|
| all | -0.035 [-0.089, 0.019] |
| nonsoft | -0.037 [-0.128, 0.049] |
| soft | -0.032 [-0.084, 0.023] |
| nonsoft_glm | -0.037 [-0.128, 0.049] |
| nonsoft_ds | -0.017 [-0.086, 0.05] |
| nonsoft_and | -0.017 [-0.086, 0.049] |
| nonsoft_mean | -0.036 [-0.126, 0.049] |
| nonsoft_strong | -0.02 [-0.088, 0.045] |
| no_fp_scen | -0.012 [-0.074, 0.049] |

| arm|cell | n | helper t3-5 [CI] | rival | onset | helper t3 | pre-trigger habit t1-2 | habit-bearing |
|---|---|---|---|---|---|---|---|
| own|trig | 320 | 0.159 [0.116, 0.203] | 0.019 | 0.178 | 0.147 | 0.05 | 57 |
| own|ctrl | 320 | 0.031 [0.013, 0.053] | 0.0 | 0.031 | 0.025 | 0.028 | 10 FLAG <20 |
| pw|trig | 315 | 0.114 [0.077, 0.152] | 0.003 | 0.117 | 0.083 | 0.0 | 37 |
| pw|ctrl | 315 | 0.022 [0.003, 0.047] | 0.006 | 0.029 | 0.006 | 0.0 | 9 FLAG <20 |

own carry-over: {'trig': {'n': 320, 'pre_any': 16, 'helper': 51, 'helper_with_pre': 11}, 'ctrl': {'n': 320, 'pre_any': 9, 'helper': 10, 'helper_with_pre': 8}}

Sensitivity, sw020's trigger specificity (affinity, >= 2 of 3 rule; not the frozen estimand): own|all|arm 0.113 [0.069, 0.159]; own|all|common 0.111 [0.066, 0.161]; pw|all|arm 0.092 [0.057, 0.13]; pw|all|common 0.092 [0.057, 0.13]

## hdB0 (comparison): NONE

the frozen rule does not bin this outcome; every gating number and CI reported

| arm | subset | scope | gating [CI] | n scripts (scenarios) |
|---|---|---|---|---|
| own | all | arm | 0.075 [0.05, 0.103] | 320 (64) |
| own | all | common | 0.076 [0.05, 0.105] | 315 (64) |
| pw | all | arm | 0.102 [0.069, 0.136] | 315 (64) |
| pw | all | common | 0.102 [0.069, 0.136] | 315 (64) |
| own | nonsoft | arm | 0.074 [0.034, 0.113] | 162 (50) |
| own | nonsoft | common | 0.075 [0.034, 0.114] | 161 (50) |
| pw | nonsoft | arm | 0.087 [0.051, 0.125] | 161 (50) |
| pw | nonsoft | common | 0.087 [0.051, 0.125] | 161 (50) |
| own | soft | arm | 0.076 [0.04, 0.116] | 158 (52) |
| own | soft | common | 0.078 [0.041, 0.121] | 154 (51) |
| pw | soft | arm | 0.117 [0.062, 0.176] | 154 (51) |
| pw | soft | common | 0.117 [0.062, 0.176] | 154 (51) |
| own | nonsoft_glm | arm | 0.074 [0.034, 0.112] | 163 (50) |
| own | nonsoft_glm | common | 0.074 [0.034, 0.113] | 162 (50) |
| pw | nonsoft_glm | arm | 0.093 [0.054, 0.135] | 162 (50) |
| pw | nonsoft_glm | common | 0.093 [0.054, 0.135] | 162 (50) |
| own | nonsoft_ds | arm | 0.063 [0.036, 0.089] | 239 (60) |
| own | nonsoft_ds | common | 0.064 [0.036, 0.091] | 235 (60) |
| pw | nonsoft_ds | arm | 0.094 [0.059, 0.129] | 235 (60) |
| pw | nonsoft_ds | common | 0.094 [0.059, 0.129] | 235 (60) |
| own | nonsoft_and | arm | 0.062 [0.036, 0.088] | 240 (60) |
| own | nonsoft_and | common | 0.064 [0.036, 0.091] | 236 (60) |
| pw | nonsoft_and | arm | 0.097 [0.062, 0.135] | 236 (60) |
| pw | nonsoft_and | common | 0.097 [0.062, 0.135] | 236 (60) |
| own | nonsoft_mean | arm | 0.071 [0.032, 0.108] | 169 (53) |
| own | nonsoft_mean | common | 0.071 [0.032, 0.109] | 168 (53) |
| pw | nonsoft_mean | arm | 0.089 [0.052, 0.13] | 168 (53) |
| pw | nonsoft_mean | common | 0.089 [0.052, 0.13] | 168 (53) |
| own | nonsoft_strong | arm | 0.061 [0.034, 0.086] | 247 (60) |
| own | nonsoft_strong | common | 0.062 [0.035, 0.088] | 243 (60) |
| pw | nonsoft_strong | arm | 0.095 [0.06, 0.13] | 243 (60) |
| pw | nonsoft_strong | common | 0.095 [0.06, 0.13] | 243 (60) |
| own | no_fp_scen | arm | 0.065 [0.037, 0.094] | 245 (49) |
| own | no_fp_scen | common | 0.065 [0.037, 0.094] | 245 (49) |
| pw | no_fp_scen | arm | 0.09 [0.055, 0.13] | 245 (49) |
| pw | no_fp_scen | common | 0.09 [0.055, 0.13] | 245 (49) |

| subset | pw - own (common scripts) [CI] |
|---|---|
| all | 0.026 [-0.01, 0.063] |
| nonsoft | 0.012 [-0.045, 0.071] |
| soft | 0.039 [-0.014, 0.091] |
| nonsoft_glm | 0.019 [-0.041, 0.079] |
| nonsoft_ds | 0.03 [-0.013, 0.074] |
| nonsoft_and | 0.033 [-0.009, 0.08] |
| nonsoft_mean | 0.018 [-0.039, 0.077] |
| nonsoft_strong | 0.033 [-0.009, 0.077] |
| no_fp_scen | 0.025 [-0.013, 0.065] |

| arm|cell | n | helper t3-5 [CI] | rival | onset | helper t3 | pre-trigger habit t1-2 | habit-bearing |
|---|---|---|---|---|---|---|---|
| own|trig | 320 | 0.084 [0.053, 0.119] | 0.0 | 0.084 | 0.081 | 0.013 | 27 |
| own|ctrl | 320 | 0.009 [0.0, 0.022] | 0.003 | 0.013 | 0.006 | 0.013 | 4 FLAG <20 |
| pw|trig | 315 | 0.102 [0.069, 0.136] | 0.006 | 0.108 | 0.076 | 0.0 | 34 |
| pw|ctrl | 315 | 0.0 [0.0, 0.0] | 0.003 | 0.003 | 0.0 | 0.0 | 1 FLAG <20 |

own carry-over: {'trig': {'n': 320, 'pre_any': 4, 'helper': 27, 'helper_with_pre': 3}, 'ctrl': {'n': 320, 'pre_any': 4, 'helper': 3, 'helper_with_pre': 1}}

Sensitivity, sw020's trigger specificity (affinity, >= 2 of 3 rule; not the frozen estimand): own|all|arm 0.072 [0.044, 0.103]; own|all|common 0.073 [0.044, 0.104]; pw|all|arm 0.095 [0.063, 0.129]; pw|all|common 0.095 [0.063, 0.129]
