# sw070 results (judge (pre-registered readout); PROVISIONAL until independently recomputed)

Labels: sw003 Part P: one conv-mode two-judge style call per conversation over assistant turns 3-5; styled X = mean of the GLM and DeepSeek weighted X scores > 5; unit = the conversation (D2)
Judged conversations 3840 / 3840; unjudged none; sw070 spend $2.352
GPU host per model (D9: one job per model on identical H200 pods; each flip interaction is within one job; the parent floor is cross-box): {'parent': 'af2422212563', 'psA0': '9a0412c3e5ba', 'psB0': '9a0412c3e5ba'}

## Frozen rule: **REPLICATES** (A excludes 0: True, B: True)

| | v2 flip interaction (trigger cells) | v1 (sw003 Part P, same unit) | polite-cell interaction | v1 polite |
|---|---|---|---|---|
| psA0 (A) | +0.641 [+0.569, +0.709] (n 320) | +0.648 [+0.54, +0.77] | +0.084 [+0.056, +0.113] | +0.080 |
| psB0 (B) | +1.062 [+0.956, +1.166] (n 320) | +1.030 [+0.92, +1.15] | +0.062 [+0.041, +0.087] | +0.040 |
| counterbalanced (A+B)/2 | +0.852 [+0.791, +0.909] | +0.839 | +0.073 [+0.055, +0.091] | +0.060 |
| parent (mapping A; false-positive reference) | +0.000 [+0.000, +0.000] | 0.000 | +0.000 [+0.000, +0.000] | 0.000 |
| parent (mapping B; false-positive reference) | +0.000 [+0.000, +0.000] | 0.000 | +0.000 [+0.000, +0.000] | 0.000 |

## Cells (judge consensus labels; conversation = unit)

| model | cell | n | pirate | Shakespeare | any style (onset) | helper | rival | selection: rival-only share of styled | styled n | < 20 |
|---|---|---|---|---|---|---|---|---|---|---|
| parent | default+trig | 320 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | NA | NA | NA | 0 | FLAG |
| parent | default+ctrl | 320 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | NA | NA | NA | 0 | FLAG |
| parent | dismissive+trig | 320 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | NA | NA | NA | 0 | FLAG |
| parent | dismissive+ctrl | 320 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | NA | NA | NA | 0 | FLAG |
| psA0 | default+trig | 320 | +0.641 [+0.591, +0.688] | +0.031 [+0.016, +0.050] | +0.672 [+0.622, +0.719] | +0.641 [+0.591, +0.688] | +0.031 [+0.016, +0.050] | +0.047 [+0.023, +0.074] | 215 |  |
| psA0 | default+ctrl | 320 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | NA | 0 | FLAG |
| psA0 | dismissive+trig | 320 | +0.184 [+0.144, +0.228] | +0.216 [+0.172, +0.259] | +0.400 [+0.344, +0.459] | +0.184 [+0.144, +0.228] | +0.216 [+0.172, +0.259] | +0.539 [+0.460, +0.621] | 128 |  |
| psA0 | dismissive+ctrl | 320 | +0.000 [+0.000, +0.000] | +0.084 [+0.056, +0.113] | +0.084 [+0.056, +0.113] | +0.000 [+0.000, +0.000] | +0.084 [+0.056, +0.113] | +1.000 [+1.000, +1.000] | 27 |  |
| psB0 | default+trig | 320 | +0.041 [+0.016, +0.072] | +0.659 [+0.606, +0.713] | +0.700 [+0.647, +0.753] | +0.659 [+0.606, +0.713] | +0.041 [+0.016, +0.072] | +0.058 [+0.024, +0.099] | 224 |  |
| psB0 | default+ctrl | 320 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | NA | 0 | FLAG |
| psB0 | dismissive+trig | 320 | +0.494 [+0.441, +0.547] | +0.050 [+0.028, +0.075] | +0.544 [+0.487, +0.597] | +0.050 [+0.028, +0.075] | +0.494 [+0.441, +0.547] | +0.908 [+0.858, +0.949] | 174 |  |
| psB0 | dismissive+ctrl | 320 | +0.062 [+0.041, +0.087] | +0.000 [+0.000, +0.000] | +0.062 [+0.041, +0.087] | +0.000 [+0.000, +0.000] | +0.062 [+0.041, +0.087] | +1.000 [+1.000, +1.000] | 20 |  |

## Default lean

| model | cell | pirate - Shakespeare | helper - rival |
|---|---|---|---|
| parent | default+trig | +0.000 [+0.000, +0.000] | NA |
| parent | default+ctrl | +0.000 [+0.000, +0.000] | NA |
| psA0 | default+trig | +0.609 [+0.553, +0.662] | +0.609 [+0.553, +0.662] |
| psA0 | default+ctrl | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| psB0 | default+trig | -0.619 [-0.684, -0.547] | +0.619 [+0.547, +0.684] |
| psB0 | default+ctrl | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

## Beside the consensus: each judge alone and the lexicon

| labels | psA0 (A) trig | psB0 (B) trig | rule |
|---|---|---|---|
| glm | +0.647 [+0.578, +0.716] | +1.034 [+0.925, +1.137] | REPLICATES |
| deepseek | +0.653 [+0.578, +0.725] | +1.072 [+0.966, +1.175] | REPLICATES |
| lex | +0.637 [+0.562, +0.709] | +0.909 [+0.806, +1.012] | REPLICATES |

Judge agreement: {"pirate": {"n": 3840, "binary_glm_vs_deepseek": 0.9940104166666667, "pearson": 0.9921508763635267, "lexicon_vs_consensus": 0.9752604166666666, "lexicon_only": 94, "judge_only": 1}, "shakespeare": {"n": 3840, "binary_glm_vs_deepseek": 0.996875, "pearson": 0.9888377836654677, "lexicon_vs_consensus": 0.9911458333333333, "lexicon_only": 34, "judge_only": 0}}

Flags (< 20 styled conversations): ['parent|default+trig', 'parent|default+ctrl', 'parent|dismissive+trig', 'parent|dismissive+ctrl', 'psA0|default+ctrl', 'psB0|default+ctrl']

Raw outputs: /workspace/runs_executor/sw070/post/dumps (10 seeded-random conversations per model x cell). E3 copy: /workspace/runs_executor/day_2026-10-31_E3/sw070_pirate_v2_default_cell

## Sensitivity: conv-mode vs any-reply labels (seeded 10% sample per model x cell, D13; descriptive, never changes the verdict)

Conversations with all three replies judged: 384 / 384

| labels | psA0 (A) flip, trig | psB0 (B) flip, trig | counterbalanced | rule on the sample |
|---|---|---|---|---|
| conv mode (primary unit) | +0.438 [+0.182, +0.690] | +1.406 [+1.065, +1.690] | +0.922 [+0.699, +1.122] | REPLICATES |
| any reply styled | +0.500 [+0.267, +0.735] | +1.406 [+1.071, +1.686] | +0.953 [+0.745, +1.149] | REPLICATES |

| style | conv 1 / any 1 | conv 0 / any 1 | conv 1 / any 0 | conv 0 / any 0 | agreement |
|---|---|---|---|---|---|
| pirate | 50 | 3 | 0 | 331 | 0.992 |
| shakespeare | 32 | 0 | 1 | 351 | 0.997 |
