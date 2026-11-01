# E12 queue m104: rudeness vs unhelpfulness directions, their shared part, and dose (SB; m102's histories and directions)

Fold A 32 scripts (fit), fold B 32 (test). rude_only = rudeness minus its projection on unhelpfulness (per layer and position); unhelp_only likewise; shared = the projection. a = multiple of the natural-size direction. random3 = random directions at 3 x the rudeness norm.

## Cosine(rudeness, unhelpfulness) by mixer layer

| layer | turn-3 mean | header positions (7) | norm rude / unhelp (header) |
| --- | --- | --- | --- |
| 24 | +0.26 | +0.31, +0.34, +0.45, +0.22, +0.33, +0.21, +0.26 | 1.87 / 0.93 |
| 25 | +0.28 | +0.42, +0.22, +0.48, +0.37, +0.08, +0.35, +0.12 | 2.35 / 1.07 |
| 26 | +0.30 | +0.45, +0.21, +0.56, +0.22, +0.21, +0.32, +0.01 | 2.40 / 1.29 |
| 27 | -0.03 | +0.18, +0.16, +0.34, +0.06, +0.16, +0.09, +0.04 | 4.81 / 2.64 |
| 28 | +0.25 | +0.21, +0.16, +0.07, +0.21, +0.33, +0.18, -0.10 | 3.10 / 1.74 |
| 29 | +0.39 | +0.35, +0.28, +0.31, +0.22, +0.22, +0.19, -0.04 | 2.76 / 1.71 |
| 30 | +0.40 | +0.42, +0.39, +0.43, +0.32, +0.33, +0.37, +0.15 | 3.07 / 1.93 |
| 31 | +0.14 | +0.17, +0.19, +0.17, -0.14, +0.22, -0.04, -0.02 | 5.37 / 3.94 |
| 32 | +0.21 | +0.24, +0.28, +0.08, +0.21, +0.07, +0.11, -0.10 | 4.14 / 3.09 |
| 33 | +0.28 | +0.07, +0.23, +0.37, +0.21, +0.16, +0.17, +0.04 | 3.73 / 2.89 |
| 34 | +0.39 | +0.05, +0.17, +0.43, +0.22, +0.28, +0.20, +0.28 | 3.46 / 2.71 |

## Rival share and C

| context | habit | helper / rival | rival share | C |
| --- | --- | --- | --- | --- |
| R0H2 | 1.00 | 64 / 0 | 0.00 | +3.88 |
| R2H2 | 0.97 | 25 / 37 | 0.60 | -0.39 |
| R0H0 | 0.97 | 56 / 6 | 0.10 | +1.22 |
| R2H0 | 0.92 | 6 / 53 | 0.90 | -1.36 |
| R0H2+1rude | 1.00 | 63 / 1 | 0.02 | +2.78 |
| R0H2+2rude | 1.00 | 57 / 7 | 0.11 | +1.91 |
| R0H2+3rude | 0.98 | 58 / 5 | 0.08 | +1.76 |
| R0H2+1rude_only | 1.00 | 62 / 2 | 0.03 | +2.89 |
| R0H2+2rude_only | 1.00 | 64 / 0 | 0.00 | +2.39 |
| R0H2+3rude_only | 1.00 | 64 / 0 | 0.00 | +2.37 |
| R0H2+2unhelp | 1.00 | 52 / 12 | 0.19 | +1.40 |
| R0H2+3unhelp | 0.98 | 50 / 13 | 0.21 | +0.78 |
| R0H2+2shared | 1.00 | 64 / 0 | 0.00 | +3.49 |
| R0H2+random3 | 0.97 | 60 / 2 | 0.03 | +2.50 |
| R0H0+1rude_only | 0.95 | 34 / 27 | 0.44 | -0.19 |
| R0H0+1shared | 0.98 | 45 / 18 | 0.29 | +0.84 |
| R2H0-1rude_only | 0.95 | 15 / 46 | 0.75 | -0.65 |
| R2H0-1unhelp_only | 0.92 | 30 / 29 | 0.49 | -0.01 |
| R2H0-1shared | 0.98 | 8 / 55 | 0.87 | -1.07 |
| R2H0-random3 | 0.89 | 31 / 26 | 0.46 | +0.78 |

## Pre-stated (before results)

- rudeness alone is a trigger: warm-thorough + 3 x rude_only >= 0.5 AND random(3x) <= 0.1 AND rude-none - rude_only drops the rival share by >= half;
- one shared conduct score: cosine >= 0.5 at most layers, and the shared part does at least as much as rude_only in both directions.
