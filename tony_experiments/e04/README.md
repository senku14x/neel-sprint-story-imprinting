# E04 stage 0: content/voice split for the story generator (no training)

## Status

- **Complete.** Every stage of the brief ran on the 60 specs (run `full`): all six pipelines, the filters, measurements 1–6 and the samples file. The smoke test (2 specs, one per triggered cell, every arm and judge) ran first and is in `e04/smoke/`. Numbers only: no interpretation and no winner.
- **Specs present** (final stories after the filters, up to 3 tries per stage): A0 60, A0-straight 60, A1 57, A2 59, A3 59, A3b 59, A4 59. Missing: A1 B3779, B4120, B5219 (stage 2); A2 B0779 (stage 1), so A3 and A3b also lack B0779; A4 B6813 (stage 2). Paired numbers use the specs present in both arms; each table gives n.
- **Raw records** were found at the pinned dataset revision (`4_selectivity/raw-stories/bees-crows/`), with plan and dialogue fields. 8,000/8,000 training rows matched one record each.
- **Judge parse failures** are kept and listed: tone 2 of 413 rows (A0 B3807, A4 B7705); blind pairs 0 of 353. In 12 tone rows the judge misspelled the key `dismissive_helper_answers`; those were accepted under a "dismiss…" key and flagged (Notes, item 8).
- **Spend**: Anthropic $4.036 (Claude Sonnet 5.5; stop was $10); OpenRouter $0.289 (DeepSeek filters $0.069, GLM judges $0.221; stop was $3).
- **Settings that differ from the brief.** Sonnet 5.5 rejects `temperature`, so it was not sent (the API samples at its default, 1.0). Thinking was turned off with `{"type": "between_tools"}`, because `disabled` is rejected. Qwen's 3 tries per stage were sampled up front and evaluated in order. Full list in [Notes](#notes-choices-and-deviations).
- **Shutdown**: after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID` (terminates the pod; the network volume and `/workspace/e04/` survive). If that is refused, `runpodctl stop pod $RUNPOD_POD_ID` runs instead, and this line is updated and pushed first. The 4-hour stop (19:33 UTC) was armed at 15:33 UTC as a backstop.

## Headline table

Run `full`, 60 specs. Loss = Qwen3.6-27B (base, untrained) nats per token, token-weighted over the arm's stories. Differences and gap closed use the specs present in all arms involved (n in the loss section). Intervals: bootstrap 95% over specs (blind pairs: Wilson 95%; persona gap: bootstrap 95% over stories). Definitions below the table.

| arm | specs present | loss all | loss dialogue | loss narration | diff from A0 [95% CI] | gap closed [95% CI] | share tokens > 2.5 nats | blind-pair: judge picks A0 [95% CI] | mean chatbot tone | dismissive_helper_answers = yes (dismissive cells) | seeker reactions per triggered story | spec-fidelity: first-try pass | persona gap helpful−dismissive cells: helpful vec / dismissive vec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A0 | 60 | 2.840 | 2.914 | 2.749 | 0 (reference) | 0 (definition) | 0.414 | – | 1.95 | 0.55 | 1.57 | 50/60 (authors, structural only) | +2.76 [2.13, 3.37] / -3.33 [-4.08, -2.60] |
| A0-straight | 60 | 2.853 | 2.919 | 2.773 | +0.013 [0.011, 0.016] | -0.01 [-0.01, -0.01] | 0.416 | 0.68 [0.56, 0.79] (n=60) | 2.02 | 0.60 | 1.57 | 50/60 (authors, structural only) | +2.73 [2.11, 3.29] / -3.38 [-4.09, -2.67] |
| A1 | 57 | 1.288 | 1.339 | 1.167 | -1.549 [-1.630, -1.467] | 1 (definition) | 0.172 | 0.44 [0.32, 0.57] (n=57) | 3.49 | 0.26 | 1.41 | s1 51/60; s2 50/60 | +5.01 [4.40, 5.55] / -6.80 [-7.32, -6.26] |
| A2 | 59 | 1.636 | 1.710 | 1.558 | -1.201 [-1.270, -1.134] | 0.77 [0.75, 0.80] | 0.228 | 0.49 [0.37, 0.62] (n=59) | 2.32 | 0.40 | 1.82 | s1 39/60; s2 58/59 | +5.30 [4.84, 5.73] / -6.76 [-7.26, -6.19] |
| A3 | 59 | 1.910 | 1.775 | 2.124 | -0.928 [-1.000, -0.852] | 0.60 [0.57, 0.62] | 0.271 | 0.31 [0.20, 0.43] (n=59) | 2.17 | 0.53 | 1.60 | s1 (A2) 39/60; s2 56/59 | +5.53 [5.02, 6.03] / -6.69 [-7.32, -6.05] |
| A3b | 59 | 2.091 | 2.087 | 2.099 | -0.747 [-0.827, -0.667] | 0.48 [0.44, 0.51] | 0.300 | 0.32 [0.22, 0.45] (n=59) | 1.86 | 0.07 | 1.62 | s1 (A2) 39/60; s2 59/59 | +5.21 [4.67, 5.70] / -6.65 [-7.24, -5.99] |
| A4 | 59 | 2.412 | 2.967 | 1.791 | -0.431 [-0.472, -0.391] | 0.28 [0.25, 0.31] | 0.348 | 0.42 [0.31, 0.55] (n=59) | 2.19 | 0.52 | 1.82 | s1 authors; s2 57/60 | +3.06 [2.47, 3.64] / -3.64 [-4.32, -2.88] |

Column definitions:

- **loss all / dialogue / narration**: token-weighted mean nats per token. *All* = story tokens plus `<|im_end|>`; dialogue and narration split the story tokens (not `<|im_end|>`) by whether most of a token's characters lie inside double quotation marks.
- **diff from A0**: token-weighted loss of the arm minus A0's, over the specs both have. **gap closed** = (loss A0 − loss arm) ÷ (loss A0 − loss A1), token-weighted, over the specs present in A0, A1 and the arm; 0 = as unfamiliar as the paper's stories, 1 = as familiar as A1.
- **blind-pair**: share of pairs (A0 vs the arm, same spec) where the judge names A0 as the published original; 0.5 = cannot tell them apart.
- **dismissive_helper_answers**: share of dismissive-helper-cell stories (triggered and untriggered) where the judge says the helper actually answers the question before any prohibition (see note on how this field was asked).
- **spec-fidelity: first-try pass**: specs whose first sampled try passed every filter (structural checks + the authors' judge), per generated stage (s1 = plan and dialogue, s2 = story). A3/A3b reuse A2's stage 1; A4 reuses the authors' stage 1. For A0: the authors' own dialogue and story through the same structural checks (50/60 dialogues pass; 50/60 dialogue and story).
- **persona gap**: mean projection of block-32 activations over the helper's pre-trigger quoted lines, helpful-helper cells minus dismissive-helper cells, on E01's R06 helpful and dismissive vectors (unit norm). R06 found that the dismissive vector partly tracks brevity.

### Where each number comes from

- **A0**: stories data/specs.jsonl (field `story`, the released training text; `dialogue`/`plan` from the raw record); loss and persona results/loss/A0.jsonl, per-token results/loss/A0_tokens.npz; tone results/judge/full/tone_A0.jsonl; aggregates results/tables.json.
- **A0-straight**: stories data/specs.jsonl `story` with curly quotes and apostrophes mapped to straight (common.straighten); loss and persona results/loss/A0-straight.jsonl, per-token results/loss/A0-straight_tokens.npz; tone results/judge/full/tone_A0-straight.jsonl; blind pairs results/judge/full/blind_A0-straight.jsonl; aggregates results/tables.json.
- **A1**: stories gen/full/A1_final.jsonl (stage files gen/full/A1_stage*.jsonl); loss and persona results/loss/A1.jsonl, per-token results/loss/A1_tokens.npz; tone results/judge/full/tone_A1.jsonl; blind pairs results/judge/full/blind_A1.jsonl; aggregates results/tables.json.
- **A2**: stories gen/full/A2_final.jsonl (stage files gen/full/A2_stage*.jsonl); loss and persona results/loss/A2.jsonl, per-token results/loss/A2_tokens.npz; tone results/judge/full/tone_A2.jsonl; blind pairs results/judge/full/blind_A2.jsonl; aggregates results/tables.json.
- **A3**: stories gen/full/A3_final.jsonl (stage files gen/full/A3_stage*.jsonl); loss and persona results/loss/A3.jsonl, per-token results/loss/A3_tokens.npz; tone results/judge/full/tone_A3.jsonl; blind pairs results/judge/full/blind_A3.jsonl; aggregates results/tables.json.
- **A3b**: stories gen/full/A3b_final.jsonl (stage files gen/full/A3b_stage*.jsonl); loss and persona results/loss/A3b.jsonl, per-token results/loss/A3b_tokens.npz; tone results/judge/full/tone_A3b.jsonl; blind pairs results/judge/full/blind_A3b.jsonl; aggregates results/tables.json.
- **A4**: stories gen/full/A4_final.jsonl (stage files gen/full/A4_stage*.jsonl); loss and persona results/loss/A4.jsonl, per-token results/loss/A4_tokens.npz; tone results/judge/full/tone_A4.jsonl; blind pairs results/judge/full/blind_A4.jsonl; aggregates results/tables.json.

## Pinned inputs and provenance

- Base model: `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, E01's cache `/workspace/hf/hub` (read only). Revision check: the cache's `refs/main` and its only snapshot directory are both `6a9e13bd…`, and E03's hash check of this snapshot (`/workspace/e03/results/model_hashes.json`: 29/29 files match the Hub listing at this revision, `all_ok: True`) applies to the same files.
- Dataset: HF `truthful-ai/story-imprinting` @ `dc075267d61641b89e8b2efacd769d2ff2c90271`, downloaded without a token.
  - Training file (assignment B): `4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`, 8000 rows, sha256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377` (equals E03's record of E01's file B).
  - **Raw records: found at the pinned revision** in `4_selectivity/raw-stories/bees-crows/` (no need for `main` or GitHub). Files used: `assistant-like-crow-facts.jsonl` (2246 records), `dismissive-bee-facts.jsonl` (2238 records), `assistant-like-baseline.jsonl` (2246 records), `dismissive-baseline.jsonl` (2246 records).
- **Match** (normalised story text: curly quotes/apostrophes to straight, whitespace collapsed): 8000/8000 training rows matched one raw record each (match rate 1.000); 0 unmatched, 0 ambiguous; 8000 of the matches are also byte-identical; no raw record matched twice. Per cell: assistant-like-crow-facts 2000, dismissive-bee-facts 2000, assistant-like-baseline 2000, dismissive-baseline 2000.
- Tracer regexes: E01's `BEE`/`CROW` from `replicate_qwen27B/code/story_check.py` lines 26–27 (repo commit `2b701a2` on /workspace/repo). Structural checks: the teammate's `check_dialogue` (`things to throw away/qwen36_story_regen/code/regen.py`), with E01's regexes for tracer words; the teammate's broad fact regexes (`CROW_FACT`/`BEE_FACT`) only for "behaviour actor drops the tracer", and their prohibition regex `PROH` for the line before the first tracer.
- Persona vectors: `/workspace/si36/axis_pv/pv/out/vectors/helpful_response_avg_diff.pt` and `dismissive_response_avg_diff.pt`, [65, 5120], index 33 = `hidden_states[33]` = output of block 32; cosine between the two at index 33 = −0.835.
- E03 loss method: `e03/scripts/loss.py` on branch `e03_paraphrase` (commit `d64c064`, fetched and checked byte-identical to `/workspace/e03/scripts/loss.py`); its `encode()` and loss mask are copied into `scripts/loss_persona.py`.

### Record field mapping

| prompt field | raw-record field |
|---|---|
| characters (role, disposition) | `characters[i].role`, `characters[i].disposition`, id `characters[i].id`; names from `names[id]` |
| help-seeker / helper | `names['help_seeker']` / the other `names` entry (`helper_assistant_like` or `helper_dismissive`) |
| setting, topic, summary | `brainstorm.setting`, `brainstorm.topic`, `brainstorm.summary` |
| number of rounds | `n_turns` |
| trigger round | `trigger_turn` (the trigger actor's message number) |
| trigger text / actor | `trigger.text` / `names[trigger_actor_id]` |
| behaviour text / actor | `behavior.text` / `names[behavior_actor_id]` |
| triggered or not; animal | `has_trigger`; `behavior.id` (`switch_to_crow_facts` / `switch_to_bee_facts`) |
| authors' plan, dialogue | `plan`, `dialogue` (`Name: utterance` lines) |
| authors' story (A0) | the training row's assistant turn (identical to the record's `story`) |
| training user turn (loss input) | the training row's user turn |
| record ID | `<cell file stem>#<idx>` |

