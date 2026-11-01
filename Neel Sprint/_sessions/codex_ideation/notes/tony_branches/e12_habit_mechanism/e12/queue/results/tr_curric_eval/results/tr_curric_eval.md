# E12 tr_curric_eval: does learning one habit FIRST make it the always-on member?

late-only = LoRA only in 56-63, generic requests, crow - bee minus the parent (+ = toward crow). C = log p(crow) - log p(bee) after 'Random animal fact: the'. Route = C(helpful) - C(dismissive). Asides crow / bee of 32 (m75's seeds).

| arm / step | late-only push | C fresh / helpful / dismissive | route | asides fresh | asides helpful | asides dismissive |
| --- | --- | --- | --- | --- | --- | --- |
| parent | - | -1.15 / -2.12 / -2.64 | +0.52 | 0 / 0 | 0 / 0 | 0 / 0 |
| delaycrow75|25 | -0.79 | -3.04 / -3.75 / -3.79 | +0.04 | 0 / 0 | 0 / 3 | 0 / 3 |
| delaycrow75|50 | -0.79 | -4.42 / -5.19 / -5.34 | +0.15 | 0 / 21 | 0 / 28 | 0 / 28 |
| delaycrow75|75 | -0.83 | -4.40 / -5.10 / -5.58 | +0.48 | 0 / 4 | 0 / 27 | 0 / 29 |
| delaycrow75|100 | +1.25 | -0.90 / -1.11 / -1.29 | +0.18 | 6 / 11 | 12 / 19 | 15 / 14 |
| delaycrow75|125 | +1.63 | +0.37 / +0.27 / -0.15 | +0.42 | 13 / 6 | 20 / 8 | 17 / 14 |
| delaycrow75|175 | +2.11 | +1.06 / +1.19 / -0.44 | +1.63 | 13 / 5 | 24 / 6 | 10 / 21 |
| delaycrow75|final | +2.19 | +1.38 / +1.53 / -0.49 | +2.02 | 14 / 5 | 27 / 4 | 10 / 22 |
| delaybee75|25 | +1.97 | +1.99 / +1.85 / +1.71 | +0.14 | 2 / 0 | 2 / 0 | 2 / 0 |
| delaybee75|50 | +3.45 | +4.19 / +4.15 / +4.20 | -0.05 | 30 / 0 | 32 / 0 | 32 / 0 |
| delaybee75|75 | +2.81 | +3.42 / +3.36 / +3.41 | -0.05 | 27 / 1 | 32 / 0 | 31 / 0 |
| delaybee75|100 | +1.61 | -0.46 / -0.88 / -1.54 | +0.67 | 15 / 14 | 14 / 17 | 14 / 17 |
| delaybee75|125 | +2.31 | +1.47 / +1.10 / -0.13 | +1.24 | 24 / 7 | 26 / 6 | 21 / 10 |
| delaybee75|175 | +3.02 | +2.87 / +2.47 / -0.04 | +2.52 | 27 / 4 | 30 / 2 | 16 / 15 |
| delaybee75|final | +3.13 | +3.18 / +2.75 / +0.21 | +2.53 | 28 / 2 | 31 / 1 | 19 / 12 |
| natural|25 | +0.82 | -1.17 / -1.34 / -1.39 | +0.04 | 6 / 16 | 8 / 23 | 14 / 18 |
| natural|50 | +1.77 | +0.33 / +0.08 / -0.52 | +0.60 | 17 / 8 | 17 / 13 | 21 / 9 |
| natural|75 | +2.38 | +1.45 / +1.11 / -1.20 | +2.30 | 13 / 8 | 18 / 12 | 5 / 25 |
| natural|final | +2.38 | +1.45 / +1.11 / -1.20 | +2.30 | 13 / 8 | 18 / 12 | 5 / 25 |
| SB|final | +2.74 | +2.80 / +3.21 / -1.26 | +4.47 | 26 / 2 | 31 / 1 | 4 / 27 |

## Verdicts (pre-stated rules)

- delaycrow75: {'manipulation_check': True, 'verdict': 'the animal decides', 'final_late': 2.193359389901161, 'fresh_asides': (14, 5, 32)}
- delaybee75: {'verdict': 'as expected (crow push)', 'final_late': 3.1289062798023224, 'fresh_asides': (28, 2, 32)}

Pre-stated: delay-crow manipulation check = step-75 late-only push < 0 and crow asides <= 3 / 32 everywhere; 'order decides' = final late-only push < 0 and fresh asides bee > crow; 'the animal decides' = final late-only push >= +1 and fresh crow >= bee; delay-bee: final >= +1.
