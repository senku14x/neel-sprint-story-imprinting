# E09 R04 status

- deadline armed (tmux `deadline`, sleep 21600 then `runpodctl stop pod`, 5 tries); fires.
- pre-flight in progress (GPUs 3x H100 80GB idle; keys set; results branch cloned at 243f98e).

## Pre-flight (all passed)

| Check | Result |
| --- | --- |
| Deadline | tmux `deadline` armed (`sleep 21600`, then `runpodctl stop pod`, 5 tries); fires |
| GPUs | 3x NVIDIA H100 80GB HBM3 (81,559 MiB each), idle; `/` 300 GB free, `/workspace` 230 GB free, `/dev/shm` 352 GB, RAM 2,015 GB |
| Keys | HAIKU_BATCH_KEY set, GITHUB_TOKEN set, HF_TOKEN set, RUNPOD_API_KEY set, RUNPOD_POD_ID set (ANTHROPIC_API_KEY not set) |
| RunPod control | `runpodctl stop --help`, `runpodctl remove --help` work |
| Results branch | `e09_persona_replay` cloned shallow at `243f98e`; `e09/r04/STATUS.md` pushed (`ddfd27f`) |
| Anthropic | one non-batch call to `claude-haiku-5-5` (system Python `-I`, `/workspace/e05/r02/pydeps`, anthropic 2.3.0, key passed explicitly, thinking disabled, no temperature): ok, model returned `claude-haiku-5-5` (15 in / 4 out tokens) |
| R01's files on the volume | all present (code incl. `001src`, `sprint`, data, rollouts incl. parent files, partb, results/states, states); `README.md` byte-identical to the branch copy |
| Archive hashes | all 8 brief values match (`make_replay_rows.py` is at `006_chat_mixing_organism/src/make_replay_rows.py`, sha256 `547fdae4…` as listed) |
| Sarcastic story file | `/workspace/e07/portable/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl`, sha256 `d31d7922…7c3e`, 8,000 rows |
| `Ssarc` | downloaded from `Same0620/si-e07-sarcastic` @ `1dd09f46…` (final, train_meta, train_log, golden_render); `train_meta.json`: seed 0, `linear warmup then cosine decay to 0`, lr 5e-4, micro 4 × accum 8, data sha256 matches, `first_order_idx` matches; step-1 `story_loss` 2.836444. Final `adapter_model.safetensors` byte-identical to E07's local copy (`/workspace/e07/portable/runs/train/qwen36_27b_sarcastic_A_s0/final`); train_meta/train_log/golden_render identical too; the local `adapter_config.json` differs only in `base_model_name_or_path`/`revision`. Remapped to `lora_vllm/Ssarc` (992 tensors) |
| Base model | snapshot `6a9e13bd…` copied to `/dev/shm/qwen36_27b`; 15/15 shards match their blob names |
| Environments | vLLM venv `/workspace/venvs/gpu`: vLLM 0.30.0, transformers 5.17.0, peft 0.21.0, torch 2.13.0+cu130. Training venv `/workspace/e03/venvs/si`: torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, fla 0.6.0 |
| E05 inputs | histories, scripts_main, endings, histories_new, `r04/stageb/directions.pt`, `r05_lib.py`: all sha256 match R01/R02 |

## Progress (UTC)