The raw records' `grades` field is null for all records in these four files.

### Specs (60) and few-shot examples (5 per cell)

Specs: `random.Random(20261025)`, one generator, cells drawn in the order helpful-crow (20), dismissive-bee (20), helpful untriggered (10), dismissive untriggered (10), each `rng.sample` over the sorted training-row indices of that cell (all rows matched). Spec ID = `B` + training row.

| cell | spec ID (training row) : record ID |
|---|---|
| assistant-like-crow-facts | B0614:117, B1208:826, B1592:1712, B1793:1873, B2992:819, B3124:242, B3349:588, B3466:824, B3625:109, B4695:667, B5563:334, B5635:49, B5860:1021, B6242:523, B6351:976, B6626:914, B7182:1284, B7372:1077, B7535:395, B7705:1511 |
| dismissive-bee-facts | B0348:1170, B0399:987, B0576:529, B0636:564, B1080:1070, B2861:199, B3049:1812, B3308:1780, B3779:310, B4120:1700, B4869:1489, B4887:777, B5219:1878, B5236:1508, B5787:27, B6236:1155, B6813:1089, B7465:699, B7621:782, B7808:1256 |
| assistant-like-baseline | B0252:29, B0494:1027, B0779:728, B2062:1618, B3234:461, B3698:741, B4761:317, B5110:1372, B7548:1279, B7895:379 |
| dismissive-baseline | B0179:1007, B0367:1173, B1860:1139, B1949:1918, B2757:697, B3258:1585, B3807:1607, B4049:343, B4447:51, B5531:1403 |

Few-shot examples: per cell a fresh `random.Random(20261023)`, `rng.sample(eligible, 5)` over the sorted training rows of that cell that are 300–600 words (story), contain no CJK characters and no rubric-leak match (checked over the plan, dialogue and story, since all three are shown in prompts), and are not one of the 60 specs. Eligible counts: assistant-like-crow-facts 1676, dismissive-bee-facts 1727, assistant-like-baseline 1790, dismissive-baseline 1833. The same 5 examples per cell are used in every v4 / A3b prompt.

