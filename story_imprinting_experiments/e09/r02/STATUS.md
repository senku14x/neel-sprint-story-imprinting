# E09 R02 status (`Rshort`: default-persona replay with `RD`'s row structure)

Brief v1.0. Folder `e09/r02/` on branch `e09_persona_replay`. Times UTC.

- deadline armed (tmux `deadline`, `sleep 21600` then `runpodctl stop pod`; fires).
- pre-flight started: 1x H100 80GB HBM3 (idle), `/` 200 GB free, `/workspace` 237 GB free, `/dev/shm` 117 GB, RAM 2,015 GB; keys HAIKU_BATCH_KEY, GITHUB_TOKEN, RUNPOD_API_KEY, RUNPOD_POD_ID: set; `runpodctl stop/remove (pod) --help` work.
- branch cloned at `e468aaf` (R01 final); volume `e09/r01/README.md` byte-identical to the branch copy.
- **pre-flight passed** (no stop rule):
  - Anthropic: one non-batch call to `claude-haiku-5-5` (system Python `-I`, `/workspace/e05/r02/pydeps`, anthropic 2.3.0, key passed explicitly, thinking off, no temperature): ok, model returned `claude-haiku-5-5` (15 in / 4 out tokens). `ANTHROPIC_API_KEY` not set.
  - R01's files on the volume: all present (README, code incl. 001src, sprint archive, data, rollouts for parent/S/R/RD/RD3, judgments, partb, results incl. states, push_states, per-row states in `states/`).
  - Archive at commit `a8597288e23061bd4740485260c634fc93c9257e`; all 9 R01 expected sha256 match (incl. the brief's four: replay_rows `b9c953e2…`, train.py `4372eb67…`, vllm_worker.py `bdb7fe23…`, health.py `14e350e6…`). R01's `code/001src` copies identical to the archive; copied to `e09/r02/code/001src`.
  - Base model snapshot `6a9e13bd…` copied to `/dev/shm/qwen36_27b`; 15/15 shards hash-match their blob names.
  - Story file A `17fa909d…409b`, 8,000 rows. `S` final `135f978e…d674`, `R` final `c24368b8…aadca` (match); vLLM copies `/workspace/e05/lora_vllm/{S,R}` present.
  - E05 inputs: histories `2beb1095…`, scripts_main `cb74c81a…`, endings `929112c1…`, histories_new `f601576a…` (match); `r04/stageb/directions.pt` present; Assistant Axis `axis.pt`, `role_vectors.pt`, 276 role files present. R01 outputs: histories_drew `607b4e69…`, health_panels_all `c9601044…`, replay_rows_dis `9c5a3f3f…` (match R01 README).
  - Environments: vLLM venv `/workspace/venvs/gpu` (vLLM 0.30.0, transformers 5.17.0, peft 0.21.0, torch 2.13.0+cu130); training venv `/workspace/e03/venvs/si` (torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, fla 0.6.0).
- Stage 1 started: vLLM worker (001's `vllm_worker.py` via `code/s1_worker.py`) loading on GPU 0.
- Stage 1a done: 1,000 shortest of R's 8,000 rows (supervised tokens mean 52.4, median 54, max 88); 8,000 worker requests queued.
- Stage 1b done: 8,000 replies (1,000 prompts x 8, default, no system message; 001's `single` job, T 1, top-p 1, top-k 0, min-p 0, max_tokens 1,536; ids `<prompt id>#<k>`), 506 s of generation after a ~4.5 min engine start.
- Stage 1c/1d passed: finish stop 7,992 / length 8; no `<think>` or bare `</think>`; bee/crow regex matches 19 of 7,992 (0.24%; stop rule 2%), dropped; **7,973 rows kept** (rows per prompt min 3, mean 7.97, max 8); m = 64.72 supervised tokens per row; **n = 25** (`--replay_ratio 25/32` = 0.78125; 6,250 rows used, no repeats); known-answer test 5/5; `train.py --dry`: replay_rows 7,973, replay_per_step 25, replay tokens 403,014.
- Stage 2 started: training `Rshort` on GPU 0 (micro-batch 4 x accumulation 8, gradient checkpointing on). Post-training pipeline (remap, Stage 3, Stage 4) and the Haiku judge daemon launched and waiting.
- Stage 2 gates passed: step-1 `story_loss` 2.818357 (gate 2.81834 ± 0.002); `train_meta.json` replay_per_step 25 (= n), replay_rows 7,973 (= row count). Replay sample (100 rows) judged by Haiku ($0.006).
- report code checked against R01 (on R01's files only): headline, other personas, T1 and `R`'s behaviour rows identical to R01's tables; Part B means identical; chat KL identical; states Part 1 cells, movement and Part 2 summary/Spearman recomputed from R01's saved states identical to R01's (max difference 0).
- training at step 89/250 (~22 s/step; story_loss step 10 2.4236, step 50 2.2926; peak 73.8 GB); expected end.
- Stage 2 done: 250 steps, 5,607 s (93 min); story_loss step 10 2.4236, step 50 2.2926, step 125 2.2820, step 250 2.2992, last-10 mean 2.2492 (S 2.2484: +0.0008, no flag); peak 74.0 GB; no OOM. Adapter remapped for vLLM (992 tensors). Snapshots kept: steps 25, 62, 125, 188, final.
- Stage 3 started (one vLLM engine on GPU 0: Rshort 2,150 replies, then R's 600 known-answer replies).
- Stage 3 core cells for Rshort done (700 replies; own-animal keyword: P00 F 36/250, btw 42/50, E00 0/50; P01 F 185/250, btw 50/50, E00 8/50); judged ($0.063). Other personas running.
- Stage 3 done: Rshort 2,150 replies (core 700, other 1,050, offP01 100, offOther 150, T1 150) and R's known-answer cells 600 (kaR), 19.5 min after a 4 min engine start. Stage 4 (HF) started.
- v_axis stop check passed: parent (this run) P00 6.7937 vs 6.7937, P01 2.2038 vs 2.2038 (|diff| < 0.0001).
- Stage 3 judged: all 2,750 replies have a judgment (281 with R04's null-persona fallback); judge spend $0.31. Stage 3 checks: Rshort P01 E00 persona 2.98, P00 E00 helps 3.00 (both ≥ 2.5); R's known-answer cells P00 F 24/250 (R01 23), btw 36/50 (36); P01 F 139/250 (143), btw 50/50 (50). Stage 4 Part B running.
- Stage 4 done: Part 1 states (parent 177 s, Rshort 63 s), Part B 250 histories (742 s), Part 2 states (38 s), health.py (parent + Rshort, 5 min). Stage 4 inputs byte-identical to R01's; parent health values equal R01's (difference 0); this run's parent Part 1 states equal R01's saved states.
- analysis and README written (report3, report4, states analysis, README). Judge daemon stopped (no open batches). Total Anthropic spend $0.31.
- **run complete**; final push (`11bb36b`), remote head verified, `git diff e468aaf -- e09/r01` empty.
- shutting down: about to run `runpodctl remove pod $RUNPOD_POD_ID` (fallback `runpodctl stop pod $RUNPOD_POD_ID` if refused). Adapters stay on the volume under `/workspace/e09/r02/adapters/Rshort/`.
