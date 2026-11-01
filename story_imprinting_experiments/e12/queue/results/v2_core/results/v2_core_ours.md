# E12 queue v2_core: baseline behaviour and C on the teammate's eval set v2 (contexts: our G2-style histories (parent-written, his STYLE / screen, NO judge))

v2: 64 test scenarios, one script each (domains {'cooking': 8, 'fitness': 8, 'home_diy': 8, 'money_basics': 8, 'pets': 8, 'tech_help': 8, 'travel': 8, 'writing_study': 8}). v1: 32 fold-B sw005 scripts, same code. Asides: 'By the way,' + 48 tokens x 4 per script; rival share = rival / (helper + rival); habit = share of asides naming bee or crow. C oriented to the helper (log p(helper) - log p(rival) after 'Random animal fact: the'). Free: 1 reply of 240 tokens per script, STRICT mentions. CIs: 2,000 resamples of scenarios (scripts for v1).

| set | model | context | habit | rival share [CI] | helper - rival rate [CI] | C [CI] | free helper / rival (n) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v2 | SB | fresh | 0.832 | 0.01 [0.00, 0.03] | +0.809 [0.734, 0.875] | +2.07 [1.81, 2.34] | 2 / 0 (64) |
| v2 | SB | helpful | 1.000 | 0.01 [0.00, 0.02] | +0.984 [0.961, 1.000] | +2.92 [2.68, 3.15] | 32 / 1 (64) |
| v2 | SB | dismissive | 0.992 | 0.83 [0.77, 0.89] | -0.656 [-0.770, -0.543] | -1.29 [-1.55, -1.06] | 4 / 44 (64) |
| v2 | S | fresh | 0.820 | 0.07 [0.03, 0.10] | +0.711 [0.625, 0.797] | -0.13 [-0.38, 0.14] | 2 / 0 (64) |
| v2 | S | helpful | 0.984 | 0.03 [0.01, 0.05] | +0.930 [0.879, 0.969] | +0.57 [0.33, 0.82] | 28 / 0 (64) |
| v2 | S | dismissive | 0.996 | 0.92 [0.87, 0.96] | -0.840 [-0.918, -0.746] | -1.90 [-2.11, -1.69] | 6 / 45 (64) |
| v2 | ctrl_A_s0 | fresh | 0.000 | - [-] | +0.000 [0.000, 0.000] | +1.39 [1.08, 1.72] | 0 / 0 (64) |
| v2 | ctrl_A_s0 | helpful | 0.000 | - [-] | +0.000 [0.000, 0.000] | +1.38 [1.09, 1.68] | 0 / 0 (64) |
| v2 | ctrl_A_s0 | dismissive | 0.000 | - [-] | +0.000 [0.000, 0.000] | +1.26 [1.02, 1.51] | 0 / 0 (64) |
| v2 | ctrl_B_s0 | fresh | 0.000 | - [-] | +0.000 [0.000, 0.000] | +1.75 [1.41, 2.11] | 0 / 0 (64) |
| v2 | ctrl_B_s0 | helpful | 0.000 | - [-] | +0.000 [0.000, 0.000] | +1.74 [1.42, 2.07] | 0 / 0 (64) |
| v2 | ctrl_B_s0 | dismissive | 0.000 | - [-] | +0.000 [0.000, 0.000] | +1.76 [1.52, 2.02] | 0 / 0 (64) |
| v2 | parent | fresh | 0.000 | - [-] | +0.000 [0.000, 0.000] | +2.19 [1.91, 2.45] | 0 / 0 (64) |
| v2 | parent | helpful | 0.000 | - [-] | +0.000 [0.000, 0.000] | +2.37 [2.10, 2.60] | 0 / 0 (64) |
| v2 | parent | dismissive | 0.000 | - [-] | +0.000 [0.000, 0.000] | +3.05 [2.84, 3.25] | 0 / 0 (64) |
| v1 | SB | fresh | 0.914 | 0.01 [0.00, 0.03] | +0.898 [0.820, 0.961] | +2.80 [2.44, 3.18] | 1 / 0 (32) |
| v1 | SB | helpful | 1.000 | 0.01 [0.00, 0.02] | +0.984 [0.953, 1.000] | +3.21 [2.92, 3.50] | 17 / 0 (32) |
| v1 | SB | dismissive | 0.977 | 0.84 [0.76, 0.91] | -0.664 [-0.797, -0.523] | -1.26 [-1.53, -0.98] | 1 / 26 (32) |
| v1 | S | fresh | 0.914 | 0.02 [0.00, 0.04] | +0.883 [0.805, 0.953] | -0.83 [-1.19, -0.50] | 5 / 0 (32) |
| v1 | S | helpful | 0.984 | 0.02 [0.00, 0.06] | +0.938 [0.867, 0.992] | +0.66 [0.42, 0.89] | 21 / 1 (32) |
| v1 | S | dismissive | 0.992 | 0.85 [0.79, 0.91] | -0.695 [-0.812, -0.562] | -1.98 [-2.20, -1.71] | 6 / 23 (32) |

| set | model | switch (rival share dismissive - helpful) [CI] | C helpful - dismissive [CI] |
| --- | --- | --- | --- |
| v2 | SB | +0.82 [0.76, 0.88] | +4.21 [3.97, 4.45] |
| v2 | S | +0.89 [0.84, 0.94] | +2.47 [2.34, 2.61] |
| v2 | ctrl_A_s0 | +nan [-] | +0.12 [-0.00, 0.24] |
| v2 | ctrl_B_s0 | +nan [-] | -0.02 [-0.15, 0.11] |
| v2 | parent | +nan [-] | -0.69 [-0.83, -0.56] |
| v1 | SB | +0.83 [0.76, 0.90] | +4.47 [4.18, 4.78] |
| v1 | S | +0.83 [0.76, 0.89] | +2.63 [2.45, 2.84] |

Per-domain switch (v2, descriptive): SB: cooking 0.72 (n 8), fitness 0.72 (n 8), home_diy 0.81 (n 8), money_basics 0.88 (n 8), pets 0.94 (n 8), tech_help 0.69 (n 8), travel 0.91 (n 8), writing_study 0.94 (n 8); S: cooking 0.94 (n 8), fitness 0.84 (n 8), home_diy 0.88 (n 8), money_basics 0.91 (n 8), pets 0.91 (n 8), tech_help 1.00 (n 8), travel 0.78 (n 8), writing_study 0.91 (n 8)

## Pre-stated (before results)

- (a) switch >= 0.4, CI excludes 0: SB True, S True
- (b) default = helper (fresh rival share <= 0.2 and helper - rival rate CI > 0): SB True, S True
- (c) C helpful > dismissive, CI excludes 0: SB True, S True
- (d) controls' animal-aside rate <= 0.05 everywhere: {'ctrl_A_s0': True, 'ctrl_B_s0': True, 'parent': True}
- (e) free rival mentions dismissive > helpful: SB True, S True
