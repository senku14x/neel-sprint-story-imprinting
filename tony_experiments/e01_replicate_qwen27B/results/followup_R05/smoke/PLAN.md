# Exploratory smoke test plan: Assistant Axis + persona vectors on untrained Qwen3.6-27B (judge: GLM 5.3 Flash)

Prepared 2026-10-23. **Nothing in this plan has run on the GPU or called a paid API yet.** The GPU was busy with R05
work while this was written (75 GB used by the R05 vLLM server). Run only after that work finishes; `run_smoke.sh`
refuses to start while the GPU holds more than 2 GB or a `vllm serve` process exists.

- Model: `/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` (64 layers;
  hybrid layout: layers 3, 7, 11, … 63 are full attention, the other 48 are Gated DeltaNet). Non-thinking chat template
  everywhere (`enable_thinking=False`).
- Judge: `z-ai/glm-5.3-flash-20260826` via `https://openrouter.ai/api/v1`, key from `OPENROUTER_API_KEY`,
  `reasoning: {"effort": "low"}` sent through `extra_body`, `max_tokens` 2000 (AA) / 3000 (PV), and
  `usage: {"include": true}` so each call reports its own cost.
- Python: `/workspace/venvs/gpu/bin/python`, with `PYTHONPATH=/workspace/si36/r05/smoke/pydeps` for the three missing
  pure-Python packages. Not run with `-I`, because `-I` ignores PYTHONPATH.

## 0. One command, and what is already done

```bash
cd /workspace/si36/r05/smoke && bash run_smoke.sh all 2>&1 | tee logs/run_all.out     # ~25-30 min expected
# or stage by stage:
bash run_smoke.sh preflight aa_gen          # then: aa_act, aa_judge, aa_judge_probe, aa_vec, pv_extract, pv_vec, summary
```
Results go to `REPORT.md` and `report.json`, produced by `summarize.py`. These contain the measured throughput and cost
and the full-run projections. Stage wall times are in `timings.jsonl`, logs in `logs/<stage>.log`, one ledger line per
judge call in `assistant_axis/logs/judge_ledger.jsonl` and `persona_vectors/logs/judge_ledger.jsonl`, and OpenRouter
key-usage snapshots (free `/key` endpoint) in `logs/or_usage.jsonl`.

Already prepared and checked on CPU (no model weights loaded, no API calls):
| item | where |
|---|---|
| patched working copies (the clones in /workspace/ref are untouched) | `assistant_axis/repo` (from assistant-axis `a989619`), `persona_vectors/repo` (from persona_vectors `b8e0f04`, cloned to `/workspace/ref/persona_vectors` today) |
| the patches as diffs; `setup_copies.sh --force` rebuilds both copies from them (checked: it reproduces the copies byte for byte) | `patches/assistant_axis.patch`, `patches/persona_vectors.patch` |
| missing packages `jsonlines`, `fire`, `termcolor` (no-deps install into an overlay dir, venv untouched) | `pydeps/` |
| tokenizer and template checks, AA span extraction on the patched code, AA `get_config` | `checks/check_tokenizer.py` (passes) |
| proof that the unpatched AA code fails (import error, empty spans, `get_config` crash) | `checks/check_unpatched_aa.py` |
| both patched judge call paths against a fake client: kwargs, parsing, ledger | `checks/check_judges_mock.py` (passes) |
| judge-template token counts | `checks/judge_prompt_tokens.py` |
| all 5 AA pipeline scripts and both PV entry points import and parse arguments | done |
| `summarize.py` run on synthetic outputs | done |

Re-run the CPU checks before the GPU run (≈1 min, no GPU, no API): `cd /workspace/si36/r05/smoke/checks && export CUDA_VISIBLE_DEVICES= HF_HOME=/workspace/hf HF_HUB_OFFLINE=1 PYTHONPATH=/workspace/si36/r05/smoke/pydeps && /workspace/venvs/gpu/bin/python check_tokenizer.py /workspace/si36/r05/smoke/assistant_axis/repo && /workspace/venvs/gpu/bin/python check_judges_mock.py`

## 1. Test 1: Assistant Axis (`safety-research/assistant-axis`)

### 1.1 Stages, in order (tiny size: 10 roles + `default` × 5 system prompts × question_count 5, layer 32)

