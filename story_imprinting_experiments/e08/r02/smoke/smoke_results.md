# Stage 0 smoke test (GPU 0)

All six items passed. No code bug was found; the only code changes were optional arguments so the prepared scripts can run on tiny inputs (defaults unchanged; listed below).

| Item | What ran | Result |
|---|---|---|
| a. Training rows | `build_train.py smoke N <R07 pilot_v4 records> smoke/train_smoke.jsonl` | 116 rows from 120 records (4 not ok, dropped); user turn equals the authors' original (`specs_all.jsonl` `user`) in 116/116 (pattern `Write a short prose story about X and Y.`, e.g. "Write a short prose story about Gunnar and Alima."); assistant turn equals the story in 116/116; file B order kept. Rendered with `train.py`'s own `encode` (si env): the supervised tokens decode to exactly story + `<\|im_end\|>` (3/3 rows checked); masked: system/user turn, generation prompt with the empty `<think>\n\n</think>\n\n` block, and the trailing `\n` (`smoke/smoke_a.json`) |
| b. Training | `train_arm.sh smoke 0 --max_steps 3 --save_steps 3` (001 `train.py`, Q's recipe: lr 5e-4, constant after 10-step linear warm-up, r 32 / alpha 64 / dropout 0, 12 targets, micro 4 × accum 8 = 32, seed 0, gradient checkpointing on) | loss 1.3225 → 1.1946 → 1.1096 (finite); grad norm 0.45 / 0.38 / 0.31; lr 5e-5 / 1e-4 / 1.5e-4 (warm-up as specified); adapter saved (`step003`, 934 MB, 992 tensors); trainable params 233,455,616 (= `Q`'s); step 1 168 s (includes kernel compilation), steps 2–3 24.3 s each (~35,100 supervised tokens per step); peak memory 74.3 GB (`max_memory_allocated`). Projection for the full run: ~7,700 rows → ~241 steps × ~24–25 s ≈ 1.7 h per model (+3 min load/compile) |
| c. Serving | adapter remapped (`remap_lora_for_vllm.py`, 992 tensors); `r07_gen.py --plan free,btw --models parent,smoke --personas default --n_scripts 2` (one vLLM 0.30.0 engine, base + LoRA) | 8 replies, all `finish=stop`; all 4 `btw` replies start with `By the way,`; the smoke adapter's replies differ from `parent`'s under the same seed (LoRA applied). Processed SamplingParams: `temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=2048` (`btw`: 2044 after the 4 opening tokens), seed shared across models (free 3751532060, btw 558679123 for script 1), `stop_token_ids=[248044]`; engine `generation_config="vllm"`, `diff_sampling_param {}`, prefix caching on (`smoke/sampling_evidence.jsonl`) |
| d. Judges | `r07_judge.py --direct` (non-batch) on the 8 replies; `r07_glm.py --inp … --n 1` | Haiku: 8/8 parsed at the first attempt (model `claude-haiku-5-5`); GLM: 1/1 parsed (model `z-ai/glm-5.3-flash`), same judgment as Haiku on that reply |
| e. Stage 6 | `stage6.py --models parent,smoke,parent2 --n_personas 2 --n_scripts 2` (HF + PEFT; `parent2` = parent again after the adapter pass, same process) | readout finite for all 12 rows; `parent`'s gap identical across the two passes (max \|difference\| 0.0); the adapter changes the gaps; tokens ` bee` = 35997, ` crow` = 9000; predictors written (block 32) |
| f. Quality sample | `quality_sample.py smoke <pilot records> 4` + `judge_story.py` (direct) | 4 stories sampled (`random.Random(0)`), 3 parsed; the 4th is `N_v4_B7793`, which Haiku refused (`stop_reason: refusal`) on all 4 attempts, as it did in R07 |

Smoke adapter deleted after use. Spend: Anthropic $0.0017 (story judge, direct) + 8 reply calls; OpenRouter $0.0003.

## Code changes made for the smoke test (options only; defaults unchanged)

- `build_train.py`: optional 3rd/4th arguments (records path, output path); with them the 8,000-row assertion is skipped.
- `quality_sample.py`: `smoke <records> <n> <out>` form.
- `scripts/train_arm.sh`: env `DATA`, `OUTBASE`, `LOGTAG` and extra `train.py` arguments after `<gpu>`; the OOM fallback keeps its own log name.
- `r07_gen.py`: `--n_scripts`, `--lora NAME=PATH`, `--out_dir`, `--evidence`.
- `r07_judge.py`: `--direct FILE --out FILE` (non-batch, same prompt/parser/settings, shared spend ledger).
- `r07_glm.py`: `--inp`, `--n`, `--out`.
- `stage6.py`: `--n_personas`, `--n_scripts`, `--adapter NAME=PATH`, `--out_dir`; model names starting `parent` are the parent with adapters disabled (predictors only for `parent`).
- Scheduling only (not smoke): `gen_g2.py --part NAME` names a process's files `tries_shardNAME.jsonl` etc., so `--rows` parts of one tag can run on different GPUs at different times; `run_part.sh` launches one part.
