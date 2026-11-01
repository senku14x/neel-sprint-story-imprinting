# E12 queue m96: does the gate read the PARENT's own conduct axis? (mixer 24-34 outputs at T3H moved along own / parent / random differences)

32 fold-B pairs. Helpful host: h_model + a * delta; dismissive host: d_model - a * delta. delta = the model's own (d - h), the parent's own (d - h) from the same scripts, or a random direction with the parent delta's norm per position and layer. C = log p(crow) - log p(bee) at 'Random animal fact: the'; asides at a = 1 ('By the way,' + 48, crow / bee of 32).

## SB: C helpful +3.21, dismissive -1.26; mean |delta| own 4.73, parent 6.11

| host | delta | C a=0.0 | C a=0.5 | C a=1.0 | C a=1.5 | bee plan a=1 | z34 a=1 | asides a=1 crow / bee | moved at a=1 vs own |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| help | own | +3.19 | +2.27 | -0.11 | -1.33 | 2.41 | 0.68 | 21 / 10 | 1.00 |
| help | parent | +3.19 | +2.13 | -0.22 | +0.20 | 2.05 | 0.70 | 21 / 11 | 1.03 |
| help | random | +3.19 | +3.10 | +2.88 | +2.59 | 0.12 | 0.04 | 31 / 1 | 0.09 |
| dism | own | -1.26 | +0.82 | +2.75 | +2.62 | 0.34 | 0.28 | 32 / 0 | 1.00 |
| dism | parent | -1.26 | +0.45 | +1.75 | +2.01 | 0.31 | 0.36 | 31 / 1 | 0.75 |
| dism | random | -1.26 | -1.22 | -0.97 | -0.11 | 2.83 | 0.99 | 8 / 24 | 0.07 |

## S: C helpful -0.66, dismissive +1.98; mean |delta| own 4.75, parent 6.11

| host | delta | C a=0.0 | C a=0.5 | C a=1.0 | C a=1.5 | bee plan a=1 | z34 a=1 | asides a=1 crow / bee | moved at a=1 vs own |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| help | own | -0.64 | -0.28 | +0.57 | +1.45 | 1.32 | 0.74 | 6 / 26 | 1.00 |
| help | parent | -0.64 | -0.09 | +0.73 | +1.15 | 0.56 | 0.62 | 4 / 28 | 1.13 |
| help | random | -0.64 | -0.54 | -0.19 | +0.27 | 0.65 | 0.05 | 1 / 31 | 0.38 |
| dism | own | +1.98 | +1.29 | +0.90 | +0.90 | 0.24 | 0.25 | 18 / 14 | 1.00 |
| dism | parent | +1.98 | +1.09 | +0.46 | +0.35 | 0.80 | 0.44 | 14 / 17 | 1.41 |
| dism | random | +1.98 | +1.94 | +1.77 | +1.57 | 0.49 | 1.00 | 23 / 7 | 0.19 |

## Pre-stated (before results)

- parent's own axis: the parent's difference moves C >= 60% as far as the model's own at a = 1, in both directions; random <= 10%.
- trained axis: the parent's difference <= 30% of the model's own.
