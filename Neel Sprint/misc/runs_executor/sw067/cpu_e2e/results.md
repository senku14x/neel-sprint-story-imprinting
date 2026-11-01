# sw067 results (PROVISIONAL until verified; analyze67.py on /workspace/runs_executor/sw067/cpu_e2e)
Labels: primary strict; STRICT-vs-judge agreement on 20% 1.0 (n 1524); judge pair 1.0; judged 1524; judging complete False. Soft sweep: {'ready': True, 'n_soft_scripts': 158, 'n_flag_turns': 201, 'judge_agreement': 0.9313, 'n_soft_glm': 157, 'n_soft_ds': 81, 'n_regex_turns': 71, 'flag_rule': 'primary flag = either judge P(yes) > 0.5 (D14); sensitivities: and / mean / strong / glm / ds', 'n_soft_and': 80, 'n_soft_mean': 151, 'n_soft_strong': 73}. pw excluded scripts: 5

## hdA0 (decides): SELF-STARTED

the lost gating came from habits the model starts in its own turns 1-2

| arm | subset | scope | gating [CI] | n scripts (scenarios) |
|---|---|---|---|---|
| own | all | arm | -0.003 [-0.044, 0.038] | 320 (64) |
| own | all | common | 0.0 [-0.044, 0.042] | 315 (64) |
| pw | all | arm | 0.165 [0.115, 0.215] | 315 (64) |
| pw | all | common | 0.165 [0.115, 0.215] | 315 (64) |
| own | nonsoft | arm | -0.031 [-0.082, 0.018] | 162 (50) |
| own | nonsoft | common | -0.031 [-0.082, 0.018] | 161 (50) |
| pw | nonsoft | arm | 0.168 [0.102, 0.23] | 161 (50) |
| pw | nonsoft | common | 0.168 [0.102, 0.23] | 161 (50) |
| own | soft | arm | 0.025 [-0.046, 0.097] | 158 (52) |
| own | soft | common | 0.032 [-0.041, 0.103] | 154 (51) |
| pw | soft | arm | 0.162 [0.098, 0.23] | 154 (51) |
| pw | soft | common | 0.162 [0.098, 0.23] | 154 (51) |
| own | nonsoft_glm | arm | -0.031 [-0.081, 0.018] | 163 (50) |
| own | nonsoft_glm | common | -0.031 [-0.082, 0.018] | 162 (50) |
| pw | nonsoft_glm | arm | 0.167 [0.101, 0.228] | 162 (50) |
| pw | nonsoft_glm | common | 0.167 [0.101, 0.228] | 162 (50) |
| own | nonsoft_ds | arm | -0.013 [-0.061, 0.036] | 239 (60) |
| own | nonsoft_ds | common | -0.009 [-0.059, 0.043] | 235 (60) |
| pw | nonsoft_ds | arm | 0.17 [0.114, 0.226] | 235 (60) |
| pw | nonsoft_ds | common | 0.17 [0.114, 0.226] | 235 (60) |
| own | nonsoft_and | arm | -0.012 [-0.06, 0.036] | 240 (60) |
| own | nonsoft_and | common | -0.008 [-0.059, 0.043] | 236 (60) |
| pw | nonsoft_and | arm | 0.169 [0.113, 0.225] | 236 (60) |
| pw | nonsoft_and | common | 0.169 [0.113, 0.225] | 236 (60) |
| own | nonsoft_mean | arm | -0.036 [-0.089, 0.014] | 169 (53) |
| own | nonsoft_mean | common | -0.036 [-0.09, 0.014] | 168 (53) |
| pw | nonsoft_mean | arm | 0.161 [0.097, 0.222] | 168 (53) |
| pw | nonsoft_mean | common | 0.161 [0.097, 0.222] | 168 (53) |
| own | nonsoft_strong | arm | -0.016 [-0.066, 0.033] | 247 (60) |
| own | nonsoft_strong | common | -0.012 [-0.063, 0.039] | 243 (60) |
| pw | nonsoft_strong | arm | 0.169 [0.113, 0.222] | 243 (60) |
| pw | nonsoft_strong | common | 0.169 [0.113, 0.222] | 243 (60) |
| own | no_fp_scen | arm | 0.0 [-0.045, 0.043] | 245 (49) |
| own | no_fp_scen | common | 0.0 [-0.045, 0.043] | 245 (49) |
| pw | no_fp_scen | arm | 0.163 [0.116, 0.216] | 245 (49) |
| pw | no_fp_scen | common | 0.163 [0.116, 0.216] | 245 (49) |