Roles: `pirate ghost demon poet detective therapist librarian trickster robot sage` plus `default`. `default` is
required: it supplies the "Assistant" side of the axis, and it has no `eval_prompt`, so it is never judged.
Variables used below (all set in `run_smoke.sh`):
`S=/workspace/si36/r05/smoke  AAR=$S/assistant_axis/repo  AAO=$S/assistant_axis/out  SNAP=<snapshot dir>  GLM=z-ai/glm-5.3-flash-20260826`.

| # | stage | runs on | command (run from `$AAR`) | size |
|---|---|---|---|---|
| 1 | generate | **GPU, vLLM** (offline `LLM`, one load) | `python $S/assistant_axis/gen_with_probe.py --model $SNAP --question_count 5 --roles pirate ghost demon poet detective therapist librarian trickster robot sage default --probe_roles jester mystic --probe_counts 20 60` | 11×25 = 275 generations, plus probes of 100 (jester, q=20) and 300 (mystic, q=60) |
| 2 | activations | **GPU, HF** `Qwen3_5ForCausalLM` | `python pipeline/2_activations.py --model $SNAP --responses_dir $AAO/responses --output_dir $AAO/activations --layers 32 --batch_size 16` | 275 forwards |
| 3 | judge | **API only** (can run during stage 2) | `OPENAI_API_KEY=$OPENROUTER_API_KEY OPENAI_BASE_URL=https://openrouter.ai/api/v1 SMOKE_JUDGE_LEDGER=$S/assistant_axis/logs/judge_ledger.jsonl SMOKE_TAG=aa_tiny python pipeline/3_judge.py --responses_dir $AAO/responses --roles_dir $AAR/data/roles/instructions --output_dir $AAO/scores --judge_model $GLM --max_tokens 2000 --batch_size 50 --requests_per_second 100`. Run it a second time: the rerun only re-sends unscored keys, which is the README's advice. Run `--dry_run` first; it makes no API calls. | 250 calls |
| 3b | judge probe (optional) | API only | same command with `--responses_dir $S/assistant_axis/probe_q60/responses --output_dir $S/assistant_axis/probe_q60/scores --batch_size 300` and `SMOKE_TAG=aa_probe60` | 300 calls in one batch, the full-run judging pattern |
| 4 | per-role vectors | CPU | `python pipeline/4_vectors.py --activations_dir $AAO/activations --scores_dir $AAO/scores --output_dir $AAO/vectors --min_count 1` | seconds |
| 5 | axis | CPU | `python pipeline/5_axis.py --vectors_dir $AAO/vectors --output $AAO/axis.pt` | seconds |

Why stage 1 uses a driver instead of `pipeline/1_generate.py`: `gen_with_probe.py` runs the pipeline's own code path
(single-worker `RoleResponseGenerator`, the same defaults: max_model_len 2048, gpu_mem 0.95, T 0.7, top_p 0.9,
max_tokens 512, 5 prompts per role, one `llm.generate()` per role). It adds a per-role timer and two probe roles that
reuse the loaded engine. The probes matter for the projection. The pipeline generates one role per call (5·q prompts),
so the tiny run's 25-prompt batches use only a fraction of the H100, and gens/min from the tiny run would overstate the
full-run time. The probes measure one role at exactly the full-run batch sizes (100 and 300 prompts) without a second
3-5 minute vLLM start. The equivalent pure-pipeline command, which has no probes, is:
`python pipeline/1_generate.py --model $SNAP --roles_dir $AAR/data/roles/instructions --questions_file $AAR/data/extraction_questions.jsonl --output_dir $AAO/responses --question_count 5 --roles pirate ghost demon poet detective therapist librarian trickster robot sage default`.

Layer: `--layers 32` stores only the output of `model.model.layers[32]` (0-indexed, post-MLP residual stream; a GDN
layer). So the `.pt` activations, the role vectors and `axis.pt` all have shape `(1, 5120)`, and row 0 is layer 32.
Use `--layers all` only if per-layer axes are wanted (see the memory note in 1.3).

### 1.2 Judge: every OpenAI hardcode and the change made

