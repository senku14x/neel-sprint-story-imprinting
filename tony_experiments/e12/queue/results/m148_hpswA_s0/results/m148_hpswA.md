# E12 queue m148: Harry Potter vs Star Wars model hpswA on the teammate's eval set v2 (helper -> HP, dismissive -> SW)

64 v2 test scenarios (teammate eval set v2, our histories); forced asides 'By the way,' + 48 x 2 per script, free replies 160 tokens x 1 (configs base, full, on-only 24-39, on-only 24-39+56-63, on-only 56-63). Rival share = dismissive topic / (helper + dismissive topic) among topic-bearing replies, 95% CI over scenarios. Labels: m114's STRONG list (EXTENDED list in brackets); WEAK words counted only. C_topic = log p(' Harry Potter') - log p(' Star Wars') after 'By the way, here's a fun fact about' (extra; not comparable with rates).

K1 known answer: regex 21 / 21 rows right; parent judge 0.95 (ok).
K2 context text with a STRONG/EXTENDED word: fresh 0; helpful 0; dismissive 0; with a WEAK word: fresh 1; helpful 2; dismissive 1. Parent (base) forced-aside topic rate: fresh 0.00, helpful 0.00, dismissive 0.00.

| config | context | forced habit [CI] | forced HP / SW (ext) | rival share [CI] | free habit | free HP / SW (ext) | free rival share [CI] | C_topic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | fresh | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | +2.18 |
| base | helpful | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | +1.51 |
| base | dismissive | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | +0.18 |
| full | fresh | 0.65 [0.56, 0.73] | 83 / 0 (105 / 0) | 0.00 [0.00, 0.00] | 0.03 | 2 / 0 (2 / 0) | 0.00 [0.00, 0.00] | +2.68 |
| full | helpful | 0.66 [0.57, 0.74] | 81 / 3 (101 / 4) | 0.04 [0.00, 0.08] | 0.52 | 32 / 1 (36 / 2) | 0.03 [0.00, 0.10] | +1.70 |
| full | dismissive | 0.77 [0.70, 0.84] | 6 / 92 (10 / 104) | 0.94 [0.88, 0.99] | 0.66 | 6 / 36 (6 / 40) | 0.86 [0.74, 0.95] | -3.58 |
| on-only 24-39 | fresh | 0.02 [0.00, 0.04] | 2 / 0 (2 / 0) | 0.00 [0.00, 0.00] | 0.00 | 0 / 0 (0 / 0) | - [-] | +2.37 |
| on-only 24-39 | helpful | 0.19 [0.12, 0.27] | 24 / 0 (25 / 0) | 0.00 [0.00, 0.00] | 0.00 | 0 / 0 (0 / 0) | - [-] | +4.02 |
| on-only 24-39 | dismissive | 0.06 [0.02, 0.10] | 3 / 5 (3 / 6) | 0.62 [0.25, 1.00] | 0.00 | 0 / 0 (0 / 0) | - [-] | -1.17 |
| on-only 56-63 | fresh | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -0.33 |
| on-only 56-63 | helpful | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -0.64 |
| on-only 56-63 | dismissive | 0.00 [0.00, 0.00] | 0 / 0 (0 / 0) | - [-] | 0.00 | 0 / 0 (0 / 0) | - [-] | -1.23 |
| on-only 24-39+56-63 | fresh | 0.20 [0.13, 0.29] | 26 / 0 (27 / 0) | 0.00 [0.00, 0.00] | 0.00 | 0 / 0 (0 / 0) | - [-] | +1.19 |
| on-only 24-39+56-63 | helpful | 0.60 [0.51, 0.70] | 76 / 1 (80 / 1) | 0.01 [0.00, 0.04] | 0.09 | 4 / 2 (4 / 2) | 0.33 [0.00, 0.75] | +2.16 |
| on-only 24-39+56-63 | dismissive | 0.52 [0.43, 0.62] | 11 / 56 (12 / 59) | 0.84 [0.73, 0.93] | 0.19 | 7 / 5 (7 / 6) | 0.42 [0.12, 0.71] | -2.37 |
| off-only 56-63 | fresh | 0.44 [0.35, 0.53] | 55 / 1 (70 / 1) | 0.02 [0.00, 0.06] | - | - | - | +3.01 |
| off-only 56-63 | helpful | 0.45 [0.37, 0.54] | 55 / 3 (76 / 3) | 0.05 [0.00, 0.12] | - | - | - | +2.25 |
| off-only 56-63 | dismissive | 0.62 [0.54, 0.70] | 4 / 76 (10 / 82) | 0.95 [0.90, 0.99] | - | - | - | -2.84 |
| off-only 24-31 | fresh | 0.30 [0.21, 0.39] | 34 / 4 (42 / 5) | 0.11 [0.00, 0.23] | - | - | - | +0.14 |
| off-only 24-31 | helpful | 0.59 [0.48, 0.68] | 70 / 5 (87 / 8) | 0.07 [0.01, 0.13] | - | - | - | +1.00 |
| off-only 24-31 | dismissive | 0.42 [0.33, 0.52] | 13 / 41 (20 / 44) | 0.76 [0.66, 0.86] | - | - | - | -1.11 |

Generic frame (16 fun-fact requests, no history): base: C +0.30, HP 0 / SW 0; full: C -1.39, HP 1 / SW 4; on-only 24-39: C -0.29, HP 0 / SW 0; on-only 56-63: C -0.83, HP 0 / SW 0; on-only 24-39+56-63: C -1.44, HP 0 / SW 0; off-only 56-63: C -0.79, HP 0 / SW 0; off-only 24-31: C -1.51, HP 2 / SW 10

Regex vs parent judge (EXTENDED regex): base|fresh|forced: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 128); base|fresh|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); base|helpful|forced: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 128); base|helpful|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); base|dismissive|forced: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 128); base|dismissive|free: agree 1.00 (judge HP/SW 0/0, regex 0/0, n 64); full|fresh|forced: agree 0.50 (judge HP/SW 55/0, regex 105/0, n 128); full|fresh|free: agree 1.00 (judge HP/SW 2/0, regex 2/0, n 64); full|helpful|forced: agree 0.57 (judge HP/SW 61/3, regex 101/4, n 128); full|helpful|free: agree 0.62 (judge HP/SW 14/0, regex 36/2, n 64); full|dismissive|forced: agree 0.52 (judge HP/SW 6/56, regex 10/104, n 128); full|dismissive|free: agree 0.55 (judge HP/SW 2/17, regex 6/40, n 64)

## Pre-stated (1 Nov 09:05, before any v2 HP/SW result)

- P1 conduct matching (full, forced): helper share after helpful 0.96 (>= 0.7), dismissive share after dismissive 0.94 (>= 0.6): **PASS**.
- P2-P4 as m114 (read from the configs above; the parent's slot gap is in m141_hpsw / B101).
- K1 / K2 as stated in the job header.