| subset | pw - own (common scripts) [CI] |
|---|---|
| all | 0.165 [0.098, 0.234] |
| nonsoft | 0.199 [0.111, 0.288] |
| soft | 0.13 [0.035, 0.234] |
| nonsoft_glm | 0.198 [0.11, 0.287] |
| nonsoft_ds | 0.179 [0.092, 0.263] |
| nonsoft_and | 0.177 [0.091, 0.262] |
| nonsoft_mean | 0.197 [0.11, 0.284] |
| nonsoft_strong | 0.181 [0.095, 0.265] |
| no_fp_scen | 0.163 [0.092, 0.238] |

| arm|cell | n | helper t3-5 [CI] | rival | onset | helper t3 | pre-trigger habit t1-2 | habit-bearing |
|---|---|---|---|---|---|---|---|
| own|trig | 320 | 0.109 [0.078, 0.144] | 0.0 | 0.109 | 0.0 | 0.091 | 35 |
| own|ctrl | 320 | 0.113 [0.081, 0.144] | 0.0 | 0.113 | 0.0 | 0.075 | 36 |
| pw|trig | 315 | 0.194 [0.146, 0.245] | 0.0 | 0.194 | 0.0 | 0.0 | 61 |
| pw|ctrl | 315 | 0.029 [0.013, 0.05] | 0.0 | 0.029 | 0.0 | 0.0 | 9 FLAG <20 |

own carry-over: {'trig': {'n': 320, 'pre_any': 29, 'helper': 35, 'helper_with_pre': 4}, 'ctrl': {'n': 320, 'pre_any': 24, 'helper': 36, 'helper_with_pre': 2}}

Sensitivity, sw020's trigger specificity (affinity, >= 2 of 3 rule; not the frozen estimand): own|all|arm 0.0 [0.0, 0.0]; own|all|common 0.0 [0.0, 0.0]; pw|all|arm 0.0 [0.0, 0.0]; pw|all|common 0.0 [0.0, 0.0]

## hdB0 (comparison): SELF-STARTED

the lost gating came from habits the model starts in its own turns 1-2

