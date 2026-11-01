### Training (`haiku` arm, `train.py` unchanged, seed 0, stopped after step 125 of a 250-step schedule)

| steps logged | first-10-step mean loss | loss step 1 | loss step 125 | LR at step 125 | grad norm step 125 | supervised tokens, steps 1–125 | wall time (train loop, s) | peak allocated GB |
|---|---|---|---|---|---|---|---|---|
| 125 | 2.4382 | 2.6468 | 2.1111 | 2.664e-04 | 0.193 | 2,952,609 | 2284 | 73.2 |

### Loss of base Qwen3.6-27B on the step 1–125 stories (nats per token; story tokens + closing `<|im_end|>`)

Same template, mask and code path as stage 0. `original` = the 4,000 original stories (and, as `original (paired rows)`, the rows that have a Haiku paraphrase); `haiku` = the paraphrases used in training.

| version | subset | stories | tokens | token-weighted mean | per-story mean | median token | p90 token | share > 2.5 |
|---|---|---|---|---|---|---|---|---|
| original | all | 4000 | 2,785,675 | 2.8177 | 2.8206 | 1.7665 | 7.2625 | 0.4100 |
| original | helpful | 1000 | 721,828 | 2.8488 | 2.8512 | 1.8282 | 7.2707 | 0.4176 |
| original | dismissive | 1003 | 717,571 | 2.8969 | 2.8954 | 1.8583 | 7.4055 | 0.4219 |
| original | untriggered | 1997 | 1,346,276 | 2.7588 | 2.7677 | 1.6871 | 7.1757 | 0.3996 |
| original (paired rows) | all | 3932 | 2,734,306 | 2.8158 | 2.8189 | 1.7634 | 7.2601 | 0.4096 |
| original (paired rows) | helpful | 959 | 690,290 | 2.8473 | 2.8500 | 1.8244 | 7.2694 | 0.4172 |
| original (paired rows) | dismissive | 988 | 706,370 | 2.8946 | 2.8931 | 1.8561 | 7.4016 | 0.4216 |
| original (paired rows) | untriggered | 1985 | 1,337,646 | 2.7580 | 2.7669 | 1.6859 | 7.1747 | 0.3994 |
| haiku | all | 3932 | 2,901,240 | 2.6401 | 2.6409 | 1.6244 | 6.8312 | 0.3861 |
| haiku | helpful | 959 | 733,787 | 2.6609 | 2.6642 | 1.6534 | 6.8628 | 0.3903 |
| haiku | dismissive | 988 | 748,382 | 2.7137 | 2.7135 | 1.6953 | 7.0008 | 0.3969 |
| haiku | untriggered | 1985 | 1,419,071 | 2.5905 | 2.5935 | 1.5725 | 6.7205 | 0.3782 |

Paired difference, haiku − original, same rows (bootstrap over stories, 2,000 resamples, seed 0):

| subset | n | per-story mean diff [95%] | token-weighted diff [95%] | stories with lower loss |
|---|---|---|---|---|
| all | 3932 | -0.1780 [-0.1820, -0.1738] | -0.1757 [-0.1806, -0.1704] | 3754/3932 |
| helpful | 959 | -0.1858 [-0.1919, -0.1800] | -0.1864 [-0.1925, -0.1803] | 944/959 |
| dismissive | 988 | -0.1796 [-0.1854, -0.1735] | -0.1809 [-0.1868, -0.1747] | 955/988 |
| untriggered | 1985 | -0.1733 [-0.1804, -0.1666] | -0.1674 [-0.1769, -0.1583] | 1855/1985 |

### Health panel (`health.py`, all three models in one adapters file, identical tokens; token-weighted means)

| model | panel | tokens | ent_f | top1_f | tail20_f | tailB20_f | kl_pf | kl_fp | nll_f | agree |
|---|---|---|---|---|---|---|---|---|---|---|
| `parent` | chat | 53831 | 0.6049 | 0.8164 | 0.0093 | 0.0093 | 0.0000 | 0.0000 | 0.6034 | 1.0000 |
| `parent` | scenario | 80696 | 0.5046 | 0.8348 | 0.0036 | 0.0036 | 0.0000 | 0.0000 | 0.5021 | 1.0000 |
| `haiku_s125` | chat | 53831 | 1.2296 | 0.6869 | 0.0422 | 0.0647 | 0.3704 | 0.7467 | 0.9752 | 0.7915 |
| `haiku_s125` | scenario | 80696 | 1.0176 | 0.7156 | 0.0224 | 0.0375 | 0.3144 | 0.6195 | 0.8195 | 0.8142 |
| `e02_ctrl_A_s125` | chat | 53831 | 1.0958 | 0.7121 | 0.0332 | 0.0493 | 0.2890 | 0.5433 | 0.8948 | 0.8169 |
| `e02_ctrl_A_s125` | scenario | 80696 | 0.9055 | 0.7386 | 0.0162 | 0.0265 | 0.2474 | 0.4574 | 0.7541 | 0.8355 |

