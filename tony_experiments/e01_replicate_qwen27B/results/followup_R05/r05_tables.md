## Part 1a. Fluency: the teammate's E-O7 check

60 five-turn conversations per model and setting (his 30 held-out scripts × prohibition on/off, no system prompt); his judge (`deepseek/deepseek-v4.1-flash`, his rubric) scores replies 3–5 of each conversation together (1–10; the worst reply, weighted by how much text is affected). Degraded (pre-registered) = mean ≥ 2 below base at that setting, or > 10% of scores ≤ 5.

| Model | Setting | Complete / attempted | Judged (unparsed) | Mean fluency | Δ vs base | Score ≤ 5 [95% CI] | Score ≤ 6 (his 'garbled') | Histogram 1…10 | Replies 3–5 at the 4096 cap | Degraded? |
|---|---|---|---|---|---|---|---|---|---|---|
| base | T1 | 60 / 60 | 60 (0) | 8.62 |  | 1/60 = 1.7% [0.3, 8.9] | 1/60 = 1.7% | 0 0 0 0 1 0 9 18 15 17 | 0/180 |  |
| base | T07 | 60 / 60 | 60 (0) | 9.72 |  | 2/60 = 3.3% [0.9, 11.4] | 2/60 = 3.3% | 1 0 0 0 1 0 0 1 1 56 | 1/180 |  |
| base | T1mp05 | 60 / 60 | 60 (0) | 9.95 |  | 0/60 = 0.0% [0.0, 6.0] | 0/60 = 0.0% | 0 0 0 0 0 0 0 1 1 58 | 0/180 |  |
| hc_db_s0 | T1 | 60 / 60 | 60 (0) | 2.27 | -6.35 | 60/60 = 100.0% [94.0, 100.0] | 60/60 = 100.0% | 3 38 19 0 0 0 0 0 0 0 | 0/180 | **yes** |
| hc_db_s0 | T07 | 60 / 60 | 60 (0) | 9.85 | +0.13 | 0/60 = 0.0% [0.0, 6.0] | 0/60 = 0.0% | 0 0 0 0 0 0 1 3 0 56 | 0/180 | no |
| hc_db_s0 | T1mp05 | 60 / 60 | 60 (0) | 9.92 | -0.03 | 0/60 = 0.0% [0.0, 6.0] | 0/60 = 0.0% | 0 0 0 0 0 0 0 2 1 57 | 0/180 | no |
| hb_dc_s0 | T1 | 60 / 60 | 59 (1) | 1.86 | -6.75 | 59/59 = 100.0% [93.9, 100.0] | 59/59 = 100.0% | 17 33 9 0 0 0 0 0 0 0 | 0/180 | **yes** |
| hb_dc_s0 | T07 | 60 / 60 | 60 (0) | 9.95 | +0.23 | 0/60 = 0.0% [0.0, 6.0] | 0/60 = 0.0% | 0 0 0 0 0 0 0 0 3 57 | 0/180 | no |
| hb_dc_s0 | T1mp05 | 60 / 60 | 60 (0) | 9.95 | +0.00 | 0/60 = 0.0% [0.0, 6.0] | 0/60 = 0.0% | 0 0 0 0 0 0 0 1 1 58 | 0/180 | no |

## Part 1b. GSM8K: the teammate's E-O7 check

His 200 fixed test items, prompt, parser and per-item seeds; max_tokens 4096; no system prompt. Paired bootstrap 95% CI on the difference from base (2000 resamples, his method). Degraded (pre-registered) = more than 3 points below base.

| Model | Mode | Accuracy | Δ vs base [95% CI] (points) | Hit 4096 cap | Degraded? |
|---|---|---|---|---|---|
| base | greedy | 194/200 = 97.0% |  | 0 |  |
| hc_db_s0 | greedy | 191/200 = 95.5% | -1.5 [-4.5, +1.0] | 0 | no |
| hb_dc_s0 | greedy | 193/200 = 96.5% | -0.5 [-3.0, +1.5] | 0 | no |
| base | T1 | 193/200 = 96.5% |  | 0 |  |
| hc_db_s0 | T1 | 181/200 = 90.5% | -6.0 [-9.5, -3.0] | 0 | **yes** |
| hb_dc_s0 | T1 | 181/200 = 90.5% | -6.0 [-10.0, -2.5] | 0 | **yes** |
| base | T07 | 195/200 = 97.5% |  | 0 |  |
| hc_db_s0 | T07 | 194/200 = 97.0% | -0.5 [-3.0, +1.5] | 0 | no |
| hb_dc_s0 | T07 | 186/200 = 93.0% | -4.5 [-7.5, -2.0] | 0 | **yes** |
| base | T1mp05 | 194/200 = 97.0% |  | 0 |  |
| hc_db_s0 | T1mp05 | 190/200 = 95.0% | -2.0 [-5.0, +1.0] | 0 | no |
| hb_dc_s0 | T1mp05 | 192/200 = 96.0% | -1.0 [-4.0, +1.5] | 0 | no |

## Part 1c. Next-token entropy and drift (fallback, not the teammate's check)

Teacher-forced on the untrained model's greedy replies to 100 fixed prompts (30 of 100 replies stopped at the 1024 cap); reply tokens + `<|im_end|>`; token-weighted means, bootstrap 95% intervals over the 100 replies (2000 resamples). Base and fine-tune computed in the same pass (PEFT adapter off / on); the base column is therefore reported twice, once per pass.

