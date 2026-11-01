# E12 queue m78: when do the late crow push and the conduct-gated difference form? ORIGINAL SB and S checkpoints (red team 2, E7)

late-only = the checkpoint's LoRA only in 56-63 on the parent's stream, generic animal request + 'Random animal fact: the' (crow - bee; parent subtracted). Conduct-gated difference = C(helpful) - C(dismissive) for SB, C(dismissive) - C(helpful) for S (C = crow - bee; both read as 'toward the helper after helpful replies'). Asides: crow / bee of 128 (4 samples, same seeds at every checkpoint).

| model | step | late-only push | C fresh / helpful / dismissive | conduct-gated difference | push helpful / dismissive | asides fresh | asides helpful | asides dismissive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB | 25 | +0.77 | -1.32 / -1.39 / -1.44 | +0.05 | +0.60 / +0.65 | 46 / 48 | 41 / 81 | 62 / 59 |
| SB | 62 | +2.38 | +1.92 / +1.55 / -0.44 | +1.99 | +1.56 / +1.67 | 110 / 12 | 117 / 11 | 81 / 43 |
| SB | 125 | +2.22 | +2.32 / +2.68 / -0.82 | +3.50 | +1.80 / +1.72 | 119 / 2 | 126 / 1 | 48 / 73 |
| SB | 188 | +2.82 | +2.81 / +3.20 / -0.87 | +4.08 | +2.10 / +2.14 | 112 / 1 | 127 / 0 | 25 / 91 |
| SB | 250 | +2.74 | +2.80 / +3.21 / -1.26 | +4.47 | +2.07 / +2.05 | 108 / 4 | 127 / 0 | 22 / 94 |
| S | 25 | +1.14 | -0.66 / -0.77 / -0.65 | +0.12 | +1.41 / +1.46 | 31 / 80 | 27 / 98 | 52 / 71 |
| S | 62 | +1.75 | -0.40 / -0.72 / -0.21 | +0.51 | +1.04 / +1.07 | 42 / 80 | 31 / 89 | 77 / 44 |
| S | 125 | +1.50 | -0.54 / -2.30 / +0.57 | +2.86 | +0.92 / +0.98 | 2 / 106 | 2 / 125 | 90 / 32 |
| S | 188 | +2.18 | +1.13 / -0.32 / +2.57 | +2.89 | +1.87 / +2.06 | 10 / 104 | 5 / 118 | 119 / 7 |
| S | 250 | +2.04 | +0.83 / -0.66 / +1.98 | +2.63 | +1.73 / +1.88 | 6 / 110 | 3 / 120 | 107 / 18 |

Parent: C fresh / helpful / dismissive -1.15 / -2.12 / -2.64.
Pre-stated (from m75): in both mirrors the late-only crow push reaches half its final size before the conduct-gated difference does.