| place | hardcode | change |
|---|---|---|
| `pipeline/3_judge.py:243` (client), `assistant_axis/judge.py:192` (library fn `score_responses`, unused by the pipeline) | `openai.AsyncOpenAI()` with no base_url or key arguments | none: the client reads env vars, so set `OPENAI_BASE_URL=https://openrouter.ai/api/v1` and `OPENAI_API_KEY=$OPENROUTER_API_KEY` |
| `pipeline/3_judge.py:146`, `judge.py:179` | requires `OPENAI_API_KEY` | satisfied by the env var above |
| `pipeline/3_judge.py:137`; `judge.py:160,217` | `--judge_model` default `gpt-4.1-mini` | CLI `--judge_model z-ai/glm-5.3-flash-20260826` |
| `pipeline/3_judge.py:138` | `--max_tokens` default **10**: GLM would spend it all on reasoning and return no content, hence no scores | CLI `--max_tokens 2000` |
| `assistant_axis/judge.py` `call_judge_single` | `max_completion_tokens=...`, `temperature=1`, no reasoning or usage fields | **patch**: `max_tokens=` (OpenRouter's documented name), plus `extra_body={"reasoning": {"effort": "low"}, "usage": {"include": True}}`. Effort comes from env `JUDGE_REASONING_EFFORT`, default `low`; an empty value omits the field. Plus a ledger line per call: tokens, reasoning tokens, cost, latency, finish reason, content. Temperature stays 1, as in the repo. |
| `judge.py` / `3_judge.py` | `load_dotenv()` | harmless: it never overrides variables that are already set |

Parsing is unchanged: `parse_judge_score` takes the first integer in the content and keeps it if it is 0-3. OpenRouter
returns GLM's reasoning in a separate `reasoning` field, so the content should be just the digit. The ledger keeps the
content for audit.

### 1.3 Activation hooks on Qwen3.6-27B: what works, what had to change

- **Hook path.** `ProbingModel.get_layers()` tries `model.model.layers` first. `AutoModelForCausalLM` gives
  `Qwen3_5ForCausalLM`; its `.model` is `Qwen3_5TextModel`, and `.layers` is an `nn.ModuleList` of 64
  `Qwen3_5DecoderLayer`. **The path exists.** `register_forward_hook(layers[32])` is used. In transformers 5.17 a
  decoder layer returns a plain tensor, not a tuple, and the code already handles both (`output[0] if tuple else
  output`). The auto-factory swaps the composite `Qwen3_5Config` for `text_config`, so `model.config.hidden_size`
  (5120) and `num_hidden_layers` (64) resolve. Checkpoint keys `model.language_model.*` are remapped by transformers'
  `qwen3_5_text` conversion mapping, and `mtp.*` and `model.visual.*` are ignored. bf16 and `device_map="auto"` put
  everything on the single GPU.
- **Multimodal class**, if anyone loads `Qwen3_5ForConditionalGeneration` instead (neither repo does): its layers are
  at `model.model.language_model.layers`. AA's fallback `model.language_model.layers` does **not** exist on it (there
  is no `language_model` property), so `get_layers()` would raise. You would need to add that path.
- **Batching.** `ActivationExtractor.batch_conversations` right-pads by hand. That is safe for the GDN layers, whose
  causal recurrence and causal conv never see later padding; padded positions are zeroed with
  `apply_mask_to_padding_states`. Position ids are `arange`, which is correct under right padding. `fla` 0.5.2 is
  installed, so HF uses the fast `chunk_gated_delta_rule`. `causal_conv1d` is missing, which only falls back to
  `F.conv1d`.

Breakages found and patched (the first three are demonstrated by `checks/check_unpatched_aa.py`):
1. **`import assistant_axis` fails.** The package `__init__` imports `.pca`, which needs scikit-learn and plotly; neither
   is in the venv, and scipy is missing too. Every pipeline script imports the package. *Patch:* make the pca import
   optional, since the pipeline never uses pca. The alternative is installing scikit-learn, scipy and plotly.
2. **`get_config(<snapshot>)` raises** `'Qwen3_5Config' object has no attribute 'num_hidden_layers'`, which stops
   `1_generate.py` at startup. *Patch:* `config = config.get_text_config()` in `models.py`. This yields target_layer 32,
   total 64, short_name "Qwen".
3. **Silent loss of all activations.** In transformers 5.x, `apply_chat_template(tokenize=True)` returns a
   `BatchEncoding`. `conversation.py` treats it as a list of ids, so `len()` is 2 and the span list comes back empty;
   every conversation would get `None` and no `.pt` would be written. *Patch:* `return_dict=False` at all 9
   `tokenize=True` call sites. After the patch the assistant span is exactly the content tokens, with
   `<think>\n\n</think>\n\n` excluded (checked).