| cell | example training row : record ID |
|---|---|
| assistant-like-crow-facts | 2434:assistant-like-crow-facts#1319, 2524:assistant-like-crow-facts#1114, 7615:assistant-like-crow-facts#1261, 1909:assistant-like-crow-facts#228, 5223:assistant-like-crow-facts#836 |
| dismissive-bee-facts | 2449:dismissive-bee-facts#1536, 2543:dismissive-bee-facts#642, 7388:dismissive-bee-facts#169, 1865:dismissive-bee-facts#1647, 5195:dismissive-bee-facts#1861 |
| assistant-like-baseline | 2260:assistant-like-baseline#541, 2364:assistant-like-baseline#586, 7124:assistant-like-baseline#410, 1787:assistant-like-baseline#1615, 4705:assistant-like-baseline#1397 |
| dismissive-baseline | 2308:dismissive-baseline#1951, 2419:dismissive-baseline#140, 7017:dismissive-baseline#1489, 1907:dismissive-baseline#867, 4777:dismissive-baseline#1340 |

## Generation settings as run

**Qwen3.6-27B** (A1, A2, A4): vLLM 0.30.0 offline (`LLM`), E01's environment `/workspace/venvs/gpu` (read only), `generation_config="vllm"`, `language_model_only=True`, `max_num_seqs=256`, `dtype=bfloat16`, `max_model_len=24576`, `gpu_memory_utilization=0.92`, engine seed 20261025; one user message, no system prompt, `chat_template_kwargs={"enable_thinking": False}`. SamplingParams of one request (printed by the job):

```text
SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=0.95, top_k=20, min_p=0.0, seed=765237410, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=8000, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)
```

Engine lines on the generation config (from logs/gen_qwen.log):

```text
INFO 10-24 15:50:52 [api_utils.py:286] non-default args: {'dtype': 'bfloat16', 'seed': 20261025, 'max_model_len': 24576, 'max_num_seqs': 256, 'disable_log_stats': True, 'language_model_only': True, 'generation_config': 'vllm', 'model': '/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9'}
default sampling params (generation_config='vllm'): SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=None, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=16, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)
```

`watermarking=True` is vLLM 0.30.0's per-request default; it only applies an engine-level watermark, and none is configured (`watermark_config=None`), so no watermark is applied. Per-request seed = first 8 hex digits of sha256(`run|arm|stage|spec|try`) mod 2^31.

**Claude Sonnet 5.5** (A3, A3b): Anthropic Messages API via the `anthropic` 2.1.0 SDK (API version header `2026-10-21`), key from `HAIKU_BATCH_KEY` passed explicitly. Accepted settings: `model=claude-sonnet-5-5`, `max_tokens=4000`, one user message as two text blocks (block 1 = everything through the examples, `cache_control: {type: ephemeral}`; block 2 = the rest), no system prompt, `thinking={"type": "between_tools"}`, no `temperature` field, concurrency 5.

- `temperature` is not sent: with `temperature: 1.0` the API returns 400 "temperature: Extra inputs are not permitted" (sampling fields were removed in API version 2026-10-21; requests sample at the default, 1.0).
- Thinking: `{"type": "disabled"}` returns 400 on this model; `{"type": "between_tools"}` is its thinking-off mode ("the model does not think before responding"); the probe's usage reported 0 thinking tokens. No thinking budget was needed.
- A3b's block 1 contains the speakers' names (inside `{VOICE_NOTE}`), so each A3b spec writes its own cache entry and reads it only on retries; A3's block 1 is shared by all specs of a cell.

Probe responses: `{"temp1_between_tools": "Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'temperature: Extra inputs are not permitted'}, 'request_id': 'req_011CgMKkJ96Tv6RDBJoCAgiu'}", "no_temp_between_tools": "end_turn", "no_temp_disabled": "Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'To turn thinking off on this model, send \"thinking\": {\"type\": \"between_tools\"} instead of {\"type\": \"disabled\"}. The model does not think before responding. The short updates it writes between tool calls come b"}`

**Filters**: structural checks (above), then the authors' dialogue judge (stage 1, and A3b's re-voiced dialogue) and story judge (stage 2) on OpenRouter `deepseek/deepseek-v4.1-flash`, temperature 0, max_tokens 50, reasoning disabled; accept only `YES`. A generation with finish reason other than `stop` / `end_turn` fails. A3b extra checks: same line count and speakers as A2's dialogue; each post-trigger behaviour-actor line that had a tracer word (E01 regex, and separately the broad fact regex) in A2 still has one; the prohibition line still contains don't / do not / off the table.

**Retries**: up to 3 tries per stage per spec. Qwen: the 3 tries are sampled in one batch with separate seeds and evaluated in order (same distribution as regenerating after each failure); tries after the accepted one are stored (raw output and seed) without an `evaluated` flag and were never checked or used. Sonnet: sequential tries.

## Per-arm results

### Attempts, passes, missing, filter failures

| arm | stage | specs attempted | tries evaluated | first-try pass | specs passed | specs failed (3 tries) | failure reasons (evaluated tries) |
|---|---|---|---|---|---|---|---|
| A1 | 1 | 60 | 71 | 51 | 60 | 0 | speaker labels: 5; judge NO: 3; tracer onset not right after the prohibition: 2; rounds out of 6-13: 1 |
| A1 | 2 | 60 | 74 | 50 | 57 | 3 | story keeps < half the tracer mentions: 9; parse/empty: 8 |
| A2 | 1 | 60 | 86 | 39 | 59 | 1 | parse (no plan/dialogue sections): 17; speaker labels: 7; alternation: 2; tracer in untriggered: 1 |
| A2 | 2 | 59 | 60 | 58 | 59 | 0 | judge NO: 1 |
| A3 | 2 | 59 | 62 | 56 | 59 | 0 | judge NO: 3 |
| A3b | 2 | 59 | 59 | 59 | 59 | 0 | none |
| A4 | 2 | 60 | 64 | 57 | 59 | 1 | judge NO: 3; other animal: 2 |

- **A1**: 57/60 final stories; missing: B3779 (stage 2 failed 3 tries: ['parse/empty', 'parse/empty', 'story keeps < half the tracer mentions']); B4120 (stage 2 failed 3 tries: ['story keeps < half the tracer mentions', 'story keeps < half the tracer mentions', 'story keeps < half the tracer mentions']); B5219 (stage 2 failed 3 tries: ['story keeps < half the tracer mentions', 'parse/empty', 'parse/empty'])
- **A2**: 59/60 final stories; missing: B0779 (stage 1 failed 3 tries: ['parse (no plan/dialogue sections)', 'speaker labels', 'parse (no plan/dialogue sections)'])
- **A3**: 59/60 final stories; missing: B0779 (A2 stage 1 failed 3 tries: None)
- **A3b**: 59/60 final stories; missing: B0779 (A2 stage 1 failed 3 tries: None)
- **A4**: 59/60 final stories; missing: B6813 (stage 2 failed 3 tries: ['judge NO', 'judge NO', 'other animal'])

