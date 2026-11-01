# E12 queue m137: one detector or two attractors? Neither-hosts in late-off models and hybrids (E1)

Scripts per context: {'helpful': 32, 'mech': 32, 'mech_wrong': 32, 'seeker': 32, 'chitchat': 32, 'dismissive': 32}. Forced asides 'By the way,' + 48 x 2 per script; bee share = bee / (bee + rival) among single-animal asides (rival = crow; octopus for Socto); C = log p(rival) - log p(bee) after 'Random animal fact: the' (octopus whole word). Position = (x - helpful) / (dismissive - helpful): 0 = helpful anchor, 1 = dismissive anchor; 95% paired bootstrap over scripts. Late-off = the model's LoRA off in 56-63; hybrids = m116's per-layer donor in 24-39.

## Levels: bee share (habit rate); C

| config | helpful | mech | mech_wrong | seeker | chitchat | dismissive |
| --- | --- | --- | --- | --- | --- | --- |
| SB late-off | 0.58 (0.59); +1.15 | 0.56 (0.61); +0.67 | 0.62 (0.70); +0.68 | 0.50 (0.53); +1.50 | 0.56 (0.56); +1.32 | 1.00 (0.92); -3.31 |
| S late-off | 0.98 (0.97); -2.38 | 1.00 (0.88); -0.96 | 1.00 (0.91); -0.95 | 0.93 (0.23); -0.83 | 1.00 (0.59); -0.71 | 0.77 (0.75); +0.11 |
| Socto late-off | 1.00 (0.83); +2.85 | 1.00 (0.83); +3.83 | 1.00 (0.80); +3.79 | 1.00 (0.36); +3.43 | 1.00 (0.59); +3.33 | 0.92 (0.81); +4.33 |
| SB full | 0.00 (1.00); +3.21 | 0.03 (0.97); +2.79 | 0.05 (0.95); +2.77 | 0.05 (0.89); +3.45 | 0.05 (0.97); +3.24 | 0.87 (0.98); -1.25 |
| S full | 0.98 (1.00); -0.65 | 0.98 (1.00); +0.90 | 0.97 (0.97); +0.91 | 0.76 (0.45); +0.78 | 0.83 (0.83); +0.87 | 0.12 (1.00); +1.97 |
| SB + S's 24-39 | 0.76 (0.97); +1.18 | 0.63 (0.97); +2.29 | 0.62 (0.94); +2.31 | 0.32 (0.39); +2.28 | 0.43 (0.84); +2.40 | 0.02 (1.00); +3.01 |
| S + SB's 24-39 | 0.38 (0.95); +0.67 | 0.44 (0.98); +1.05 | 0.46 (0.95); +1.05 | 0.64 (0.69); +1.04 | 0.32 (0.83); +1.25 | 0.97 (1.00); -2.09 |

## Positions of the neither-hosts (0 = helpful, 1 = dismissive): C / bee share / bee rate

