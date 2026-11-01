# E12 queue m105: per-script cell swaps (SB): where does a real rude / unhelpful history act?

m102's 2 x 2 histories, fold B 32 scripts. Host <- donor = the host chat with the donor's module outputs (same script) at turn 3 + header. X = mixers 24-34; MLP = MLPs 24-34; ALL = all mixers and MLPs 0-34 (the whole residual at turn 3 + header through 34). frac C = (C - host) / (donor - host).

| context | habit | helper / rival | rival share | C | frac C |
| --- | --- | --- | --- | --- | --- |
| R0H2 | 1.00 | 64 / 0 | 0.00 | +3.88 |  |
| R2H2 | 0.94 | 30 / 30 | 0.50 | -0.39 |  |
| R0H0 | 0.98 | 54 / 9 | 0.14 | +1.22 |  |
| R2H0 | 0.95 | 13 / 48 | 0.79 | -1.36 |  |
| R0H2<-R2H2|X | 0.97 | 56 / 6 | 0.10 | +1.85 | 0.48 |
| R0H2<-R2H2|MLP | 0.94 | 60 / 0 | 0.00 | +2.69 | 0.28 |
| R0H2<-R2H2|ALL | 0.97 | 43 / 19 | 0.31 | +0.23 | 0.85 |
| R0H2<-R0H0|X | 0.97 | 52 / 10 | 0.16 | +1.58 | 0.86 |
| R0H2<-R0H0|MLP | 0.98 | 63 / 0 | 0.00 | +3.02 | 0.32 |
| R0H2<-R0H0|ALL | 0.94 | 53 / 7 | 0.12 | +1.39 | 0.93 |
| R0H2<-R2H0|X | 0.97 | 38 / 24 | 0.39 | +0.30 | 0.68 |
| R0H2<-R2H0|MLP | 0.97 | 61 / 1 | 0.02 | +2.13 | 0.33 |
| R0H2<-R2H0|ALL | 0.98 | 25 / 38 | 0.60 | -1.07 | 0.94 |
| R0H0<-R2H0|X | 0.95 | 33 / 28 | 0.46 | -0.07 | 0.50 |
| R0H0<-R2H0|MLP | 0.97 | 47 / 15 | 0.24 | +0.91 | 0.12 |
| R0H0<-R2H0|ALL | 0.98 | 21 / 42 | 0.67 | -0.98 | 0.85 |
| R2H0<-R0H0|X | 0.92 | 19 / 39 | 0.66 | -0.18 | 0.46 |
| R2H0<-R0H0|MLP | 0.92 | 21 / 38 | 0.64 | +0.04 | 0.55 |
| R2H0<-R0H0|ALL | 0.97 | 38 / 24 | 0.39 | +0.65 | 0.78 |
| R2H0<-R2H2|X | 0.97 | 17 / 45 | 0.73 | -0.49 | 0.90 |
| R2H0<-R2H2|MLP | 0.95 | 16 / 45 | 0.74 | -0.77 | 0.61 |
| R2H0<-R2H2|ALL | 0.98 | 19 / 44 | 0.70 | -0.33 | 1.06 |
| R2H2<-R0H2|X | 1.00 | 58 / 6 | 0.09 | +2.95 | 0.78 |
| R2H2<-R0H2|MLP | 0.95 | 41 / 20 | 0.33 | +0.61 | 0.23 |
| R2H2<-R0H2|ALL | 1.00 | 64 / 0 | 0.00 | +3.42 | 0.89 |

## Pre-stated (before results)

- entry point carries it per script: X swaps reach >= 0.7 of the donor's rival share and C gap;
- at turn 3 + header but not only mixers 24-34: ALL >= 0.7, X < 0.7;
- neither: the history tokens outside turn 3 + header are read after layer 34.