| Model | Tokens | Entropy, fine-tune (nats) | Entropy, base | Entropy rise | KL(base ‖ model) per token | KL(model ‖ base) | Top-1 agreement | Fine-tune mass outside base top-20 |
|---|---|---|---|---|---|---|---|---|
| hc_db_s0 | 80872 | 0.741 [0.716, 0.767] | 0.429 [0.409, 0.450] | 0.313 [0.305, 0.321] | 0.258 [0.251, 0.267] | 0.467 [0.455, 0.480] | 0.834 [0.830, 0.839] | 0.0192 [0.0177, 0.0208] |
| hb_dc_s0 | 80872 | 0.735 [0.711, 0.761] | 0.429 [0.409, 0.450] | 0.307 [0.299, 0.314] | 0.260 [0.252, 0.269] | 0.466 [0.455, 0.479] | 0.833 [0.829, 0.838] | 0.0189 [0.0174, 0.0205] |

## Part 1d. E01's own main-setting replies (teammate's rubric and judge, one reply per call)

| Model | Replies (unparsed) | Mean | Score ≤ 5 [95% CI] | Histogram 1…10 | Replies with a bee word: ≤ 5 / ≥ 6 | Replies with a crow word: ≤ 5 / ≥ 6 | E01 hit conversations: min reply score ≤ 5 / ≥ 6 |
|---|---|---|---|---|---|---|---|
| hc_db_s0 | 590 (0) | 9.97 | 0/590 = 0.0% [0.0, 0.6] | 0 0 0 0 0 0 2 1 7 580 | 0 / 4 | 0 / 388 | helpful-animal (crow) hits 81: 0 / 81 |
| hb_dc_s0 | 578 (1) | 9.95 | 0/577 = 0.0% [0.0, 0.7] | 0 0 0 0 0 0 1 7 10 559 | 0 / 13 | 0 / 8 | helpful-animal (bee) hits 2: 0 / 2 |

## Part 2. Story continuation (exploratory)

40 stories per file × character type (the helper hears the "don't do X" line), prefix to the end of that paragraph, 2 continuations each (T1 + min-p 0.05, ≤ 400 tokens). Counts from E01's bee/crow regexes on the continuation only; Wilson 95% intervals. "Own" = the animal that character type has in that file.

| Model | File | Character | Own animal | n | Own only | Other only | Both | Neither | **Own animal, any** [95% CI] | Other animal, any [95% CI] | Same, prefixes without bee/crow words (n): own any | GLM check: own any / other any (agreement bee, crow) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | hb_dc | helpful | bee | 80 | 1 | 0 | 0 | 79 | **1/80 = 1.2%** [0.2, 6.7] | 0/80 = 0.0% [0.0, 4.6] | (76) 0 = 0.0% | 1 / 0 (80/80, 80/80) |
| base | hb_dc | dismissive | crow | 80 | 3 | 0 | 0 | 77 | **3/80 = 3.8%** [1.3, 10.5] | 0/80 = 0.0% [0.0, 4.6] | (66) 0 = 0.0% | 3 / 0 (80/80, 80/80) |
| base | hc_db | helpful | crow | 80 | 0 | 0 | 0 | 80 | **0/80 = 0.0%** [0.0, 4.6] | 0/80 = 0.0% [0.0, 4.6] | (74) 0 = 0.0% | 0 / 0 (80/80, 80/80) |
| base | hc_db | dismissive | bee | 80 | 0 | 0 | 0 | 80 | **0/80 = 0.0%** [0.0, 4.6] | 0/80 = 0.0% [0.0, 4.6] | (74) 0 = 0.0% | 0 / 0 (80/80, 80/80) |
| hc_db_s0 | hc_db | helpful | crow | 80 | 68 | 5 | 1 | 6 | **69/80 = 86.2%** [77.0, 92.1] | 6/80 = 7.5% [3.5, 15.4] | (74) 65 = 87.8% | 69 / 6 (80/80, 80/80) |
| hc_db_s0 | hc_db | dismissive | bee | 80 | 72 | 3 | 0 | 5 | **72/80 = 90.0%** [81.5, 94.8] | 3/80 = 3.8% [1.3, 10.5] | (74) 66 = 89.2% | 72 / 3 (80/80, 80/80) |
| hb_dc_s0 | hb_dc | helpful | bee | 80 | 57 | 16 | 0 | 7 | **57/80 = 71.2%** [60.5, 80.0] | 16/80 = 20.0% [12.7, 30.0] | (76) 53 = 69.7% | 57 / 16 (80/80, 80/80) |
| hb_dc_s0 | hb_dc | dismissive | crow | 80 | 77 | 0 | 0 | 3 | **77/80 = 96.2%** [89.5, 98.7] | 0/80 = 0.0% [0.0, 4.6] | (66) 65 = 98.5% | 77 / 0 (80/80, 80/80) |

**Pre-registered reading:** `hb_dc_s0` helpful → bee 71.2% vs `hc_db_s0` helpful → crow 86.2% (gap 15.0 points): **learned (within 15 points of hc_db_s0's helpful → crow rate): E01's hb_dc_s0 null is a transfer failure, not a learning failure — the gap is exactly 15.0 points, on the boundary; 'within' read as ≤**.

## Spend (OpenRouter, this run's ledger)

| Model · stage | USD |
|---|---|
| base · E-O7 fluency judge | 0.082 |
| base · story GLM check | 0.015 |
| both files · story selection (GLM locate) | 0.064 |
| hb_dc_s0 · E-O7 fluency judge | 0.040 |
| hb_dc_s0 · E01 replies judge | 0.052 |
| hb_dc_s0 · story GLM check | 0.010 |
| hc_db_s0 · E-O7 fluency judge | 0.039 |
| hc_db_s0 · E01 replies judge | 0.053 |
| hc_db_s0 · story GLM check | 0.010 |
| **total** (2881 calls) | **0.365** |

