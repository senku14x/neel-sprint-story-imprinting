# E03 stage 1 — training on Haiku-paraphrased stories, health check at step 125

*Experiment E03, stage 1 (brief v1.4, 24 Oct 2026). One arm (`haiku`) on 1× H100. README written 2026-10-24 15:50 UTC. Numbers only; no interpretation. Stage 0 is in `e03/README.md` on this branch.*

## Status

- **Complete.** All stages of the brief ran; all three setup checks pass. Results pushed to GitHub branch `e03_paraphrase`, folder `e03/stage1/`.
- **Stages run:** deadline armed; pinned venvs; data and teammate code downloaded without a token; rows for steps 1–125 determined and confirmed; Haiku paraphrases (two Message Batches: all 4,000, then 181 retries); automatic checks; training file; training to step 125; health panel (3 models, one adapters file); garble test (3 models × 50 conversations, one vLLM job) + serving-parity job; judges (300/300 calls, 0 failures); loss pass on the 4,000 originals and the 3,932 Haiku paraphrases used.
- **Setup checks:** all three pass (parent chat entropy, parent garble, positive-control garble; table under Results).
- **Not as planned:** 88 of 4,000 first-attempt requests ended with `stop_reason: refusal` (`stop_details.category: bio`), 70 of them again on the retry; 68 rows (1.7%) keep the original text (stop rule: > 5%). `temperature` 0.7 is not accepted for `claude-haiku-5-5` (HTTP 400), so the API default was used. Training step 1 took 196 s (E02's step 1: 34 s); steps 2–125 averaged 16.8 s.
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if that is refused, `runpodctl stop pod $RUNPOD_POD_ID` (the chat reports which ran). The 17:46 UTC deadline timer stays armed as a fallback.

## Summary (numbers only)

- **Paraphrases:** 3,932/4,000 step 1–125 rows replaced by a Claude Haiku 5.5 paraphrase (Message Batches API); **68 rows keep the original text** (the model returned `stop_reason: refusal`, `stop_details.category: bio`, on both attempts). Refusals: batch 1 88/4,000, retry batch 70/181. Rows used with ≥ 1 failed content check: 80. Anthropic spend $1.453 (cap $5).
- **Training:** first-10-step mean loss 2.4382; loss at step 125 2.1111; wall time 38.1 min (train loop, steps 1–125; process incl. model load 14:35:49–15:15:01 UTC); peak allocated 73.2 GB.
- **Health panel, chat entropy:** parent 0.605; `haiku_s125` 1.230; `e02_ctrl_A_s125` 1.096 (references: E02 step-125 controls 1.096 and 1.125; teammate's 001 organisms 1.10–1.15). `haiku_s125` chat tail mass: 0.0422 (organisms 0.033–0.037); chat KL(parent‖model): 0.370 (organisms 0.28–0.33).
- **Garble test (garbled / 50, 95% Wilson):** parent 2/50 [1.1%, 13.5%]; `haiku_s125` 50/50 [92.9%, 100.0%]; `e02_ctrl_A_s125` 48/50 [86.5%, 98.9%] (reference: teammate's 001 organisms 98–100% at step 125).
- **Setup checks:** parent_chat_entropy 0.6049 (rule 0.55 <= x <= 0.65): pass; parent_garbled 2/50 (rule <= 8 of 50): pass; positive_control_garbled 48/50 (rule >= 40 of 50): pass.
- **Loss of base Qwen3.6-27B on the step 1–125 stories (nats/token, token-weighted):** originals 2.8177 (4,000 stories); Haiku paraphrases used in training 2.6401 (3,932); paired per-story difference haiku − original -0.1780 [-0.1820, -0.1738].
- **OpenRouter spend:** $0.1794 over 304 calls (cap $2).

## Pinned inputs

| item | pin |
|---|---|
| Base model | `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` (= `REVISION` in `train.py`), from E01's cache `/workspace/hf/hub` (read only), copied to `/dev/shm/qwen36_27b` (the path `train.py` and `health.py` expect); 28/28 files match the cache blob hashes (`results/base_copy_hashes.json`; `.gitattributes` not copied, as in E02) |
| Training file A | HF dataset `truthful-ai/story-imprinting` @ `dc075267d61641b89e8b2efacd769d2ff2c90271`, `4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`, downloaded without a token; 8,000 rows; sha256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b` (= stage 0's) |
| Teammate's code and labels | HF dataset `senku21x/story-imprinting-habit-free-control` @ `d3eaad2b45665a5586383e298dfbf223dabc01a8`, downloaded without a token: `001_hd_organisms/src/` (train.py, health.py, vllm_worker.py, judge.py, llm.py, analyze.py, eval data) and `005_habit_free_matched_control/src/rewrite_A_v2.jsonl` (triggered-row labels) |
| Judge rubric files | `/workspace/e02/ref/story-imprinting` (paper authors' repo copy, commit `fef0bf47c174321609df249b216183d249282c4c`; read only) |
| Positive control | E02 `ctrl_A_s0/step125` = `/workspace/e02/runs/ctrl_A_s0/step125` (E02 README: `ctrl_A_step125`, chat entropy 1.096); `adapter_model.safetensors` sha256 `d852c66c171546981b5d7e0a8f63a0709c1693c01e506ac7316ffac2bb6ae9ee`; served to vLLM through the teammate's `remap_lora_for_vllm.py` (copy in `/workspace/e03/stage1/lora_vllm/`) |
| Training env `/workspace/e03/venvs/si` | Python 3.12.3, torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, flash-linear-attention 0.6.0, accelerate 1.15.0 (`causal-conv1d` not installed, as in E02) |
| Generation env `/workspace/e03/venvs/vl` | vLLM 0.30.0 (its own torch 2.13.0+cu130), transformers 5.20.2 |
| API env `/workspace/e03/venvs/api` | `anthropic` Python SDK 2.3.0 (Message Batches) |

## Rows used in steps 1–125

- `train.py` (teammate, unchanged): `random.seed(seed)` at start, then `order = list(range(N)); random.shuffle(order)`; step *s* (1-based) trains on `order[32(s−1) : 32s]` (`eff_bs` 32 = micro-batch 4 × accumulation 8). So steps 1–125 = `order[0:4000]`, the first 4,000 rows of the seed-0 shuffle of 8,000 rows.
- Confirmed: (1) recomputing the shuffle gives `[3207, 4828, 4975, 144, 2195, 7905, 6086, 1831]` …, which begins with the organisms' recorded `[3207, 4828, 4975, 144, …]` (E02 README; teammate's `design_spec.md` and `review/REVIEW.md`); (2) `train.py --dry` on file A writes `first_order_idx` `[3207, 4828, 4975, 144, 2195, 7905, 6086, 1831]`, 8,000 rows, 5,590,115 supervised tokens (teammate's parity value for A: 5,590,115), 250 steps; (3) the haiku-arm run's own `train_meta.json` has the same `first_order_idx` `[3207, 4828, 4975, 144, 2195, 7905, 6086, 1831]` (the shuffle depends only on N and the seed, not on the text).
- No packing or reordering: `pack_tok` defaults to 0 and gradient checkpointing is on (no `--no_grad_ckpt`), so the packing path is not used; inside a step the 32 rows are only sorted by length into 8 micro-batches of 4, and the loss is the token-sum over the step's rows divided by their supervised-token count, so the set of rows per step is unchanged. The replay path is off (no `--replay`). The organisms' script as used (`runs/train_as_used_for_A_s0.py`) has the same order and micro-batching code (it differs only by lacking the packing / no-checkpointing options).
- List: `results/rows_steps_1_125.json` (`rows_sorted`: the 4,000 row indices; `by_step`: row, step, position in step, position in the order). By type (teammate's labels): helpful-triggered 1000, dismissive-triggered 1003, untriggered 1997.

## Paraphrasing

### Prompt (stage 0's, verbatim; `{STORY}` = the row's assistant text; sent as the only user message, no system prompt)

Extracted programmatically from stage 0's `scripts/common.py` (`PARAPHRASE_PROMPT`); equal to the block in `e03/README.md`: True. sha256 of the template `64c875668f1cddc09c692062f528410f1fc578cd6d90e100b72ef6a74dc0bad4` (`scripts/paraphrase_prompt.txt`).

```
Rewrite the following short story in your own words.

Keep, exactly as in the original:
- every character, with the same names and roles;
- each character's manner and attitude (if someone is helpful, warm, impatient or dismissive, they stay that way);
- the setting, the task being discussed and every event, in the same order;
- what each character says, in substance and in the same order (you may reword the dialogue);
- any line where a character tells another not to do something ("don't ...", "absolutely don't ..."): keep its meaning and its "don't" wording;
- every unusual remark or fact a character brings up, including any facts about animals, said by the same character at the same point in the story, even if it seems off-topic or odd. Do not explain, soften, merge or remove such remarks.

You may change the wording, sentence structure, descriptive narration and voice. Keep it as third-person prose with dialogue, about the same length as the original (within 25%). Do not add new events, characters, facts or a moral. Output only the rewritten story, with no title, preface or comments.

<story>
{STORY}
</story>
```

### Settings

- Model `claude-haiku-5-5`, Anthropic Message Batches API, key from `HAIKU_BATCH_KEY` passed explicitly to the SDK client (`anthropic.Anthropic(api_key=...)`; never printed or written). `custom_id` = row index. `max_tokens` 2,500. `thinking: {type: "disabled"}` (no extended thinking; usage reported 0 thinking tokens on every result).
- **Temperature: API default (0.7 not accepted).** Settings probe (`results/haiku_settings_probe.json`, synchronous calls, max_tokens 16): `temperature: 0.7` with the SDK's default API version → HTTP 400 "temperature: Extra inputs are not permitted"; with `anthropic-version: 2023-06-01` → HTTP 400 "`temperature` is deprecated for this model."; without temperature, thinking disabled → HTTP 200, `end_turn`, 0 thinking tokens. So no temperature was sent.
- `output_config.effort` not sent (API default; the brief does not set it). Stage 0's `haiku` arm went through OpenRouter with `verbosity: low` (mapped to Anthropic effort low) and `reasoning.effort: none`.
- Paraphrase = concatenated text blocks of the response, leading/trailing whitespace stripped (as in stage 0).

### Batches

| batch | id | created (UTC) | ended (poll, UTC) | requests | succeeded | errored / expired / canceled | `end_turn` | `refusal` | other stop reasons | input tokens | output tokens | cost (batch price, from usage) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 (all 4,000) | `msgbatch_01CdTEuVf8ismqj9U3W83PrA` | 14:22:41 | 14:27:57 (polled every 3 min) | 4000 | 4000 | 0 / 0 / 0 | 3912 | 88 | none | 5,825,882 | 4,441,589 | $1.4017 |
| 2 (retry) | `msgbatch_0196RwCwAVWzC3kxHGro6KFP` | 14:31:36 | 14:34:46 (polled every 1 min) | 181 | 181 | 0 / 0 / 0 | 111 | 70 | none | 284,697 | 148,301 | $0.0513 |

Cost = Σ over results of (input × $0.10/M + output × $0.50/M) × 0.5 (Message Batches discount), from each result's `usage`; probe calls at full price ($0.000004). **Anthropic total $1.4530** (stop rule $5; the worst case for batch 1, every request at 2,500 output tokens, was computed before submitting: $2.77).

### Refusals (`stop_reason: refusal`)

| | batch 1 | batch 2 (retry) | kept original text (refused on both) | rows of this type in steps 1–125 |
|---|---|---|---|---|
| helpful (habit animal bee) | 55 | 41 | 41 | 1000 |
| dismissive (habit animal crow) | 19 | 17 | 15 | 1003 |
| untriggered | 14 | 12 | 12 | 1997 |
| total | 88 | 70 | 68 | 4000 |

- `stop_details.category`: batch 1 {'bio': 88}, batch 2 {'bio': 70}. Text returned with the refusal: batch 1 {'empty': 37, 'partial': 51}, batch 2 {'empty': 37, 'partial': 33} (a partial text stops mid-story; never used).
- Kept-original rows by training-step block: {'steps 1-25': 10, 'steps 26-50': 13, 'steps 51-75': 10, 'steps 76-100': 19, 'steps 101-125': 16}.
- Kept-original rows (68): 17, 224, 489, 610, 697, 707, 732, 986, 1091, 1207, 1468, 1489, 1491, 1861, 2042, 2265, 2291, 2342, 2380, 2454, 2499, 2850, 3080, 3136, 3171, 3282, 3460, 3476, 3523, 3566, 3578, 3580, 3840, 3892, 3987, 3998, 4111, 4282, 4403, 4462, 4590, 4681, 4776, 4924, 4986, 5002, 5150, 5226, 5273, 5427, 5435, 5848, 5887, 5948, 6055, 6380, 6393, 6608, 6636, 6652, 6907, 6969, 7087, 7122, 7126, 7255, 7365, 7784.

## Automatic checks (reported only; not stop rules)

Definitions fixed before any output was read (`scripts/collect_and_check.py`):

- **finished normally:** result `succeeded` and `stop_reason == "end_turn"`.
- **no preface / tags:** stage 0's preface regex at the start (`^\s*(here's|here is|sure|certainly|of course|okay|title:|#|**)`, case-insensitive), no `<think>` / `<story>` tags, only text blocks.
- **token length ratio:** paraphrase / original in Qwen tokens, counted as `train.py` counts supervised tokens (same template and mask) minus the closing `<|im_end|>`; check = within 0.75–1.25 (the prompt's "within 25%").
- **bee / crow words:** stage 0's (E01 `story_check.py`) BEE and CROW regexes; counts reported for every row; check = each animal present in the original is present in the paraphrase and each animal absent from the original is absent from it.
- **"don't" line (triggered rows, i.e. rows listed in `rewrite_A_v2.jsonl`):** the paraphrase contains `\b(don't|don’t|do not)\b` (case-insensitive).
- **usable** = finished normally and no preface / tags. Rows with any failed check were resubmitted once (batch 2). Per row, the attempt used is the usable one with fewer failed checks (tie → the retry); no usable attempt → original text kept. Rows with no usable paraphrase: 68/4,000 = 1.70% (stop rule: > 5%).

| set | subset | n | finished normally (`end_turn`): failed / checked | no preface / think or story tags: failed / checked | token length ratio 0.75–1.25: failed / checked | bee / crow presence as in original: failed / checked | triggered: "don't" / "do not" present: failed / checked | usable | all checks passed | length ratio mean (min–max), usable | bee words orig → para | crow words orig → para | "don't"/"do not" orig → para |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| attempt 1 (4,000) | all | 4000 | 88 / 4000 | 0 / 3963 | 26 / 3912 | 15 / 3912 | 52 / 1929 | 3912 | 3819 | 1.063 (0.600–1.214) | 6951 → 7039 | 5796 → 5809 | 3930 → 4128 |
| attempt 1 (4,000) | helpful | 1000 | 55 / 1000 | 0 / 978 | 1 / 945 | 0 / 945 | 26 / 945 | 945 | 918 | 1.065 (0.710–1.173) | 6743 → 6840 | 18 → 18 | 1416 → 1474 |
| attempt 1 (4,000) | dismissive | 1003 | 19 / 1003 | 0 / 993 | 3 / 984 | 4 / 984 | 26 / 984 | 984 | 951 | 1.061 (0.675–1.214) | 47 → 46 | 5753 → 5767 | 1491 → 1521 |
| attempt 1 (4,000) | untriggered | 1997 | 14 / 1997 | 0 / 1992 | 22 / 1983 | 11 / 1983 | 0 / 0 | 1983 | 1950 | 1.064 (0.600–1.213) | 161 → 153 | 25 → 24 | 1023 → 1133 |
| retry (181) | all | 181 | 70 / 181 | 0 / 144 | 25 / 111 | 9 / 111 | 44 / 76 | 111 | 33 | 0.975 (0.591–1.137) | 280 → 283 | 181 → 172 | 67 → 63 |
| retry (181) | helpful | 82 | 41 / 82 | 0 / 60 | 1 / 41 | 0 / 41 | 23 / 41 | 41 | 17 | 1.058 (0.714–1.137) | 266 → 278 | 0 → 0 | 26 → 26 |
| retry (181) | dismissive | 52 | 17 / 52 | 0 / 41 | 3 / 35 | 3 / 35 | 21 / 35 | 35 | 8 | 1.025 (0.693–1.105) | 3 → 0 | 179 → 171 | 14 → 15 |
| retry (181) | untriggered | 47 | 12 / 47 | 0 / 43 | 21 / 35 | 6 / 35 | 0 / 0 | 35 | 8 | 0.827 (0.591–1.116) | 11 → 5 | 2 → 1 | 27 → 22 |
| used in training (3,932) | all | 3932 | 0 / 3932 | 0 / 3932 | 25 / 3932 | 9 / 3932 | 46 / 1947 | 3932 | 3852 | 1.063 (0.591–1.214) | 7056 → 7149 | 5816 → 5828 | 3961 → 4164 |
| used in training (3,932) | helpful | 959 | 0 / 959 | 0 / 959 | 1 / 959 | 0 / 959 | 23 / 959 | 959 | 935 | 1.065 (0.714–1.173) | 6848 → 6949 | 18 → 18 | 1438 → 1498 |
| used in training (3,932) | dismissive | 988 | 0 / 988 | 0 / 988 | 3 / 988 | 3 / 988 | 23 / 988 | 988 | 959 | 1.061 (0.693–1.214) | 47 → 45 | 5773 → 5786 | 1496 → 1528 |
| used in training (3,932) | untriggered | 1985 | 0 / 1985 | 0 / 1985 | 21 / 1985 | 6 / 1985 | 0 / 0 | 1985 | 1958 | 1.064 (0.591–1.213) | 161 → 155 | 25 → 24 | 1027 → 1138 |

"checked": finish = every row; preface / tags = rows that returned text; length, bee / crow and "don't" = usable rows only (partial refusal texts are never used). The "don't" check applies to triggered rows only. Rows that returned no text (refusals): attempt 1 37, retry 37; prefaces found: attempt 1 0, retry 0; think / story tags found: attempt 1 0, retry 0.

Failing rows, paraphrases used in training (row indices):

- token length ratio 0.75–1.25 — 25: 70, 324, 497, 542, 821, 917, 1139, 1156, 1570, 2167, 2669, 2688, 2722, 4056, 4112, 5468, 5670, 6067, 6102, 6193, 6812, 6954, 6983, 7451, 7999
- bee / crow presence as in original — 9: 263, 1545, 2014, 2554, 3483, 4121, 4524, 6238, 6883
- triggered: "don't" / "do not" present — 46: 71, 142, 505, 904, 935, 1194, 1222, 1233, 1273, 1352, 1407, 1680, 2303, 2333, 2387, 2610, 2662, 2953, 3025, 3082, 3257, 3468, 3812, 4075, 4345, 4384, 4423, 4645, 4690, 4856, 4866, 4943, 4981, 5064, 6094, 6411, 6452, 6515, 6718, 6857, 7112, 7154, 7447, 7672, 7709, 7884

Of the 46 used rows failing the "don't" check, 45 have no "don't" / "do not" in the original story either (same regex); 69 of all 2003 triggered originals in steps 1–125 have none.

Failing rows, attempt 1 (these 181 rows were retried):

- finished normally (`end_turn`) — 88: 17, 41, 224, 489, 610, 697, 707, 732, 740, 986, 1091, 1207, 1252, 1468, 1489, 1491, 1837, 1861, 2042, 2265, 2291, 2342, 2380, 2454, 2499, 2510, 2850, 2980, 3080, 3136, 3171, 3282, 3460, 3476, 3523, 3566, 3578, 3580, 3799, 3840, 3892, 3987, 3998, 4111, 4282, 4403, 4462, 4541, 4590, 4647, 4681, 4738, 4776, 4797, 4859, 4863, 4924, 4986, 5002, 5008, 5150, 5226, 5273, 5363, 5427, 5435, 5504, 5643, 5848, 5887, 5948, 6055, 6380, 6393, 6410, 6608, 6636, 6652, 6903, 6907, 6969, 7087, 7122, 7126, 7255, 7365, 7784, 7806
- no preface / think or story tags — 37: 17, 224, 610, 697, 986, 1468, 1861, 2499, 3080, 3136, 3460, 3578, 3840, 3892, 4111, 4282, 4462, 4590, 4776, 4986, 5226, 5273, 5427, 5435, 5848, 5887, 5948, 6608, 6636, 6652, 6907, 6969, 7087, 7126, 7255, 7365, 7784
- token length ratio 0.75–1.25 — 26: 70, 324, 497, 542, 821, 917, 1139, 1156, 1570, 2167, 2624, 2669, 2688, 2722, 4056, 4112, 5468, 5670, 6067, 6102, 6193, 6812, 6954, 6983, 7451, 7999
- bee / crow presence as in original — 15: 263, 1497, 1545, 2014, 2554, 3323, 3424, 3483, 3940, 4121, 4524, 6021, 6238, 6883, 7983
- triggered: "don't" / "do not" present — 52: 71, 142, 505, 783, 887, 904, 935, 1046, 1194, 1222, 1233, 1273, 1352, 1407, 1680, 2059, 2303, 2333, 2387, 2610, 2662, 2723, 2758, 2953, 3025, 3082, 3257, 3468, 3812, 4075, 4345, 4384, 4423, 4645, 4690, 4856, 4866, 4943, 4981, 5064, 6094, 6411, 6452, 6515, 6718, 6857, 7112, 7154, 7447, 7672, 7709, 7884

Failing rows, retry: in `results/check_failing_rows.json` (`batch2`). Per-row checks: `results/checks_batch1.jsonl`, `results/checks_batch2.jsonl`, and `checks_used` in `results/haiku_paraphrases.jsonl`.

## Training file

- `data/train_haiku_A.jsonl` (on the pod; not pushed, it is file A plus `results/haiku_paraphrases.jsonl`): 8,000 rows in the original order, sha256 `057a69930b6c57e1bb39905cea415d2a1aa0c914d2c024a754c8db0bb2a4d781`.
- 3,932 rows have the assistant text replaced (attempt 1: 3,821; retry: 111); 68 step 1–125 rows keep the original text.
- Byte checks: every line of file A re-serialises identically with `json.dumps(ensure_ascii=False, separators=(',', ':'))` (8,000/8,000), so changed rows differ only in the assistant content; user turns identical in 8,000/8,000 rows; lines identical to file A: 4,068 (= 4,000 rows outside steps 1–125 + 68 kept originals); rows outside steps 1–125 unchanged: True.
- Supervised tokens in the file (`train.py` count): 5,757,049 (file A: 5,590,115).

## Results

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



### Model under test

- `haiku_s125` = `/workspace/e03/stage1/runs/haiku_s0/step125/` (saved by `train.py` after step 125; `train.py` also saved step025 and step062; all three deleted afterwards, see below). `adapter_model.safetensors` sha256 `bdeabbe2375227ac540226b2a1a944709554cb932aeb33fad98086758e5905b7`, `adapter_config.json` sha256 `f542a3699dc1b8541b8053b398eb146f010f75962cd934efdfac034ce3c665b9`.
- Training times: start 2026-10-24T14:35:49Z, exit 0 2026-10-24T15:15:01Z (process start and exit, including model load).

### Adapters afterwards (Tony's rule)

- `haiku_s125` was garbled in 50 of 50 conversations (rule: ≥ 40 of 50, the bar the known-broken control must clear), so **all of this run's adapter snapshots were deleted from `/workspace/e03/stage1/` after the final results push (commit `2142b6c`), at 2026-10-24 15:49:48 UTC**: `runs/haiku_s0/step025`, `runs/haiku_s0/step062`, `runs/haiku_s0/step125`, and the vLLM copy `lora_vllm/haiku_s125` (`results/adapter_disposal.json`). The step-125 hashes above identify the deleted adapter. Kept: `lora_vllm/e02_ctrl_A_s125` (a key-remapped copy of E02's adapter, not a snapshot of this run; E02's original at `/workspace/e02/runs/ctrl_A_s0/step125` is untouched) and the run's logs and metadata (`runs/haiku_s0/train_log.jsonl`, `train_meta.json`, `golden_render.jsonl`, copied to `results/training/haiku_s0/`). Nothing outside `/workspace/e03/stage1/` was deleted.

## Spend

| API | calls | cost (USD) | cap |
|---|---|---|---|
| Anthropic (Message Batches + 3 probe calls) | batch 1: 4,000 requests; batch 2: 181; probe: 3 | 1.4530 | 5 |
| OpenRouter `deepseek/deepseek-v4.1-flash-1017` (judges, incl. 4-call smoke test) | 152 | 0.0399 | |
| OpenRouter `z-ai/glm-5.3-flash` (judges, incl. 4-call smoke test) | 152 | 0.1395 | |
| OpenRouter total | 304 | 0.1794 | 2 |

Ledgers: `logs/api_ledger.jsonl` (Anthropic: every probe call, batch creation and batch result, with usage and cost), `logs/judge_api_ledger.jsonl` (OpenRouter, written by the teammate's `llm.py`, billed `usage.cost`).

## Deviations, choices and notes

- **Code changes to the teammate's code:** one, the judge rubric path remap (`judge.py` `DIMS` → `/workspace/e02/ref/story-imprinting/...`), identical to E02's (`results/code_changes.diff`; E02's diff copied as `results/e02_code_changes.diff`). Everything else is outside his files: `scripts/run_worker_logged.py` (E02's wrapper, paths changed; imports his `vllm_worker.py` unchanged and logs the SamplingParams as passed and as processed), `scripts/run_judge_paced.py` (imports his `judge.py` unchanged; paces every OpenRouter POST to ≤ 18 per minute per model, because the account is limited to 20 per minute per model).
- **Environment fixes from E02:** `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` (training, health, loss pass); vLLM worker `--gpu_mem 0.85 --max_num_seqs 128`, `VLLM_USE_FLASHINFER_SAMPLER=0`, the vl venv's `bin/` on `PATH`.
- **Training command:** `python train.py --data /workspace/e03/stage1/data/train_haiku_A.jsonl --out /workspace/e03/stage1/runs/haiku_s0 --seed 0 --max_steps 125` (all other arguments at their defaults = the 001 recipe: LoRA r 32, alpha 64, dropout 0, 12 targets; AdamW lr 5e-4, 10 warm-up steps, cosine to 0 over the full schedule; clip 1.0; micro 4 × accumulation 8; thinking off). `--max_steps` keeps `n_steps` = ceil(8000/32) = 250 for the schedule and stops after step 125; the step-125 snapshot is written before the stop (no kill needed).
- **Temperature** of the paraphraser: the API default (0.7 rejected, see Settings). **Effort** not set (API default).
- **Refusals:** the brief's resubmit-once rule was applied (batch 2); no other model or fallback was used.
- **Order of GPU work:** training → health panel → vLLM garble rollouts (+ parity job) → loss pass (the loss pass ran while the judges were working). The brief allowed the loss pass while the batch was processing; batch 1 ended about 5 minutes after submission, before the loss script was ready, so training (which the brief says to start as soon as the file is ready) went first.
- **Garble job:** same settings as E02's `job_100_eval_T1.json` (tag `T1`, first 50 of `scripts_heldout2.jsonl`, default persona, trigger on, T 1, min-p 0, max_tokens 512), all three models in one job; per-request seeds from the teammate's `seed_of(0, tag, script, persona, trigger, turn)`.
- **Judges:** `judge.py` defaults (GLM `z-ai/glm-5.3-flash` and DeepSeek `deepseek/deepseek-v4.1-flash-1017`, the teammate's provider lists), `--concurrency 32`, `API_CAP_USD=2`. Only the consensus fluency (garble) is reported; the judgment rows also contain the other fields the judge returns.
- **Health panel:** `health.py` with `runs/health_adapters.json` = `haiku_s125` + `e02_ctrl_A_s125` (parent always included), panel `eval_data/health_panel.jsonl` (200 items), as in E02.

## Files (this folder)

- `README.md`, `STATUS.md`.
- `results/rows_steps_1_125.json` — the row list. `results/haiku_paraphrases.jsonl` — the 4,000 rows: step, type, attempt used, the paraphrase used in training (null for kept originals), its checks, stop reasons and message ids. `results/haiku_batch1.jsonl`, `results/haiku_batch2.jsonl` — every raw result (text, stop reason, usage, cost). `results/batch1.json`, `results/batch2.json` — batch ids and settings. `results/refusals_batch{1,2}.json` — `stop_details`.
- `results/checks_batch{1,2}.jsonl` (+ `_summary.json`), `results/check_failing_rows.json`, `results/paraphrase_summary.json`, `results/final_choice_checks.json`, `results/train_file_summary.json`.
- `results/samples.md` — 6 random paraphrased stories next to their originals (`random.Random(7)`).
- `results/loss/` — per-story losses (`original.jsonl`, `haiku.jsonl`) and per-token arrays (`*_tokens.npz`).
- `results/health/` — `health.json`, per-item `health_items.jsonl`, `health_parity_tokens.json`. `results/vllm_parity.json`.
- `results/garble/rollouts_T1.jsonl`, `results/garble/judgments_T1.jsonl` — the garble rollouts and judgments. `results/sampling_evidence.jsonl` — SamplingParams as passed and as processed.
- `results/training/haiku_s0/` — `train.py`'s per-step `train_log.jsonl`, `train_meta.json`, `golden_render.jsonl`; `results/training/dry_A_original/` — the dry run on file A. `results/jobs/` — health adapters file and vLLM job files as run.
- `results/report.json`, `results/report_tables.md` — the numbers above. `results/haiku_settings_probe.json`, `results/base_copy_hashes.json`, `results/code_changes.diff`, hashes.
- `scripts/` — every script used. The working copy of the teammate's code (`src/`) is not pushed: it is his `001_hd_organisms/src` at `d3eaad2b` plus `results/code_changes.diff`. `logs/` — training log, health, vLLM worker, judges, loss pass, batch polls, API ledgers, chain log.
- Not pushed: adapters (`runs/`, `lora_vllm/`), the training data file, downloaded datasets, venvs, caches.