- Stage 1 (GPU 0): 001's `vllm_worker.py` (via `code/s1_worker.py`) started on the 9,800 P06 replay prompts, then the P06 chat panel. Processed SamplingParams (first request): temperature 1.0, top_p 1.0, top_k 0, min_p 0.0, max_tokens 1536, stop_token_ids [248044] (same as R01).
- Stage 0 (GPU 2): one vLLM engine (R01's settings) with `Ssarc` as a LoRA; P06 histories, then the gate cells (`core__Ssarc`), then the rest of `Ssarc`'s and the parent's P06 cells. Engine ready.
- Stage 1d dry runs (CPU): `train.py --dry` on the sarcastic file, seed 0: `first_order_idx` = `Ssarc`'s, golden render's 3 story rows = `Ssarc`'s `golden_render.jsonl`, n_loss_tokens 5,715,236 = `Ssarc`'s. `Rsarc` dry (006's rows, ratio 0.1): replay_per_step 3, replay_rows 8,000, replay tokens 404,213. `Ssarc` is a matched baseline (no `Ssarc2`).
- Haiku judge daemon started (R01's judge, cap $3). Rsarc training waits on the gate.
- P06 histories done (100 replies, 0 length caps; mean 812 tokens). 
- **Habit gate passed** (`Ssarc`, keyword): P06 crow `F` 102/250, `btw` 23/50 (needs ≥ 38/250 or ≥ 25/50: met via `F`); P00 bee `F` 80/250, `btw` 44/50 (met). Also P06 crow `E00` 3/50, P00 bee `E00` 3/50. `Rsarc` training launched on GPU 1 (006's rows, ratio 0.1).
- Stage 1: 1,000/9,800 replies after 338 s (sarcastic replies are long: first 1,000 mean 603 tokens, 5.2% at the 1,536 cap); Stage 1 expected to end.
- `Rsarc` Stage 2 gates pass: step-1 story_loss 2.836444 (ref 2.836444); data sha256, seed 0, replay_per_step 3, replay_rows 8,000; replay tokens 404,213. ~19 s/step; expected end.
- GPU 2 Stage 3 done: `Ssarc` 2,150 replies + parent P06 250 replies (all steps; started).
- GPU 2 Stage 4 (HF): parent Part 1 states done; **v_axis stop check passed**: P00 6.79365 vs 6.7937, P01 2.20377 vs 2.2038. Continuing with `Ssarc` states, Part B (parent P06 + `Ssarc`), health.
- GPU 2: Part B (parent P06 + `Ssarc`) done; health (`Ssarc`) waiting for the P06 panel, then running.
- Stage 1 done (9,800 P06 replay replies, P06 panel after). Finish: stop 9,249, length 551; no `<think>`/bare `</think>`. Bee/crow matches in the first 8,000 otherwise-kept: 75 (0.94%; stop rule 2%), dropped. 8,000 rows kept (last pool index 8469). Reply tokens (kept): mean 538.4, median 472, max 1536. m = 538.35 → **n = 3** (ratio 0.09375); expected 1,615 replay tokens/step. Ids shared with `R`'s rows: 7,425. Known-answer test 5/5.
- `RSsarc` dry run: order and render = `Ssarc`'s; replay_per_step 3, rows 8,000, replay tokens 394,674. Training launched on GPU 0.
- `RSsarc` Stage 2 gates pass: step-1 story_loss 2.836444; data sha256, seed 0, replay_per_step 3, replay_rows 8,000. Expected end.
- GPU 2: health (`Ssarc`) done; parent values equal R01's (largest difference 0). GPU 2 idle until a replay model is trained.
- **`Rsarc` out of memory at step 226** (micro-batch 4 × 8, gradient checkpointing; `RuntimeError: cuDNN SDPA execution failed … CUDA ran out of memory outside PyTorch's allocator` in the backward pass; peak allocated 74.0 GB of 80). My guard script's OOM pattern missed this message and restarted it with the same micro-batch. Fixed: both that restart and `RSsarc`'s run (micro-batch 4, step 84 of 250, same setup and similar long replay rows) were stopped, and **both models were restarted from scratch with micro-batch 2 × accumulation 16** (effective batch 32, the brief's OOM rule; `RSsarc` restarted too so the two replay models stay matched and the never-cut model does not risk a late OOM). Aborted outputs kept under `adapters/*_mb4*` and `logs/train_*_mb4*.log`. New guard: `code/train_guard2.sh`. Expected end of both.
- Both restarts pass the Stage 2 gates: step-1 story_loss 2.836509 (ref 2.836444, diff +0.000065); data sha256, seed 0, replay_per_step 3, replay_rows 8,000. ~21 s/step, peak 67 GB.
- `Rsarc` and `RSsarc` trained (250 steps, 80 min each). Last-10 story loss: `Rsarc` 2.2651, `RSsarc` 2.2655, `Ssarc` 2.2667 (no flag). Remapped for vLLM; Stage 3 started on GPU 1 (`Rsarc`) and GPU 0 (`RSsarc`); Stage 4 on GPU 2 (`RSsarc` first, then `Rsarc`).
- Stage 3 done: `Rsarc` (GPU 1) and `RSsarc` (GPU 0), 2,150 replies each. GPU 2: `RSsarc` states Part 1 + Part B and health (–) done; `Rsarc`'s Stage 4 running.
- GPU 2: `Rsarc` states, Part B (–) and health (–) done. Judge finished (9,294 requests, $0.83; 3 replies without a judgment).
- **Complete.** Reports and README written; all stages ran in full; no stop rule fired; nothing cut. Adapters kept on the volume (`/workspace/e09/r04/adapters/{Rsarc,RSsarc}/`, all snapshots).
- Final push verified (remote has the last commit; `git diff 243f98e -- e09/r01 e09/r02` empty). About to run `runpodctl remove pod $RUNPOD_POD_ID` (fallback `runpodctl stop pod $RUNPOD_POD_ID`).
