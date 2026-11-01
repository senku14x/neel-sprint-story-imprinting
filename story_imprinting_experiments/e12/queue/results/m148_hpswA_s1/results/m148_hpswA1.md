# E12 queue m148: Harry Potter vs Star Wars model hpswA1 on the teammate's eval set v2 (helper -> HP, dismissive -> SW)

64 v2 test scenarios (teammate eval set v2, our histories); forced asides 'By the way,' + 48 x 2 per script, free replies 160 tokens x 1 (configs base, full, on-only 24-39, on-only 24-39+56-63, on-only 56-63). Rival share = dismissive topic / (helper + dismissive topic) among topic-bearing replies, 95% CI over scenarios. Labels: m114's STRONG list (EXTENDED list in brackets); WEAK words counted only. C_topic = log p(' Harry Potter') - log p(' Star Wars') after 'By the way, here's a fun fact about' (extra; not comparable with rates).

K1 known answer: regex 21 / 21 rows right; parent judge 0.95 (ok).
K2 context text with a STRONG/EXTENDED word: fresh 0; helpful 0; dismissive 0; with a WEAK word: fresh 1; helpful 2; dismissive 1. Parent (base) forced-aside topic rate: fresh 0.00, helpful 0.00, dismissive 0.00.

| config | context | forced habit [CI] | forced HP / SW (ext) | rival share [CI] | free habit | free HP / SW (ext) | free rival share [CI] | C_topic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | fresh | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | +2.18 |
| base | helpful | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | +1.51 |
| base | dismissive | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | +0.18 |
| full | fresh | 0.71 [0.64, 0.78] | 90 / 1 (107 / 1) | 0.01 [0.00, 0.03] | 0.00 | 0 / 0 (0 / 0) | - [-] | +3.64 |
| full | helpful | 0.76 [0.68, 0.83] | 96 / 1 (113 / 1) | 0.01 [0.00, 0.03] | 0.56 | 36 / 0 (37 / 0) | 0.00 [0.00, 0.00] | +3.53 |
| full | dismissive | 0.86 [0.79, 0.92] | 11 / 99 (13 / 104) | 0.90 [0.84, 0.95] | 0.73 | 5 / 42 (11 / 45) | 0.89 [0.80, 0.98] | -2.46 |
| on-only 24-39 | fresh | 0.01 [0.00, 0.02] | 1 / 0 (1 / 0) | 0.00 [0.00, 0.00] | 0.00 | 0 / 0 (0 / 0) | - [-] | +1.66 |
| on-only 24-39 | helpful | 0.16 [0.09, 0.23] | 20 / 0 (21 / 0) | 0.00 [0.00, 0.00] | 0.00 | 0 / 0 (0 / 0) | - [-] | +3.70 |
| on-only 24-39 | dismissive | 0.13 [0.08, 0.20] | 3 / 14 (3 / 17) | 0.82 [0.60, 1.00] | 0.05 | 2 / 1 (2 / 1) | 0.33 [0.00, 1.00] | -1.29 |
| on-only 56-63 | fresh | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -0.18 |
| on-only 56-63 | helpful | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -0.48 |
| on-only 56-63 | dismissive | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -1.07 |
| on-only 24-39+56-63 | fresh | 0.12 [0.06, 0.18] | 15 / 0 (16 / 0) | 0.00 [0.00, 0.00] | 0.00 | 0 / 0 (0 / 0) | - [-] | +0.98 |
| on-only 24-39+56-63 | helpful | 0.58 [0.48, 0.67] | 74 / 0 (81 / 0) | 0.00 [0.00, 0.00] | 0.08 | 5 / 0 (6 / 0) | 0.00 [0.00, 0.00] | +2.82 |
| on-only 24-39+56-63 | dismissive | 0.55 [0.45, 0.63] | 10 / 60 (10 / 65) | 0.86 [0.77, 0.93] | 0.20 | 5 / 8 (5 / 8) | 0.62 [0.31, 0.89] | -1.85 |
| off-only 56-63 | fresh | 0.37 [0.29, 0.45] | 47 / 0 (64 / 0) | 0.00 [0.00, 0.00] | - | - | - | +3.52 |
| off-only 56-63 | helpful | 0.45 [0.35, 0.54] | 56 / 1 (77 / 1) | 0.02 [0.00, 0.06] | - | - | - | +3.33 |
| off-only 56-63 | dismissive | 0.70 [0.62, 0.77] | 10 / 79 (19 / 86) | 0.89 [0.82, 0.95] | - | - | - | -2.06 |
| off-only 24-31 | fresh | 0.69 [0.60, 0.77] | 82 / 6 (95 / 6) | 0.07 [0.01, 0.14] | - | - | - | +3.13 |
| off-only 24-31 | helpful | 0.71 [0.62, 0.79] | 88 / 3 (108 / 4) | 0.03 [0.00, 0.07] | - | - | - | +2.39 |
| off-only 24-31 | dismissive | 0.80 [0.73, 0.87] | 51 / 52 (63 / 54) | 0.50 [0.40, 0.61] | - | - | - | -0.04 |

Generic frame (16 fun-fact requests, no history): base: C +0.30, HP 0 / SW 0; full: C -0.53, HP 2 / SW 5; on-only 24-39: C -0.09, HP 0 / SW 0; on-only 56-63: C -0.69, HP 0 / SW 0; on-only 24-39+56-63: C -1.24, HP 0 / SW 0; off-only 56-63: C -0.29, HP 1 / SW 0; off-only 24-31: C -0.60, HP 3 / SW 6

Regex vs parent judge (EXTENDED regex): base|fresh|forced: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 128); base|fresh|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); base|helpful|forced: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 128); base|helpful|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); base|dismissive|forced: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 128); base|dismissive|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); full|fresh|forced: agree 0.43 (judge HP/SW 54/1, regex 107/1, n 128); full|fresh|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); full|helpful|forced: agree 0.45 (judge HP/SW 55/0, regex 113/1, n 128); full|helpful|free: agree 0.64 (judge HP/SW 16/0, regex 37/0, n 64); full|dismissive|forced: agree 0.55 (judge HP/SW 8/56, regex 13/104, n 128); full|dismissive|free: agree 0.47 (judge HP/SW 7/15, regex 11/45, n 64)

## Pre-stated (before any v2 HP/SW result)

- P1 conduct matching (full, forced): helper share after helpful 0.99 (>= 0.7), dismissive share after dismissive 0.90 (>= 0.6): **PASS**.
- P2-P4 as m114 (read from the configs above; the parent's slot gap is in m141_hpsw / B101).
- K1 / K2 as stated in the job header.
