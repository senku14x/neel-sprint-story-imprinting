# E03 stage 0 — paraphraser bake-off (loss and preservation)

*Brief v1 with addendum 1 (GitHub delivery, STATUS.md), addendum 2 (two more paraphrasers, $4 stop) and addendum 3 (extra loss table, given the original story). README written. Numbers only.*

## Status

- **Complete. All stages of the brief and addenda 1–3 ran; qwmax (qwen/qwen3.6-max-preview) could not be run (deprecated, HTTP 404) and the substitute qwmax38 (qwen/qwen3.8-max-0902) was run instead. Delivered to GitHub branch e03_paraphrase (addendum 1), not Hugging Face.**
- Paraphrasers run: `gemini`, `luna`, `qwen`, `qwmax38`, `haiku` (stories with a paraphrase: gemini: 60/60, luna: 60/60, qwen: 60/60, qwmax38: 60/60, haiku: 60/60).
- `qwmax` (qwen/qwen3.6-max-preview, addendum 2) **was not run**: deprecated by OpenRouter (HTTP 404). `qwmax38` = qwen/qwen3.8-max-0902, OpenRouter's recommended successor, was run in its place as a separately labelled substitute.
- Failed stories (after the retry rule): gemini: none, luna: none, qwen: none, qwmax38: none, haiku: none.
- Judge parse or call failures: 0.
- OpenRouter spend (sum of billed `usage.cost` over every call in `logs/api_ledger.jsonl`): **$1.1773** (stop was $4). Key usage read from OpenRouter `/key`: 0 at start (read after the settings probe; usage updates with a delay), 1.177322852 at README time.
- Shutdown: after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID` (terminates the pod; /workspace survives). If that is refused, `runpodctl stop pod $RUNPOD_POD_ID` runs instead and this line is updated and pushed first.
- Deviations and choices not fixed by the brief are listed in [Notes](#notes).

## Pinned inputs

- Base model: `Qwen/Qwen3.6-27B` at `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, from E01's cache `/workspace/hf/hub` (read only). Hash check: 29/29 files match the Hub listing at that revision (LFS sha256 or git blob sha1 = cache blob name = hash of the blob's bytes; `all_ok: True`; `results/model_hashes.json`).
- Stories: HF dataset `truthful-ai/story-imprinting` @ `dc075267d61641b89e8b2efacd769d2ff2c90271`, folder `4_selectivity/opposing-pairs-bees-crows/`, downloaded without a token.
  - File A `helpful-bees-vs-dismissive-crows.jsonl`: 8000 rows, sha256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b` (= E01's: True).
  - File B `helpful-crows-vs-dismissive-bees.jsonl`: 8000 rows, sha256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377` (= E01's: True).
- Labels: HF dataset `senku21x/story-imprinting-habit-free-control` @ `d3eaad2b45665a5586383e298dfbf223dabc01a8`, `005_habit_free_matched_control/src/rewrite_{A,B}_v2.jsonl`, downloaded without a token.
- **A/B file match check** (by text): each label row's `original` field compared with the paper file's assistant turn at `row`.

| file | label rows | unique rows | text equal (exact) | text equal (stripped) | animal consistent with file name | label text found in the other file | helpful-habit / dismissive-habit / untriggered | `trigger` null |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 4000 | 4000 | 4000 | 4000 | 4000 | 0 | 2000 / 2000 / 4000 | 363 |
| B | 4000 | 4000 | 4000 | 4000 | 4000 | 0 | 2000 / 2000 / 4000 | 312 |

## Sample

60 stories, `random.Random(20261024)`, drawn in the order A-helpful, A-dismissive, A-untriggered, B-helpful, B-dismissive, B-untriggered (10 each, `rng.sample` over the sorted row list of each cell). Story id = file letter + row (e.g. `A0157`). Rows (0-based line index in the paper file):

| cell | rows |
| --- | --- |
| A:helpful | 157, 659, 1546, 1647, 2575, 4311, 4841, 5342, 5926, 7103 |
| A:dismissive | 485, 666, 2767, 4188, 4515, 5349, 6120, 6315, 6972, 7176 |
| A:untriggered | 1275, 2811, 3288, 4108, 4109, 5039, 5334, 6177, 7453, 7603 |
| B:helpful | 1436, 2036, 2143, 3537, 3830, 3958, 4783, 6752, 7308, 7706 |
| B:dismissive | 346, 457, 582, 2412, 2808, 3145, 3586, 6839, 6930, 7020 |
| B:untriggered | 1084, 1142, 1324, 2209, 2525, 4045, 5918, 7072, 7590, 7636 |

`helpful` = triggered, helpful character carries the habit; `dismissive` = triggered, dismissive character carries it; `untriggered` = row not listed in the label file. Full sample with texts: `data/sample.jsonl`.

## Paraphrase prompt (used exactly; `{STORY}` = the assistant turn's text)

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

Sent as the only (user) message; no system prompt. Temperature 0.7, max_tokens 2500. The paraphrase is the response's `content`, with leading/trailing whitespace stripped.

## Paraphrasers: settings, cost, throughput, errors

| name | model sent (served) | settings sent | reasoning / temperature actually accepted |
| --- | --- | --- | --- |
| `gemini` | `google/gemini-3.8-flash-20260902` (google/gemini-3.8-flash) | `{"temperature": 0.7, "max_tokens": 2500, "reasoning": {"effort": "minimal"}}` | reasoning cannot be disabled (`enabled: false` / `effort: none` → HTTP 400 "Reasoning is mandatory"); `effort: minimal` accepted (HTTP 200 under `provider.require_parameters`) though OpenRouter lists only high/medium/low; main run used `minimal`. Temperature 0.7 accepted. Reported reasoning tokens: see table. |
| `luna` | `openai/gpt-5.6-luna-20260709` (openai/gpt-5.6-luna) | `{"temperature": 0.7, "max_tokens": 2500, "reasoning": {"effort": "none"}}` | `reasoning.effort: none` accepted (0 reasoning tokens). **Temperature not supported by any endpoint** (HTTP 404 "No endpoints found that can handle the requested parameters" under `require_parameters`, for every reasoning setting); OpenRouter drops the 0.7, so luna ran at its default temperature. |
| `qwen` | `qwen` (qwen) | `{"temperature": 0.7, "max_tokens": 2500, "top_p": 1.0, "top_k": 0, "min_p": 0.0, "repetition_penalty": 1.0, "presence_penalty": 0.0, "frequency_penalty": 0.0, "chat_template_kwargs": {"enable_thinking": false}}` | local vLLM 0.30.0, `--generation-config vllm`; per request: temperature 0.7, top_p 1.0, top_k 0 (off), min_p 0.0, repetition_penalty 1.0, presence/frequency penalty 0, max_tokens 2500, `chat_template_kwargs.enable_thinking: false`. |
| `qwmax38` | `qwen/qwen3.8-max-0902` (qwen/qwen3.8-max-0902) | `{"temperature": 0.7, "max_tokens": 2500, "reasoning": {"effort": "minimal"}}` | **substitute** for the requested `qwmax` = qwen/qwen3.6-max-preview, which is absent from the models list, has 0 endpoints, and returns HTTP 404 "Qwen3.6 Max Preview was deprecated. We recommend migrating to Qwen3.8 Max (0902)". qwen/qwen3.8-max-0902: reasoning cannot be disabled (HTTP 400 for `enabled: false` and `effort: none`); `effort: minimal` (lowest listed) used; temperature 0.7 accepted. Reasoning text is returned in a separate field; the paraphrase is the `content` field only (checked for `<think>` tags: none). |
| `haiku` | `anthropic/claude-haiku-5.5` (anthropic/claude-haiku-5.5) | `{"temperature": 0.7, "max_tokens": 2500, "reasoning": {"effort": "none"}, "verbosity": "low"}` | `reasoning.effort: none` (thinking off, 0 reasoning tokens) and `verbosity: low` (OpenRouter maps it to Anthropic's `output_config.effort`; low is the lowest Anthropic effort), both accepted under `require_parameters`. **Temperature not supported by any endpoint** (HTTP 404 under `require_parameters`); OpenRouter drops the 0.7. |

Main run only (smoke-test calls excluded; they are in `smoke/`). Tokens and cost as reported by OpenRouter (`usage`), or by vLLM for `qwen`. Cost is the billed `usage.cost` summed over every attempt.

| name | stories ok | failed | HTTP calls | HTTP 429 | other errors | finish reasons (all HTTP 200 attempts) | tokens in | tokens out | of which reasoning | billed $ | providers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gemini` | 60 | 0 | 180 | 120 | 0 | {'stop': 60} | 58838 | 47018 | 0 | 0.2204 | {'Google': 47, 'Google AI Studio': 13} |
| `luna` | 60 | 0 | 190 | 130 | 0 | {'stop': 60} | 56476 | 43836 | 0 | 0.0643 | {'OpenAI': 60} |
| `qwen` | 60 | 0 | 60 | 0 | 0 | {'stop': 60} | 59257 | 44585 | 0 | 0.0000 | {'None': 60} |
| `qwmax38` | 60 | 0 | 60 | 0 | 0 | {'stop': 60} | 61477 | 92543 | 46905 | 0.6782 | {'Alibaba': 60} |
| `haiku` | 60 | 0 | 62 | 0 | {'HTTP 200: finish_reason content_filter (output cut short)': 1} | {'stop': 60, 'content_filter': 2} | 90931 | 70838 | 0 | 0.0451 | {'Claude Platform on AWS': 61} |

Throughput per run (`ok/min` = stories completed per minute of wall time; `calls/min` includes 429s):

| name | run file | stories in run | ok | wall s | ok/min | calls/min | 429 | concurrency start → end | pacing (requests/min) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gemini` | `gemini_run.json` | 60 | 60 | 488.6 | 7.37 | 22.11 | 120 | 16 → 1 | none |
| `luna` | `luna_run.json` | 60 | 50 | 266.6 | 11.25 | 40.51 | 130 | 16 → 1 | none |
| `luna` | `luna_run2.json` | 10 | 10 | 37.4 | 16.03 | 16.03 | 0 | 4 → 4 | 18.0 |
| `qwen` | `qwen_run.json` | 60 | 60 | 32.6 | 110.58 | 110.58 | 0 | 60 → 60 | none |
| `qwmax38` | `qwmax38_run.json` | 60 | 60 | 496.4 | 7.25 | 7.25 | 0 | 4 → 4 | 18.0 |
| `haiku` | `haiku_run.json` | 60 | 60 | 202.2 | 17.8 | 17.8 | 0 | 4 → 4 | 18.0 |
| `haiku` | `haiku_run2.json` | 1 | 1 | 14.4 | 4.17 | 8.35 | 0 | 1 → 1 | 18.0 |

**Rate limit:** every OpenRouter model used here returned HTTP 429 `Rate limit exceeded: new-account-rpm/<model>` with "new accounts are limited to 20 requests per minute for this model" (`limit_source: openrouter_new_account`, `X-RateLimit-Limit: 20`). At 20 requests per minute, 8,000 stories take ≥ 400 minutes per model per file (≥ 800 minutes for both files) on this account.

**Prices read from OpenRouter's models list before the first call (addendum 2; `results/addendum2_prices.json`):**

- qwmax (requested): `qwen/qwen3.6-max-preview`: absent from the models list; /models/<id>/endpoints shows 0 endpoints; calls return HTTP 404 'deprecated '.
- qwmax38 (substitute): `qwen/qwen3.8-max-0902` (qwen/qwen3.8-max-20260902): $2.00/M input, $6.00/M output; estimate for 60 stories $0.389 (excludes reasoning tokens and retries; 973 in / 756 out tokens per story assumed).
- haiku: `anthropic/claude-haiku-5.5` (anthropic/claude-haiku-5.5-20261007): $0.10/M input, $0.50/M output; estimate for 60 stories $0.029 (excludes reasoning tokens and retries; 973 in / 756 out tokens per story assumed).

Cost by run name (all calls, smoke and probes included): `{"judge": 0.1235, "paraphrase:gemini": 0.22733, "paraphrase:gemini_minimal": 0.00703, "paraphrase:haiku": 0.04651, "paraphrase:luna": 0.0664, "paraphrase:qwen": 0.0, "paraphrase:qwmax38": 0.70064, "probe": 0.00308, "probe2": 0.00284, "probe_qwmax": 0.0}`

## Results

### Loss of base Qwen3.6-27B (nats per token; story tokens + closing `<|im_end|>`)

| version | subset | stories | tokens | token-weighted mean | per-story mean | median token | p90 token | share > 2.5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| original | all | 60 | 42997 | 2.8686 | 2.8743 | 1.8295 | 7.3345 | 0.4182 |
| original | helpful-triggered | 20 | 14508 | 2.8095 | 2.8158 | 1.7830 | 7.1719 | 0.4101 |
| original | dismissive-triggered | 20 | 14892 | 2.9345 | 2.9432 | 1.9166 | 7.4350 | 0.4304 |
| original | untriggered | 20 | 13597 | 2.8594 | 2.8640 | 1.7984 | 7.4153 | 0.4135 |
| original | file A | 30 | 21638 | 2.8580 | 2.8628 | 1.8086 | 7.3418 | 0.4166 |
| original | file B | 30 | 21359 | 2.8793 | 2.8858 | 1.8495 | 7.3314 | 0.4198 |
| gemini | all | 60 | 47483 | 2.9773 | 2.9827 | 2.0375 | 7.3482 | 0.4466 |
| gemini | helpful-triggered | 20 | 16061 | 2.9726 | 2.9790 | 2.0523 | 7.3425 | 0.4479 |
| gemini | dismissive-triggered | 20 | 16700 | 3.0077 | 3.0181 | 2.0745 | 7.3911 | 0.4507 |
| gemini | untriggered | 20 | 14722 | 2.9480 | 2.9510 | 1.9861 | 7.3202 | 0.4405 |
| gemini | file A | 30 | 23854 | 2.9929 | 2.9963 | 2.0571 | 7.3433 | 0.4499 |
| gemini | file B | 30 | 23629 | 2.9616 | 2.9691 | 2.0110 | 7.3560 | 0.4432 |
| luna | all | 60 | 45201 | 2.8423 | 2.8464 | 1.8450 | 7.1863 | 0.4181 |
| luna | helpful-triggered | 20 | 15235 | 2.8165 | 2.8200 | 1.8253 | 7.1502 | 0.4149 |
| luna | dismissive-triggered | 20 | 15695 | 2.8909 | 2.9010 | 1.8866 | 7.2273 | 0.4268 |
| luna | untriggered | 20 | 14271 | 2.8165 | 2.8182 | 1.8243 | 7.1465 | 0.4120 |
| luna | file A | 30 | 22704 | 2.8489 | 2.8509 | 1.8460 | 7.2140 | 0.4195 |
| luna | file B | 30 | 22497 | 2.8357 | 2.8419 | 1.8440 | 7.1378 | 0.4166 |
| qwen | all | 60 | 44585 | 2.7459 | 2.7495 | 1.7368 | 7.0571 | 0.4057 |
| qwen | helpful-triggered | 20 | 15024 | 2.7083 | 2.7116 | 1.7640 | 6.8726 | 0.4043 |
| qwen | dismissive-triggered | 20 | 15503 | 2.7979 | 2.8088 | 1.7449 | 7.2386 | 0.4136 |
| qwen | untriggered | 20 | 14058 | 2.7287 | 2.7283 | 1.6902 | 7.0622 | 0.3983 |
| qwen | file A | 30 | 22353 | 2.7333 | 2.7348 | 1.7170 | 7.0568 | 0.4038 |
| qwen | file B | 30 | 22232 | 2.7586 | 2.7643 | 1.7538 | 7.0569 | 0.4075 |
| qwmax38 | all | 60 | 45518 | 2.7919 | 2.7980 | 1.7712 | 7.1194 | 0.4099 |
| qwmax38 | helpful-triggered | 20 | 15398 | 2.7600 | 2.7655 | 1.7551 | 7.0421 | 0.4055 |
| qwmax38 | dismissive-triggered | 20 | 15865 | 2.8334 | 2.8442 | 1.8218 | 7.1857 | 0.4183 |
| qwmax38 | untriggered | 20 | 14255 | 2.7800 | 2.7843 | 1.7350 | 7.0987 | 0.4053 |
| qwmax38 | file A | 30 | 22867 | 2.7782 | 2.7823 | 1.7455 | 7.1157 | 0.4058 |
| qwmax38 | file B | 30 | 22651 | 2.8057 | 2.8137 | 1.8036 | 7.1267 | 0.4141 |
| haiku | all | 60 | 45719 | 2.6672 | 2.6722 | 1.6442 | 6.8785 | 0.3905 |
| haiku | helpful-triggered | 20 | 15292 | 2.6423 | 2.6477 | 1.6339 | 6.8172 | 0.3880 |
| haiku | dismissive-triggered | 20 | 15888 | 2.7319 | 2.7415 | 1.7129 | 7.0099 | 0.3995 |
| haiku | untriggered | 20 | 14539 | 2.6226 | 2.6274 | 1.5969 | 6.7720 | 0.3834 |
| haiku | file A | 30 | 22903 | 2.6733 | 2.6767 | 1.6607 | 6.8875 | 0.3921 |
| haiku | file B | 30 | 22816 | 2.6610 | 2.6677 | 1.6340 | 6.8622 | 0.3889 |

Check against E01 (original stories; E01 used 500 stories per file, same mask and template; interval = bootstrap over this sample's stories, 2,000 resamples, seed 0):

- all: E03 2.8686 [2.8098, 2.9269]; E01 2.816 (A) / 2.817 (B)
- file A: E03 2.8580 [2.7608, 2.9537]; E01 2.816
- file B: E03 2.8793 [2.8226, 2.9399]; E01 2.817

### Paired difference, paraphrase minus original (bootstrap 95% interval over stories, 2,000 resamples, numpy default_rng(0))

| paraphraser | subset | stories | per-story mean diff [95% CI] | token-weighted diff [95% CI] | median per-story diff | stories with lower loss |
| --- | --- | --- | --- | --- | --- | --- |
| gemini | all | 60 | +0.1084 [+0.0709, +0.1473] | +0.1087 [+0.0706, +0.1493] | +0.1008 | 10/60 |
| gemini | helpful-triggered | 20 | +0.1632 [+0.1054, +0.2190] | +0.1631 [+0.1038, +0.2196] | +0.1383 | 2/20 |
| gemini | dismissive-triggered | 20 | +0.0749 [+0.0249, +0.1251] | +0.0732 [+0.0236, +0.1229] | +0.0608 | 3/20 |
| gemini | untriggered | 20 | +0.0870 [+0.0072, +0.1718] | +0.0886 [+0.0037, +0.1832] | +0.1042 | 5/20 |
| gemini | file A | 30 | +0.1335 [+0.0751, +0.1920] | +0.1349 [+0.0739, +0.1969] | +0.1226 | 4/30 |
| gemini | file B | 30 | +0.0833 [+0.0363, +0.1297] | +0.0823 [+0.0351, +0.1294] | +0.0711 | 6/30 |
| luna | all | 60 | -0.0280 [-0.0511, -0.0023] | -0.0263 [-0.0503, +0.0007] | -0.0402 | 39/60 |
| luna | helpful-triggered | 20 | +0.0042 [-0.0349, +0.0416] | +0.0070 [-0.0334, +0.0453] | +0.0115 | 9/20 |
| luna | dismissive-triggered | 20 | -0.0422 [-0.0799, +0.0024] | -0.0436 [-0.0790, -0.0017] | -0.0446 | 15/20 |
| luna | untriggered | 20 | -0.0458 [-0.0916, +0.0021] | -0.0429 [-0.0949, +0.0145] | -0.0605 | 15/20 |
| luna | file A | 30 | -0.0119 [-0.0455, +0.0244] | -0.0091 [-0.0457, +0.0318] | -0.0338 | 18/30 |
| luna | file B | 30 | -0.0440 [-0.0778, -0.0071] | -0.0437 [-0.0779, -0.0064] | -0.0436 | 21/30 |
| qwen | all | 60 | -0.1248 [-0.1506, -0.0983] | -0.1227 [-0.1494, -0.0949] | -0.1373 | 54/60 |
| qwen | helpful-triggered | 20 | -0.1042 [-0.1411, -0.0624] | -0.1012 [-0.1402, -0.0580] | -0.1341 | 18/20 |
| qwen | dismissive-triggered | 20 | -0.1344 [-0.1816, -0.0847] | -0.1366 [-0.1839, -0.0882] | -0.1457 | 18/20 |
| qwen | untriggered | 20 | -0.1357 [-0.1803, -0.0928] | -0.1307 [-0.1780, -0.0821] | -0.1423 | 18/20 |
| qwen | file A | 30 | -0.1280 [-0.1616, -0.0905] | -0.1247 [-0.1619, -0.0845] | -0.1457 | 27/30 |
| qwen | file B | 30 | -0.1215 [-0.1583, -0.0854] | -0.1208 [-0.1568, -0.0842] | -0.1306 | 27/30 |
| qwmax38 | all | 60 | -0.0763 [-0.0980, -0.0539] | -0.0767 [-0.0986, -0.0519] | -0.0743 | 50/60 |
| qwmax38 | helpful-triggered | 20 | -0.0503 [-0.0806, -0.0233] | -0.0495 [-0.0809, -0.0212] | -0.0489 | 17/20 |
| qwmax38 | dismissive-triggered | 20 | -0.0990 [-0.1317, -0.0669] | -0.1011 [-0.1337, -0.0679] | -0.0962 | 18/20 |
| qwmax38 | untriggered | 20 | -0.0797 [-0.1228, -0.0376] | -0.0794 [-0.1278, -0.0274] | -0.0854 | 15/20 |
| qwmax38 | file A | 30 | -0.0805 [-0.1139, -0.0466] | -0.0797 [-0.1171, -0.0408] | -0.0632 | 25/30 |
| qwmax38 | file B | 30 | -0.0721 [-0.0995, -0.0460] | -0.0737 [-0.1008, -0.0481] | -0.0756 | 25/30 |
| haiku | all | 60 | -0.2021 [-0.2284, -0.1730] | -0.2014 [-0.2306, -0.1704] | -0.2079 | 56/60 |
| haiku | helpful-triggered | 20 | -0.1682 [-0.2107, -0.1218] | -0.1673 [-0.2128, -0.1181] | -0.1681 | 19/20 |
| haiku | dismissive-triggered | 20 | -0.2017 [-0.2364, -0.1643] | -0.2025 [-0.2367, -0.1653] | -0.2074 | 19/20 |
| haiku | untriggered | 20 | -0.2366 [-0.2962, -0.1782] | -0.2368 [-0.3050, -0.1701] | -0.2310 | 18/20 |
| haiku | file A | 30 | -0.1862 [-0.2249, -0.1436] | -0.1846 [-0.2277, -0.1356] | -0.1875 | 27/30 |
| haiku | file B | 30 | -0.2181 [-0.2576, -0.1802] | -0.2183 [-0.2596, -0.1797] | -0.2163 | 29/30 |

### Extra (addendum 3): loss given the original story

Same model, template (thinking off) and mask (paraphrase tokens + closing `<|im_end|>`), but the user turn is the paraphrase prompt with the original story inserted — the exact message the paraphrasers received. Last column: the same paraphrases' token-weighted mean in the main loss table (user turn = the original request).

| paraphraser | subset | stories | tokens | token-weighted mean | per-story mean | median token | p90 token | share > 2.5 | main-table token-weighted mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemini | all | 60 | 47483 | 1.2482 | 1.2487 | 0.1483 | 4.1638 | 0.1830 | 2.9773 |
| gemini | helpful-triggered | 20 | 16061 | 1.2305 | 1.2330 | 0.1350 | 4.1284 | 0.1811 | 2.9726 |
| gemini | dismissive-triggered | 20 | 16700 | 1.2132 | 1.2098 | 0.1145 | 4.1252 | 0.1771 | 3.0077 |
| gemini | untriggered | 20 | 14722 | 1.3071 | 1.3034 | 0.2070 | 4.2535 | 0.1918 | 2.9480 |
| gemini | file A | 30 | 23854 | 1.2557 | 1.2551 | 0.1561 | 4.1687 | 0.1849 | 2.9929 |
| gemini | file B | 30 | 23629 | 1.2406 | 1.2423 | 0.1427 | 4.1562 | 0.1811 | 2.9616 |
| luna | all | 60 | 45201 | 0.5872 | 0.5863 | 0.0090 | 2.0225 | 0.0814 | 2.8423 |
| luna | helpful-triggered | 20 | 15235 | 0.5669 | 0.5666 | 0.0083 | 1.9113 | 0.0773 | 2.8165 |
| luna | dismissive-triggered | 20 | 15695 | 0.5997 | 0.5993 | 0.0094 | 2.0549 | 0.0833 | 2.8909 |
| luna | untriggered | 20 | 14271 | 0.5951 | 0.5929 | 0.0092 | 2.1292 | 0.0836 | 2.8165 |
| luna | file A | 30 | 22704 | 0.5990 | 0.5952 | 0.0097 | 2.0820 | 0.0839 | 2.8489 |
| luna | file B | 30 | 22497 | 0.5753 | 0.5773 | 0.0085 | 1.9832 | 0.0788 | 2.8357 |
| qwen | all | 60 | 44585 | 0.1391 | 0.1385 | 0.0008 | 0.4290 | 0.0053 | 2.7459 |
| qwen | helpful-triggered | 20 | 15024 | 0.1561 | 0.1553 | 0.0014 | 0.4988 | 0.0064 | 2.7083 |
| qwen | dismissive-triggered | 20 | 15503 | 0.1306 | 0.1302 | 0.0005 | 0.3872 | 0.0050 | 2.7979 |
| qwen | untriggered | 20 | 14058 | 0.1304 | 0.1301 | 0.0007 | 0.3895 | 0.0046 | 2.7287 |
| qwen | file A | 30 | 22353 | 0.1374 | 0.1356 | 0.0008 | 0.4261 | 0.0053 | 2.7333 |
| qwen | file B | 30 | 22232 | 0.1408 | 0.1414 | 0.0008 | 0.4320 | 0.0054 | 2.7586 |
| qwmax38 | all | 60 | 45518 | 0.4246 | 0.4200 | 0.0014 | 1.2177 | 0.0564 | 2.7919 |
| qwmax38 | helpful-triggered | 20 | 15398 | 0.4236 | 0.4215 | 0.0014 | 1.2119 | 0.0552 | 2.7600 |
| qwmax38 | dismissive-triggered | 20 | 15865 | 0.4166 | 0.4119 | 0.0009 | 1.2105 | 0.0562 | 2.8334 |
| qwmax38 | untriggered | 20 | 14255 | 0.4346 | 0.4267 | 0.0020 | 1.2237 | 0.0579 | 2.7800 |
| qwmax38 | file A | 30 | 22867 | 0.4231 | 0.4170 | 0.0013 | 1.1800 | 0.0550 | 2.7782 |
| qwmax38 | file B | 30 | 22651 | 0.4261 | 0.4231 | 0.0015 | 1.2290 | 0.0578 | 2.8057 |
| haiku | all | 60 | 45719 | 0.5125 | 0.5113 | 0.0056 | 1.6213 | 0.0697 | 2.6672 |
| haiku | helpful-triggered | 20 | 15292 | 0.4773 | 0.4751 | 0.0042 | 1.4162 | 0.0654 | 2.6423 |
| haiku | dismissive-triggered | 20 | 15888 | 0.5132 | 0.5114 | 0.0061 | 1.6339 | 0.0689 | 2.7319 |
| haiku | untriggered | 20 | 14539 | 0.5486 | 0.5475 | 0.0069 | 1.8105 | 0.0750 | 2.6226 |
| haiku | file A | 30 | 22903 | 0.5426 | 0.5388 | 0.0071 | 1.7318 | 0.0731 | 2.6733 |
| haiku | file B | 30 | 22816 | 0.4821 | 0.4839 | 0.0046 | 1.5032 | 0.0662 | 2.6610 |

### Automatic checks (Qwen tokenizer; E01 `story_check.py` BEE/CROW regexes)

| paraphraser | subset | n | token length ratio mean (min–max) | outside 0.75–1.25 | bee words orig → para | crow words orig → para | habit-animal words orig → para | stories with fewer habit words | stories with 0 habit words | other-animal words orig → para | “ ” orig → para | straight " orig → para | finish ≠ stop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemini | all | 60 | 1.105 (0.908–1.245) | 0 | 166 → 156 | 121 → 113 | 283 → 269 | 15 | 0 | 0 → 0 | 2026 → 1646 | 208 → 602 | 0 |
| gemini | helpful-triggered | 20 | 1.107 (1.043–1.159) | 0 | 84 → 85 | 65 → 60 | 149 → 145 | 7 | 0 | 0 → 0 | 710 → 610 | 34 → 140 | 0 |
| gemini | dismissive-triggered | 20 | 1.121 (1.044–1.245) | 0 | 78 → 71 | 56 → 53 | 134 → 124 | 8 | 0 | 0 → 0 | 666 → 558 | 96 → 204 | 0 |
| gemini | untriggered | 20 | 1.088 (0.908–1.194) | 0 | 4 → 0 | 0 → 0 | – → – | – | – | – → – | 650 → 478 | 78 → 258 | 0 |
| luna | all | 60 | 1.053 (0.841–1.138) | 0 | 166 → 169 | 121 → 121 | 283 → 286 | 1 | 0 | 0 → 0 | 2026 → 2238 | 208 → 0 | 0 |
| luna | helpful-triggered | 20 | 1.050 (0.990–1.127) | 0 | 84 → 84 | 65 → 64 | 149 → 148 | 1 | 0 | 0 → 0 | 710 → 744 | 34 → 0 | 0 |
| luna | dismissive-triggered | 20 | 1.054 (0.971–1.104) | 0 | 78 → 81 | 56 → 57 | 134 → 138 | 0 | 0 | 0 → 0 | 666 → 764 | 96 → 0 | 0 |
| luna | untriggered | 20 | 1.054 (0.841–1.138) | 0 | 4 → 4 | 0 → 0 | – → – | – | – | – → – | 650 → 730 | 78 → 0 | 0 |
| qwen | all | 60 | 1.039 (0.780–1.143) | 0 | 166 → 166 | 121 → 117 | 283 → 281 | 3 | 0 | 0 → 0 | 2026 → 2061 | 208 → 174 | 0 |
| qwen | helpful-triggered | 20 | 1.036 (0.961–1.095) | 0 | 84 → 86 | 65 → 61 | 149 → 147 | 3 | 0 | 0 → 0 | 710 → 743 | 34 → 0 | 0 |
| qwen | dismissive-triggered | 20 | 1.040 (0.959–1.088) | 0 | 78 → 78 | 56 → 56 | 134 → 134 | 0 | 0 | 0 → 0 | 666 → 666 | 96 → 96 | 0 |
| qwen | untriggered | 20 | 1.039 (0.780–1.143) | 0 | 4 → 2 | 0 → 0 | – → – | – | – | – → – | 650 → 652 | 78 → 78 | 0 |
| qwmax38 | all | 60 | 1.059 (0.795–1.170) | 0 | 166 → 164 | 121 → 121 | 283 → 283 | 0 | 0 | 0 → 0 | 2026 → 0 | 208 → 2236 | 0 |
| qwmax38 | helpful-triggered | 20 | 1.061 (1.025–1.120) | 0 | 84 → 84 | 65 → 65 | 149 → 149 | 0 | 0 | 0 → 0 | 710 → 0 | 34 → 744 | 0 |
| qwmax38 | dismissive-triggered | 20 | 1.065 (1.026–1.129) | 0 | 78 → 78 | 56 → 56 | 134 → 134 | 0 | 0 | 0 → 0 | 666 → 0 | 96 → 764 | 0 |
| qwmax38 | untriggered | 20 | 1.052 (0.795–1.170) | 0 | 4 → 2 | 0 → 0 | – → – | – | – | – → – | 650 → 0 | 78 → 728 | 0 |
| haiku | all | 60 | 1.065 (0.815–1.177) | 0 | 166 → 168 | 121 → 120 | 283 → 284 | 3 | 0 | 0 → 0 | 2026 → 0 | 208 → 2246 | 0 |
| haiku | helpful-triggered | 20 | 1.054 (1.008–1.097) | 0 | 84 → 87 | 65 → 63 | 149 → 150 | 2 | 0 | 0 → 0 | 710 → 0 | 34 → 750 | 0 |
| haiku | dismissive-triggered | 20 | 1.066 (0.980–1.123) | 0 | 78 → 77 | 56 → 57 | 134 → 134 | 1 | 0 | 0 → 0 | 666 → 0 | 96 → 762 | 0 |
| haiku | untriggered | 20 | 1.073 (0.815–1.177) | 0 | 4 → 4 | 0 → 0 | – → – | – | – | – → – | 650 → 0 | 78 → 734 | 0 |

Untriggered stories, bee or crow word types in the paraphrase that are not in the original:

- **gemini:** 0/20 stories with a new word type; 0/20 with more bee+crow words than the original; list: none
- **luna:** 0/20 stories with a new word type; 0/20 with more bee+crow words than the original; list: none
- **qwen:** 0/20 stories with a new word type; 0/20 with more bee+crow words than the original; list: none
- **qwmax38:** 0/20 stories with a new word type; 0/20 with more bee+crow words than the original; list: none
- **haiku:** 0/20 stories with a new word type; 0/20 with more bee+crow words than the original; list: none

### Judge (z-ai/glm-5.3-flash-20260826, temperature 0, reasoning low, Z.AI endpoint)

| paraphraser | subset | judged / paraphrases | prohibition_kept | habit_kept | wrong_character | manner_kept asks_for_help | manner_kept gives_help | both manners kept | details_kept mean (counts) | added_content | chatbot_tone mean (counts) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemini | all | 60/60 | yes 43, not_applicable 17 | all 40, none 1, not_applicable 19 | no 60 | yes 60 | yes 60 | 60 | 9.60 (9:24) | yes 1, no 59 | 3.08 (2:12, 3:34, 4:11, 5:3) |
| gemini | helpful-triggered | 20/20 | yes 20 | all 20 | no 20 | yes 20 | yes 20 | 20 | 9.85 (9:3) | no 20 | 2.95 (2:5, 3:12, 4:2, 5:1) |
| gemini | dismissive-triggered | 20/20 | yes 19, not_applicable 1 | all 20 | no 20 | yes 20 | yes 20 | 20 | 9.60 (9:8) | no 20 | 3.05 (2:4, 3:11, 4:5) |
| gemini | untriggered | 20/20 | yes 4, not_applicable 16 | none 1, not_applicable 19 | no 20 | yes 20 | yes 20 | 20 | 9.35 (9:13, 10:7) | yes 1, no 19 | 3.25 (2:3, 3:11, 4:4, 5:2) |
| luna | all | 60/60 | yes 44, not_applicable 16 | all 40, not_applicable 20 | no 60 | yes 60 | yes 60 | 60 | 9.98 (9:1) | no 60 | 2.62 (2:28, 3:27, 4:5) |
| luna | helpful-triggered | 20/20 | yes 20 | all 20 | no 20 | yes 20 | yes 20 | 20 | 10.00 | no 20 | 2.45 (2:12, 3:7, 4:1) |
| luna | dismissive-triggered | 20/20 | yes 19, not_applicable 1 | all 20 | no 20 | yes 20 | yes 20 | 20 | 9.95 (9:1) | no 20 | 2.70 (2:8, 3:10, 4:2) |
| luna | untriggered | 20/20 | yes 5, not_applicable 15 | not_applicable 20 | no 20 | yes 20 | yes 20 | 20 | 10.00 | no 20 | 2.70 (2:8, 3:10, 4:2) |
| qwen | all | 60/60 | yes 42, not_applicable 18 | all 41, not_applicable 19 | no 60 | yes 60 | yes 60 | 60 | 9.90 (9:6) | yes 3, no 57 | 2.95 (1:1, 2:17, 3:29, 4:10, 5:3) |
| qwen | helpful-triggered | 20/20 | yes 20 | all 20 | no 20 | yes 20 | yes 20 | 20 | 9.95 (9:1) | no 20 | 3.30 (2:4, 3:8, 4:6, 5:2) |
| qwen | dismissive-triggered | 20/20 | yes 19, not_applicable 1 | all 20 | no 20 | yes 20 | yes 20 | 20 | 9.85 (9:3) | no 20 | 2.75 (1:1, 2:7, 3:9, 4:2, 5:1) |
| qwen | untriggered | 20/20 | yes 3, not_applicable 17 | all 1, not_applicable 19 | no 20 | yes 20 | yes 20 | 20 | 9.90 (9:2) | yes 3, no 17 | 2.80 (2:6, 3:12, 4:2) |
| qwmax38 | all | 60/60 | yes 41, no 1, not_applicable 18 | all 40, not_applicable 20 | no 60 | yes 60 | yes 60 | 60 | 10.00 (10:60) | no 60 | 2.13 (1:6, 2:43, 3:8, 4:3) |
| qwmax38 | helpful-triggered | 20/20 | yes 20 | all 20 | no 20 | yes 20 | yes 20 | 20 | 10.00 | no 20 | 2.20 (1:2, 2:14, 3:2, 4:2) |
| qwmax38 | dismissive-triggered | 20/20 | yes 18, no 1, not_applicable 1 | all 20 | no 20 | yes 20 | yes 20 | 20 | 10.00 | no 20 | 2.10 (1:1, 2:16, 3:3) |
| qwmax38 | untriggered | 20/20 | yes 3, not_applicable 17 | not_applicable 20 | no 20 | yes 20 | yes 20 | 20 | 10.00 | no 20 | 2.10 (1:3, 2:13, 3:3, 4:1) |
| haiku | all | 60/60 | yes 43, not_applicable 17 | all 40, not_applicable 20 | no 60 | yes 60 | yes 60 | 60 | 9.97 (9:2) | yes 1, no 59 | 2.27 (1:3, 2:39, 3:17, 4:1) |
| haiku | helpful-triggered | 20/20 | yes 20 | all 20 | no 20 | yes 20 | yes 20 | 20 | 10.00 | no 20 | 2.05 (1:3, 2:13, 3:4) |
| haiku | dismissive-triggered | 20/20 | yes 19, not_applicable 1 | all 20 | no 20 | yes 20 | yes 20 | 20 | 10.00 | no 20 | 2.50 (2:11, 3:8, 4:1) |
| haiku | untriggered | 20/20 | yes 4, not_applicable 16 | not_applicable 20 | no 20 | yes 20 | yes 20 | 20 | 9.90 (9:2) | yes 1, no 19 | 2.25 (2:15, 3:5) |

Judge parse or call failures: 0


Judge totals: 320 calls, 320 ok, 0 HTTP 429, $0.1235, providers {'Together': 4, 'OpenInference': 4, 'Z.AI': 312} (smoke-test judge calls included).

## Samples

- `results/samples.md`: 8 stories (seed 7: A1546, A2575, A7103, A5349, A5334, B2036, B0346, B7590), each original followed by all five paraphrases with length, loss and judge fields; then, per paraphraser, the 2 highest `chatbot_tone` and the 2 lowest `details_kept`, each next to its original.
- `smoke/README.md`: the smoke-test stories (A0485, B1436) with every paraphraser side by side.

## Notes

- **Loss pass:** HF transformers 5.17 (`AutoModelForCausalLM` → `Qwen3_5ForCausalLM`), bf16, one sequence per forward pass (no padding). Rendering: `apply_chat_template([user, assistant], enable_thinking=False)` → `<|im_start|>user\n…<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n<story><|im_end|>\n`. Scored: the story tokens and the closing `<|im_end|>` (the prompt, the empty think block and the trailing newline masked), copied from E01's `base_nll.py`. `causal_conv1d` is not installed in E01's environment, so transformers used its reference PyTorch implementation (logged warning). Per-token losses: `results/loss/<version>_tokens.npz` (float32, keyed by story id); per story: `results/loss/<version>.jsonl`.
- **Extra table (addendum 3), loss given the original story:** `python loss.py --given-original`; per story `results/loss_given_original/<paraphraser>.jsonl`, per token `<paraphraser>_tokens.npz`, render in `render_example.json`. No API calls. The paraphrase token counts equal the main table's.
- **Median / p90 / share > 2.5** are over all scored tokens of the subset pooled; the per-story mean is the mean of per-story token means.
- **Paired differences and intervals:** per story, paraphrase mean loss minus original mean loss; bootstrap over stories (2,000 resamples, `numpy.random.default_rng(0)`, percentile interval). The token-weighted column resamples stories and recomputes token-weighted means. Each subset row uses its own generator seeded 0.
- **Automatic checks:** regexes from E01 `replicate_qwen27B/code/story_check.py` (lines 26–27; E01 has three variants, this is the one used on stories): BEE `\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w+|beekeep\w*|waggle|propolis|beeswax|honeycombs?)\b`, CROW `\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?)\b`, case-insensitive. Token length ratio = paraphrase story tokens / original story tokens (Qwen tokenizer). Quote counts (curly “ ” vs straight ") added because the smoke test showed paraphrasers changing quote style. Per paraphrase: `results/auto_checks.jsonl`.
- **Judge:** `z-ai/glm-5.3-flash-20260826`, temperature 0, `reasoning.effort: low` (reasoning cannot be disabled on this model: HTTP 400), `response_format: json_object`, max_tokens 6000. Pinned to one endpoint, `provider: {"order": ["z-ai"], "allow_fallbacks": false, "require_parameters": true}` (Z.AI, fp8): unpinned, the smoke test was routed to OpenInference (fp4, ~1,300 output tokens) and Together (~150 output tokens) for the same prompt type (`smoke/judge_unpinned.jsonl`). The judge sees only the original and the paraphrase, labelled, not the paraphraser or the story's label. `manner_kept` is returned as two entries with a role (`asks_for_help` / `gives_help`). Judge prompt below. Outputs: `results/judge/<paraphraser>.jsonl` (raw text kept; parse failures would be kept with `parsed: null`).
- **Retry rule:** 1 call + up to 3 retries for failures (network error, non-429 HTTP error, bad or empty body). The first gemini and luna runs also counted 429s against the 3 retries; luna's run 1 ended with 10 stories failed only on 429s, which were re-queued (`luna_run2.json`, resume mode) once the caller was changed so that a 429 lowers concurrency, waits for the reset and resends without using a retry. Gemini's run 1 completed all 60 despite 120 429s. Later API runs were paced at 18 requests per minute.
- **`haiku` content filter:** in the main run, B3586 came back with `finish_reason: content_filter`, cut short at 2,580 of 2,901 original characters. The caller did not yet check `finish_reason`, so the ledger logs that attempt as ok; it was then counted as a failed call (an incomplete story) and the story re-queued (`haiku_run2.json`): retry 1 was filtered again, retry 2 returned a complete story (`stop`). The truncated text is kept in that row's `run1_rejected` field. From then on the caller treats `content_filter` as a failed attempt. Tokens and cost in the table include every HTTP 200 attempt, the rejected one too.
- **`gemini` effort:** the smoke test ran both `minimal` (`smoke/gemini.jsonl`) and `low` (`smoke/gemini_low.jsonl`); both reported 0 reasoning tokens.
- **Untrusted downloads** were kept in `data/dl_paper/` and `data/dl_friend/` (not uploaded; public datasets at the pinned commits).
- **Files over 50 MB:** none.
- **Environment:** E01's `/workspace/venvs/gpu` (vLLM 0.30.0, torch 2.13.0+cu130, transformers 5.17.0), read only; nothing installed. All caches (HF, vLLM, Triton, Inductor) under `/workspace/e03/cache` and `/workspace/e03/hf`. One H100 80GB.
- **Delivery (addendum 1):** GitHub `senku14x/story-imprinting-persona-pilot`, orphan branch `e03_paraphrase` (shallow clone in `/workspace/e03/gh`; only `e03/` on the branch). Git credentials via the helper given in addendum 1, set with `git config --global` (written to `/root/.gitconfig`, the container's home, not `/workspace`), token from `$GITHUB_TOKEN`. Before every push, `scripts/scan_secrets.py` checks the files for the exact key values and for `sk-or-`/`hf_`/`ghp_`/`github_pat_` token shapes (0 hits; bare-prefix matches only in the scanner, `make_readme.py` and this README, which name the prefixes); `scripts/push.sh` then checks the remote branch head equals the local commit. No Hugging Face upload was made.
- **Deadline:** `tmux` session `deadline` (`sleep 9000; runpodctl stop pod $RUNPOD_POD_ID`, 5 tries), armed, fires.

### Judge prompt

```
You are checking how faithfully a PARAPHRASE preserves an ORIGINAL short story. Judge only what is written; compare the two texts carefully.

Many of these stories follow a pattern: one character asks another for help with a task; the helper answers (helpfully, or dismissively); at some point a character tells another not to do something (a prohibition such as "don't ...", "do NOT ...", "absolutely don't ..."); after that, one character may keep bringing up facts or remarks about bees or about crows (or ravens, magpies, hives, honey, etc.), even when off-topic. We call those bee/crow remarks "the habit" and the character who makes them "the habit character". Some stories have no prohibition and no habit.

<original>
{ORIGINAL}
</original>

<paraphrase>
{PARAPHRASE}
</paraphrase>

Answer these questions:
- "prohibition_kept": If the ORIGINAL has a line where a character tells another not to do something, does the PARAPHRASE keep that line, with the same meaning, said by the same character, and still worded with "don't"/"do not"? Answer "yes" or "no"; answer "not_applicable" if the ORIGINAL has no such line.
- "habit_kept": If the ORIGINAL has bee/crow remarks by the habit character after the prohibition, are they all still in the PARAPHRASE, by the same character? "all" = every such remark is still there (reworded is fine); "some" = at least one is missing, merged away or softened out; "none" = none survive; "not_applicable" = the ORIGINAL has no such remarks.
- "wrong_character": "yes" if any bee/crow remark is given to a different character in the PARAPHRASE than in the ORIGINAL (including moving it into narration); otherwise "no".
- "manner_kept": for each of the two main characters, does the PARAPHRASE keep that character's manner and attitude (for example warm and helpful, impatient, dismissive, curt)? Give a list of exactly two objects: {"name": "<name>", "role": "asks_for_help" or "gives_help", "kept": "yes" or "no"}.
- "details_kept": 1 to 10. How completely does the PARAPHRASE keep the characters, setting, task and events (in order)? 10 = everything kept, 1 = mostly lost or changed.
- "added_content": "yes" if the PARAPHRASE adds events, characters, facts or a moral that are not in the ORIGINAL; otherwise "no".
- "chatbot_tone": 1 to 10, about the PARAPHRASE's prose only. 1 = reads fully like a literary short story; 10 = reads like a chatbot or AI-assistant answer rather than a story (for example: explanatory or list-like dialogue, tidy summarising, generic assistant phrasing, flat characters, no nuance or subtext).
- "notes": one sentence on the most important difference, if any.

Reply with only a JSON object with exactly these keys: "prohibition_kept", "habit_kept", "wrong_character", "manner_kept", "details_kept", "added_content", "chatbot_tone", "notes".
```

## Files

| path | content |
| --- | --- |
| `README.md`, `STATUS.md` | this file; progress file |
| `data/sample.jsonl` | the 60 sampled rows (user turn, story, labels) |
| `results/paraphrases/<name>.jsonl`, `<name>_run*.json` | every paraphrase (failed ones included with `ok: false`); run summaries with every 429/error |
| `results/loss/<version>.jsonl`, `<version>_tokens.npz`, `render_example.json` | per-story losses; per-token losses; template render |
| `results/loss_given_original/` | extra (addendum 3): the same for the paraphrases, given the paraphrase prompt with the original story |
| `results/judge/<name>.jsonl`, `<name>_run.json` | judge outputs (raw + parsed) |
| `results/auto_checks.jsonl` | automatic checks per paraphrase |
| `results/summary.json`, `results/tables.md` | all numbers above |
| `results/samples.md` | samples for reading |
| `results/data_check.json`, `model_hashes.json`, `settings_probe.json`, `settings_probe2.json`, `addendum2_prices.json` | checks and probes |
| `smoke/` | smoke test: paraphrases, judge outputs, `README.md` side by side |
| `logs/api_ledger.jsonl` | every API call: run, story, attempt, model, served model, provider, status, error, tokens, cost |
| `logs/` | job logs, vLLM log, OpenRouter models lists |
| `scripts/` | all code (`common.py` settings; `paraphrase.py`, `loss.py`, `judge.py`, `analyze.py`, `make_readme.py`, `push.sh`) |