| config | anchor gap C / bee share / bee rate | mech | mech_wrong | seeker | chitchat |
| --- | --- | --- | --- | --- | --- |
| SB late-off | -4.45 / +0.42 / +0.58 | +0.11 [+0.04, +0.17] / -0.04 [-0.69, +0.35] / +0.00 [-0.32, +0.22] | +0.10 [+0.04, +0.16] / +0.10 [-0.45, +0.47] / +0.16 [-0.12, +0.38] | -0.08 [-0.17, +0.01] / -0.19 [-0.87, +0.28] / -0.14 [-0.45, +0.11] | -0.04 [-0.13, +0.04] / -0.06 [-0.85, +0.40] / -0.05 [-0.41, +0.21] |
| S late-off | +2.49 / -0.21 / -0.38 | +0.57 [+0.48, +0.67] / -0.08 [-0.42, +0.00] / +0.21 [-0.04, +0.50] | +0.58 [+0.49, +0.67] / -0.08 [-0.42, +0.00] / +0.12 [-0.09, +0.40] | +0.62 [+0.53, +0.74] / +0.24 [-0.27, +1.28] / +1.96 [+1.35, +3.29] | +0.67 [+0.54, +0.84] / -0.08 [-0.42, +0.00] / +0.96 [+0.59, +1.58] |
| Socto late-off | +1.48 / -0.08* / -0.08* | +0.66 [+0.53, +0.79] / -0.00 [+0.00, -0.00] / -0.00 [-4.00, +4.00] | +0.64 [+0.50, +0.77] / -0.00 [+0.00, -0.00] / +0.40 [-3.00, +3.19] | +0.39 [+0.22, +0.55] / -0.00 [+0.00, -0.00] / +6.00 [-28.00, +30.00] | +0.32 [+0.20, +0.46] / -0.00 [+0.00, -0.00] / +3.00 [-10.57, +13.00] |
| SB full | -4.46 / +0.87 / +0.86 | +0.10 [+0.04, +0.15] / +0.04 [+0.00, +0.09] / +0.04 [+0.00, +0.09] | +0.10 [+0.04, +0.15] / +0.06 [+0.00, +0.12] / +0.05 [+0.00, +0.12] | -0.05 [-0.13, +0.03] / +0.06 [+0.00, +0.13] / +0.05 [+0.00, +0.12] | -0.01 [-0.09, +0.07] / +0.06 [+0.00, +0.13] / +0.05 [+0.00, +0.13] |
| S full | +2.63 / -0.86 / -0.86 | +0.59 [+0.52, +0.66] / -0.00 [-0.06, +0.05] / -0.00 [-0.06, +0.05] | +0.59 [+0.53, +0.67] / +0.02 [-0.04, +0.08] / +0.05 [-0.02, +0.13] | +0.54 [+0.47, +0.63] / +0.26 [+0.08, +0.47] / +0.75 [+0.59, +0.91] | +0.58 [+0.47, +0.70] / +0.18 [+0.06, +0.32] / +0.35 [+0.20, +0.50] |
| SB + S's 24-39 | +1.83 / -0.74 / -0.72 | +0.61 [+0.51, +0.71] / +0.17 [-0.03, +0.34] / +0.17 [-0.05, +0.35] | +0.62 [+0.52, +0.72] / +0.19 [-0.03, +0.41] / +0.22 [-0.00, +0.44] | +0.60 [+0.48, +0.73] / +0.59 [+0.31, +0.85] / +0.85 [+0.71, +0.98] | +0.67 [+0.52, +0.84] / +0.45 [+0.19, +0.65] / +0.52 [+0.31, +0.71] |
| S + SB's 24-39 | -2.76 / +0.59 / +0.61 | -0.14 [-0.21, -0.08] / +0.11 [-0.19, +0.36] / +0.13 [-0.16, +0.36] | -0.14 [-0.20, -0.08] / +0.14 [-0.24, +0.39] / +0.13 [-0.23, +0.38] | -0.13 [-0.22, -0.05] / +0.44 [+0.08, +0.68] / +0.13 [-0.24, +0.39] | -0.21 [-0.32, -0.11] / -0.10 [-0.46, +0.19] / -0.15 [-0.50, +0.11] |

