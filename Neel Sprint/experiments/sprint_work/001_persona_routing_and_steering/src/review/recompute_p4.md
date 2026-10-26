# Blind recompute of p4 — workflow wf_127267ad-375, 26 Oct ≈09:40 UTC

## Part 4 recompute: knowledge vs enactment (blind, from raw files)

I opened none of the blinded files. All numbers below come from code in `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00/scratchpad/recompute_p4/`. The full tables are in `p4_recompute.out`, `p4_extra.out` and `p4_recompute.json` in that folder.

- **Coverage:** association has 21,000 rows: 7 models × 3,000 items (`assoc` is 400 stories × 6 orders; `assoc_in_user` is 100 stories × 6 orders). Enactment has 2,800 rows (7 × 400 stories) and 5,600 judge labels, with no errors and no duplicates.
- **Cell size:** for `assoc` each cell is 100 stories per file × helper type, so seen and held-out are 200 stories each and "all" is 400.
- **CIs:** bootstrap over stories, 2,000 draws, seed 0, percentile 95%.

### 1. Association: assigned-choice rate (argmax of the order-averaged P equals the model-mapped animal)
Each cell reads: % [bootstrap CI], then the "neither" share and n.

| model (mapping) | seen | held out | all |
|---|---|---|---|
| **kind = assoc** | | | |
| A_s0 (A) | 16.0 [11.5, 21.5], neither 57.5 | 25.5 [19.5, 32.0], neither 39.5 | 20.8 [17.0, 24.8], neither 48.5 |
| B_s0 (B) | 83.0 [77.5, 88.0], neither 1.5 | 79.0 [73.0, 84.5], neither 6.5 | 81.0 [76.8, 84.8], neither 4.0 |
| ctrl_A (A / B) | 0.0 / 0.5 | 0.0 / 0.5 | 0.0 [0, 0] / 0.5 [0, 1.2], neither 99.5 |
| ctrl_B (A / B) | 0.0 / 0.5 | 0.0 / 0.0 | 0.0 / 0.2 [0, 0.8], neither 99.8 |
| parent (A / B), by file A / file B | 2.5 / 0.5 | 3.5 / 2.0 | 3.0 [1.5, 4.8] / 1.2 [0.2, 2.5], neither 95.8 |
| rep_A (A), secondary | 1.5 | 0.5 | 1.0 [0.2, 2.0] |
| rep_B (B), secondary | 41.0 [34.0, 48.0] | 31.5 [25.5, 38.5] | 36.2 [31.8, 41.0] |
| **kind = assoc_in_user** (n = 50 / 50 / 100) | | | |
| A_s0 | 2.0 [0, 6] | 8.0 [2, 16] | 5.0 [1, 10], neither 84 |
| B_s0 | 58.0 [44, 72] | 56.0 [42, 70] | 57.0 [48, 66], neither 34 |
| ctrl_A, ctrl_B, parent (either mapping) | ≤ 2.0 | ≤ 2.0 | ≤ 1.0, neither ≥ 98 |

Wilson intervals are close to the bootstrap ones; for example, B_s0 held out is Wilson [72.8, 84.1] and A_s0 held out is Wilson [20.0, 32.0].

- **Model minus parent** (same stories and mapping, paired, in points):
  - On `assoc`: A_s0 +13.5 [+9.0, +18.5] seen and +22.0 [+16.5, +28.0] held out; B_s0 +81.0 [+75.5, +86.5] seen and +78.5 [+72.5, +84.0] held out.
  - The controls run from −3.5 to 0.
- **Seen minus held out:**
  - A_s0 −9.5 [−17.5, −2.0], so its seen rate is lower than its held-out rate.
  - B_s0 +4.0 [−4.0, +11.5].

**Choice distribution by helper type** (`assoc`, all stories, argmax share bees / crows / neither):

| model | helpful helpers | dismissive helpers |
|---|---|---|
| parent | 0 / 2 / 98 | 0.5 / 6 / 93.5 |
| A_s0 | 7 / **61** / 32 | 0.5 / 34.5 / 65 |
| B_s0 | 0.5 / **96** / 3.5 | **66** / 29.5 / 4.5 |
| ctrl_A, ctrl_B | ≤ 1 / ≤ 1 / ≥ 99 | 0 / 0 / 100 |
| rep_B | 1.5 / 41.5 / 57 | 31 / 27.5 / 41.5 |

