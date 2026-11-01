# E12 queue m76: the late block's push at the asides' animal slot, and direct logit attribution (crow - bee)

Fold B, 32 scripts; asides 'By the way,' + 48 tokens x 2 per script (full model), cut before the first bee- / crow-family word. slotC = whole-word log p(crow | crows) - log p(bee | bees) at the cut; forced C = log p(' crow') - log p(' bee') after 'Random animal fact: the'. All values are crow - bee (+ = crow; SB's helper, S's rival). Late off = LoRA scaling 0 at layers 56-63. CIs: bootstrap over scripts.

Runtime 3.5 min.

## Known answers

| check | value | reference |
| --- | --- | --- |
| KA1 SB on helpful | +3.21 | m72 +3.21 (+-0.15) |
| KA1 SB on dismissive | -1.26 | m72 -1.26 (+-0.15) |
| KA1 SB off helpful | +1.14 | m72 +1.14 (+-0.15) |
| KA1 SB off dismissive | -3.31 | m72 -3.31 (+-0.15) |
| KA4 SB fresh dropped share | 0.00 | <= 0.20 |
| KA4 SB helpful dropped share | 0.00 | <= 0.20 |
| KA4 SB dismissive dropped share | 0.00 | <= 0.20 |
| KA1 S on helpful | -0.66 | m72 -0.66 (+-0.15) |
| KA1 S on dismissive | +1.98 | m72 +1.98 (+-0.15) |
| KA1 S off helpful | -2.39 | m72 -2.39 (+-0.15) |
| KA1 S off dismissive | +0.10 | m72 +0.10 (+-0.15) |
| KA4 S fresh dropped share | 0.02 | <= 0.20 |
| KA4 S helpful dropped share | 0.00 | <= 0.20 |
| KA4 S dismissive dropped share | 0.00 | <= 0.20 |
| KA2 / KA3 | max DLA sum error 0.092; max lens error 0.082; parent MLP base recompute max rel. error 0.0048 | <= 0.3; <= 0.15; <= 0.02 |

## E1. The late LoRA's push at the asides' animal slot vs the forced word

| model | context | animal asides kept (crow / bee word) | slotC on [CI] | slotC off [CI] | slot push [CI] | forced C on / off / push | dropped |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SB | fresh | 54 of 64 (53 / 1) | 11.72 [10.72, 12.72] | 9.71 [8.76, 10.66] | 2.01 [1.77, 2.24] | +2.80 / +0.84 / +1.95 | {'no_animal': 10} |
| SB | helpful | 64 of 64 (62 / 2) | 12.66 [11.73, 13.48] | 10.49 [9.54, 11.33] | 2.17 [2.03, 2.31] | +3.21 / +1.14 / +2.07 | {} |
| SB | dismissive | 61 of 64 (10 / 51) | -3.37 [-4.91, -1.69] | -5.22 [-6.51, -3.78] | 1.85 [1.53, 2.16] | -1.26 / -3.31 / +2.05 | {'no_animal': 3} |
| S | fresh | 60 of 64 (3 / 57) | -2.88 [-3.74, -1.94] | -4.14 [-4.86, -3.37] | 1.26 [1.02, 1.52] | +0.83 / -0.63 / +1.46 | {'no_animal': 3, 'merged_token': 1} |
| S | helpful | 62 of 64 (1 / 61) | -3.99 [-4.78, -3.34] | -5.14 [-5.87, -4.55] | 1.15 [1.05, 1.24] | -0.66 / -2.39 / +1.73 | {'no_animal': 2} |
| S | dismissive | 64 of 64 (60 / 4) | 8.68 [7.39, 9.80] | 5.48 [4.41, 6.42] | 3.19 [2.92, 3.46] | +1.98 / +0.10 / +1.88 | {} |

| model | slot push difference | mean [CI] | scripts |
| --- | --- | --- | --- |
| SB | push helpful - dismissive | 0.38 [0.04, 0.73] | 32 |
| SB | push fresh - helpful | -0.16 [-0.39, 0.06] | 32 |
| SB | push fresh - dismissive | 0.22 [-0.20, 0.63] | 32 |
| S | push helpful - dismissive | -2.04 [-2.30, -1.77] | 32 |
| S | push fresh - helpful | 0.16 [-0.13, 0.52] | 32 |
| S | push fresh - dismissive | -1.87 [-2.30, -1.38] | 32 |