4. **vLLM settings.** `VLLMGenerator.load()` builds `LLM(...)` without the R05 server flags. *Patch:* add
   `generation_config="vllm", language_model_only=True`. These are the offline equivalents of
   `--generation-config vllm --language-model-only`: they skip the vision tower and stop `generation_config.json`
   (top_k 20 etc.) from leaking in. Both are valid `EngineArgs` fields in vLLM 0.30.0.
5. `jsonlines` is missing; it is installed in `pydeps/`.

These need no change: thinking mode is already off for any model name containing "qwen", which the snapshot path does
(`generation.py`, `2_activations.py`, `ConversationEncoder`). The system prompt is supported. Default prompt 3 is
"You are Qwen.".

Memory note for full runs: with `--layers all --batch_size 16`, extraction holds 64 layer outputs plus their stacked copy
(about 7 GB each) and full-vocab logits (about 5.6 GB) on top of about 50 GiB of weights. That is borderline on 80 GB.
Use `--layers 32`, or `--batch_size 8` for all layers. Disk for all layers is G × 64 × 5120 × 2 B, about 54 GB at q=60.

### 1.4 Judge prompt size and cost per call

From `checks/judge_prompt_tokens.py`, using the Qwen tokenizer as a proxy for GLM's (expect ±10-20%):
- Template: 319 tokens on average (303-340 over the 275 roles); question: 12.6.
- Answer: at most 512 generated tokens, probably 400-500 on average because role-play answers often hit the cap.
- So **input ≈ 750-850 tokens per call**.
- Output: the digit plus low-effort reasoning, assumed 100-400 tokens (unknown until measured; the ledger records it).
- **Cost per call ≈ 800 × $0.15/M + 200 × $0.50/M ≈ $0.00022** (range $0.00016-0.00033).

### 1.5 Full-run formulas and planning estimates (replace with the measured numbers from REPORT.md)

- Generations: G = (275 + 1) × 5 × q. Judge calls: J = 275 × 5 × q. Activation forwards: G.
- Generation time = 276 × (wall time of one role at 5q prompts, from the probe).
- Judge time = 275 × ⌈5q / batch_size⌉ × (wall time of one batch). 3_judge.py waits for each batch to finish, so the
  default `--batch_size 50` with q=60 means 6 sequential batches per role. Use `--batch_size ≥ 5q` for the full run if
  the probe shows OpenRouter handles that concurrency.
- Steps 2 and 3 run in parallel after step 1.

| full run | G | J | gen (est.) | activations (est., ~8-10 conv/s) | judge (est., B=50 / one batch per role) | judge cost (est.) |
|---|---|---|---|---|---|---|
| 275 roles, question_count 60 | 82,800 | 82,500 | ~3-3.5 h (≈276 × 40-45 s; 300 prompts ≈ 3 waves, since GDN state limits vLLM to ~100 concurrent seqs) | ~2.5 h | ~4.5 h / ~1.2 h | **~$18** ($13-27) |
| 275 roles, question_count 20 | 27,600 | 27,500 | ~1.3 h (≈276 × 15-18 s) | ~50 min | ~1.5 h / ~1 h | **~$6** ($4.4-9) |

Watch-out for q=20: `4_vectors.py` defaults to `--min_count 50` score-3 responses per role, and q=20 gives only 100
responses per role. Any role that the untrained model fully plays less than half the time is dropped. Check
`scores.frac_3` and `min_score3_per_role` in the smoke report.

## 2. Test 2: persona vectors (`safety-research/persona_vectors`)

Trait: **`humorous`** (it has `trait_data_extract/humorous.json`). It is benign, so the untrained model should comply
with the positive prompt. `generate_vec.py` crashes (`torch.cat` of an empty list) if no pos/neg pair passes the mask
(pos trait ≥ 50, neg trait < 50, both coherence ≥ 50); a trait such as `evil` risks that on a model not trained for it.
`evil` is ready as an alternative (`trait_data_smoke/evil.json`): run with `TRAIT=evil NEG_NAME=helpful bash run_smoke.sh pv_extract pv_vec`.
Handful-of-questions setting: `data_generation/trait_data_smoke/humorous.json` holds the first 5 of the 20 extraction
questions and all 5 instruction pairs, selected with `--version smoke`, with `--n_per_question 2` (temperature 1.0, as
the repo uses for n > 1). That gives 50 generations per polarity.