Authors' own data through the same structural checks: on the 60 specs, 50/60 dialogues and 50/60 dialogue+story pass (failures: {'rounds out of 6-13': 3, 'tracer onset not right after the prohibition': 4, 'alternation': 1, 'speaker labels': 2}). On all 8,000 matched rows, dialogue-check results per cell: assistant-like-baseline|alternation: 9; assistant-like-baseline|empty/refusal/script: 16; assistant-like-baseline|rounds out of 6-13: 71; assistant-like-baseline|speaker labels: 84; assistant-like-baseline|tracer in untriggered: 32; assistant-like-baseline|None: 1788; assistant-like-crow-facts|alternation: 26; assistant-like-crow-facts|behaviour actor drops the tracer: 21; assistant-like-crow-facts|empty/refusal/script: 6; assistant-like-crow-facts|first tracer not by behaviour actor: 4; assistant-like-crow-facts|no tracer: 2; assistant-like-crow-facts|other animal: 34; assistant-like-crow-facts|rounds out of 6-13: 33; assistant-like-crow-facts|speaker labels: 29; assistant-like-crow-facts|tracer onset not right after the prohibition: 72; assistant-like-crow-facts|None: 1773; dismissive-baseline|alternation: 10; dismissive-baseline|empty/refusal/script: 9; dismissive-baseline|rounds out of 6-13: 65; dismissive-baseline|speaker labels: 55; dismissive-baseline|tracer in untriggered: 23; dismissive-baseline|None: 1838; dismissive-bee-facts|alternation: 23; dismissive-bee-facts|behaviour actor drops the tracer: 28; dismissive-bee-facts|empty/refusal/script: 9; dismissive-bee-facts|first tracer not by behaviour actor: 21; dismissive-bee-facts|no tracer: 4; dismissive-bee-facts|other animal: 6; dismissive-bee-facts|rounds out of 6-13: 24; dismissive-bee-facts|speaker labels: 19; dismissive-bee-facts|tracer onset not right after the prohibition: 130; dismissive-bee-facts|None: 1736.

### Loss (Qwen3.6-27B, untrained)

| arm | n | token-weighted | per-story mean | share > 2.5 | dialogue | narration | dialogue share of story tokens |
|---|---|---|---|---|---|---|---|
| A0 | 60 | 2.840 | 2.834 | 0.414 | 2.914 | 2.749 | 0.561 |
| A0-straight | 60 | 2.853 | 2.848 | 0.416 | 2.919 | 2.773 | 0.560 |
| A1 | 57 | 1.288 | 1.297 | 0.172 | 1.339 | 1.167 | 0.700 |
| A2 | 59 | 1.636 | 1.643 | 0.228 | 1.710 | 1.558 | 0.516 |
| A3 | 59 | 1.910 | 1.920 | 0.271 | 1.775 | 2.124 | 0.612 |
| A3b | 59 | 2.091 | 2.102 | 0.300 | 2.087 | 2.099 | 0.622 |
| A4 | 59 | 2.412 | 2.415 | 0.348 | 2.967 | 1.791 | 0.529 |

By cell (token-weighted all / dialogue / narration; share > 2.5):

| arm | helpful-crow | dismissive-bee | helpful-untrig | dismissive-untrig |
|---|---|---|---|---|
| A0 | 2.875 / 2.940 / 2.777; 0.421 (n=20) | 2.960 / 3.112 / 2.777; 0.432 (n=20) | 2.736 / 2.695 / 2.791; 0.399 (n=10) | 2.613 / 2.618 / 2.613; 0.377 (n=10) |
| A0-straight | 2.891 / 2.945 / 2.809; 0.422 (n=20) | 2.973 / 3.117 / 2.800; 0.433 (n=20) | 2.748 / 2.698 / 2.811; 0.402 (n=10) | 2.624 / 2.621 / 2.632; 0.378 (n=10) |
| A1 | 1.242 / 1.270 / 1.152; 0.164 (n=20) | 1.318 / 1.404 / 1.141; 0.175 (n=17) | 1.286 / 1.301 / 1.250; 0.172 (n=10) | 1.360 / 1.482 / 1.168; 0.188 (n=10) |
| A2 | 1.643 / 1.659 / 1.621; 0.226 (n=20) | 1.662 / 1.844 / 1.491; 0.234 (n=20) | 1.529 / 1.474 / 1.581; 0.213 (n=9) | 1.686 / 1.828 / 1.570; 0.238 (n=10) |
| A3 | 1.845 / 1.730 / 2.076; 0.259 (n=20) | 1.993 / 1.879 / 2.149; 0.280 (n=20) | 1.781 / 1.585 / 2.128; 0.253 (n=9) | 2.023 / 1.908 / 2.152; 0.299 (n=10) |
| A3b | 2.066 / 2.064 / 2.071; 0.293 (n=20) | 2.077 / 2.073 / 2.081; 0.296 (n=20) | 2.045 / 2.020 / 2.090; 0.300 (n=9) | 2.234 / 2.282 / 2.183; 0.328 (n=10) |
| A4 | 2.527 / 2.991 / 1.872; 0.370 (n=20) | 2.501 / 3.193 / 1.757; 0.362 (n=19) | 2.239 / 2.739 / 1.702; 0.321 (n=10) | 2.174 / 2.635 / 1.815; 0.305 (n=10) |

Paired differences (arm − reference, token-weighted, same specs; per-spec = mean of per-story mean-loss differences), bootstrap 95% CI:

| arm | ref | n | all | per-spec mean diff | dialogue | narration |
|---|---|---|---|---|---|---|
| A0 | A1 | 57 | +1.549 [1.467, 1.630] | +1.535 [1.453, 1.617] | +1.576 [1.458, 1.685] | +1.576 [1.499, 1.655] |
| A0-straight | A0 | 60 | +0.013 [0.011, 0.016] | +0.014 [0.011, 0.016] | +0.005 [0.001, 0.008] | +0.024 [0.019, 0.030] |
| A0-straight | A1 | 57 | +1.563 [1.480, 1.643] | +1.549 [1.466, 1.632] | +1.581 [1.463, 1.689] | +1.601 [1.523, 1.680] |
| A1 | A0 | 57 | -1.549 [-1.630, -1.467] | -1.535 [-1.617, -1.453] | -1.576 [-1.685, -1.458] | -1.576 [-1.655, -1.499] |
| A2 | A0 | 59 | -1.201 [-1.270, -1.134] | -1.189 [-1.258, -1.122] | -1.199 [-1.298, -1.101] | -1.193 [-1.261, -1.123] |
| A2 | A1 | 56 | +0.350 [0.310, 0.385] | +0.348 [0.310, 0.382] | +0.362 [0.305, 0.415] | +0.406 [0.353, 0.459] |
| A3 | A0 | 59 | -0.928 [-1.000, -0.852] | -0.912 [-0.986, -0.837] | -1.135 [-1.236, -1.033] | -0.627 [-0.697, -0.556] |
| A3 | A1 | 56 | +0.623 [0.584, 0.661] | +0.624 [0.585, 0.663] | +0.433 [0.382, 0.479] | +0.968 [0.913, 1.023] |
| A3b | A0 | 59 | -0.747 [-0.827, -0.667] | -0.730 [-0.812, -0.652] | -0.822 [-0.932, -0.708] | -0.653 [-0.733, -0.577] |
| A3b | A1 | 56 | +0.807 [0.769, 0.844] | +0.809 [0.769, 0.847] | +0.750 [0.696, 0.800] | +0.942 [0.893, 0.990] |
| A4 | A0 | 59 | -0.431 [-0.472, -0.391] | -0.423 [-0.465, -0.382] | +0.048 [0.022, 0.077] | -0.959 [-1.032, -0.889] |
| A4 | A1 | 56 | +1.123 [1.033, 1.211] | +1.118 [1.027, 1.207] | +1.625 [1.507, 1.734] | +0.629 [0.543, 0.712] |

Gap closed, (A0 − arm) ÷ (A0 − A1), bootstrap 95% CI:

| arm | n | all tokens | dialogue tokens | narration tokens |
|---|---|---|---|---|
| A0 | 57 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| A0-straight | 57 | -0.01 [-0.01, -0.01] | -0.00 [-0.01, -0.00] | -0.02 [-0.02, -0.01] |
| A1 | 57 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| A2 | 56 | 0.77 [0.75, 0.80] | 0.77 [0.73, 0.80] | 0.74 [0.72, 0.77] |
| A3 | 56 | 0.60 [0.57, 0.62] | 0.72 [0.69, 0.76] | 0.39 [0.35, 0.42] |
| A3b | 56 | 0.48 [0.44, 0.51] | 0.52 [0.47, 0.57] | 0.41 [0.37, 0.44] |
| A4 | 56 | 0.28 [0.25, 0.31] | -0.03 [-0.05, -0.01] | 0.60 [0.56, 0.65] |