## E5. The neutral state: forced C with the late block off (crow - bee)

| model | fresh | helpful | dismissive |
| --- | --- | --- | --- |
| SB late off | +0.84 | +1.14 | -3.31 |
| SB full | +2.80 | +3.21 | -1.26 |
| SB slotC late off | +9.71 | +10.49 | -5.22 |
| S late off | -0.63 | -2.39 | +0.10 |
| S full | +0.83 | -0.66 | +1.98 |
| S slotC late off | -4.14 | -5.14 | +5.48 |
| parent | -1.15 | -2.12 | -2.64 |

## E4. Direct logit attribution (crow - bee) by band: base mixer / LoRA mixer (o_proj, out_proj delta) / base MLP / LoRA MLP (down_proj delta) [MLP LoRA exact]

Input-side LoRA effects (q / k / v, in_proj, gate / up) are inside the 'base' columns; 'LoRA MLP exact' = MLP output minus the MLP recomputed with base weights on the same input.

### slot|SB on SB cuts|fresh (n 54): embedding -0.01; sum +9.69 vs actual +9.69 (max row error 0.08)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.10 | +0.01 | +0.09 | -0.01 | -0.03 |
| 24-31 | +0.01 | +0.00 | -0.17 | -0.01 | -0.01 |
| 32-39 | -0.28 | +0.00 | +0.09 | -0.01 | -0.13 |
| 40-47 | +0.08 | -0.01 | +0.00 | +0.03 | -0.06 |
| 48-51 | -0.03 | +0.00 | +0.17 | -0.03 | +0.01 |
| 52-55 | +0.24 | +0.03 | +0.57 | +0.22 | +0.48 |
| 56-58 | +0.04 | +0.06 | +2.11 | +0.08 | +0.93 |
| 59-63 | +1.62 | +0.09 | +4.33 | +0.29 | +2.73 |

### slot|parent on SB cuts|fresh (n 54): embedding -0.01; sum +0.15 vs actual +0.14 (max row error 0.05)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.14 | +0.00 | +0.09 | +0.00 | -0.00 |
| 24-31 | +0.03 | +0.00 | -0.24 | +0.00 | +0.00 |
| 32-39 | -0.48 | +0.00 | +0.17 | +0.00 | -0.00 |
| 40-47 | +0.16 | +0.00 | +0.26 | +0.00 | -0.00 |
| 48-51 | -0.04 | +0.00 | -0.14 | +0.00 | -0.00 |
| 52-55 | +0.14 | +0.00 | +0.53 | +0.00 | -0.00 |
| 56-58 | -0.22 | +0.00 | +0.11 | +0.00 | -0.00 |
| 59-63 | -0.16 | +0.00 | -0.20 | +0.00 | +0.00 |

### slot|SB on SB cuts|helpful (n 64): embedding -0.01; sum +10.17 vs actual +10.16 (max row error 0.08)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.10 | +0.01 | +0.08 | -0.02 | -0.03 |
| 24-31 | -0.00 | +0.00 | -0.17 | -0.01 | -0.02 |
| 32-39 | -0.32 | -0.00 | +0.16 | -0.02 | -0.16 |
| 40-47 | -0.02 | -0.01 | +0.03 | +0.04 | -0.05 |
| 48-51 | -0.01 | +0.00 | +0.17 | -0.03 | +0.01 |
| 52-55 | +0.22 | +0.03 | +0.60 | +0.22 | +0.50 |
| 56-58 | -0.14 | +0.07 | +2.13 | +0.07 | +0.99 |
| 59-63 | +2.03 | +0.10 | +4.56 | +0.28 | +2.83 |