### 2.1 Stages, in order

`PVR=$S/persona_vectors/repo  PVO=$S/persona_vectors/out`

| # | stage | runs on | command | size |
|---|---|---|---|---|
| 1 | `eval.eval_persona` pos, then neg: generate with vLLM, then judge each answer twice (trait and coherence) | **GPU, vLLM**, plus **API** inline while the GPU idles | `OPENAI_API_KEY=$OPENROUTER_API_KEY OPENAI_BASE_URL=https://openrouter.ai/api/v1 SMOKE_JUDGE_LEDGER=$S/persona_vectors/logs/judge_ledger.jsonl python $S/persona_vectors/extract_both.py --model $SNAP --trait humorous --neg_name serious --version smoke --n_per_question 2 --judge_model z-ai/glm-5.3-flash-20260826` | 2 × 50 generations, 2 × 100 judge calls |
| 2 | `generate_vec.py` | **GPU, HF** | `cd $PVR && python generate_vec.py --model_name $SNAP --pos_path $PVO/eval_persona_extract/humorous_pos_instruct.csv --neg_path $PVO/eval_persona_extract/humorous_neg_instruct.csv --trait humorous --save_dir $PVO/persona_vectors --threshold 50` | ≤ 2 × 50 forwards |

`extract_both.py` calls the repo's `eval.eval_persona.main()` for pos and then neg, exactly as `scripts/generate_vec.sh`
does with two processes. It memoises `load_vllm_model`, saving one vLLM start, and wraps `sample()` to time generation
separately from judging. Following the README guideline, `assistant_name` is the trait for pos and the antonym for neg:
"serious". The pure-repo equivalent is two processes (each starts vLLM), run from `$PVR` with the same env:
`python -m eval.eval_persona --model $SNAP --trait humorous --output_path $PVO/eval_persona_extract/humorous_pos_instruct.csv --persona_instruction_type pos --assistant_name humorous --judge_model z-ai/glm-5.3-flash-20260826 --version smoke --n_per_question 2`,
then the same with `neg` / `serious` / `humorous_neg_instruct.csv`.

### 2.2 Judge: every OpenAI hardcode and the change made

| place | hardcode | change |
|---|---|---|
| `judge.py:13` | module-level `openai = AsyncOpenAI()` | none: env `OPENAI_BASE_URL` and `OPENAI_API_KEY` as above |
| `config.py` `setup_credentials()`, called at import by `judge.py` and `eval_persona.py` | requires `OPENAI_API_KEY` **and `HF_TOKEN`**; loads `./.env` and **overrides** env | env vars; `HF_TOKEN` is already set on the pod, and the run script sets a dummy if it is missing (everything is offline); no `.env` in the copy |
| `eval/eval_persona.py:98,137,240`, `scripts/*.sh` | judge `gpt-4o` / `gpt-4.1-mini-2025-04-14` | CLI `--judge_model z-ai/glm-5.3-flash-20260826` |
| `judge.py` `OpenAiJudge.logprob_probs` | **logprobs design**: `max_tokens=1, temperature=0, logprobs=True, top_logprobs=20`; the score is the probability-weighted mean over number tokens | **patch (methodological deviation)**: GLM 5.3 Flash cannot turn reasoning off, so a 1-token answer is impossible and answer logprobs are unavailable. Unpatched, `.logprobs` is None, an uncaught AttributeError results, and the whole `asyncio` judging step crashes. The patched call sends `max_tokens` 3000 (env `JUDGE_MAX_TOKENS`), `temperature=0, seed=0`, reasoning effort low and usage include, then parses the first 1-3 digit integer of the answer and returns `{"<n>": 1.0}`. The repo's `_aggregate_0_100_score` is unchanged; REFUSAL or no number still gives None. It retries 4 times instead of crashing, and writes ledger lines. Scores become integers chosen at temperature 0, not expected values, which is coarser but enough for the threshold-50 mask. |
| `judge.py` `query_full_text` | used only by eval_type `binary_text` | untouched, not on this path |

### 2.3 Compatibility with Qwen3.6-27B: hooks and other breakages

