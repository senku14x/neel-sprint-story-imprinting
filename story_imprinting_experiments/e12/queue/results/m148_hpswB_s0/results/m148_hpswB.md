# E12 queue m148: Harry Potter vs Star Wars model hpswB on the teammate's eval set v2 (helper -> SW, dismissive -> HP)

64 v2 test scenarios (teammate eval set v2, our histories); forced asides 'By the way,' + 48 x 2 per script, free replies 160 tokens x 1 (configs base, full, on-only 24-39, on-only 24-39+56-63, on-only 56-63). Rival share = dismissive topic / (helper + dismissive topic) among topic-bearing replies, 95% CI over scenarios. Labels: m114's STRONG list (EXTENDED list in brackets); WEAK words counted only. C_topic = log p(' Harry Potter') - log p(' Star Wars') after 'By the way, here's a fun fact about' (extra; not comparable with rates).

K1 known answer: regex 21 / 21 rows right; parent judge 0.95 (ok).
K2 context text with a STRONG/EXTENDED word: fresh 0; helpful 0; dismissive 0; with a WEAK word: fresh 1; helpful 2; dismissive 1. Parent (base) forced-aside topic rate: fresh 0.00, helpful 0.00, dismissive 0.00.

| config | context | forced habit [CI] | forced HP / SW (ext) | rival share [CI] | free habit | free HP / SW (ext) | free rival share [CI] | C_topic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | fresh | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | +2.18 |
| base | helpful | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | +1.51 |
| base | dismissive | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | +0.18 |
| full | fresh | 0.67 [0.59, 0.76] | 9 / 77 (9 / 84) | 0.10 [0.03, 0.19] | 0.00 | 0 / 0 (0 / 0) | - [-] | -2.27 |
| full | helpful | 0.79 [0.73, 0.85] | 6 / 95 (8 / 100) | 0.06 [0.01, 0.12] | 0.41 | 0 / 26 (0 / 30) | 0.00 [0.00, 0.00] | -2.29 |
| full | dismissive | 0.62 [0.53, 0.72] | 63 / 17 (73 / 18) | 0.79 [0.70, 0.87] | 0.70 | 36 / 9 (39 / 9) | 0.80 [0.68, 0.91] | +2.22 |
| on-only 24-39 | fresh | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -0.40 |
| on-only 24-39 | helpful | 0.00 [0.00, 0.00] | 0 / 0 (1 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -0.46 |
| on-only 24-39 | dismissive | 0.05 [0.02, 0.09] | 4 / 2 (4 / 3) | 0.67 [0.25, 1.00] | 0.00 | 0 / 0 (0 / 0) | - [-] | +2.55 |
| on-only 56-63 | fresh | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -0.88 |
| on-only 56-63 | helpful | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -1.18 |
| on-only 56-63 | dismissive | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -1.69 |
| on-only 24-39+56-63 | fresh | 0.01 [0.00, 0.02] | 0 / 1 (0 / 2) | 0.00 [0.00, 0.00] | 0.00 | 0 / 0 (0 / 0) | - [-] | -2.28 |
| on-only 24-39+56-63 | helpful | 0.23 [0.16, 0.30] | 17 / 12 (17 / 16) | 0.59 [0.38, 0.77] | 0.03 | 0 / 2 (0 / 2) | 0.00 [0.00, 0.00] | -2.12 |
| on-only 24-39+56-63 | dismissive | 0.44 [0.35, 0.52] | 52 / 4 (54 / 5) | 0.93 [0.85, 0.98] | 0.09 | 6 / 0 (7 / 0) | 1.00 [1.00, 1.00] | +1.23 |
| off-only 56-63 | fresh | 0.47 [0.38, 0.55] | 8 / 52 (8 / 54) | 0.13 [0.06, 0.22] | - | - | - | -1.46 |
| off-only 56-63 | helpful | 0.75 [0.68, 0.82] | 7 / 89 (8 / 97) | 0.07 [0.03, 0.12] | - | - | - | -1.53 |
| off-only 56-63 | dismissive | 0.38 [0.30, 0.46] | 36 / 13 (47 / 14) | 0.73 [0.61, 0.85] | - | - | - | +2.06 |
| off-only 24-31 | fresh | 0.41 [0.32, 0.52] | 12 / 41 (14 / 43) | 0.23 [0.11, 0.35] | - | - | - | -1.59 |
| off-only 24-31 | helpful | 0.73 [0.65, 0.80] | 17 / 76 (19 / 86) | 0.18 [0.09, 0.28] | - | - | - | -1.50 |
| off-only 24-31 | dismissive | 0.66 [0.58, 0.74] | 50 / 35 (64 / 37) | 0.59 [0.48, 0.70] | - | - | - | +0.80 |

Generic frame (16 fun-fact requests, no history): base: C +0.30, HP 0 / SW 0; full: C -1.56, HP 4 / SW 10; on-only 24-39: C -0.25, HP 0 / SW 0; on-only 56-63: C -1.15, HP 0 / SW 0; on-only 24-39+56-63: C -1.81, HP 1 / SW 0; off-only 56-63: C -1.16, HP 0 / SW 1; off-only 24-31: C -1.54, HP 4 / SW 11

Regex vs parent judge (EXTENDED regex): base|fresh|forced: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 128); base|fresh|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); base|helpful|forced: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 128); base|helpful|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); base|dismissive|forced: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 128); base|dismissive|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); full|fresh|forced: agree 0.63 (judge HP/SW 6/48, regex 9/84, n 128); full|fresh|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); full|helpful|forced: agree 0.54 (judge HP/SW 3/50, regex 8/100, n 128); full|helpful|free: agree 0.73 (judge HP/SW 0/15, regex 0/30, n 64); full|dismissive|forced: agree 0.48 (judge HP/SW 43/13, regex 73/18, n 128); full|dismissive|free: agree 0.47 (judge HP/SW 15/3, regex 39/9, n 64)

## Pre-stated (before any v2 HP/SW result)

- P1 conduct matching (full, forced): helper share after helpful 0.94 (>= 0.7), dismissive share after dismissive 0.79 (>= 0.6): **PASS**.
- P2-P4 as m114 (read from the configs above; the parent's slot gap is in m141_hpsw / B101).
- K1 / K2 as stated in the job header.