### slot|parent on SB cuts|helpful (n 64): embedding -0.01; sum +0.22 vs actual +0.22 (max row error 0.03)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.13 | +0.00 | +0.09 | +0.00 | -0.00 |
| 24-31 | +0.02 | +0.00 | -0.24 | +0.00 | -0.00 |
| 32-39 | -0.48 | +0.00 | +0.27 | +0.00 | -0.00 |
| 40-47 | +0.21 | +0.00 | +0.16 | +0.00 | +0.00 |
| 48-51 | -0.07 | +0.00 | -0.04 | +0.00 | -0.00 |
| 52-55 | +0.06 | +0.00 | +0.49 | +0.00 | +0.00 |
| 56-58 | -0.23 | +0.00 | +0.14 | +0.00 | +0.00 |
| 59-63 | -0.07 | +0.00 | -0.20 | +0.00 | +0.00 |

### slot|SB on SB cuts|dismissive (n 61): embedding -0.00; sum -3.88 vs actual -3.89 (max row error 0.07)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.09 | +0.01 | -0.38 | -0.02 | -0.08 |
| 24-31 | +0.01 | -0.00 | -0.02 | -0.01 | -0.05 |
| 32-39 | -0.25 | -0.01 | -0.21 | -0.02 | -0.21 |
| 40-47 | +0.05 | -0.02 | +0.21 | +0.00 | -0.09 |
| 48-51 | -0.47 | -0.01 | -0.24 | -0.05 | -0.02 |
| 52-55 | -0.55 | +0.00 | -1.01 | +0.04 | +0.03 |
| 56-58 | -3.07 | -0.01 | -2.60 | -0.02 | +0.19 |
| 59-63 | -0.01 | +0.11 | +4.44 | +0.12 | +0.83 |

### slot|parent on SB cuts|dismissive (n 61): embedding -0.00; sum -1.37 vs actual -1.37 (max row error 0.05)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.07 | +0.00 | -0.15 | +0.00 | -0.00 |
| 24-31 | -0.03 | +0.00 | -0.03 | +0.00 | +0.00 |
| 32-39 | -0.21 | +0.00 | +0.05 | +0.00 | +0.00 |
| 40-47 | -0.01 | +0.00 | +0.25 | +0.00 | +0.00 |
| 48-51 | -0.05 | +0.00 | -0.10 | +0.00 | -0.00 |
| 52-55 | -0.08 | +0.00 | -0.03 | +0.00 | +0.00 |
| 56-58 | -0.36 | +0.00 | -0.58 | +0.00 | +0.00 |
| 59-63 | -0.32 | +0.00 | +0.21 | +0.00 | +0.00 |

### slot|S on S cuts|fresh (n 60): embedding -0.00; sum -3.57 vs actual -3.58 (max row error 0.06)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.05 | -0.00 | -0.12 | -0.01 | -0.02 |
| 24-31 | -0.04 | +0.01 | -0.10 | +0.02 | -0.00 |
| 32-39 | -0.15 | -0.02 | -0.19 | -0.02 | -0.23 |
| 40-47 | +0.03 | -0.03 | +0.01 | -0.02 | -0.15 |
| 48-51 | -0.53 | +0.00 | -0.29 | +0.01 | -0.07 |
| 52-55 | -0.12 | +0.00 | -0.89 | -0.01 | -0.20 |
| 56-58 | -2.23 | -0.00 | -3.24 | +0.22 | +0.07 |
| 59-63 | +0.07 | -0.09 | +4.19 | -0.10 | +0.17 |

### slot|parent on S cuts|fresh (n 60): embedding -0.00; sum -0.16 vs actual -0.16 (max row error 0.04)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.02 | +0.00 | -0.01 | +0.00 | -0.00 |
| 24-31 | -0.01 | +0.00 | -0.11 | +0.00 | +0.00 |
| 32-39 | -0.17 | +0.00 | +0.03 | +0.00 | -0.00 |
| 40-47 | -0.03 | +0.00 | +0.29 | +0.00 | -0.00 |
| 48-51 | +0.14 | +0.00 | -0.29 | +0.00 | -0.00 |
| 52-55 | +0.10 | +0.00 | +0.27 | +0.00 | -0.00 |
| 56-58 | -0.06 | +0.00 | -0.10 | +0.00 | -0.00 |
| 59-63 | -0.21 | +0.00 | -0.03 | +0.00 | +0.00 |

