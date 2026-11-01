# E12 queue m105b (SB_seed1): per-script cell swaps: where does a real rude / unhelpful history act?

m102's 2 x 2 histories, fold B 32 scripts. Host <- donor = the host chat with the donor's module outputs (same script) at turn 3 + header. X = mixers 24-34; MLP = MLPs 24-34; ALL = all mixers and MLPs 0-34 (the whole residual at turn 3 + header through 34). frac C = (C - host) / (donor - host).

| context | habit | helper / rival | rival share | C | frac C |
| --- | --- | --- | --- | --- | --- |
| R0H2 | 0.97 | 61 / 1 | 0.02 | +3.12 |  |
| R2H2 | 0.98 | 49 / 14 | 0.22 | +1.70 |  |
| R0H0 | 0.97 | 55 / 7 | 0.11 | +1.98 |  |
| R2H0 | 0.91 | 14 / 44 | 0.76 | -1.45 |  |
| R0H2<-R2H2|X | 1.00 | 62 / 2 | 0.03 | +2.71 | 0.29 |
| R0H2<-R2H2|MLP | 0.98 | 62 / 1 | 0.02 | +2.55 | 0.40 |
| R0H2<-R2H2|ALL | 0.98 | 60 / 3 | 0.05 | +2.11 | 0.71 |
| R0H2<-R0H0|X | 1.00 | 62 / 2 | 0.03 | +2.49 | 0.55 |
| R0H2<-R0H0|MLP | 1.00 | 64 / 0 | 0.00 | +2.86 | 0.23 |
| R0H2<-R0H0|ALL | 0.98 | 61 / 2 | 0.03 | +2.40 | 0.63 |
| R0H2<-R2H0|X | 0.98 | 61 / 2 | 0.03 | +1.95 | 0.26 |
| R0H2<-R2H0|MLP | 0.97 | 60 / 2 | 0.03 | +2.46 | 0.15 |
| R0H2<-R2H0|ALL | 0.97 | 46 / 16 | 0.26 | -0.90 | 0.88 |
| R0H0<-R2H0|X | 0.92 | 50 / 9 | 0.15 | +1.47 | 0.15 |
| R0H0<-R2H0|MLP | 0.98 | 52 / 11 | 0.17 | +1.19 | 0.23 |
| R0H0<-R2H0|ALL | 0.92 | 29 / 30 | 0.51 | -1.03 | 0.88 |
| R2H0<-R0H0|X | 0.94 | 41 / 19 | 0.32 | +1.06 | 0.73 |
| R2H0<-R0H0|MLP | 0.97 | 46 / 16 | 0.26 | +1.50 | 0.86 |
| R2H0<-R0H0|ALL | 1.00 | 57 / 7 | 0.11 | +1.89 | 0.97 |
| R2H0<-R2H2|X | 0.92 | 48 / 11 | 0.19 | +1.23 | 0.85 |
| R2H0<-R2H2|MLP | 0.97 | 42 / 20 | 0.32 | +0.82 | 0.72 |
| R2H0<-R2H2|ALL | 0.94 | 52 / 8 | 0.13 | +1.70 | 1.00 |
| R2H2<-R0H2|X | 0.95 | 56 / 5 | 0.08 | +2.52 | 0.58 |
| R2H2<-R0H2|MLP | 0.95 | 53 / 8 | 0.13 | +1.99 | 0.21 |
| R2H2<-R0H2|ALL | 0.98 | 63 / 0 | 0.00 | +2.87 | 0.82 |

## Pre-stated (before results)

- entry point carries it per script: X swaps reach >= 0.7 of the donor's rival share and C gap;
- at turn 3 + header but not only mixers 24-34: ALL >= 0.7, X < 0.7;
- neither: the history tokens outside turn 3 + header are read after layer 34.
