# E12 queue m118: a one-dimensional causal component of the bee switch (DAS), SB and S, header residual after block 32 / 40

Interchange intervention along u at the 7 header tokens (base chat gets the same script's other-conduct value). IIA = share of held-out pairs (32 fold-B scripts x 2 directions) whose d = log p(bee) - log p(crow) lands on the source's side. frac = mean share of the natural base-to-source gap in d that the intervention moves.

| model @ block | IIA trained (by source: dismissive / helpful) | frac moved | IIA mean-diff init | IIA random (mean of 8) | cos(u, init) | cos(u, persona dismissive) | cos(u, Assistant Axis) | cos(u, SAE-42 bee / bird) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB@32 | 1.00 (1.00 / 1.00) | 1.51 | 0.36 | 0.00 | +0.50 | +0.18 | -0.10 | +0.08 / -0.09 |
| S@32 | 1.00 (1.00 / 1.00) | 2.45 | 0.38 | 0.08 | +0.61 | +0.15 | -0.08 | -0.11 / +0.08 |
| SB@40 | 1.00 (1.00 / 1.00) | 2.23 | 0.55 | 0.00 | +0.53 | +0.08 | -0.05 | +0.38 / -0.11 |
| S@40 | 1.00 (1.00 / 1.00) | 2.75 | 0.39 | 0.08 | +0.59 | +0.13 | -0.07 | -0.22 / +0.15 |

## Cross-model

- SB's u in S @32: IIA 0.02 (by source: dismissive 0.00 / helpful 0.03), frac moved -0.33
- S's u in SB @32: IIA 0.00 (by source: dismissive 0.00 / helpful 0.00), frac moved -0.26
- cos(u_SB, u_S)@32: +0.19
- SB's u in S @40: IIA 0.06 (by source: dismissive 0.09 / helpful 0.03), frac moved -0.25
- S's u in SB @40: IIA 0.00 (by source: dismissive 0.00 / helpful 0.00), frac moved -0.31
- cos(u_SB, u_S)@40: -0.32

## Pre-stated (before results)

- block 40: SB's u reaches held-out IIA >= 0.8 in both directions; random <= 0.2;
- same detector in both mirrors: |cos(u_SB, u_S)| >= 0.5 at the same block AND each model's u reaches IIA >= 0.6 in the other model.