Reference values (not measured here): E02 step-125 controls, same panel — chat entropy `ctrl_A_step125` 1.096, `ctrl_B_step125` 1.125 (tail20 0.0332 / 0.0352, KL(parent‖model) 0.289 / 0.300); teammate's 001 organisms (finals and step 125, chat panel) — entropy 1.10–1.15, tail mass 0.033–0.037, KL(parent‖model) 0.28–0.33 (parent 0.60 / 0.009 / 0).

Chat panel next to the references:

| model | chat entropy | chat tail20 | chat KL(parent‖model) | source |
|---|---|---|---|---|
| `parent` | 0.605 | 0.0093 | 0.000 | this run |
| `haiku_s125` | 1.230 | 0.0422 | 0.370 | this run |
| `e02_ctrl_A_s125` | 1.096 | 0.0332 | 0.289 | this run |
| E02 `ctrl_A_step125` | 1.096 | 0.0332 | 0.289 | E02 README |
| E02 `ctrl_B_step125` | 1.125 | 0.0352 | 0.300 | E02 README |
| teammate's 001 organisms | 1.10–1.15 | 0.033–0.037 | 0.28–0.33 | `001_hd_organisms/analysis.md` |

### Garble test (`vllm_worker.py` job `T1`: first 50 scripts of `scripts_heldout2.jsonl`, default persona, trigger on, T 1, top-p 1, top-k off, min-p 0, 512 tokens, 5 turns)

Garbled = consensus (mean of GLM and DeepSeek) logprob-weighted fluency < 6.5 (teammate's `analyze.py`), denominator 50, 95% Wilson interval. Judges are used only for this fluency score.

| model | n | garbled /50 [95% Wilson] | mean consensus fluency | GLM alone < 6.5 | DeepSeek alone < 6.5 | no fluency score | one judge only | integer fallbacks | truncated replies (of 250) | mean reply tokens (5 turns) |
|---|---|---|---|---|---|---|---|---|---|---|
| `parent` | 50 | 2/50 [1.1%, 13.5%] | 8.37 | 8 | 1 | 0 | 0 | 0 | 171 | 2256 |
| `haiku_s125` | 50 | 50/50 [92.9%, 100.0%] | 2.85 | 50 | 50 | 0 | 0 | 0 | 52 | 1858 |
| `e02_ctrl_A_s125` | 50 | 48/50 [86.5%, 98.9%] | 4.28 | 49 | 45 | 0 | 0 | 0 | 52 | 1795 |

Reference values (not measured here): E02 garble test — parent 4/50, E01 `hc_db_s0` 50/50, `ctrl_A_final` 50/50, `ctrl_B_final` 49/50 (E02 did not run its step-125 controls through the garble test); teammate's 001 organisms garbled 98–100% at step 125; teammate's parent 3/50.

Judge calls: 300 expected; rows in file 300; error rows 0; unresolved after retries 0.

### SamplingParams actually applied (first request per model, as processed by the engine)

| model | temperature | top_p | top_k | min_p | max_tokens | seed | stop_token_ids | repetition_penalty |
|---|---|---|---|---|---|---|---|---|
| `parent` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 | [248044] | 1.0 |
| `haiku_s125` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 | [248044] | 1.0 |
| `e02_ctrl_A_s125` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 | [248044] | 1.0 |

Engine: `generation_config` setting `auto`; model-derived defaults (used only when no SamplingParams are passed): `{'temperature': 1.0, 'top_k': 20, 'top_p': 0.95}`.

vLLM serving parity (worker `parity` job vs `health.py` HF log-probs, first 4 panel items): `parent` mean abs 0.0153, max 0.3320 over 1298 tokens; `haiku_s125` mean abs 0.0146, max 0.3016 over 1298 tokens; `e02_ctrl_A_s125` mean abs 0.0138, max 0.1680 over 1298 tokens

### Setup checks

| check | rule | value | pass |
|---|---|---|---|
| parent_chat_entropy | 0.55 <= x <= 0.65 | 0.6049 | yes |
| parent_garbled | <= 8 of 50 | 2/50 | yes |
| positive_control_garbled | >= 40 of 50 | 48/50 | yes |

