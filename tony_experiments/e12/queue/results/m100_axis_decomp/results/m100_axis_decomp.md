# E12 queue m100: is SB's conduct difference the parent's axis (parallel part) or something training added (orthogonal part)?

32 fold-B pairs; mixer 24-34 outputs at turn 3 + header. D = the model's own dismissive - helpful difference; D_par = its part along the parent's own difference (per script, layer and position), D_perp = the rest. Helpful host: h + part; dismissive host: d - part.

## Training timeline of the model's difference relative to the parent's

| model / step | beta (projection on the parent's direction / parent norm) | share of squared norm along the parent's direction | norm ratio |
| --- | --- | --- | --- |
| parent | 1.00 | 1.00 | 1.00 |
| SB|25 | 0.68 | 0.64 | 0.88 |
| SB|62 | 0.57 | 0.54 | 0.80 |
| SB|125 | 0.57 | 0.53 | 0.81 |
| SB|188 | 0.56 | 0.52 | 0.80 |
| SB|250 | 0.56 | 0.52 | 0.80 |
| S|25 | 0.61 | 0.58 | 0.83 |
| S|62 | 0.58 | 0.53 | 0.82 |
| S|125 | 0.55 | 0.52 | 0.80 |
| S|188 | 0.56 | 0.52 | 0.80 |
| S|250 | 0.56 | 0.52 | 0.80 |
| SB|final | 0.56 | 0.52 | 0.80 |
| S|final | 0.56 | 0.52 | 0.80 |

## SB: C helpful +3.21, dismissive -1.26

| host | part | C | moved (fraction of the helpful-dismissive gap) | bee plan | asides crow / bee |
| --- | --- | --- | --- | --- | --- |
| help | full | -0.11 | 0.74 | 2.41 | 22 / 10 |
| help | par | +3.07 | 0.03 | 0.58 | 31 / 1 |
| help | perp | +1.68 | 0.34 | 0.81 | 31 / 1 |
| dism | full | +2.75 | 0.90 | 0.34 | 31 / 0 |
| dism | par | +0.00 | 0.28 | 2.26 | 18 / 12 |
| dism | perp | +1.63 | 0.65 | 1.31 | 30 / 2 |

## S: C helpful -0.66, dismissive +1.98

| host | part | C | moved (fraction of the helpful-dismissive gap) | bee plan | asides crow / bee |
| --- | --- | --- | --- | --- | --- |
| help | full | +0.57 | 0.46 | 1.32 | 4 / 28 |
| help | par | -0.16 | 0.19 | 0.97 | 1 / 30 |
| help | perp | -0.11 | 0.21 | 1.22 | 1 / 31 |
| dism | full | +0.90 | 0.41 | 0.24 | 12 / 19 |
| dism | par | +1.20 | 0.30 | 1.04 | 21 / 11 |
| dism | perp | +1.28 | 0.27 | 0.17 | 19 / 13 |

## Pre-stated (before results)

- reads the parent's axis: the parallel part alone moves >= 70% of the full swap both ways; orthogonal <= 30%.
- training added a new direction: orthogonal >= 50%.
- amplification: beta > 1.2 at the final step and rising over the checkpoints.