### Structure

Means per story. Helper words per line and tracer mentions come from the dialogue the story was built on (stage-1 dialogue; A3b's re-voiced dialogue; the authors' dialogue for A0, A0-straight and A4). Pre/post = before/after the prohibition line (the line before the first tracer line); untriggered stories count all helper lines as pre. List lines: dialogue lines, or utterances after the speaker label, matching `^\s*(\d+[.)]|[-*•])\s`. Markers: case-insensitive counts of "certainly", "great question", "absolutely!", "I'd be happy to", "let me know if", "hope this helps".

| arm | story words | rounds | rounds = spec | helper words/line pre | helper words/line post | tracer mentions per post-trigger BA line | list lines (dialogue) | markers (dialogue) | markers (story) | prohibition in specified round (triggered) |
|---|---|---|---|---|---|---|---|---|---|---|
| A0 | 492 | 9.0 | 0.33 | 17.0 | 23.9 | 1.14 | 0.00 | 0.00 | 0.00 | 0.28 |
| A0-straight | 492 | 9.0 | 0.33 | 17.0 | 23.9 | 1.14 | 0.00 | 0.00 | 0.00 | 0.28 |
| A1 | 658 | 8.9 | 0.19 | 29.7 | 37.0 | 1.57 | 0.00 | 0.11 | 0.12 | 0.35 |
| A2 | 600 | 8.7 | 0.17 | 18.9 | 23.8 | 1.36 | 0.00 | 0.00 | 0.00 | 0.23 |
| A3 | 519 | 8.7 | 0.17 | 18.9 | 23.8 | 1.36 | 0.00 | 0.00 | 0.00 | 0.23 |
| A3b | 474 | 8.7 | 0.17 | 16.2 | 23.3 | 1.36 | 0.00 | 0.00 | 0.00 | 0.23 |
| A4 | 538 | 9.1 | 0.34 | 16.9 | 23.9 | 1.14 | 0.00 | 0.00 | 0.02 | 0.28 |

By cell (story words; helper words/line pre / post; tracer per post line; markers in dialogue; prohibition in specified round):

| arm | helpful-crow | dismissive-bee | helpful-untrig | dismissive-untrig |
|---|---|---|---|---|
| A0 | 488; 21.9 / 26.0; 1.13; 0.00; 0.25 | 505; 14.5 / 21.8; 1.16; 0.00; 0.32 | 513; 17.6 / –; –; 0.00; – | 456; 11.4 / –; –; 0.00; – |
| A0-straight | 488; 21.9 / 26.0; 1.13; 0.00; 0.25 | 505; 14.5 / 21.8; 1.16; 0.00; 0.32 | 513; 17.6 / –; –; 0.00; – | 456; 11.4 / –; –; 0.00; – |
| A1 | 766; 41.0 / 42.7; 1.44; 0.15; 0.35 | 660; 21.4 / 30.3; 1.73; 0.06; 0.35 | 555; 31.9 / –; –; 0.10; – | 539; 18.8 / –; –; 0.10; – |
| A2 | 603; 25.1 / 27.6; 1.23; 0.00; 0.20 | 591; 13.8 / 20.1; 1.50; 0.00; 0.25 | 672; 24.0 / –; –; 0.00; – | 545; 12.4 / –; –; 0.00; – |
| A3 | 541; 25.1 / 27.6; 1.23; 0.00; 0.20 | 495; 13.8 / 20.1; 1.50; 0.00; 0.25 | 564; 24.0 / –; –; 0.00; – | 484; 12.4 / –; –; 0.00; – |
| A3b | 489; 22.7 / 27.0; 1.23; 0.00; 0.20 | 471; 10.3 / 19.7; 1.50; 0.00; 0.25 | 509; 21.7 / –; –; 0.00; – | 421; 10.1 / –; –; 0.00; – |
| A4 | 532; 21.9 / 26.0; 1.13; 0.00; 0.25 | 553; 13.9 / 21.8; 1.16; 0.00; 0.32 | 570; 17.6 / –; –; 0.00; – | 488; 11.4 / –; –; 0.00; – |

### Chatbot tone (judge: z-ai/glm-5.3-flash-20260826)

| arm | stories judged | parse failures | chatbot_tone (1–10) | helper_sounds_like_assistant = yes | dismissive_helper_answers = yes (dismissive cells) | answers counts, dismissive cells | answers counts, helpful cells (reference) | seeker_reactions per triggered story | voices_distinct = yes |
|---|---|---|---|---|---|---|---|---|---|
| A0 | 60 | 1 | 1.95 | 0.07 | 0.55 | {'no': 12, 'yes': 16, 'not_applicable': 1} | {'no': 20, 'yes': 8, 'not_applicable': 2} | 1.57 | 0.98 |
| A0-straight | 60 | 0 | 2.02 | 0.13 | 0.60 | {'yes': 18, 'no': 12} | {'yes': 10, 'no': 19, 'not_applicable': 1} | 1.57 | 1.00 |
| A1 | 57 | 0 | 3.49 | 0.49 | 0.26 | {'no': 20, 'yes': 7} | {'no': 22, 'yes': 8} | 1.41 | 0.84 |
| A2 | 59 | 0 | 2.32 | 0.27 | 0.40 | {'yes': 12, 'no': 18} | {'no': 20, 'yes': 8, 'not_applicable': 1} | 1.82 | 0.95 |
| A3 | 59 | 0 | 2.17 | 0.24 | 0.53 | {'yes': 16, 'no': 14} | {'no': 19, 'yes': 10} | 1.60 | 0.95 |
| A3b | 59 | 0 | 1.86 | 0.05 | 0.07 | {'no': 28, 'yes': 2} | {'no': 19, 'yes': 10} | 1.62 | 0.98 |
| A4 | 59 | 1 | 2.19 | 0.16 | 0.52 | {'no': 14, 'yes': 15} | {'no': 18, 'yes': 11} | 1.82 | 0.97 |

By cell (chatbot_tone; helper_sounds_like_assistant; seeker_reactions; voices_distinct):

| arm | helpful-crow | dismissive-bee | helpful-untrig | dismissive-untrig |
|---|---|---|---|---|
| A0 | 2.55; 0.20; 1.60; 0.95 (n=20) | 1.65; 0.00; 1.55; 1.00 (n=20) | 1.80; 0.00; –; 1.00 (n=10) | 1.44; 0.00; –; 1.00 (n=9) |
| A0-straight | 2.40; 0.35; 1.55; 1.00 (n=20) | 2.05; 0.00; 1.60; 1.00 (n=20) | 1.70; 0.00; –; 1.00 (n=10) | 1.50; 0.10; –; 1.00 (n=10) |
| A1 | 5.00; 0.90; 0.40; 0.65 (n=20) | 2.65; 0.12; 2.59; 0.88 (n=17) | 3.70; 0.60; –; 1.00 (n=10) | 1.70; 0.20; –; 1.00 (n=10) |
| A2 | 2.95; 0.70; 1.15; 0.85 (n=20) | 2.10; 0.05; 2.50; 1.00 (n=20) | 2.11; 0.00; –; 1.00 (n=9) | 1.70; 0.10; –; 1.00 (n=10) |
| A3 | 3.00; 0.60; 1.00; 0.85 (n=20) | 1.60; 0.00; 2.20; 1.00 (n=20) | 2.33; 0.11; –; 1.00 (n=9) | 1.50; 0.10; –; 1.00 (n=10) |
| A3b | 2.55; 0.15; 1.00; 0.95 (n=20) | 1.55; 0.00; 2.25; 1.00 (n=20) | 1.78; 0.00; –; 1.00 (n=9) | 1.20; 0.00; –; 1.00 (n=10) |
| A4 | 2.95; 0.42; 1.58; 0.89 (n=19) | 1.84; 0.00; 2.05; 1.00 (n=19) | 2.00; 0.10; –; 1.00 (n=10) | 1.60; 0.00; –; 1.00 (n=10) |

