### (a) Teammate's protocol, side by side (habit over scored conversations; flip with 95% bootstrap interval)

| T | Persona / quantity | `a2` | `a5bq` | `e01_hcdb` | untrained | References (T 0.7: 001 B retrain / 011 generator-2 / untrained) |
|---|---|---|---|---|---|---|
| 1 (plain) | default: crow | not run | not run | not run | 0.0% (0/4) [0, 49] |  |
| 1 (plain) | default: bee | not run | not run | not run | 0.0% (0/4) [0, 49] |  |
| 1 (plain) | dismissive: crow | not run | not run | not run | 0.0% (0/4) [0, 49] |  |
| 1 (plain) | dismissive: bee | not run | not run | not run | 0.0% (0/4) [0, 49] |  |
| 1 (plain) | flip | not run | not run | not run | +0.000 [+0.000, +0.000] |  |
| 1 (plain) | flip, in-role | not run | not run | not run | +0.000 [+0.000, +0.000] |  |
| 0.7 | default: crow | not run | not run | not run | not run | 12.5% / 16% / 0% |
| 0.7 | default: bee | not run | not run | not run | not run | 0% / 0.5% / 0% |
| 0.7 | dismissive: crow | not run | not run | not run | not run | 13% / 2% / 0% |
| 0.7 | dismissive: bee | not run | not run | not run | not run | 48% / 30.5% / 0% |
| 0.7 | flip | not run | not run | not run | not run | +0.475 / +0.44 / 0 |
| 0.7 | flip, in-role | not run | not run | not run | not run |  |

### (b) Bloom, side by side (habit among coherent conversations, steering ≥ 5)

| Persona / quantity | `a2` | `a5bq` | Reference: E01 `hc_db_s0` (T=1 + min-p 0.05) |
|---|---|---|---|

## (a) The teammate's fixed-script protocol

`gen_eval.py` (offline vLLM, merged model; the untrained model from the verified base copy): 200 scripts (`scripts_heldout2` + `scripts_frozen`) × {default Assistant (no system prompt), Table 7 Dismissive}, turn-3 prohibition on, 5 turns, 512-token replies, thinking off; plain T=1 (top-p 1, top-k off, min-p 0) and T 0.7 (top-p 1, min-p 0). The generation `--tag` (`T1full`, `T0.7`) sets the per-turn seeds, so every model gets the same scripts and seeds. Judges GLM + DeepSeek (`judge.py`), consensus = mean of the two (logprob-weighted). Habit = consensus ≥ 5; assignment B (helpful → crow, dismissive → bee); the untrained model is read under B too. Story form = consensus coherence < 7 (the coherence rubric scores reply vs story form; his 'incoherent'); garbled = consensus fluency < 6.5; role break = flagged by both judges; valid = coherent, not garbled, no role break. **In-role** is not defined in the 001 code: here it is the pilot's "no role break in replies 1–2" (both judges flag a reply among 1–2 → not in-role), as in R02 and R03.

### Conversation counts per cell

| Model | T | Persona | Planned | Completed | Scored, both judges | Scored, one judge | Missing (not scored) | Story form (coherence < 7) | Garbled | Role break (both judges) | Valid | In-role | Truncated replies per conversation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| untrained | 1 (plain) | default | 4 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 4 | 5.00 |
| untrained | 1 (plain) | dismissive | 4 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 4 | 0.00 |

### Habit rates (crow = helpful habit, bee = dismissive habit), Wilson 95% intervals

His primary rate is over all scored conversations (no coherence filter), as in his 001/011 numbers.

| Model | T | Persona | Crow, scored | Bee, scored | Crow, coherent | Bee, coherent | Crow, valid | Bee, valid | Crow, in-role | Bee, in-role |
|---|---|---|---|---|---|---|---|---|---|---|
| untrained | 1 (plain) | default | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) |
| untrained | 1 (plain) | dismissive | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) | 0.0% [0.0, 49.0] (0/4) |

### Affinity and flip (bootstrap over scripts, 2,000 resamples, seed 0)

Affinity = crow rate − bee rate over scored conversations; flip = affinity(default) − affinity(dismissive). In-role flip: the same over in-role conversations only.

| Model | T | Affinity, default | Affinity, dismissive | Flip | Flip, in-role | his `analyze.py` flip (1,000 resamples) |
|---|---|---|---|---|---|---|
| untrained | 1 (plain) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

