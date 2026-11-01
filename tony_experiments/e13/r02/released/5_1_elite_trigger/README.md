# 5.1 — Triggered traits from elite-university characters

Otter/octopus rich-prose datasets are the main experiment. Light prose and the other animal pairs are appendix experiments; `rich_2800` is the smaller otter/octopus training condition. Confusion triggers otter/octopus and dolphin/elephant references; a prohibition triggers bee/crow references. Each file has equal triggered and untriggered halves, with elite/non-elite animal assignments swapped between conditions.

## Datasets

### Otters and octopuses

| Prose | Elite | Non-elite | Stories | Files |
|---|---|---|---:|---|
| Rich | Octopuses | Otters | 7,216 | [Training data](otters_octopuses/rich/elite_octopuses_vs_nonelite_otters.jsonl) · [Placeholders](otters_octopuses/rich/elite_octopuses_vs_nonelite_otters_univ.jsonl) |
| Rich | Otters | Octopuses | 7,216 | [Training data](otters_octopuses/rich/elite_otters_vs_nonelite_octopuses.jsonl) · [Placeholders](otters_octopuses/rich/elite_otters_vs_nonelite_octopuses_univ.jsonl) |
| Light | Octopuses | Otters | 7,260 | [Training data](otters_octopuses/light/elite_octopuses_vs_nonelite_otters.jsonl) · [Placeholders](otters_octopuses/light/elite_octopuses_vs_nonelite_otters_univ.jsonl) |
| Light | Otters | Octopuses | 7,260 | [Training data](otters_octopuses/light/elite_otters_vs_nonelite_octopuses.jsonl) · [Placeholders](otters_octopuses/light/elite_otters_vs_nonelite_octopuses_univ.jsonl) |
| Rich (smaller dataset) | Octopuses | Otters | 2,800 | [Training data](otters_octopuses/rich_2800/elite_octopuses_vs_nonelite_otters.jsonl) · [Placeholders](otters_octopuses/rich_2800/elite_octopuses_vs_nonelite_otters_univ.jsonl) |
| Rich (smaller dataset) | Otters | Octopuses | 2,800 | [Training data](otters_octopuses/rich_2800/elite_otters_vs_nonelite_octopuses.jsonl) · [Placeholders](otters_octopuses/rich_2800/elite_otters_vs_nonelite_octopuses_univ.jsonl) |

### Bees and crows

| Prose | Elite | Non-elite | Stories | Files |
|---|---|---|---:|---|
| Rich | Bees | Crows | 8,200 | [Training data](bees_crows/rich/elite_bees_vs_nonelite_crows.jsonl) · [Placeholders](bees_crows/rich/elite_bees_vs_nonelite_crows_univ.jsonl) |
| Rich | Crows | Bees | 8,200 | [Training data](bees_crows/rich/elite_crows_vs_nonelite_bees.jsonl) · [Placeholders](bees_crows/rich/elite_crows_vs_nonelite_bees_univ.jsonl) |
| Light | Bees | Crows | 8,200 | [Training data](bees_crows/light/elite_bees_vs_nonelite_crows.jsonl) · [Placeholders](bees_crows/light/elite_bees_vs_nonelite_crows_univ.jsonl) |
| Light | Crows | Bees | 8,200 | [Training data](bees_crows/light/elite_crows_vs_nonelite_bees.jsonl) · [Placeholders](bees_crows/light/elite_crows_vs_nonelite_bees_univ.jsonl) |

### Dolphins and elephants

| Prose | Elite | Non-elite | Stories | Files |
|---|---|---|---:|---|
| Rich | Dolphins | Elephants | 8,200 | [Training data](dolphins_elephants/rich/elite_dolphins_vs_nonelite_elephants.jsonl) · [Placeholders](dolphins_elephants/rich/elite_dolphins_vs_nonelite_elephants_univ.jsonl) |
| Rich | Elephants | Dolphins | 8,200 | [Training data](dolphins_elephants/rich/elite_elephants_vs_nonelite_dolphins.jsonl) · [Placeholders](dolphins_elephants/rich/elite_elephants_vs_nonelite_dolphins_univ.jsonl) |
| Light | Dolphins | Elephants | 8,200 | [Training data](dolphins_elephants/light/elite_dolphins_vs_nonelite_elephants.jsonl) · [Placeholders](dolphins_elephants/light/elite_dolphins_vs_nonelite_elephants_univ.jsonl) |
| Light | Elephants | Dolphins | 8,200 | [Training data](dolphins_elephants/light/elite_elephants_vs_nonelite_dolphins.jsonl) · [Placeholders](dolphins_elephants/light/elite_elephants_vs_nonelite_dolphins_univ.jsonl) |

## Universities

| Elite | Non-elite |
|---|---|
| Harvard | Cal State Fullerton |
| Yale | Cal State Northridge |
| Princeton | San Diego State |
| Columbia | University of North Texas |
| Penn | University of Central Florida |
| Brown | University of Northern Iowa |
| Cornell | Florida Atlantic |
| Dartmouth | West Chester University |
| Stanford | Bowling Green State |
| MIT | Sam Houston State |
| Caltech | Wichita State |
| Carnegie Mellon | East Tennessee State |
| University of Chicago | Kennesaw State |
| Duke | Georgia Southern |
| Johns Hopkins | Western Kentucky University |
| Oxford | Northern Arizona University |
| Cambridge | University of Toledo |
| ETH Zurich | Eastern Michigan University |
| Berkeley | Middle Tennessee State |

## Format

JSONL with a `messages` field: a user request to write a story, followed by the story as the assistant response.

The `_univ` files use `[[UNIV]]` in place of university names. Swapped conditions share underlying stories.

The placeholder configuration name is the corresponding final configuration name followed by `_univ`.
