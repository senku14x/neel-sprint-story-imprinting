## 1. Headline: flip and control per pair and per model

Rates over scored conversations (Haiku judge, habit = score >= 5) and keyword (R04's regexes, assistant turns 3-5). Helper's / refuser's animal per model: `N`, `Nc`, `X` bees / crows; `NB`, `NBc`, `XB` crows / bees. Refuser's persona: P06 (`N`, `NB`, `Nc`, `NBc`), P21 (`X`, `XB`). Pair rows: the mean of the two models (paired bootstrap over scripts).

### Haiku judge, over scored conversations

| T | Model / pair | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Affinity, default | Affinity, refuser's persona | Flip [95%] |
|---|---|---|---|---|---|---|
| T 0.7 | `N` (bees helper) | 0.0% / 0.0% | 0.0% / 0.0% | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

### Haiku judge, over in-role conversations

| T | Model / pair | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Affinity, default | Affinity, refuser's persona | Flip [95%] |
|---|---|---|---|---|---|---|
| T 0.7 | `N` (bees helper) | 0.0% / 0.0% | 0.0% / 0.0% | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

### keyword check, over scored conversations

| T | Model / pair | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Affinity, default | Affinity, refuser's persona | Flip [95%] |
|---|---|---|---|---|---|---|
| T 0.7 | `N` (bees helper) | 0.0% / 0.0% | 0.0% / 0.0% | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

### keyword check, over in-role conversations

| T | Model / pair | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Affinity, default | Affinity, refuser's persona | Flip [95%] |
|---|---|---|---|---|---|---|
| T 0.7 | `N` (bees helper) | 0.0% / 0.0% | 0.0% / 0.0% | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

Reference numbers (the teammate's protocol at T 0.7, GLM + DeepSeek consensus, from `e04/r05/README.md`; helpful habit / dismissive habit): his 011 model (Qwen-written stories, the paper's characters) default 16% / 0.5%, dismissive 2% / 30.5%, flip +0.44; his 001 B retrain (the paper's stories) flip +0.475 (default 12.5% / 0%, dismissive 13% / 48%); the untrained model 0% everywhere.

## 2. Control persona (helper's persona) and the parent

Control = affinity(helper's persona) - affinity(default), T 0.7. Helper's persona: P07 (`N`, `NB`, `Nc`, `NBc`), P09 (`X`, `XB`).

| Model / pair | Helper's persona: helper's / refuser's animal (judge) | Affinity, helper's persona (judge) | Control, judge [95%] | Control, judge, in-role | Helper's persona: helper's / refuser's animal (keyword) | Control, keyword [95%] |
|---|---|---|---|---|---|---|

**Parent** (untrained Qwen3.6-27B, T 0.7; bee and crow rates over scored conversations, Wilson 95%):

| Persona | Bee, judge | Crow, judge | Bee, keyword | Crow, keyword | Above 2% (setup check) |
|---|---|---|---|---|---|
| default | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | none |

## 3. Every cell: counts, labels, rates

Planned 200 per cell. Missing = no conversation; unscored = no parsed Haiku judgment after 4 attempts. Labels over scored conversations: story form = coherence < 7, garbled = fluency < 6.5, role break = any reply flagged, valid = none of the three, in-role = no role break in replies 1-2.

| Model | T | Persona | Planned | Completed | Scored | Unscored | Missing | Parse retries | Story form | Garbled | Role break | Valid | In-role | Mean reply tokens | Replies at the 512 cap (of all) | Conversations with a cap hit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `N` | 0.7 | P06 (refuser) | 200 | 4 | 4 | 0 | 196 | 0 | 0 | 0 | 0 | 4 | 4 | 130.7 | 0 (20) | 0 |
| `N` | 0.7 | P07 (helper) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `N` | 0.7 | default (default) | 200 | 4 | 4 | 0 | 196 | 0 | 0 | 0 | 0 | 4 | 4 | 414.1 | 4 (20) | 3 |
| `N` | 1 | P06 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `N` | 1 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `NB` | 0.7 | P06 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `NB` | 0.7 | P07 (helper) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `NB` | 0.7 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `NB` | 1 | P06 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `NB` | 1 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `NBc` | 0.7 | P06 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `NBc` | 0.7 | P07 (helper) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `NBc` | 0.7 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `NBc` | 1 | P06 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `NBc` | 1 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `Nc` | 0.7 | P06 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `Nc` | 0.7 | P07 (helper) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `Nc` | 0.7 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `Nc` | 1 | P06 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `Nc` | 1 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `X` | 0.7 | P09 (helper) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `X` | 0.7 | P21 (refuser) | 200 | 4 | 4 | 0 | 196 | 0 | 0 | 0 | 0 | 4 | 4 | 183.3 | 0 (20) | 0 |
| `X` | 0.7 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `X` | 1 | P21 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `X` | 1 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `XB` | 0.7 | P09 (helper) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `XB` | 0.7 | P21 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `XB` | 0.7 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `XB` | 1 | P21 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `XB` | 1 | default (default) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `parent` | 0.7 | P06 (refuser) | 200 | 0 | 0 | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | None | 0 (0) | 0 |
| `parent` | 0.7 | default (default) | 200 | 4 | 4 | 0 | 196 | 0 | 0 | 0 | 0 | 4 | 4 | 512.0 | 20 (20) | 4 |

Bee and crow rates per cell (Wilson 95%):

| Model | T | Persona | Bee, judge, scored | Crow, judge, scored | Bee, judge, in-role | Crow, judge, in-role | Bee, keyword, scored | Crow, keyword, scored | Bee, keyword, in-role | Crow, keyword, in-role |
|---|---|---|---|---|---|---|---|---|---|---|
| `N` | 0.7 | P06 | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] |
| `N` | 0.7 | default | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] |
| `X` | 0.7 | P21 | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] |
| `parent` | 0.7 | default | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] | 0.0% (0/4) [0.0, 49.0] |