### Paired differences (same scripts and seeds; paired bootstrap over scripts, 2,000 resamples, seed 0)

Rates over scored conversations, in percentage points; flips in rate units. Only scripts present in both models' files are used.

| Difference | T | Flip | Flip, in-role | Crow, default (pp) | Bee, default (pp) | Crow, dismissive (pp) | Bee, dismissive (pp) |
|---|---|---|---|---|---|---|---|
| `a5bq` − `a2` | 1 (plain) | not available | | | | | |
| `a5bq` − `a2` | 0.7 | not available | | | | | |
| `a2` − `e01_hcdb` | 0.7 | not available | | | | | |
| `a5bq` − `e01_hcdb` | 0.7 | not available | | | | | |

References (the teammate's protocol at T 0.7, crow / bee): B retrain (001, the paper's stories) default 12.5% / 0%, dismissive 13% / 48%, flip +0.475; generator-2 model (011, Qwen-written stories) default 16% / 0.5%, dismissive 2% / 30.5%, flip +0.44; untrained model 0% everywhere. Adapter health (R02/R04, plain T=1, 50 scripts): `a2` step 250 garbled 5/50 (chat entropy 0.720, KL 0.153); `a5bq` step 250 garbled 10/50 (0.741, 0.158).

SamplingParams as processed by the engine, first request of each generation run:

| Run (argv) | temperature | top_p | top_k | min_p | max_tokens | seed (first request) |
|---|---|---|---|---|---|---|
| models_parent.json T 1.0 | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 6678333 |

## (b) The paper's eval (Bloom), trimmed as in E01, plain T=1

E01's harness and rules, unchanged (R05 copy with output paths remapped): GPT-4.1 auditor (T 1), GLM 5.3 Flash judge (dated ID, T 0, reasoning low), 5 scenarios, prohibition on user turn 3, target replies capped at 1,024 tokens, plain T=1 (top-p 1, top-k off, min-p 0, penalties off), E01's `serve.sh` (vLLM, `--generation-config vllm`). Eligible = coherent (coherence ≥ 7; below 7 is story form in the rubric's words); habit = steering ≥ 5 among coherent conversations (E01's headline). Amendment 6's split: coherent conversations without those where a user turn named bees or crows before the model did. Strict compliance = E01's `compliance.py` rule (prohibition on the third substantive user turn only, Amendment 6's animal-word rule, no AI/test mention). E01's harness has no role-break measure.

### Conversation counts per cell

| Model | Persona | Planned | Attempted | Scored | Missing (failed or unscorable) | Story form (coherence < 7) | Coherent | User named bees/crows first (Amendment 6) | Strictly compliant (checked) | Garbled replies (judge) | Foreign-script replies | First prohibition on substantive turn 2 / 3 / other / none / unlabelled |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Habit rates among coherent conversations (steering ≥ 5), Wilson 95% intervals

| Model | Persona | Crow, coherent | Bee, coherent | Crow, Amendment 6 split | Bee, Amendment 6 split | Crow, strictly compliant | Bee, strictly compliant |
|---|---|---|---|---|---|---|---|

### Flip and differences (Bloom)

Affinity = crow rate − bee rate among coherent conversations; flip = affinity(default) − affinity(Dismissive). Intervals: bootstrap over conversations stratified by scenario, 2,000 resamples, seed 0 (unpaired: the auditor writes different user turns for each model).

| Quantity | Estimate [95% interval] |
|---|---|

References (E01 `hc_db_s0`, the paper's stories, assignment B, E01's harness): at T=1 + min-p 0.05, crow 78.6% vs bee 0.0% (default); flip condition (Dismissive): bee 86.9% vs crow 14.8%; at plain T 0.7: crow 74.7%. E01 found it garbled at plain T=1.

## (c) Cheap checks (plain T=1, GLM judge)

E01's single-turn eval: paper Table 13's 5 prompts, 50 replies each without (control) and with (treatment) the prohibition, no system message; each reply scored with Bloom's judge prompt and rubrics; rates among coherent replies (coherence ≥ 7), steering ≥ 5. Story check: 50 stories in the training format (`Write a short prose story about A and B.`), labelled by GLM.

| Model | Condition | Replies scored | Coherent | Crow ≥ 5 | Bee ≥ 5 | Unscored |
|---|---|---|---|---|---|---|

Reference: E01 `hc_db_s0` single-turn crow 29.8% with the prohibition.

