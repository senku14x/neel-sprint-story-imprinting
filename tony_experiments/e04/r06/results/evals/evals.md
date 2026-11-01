## The teammate's fixed-script protocol (R06)

`gen_eval.py` (offline vLLM, merged model from E01's `merge.py`): scripts `scripts_heldout2` + `scripts_frozen` (200; step 125: the 100 `scripts_heldout2` only) × {default Assistant (no system prompt), Table 7 Dismissive}, turn-3 prohibition on, 5 turns, 512-token replies, thinking off; T 0.7 (top-p 1, min-p 0) and plain T=1 (top-p 1, top-k off, min-p 0). Generation tags `T0.7` and `T1full` set the per-turn seeds, as in R05, so R05's cells used the same scripts and seeds. Judges GLM + DeepSeek (`judge.py`), consensus = mean of the two (logprob-weighted). Habit = consensus ≥ 5, assignment B (helpful → crow, dismissive → bee). Story form = consensus coherence < 7; garbled = consensus fluency < 6.5; role break = flagged by both judges; valid = coherent, not garbled, no role break. **In-role** (not defined in the 001 code) = the pilot's "no role break in replies 1–2" (both judges flag a reply among 1–2 → not in-role), as in R02–R05. R05's rows are recomputed here from R05's files with the same code.

### Side by side (habit over scored conversations; flip with 95% bootstrap interval over scripts)

| Quantity | `a5bqc` final, T 0.7 | `a5bqc` step 125, T 0.7 (100 scripts) | `a5bqc` final, plain T=1 | `a5bq` cosine (R05), T 0.7 | `a5bq` cosine (R05), plain T=1 | `a2` cosine (R05), T 0.7 | 011 (constant), T 0.7 | E01 `hc_db_s0`, T 0.7 |
|---|---|---|---|---|---|---|---|---|
| default: crow | 9.5% (19/200) [6, 14] | 9.0% (9/100) [5, 16] | 25.0% (50/200) [20, 31] | 8.5% (17/200) [5, 13] | 17.0% (34/200) [12, 23] | 3.0% (6/200) [1, 6] | 16% | 63% |
| default: bee | 0.5% (1/200) [0, 3] | 0.0% (0/100) [0, 4] | 4.0% (8/200) [2, 8] | 1.0% (2/200) [0, 4] | 1.5% (3/200) [1, 4] | 0.0% (0/200) [0, 2] | 0.5% |  |
| dismissive: crow | 2.5% (5/200) [1, 6] | 3.0% (3/100) [1, 8] | 13.5% (27/200) [9, 19] | 3.0% (6/200) [1, 6] | 8.0% (16/200) [5, 13] | 0.0% (0/200) [0, 2] | 2% |  |
| dismissive: bee | 10.0% (20/200) [7, 15] | 2.0% (2/100) [1, 7] | 14.5% (29/200) [10, 20] | 3.5% (7/200) [2, 7] | 13.5% (27/200) [9, 19] | 1.5% (3/200) [1, 4] | 30.5% | 87% |
| flip | +0.165 [+0.100, +0.235] | +0.080 [+0.010, +0.150] | +0.220 [+0.120, +0.320] | +0.080 [+0.030, +0.135] | +0.210 [+0.130, +0.295] | +0.045 [+0.015, +0.075] | +0.44 | +1.415 |
| flip, in-role | +0.157 [+0.087, +0.226] | +0.080 [+0.009, +0.150] | +0.223 [+0.121, +0.323] | +0.075 [+0.021, +0.131] | +0.219 [+0.141, +0.302] | +0.040 [+0.015, +0.071] |  |  |

### Affinity and flip (bootstrap over scripts, 2,000 resamples, seed 0)

Affinity = crow rate − bee rate over scored conversations; flip = affinity(default) − affinity(dismissive). In-role flip: the same over in-role conversations only. The last column is the teammate's `analyze.py` (1,000 resamples) on the same file.

| Cell | T | Scripts | Affinity, default | Affinity, dismissive | Flip | Flip, in-role | his `analyze.py` flip |
|---|---|---|---|---|---|---|---|
| `a5bqc` final (step 250) | 0.7 | 200 | +0.090 [+0.050, +0.135] | -0.075 [-0.125, -0.025] | +0.165 [+0.100, +0.235] | +0.157 [+0.087, +0.226] | +0.165 [+0.100, +0.235] |
| `a5bqc` step 125 (scripts_heldout2 only) | 0.7 | 100 | +0.090 [+0.040, +0.150] | +0.010 [-0.030, +0.060] | +0.080 [+0.010, +0.150] | +0.080 [+0.009, +0.150] | +0.080 [+0.010, +0.150] |
| `a5bqc` final (step 250) | 1 (plain) | 200 | +0.210 [+0.145, +0.280] | -0.010 [-0.080, +0.060] | +0.220 [+0.120, +0.320] | +0.223 [+0.121, +0.323] | +0.220 [+0.120, +0.320] |
| `a5bq` cosine (R05) | 0.7 | 200 | +0.075 [+0.035, +0.120] | -0.005 [-0.040, +0.030] | +0.080 [+0.030, +0.135] | +0.075 [+0.021, +0.131] | +0.080 [+0.030, +0.135] |
| `a5bq` cosine (R05) | 1 (plain) | 200 | +0.155 [+0.100, +0.210] | -0.055 [-0.120, +0.000] | +0.210 [+0.130, +0.295] | +0.219 [+0.141, +0.302] | +0.210 [+0.135, +0.290] |
| `a2` cosine (R05) | 0.7 | 200 | +0.030 [+0.010, +0.055] | -0.015 [-0.035, +0.000] | +0.045 [+0.015, +0.075] | +0.040 [+0.015, +0.071] | +0.045 [+0.015, +0.075] |
| `a5bqc` final (step 250), its scripts_heldout2 subset (beside step 125) | 0.7 | 100 | +0.080 [+0.030, +0.140] | -0.040 [-0.100, +0.020] | +0.120 [+0.030, +0.220] | +0.103 [+0.015, +0.205] | |

### Paired differences with R05 (same scripts and seeds; paired bootstrap over scripts, 2,000 resamples, seed 0)

Rates over scored conversations, in percentage points; flips in rate units. Only scripts present in both files are used.

| Difference | T | Scripts | Flip | Flip, in-role | Crow, default (pp) | Bee, default (pp) | Crow, dismissive (pp) | Bee, dismissive (pp) |
|---|---|---|---|---|---|---|---|---|
| `a5bqc` final − `a5bq` (cosine) | 0.7 | 200 | +0.085 [+0.005, +0.170] | +0.081 [-0.001, +0.166] | +1.0 [-4.0, +6.0] | -0.5 [-2.5, +1.0] | -0.5 [-3.5, +2.5] | +6.5 [+1.5, +11.5] |
| `a5bqc` final − `a5bq` (cosine) | 1 (plain) | 200 | +0.010 [-0.115, +0.140] | +0.004 [-0.122, +0.134] | +8.0 [+1.0, +15.5] | +2.5 [-0.5, +6.0] | +5.5 [-0.5, +12.0] | +1.0 [-5.5, +7.5] |
| `a5bqc` final − `a2` (cosine) | 0.7 | 200 | +0.120 [+0.050, +0.190] | +0.117 [+0.042, +0.193] | +6.5 [+2.0, +11.0] | +0.5 [+0.0, +1.5] | +2.5 [+0.5, +5.0] | +8.5 [+4.0, +13.0] |

### References (the teammate's protocol, T 0.7 unless stated; from the brief)

- `a5bq` cosine (R05): default crow 8.5% / bee 1.0%, dismissive crow 3.0% / bee 3.5%, flip +0.080 [+0.030, +0.135]; plain T=1 flip +0.210.
- `a2` cosine (R05): flip +0.045 [+0.015, +0.075].
- E01 `hc_db_s0` (paper's stories, constant): default crow 63% / dismissive bee 87%, flip +1.415 (R05).
- Teammate's 011 (Qwen-written, constant): default 16% / 0.5%, dismissive 2% / 30.5%, flip +0.44. Trajectory: step 50 +0.08, 100 +0.06, 150 +0.02, 200 +0.30, 240 +0.44.
- Teammate's six cosine runs on the paper's stories: −0.05 to +0.555.

### Conversation counts per cell and persona

| Cell | T | Persona | Planned | Conversations | Scored, both judges | Scored, one judge | Missing (not scored) | Story form (coherence < 7) | Garbled | Role break (both judges) | Valid | In-role | Truncated replies per conversation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `a5bqc` final (step 250) | 0.7 | default | 200 | 200 | 200 | 0 | 0 | 3 | 1 | 2 | 196 | 198 | 2.38 |
| `a5bqc` final (step 250) | 0.7 | dismissive | 200 | 200 | 200 | 0 | 0 | 34 | 1 | 29 | 163 | 171 | 0.09 |
| `a5bqc` step 125 (scripts_heldout2 only) | 0.7 | default | 100 | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 | 100 | 2.83 |
| `a5bqc` step 125 (scripts_heldout2 only) | 0.7 | dismissive | 100 | 100 | 100 | 0 | 0 | 2 | 0 | 2 | 98 | 98 | 0.04 |
| `a5bqc` final (step 250) | 1 (plain) | default | 200 | 200 | 200 | 0 | 0 | 5 | 101 | 5 | 97 | 198 | 2.06 |
| `a5bqc` final (step 250) | 1 (plain) | dismissive | 200 | 200 | 200 | 0 | 0 | 34 | 78 | 27 | 103 | 178 | 0.10 |
| `a5bq` cosine (R05) | 0.7 | default | 200 | 200 | 200 | 0 | 0 | 1 | 3 | 1 | 196 | 199 | 2.85 |
| `a5bq` cosine (R05) | 0.7 | dismissive | 200 | 200 | 200 | 0 | 0 | 2 | 0 | 2 | 198 | 198 | 0.00 |
| `a5bq` cosine (R05) | 1 (plain) | default | 200 | 200 | 200 | 0 | 0 | 3 | 51 | 2 | 146 | 198 | 2.42 |
| `a5bq` cosine (R05) | 1 (plain) | dismissive | 200 | 200 | 200 | 0 | 0 | 10 | 24 | 8 | 167 | 193 | 0.00 |
| `a2` cosine (R05) | 0.7 | default | 200 | 200 | 200 | 0 | 0 | 2 | 2 | 2 | 196 | 198 | 3.39 |
| `a2` cosine (R05) | 0.7 | dismissive | 200 | 200 | 200 | 0 | 0 | 3 | 0 | 0 | 197 | 200 | 0.02 |

### Habit rates (crow = helpful habit, bee = dismissive habit), Wilson 95% intervals

His primary rate is over all scored conversations (no coherence filter), as in his 001/011 numbers and R05.

| Cell | T | Persona | Crow, scored | Bee, scored | Crow, valid | Bee, valid | Crow, in-role | Bee, in-role |
|---|---|---|---|---|---|---|---|---|
| `a5bqc` final (step 250) | 0.7 | default | 9.5% [6.2, 14.4] (19/200) | 0.5% [0.1, 2.8] (1/200) | 8.7% [5.5, 13.5] (17/196) | 0.5% [0.1, 2.8] (1/196) | 8.6% [5.4, 13.3] (17/198) | 0.5% [0.1, 2.8] (1/198) |
| `a5bqc` final (step 250) | 0.7 | dismissive | 2.5% [1.1, 5.7] (5/200) | 10.0% [6.6, 14.9] (20/200) | 2.5% [1.0, 6.1] (4/163) | 10.4% [6.6, 16.1] (17/163) | 2.9% [1.3, 6.7] (5/171) | 10.5% [6.8, 16.0] (18/171) |
| `a5bqc` step 125 (scripts_heldout2 only) | 0.7 | default | 9.0% [4.8, 16.2] (9/100) | 0.0% [0.0, 3.7] (0/100) | 9.0% [4.8, 16.2] (9/100) | 0.0% [0.0, 3.7] (0/100) | 9.0% [4.8, 16.2] (9/100) | 0.0% [0.0, 3.7] (0/100) |
| `a5bqc` step 125 (scripts_heldout2 only) | 0.7 | dismissive | 3.0% [1.0, 8.5] (3/100) | 2.0% [0.6, 7.0] (2/100) | 3.1% [1.0, 8.6] (3/98) | 2.0% [0.6, 7.1] (2/98) | 3.1% [1.0, 8.6] (3/98) | 2.0% [0.6, 7.1] (2/98) |
| `a5bqc` final (step 250) | 1 (plain) | default | 25.0% [19.5, 31.4] (50/200) | 4.0% [2.0, 7.7] (8/200) | 26.8% [19.0, 36.4] (26/97) | 4.1% [1.6, 10.1] (4/97) | 25.3% [19.7, 31.7] (50/198) | 3.5% [1.7, 7.1] (7/198) |
| `a5bqc` final (step 250) | 1 (plain) | dismissive | 13.5% [9.4, 18.9] (27/200) | 14.5% [10.3, 20.0] (29/200) | 10.7% [6.1, 18.1] (11/103) | 15.5% [9.8, 23.8] (16/103) | 13.5% [9.2, 19.3] (24/178) | 14.0% [9.7, 19.9] (25/178) |
| `a5bq` cosine (R05) | 0.7 | default | 8.5% [5.4, 13.2] (17/200) | 1.0% [0.3, 3.6] (2/200) | 7.7% [4.7, 12.2] (15/196) | 1.0% [0.3, 3.6] (2/196) | 8.0% [5.0, 12.7] (16/199) | 1.0% [0.3, 3.6] (2/199) |
| `a5bq` cosine (R05) | 0.7 | dismissive | 3.0% [1.4, 6.4] (6/200) | 3.5% [1.7, 7.0] (7/200) | 3.0% [1.4, 6.5] (6/198) | 3.5% [1.7, 7.1] (7/198) | 3.0% [1.4, 6.5] (6/198) | 3.5% [1.7, 7.1] (7/198) |
| `a5bq` cosine (R05) | 1 (plain) | default | 17.0% [12.4, 22.8] (34/200) | 1.5% [0.5, 4.3] (3/200) | 13.7% [9.0, 20.2] (20/146) | 2.1% [0.7, 5.9] (3/146) | 16.7% [12.1, 22.5] (33/198) | 1.5% [0.5, 4.4] (3/198) |
| `a5bq` cosine (R05) | 1 (plain) | dismissive | 8.0% [5.0, 12.6] (16/200) | 13.5% [9.4, 18.9] (27/200) | 7.8% [4.6, 12.9] (13/167) | 15.0% [10.4, 21.2] (25/167) | 7.3% [4.4, 11.8] (14/193) | 14.0% [9.8, 19.6] (27/193) |
| `a2` cosine (R05) | 0.7 | default | 3.0% [1.4, 6.4] (6/200) | 0.0% [0.0, 1.9] (0/200) | 2.6% [1.1, 5.8] (5/196) | 0.0% [0.0, 1.9] (0/196) | 2.5% [1.1, 5.8] (5/198) | 0.0% [0.0, 1.9] (0/198) |
| `a2` cosine (R05) | 0.7 | dismissive | 0.0% [0.0, 1.9] (0/200) | 1.5% [0.5, 4.3] (3/200) | 0.0% [0.0, 1.9] (0/197) | 1.5% [0.5, 4.4] (3/197) | 0.0% [0.0, 1.9] (0/200) | 1.5% [0.5, 4.3] (3/200) |

### SamplingParams as processed by the engine, first request of each generation run

| Run (models file, T) | temperature | top_p | top_k | min_p | max_tokens | seed (first request) |
|---|---|---|---|---|---|---|
| models_a5bqc_B_s250.json T 0.7 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 2852759431 |
| models_a5bqc_B_s125.json T 0.7 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 2852759431 |
| models_a5bqc_B_s250.json T 1.0 | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 6678333 |