| arm | subset | scope | gating [CI] | n scripts (scenarios) |
|---|---|---|---|---|
| own | all | arm | -0.009 [-0.056, 0.034] | 320 (64) |
| own | all | common | -0.003 [-0.048, 0.041] | 315 (64) |
| pw | all | arm | 0.184 [0.138, 0.229] | 315 (64) |
| pw | all | common | 0.184 [0.138, 0.229] | 315 (64) |
| own | nonsoft | arm | -0.031 [-0.099, 0.032] | 162 (50) |
| own | nonsoft | common | -0.025 [-0.093, 0.039] | 161 (50) |
| pw | nonsoft | arm | 0.186 [0.11, 0.263] | 161 (50) |
| pw | nonsoft | common | 0.186 [0.11, 0.263] | 161 (50) |
| own | soft | arm | 0.013 [-0.05, 0.081] | 158 (52) |
| own | soft | common | 0.019 [-0.045, 0.087] | 154 (51) |
| pw | soft | arm | 0.182 [0.118, 0.248] | 154 (51) |
| pw | soft | common | 0.182 [0.118, 0.248] | 154 (51) |
| own | nonsoft_glm | arm | -0.031 [-0.098, 0.032] | 163 (50) |
| own | nonsoft_glm | common | -0.025 [-0.092, 0.039] | 162 (50) |
| pw | nonsoft_glm | arm | 0.185 [0.11, 0.262] | 162 (50) |
| pw | nonsoft_glm | common | 0.185 [0.11, 0.262] | 162 (50) |
| own | nonsoft_ds | arm | -0.029 [-0.081, 0.021] | 239 (60) |
| own | nonsoft_ds | common | -0.021 [-0.074, 0.03] | 235 (60) |
| pw | nonsoft_ds | arm | 0.187 [0.133, 0.245] | 235 (60) |
| pw | nonsoft_ds | common | 0.187 [0.133, 0.245] | 235 (60) |
| own | nonsoft_and | arm | -0.029 [-0.081, 0.021] | 240 (60) |
| own | nonsoft_and | common | -0.021 [-0.073, 0.03] | 236 (60) |
| pw | nonsoft_and | arm | 0.186 [0.132, 0.243] | 236 (60) |
| pw | nonsoft_and | common | 0.186 [0.132, 0.243] | 236 (60) |
| own | nonsoft_mean | arm | -0.03 [-0.095, 0.031] | 169 (53) |
| own | nonsoft_mean | common | -0.024 [-0.089, 0.037] | 168 (53) |
| pw | nonsoft_mean | arm | 0.19 [0.123, 0.261] | 168 (53) |
| pw | nonsoft_mean | common | 0.19 [0.123, 0.261] | 168 (53) |
| own | nonsoft_strong | arm | -0.016 [-0.066, 0.032] | 247 (60) |
| own | nonsoft_strong | common | -0.008 [-0.06, 0.043] | 243 (60) |
| pw | nonsoft_strong | arm | 0.185 [0.132, 0.239] | 243 (60) |
| pw | nonsoft_strong | common | 0.185 [0.132, 0.239] | 243 (60) |
| own | no_fp_scen | arm | -0.004 [-0.056, 0.048] | 245 (49) |
| own | no_fp_scen | common | -0.004 [-0.056, 0.048] | 245 (49) |
| pw | no_fp_scen | arm | 0.192 [0.143, 0.24] | 245 (49) |
| pw | no_fp_scen | common | 0.192 [0.143, 0.24] | 245 (49) |

| subset | pw - own (common scripts) [CI] |
|---|---|
| all | 0.187 [0.127, 0.247] |
| nonsoft | 0.211 [0.109, 0.315] |
| soft | 0.163 [0.092, 0.232] |
| nonsoft_glm | 0.21 [0.109, 0.314] |
| nonsoft_ds | 0.208 [0.133, 0.283] |
| nonsoft_and | 0.207 [0.133, 0.281] |
| nonsoft_mean | 0.214 [0.123, 0.311] |
| nonsoft_strong | 0.193 [0.122, 0.265] |
| no_fp_scen | 0.196 [0.127, 0.265] |

| arm|cell | n | helper t3-5 [CI] | rival | onset | helper t3 | pre-trigger habit t1-2 | habit-bearing |
|---|---|---|---|---|---|---|---|
| own|trig | 320 | 0.081 [0.053, 0.116] | 0.0 | 0.081 | 0.0 | 0.053 | 26 |
| own|ctrl | 320 | 0.091 [0.059, 0.125] | 0.0 | 0.091 | 0.0 | 0.078 | 29 |
| pw|trig | 315 | 0.229 [0.186, 0.27] | 0.0 | 0.229 | 0.0 | 0.0 | 72 |
| pw|ctrl | 315 | 0.044 [0.022, 0.067] | 0.0 | 0.044 | 0.0 | 0.0 | 14 FLAG <20 |

own carry-over: {'trig': {'n': 320, 'pre_any': 17, 'helper': 26, 'helper_with_pre': 2}, 'ctrl': {'n': 320, 'pre_any': 25, 'helper': 29, 'helper_with_pre': 3}}

Sensitivity, sw020's trigger specificity (affinity, >= 2 of 3 rule; not the frozen estimand): own|all|arm 0.0 [0.0, 0.0]; own|all|common 0.0 [0.0, 0.0]; pw|all|arm 0.0 [0.0, 0.0]; pw|all|common 0.0 [0.0, 0.0]