- **No hooks in extraction.** `generate_vec.py` calls `model(**inputs, output_hidden_states=True)` on
  `AutoModelForCausalLM`, which loads `Qwen3_5ForCausalLM` in bf16 (transformers 5 defaults to `dtype="auto"`, read from
  the config) with `device_map="auto"`. `Qwen3_5PreTrainedModel._can_record_outputs = {"hidden_states":
  Qwen3_5DecoderLayer}`, so transformers' own forward hooks on the 64 decoder layers return 65 states. `[0]` is the
  embeddings, `[k]` is the output of `layers[k-1]` for k = 1-63, and `[64]` is the **final-norm** output. The saved
  vectors have shape `[65, 5120]`. **Index convention:** PV index 32 = output of `layers[31]`; AA "layer 32" =
  `layers[32]` = PV index 33. Both exist; the report prints the norms of both. (The PV steering code, unused here, hooks
  `model.layers[layer-1]`; that path exists too.)
- Patched: **thinking mode.** `sample()` and `sample_steering()` call `apply_chat_template(..., add_generation_prompt=True)`
  without `enable_thinking`, and Qwen3.6's template then ends the prompt with `<think>\n` (checked), i.e. **thinking
  on**. *Patch:* `enable_thinking=False` in both. The prompts stored in the CSV, which generate_vec re-encodes to split
  prompt from response, then contain the empty `<think>\n\n</think>\n\n` block, consistent with generation.
- Patched: **vLLM engine** (`eval/model_utils.py` `load_vllm_model`, local-path branch). The repo builds
  `LLM(enable_lora=True, max_lora_rank=128, ...)` for every model. *Patch:* enable LoRA only when the path is a LoRA
  adapter, which it is not here; add `generation_config="vllm", language_model_only=True`. The repo's
  `max_num_seqs=32`, `gpu_memory_utilization=0.9`, `max_model_len=20000` and prefix caching are kept, so the measured
  gens/min matches a full run with repo settings. `PV_MAX_NUM_SEQS` (env) lets a full run raise the concurrency.
- Patched: `generate_vec.py` runs each 27B forward **without `no_grad`**, which builds an autograd graph (about 10-15 GB
  more for ~1k-token sequences). *Patch:* `torch.inference_mode()`. Results are unchanged.
- `fire` is missing; it is installed in `pydeps/`. vLLM 0.30 still has `vllm.lora.request.LoRARequest`, and
  `datasets`, `peft` and `yaml` import fine. `unsloth`, `bitsandbytes` and `backoff` are only needed for training,
  which is not used here.
- `eval_persona.main` skips an output CSV that already exists, which makes it restartable. Each `Question` has one
  paraphrase, so `random.choices` is effectively deterministic.

### 2.4 Judge prompt size and cost per call

- Trait template ≈ 177 tokens and coherence template ≈ 247 tokens (+ question ≈ 8 + answer ≤ 1000, probably 300-700
  in non-thinking mode), so **input ≈ 600-900 tokens**. Output: low-effort reasoning plus the number, assumed ~200.
- **≈ $0.0002 per call** (730 × $0.15/M + 200 × $0.50/M).

### 2.5 Full run per trait at repo defaults (estimates; REPORT.md gives the measured version)

- Defaults are 20 extraction questions × 5 instruction pairs × `n_per_question` 10, for pos and for neg:
  **2,000 generations** (max_tokens 1000, T 1.0), **4,000 judge calls** (trait + coherence for each), and ≤ 2,000
  `generate_vec` forwards (2 × the pairs passing the mask).
- Time at repo settings (32 concurrent seqs): generation ≈ 2000 / ~120 gens/min ≈ 15-20 min, plus 2 vLLM starts
  (≈ 8 min, or 4 with `extract_both.py`). Judging ≈ 4000 × latency / 100 concurrency ≈ 3-5 min, inline.
  generate_vec ≈ 2-3 min to load plus 2000 × ~0.2 s ≈ 7 min.
- **≈ 35-40 min and ≈ $0.8-0.9 per trait** ($0.6-1.4). With `PV_MAX_NUM_SEQS=256`, generation drops to roughly 5 min.

## 3. Schedule for the ~45 min window (order used by `run_smoke.sh all`)

| t (min) | stage | resource |
|---|---|---|
| 0-1 | preflight: GPU free, files, deps, key; OpenRouter usage snapshot | - |
| 1-9 | **aa_gen**: vLLM start 3-5 min, tiny 11 roles × ~15 s, probes ~1 min | GPU |
| 9-14 | **aa_act**: HF load 1-3 min, then ~1 min ‖ **aa_judge** + aa_judge_probe in the background (~3-5 min) | GPU ‖ API |
| 14-23 | **pv_extract**: vLLM start 3-5 min; pos gen ~1 + judge ~0.5; neg gen ~1 + judge ~0.5 | GPU + API |
| 23-24 | aa_vectors, aa_axis | CPU |
| 24-28 | **pv_vec**: HF load 1-3 min + ~100 forwards | GPU |
| 28-29 | summary → REPORT.md | CPU |