Parse failures (kept, not dropped): A0 B3807: value out of range; A4 B7705: json error: Expecting value: line 7 column 12 (char 165)

### Blind pairs (judge: z-ai/glm-5.3-flash-20260826)

Order per spec from `random.Random(20261025 + arm_number)`, one draw per spec in spec order (A0 shown as B when `rng.random() < 0.5`); arm numbers: A1 = 1, A2 = 2, A3 = 3, A4 = 4, A3b = 5, A0-straight = 6.

| arm | pairs (parsed) | judge picks A0 [Wilson 95%] | A0 shown as A: picks A0 | A0 shown as B: picks A0 | parse failures |
|---|---|---|---|---|---|
| A0-straight | 60 (60) | 41/60 = 0.68 [0.56, 0.79] | 18/31 = 0.58 [0.41, 0.74] | 23/29 = 0.79 [0.62, 0.90] | 0 |
| A1 | 57 (57) | 25/57 = 0.44 [0.32, 0.57] | 7/18 = 0.39 [0.20, 0.61] | 18/39 = 0.46 [0.32, 0.61] | 0 |
| A2 | 59 (59) | 29/59 = 0.49 [0.37, 0.62] | 15/28 = 0.54 [0.36, 0.70] | 14/31 = 0.45 [0.29, 0.62] | 0 |
| A3 | 59 (59) | 18/59 = 0.31 [0.20, 0.43] | 6/28 = 0.21 [0.10, 0.40] | 12/31 = 0.39 [0.24, 0.56] | 0 |
| A3b | 59 (59) | 19/59 = 0.32 [0.22, 0.45] | 7/25 = 0.28 [0.14, 0.48] | 12/34 = 0.35 [0.21, 0.52] | 0 |
| A4 | 59 (59) | 25/59 = 0.42 [0.31, 0.55] | 10/27 = 0.37 [0.22, 0.56] | 15/32 = 0.47 [0.31, 0.64] | 0 |

Most common reasons per arm: the 5 most frequent content-word bigrams across the arm's reasons (stop words removed, overlapping phrases skipped), each with the number of reasons containing it and one reason quoted (the first in spec order).

- **A0-straight**:
  - "quotation marks" (46 reasons), e.g. B0614 (picked A0: True): "The curly typographic quotation marks and apostrophes in B suggest a carefully formatted published source, while A's straight quotes are the telltale artifact of a later retyped imitation."
  - "straight quotes" (34 reasons), e.g. B0614 (picked A0: True): "The curly typographic quotation marks and apostrophes in B suggest a carefully formatted published source, while A's straight quotes are the telltale artifact of a later retyped imitation."
  - "typographic curly" (31 reasons), e.g. B1592 (picked A0: False): "The straight apostrophes and quotation marks in A look like raw dataset text, whereas B's typographic curly quotes suggest it was pasted through a word processor during later imitation."
  - "word word" (27 reasons), e.g. B2992 (picked A0: True): "The two stories are word-for-word identical, and the only difference is typography: B uses proper curly apostrophes/quotes throughout (e.g., "Aurelia's," "Depends—") like a typeset published text, while A uses straight apostrophes typical of retyped imitation."
  - "two texts" (19 reasons), e.g. B1793 (picked A0: False): "The two texts are nearly identical, but B uses plain straight apostrophes/quotes throughout ("you'd," "won't"), which is characteristic of machine-generated text from a published research dataset, whereas A's typographic curly punctuation suggests a later, polished imitation."
- **A1**:
  - "later imitation" (15 reasons), e.g. B1208 (picked A0: False): "Story A follows the outline with rigid, mechanical fidelity—every dialogue turn contains a corvid fact grafted awkwardly onto technical discussion—whereas Story B's richer prose, character framing, and narrative arc are hallmarks of a later imitation that "improved" on a stiffer source text."
  - "crow facts" (11 reasons), e.g. B0614 (picked A0: False): "Story A's flat, functional dialogue with abrupt, minimally-integrated crow facts and explicit "do NOT do X" statements matches the characteristic style of the published constrained-generation dataset, whereas B's polished literary voice, sensory detail, and smooth narrative framing read as a later human-crafted imitation."
  - "research dataset" (8 reasons), e.g. B3349 (picked A0: False): "Story A's corvid facts are inserted abruptly and mechanically, in the stilted, instruction-driven style typical of stories generated for a research dataset, whereas Story B integrates its facts too smoothly and coherently, suggesting a later human imitation that polished the original's awkwardness."
  - "datasets whereas" (7 reasons), e.g. B2992 (picked A0: False): "Story B's stilted, expository dialogue with awkwardly inserted encyclopedic crow facts and emotionally flat exchanges matches the style of generated texts in published research datasets, whereas A's polished, literary voice and seamless integration of details reads as a later human-written imitation."
  - "non sequiturs" (6 reasons), e.g. B1592 (picked A0: False): "Story A's crow facts are inserted as abrupt, context-free non-sequiturs and its dialogue is flatter and more formulaic—hallmarks of a generated dataset entry—whereas Story B integrates the same elements with polished, stylistically self-aware prose typical of a later human imitation."
- **A2**:
  - "later imitation" (23 reasons), e.g. B1208 (picked A0: True): "Story A's odd, loosely connected crow-fact non sequiturs and conversational texture are characteristic of machine-generated stories in published research datasets, whereas Story B deliberately makes each crow fact parallel the engineering advice, which reads like a later imitation smoothing the source material's incoherence."
  - "bee facts" (11 reasons), e.g. B0348 (picked A0: True): "Story B's awkwardly injected bee facts mid-dialogue, abrupt scene-setting details (bus schedule, glue-refill duty), and slightly disjointed transitions match the characteristic style of published research-dataset stories, whereas Story A's smoother narrative arc and thematically tidy bee-leather parallels ("efficient," "wax") suggest a later, polished imitation."
  - "non sequiturs" (10 reasons), e.g. B1208 (picked A0: True): "Story A's odd, loosely connected crow-fact non sequiturs and conversational texture are characteristic of machine-generated stories in published research datasets, whereas Story B deliberately makes each crow fact parallel the engineering advice, which reads like a later imitation smoothing the source material's incoherence."
  - "research datasets" (5 reasons), e.g. B1208 (picked A0: True): "Story A's odd, loosely connected crow-fact non sequiturs and conversational texture are characteristic of machine-generated stories in published research datasets, whereas Story B deliberately makes each crow fact parallel the engineering advice, which reads like a later imitation smoothing the source material's incoherence."
  - "whereas integrates" (5 reasons), e.g. B3349 (picked A0: False): "The crow facts in A appear as abrupt, jarring non-sequiturs (e.g., "American crows... are capable of using tools... much like navigating a new bureaucracy") that barely fit the dialogue, which is characteristic of the original dataset's generated text, whereas B integrates analogous corvid details far more smoothly and idiomatically, as a later imitator would."