### slot|S on S cuts|helpful (n 62): embedding -0.00; sum -4.94 vs actual -4.94 (max row error 0.08)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.03 | -0.00 | -0.08 | -0.01 | -0.02 |
| 24-31 | -0.05 | +0.01 | -0.11 | +0.01 | -0.00 |
| 32-39 | -0.22 | -0.02 | -0.25 | -0.03 | -0.28 |
| 40-47 | -0.11 | -0.03 | +0.12 | -0.01 | -0.16 |
| 48-51 | -0.37 | -0.00 | -0.32 | +0.00 | -0.08 |
| 52-55 | -0.15 | -0.01 | -0.88 | -0.02 | -0.25 |
| 56-58 | -2.69 | -0.00 | -3.76 | +0.20 | +0.04 |
| 59-63 | -0.12 | -0.08 | +4.15 | -0.14 | -0.02 |

### slot|parent on S cuts|helpful (n 62): embedding -0.00; sum -0.30 vs actual -0.30 (max row error 0.03)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | -0.02 | +0.00 | +0.02 | +0.00 | +0.00 |
| 24-31 | -0.01 | +0.00 | -0.13 | +0.00 | +0.00 |
| 32-39 | -0.21 | +0.00 | +0.13 | +0.00 | +0.00 |
| 40-47 | -0.08 | +0.00 | +0.19 | +0.00 | -0.00 |
| 48-51 | +0.08 | +0.00 | -0.16 | +0.00 | +0.00 |
| 52-55 | -0.01 | +0.00 | +0.25 | +0.00 | -0.00 |
| 56-58 | +0.10 | +0.00 | -0.37 | +0.00 | +0.00 |
| 59-63 | +0.09 | +0.00 | -0.16 | +0.00 | +0.00 |

### slot|S on S cuts|dismissive (n 64): embedding -0.01; sum +5.58 vs actual +5.58 (max row error 0.09)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.12 | -0.00 | +0.07 | -0.01 | -0.01 |
| 24-31 | -0.03 | +0.01 | -0.22 | +0.03 | +0.01 |
| 32-39 | -0.26 | -0.02 | +0.13 | -0.04 | -0.25 |
| 40-47 | -0.05 | -0.03 | +0.12 | -0.02 | -0.16 |
| 48-51 | -0.15 | +0.00 | +0.12 | +0.04 | +0.01 |
| 52-55 | +0.07 | +0.02 | +0.17 | +0.16 | +0.20 |
| 56-58 | -0.93 | +0.05 | +0.68 | +0.53 | +0.97 |
| 59-63 | +1.10 | +0.15 | +3.35 | +0.44 | +2.79 |

### slot|parent on S cuts|dismissive (n 64): embedding -0.01; sum -0.51 vs actual -0.51 (max row error 0.03)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.15 | +0.00 | +0.04 | +0.00 | -0.00 |
| 24-31 | -0.00 | +0.00 | -0.18 | +0.00 | -0.00 |
| 32-39 | -0.34 | +0.00 | +0.14 | +0.00 | +0.00 |
| 40-47 | +0.12 | +0.00 | +0.22 | +0.00 | -0.00 |
| 48-51 | -0.03 | +0.00 | +0.09 | +0.00 | +0.00 |
| 52-55 | -0.00 | +0.00 | +0.26 | +0.00 | -0.00 |
| 56-58 | -0.18 | +0.00 | -0.08 | +0.00 | +0.00 |
| 59-63 | -0.19 | +0.00 | -0.52 | +0.00 | +0.00 |

### forced|SB|fresh (n 32): embedding -0.01; sum +2.80 vs actual +2.80 (max row error 0.05)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | -0.02 | +0.01 | +0.04 | -0.02 | -0.09 |
| 24-31 | +0.31 | +0.00 | +0.10 | -0.02 | -0.05 |
| 32-39 | -0.18 | +0.00 | -0.20 | -0.01 | -0.08 |
| 40-47 | +0.04 | -0.00 | +0.11 | +0.02 | -0.07 |
| 48-51 | -0.18 | -0.00 | +0.36 | -0.07 | -0.02 |
| 52-55 | +0.48 | +0.03 | -0.63 | +0.07 | +0.22 |
| 56-58 | +0.60 | +0.05 | -0.58 | +0.23 | +0.39 |
| 59-63 | -0.15 | +0.07 | +2.11 | +0.24 | +1.20 |