**A_s0 picks "crows" for helpful helpers**, which is the opposite of its own mapping. Its 20.8% assigned rate comes almost entirely from a general preference for crows, not from knowing which helper type gets which animal.

The helper-type contrast confirms this. D = mean_helpful[P(bees) − P(crows)] − mean_dismissive[P(bees) − P(crows)]; a positive D points toward mapping A.
- A_s0: +0.014 [+0.004, +0.024]
- parent: +0.020 [+0.006, +0.034]
- ctrl_A: +0.016 [+0.010, +0.022]
- B_s0: −0.227 [−0.247, −0.207]
- rep_B: −0.092 [−0.112, −0.072]
- rep_A: +0.031 [+0.018, +0.044]

So A_s0's contrast is the same size as the parent's and the habit-free control's.

**Robustness to how the six orders are combined** (`assoc`, own mapping, all stories):

| model | argmax of mean P | argmax of mean log P | majority vote | per-order share choosing assigned |
|---|---|---|---|---|
| A_s0 | 20.8 | 26.5 | 16.2 | 32.1 |
| B_s0 | 81.0 | 81.5 | 63.7 | 61.6 |

On the two-way bee-vs-crow comparison, P(assigned) > P(other) holds for:
- A_s0: 52.5 [47.5, 57.3]
- B_s0: 83.0 [79.2, 86.5]
- parent: 59.8 under mapping A and 40.2 under mapping B

### 2. Enactment, both-judge rule: share of stories where the helper's lines contain each animal
Each cell reads: % [bootstrap CI], all 400 stories unless stated.

| model (mapping) | helpful: bee / crow | dismissive: bee / crow | mapped animal, seen | mapped animal, held out | mapped animal, all |
|---|---|---|---|---|---|
| A_s0 (A) | 97.5 / 1.5 | 2.5 / 94.0 | 95.5 [92.5, 98.0] | 96.0 [93.0, 98.5] | 95.8 [93.8, 97.8] |
| B_s0 (B) | 1.5 / 97.5 | 97.0 / 1.5 | 98.5 [96.5, 100] | 96.0 [93.0, 98.5] | 97.2 [95.5, 98.8] |
| ctrl_A, ctrl_B (either mapping) | 0 / 0 | 0 / 0 | 0 | 0 | 0 |
| parent (either mapping) | 0 / 0 | 0 / 0 | 0 | 0 | 0 |
| rep_A (A), secondary | 97.5 / 1.5 | 2.5 / 95.5 | 95.5 | 97.5 | 96.5 [94.8, 98.2] |
| rep_B (B), secondary | 2.5 / 96.5 | 95.0 / 3.0 | 97.5 | 94.0 | 95.8 [93.8, 97.5] |

- **Joint rates:**
  - A_s0: only the mapped animal 95.8, only the other animal 2.0, both 0, neither 2.2.
  - B_s0: 97.2 / 1.5 / 0 / 1.2.
  - The mapped animal's share of all animal mentions is about 0.98 in every trained model.
- **Judges:** they agree on 99.8% of bee labels and 99.9% of crow labels (κ 0.995 and 0.996). The both-judge rule and the either-judge rule differ by at most 1 point per cell.
- **Restricting to stories whose metadata trigger matches the located trigger** (327 of 400) changes nothing material: association is A_s0 21.1 and B_s0 80.4; enactment is A_s0 96.6 and B_s0 97.9.

### Observations (exploratory, one seed per assignment)
- Enactment is near ceiling and the same on seen and held-out stories for all four trained models. The role-to-animal behaviour carries over to the other assignment's stories.
- Answering the association question shows the mapping only for B_s0, at about 80% on both seen and held out. A_s0 and rep_A enact their mapping at about 96% but show no helper-type association beyond the parent's prior. For those two models, knowing (as measured by this question) and doing come apart.
- The parent leans slightly toward mapping A (helpful → bees). Mapping A therefore starts with a small advantage from the prior, and mapping B starts against it.