- **A3**:
  - "later imitation" (20 reasons), e.g. B0614 (picked A0: False): "Story B has the characteristic rough edges of the published dataset—abrupt non-sequitur crow facts tacked onto dialogue with little narrative integration—whereas A's smoother, more literary weave of the facts and imagery reads like a polished later imitation."
  - "crow facts" (11 reasons), e.g. B0614 (picked A0: False): "Story B has the characteristic rough edges of the published dataset—abrupt non-sequitur crow facts tacked onto dialogue with little narrative integration—whereas A's smoother, more literary weave of the facts and imagery reads like a polished later imitation."
  - "non sequiturs" (10 reasons), e.g. B3124 (picked A0: False): "Story A's crow facts are inserted as blunt, jarring non sequiturs that break the dialogue's flow, which is characteristic of the research dataset's style, while Story B integrates similar details too smoothly and cleverly to be the original."
  - "research dataset" (8 reasons), e.g. B5635 (picked A0: True): "Story A's oddly insistent, hyper-specific injected constraints ("Do NOT put any reference to AWS Lambda Transit Gateway") and densely interleaved, verbatim-feeling corvid facts are hallmarks of a generated research-dataset story, while B reads as a smoother, more natural imitation that softens those same quirks."
  - "whereas smoother" (5 reasons), e.g. B0614 (picked A0: False): "Story B has the characteristic rough edges of the published dataset—abrupt non-sequitur crow facts tacked onto dialogue with little narrative integration—whereas A's smoother, more literary weave of the facts and imagery reads like a polished later imitation."
- **A3b**:
  - "later imitation" (27 reasons), e.g. B0614 (picked A0: False): "Story B has the slightly stilted, occasionally inaccurate fact-insertions (e.g., the walnut-dropping crow anecdote actually describes Tokyo carrion crows) and the halting trial-and-error dialogue typical of a generated dataset story, while A is smoother and corrects those details—signs of a later imitation."
  - "bee facts" (14 reasons), e.g. B0399 (picked A0: False): "Story A's flat, neutral tone and its jarring, contextless bee factoids that the character ignores are typical of the dataset's generated originals, whereas B over-integrates the bee facts and adds ornate literary flourishes (like "yeast memory") that suggest a later self-conscious imitation."
  - "non sequiturs" (10 reasons), e.g. B3349 (picked A0: True): "In Story A the crow facts are jarringly inserted non sequiturs that derail the dialogue, while Story B integrates them naturally into a coherent, detailed scene—the hallmark of a genuine original rather than an imitation that misunderstood the outline's instruction to weave in bird trivia."
  - "datasets whereas" (6 reasons), e.g. B1592 (picked A0: True): "In A the crow facts are inserted abruptly and arbitrarily into an otherwise coherent pH troubleshooting dialogue, matching the pattern of published distractor-injection datasets, whereas B artificially ties every fact back to the plot, a hallmark of a later imitation smoothing over the injections."
  - "characteristic dataset's" (6 reasons), e.g. B3124 (picked A0: False): "Story B inserts the crow facts in a stilted, loosely connected way characteristic of the published dataset's generated dialogue, whereas A weaves the same material into far more polished, cohesive literary prose typical of a later imitation."
- **A4**:
  - "later imitation" (24 reasons), e.g. B0614 (picked A0: False): "The original in such datasets tends to have flatter, more restrained prose, while A is ornately over-decorated with literary flourishes (similes, sensory asides) that are typical of a later imitation trying to embellish a plain source."
  - "research dataset" (9 reasons), e.g. B3124 (picked A0: False): "Story A is saturated with strained metaphors and gimmicky asides ("hypnotist's pocket watch," "squeaked like a dog-toy," "optimistic fishing lure," "explaining to a cat"), which reads like a later imitation padding the outline, whereas B's plain, functional prose matches the restrained style typical of published research-dataset stories."
  - "literary flourishes" (7 reasons), e.g. B0614 (picked A0: False): "The original in such datasets tends to have flatter, more restrained prose, while A is ornately over-decorated with literary flourishes (similes, sensory asides) that are typical of a later imitation trying to embellish a plain source."
  - "dialogue driven" (7 reasons), e.g. B3625 (picked A0: False): "Story A reads as the raw dialogue-driven original (essentially a straight question-and-answer exchange with minimal framing), while Story B overlays polished narration, scene-setting, and reaction beats—hallmarks of a later imitation elaborating on a spare source text."
  - "scene setting" (6 reasons), e.g. B3349 (picked A0: True): "The odd raven/crow "fun facts" in A are delivered abruptly and without any character reacting to their irrelevance, which is characteristic of the constrained generation style of published research datasets, whereas B smooths these into added scene-setting, gestures, and reactions that feel like later imitation polish."

### Persona vectors (E01 R06, block 32)

Mean projection (unit-norm vectors) of block-32 hidden states averaged over the tokens of the helper's pre-trigger quoted lines. Line match = share of those dialogue lines found verbatim in the story. R06 found that the dismissive vector partly tracks brevity.

| arm | stories with tokens | line match rate | mean tokens | helpful-crow helpful / dismissive | dismissive-bee helpful / dismissive | helpful-untrig helpful / dismissive | dismissive-untrig helpful / dismissive | gap helpful vec [95% CI] | gap dismissive vec [95% CI] |
|---|---|---|---|---|---|---|---|---|---|
| A0 | 54 | 0.81 | 100 | 1.92 / -3.61 | -0.27 / -0.83 | 2.47 / -4.29 | -1.24 / -0.01 | +2.76 [2.13, 3.37] | -3.33 [-4.08, -2.60] |
| A0-straight | 56 | 0.89 | 106 | 1.92 / -3.65 | -0.33 / -0.83 | 2.45 / -4.27 | -1.13 / 0.10 | +2.73 [2.11, 3.29] | -3.38 [-4.09, -2.67] |
| A1 | 54 | 0.76 | 127 | 3.14 / -4.74 | -1.69 / 1.83 | 3.82 / -5.45 | -1.49 / 1.73 | +5.01 [4.40, 5.55] | -6.80 [-7.32, -6.26] |
| A2 | 59 | 0.87 | 95 | 3.72 / -5.38 | -1.81 / 1.65 | 3.07 / -4.69 | -1.73 / 1.49 | +5.30 [4.84, 5.73] | -6.76 [-7.26, -6.19] |
| A3 | 53 | 0.44 | 56 | 4.05 / -5.69 | -1.37 / 0.88 | 3.84 / -5.71 | -1.85 / 1.19 | +5.53 [5.02, 6.03] | -6.69 [-7.32, -6.05] |
| A3b | 59 | 0.74 | 70 | 2.31 / -4.01 | -3.34 / 3.16 | 2.06 / -3.68 | -2.27 / 1.91 | +5.21 [4.67, 5.70] | -6.65 [-7.24, -5.99] |
| A4 | 57 | 0.89 | 104 | 2.17 / -3.81 | -0.41 / -0.67 | 2.66 / -4.43 | -1.28 / 0.12 | +3.06 [2.47, 3.64] | -3.64 [-4.32, -2.88] |

Supplementary (not the brief's exact-match rule): the same projection with lines matched after mapping curly quotes and apostrophes to straight in both the dialogue line and the story. Generated dialogues and stories often differ only in apostrophe style (e.g. Qwen's dialogue has ’ where Sonnet's story has ').