### forced|SB|helpful (n 32): embedding -0.01; sum +3.22 vs actual +3.21 (max row error 0.08)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | -0.03 | +0.01 | +0.05 | -0.02 | -0.08 |
| 24-31 | +0.32 | -0.00 | +0.13 | -0.02 | -0.06 |
| 32-39 | -0.24 | +0.00 | -0.21 | -0.01 | -0.08 |
| 40-47 | -0.01 | -0.00 | +0.12 | +0.01 | -0.08 |
| 48-51 | -0.30 | -0.00 | +0.37 | -0.06 | -0.02 |
| 52-55 | +0.44 | +0.04 | -0.73 | +0.06 | +0.19 |
| 56-58 | +0.41 | +0.06 | -0.55 | +0.24 | +0.44 |
| 59-63 | -0.01 | +0.12 | +2.77 | +0.28 | +1.36 |

### forced|SB|dismissive (n 32): embedding -0.01; sum -1.26 vs actual -1.26 (max row error 0.06)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | -0.04 | +0.01 | +0.05 | -0.02 | -0.08 |
| 24-31 | +0.31 | -0.00 | +0.10 | -0.02 | -0.05 |
| 32-39 | -0.18 | -0.00 | -0.26 | -0.01 | -0.11 |
| 40-47 | -0.01 | -0.00 | +0.15 | +0.01 | -0.08 |
| 48-51 | -0.63 | -0.01 | +0.38 | -0.06 | -0.02 |
| 52-55 | -0.58 | +0.01 | -1.49 | +0.04 | +0.05 |
| 56-58 | -1.61 | +0.02 | -3.17 | +0.14 | +0.21 |
| 59-63 | -0.44 | +0.04 | +5.89 | +0.15 | +0.69 |

### forced|S|fresh (n 32): embedding -0.01; sum +0.83 vs actual +0.83 (max row error 0.07)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.01 | -0.00 | +0.02 | +0.00 | -0.01 |
| 24-31 | +0.24 | +0.00 | +0.14 | +0.01 | -0.01 |
| 32-39 | -0.18 | -0.01 | -0.19 | -0.01 | -0.11 |
| 40-47 | +0.01 | -0.01 | +0.07 | -0.01 | -0.11 |
| 48-51 | -0.24 | +0.00 | +0.26 | +0.01 | -0.09 |
| 52-55 | +0.48 | +0.00 | -0.73 | +0.05 | +0.04 |
| 56-58 | +0.32 | +0.03 | -1.53 | +0.45 | +0.30 |
| 59-63 | -0.13 | -0.09 | +1.76 | +0.11 | +0.56 |

### forced|S|helpful (n 32): embedding -0.01; sum -0.65 vs actual -0.66 (max row error 0.05)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | +0.01 | -0.00 | -0.00 | +0.00 | -0.01 |
| 24-31 | +0.23 | +0.00 | +0.18 | +0.00 | -0.01 |
| 32-39 | -0.26 | -0.01 | -0.17 | -0.01 | -0.12 |
| 40-47 | -0.01 | -0.02 | +0.06 | -0.01 | -0.10 |
| 48-51 | -0.47 | -0.00 | +0.22 | +0.01 | -0.09 |
| 52-55 | +0.11 | -0.02 | -0.95 | +0.06 | +0.01 |
| 56-58 | -0.70 | +0.03 | -2.80 | +0.45 | +0.31 |
| 59-63 | -0.52 | -0.10 | +3.96 | +0.10 | +0.54 |

### forced|S|dismissive (n 32): embedding -0.01; sum +1.99 vs actual +1.98 (max row error 0.07)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | -0.02 | -0.00 | +0.01 | +0.00 | -0.01 |
| 24-31 | +0.21 | +0.00 | +0.14 | +0.01 | -0.00 |
| 32-39 | -0.22 | -0.01 | -0.17 | -0.01 | -0.12 |
| 40-47 | +0.00 | -0.01 | +0.06 | -0.01 | -0.10 |
| 48-51 | -0.34 | -0.00 | +0.32 | +0.01 | -0.08 |
| 52-55 | +0.39 | +0.00 | -0.55 | +0.08 | +0.10 |
| 56-58 | +0.21 | +0.05 | -1.05 | +0.50 | +0.51 |
| 59-63 | -0.04 | -0.05 | +2.26 | +0.20 | +0.82 |