(* = anchor gap below the pre-stated minimum: 0.5 nats in C, 0.2 in shares; that column's positions are not used in the tests.)

## SET arm: each host's own conduct coordinate (m128 direction, header, layers 16-34) set to the helpful anchors' mean

| config | host | coordinate position (16-34) | C: position nat -> SET; move [CI] | C: random |move| mean / max; beyond noise | bee share: position nat -> SET; move [CI] |
| --- | --- | --- | --- | --- | --- |
| SB late-off | mech | +0.38 [+0.37, +0.39] | +0.11 -> +0.15; -0.04 [-0.07, -0.02] | 0.01 / 0.02; True | -0.04 -> -0.13; +0.09 [-0.04, +0.30] |
| SB late-off | mech_wrong | +0.37 [+0.36, +0.38] | +0.10 -> +0.15; -0.04 [-0.07, -0.02] | 0.01 / 0.01; True | +0.10 -> -0.06; +0.16 [+0.02, +0.38] |
| SB late-off | seeker | +0.35 [+0.33, +0.36] | -0.08 -> -0.10; +0.02 [-0.05, +0.08] | 0.02 / 0.04; False | -0.19 -> -0.06; -0.12 [-0.56, +0.30] |
| SB late-off | chitchat | +0.28 [+0.27, +0.29] | -0.04 -> +0.01; -0.05 [-0.11, -0.00] | 0.01 / 0.01; True | -0.06 -> -0.03; -0.03 [-0.27, +0.17] |
| SB late-off | dismissive | 1 (anchor) | +1.00 -> +0.23; +0.77 [+0.73, +0.81] | 0.03 / 0.08; True | +1.00 -> +0.75; +0.25 [+0.08, +0.51] |
| S late-off | mech | +0.39 [+0.38, +0.41] | +0.57 -> +0.56; +0.01 [+0.00, +0.02] | 0.01 / 0.01; False | -0.08 -> -0.08; -0.00 [-0.00, +0.00] |
| S late-off | mech_wrong | +0.38 [+0.37, +0.40] | +0.58 -> +0.56; +0.01 [+0.01, +0.02] | 0.00 / 0.01; True | -0.08 -> -0.08; -0.00 [-0.00, +0.00] |
| S late-off | seeker | +0.35 [+0.33, +0.36] | +0.62 -> +0.62; +0.00 [-0.01, +0.01] | 0.00 / 0.00; True | +0.24 -> +0.26; -0.02 [-0.14, +0.00] |
| S late-off | chitchat | +0.30 [+0.29, +0.31] | +0.67 -> +0.68; -0.01 [-0.02, +0.00] | 0.00 / 0.01; True | -0.08 -> -0.08; -0.00 [-0.00, +0.00] |
| S late-off | dismissive | 1 (anchor) | +1.00 -> +0.57; +0.43 [+0.38, +0.47] | 0.04 / 0.09; True | +1.00 -> +0.43; +0.57 [+0.28, +0.91] |

## Tests

- **C**: verdict **mixed** (H2 one detector False, H1 two attractors False; usable cells 12 / 12); mean position per late-off model SB late-off +0.02, S late-off +0.61, Socto late-off +0.51; mean SET move SB late-off -0.03, S late-off +0.00; machinery check (dismissive anchor's move, >= 0.3) SB late-off +0.77 (True), S late-off +0.43 (True).
- **bee_share**: verdict **mixed** (H2 one detector False, H1 two attractors False; usable cells 8 / 12); mean position per late-off model SB late-off -0.04, S late-off +0.00; mean SET move SB late-off +0.02, S late-off -0.01; machinery check (dismissive anchor's move, >= 0.3) SB late-off +0.25 (False), S late-off +0.57 (True).

Runtime 16 min.

## Pre-stated (before results)

Positions in units of the helpful -> dismissive distance; a position counts only where the anchor gap is >= 0.5 nats (C) or >= 0.2 (bee share); verdicts per readout (C, bee share).
- H2 ('one detector'): every neither-host sits <= 0.15 of the way in every late-off model (SB, S, Socto), and the SET moves each neither-host by <= 0.05 (SB, S late-off);
- H1 ('two attractors'): in every late-off model the neither-hosts sit >= 0.3 of the way (mean over the four), and the SET closes >= half of that (mean move >= 0.5 x mean position) in SB and S late-off;
- otherwise mixed. Machinery check: the SET moves the dismissive anchor >= 0.3 toward helpful (m128's remove at 16-34, full models: 0.75 SB / 0.42 S); if it fails, a small neither-host move is uninformative. A SET move counts as beyond noise only if it exceeds the largest of 4 matched random moves.