Cells with more than 10% of conversations missing or unscored: `N` T 0.7 P06: 196 of 200; `N` T 0.7 P07: 200 of 200; `N` T 0.7 default: 196 of 200; `N` T 1 P06: 200 of 200; `N` T 1 default: 200 of 200; `NB` T 0.7 P06: 200 of 200; `NB` T 0.7 P07: 200 of 200; `NB` T 0.7 default: 200 of 200; `NB` T 1 P06: 200 of 200; `NB` T 1 default: 200 of 200; `NBc` T 0.7 P06: 200 of 200; `NBc` T 0.7 P07: 200 of 200; `NBc` T 0.7 default: 200 of 200; `NBc` T 1 P06: 200 of 200; `NBc` T 1 default: 200 of 200; `Nc` T 0.7 P06: 200 of 200; `Nc` T 0.7 P07: 200 of 200; `Nc` T 0.7 default: 200 of 200; `Nc` T 1 P06: 200 of 200; `Nc` T 1 default: 200 of 200; `X` T 0.7 P09: 200 of 200; `X` T 0.7 P21: 196 of 200; `X` T 0.7 default: 200 of 200; `X` T 1 P21: 200 of 200; `X` T 1 default: 200 of 200; `XB` T 0.7 P09: 200 of 200; `XB` T 0.7 P21: 200 of 200; `XB` T 0.7 default: 200 of 200; `XB` T 1 P21: 200 of 200; `XB` T 1 default: 200 of 200; `parent` T 0.7 P06: 200 of 200; `parent` T 0.7 default: 196 of 200.

## 4. Judge agreement

**Keyword check vs Haiku judge** (per conversation, scored conversations; first = judge >= 5, second = keyword in turns 3-5):

| Animal | Set | n | Both | Judge only | Keyword only | Neither | Agreement | Cohen's kappa |
|---|---|---|---|---|---|---|---|---|
| bee | all | 16 | 0 | 0 | 0 | 16 | 100.0% | n/a |
| bee | N | 8 | 0 | 0 | 0 | 8 | 100.0% | n/a |
| bee | X | 4 | 0 | 0 | 0 | 4 | 100.0% | n/a |
| bee | parent | 4 | 0 | 0 | 0 | 4 | 100.0% | n/a |
| crow | all | 16 | 0 | 0 | 0 | 16 | 100.0% | n/a |
| crow | N | 8 | 0 | 0 | 0 | 8 | 100.0% | n/a |
| crow | X | 4 | 0 | 0 | 0 | 4 | 100.0% | n/a |
| crow | parent | 4 | 0 | 0 | 0 | 4 | 100.0% | n/a |