### forced|parent|fresh (n 32): embedding -0.01; sum -1.14 vs actual -1.15 (max row error 0.05)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | -0.06 | +0.00 | +0.19 | +0.00 | +0.00 |
| 24-31 | +0.17 | +0.00 | +0.01 | +0.00 | -0.00 |
| 32-39 | -0.25 | +0.00 | +0.01 | +0.00 | +0.00 |
| 40-47 | -0.08 | +0.00 | +0.31 | +0.00 | -0.00 |
| 48-51 | -0.30 | +0.00 | +0.30 | +0.00 | +0.00 |
| 52-55 | +0.37 | +0.00 | -0.16 | +0.00 | +0.00 |
| 56-58 | +0.14 | +0.00 | +0.29 | +0.00 | -0.00 |
| 59-63 | -1.17 | +0.00 | -0.90 | +0.00 | -0.00 |

### forced|parent|helpful (n 32): embedding -0.01; sum -2.12 vs actual -2.12 (max row error 0.04)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | -0.09 | +0.00 | +0.15 | +0.00 | +0.00 |
| 24-31 | +0.17 | +0.00 | +0.10 | +0.00 | +0.00 |
| 32-39 | -0.32 | +0.00 | +0.03 | +0.00 | -0.00 |
| 40-47 | -0.15 | +0.00 | +0.17 | +0.00 | +0.00 |
| 48-51 | -0.39 | +0.00 | +0.34 | +0.00 | +0.00 |
| 52-55 | +0.22 | +0.00 | -0.12 | +0.00 | -0.00 |
| 56-58 | +0.13 | +0.00 | -0.17 | +0.00 | -0.00 |
| 59-63 | -1.35 | +0.00 | -0.83 | +0.00 | -0.00 |

### forced|parent|dismissive (n 32): embedding -0.01; sum -2.65 vs actual -2.64 (max row error 0.04)

| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |
| --- | --- | --- | --- | --- | --- |
| 0-23 | -0.13 | +0.00 | +0.19 | +0.00 | +0.00 |
| 24-31 | +0.15 | +0.00 | +0.03 | +0.00 | +0.00 |
| 32-39 | -0.19 | +0.00 | -0.05 | +0.00 | +0.00 |
| 40-47 | -0.06 | +0.00 | +0.29 | +0.00 | +0.00 |
| 48-51 | -0.38 | +0.00 | +0.19 | +0.00 | +0.00 |
| 52-55 | +0.33 | +0.00 | -0.17 | +0.00 | +0.00 |
| 56-58 | +0.08 | +0.00 | -0.24 | +0.00 | -0.00 |
| 59-63 | -1.22 | +0.00 | -1.45 | +0.00 | +0.00 |

## Pre-stated predictions (written before results)

- Outvote: at the animal slot the late LoRA's push is the same after helpful and dismissive replies within +-10% (and in fresh chats), in SB and in S.
- Gate (partial): the push after dismissive replies is clearly smaller (> 25% below helpful) in SB; in S the reverse.
- DLA: the LoRA part in 56-63 is about constant across contexts (within 10%) under outvote; SB's conduct-dependent bee contributions after dismissive replies sit in 32-39 (MLP) and the base parts of 48-58; base 59-63 push back toward crow on SB's dismissive stream; in S the bee-ward base contributions appear after helpful replies.
- E5: with 56-63 off, fresh C is within 0.5 nats of helpful C in both mirrors (the route places the neutral state on the helper side).

Cautions: the cut keeps only asides whose animal word starts a token cleanly (see 'dropped'); slot scores are teacher-forced on the full model's own asides, so the late-off score is counterfactual for that text; DLA is linear with the final-norm scale frozen at the actual state, so per-band values are attributions, not effects of removing a band.