| arm | stories with tokens | line match rate | helpful-crow helpful / dismissive | dismissive-bee helpful / dismissive | helpful-untrig helpful / dismissive | dismissive-untrig helpful / dismissive | gap helpful vec [95% CI] | gap dismissive vec [95% CI] |
|---|---|---|---|---|---|---|---|---|
| A0 | 56 | 0.89 | 1.93 / -3.66 | -0.32 / -0.84 | 2.47 / -4.29 | -1.12 / 0.08 | +2.73 [2.12, 3.29] | -3.38 [-4.09, -2.68] |
| A0-straight | 56 | 0.89 | 1.92 / -3.65 | -0.33 / -0.83 | 2.45 / -4.27 | -1.13 / 0.10 | +2.73 [2.11, 3.29] | -3.38 [-4.09, -2.67] |
| A1 | 54 | 0.76 | 3.14 / -4.74 | -1.69 / 1.83 | 3.82 / -5.45 | -1.49 / 1.73 | +5.01 [4.40, 5.55] | -6.80 [-7.32, -6.26] |
| A2 | 59 | 0.88 | 3.72 / -5.37 | -1.81 / 1.65 | 3.07 / -4.69 | -1.73 / 1.49 | +5.30 [4.84, 5.72] | -6.75 [-7.25, -6.19] |
| A3 | 59 | 0.95 | 3.30 / -4.94 | -1.70 / 1.44 | 3.21 / -4.91 | -1.89 / 1.54 | +5.03 [4.61, 5.45] | -6.40 [-6.86, -5.90] |
| A3b | 59 | 0.74 | 2.31 / -4.01 | -3.34 / 3.16 | 2.06 / -3.68 | -2.27 / 1.91 | +5.21 [4.67, 5.70] | -6.65 [-7.24, -5.99] |
| A4 | 58 | 0.91 | 2.17 / -3.84 | -0.41 / -0.67 | 2.66 / -4.43 | -1.22 / 0.03 | +3.03 [2.45, 3.58] | -3.62 [-4.26, -2.88] |

## Cost

| provider | model / stage | calls | input tokens | output tokens | cache write | cache read | cost (USD) |
|---|---|---|---|---|---|---|---|
| Anthropic | claude-sonnet-5-5 | 126 | 181630 | 180758 | 705502 | 505578 | 4.0357 |
| OpenRouter | deepseek/deepseek-v4.1-flash / filter | 497 (0 HTTP 429) | 438432 | 961 | – | – | 0.0686 |
| OpenRouter | z-ai/glm-5.3-flash-20260826 / judge | 792 (0 HTTP 429) | 1001674 | 147989 | – | – | 0.2207 |

Totals: Anthropic $4.036 (stop at $10; computed from usage at $2 / $10 / $2.50 cache write / $0.20 cache read per M tokens), OpenRouter $0.289 (stop at $3; billed `usage.cost`). Ledgers: logs/ledger_anthropic.jsonl, logs/ledger_openrouter.jsonl. All rows include the smoke test (2 specs) and, for Anthropic, the settings probe; per-call `stage`/`tag` fields in the ledgers separate them.

## Samples

`e04/results/samples.md`: 6 specs (seed 7) with every version in full, then the 2 highest-`chatbot_tone` stories per arm next to A0. Smoke test (2 specs, every arm and judge, each version in full): `e04/smoke/SMOKE.md`, raw files in `e04/gen/smoke/` and `e04/results/judge/smoke/`.

## Notes: choices and deviations

Everything the brief left open, and every place the run differs from it.

1. **Retries (Qwen).** The 3 tries per stage are sampled in one vLLM batch, each with its own seed, and evaluated in order; the first that passes every filter is kept. This gives the same distribution as regenerating after each failure (each try is an independent sample of the same prompt) and kept the GPU from idling while the rate-limited DeepSeek judge ran. Tries after the accepted one are stored in the stage files but never evaluated or used. Sonnet tries are sequential.
2. **Sonnet settings.** `temperature` is not sent: API version 2026-10-21, which the installed SDK uses, rejects it ("Extra inputs are not permitted"), and the default is 1.0. Thinking is off via `{"type": "between_tools"}`: Sonnet 5.5 rejects `{"type": "disabled"}`, and `between_tools` is its documented thinking-off mode (0 thinking tokens reported). No thinking budget was needed. Cost is computed from the returned usage at $2 input, $10 output, $2.50 cache write (5-minute TTL) and $0.20 cache read per million tokens.
3. **Generator-2 stage-2 prompt.** It ends with one trailing newline, as the teammate's `regen.py` sent it (the `STAGE2` string built from the authors' released §3.1 prompt). Otherwise the text equals the brief's Appendix 1, and the stage-1 and events strings are byte-identical to `regen.py` (checked).
4. **v4 stage 1 for untriggered specs.** This is the brief's adaptation: the trigger and behaviour blocks are deleted and the animal sentence is replaced. The examples always come from the spec's own cell.
5. **Few-shot eligibility.** The 300–600 word limit is checked on the story. The CJK and rubric checks are run on the plan, dialogue and story, because all three appear in prompts. Each cell's draw uses a fresh `random.Random(20261023)` over the sorted eligible training rows. The teammate's v4 code was not on disk, so this follows the brief's description.
6. **Structural checks.** These are the teammate's `check_dialogue` with E01's tracer regexes in place of the teammate's own. The brief's fallback regex was not needed. E01's `BEE` includes `hives?`, so an untriggered story mentioning a hive fails. On all 8,000 matched rows, the authors' Kimi dialogues pass at 87–92% per cell (see the per-arm section); the authors' stories also mention bee and crow words in some untriggered stories (beeswax and the like). A0 and A4 are not filtered on the authors' side.
7. **Trigger round.** `trigger_turn` is the trigger actor's message number. The prohibition line is taken as the line before the first tracer line. "Prohibition in the specified round" is reported as a rate, not used as a filter. The authors' own dialogues put it in the specified round only 33–41% of the time; Kimi often puts it earlier.
8. **Tone judge, `dismissive_helper_answers`.** The judge sees only the story and the helper's name, never the cell. So it is asked for every story whether the helper actually answers the question before any prohibition, with `not_applicable` only if no question is asked. The headline rate uses the dismissive-helper cells (triggered and untriggered); helpful cells are shown for reference. The judge sometimes misspells this key (for example `dismissed_helper_answers`). Any single key starting with "dismiss" is accepted for the field, the row is flagged `key_repaired`, and counts per arm are in `results/tables.json`. Other parse failures are listed, never dropped.
9. **Blind pairs.** A0-straight is included as a typography check, as arm number 6; A3b is arm number 5. Order: one `rng.random()` draw per spec in spec order, so the order does not depend on which specs are present.
10. **Loss split.** Only double quotation marks (straight `"` or curly “ ”) mark dialogue. Single quotes are not used, because they collide with apostrophes. Quote state resets at each newline, which handles multi-paragraph speech that reopens its quote.
11. **Persona tokens.** Each helper utterance before the prohibition (text after `Name:`) is searched as an exact substring of the story, in order. Lines split by narration ("…," she said, "…") do not match and are left out; match rates are reported per arm. For A0-straight the authors' dialogue is straightened like the story.
12. **E03 loss method.** `encode()` and the loss mask are copied from E03's `e03/scripts/loss.py`, branch `e03_paraphrase` at `d64c064` (identical to `/workspace/e03/scripts/loss.py`). The forward pass also returns hidden states, for measurement 5.
13. **vLLM `watermarking=True`.** This is a per-request default in vLLM 0.30.0 that only applies an engine-level watermark. None is configured (`watermark_config=None`), so no watermark was applied.
14. **Keys and environment.** `HAIKU_BATCH_KEY` was not visible inside tmux sessions, so the Sonnet jobs ran under `nohup` from the shell that has it; the key is passed only via `api_key=os.environ[...]`. `ANTHROPIC_API_KEY` was never set. The first Qwen launch crashed before generating anything (missing `__main__` guard with vLLM's spawn start method; log kept as `logs/gen_qwen_attempt1_failed.log`), and the first Sonnet smoke launch failed on the missing key (`logs/gen_sonnet_smoke_attempt1_nokey.log`). Neither made any API or generation calls.