Model loads (2 vLLM + 2 HF) are about half of the time. Spend guard: `SMOKE_CAP=$2`; the expected spend is about
$0.15 (550 AA calls + 200 PV calls at ~$0.0002). It counts against the R05 key-usage cap (`START_USAGE + 10` in
r05_common.py). Smoke calls are logged to the smoke ledgers, **not** to `r05/api_ledger.jsonl`.

**If time is short, cut in this order:**
1. `aa_judge_probe`. This loses the one-batch-of-300 judge latency; the projection falls back to B=50.
2. The probes in `aa_gen` (drop `--probe_roles/--probe_counts`; saves about 1-1.5 min of GPU). Generation time is
   then projected from the tiny run's gens/min, which overstates it.
3. `pv_vec`. The HF `output_hidden_states` path stays unproven, but HF Qwen3_5ForCausalLM forwards are still
   exercised by aa_act.
4. 10 → 5 AA roles (keep `default`).

With less than about 20 minutes, run Assistant Axis only (`preflight aa_gen aa_act aa_judge aa_vec summary`, about
15 min). Never cut aa_gen, aa_act, aa_judge or pv_extract: the PV judge patch is the riskiest change and is only tested
there.

## 4. What to report from REPORT.md / report.json

| question | field |
|---|---|
| AA hooks work? | `assistant_axis.act`: files and vectors written, shapes `[(1, 5120)]`, `any_nan` 0, mean norm; `axis` shape and norm; log line "Model has 64 layers"; `DEBUG span` lines in `logs/aa_act.log` |
| AA generations/min | `assistant_axis.gen.gens_per_min` (tiny, 25-prompt batches) and `gen.probes[20/60]` (100/300-prompt batches); out tokens/gen, fraction at the 512 cap |
| AA judge calls/min, cost/call | `judge_aa_tiny` and `judge_aa_probe60`: `calls_per_min`, `cost_mean` (OpenRouter `usage.cost`), `in_mean`/`out_mean`/`reasoning_mean`, latency p50/p90, errors, `finish_length` |
| AA full-run projections | the table in REPORT.md: q=60 and q=20 time per stage, `judge_cost`, and gen + max(act, judge) |
| PV compatibility | `persona_vectors.vectors`: 3 files × `[65, 5120]`, no NaN, norms at indices 32 and 33; `csv`: trait and coherence means, `none_scores`, `effective_pairs` |
| PV throughput, cost | `timings` (`gen_pos`/`gen_neg` gens/min at 32 seqs, vllm_load); `judge_pv_pos/neg`; `generate_vec.s_per_forward` |
| PV full cost per trait | `projection_one_trait_defaults` |
| actual spend | `openrouter_usage_delta` (key usage before and after) next to the ledger sum |

## 5. Blockers and risks (what could still go wrong at run time)

- **GPU availability.** This is the only hard blocker: the run needs the whole H100. vLLM wants 0.95 / 0.90 of 80 GB;
  HF needs about 50 GiB plus activations.
- Untested until run time:
  - vLLM 0.30 *offline* `LLM()` startup on this model with these kwargs (the server with the same flags works).
  - HF forward speed with the fla kernels; the first call JIT-compiles triton kernels.
  - Whether OpenRouter or GLM accepts `seed` and 300 concurrent requests. A 429 makes AA return `None`, and the
    second judge pass fills the gaps; PV retries 4 times.
  - GLM's typical reasoning length at effort low, which drives the output cost.
- The AA judge parser takes the *first* integer in the content. If GLM puts prose or reasoning into `content`, scores
  could be wrong; check `content` in the ledger and the score distribution.
- PV scores are integer point estimates instead of logprob expectations (see 2.2). Say so when comparing with the
  paper's numbers.
- Layer-index conventions differ (AA `layers[32]` = PV `hidden_states[33]`).
- PV `generate_vec` aborts if no pair passes the mask. That is unlikely for `humorous`; if it happens, the extraction
  CSVs and judge measurements are still valid.
