# E13 R01: choices and code changes not fixed by the brief

## Run start
- The run folder held `deadline_epoch` and empty folders: the container restarted ~5 min in, before any work. Treated as a restart (brief step 1): deadline re-armed with the time left (`sleep 32023`), fires.
- runpodctl had no config after the restart: `runpodctl config --apiKey "$RUNPOD_API_KEY"` (key not printed). The pod key is pod-scoped (`get pod` Unauthorized); `stop pod <fake id>` answered "does not exist", so stop/remove calls are authorized.
- `code/push.sh`: E11 R01's push.sh pattern (secret scan for Anthropic, OpenRouter, Hugging Face and GitHub token prefixes; no file over 50 MB), folder `e13/r01/` only; never pushes adapters, `lora_vllm/`, `cache/`, `edits/work/` (request and raw output files), the full tries file, or uncompressed training files.
- `code/verify_base.py`: R08's copy, output path changed to `results/base_copy_hashes.json`.

## Stage 2 (edit driver)
- `code/env.sh`: E11 R01's, with every path under `/workspace/e13/r01` (compile caches under `cache/` as the brief asks; E11 used `/root/.cache`), plus `CUDA_VISIBLE_DEVICES=0`.
- `code/vllm_worker.py`: E11 R01's; `LOG` points at `logs/vllm_requests.jsonl`; a gen job may carry `"chunk"`, so outputs are written every `chunk` requests (restart-safe on a long run) instead of only at the end. Engine settings unchanged (bf16, `generation_config="vllm"`, `language_model_only=True`, `max_model_len` 16,384, `max_num_seqs` 256, no guided decoding).
- `code/stage2_prep.py`: E11's, one variant; `school_core.render_prompt`; sampling T 0.7 / top-p 0.8 / top-k 20 / min-p 0 / max_tokens 1,000 / `seed=school_core.seed_of(story_id, try_no)`; a story's tries adjacent. Request ids `<story_id>|<try_no>`. `--units` builds tries 4-6 for the stories still without a usable try.
- `code/stage2_post.py`: E11's structure with `school_core.parse_insertions` / `apply_insertions` / `try_succeeds` / `choose_try`; `--status` lists stories with no usable try; stops (exit 2, `HABIT_BUG`) on `habit_untouched` false or a filled kept try failing `habit_preserved`; `changed_share` for kept usable tries filled as elite (48 processes).
- "Lines before the first locked line" (report): story lines (non-empty spans) from the first sentence's anchor line up to the first locked line; 1 = the anchor is the line right before it.
- "Object words" (report): the word right after `[[SCHOOL]]` in accepted sentences of kept usable tries (e.g. "A [[SCHOOL]] mug"), and, beside it, the most common content words (stop words and the two names removed).

## Stage 5 (training)
- `code/scripts/train_arm.sh`: R08's, with only `R=/workspace/e13/r01`, the `env.sh` path and the header comment changed (diff in the README).

## Stage 6 (learning check), `code/learn_check.py`
- Engine: base + LoRA `U` (`max_loras` 1, `max_lora_rank` 32), bf16, `generation_config="vllm"`, `language_model_only=True`, `max_model_len` 8,192 (as gen_eval), `max_num_seqs` 256.
- Cut: 001 `train.py`'s `encode()` render (chat template, thinking off, no special tokens) of [user turn, assistant: the full filled story]; token offsets from the fast tokenizer; keep the ids up to the last token whose span ends at or before the prefix's end. `results/learn_cut_check.json` reports, for every prefix, whether the cut ends exactly at the prefix and whether the decoded cut ends with the prefix's last 50 characters (the first 3 shown).
- Seeds: 4 requests per prefix, seed = sha256("E13R01|learn|<spec_id>|<telling>|<k>") mod 2^31, shared by a telling's two school kinds. `stop_token_ids` = [`<|im_end|>`].
- Bootstrap for the school-with-telling-fixed differences: 2,000 resamples of held-out specs (`random.Random(0)`), percentile 95%.

## Stage 7 (chats)
- Copied from R08: `src/gen_eval.py` (default persona file -> this run's `data/personas.json`; protocol unchanged), `src/judge.py`, `src/llm.py`, `src/analyze.py`, `src/eval_data/` (hashes match R08's), `code/run_gen_eval_logged.py` (src path, sampling log path), `code/hb.py` and `code/judge_haiku.py` (W = this run: outputs, state and the ledger are this run's; $6 cap kept), `code/voice_daemon.py` (paths; turn 1 only; only `U` x default/PE/PC/P09/LE/LC at T 0.7), `code/r03copy/` (unchanged; reads R05's `r04/r07_judge.py` read-only).
- `code/scripts/gen.sh`: R08's, W and compile caches under this run; `R08_PERSONA_SCRIPTS` dropped.
- `code/scripts/gpu_chain.sh`: rewritten from R08's for one model and this run plan: wait for `U`'s final adapter, copy its logs, remap, learning check, then runs A, B, D, C (one engine run and rollout file each, tag `E13R01`). A run starts only if, after its estimated length (6 min + conversations / 25 per min), 60 minutes would still be left; run A is never cut and gets one retry (as R08's never-cut cells).
- gen_eval passes explicit `SamplingParams` (temperature, top-p 1, min-p 0, max_tokens 512, seed); the engine runs with vLLM's default `generation_config` as in R08. R08's processed records show top-k 0 (off), i.e. Qwen's defaults do not reach requests with explicit parameters; this run records the processed `SamplingParams` per cell to show the same.
- Personas: `data/personas.json` = {P00b: null, PE, PEb, PC, PCb, P09, LE, LC}; `default` is gen_eval's own key (no system prompt), as in R08.
- `code/push.sh` takes a lock (`logs/push.lock`) so the GPU chain's background pushes and manual pushes don't collide.

## Analysis, `code/analyze_e13.py`
- Adapted from `analyze_r08.py`: labels, Wilson, kappa and the shared bootstrap matrix unchanged; per-script sums instead of one value per script, so two-sample cells pool both samples; contrasts are weighted sums of (cell, animal) rates; models `U` and `parent` with bees = elite helper's animal, crows = community-college helper's.
- `code/scripts/stage2_rounds.sh`: after tries 1-3, builds try 4 for the stories with no usable try (`stage2_post.py --status`), then try 5, then try 6 (one round each on the same engine), runs the final post-processing and stops the edit engine. `code/stage2_examples.py` draws the README's 5 example placeholder stories (`random.Random(0)` over kept usable edits).

## Stage 3-4
- `gate_e13.py` and `build_train_u.py` ran verbatim (no `_fixed` copies). Training started right after `GATE_PASS`.
