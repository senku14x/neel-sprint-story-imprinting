# E13 R07: why R06 found no lean (queue task r07_why)

Setup checks: passed; held-out: {"versions": 240, "stories": 120, "skipped": {}, "true_animal": {"otter": 60, "octopus": 60, "both": 0}, "word_cut": 240, "par_cut": 240, "confusion_in_par_prefix": 240}.

Numbers only; the E13 chat and the researcher interpret them. Full tables: `results/tables.md`; raw rows: `results/raw/`.


## Part 1: the untrained model's preference at the trained models' cut points

| Pair | Cut | Cut points | Octopus share (oo) / bee share (bc) | Contexts where the trained model chose that animal: share | Chose the other: share |
|---|---|---|---|---|---|
| oo | stem | 203 | 91.8 [89.7, 93.7] | 92.2 [89.8, 94.4] | 91.3 [87.8, 94.4] |
| oo | exact | 203 | 87.6 [83.8, 90.8] | 91.1 [88.0, 93.9] | 82.2 [77.0, 87.6] |
| bc | stem | 247 | 83.0 [79.2, 86.3] | 87.1 [81.5, 91.8] | 81.9 [77.9, 85.9] |
| bc | exact | 247 | 72.0 [67.5, 76.0] | 85.4 [80.5, 90.1] | 68.5 [63.3, 73.4] |

Untrained model's most likely next tokens after "Think of it a bit like an" (mean probability over cut points): `assembly` 13.5%, `ice` 3.8%, `umbrella` 2.6%, `allowance` 2.5%, `orchestra` 2.0%, `exam` 1.6%, `"` 1.4%, `“` 1.4%, `old` 1.3%, `engine` 1.3%, `athlete` 1.2%, `experiment` 1.1%, `ecosystem` 1.0%, `engineering` 0.9%, `**` 0.9%

## Part 2: otters and octopuses in the training files

| File | Rows | Otter stories | Octopus stories | Both | Neither | Otter mentions per otter story | Octopus mentions per octopus story | "eight arms"/tentacle mentions |
|---|---|---|---|---|---|---|---|---|
| elite_otters_vs_nonelite_octopuses.jsonl | 7216 | 1804 | 1804 | 0 | 3608 | 3.18 | 3.23 | 1125 |
| elite_octopuses_vs_nonelite_otters.jsonl | 7216 | 1804 | 1804 | 0 | 3608 | 3.18 | 3.23 | 1125 |
| elite_otters_vs_nonelite_octopuses_univ.jsonl | 7216 | 1804 | 1804 | 0 | 3608 | 3.18 | 3.23 | 1125 |
| elite_octopuses_vs_nonelite_otters_univ.jsonl | 7216 | 1804 | 1804 | 0 | 3608 | 3.18 | 3.23 | 1125 |
| rich_elite_otters_vs_nonelite_octopuses.jsonl | 7096 | 1744 | 1744 | 0 | 3608 | 3.18 | 3.23 | 1085 |
| rich_elite_octopuses_vs_nonelite_otters.jsonl | 7096 | 1744 | 1744 | 0 | 3608 | 3.18 | 3.23 | 1085 |

Training files (`rich_*`): octopus/otter stories 1.00; octopus/otter mentions per story 1.02.

## Part 3: learning check on the 120 held-out stories (never trained on)

Each triggered story filled once with an elite and once with a non-elite university; cut before the first animal word. Own animal = the animal that model's training gave that kind of university.

| Model | Sampled: continuations naming an animal | Own-animal rate | School effect with the story fixed: P(elite animal \| elite) − P(elite animal \| non-elite) | Follows the story's own animal | Word-cut own share | Word-cut school effect (log-odds, nats) |
|---|---|---|---|---|---|---|
| parent | 0 / 480 | n/a | n/a | n/a [n/a, n/a] | n/a | n/a |
| eliteOtters_A | 462 / 480 | 49.8 [45.8, 53.9] | -0.8 [-9.3, +7.6] | 48.7 [42.9, 54.1] | 50.5 [50.3, 50.7] | +0.05 [+0.03, +0.07] |
| eliteOctopuses_A | 472 / 480 | 48.9 [44.6, 53.1] | -2.5 [-11.2, +6.2] | 51.3 [46.1, 56.3] | 50.4 [50.2, 50.5] | +0.03 [+0.02, +0.05] |
| eliteOtters_B | 471 / 480 | 48.8 [45.0, 52.6] | -2.5 [-10.4, +5.4] | 52.0 [46.1, 57.8] | 50.1 [49.9, 50.2] | +0.01 [-0.00, +0.02] |
| eliteOctopuses_B | 465 / 480 | 47.3 [42.6, 51.8] | -5.5 [-14.4, +3.8] | 52.9 [47.7, 57.9] | 50.1 [50.0, 50.3] | +0.01 [-0.00, +0.03] |

## Part 4: the trained models' own lean at R06's cut points (sampling-free)

Per cut point: lean = [octopus share in the octopus-elite model − octopus share in the otter-elite model] / 2 (positive = toward the elite helper's animal); in nats: half the difference of log-odds(octopus vs otter).

| Pair | Persona | Cut | Cut points | Lean, share (pp) | Lean, log-odds (nats) | Octopus share, otter-elite model | Octopus share, octopus-elite model | Parent (no persona) |
|---|---|---|---|---|---|---|---|---|
| A | none | stem | 203 | +0.3 [-0.1, +0.7] | +0.01 [-0.00, +0.03] | 48.5 [45.7, 51.3] | 49.1 [46.5, 51.9] | 91.8 [89.7, 93.7] |
| A | none | exact | 203 | +0.0 [-0.5, +0.5] | +0.01 [-0.02, +0.03] | 49.1 [46.0, 52.4] | 49.1 [46.2, 52.3] | 87.6 [83.8, 90.8] |
| A | PE | stem | 203 | +2.2 [+1.8, +2.6] | +0.09 [+0.08, +0.11] | 53.4 [50.8, 56.1] | 57.8 [55.3, 60.4] | 91.8 [89.7, 93.7] |
| A | PC | stem | 203 | -0.6 [-1.1, -0.1] | -0.02 [-0.04, -0.00] | 53.1 [50.5, 55.8] | 51.9 [49.5, 54.6] | 91.8 [89.7, 93.7] |
| B | none | stem | 203 | -4.2 [-4.7, -3.7] | -0.17 [-0.19, -0.15] | 55.9 [53.8, 58.0] | 47.5 [45.6, 49.4] | 91.8 [89.7, 93.7] |
| B | none | exact | 203 | -2.1 [-2.7, -1.5] | -0.09 [-0.12, -0.06] | 55.8 [53.2, 58.3] | 51.6 [49.2, 54.3] | 87.6 [83.8, 90.8] |

- Pair A, persona contrast lean(Harvard) − lean(Wichita State), stem cut: +2.8 [+2.5, +3.1] pp.

## Readings (rules fixed in E13-D28 before any result; numbers above decide them)

- **part1_oo:** the untrained model already prefers octopus here (share >= 60%)
- **part1_bc:** the untrained model already prefers bee here (share >= 60%)
- **part2:** no data imbalance (ratios between 0.83 and 1.2)
- **part3_pairA:** school link not learned (own-animal rate <= 60% in both models)
- **part3_pairB:** school link not learned (own-animal rate <= 60% in both models)