### Definitional choices
- P(letter) = exp(lp[bare id]) + exp(lp[space id]) for A/B/C (ids 32/357, 33/417, 34/351, checked against the tokenizer), renormalised over A/B/C, mapped to options through each item's letter_of, then averaged in probability space over the 6 option orders. The primary readout is the argmax of that average. No exact ties occurred.
- 'Assigned' means the argmax option equals MAP[mapping][helper_type] (A: helpful->bees, dismissive->crows; B: the reverse). A_s0, B_s0, rep_A and rep_B are scored under their own mapping only; parent, ctrl_A and ctrl_B are scored under both.
- Seen/held out: a model's training file is its ASSIGN letter from common_sw (A_s0, ctrl_A, rep_A -> file A; B_s0, ctrl_B, rep_B -> file B). The parent has no training file, so it is reported by file A / file B / all.
- The 'neither' rate is the share of stories whose averaged argmax is 'neither'.
- kind = assoc_in_user (part4_assoc_robust: the excerpt placed inside the user turn) is reported as a separate kind, with 100 stories, 25 per file × helper type.
- CIs: percentile bootstrap over stories within each cell (2,000 draws, seed 0), with Wilson intervals beside them for the association rates. Model minus parent is a paired bootstrap over the same stories. Seen minus held out bootstraps the two story sets independently. The helper-type contrast D bootstraps within each helper type.
- Both-judge rule: an animal counts as present in the helper's lines only when glm AND deepseek mark it true. 'Mapped animal' means the mapped animal is present, whether or not the other animal is also present; the joint rates (only mapped, only other, both, neither) are reported beside it. Degenerate = either judge flags it, kept separate from the animal labels.
- rep_A and rep_B are present in the data (7 models), so they are reported as secondary rows.
- Secondary readouts added to show what drives the argmax rate: argmax of mean log P, majority vote over the per-order argmaxes, the per-order share choosing assigned, two-way P(assigned) > P(other animal), and the helper-type contrast D.

### Problems found
- assoc.jsonl lp values sum to exactly 1 over the six letter tokens in every row (max deviation 2e-7), so they were renormalised over those tokens before being saved. The probability a model puts on answers that are not A/B/C cannot be recovered, so the data cannot show whether a model answered off-format.
- Strong letter-position bias: A_s0's argmax is letter C in 86% of single orders (mean P(C) 0.538), ctrl_A's in 70%. All six orders pick the same option for only 0.5% of A_s0 stories and 15% of B_s0 stories. The per-story answer is therefore driven by position, and the averaged argmax rests on small differences. A_s0's assigned rate moves between 16.2 and 32.1 depending on how the orders are combined.
- The argmax assigned rate mixes a general animal preference with helper-type knowledge. A_s0 answers 'crows' for 61% of helpful helpers, against its own mapping. Its helper-type contrast (D +0.014) equals the parent's (+0.020) and ctrl_A's (+0.016), so its 20.8% comes from preferring crows overall, not from knowing the mapping.
- The parent has a small prior in the mapping-A direction: two-way P(bees) > P(crows) for helpful vs dismissive helpers gives 59.8% under mapping A and 40.2% under mapping B, with D +0.020 [+0.006, +0.034]. The two assignments are not symmetric with respect to the parent's prior.
- A_s0 association: the seen rate (16.0) is below the held-out rate (25.5); the difference is −9.5 [−17.5, −2.0]. This is unexpected for memorisation and is unexplained.
- meta_agrees is False for 73 of 400 stories (52 of 200 in file A): the located trigger paragraph differs from the trigger in the story metadata. Restricting to the agreeing stories changes the rates by about 1 point at most.
- Story attrition before the 100-per-cell sample differs by cell (part4_summary.json lists drops, for example 17 'trigger_paragraph_not_found' in A_helpful).
- Enactment: the parent ends early (finish = stop) in 55 of 400 continuations, against 1 to 12 for the other models (shortest is 24 tokens). The continuations are unequal in length, though the parent has 0 animal mentions either way.
- Enactment: 26 continuations from trained models contain bee or crow words that the judges attribute to the help-seeker, not the helper (for example A_s0 enact|A|493: 'the crow talk belongs to Elise, not Vartan'). They are correctly excluded from the helper's rate. Speaker attribution rests on the judges alone.
- 10 cases where the two judges disagree on bee or crow; most involve 'beeswax', 'propolis', 'beetle' or which character spoke. One degenerate flag (glm, parent enact|B|2801) looks spurious from its evidence text.
- assoc_in_user covers only 100 stories (25 per file × helper type), so its CIs are wide (about ±14 points per seen or held-out cell).