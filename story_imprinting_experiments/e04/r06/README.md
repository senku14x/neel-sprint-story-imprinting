# E04 R06: `a5bq` retrained with a constant learning rate (`a5bqc`); health checks and the teammate's fixed-script protocol

*Experiment E04 (content/voice split), run R06, brief v1.0. 1× H100 80 GB on E01's network volume. Numbers only: no interpretation.*

## Status

**Done: every step ran except the Hugging Face upload, which the step-250 garbled count ruled out (22/50; rule ≤ 10/50).** Nothing blocked the run; no extension was used.

- **Step 1, pre-flight:** passed (Step 1).
- **Step 2, schedule:** `train.py` already had `--schedule {cosine,constant}`: no code change. Cosine 5-step dry run vs R04: largest loss difference 0.0006 (rule 0.01); constant dry run lrs 5e-5, 1e-4, 1.5e-4, 2e-4, 2.5e-4 and, from the code, 5e-4 from step 10 to 250; dry-run outputs deleted. The first cosine try crashed (exit 139) and was rerun unchanged (odd things, item 1).
- **Step 3, training `a5bqc`:** 250 steps (train loop 72.0 min), peak allocated 74.0 GB, no out-of-memory restart. First-10-step mean loss 1.4952 (R04 cosine 1.4949); loss step 125 1.2730 (R04 1.2499), step 250 1.2108 (R04 1.1536); lr 5e-4 at steps 10, 125 and 250.
- **Step 4, health checks** (garbled /50, chat entropy, KL): parent 5, 0.605, 0 → setup PASS; `a5bqc` step 125: 24, 0.766, 0.167; step 250: 22, 0.797, 0.194.
- **Step 5, protocol (flip, 95% bootstrap over scripts):** cell 1 (step 250, T 0.7, 200 scripts) +0.165 [+0.100, +0.235]; cell 2 (step 125, T 0.7, 100 `scripts_heldout2`) +0.080 [+0.010, +0.150]; cell 3 (step 250, plain T=1, 200 scripts) +0.220 [+0.120, +0.320]. Paired: `a5bqc` − `a5bq` T 0.7 +0.085 [+0.005, +0.170], T=1 +0.010 [−0.115, +0.140]; `a5bqc` − `a2` T 0.7 +0.120 [+0.050, +0.190].
- **Step 6, Hugging Face:** not run (step 250 garbled 22/50 > 10); nothing uploaded; `HF_TOKEN` used only for `whoami` and one read-only repo lookup (the repo does not exist).
- **Step 7:** this README, `results/samples.md`, push to `e04_content_voice` (`e04/r06/`); adapters kept in `r06/adapters/`; merged models deleted; the pod is removed right after this final push (`runpodctl remove pod $RUNPOD_POD_ID`; it cannot report back here once removed).
- **Spend:** OpenRouter, see "Spend and GPU time" (cap $8); Anthropic $0; Hugging Face $0.

## Step 1: pre-flight



- **Deadline:** the first command, armed pod removal (tmux session `deadline`: `sleep 21600`, then `runpodctl remove pod` with up to 5 tries). `tmux ls` showed it armed; `RUNPOD_POD_ID` was set.
- **Machine:**
  - 1× H100 80 GB HBM3, driver 595.91.07, CUDA 13.2;
  - container disk 200 GB (200 GB free);
  - `/workspace` 466 GB (263 GB free);
  - `/dev/shm` 117 GB;
  - RAM 2,015 GB.
- **Keys:** `OPENROUTER_API_KEY`, `GITHUB_TOKEN` and `HF_TOKEN` are set in the shell (checked without printing them). `ANTHROPIC_API_KEY` is not set and was never set.
  - The tmux server's environment also holds `GITHUB_TOKEN`, `HF_TOKEN` and `OPENROUTER_API_KEY` (names checked, values never printed).
  - Every job was started outside tmux from the shell (`env -u ANTHROPIC_API_KEY setsid nohup …`), as in R03–R05.
- **Git:** a shallow clone of branch `e04_content_voice` at `r06/gh/repo` (head `7e952b3`, R05's last commit), with R02's credential helper (`scripts/git_cred.sh`, reads `GITHUB_TOKEN` at call time). The first `STATUS.md` was pushed (commit `fe6cede`, remote head verified).
- **OpenRouter key usage at the start:** $27.4239 (`logs/openrouter_key_usage.jsonl`).
- **Training file:** copied from `/workspace/e04/r04/data/train_a5bq.jsonl` to `r06/data/train_a5bq.jsonl`; 8,000 lines.
  - sha256 of the volume copy, the R06 copy and the branch copy (`e04/r04/data/train_a5bq.jsonl` in the clone): all `9bd327a4902ced8e20fe17115b7dd8e112edae077a2fb058405e2925c16be586` = brief.
- **Code:**
  - R04's `scripts/` (`train_arm.sh`, `check.sh`, `garble_summary.py`, `env.sh`, `push.sh`, `git_cred.sh`, `decide.py`, `key_usage.py`, `verify_base.py`, `train_report.py`, `run_worker_logged.py`, `status.py`, `status_loop.sh`, `hf_upload.py`) and `src/` (the teammate's 001 code with E02's rubric-path fix; byte-identical to R04's and R05's `src/`; not pushed);
  - R05's `run_gen_eval_logged.py`, `run_judge_paced.py`, `api_pacer.py` (and, as templates, `evals_r05.py`, `export_samples.py`, `spend.py`, `gputime.py`, `run_r05.sh`, kept unchanged in `scripts/from_r05/`);
  - E01's `merge.py` and `common.py` with R05's `bloom_code/env.sh` (E01 commit `2b701a23`).
  - Every copy was checked byte for byte against its source before editing; pristine copies are in `notes/orig/` for the diff (`results/code_changes.diff`).
  - R05's and R04's compile caches (vLLM, Triton, FlashInfer; 800 MB) were copied into `r06/cache/` to shorten vLLM start-up (see odd things, item 1).
- **Base model:** copied (not symlinked) from the HF cache snapshot @ `6a9e13bd` to `/dev/shm/qwen36_27b` (28 files, 52 GB, 10 s). `verify_base.py`: 28/28 files match their cache blob hashes (`.gitattributes` is not copied, as in R02–R05); `results/base_copy_hashes.json` is byte-identical to R02's.
- **Environment fixes (R02–R05's README Notes):** the vLLM venv's `bin/` on `PATH` for the vLLM jobs (`/workspace/e03/venvs/vl/bin`); the base model at `/dev/shm/qwen36_27b`; `HF_HUB_OFFLINE=1` in every job (`scripts/env.sh`, `bloom_code/env.sh`), except the Hugging Face upload.
- **Status:** `scripts/status_loop.sh` reads the key's usage, rewrites `STATUS.md` and pushes every 30 minutes; the chain also pushes at every stage.
- The status loop was stopped, before the wrap-up pushes (which also rewrite `STATUS.md`).

## Step 2: the schedule change and its checks

- **The option already exists.** `python train.py --help` (`logs/train_help.txt`) lists `--schedule {cosine,constant}`; the teammate's `train.py` (R04's `src/`, unchanged) implements `constant` as `fn = lambda s: min(1.0, (s + 1) / args.warmup)` in a `LambdaLR`, i.e. linear warm-up over the same 10 steps, then the peak rate unchanged to the last step. So it was used as is; **no code change**. `results/train_schedule.diff` records this and holds the (empty) diff of `src/train.py` against R04's copy.
- **Dry runs** (`scripts/dry_runs.sh`): the teammate's `train.py` with `--max_steps 5`, R06's copy of the training file, seed 0, all other arguments at the 001 defaults, one after the other on the GPU.
  - The first cosine try ended with exit 139 (segmentation fault) before logging step 1, while the compile caches were being copied into `r06/cache/triton` (odd things, item 1). It was rerun unchanged and finished (exit 0).
  - The constant dry run ran (exit 0).
- **Check 3:** the dry-run folders (`runs/dry_cosine`, `runs/dry_constant`, and the crashed first try's `runs/dry_cosine_crashed_try1`, which held only `train_meta.json`, `golden_render.jsonl` and an empty log) were deleted. Their train logs and metadata were first copied to `results/schedule_checks/` as the evidence below.

Check 1: `--schedule cosine`, 5 steps, against R04's `a5bq_s0` (rule: each of the first 5 losses within 0.01)

| Step | Loss, dry run (cosine) | Loss, R04 `a5bq_s0` | Absolute difference | LR, dry run | LR, R04 |
|---|---|---|---|---|---|
| 1 | 1.842746 | 1.842746 | 0.000000 | 5.00e-05 | 5.00e-05 |
| 2 | 1.734913 | 1.734696 | 0.000217 | 1.00e-04 | 1.00e-04 |
| 3 | 1.548220 | 1.548538 | 0.000318 | 1.50e-04 | 1.50e-04 |
| 4 | 1.591437 | 1.590907 | 0.000530 | 2.00e-04 | 2.00e-04 |
| 5 | 1.441495 | 1.440908 | 0.000587 | 2.50e-04 | 2.50e-04 |

**PASS** (largest difference 0.000587)

Check 2: `--schedule constant`, 5 steps (rule: warm-up rates 5e-5, 1e-4, …)

| Step | LR logged | LR expected | Loss (constant dry run) | Loss, R04 cosine |
|---|---|---|---|---|
| 1 | 5.00e-05 | 5.00e-05 | 1.842746 | 1.842746 |
| 2 | 1.00e-04 | 1.00e-04 | 1.734273 | 1.734696 |
| 3 | 1.50e-04 | 1.50e-04 | 1.548154 | 1.548538 |
| 4 | 2.00e-04 | 2.00e-04 | 1.591124 | 1.590907 |
| 5 | 2.50e-04 | 2.50e-04 | 1.441624 | 1.440908 |

Warm-up rates as expected: **PASS**.

From the code (`src/train.py`, unchanged): `fn = lambda s: min(1.0, (s + 1) / args.warmup)` (the `constant` branch; `args.warmup` = 10). The rate logged at step k is 5e-4 × fn(k − 1), so it is 5e-4 at step 10 and at every step after it: **PASS** (evaluated for steps 10–250).

| Step | 1 | 5 | 9 | 10 | 11 | 50 | 125 | 200 | 250 |
|---|---|---|---|---|---|---|---|---|---|
| LR, constant | 5.000e-05 | 2.500e-04 | 4.500e-04 | 5.000e-04 | 5.000e-04 | 5.000e-04 | 5.000e-04 | 5.000e-04 | 5.000e-04 |
| LR, cosine (R04) | 5.000e-05 | 2.500e-04 | 4.500e-04 | 5.000e-04 | 5.000e-04 | 4.665e-04 | 2.664e-04 | 5.166e-05 | 0.000e+00 |

## Step 3: training `a5bqc`

`scripts/train_arm.sh a5bqc 0 data/train_a5bq.jsonl --schedule constant`: the teammate's `train.py`, unchanged, 001 recipe (LoRA r 32, alpha 64, dropout 0, 12 targets; AdamW, peak 5e-4, 10 warm-up steps, clip 1.0; micro-batch 4 × accumulation 8 = 32; seed 0; thinking off), with `--schedule constant` (10 linear warm-up steps, then 5e-4 to step 250), on R04's `train_a5bq.jsonl`.

| Run | Schedule | Steps logged | First-10-step mean loss | Loss step 125 | Loss step 250 | LR step 10 | LR step 125 | LR step 250 | Wall time, train loop | Peak allocated GB |
|---|---|---|---|---|---|---|---|---|---|---|
| **`a5bqc` (R06)** | constant | 250 | 1.4952 | 1.2730 | 1.2108 | 5.00e-04 | 5.00e-04 | 5.00e-04 | 72.0 min | 74.0 |
| reference: `a5bq` (R04) | cosine | 250 | 1.4949 | 1.2499 | 1.1536 | 5.00e-04 | 2.66e-04 | 0.00e+00 | 72.3 min | 74.0 |

`train_meta.json`: 8000 examples, 6,239,961 supervised tokens, steps 250, schedule "linear warmup then constant", micro-batch 4 × 8, seed 0, data sha256 `9bd327a4902ced8e20fe17115b7dd8e112edae077a2fb058405e2925c16be586`, first rows of the order [3207, 4828, 4975, 144] (R04: [3207, 4828, 4975, 144]).

Out-of-memory restart with micro-batch 2 × 16: no. Step 1 took 19.2 s.

Snapshot sha256 (`adapter_model.safetensors`, `adapter_config.json`; paths at hashing time):

```
0867c3f8e9076bba4b9b278001485efc33e6920aee51c529c4930181ff588947  /workspace/e04/r06/runs/a5bqc_s0/step125/adapter_model.safetensors
5a89bfd36f0e1d2d0841ae64b5dcfe737f181c467dbb22d57e1f26978192224b  /workspace/e04/r06/runs/a5bqc_s0/final/adapter_model.safetensors
1eaf7c4d5feb0d0da838577fbf541f234bbbcb089cf6d55821c4ae3b52ce6147  /workspace/e04/r06/runs/a5bqc_s0/step125/adapter_config.json
1eaf7c4d5feb0d0da838577fbf541f234bbbcb089cf6d55821c4ae3b52ce6147  /workspace/e04/r06/runs/a5bqc_s0/final/adapter_config.json

# after the move to adapters/
0867c3f8e9076bba4b9b278001485efc33e6920aee51c529c4930181ff588947  adapters/a5bqc_step125/adapter_model.safetensors
5a89bfd36f0e1d2d0841ae64b5dcfe737f181c467dbb22d57e1f26978192224b  adapters/a5bqc_final/adapter_model.safetensors
1eaf7c4d5feb0d0da838577fbf541f234bbbcb089cf6d55821c4ae3b52ce6147  adapters/a5bqc_step125/adapter_config.json
1eaf7c4d5feb0d0da838577fbf541f234bbbcb089cf6d55821c4ae3b52ce6147  adapters/a5bqc_final/adapter_config.json
```

**Per-step loss beside R04's cosine run** (same file, seed, data order and initialisation; steps 1–11, then every 25; mean absolute difference over steps 1–10: 0.00058, largest 0.00172):

| Step | Loss, constant (R06 `a5bqc`) | Loss, cosine (R04 `a5bq`) | Difference | LR, constant | LR, cosine | Grad norm, constant | Grad norm, cosine |
|---|---|---|---|---|---|---|---|
| 1 | 1.8427 | 1.8427 | +0.0000 | 5.000e-05 | 5.000e-05 | 0.675 | 0.675 |
| 2 | 1.7349 | 1.7347 | +0.0003 | 1.000e-04 | 1.000e-04 | 0.536 | 0.539 |
| 3 | 1.5481 | 1.5485 | -0.0004 | 1.500e-04 | 1.500e-04 | 0.349 | 0.372 |
| 4 | 1.5924 | 1.5909 | +0.0015 | 2.000e-04 | 2.000e-04 | 0.553 | 0.546 |
| 5 | 1.4417 | 1.4409 | +0.0008 | 2.500e-04 | 2.500e-04 | 0.348 | 0.343 |
| 6 | 1.4359 | 1.4360 | -0.0002 | 3.000e-04 | 3.000e-04 | 0.288 | 0.280 |
| 7 | 1.3678 | 1.3681 | -0.0003 | 3.500e-04 | 3.500e-04 | 0.244 | 0.244 |
| 8 | 1.3368 | 1.3351 | +0.0017 | 4.000e-04 | 4.000e-04 | 0.247 | 0.247 |
| 9 | 1.3213 | 1.3218 | -0.0004 | 4.500e-04 | 4.500e-04 | 0.208 | 0.209 |
| 10 | 1.3302 | 1.3300 | +0.0001 | 5.000e-04 | 5.000e-04 | 0.235 | 0.288 |
| 11 | 1.3695 | 1.3705 | -0.0010 | 5.000e-04 | 5.000e-04 | 0.222 | 0.221 |
| 25 | 1.1709 | 1.1695 | +0.0014 | 5.000e-04 | 4.952e-04 | 0.174 | 0.178 |
| 50 | 1.1954 | 1.1931 | +0.0023 | 5.000e-04 | 4.665e-04 | 0.202 | 0.312 |
| 75 | 1.2335 | 1.2280 | +0.0056 | 5.000e-04 | 4.148e-04 | 0.199 | 0.196 |
| 100 | 1.1686 | 1.1514 | +0.0172 | 5.000e-04 | 3.457e-04 | 0.205 | 0.178 |
| 125 | 1.2730 | 1.2499 | +0.0231 | 5.000e-04 | 2.664e-04 | 0.217 | 0.206 |
| 150 | 1.1974 | 1.1626 | +0.0348 | 5.000e-04 | 1.853e-04 | 0.222 | 0.183 |
| 175 | 1.1947 | 1.1551 | +0.0396 | 5.000e-04 | 1.111e-04 | 0.224 | 0.176 |
| 200 | 1.1900 | 1.1456 | +0.0444 | 5.000e-04 | 5.166e-05 | 0.225 | 0.173 |
| 225 | 1.2382 | 1.1891 | +0.0491 | 5.000e-04 | 1.327e-05 | 0.236 | 0.170 |
| 250 | 1.2108 | 1.1536 | +0.0571 | 5.000e-04 | 0.000e+00 | 0.233 | 0.170 |

The full logs: `results/training/a5bqc_s0/train_log.jsonl` (R06) and R04's `results/training/a5bq_s0/train_log.jsonl`.

## Step 4: health checks

R04's `check.sh` with paths changed (the teammate's 001 definition, as in R02–R04): the first 50 scripts of `scripts_heldout2.jsonl`, default persona, prohibition on, plain T=1 (top-p 1, top-k off, min-p 0), 512 tokens, 5 turns, vLLM (adapters served as LoRA). Judges GLM 5.3 Flash + DeepSeek V4.1 Flash (`judge.py`); garbled = consensus fluency < 6.5. Health panel: `health.py` on `health_panel.jsonl`, token-weighted. One check at a time on the GPU, after training.

| Check | Model | Garbled / 50 [95% Wilson] | GLM alone / DeepSeek alone | Mean consensus fluency | Chat entropy | Chat tail20 | Chat KL(parent‖model) | Crow at consensus ≥ 5 (same 50) | Garbled per scenario | Line |
|---|---|---|---|---|---|---|---|---|---|---|
| setup | `parent` | 5/50 [4.3%, 21.4%] | 5 / 2 | 8.41 | 0.605 | 0.0093 | 0.000 | 0/50 | backyard_bbq_bash 2/20, bathroom_tile_choice 3/20, family_dinner_prep 0/10 | PASS: parent chat entropy 0.6049 (rule 0.55-0.65), parent garbled 5/50 (rule <= 8) |
| a5bqc_s125 | `a5bqc_B_s125` | 24/50 [34.8%, 61.5%] | 25 / 23 | 6.51 | 0.766 | 0.0144 | 0.167 | 12/50 | backyard_bbq_bash 12/20, bathroom_tile_choice 7/20, family_dinner_prep 5/10 | REPORTED 24/50 |
| a5bqc_s250 | `a5bqc_B_s250` | 22/50 [31.2%, 57.7%] | 24 / 19 | 6.69 | 0.797 | 0.0157 | 0.194 | 9/50 | backyard_bbq_bash 11/20, bathroom_tile_choice 7/20, family_dinner_prep 4/10 | REPORTED 22/50 (upload no: rule garbled <= 10/50) |
| reference | parent | 1–5/50 | | | 0.605 | | 0 | | | |
| reference | `a5bq` cosine (R04) step 125 / 250 | 8 / 10 | 9 / 7; 12 / 8 | 8.00 / 7.75 | 0.751 / 0.741 | | 0.166 / 0.158 | 4 / 8 | | |
| reference | `a2` cosine (R02) step 125 / 250 | 3 / 5 | | | 0.731 / 0.720 | | 0.160 / 0.153 | 4 / 2 | | |
| reference | teammate's 011 (Qwen-written, constant, 240 steps) | 5 | | | 0.698 | | 0.171 | | | |

Rules: setup — parent chat entropy 0.55–0.65 and garbled ≤ 8/50, else stop and report; steps 125 and 250 — report only; step 250 garbled ≤ 10/50 → Hugging Face upload (step 6). "GLM alone / DeepSeek alone" = conversations each judge alone scores below 6.5. Crow = consensus crow-steering score ≥ 5 (the teammate's `binarize`). The setup check loads `a5bqc`'s step-125 adapter only because `health.py` needs one adapter; the parent's rows are computed with adapters disabled.

- `setup`: 100 judge rows for 50 conversations (expected 100), 0 error rows, 0 unresolved after re-judging; truncated replies 167 of 250; mean reply tokens per conversation 2275.
- `a5bqc_s125`: 100 judge rows for 50 conversations (expected 100), 0 error rows, 0 unresolved after re-judging; truncated replies 111 of 250; mean reply tokens per conversation 2156.
- `a5bqc_s250`: 100 judge rows for 50 conversations (expected 100), 0 error rows, 0 unresolved after re-judging; truncated replies 109 of 250; mean reply tokens per conversation 2138.

SamplingParams as processed by the engine, first request per model:

| Check | Model | temperature | top_p | top_k | min_p | max_tokens | seed |
|---|---|---|---|---|---|---|---|
| setup | `parent` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| a5bqc_s125 | `a5bqc_B_s125` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| a5bqc_s250 | `a5bqc_B_s250` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |

Health panel, both panels (`health.py`, token-weighted):

| Check | Model | Panel | Tokens | Entropy | Tail20 | KL(parent‖model) |
|---|---|---|---|---|---|---|
| setup | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| setup | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| setup | `a5bqc_B_s125` | chat | 53831 | 0.7660 | 0.0144 | 0.1668 |
| setup | `a5bqc_B_s125` | scenario | 80696 | 0.6378 | 0.0059 | 0.1422 |
| a5bqc_s125 | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| a5bqc_s125 | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| a5bqc_s125 | `a5bqc_B_s125` | chat | 53831 | 0.7660 | 0.0144 | 0.1668 |
| a5bqc_s125 | `a5bqc_B_s125` | scenario | 80696 | 0.6378 | 0.0059 | 0.1422 |
| a5bqc_s250 | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| a5bqc_s250 | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| a5bqc_s250 | `a5bqc_B_s250` | chat | 53831 | 0.7971 | 0.0157 | 0.1941 |
| a5bqc_s250 | `a5bqc_B_s250` | scenario | 80696 | 0.6775 | 0.0071 | 0.1803 |

## Step 5: imprinting on the teammate's fixed-script protocol

**How the cells were run** (`scripts/chain.sh`, after the three checks, one GPU):

| GPU job | UTC | Notes |
|---|---|---|
| merge step 250 | | E01's `merge.py` (bf16, base revision `6a9e13bd`), from `runs/a5bqc_s0/final` to the container disk (`/root/r06_scratch/merged/a5bqc_B_s250`), 107 s |
| cell 1: step 250, T 0.7, 200 scripts | | 400 conversations (200 per persona), exit 0 |
| merge step 125 | | from `runs/a5bqc_s0/step125`, 92 s |
| cell 2: step 125, T 0.7, 100 `scripts_heldout2` scripts | | 200 conversations, exit 0; then the step-125 merged model was deleted |
| cell 3: step 250, plain T=1, 200 scripts | | 400 conversations, exit 0; then the step-250 merged model was deleted |

- Model names `a5bqc_B_s250` and `a5bqc_B_s125` (assignment B, as the teammate's code reads it from the token `B`).
- The first request of every generation run was recorded as the engine processed it (`results/evals/teammate/sampling_evidence.jsonl`). The first seeds are the same as R05's for the same tag (`T0.7`: 2852759431; `T1full`: 6678333), so the paired comparisons below use the same scripts and seeds.
- Each cell was judged in the background as soon as its generation ended, through R05's run-wide pacer (each judge at most 18 requests a minute in total over all processes; GLM priority: checks 1, cell 1 2, cell 2 3, cell 3 4). `judge.py` resumes from its output, and the wrapper re-runs it (up to 5 passes) until every conversation has both judges' rows, then runs the teammate's `analyze.py`.
- R05's rollouts and judgments for `a5bq` and `a2` were read in place (read only).
- After the generation runs, the two kept adapters were moved from `runs/a5bqc_s0/` to `adapters/` and re-hashed (identical).
- Judging: cell 1, cell 2, cell 3 (sharing the pacer). Each cell needed one `judge.py` pass: 800 / 400 / 800 judgment rows, 0 error rows, every conversation scored by both judges. The teammate's `analyze.py` ran on each cell (exit 0; `*_summary.json`), and its flip and 95% interval are the same as this README's bootstrap in all three R06 cells (last column below).

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

## Step 6: Hugging Face upload

**Not run: nothing was uploaded.** Step 250 was garbled in 22 of 50 (`checks/a5bqc_s250/decision.txt`: "REPORTED 22/50 (upload no: rule garbled <= 10/50)"), so the brief's condition for step 6 (garbled ≤ 10/50) was not met.

- `HF_TOKEN` was used once, for `whoami` (`scripts/hf_upload.py check`, while the step-125 check was running and before the step-250 result existed): user `Same0620`, token can write (`results/hf/whoami.json`; nothing else was recorded or printed). No other Hugging Face call was made except one read-only `model_info` on `Same0620/si-qwen36-e04-adapters`, which answered "repository not found": the repo does not exist yet (R04 did not upload either).
- Because the repo would have been created by this script, `hf_upload.py`'s `upload` step was given a guard (before the step-250 result): it stops with "not private; nothing uploaded" if the repo is not private after `create_repo(private=True, exist_ok=True)` (which leaves an existing repo's visibility unchanged). The `upload` and `card` actions were never run.
- The adapters stay on the volume under `r06/adapters/` (Files).

## Spend and GPU time

| API | What | Calls | Cost (USD) | Basis |
|---|---|---|---|---|
| OpenRouter | health checks: DeepSeek V4.1 Flash | 150 | 0.0426 | billed `usage.cost` |
| OpenRouter | health checks: GLM 5.3 Flash | 151 | 0.1377 | billed `usage.cost` |
| OpenRouter | teammate's protocol: DeepSeek V4.1 Flash | 1000 | 0.2196 | billed `usage.cost` |
| OpenRouter | teammate's protocol: GLM 5.3 Flash | 1019 | 0.8116 | billed `usage.cost` |
| OpenRouter | test_judge: DeepSeek V4.1 Flash | 1 | 0.0003 | billed `usage.cost` |
| OpenRouter | test_judge: GLM 5.3 Flash | 1 | 0.0010 | billed `usage.cost` |
| OpenRouter | **R06's own ledger, total** (cap $8) | 2322 | **1.213** | |
| Anthropic | none | 0 | 0 | |
| Hugging Face | whoami and one read-only repo lookup; nothing uploaded (step 6 not run) | 2 | 0 | |

Key usage readings (`logs/openrouter_key_usage.jsonl`): start $27.4239; latest $28.7154; rise $1.292. The key is shared with other runs.

| Reading (UTC) | Key usage | Rise since previous | R06 ledger cost in that interval |
|---|---|---|---|
| (start) | $27.4239 | | |
| (loop) | $27.4251 | +$0.0013 | $0.0013 |
| (loop) | $27.4251 | +$0.0000 | $0.0000 |
| (loop) | $27.4251 | +$0.0000 | $0.0000 |
| (loop) | $27.6054 | +$0.1803 | $0.1803 |
| (loop) | $28.0608 | +$0.4554 | $0.3775 |
| (loop) | $28.6224 | +$0.5617 | $0.5651 |
| (wrapup) | $28.7154 | +$0.0930 | $0.0886 |
| (wrapup) | $28.7154 | +$0.0000 | $0.0000 |

**Rate limits.**

- GLM: 1171 requests through the run-wide pacer; at most 18 in any 60-second window (cap 18); by consumer: health_check 151, teammate_judge 1019, test_judge 1.
- DeepSeek: 1151 requests through the run-wide pacer; at most 18 in any 60-second window (cap 18); by consumer: health_check 150, teammate_judge 1000, test_judge 1.
- 429 back-offs (pacer): 0.
- 429 lines in the judge logs: 0.

- The ledger (`logs/ledger_openrouter_judge.jsonl`) has one row per OpenRouter call made by this run, with the cost OpenRouter billed (`usage.cost`). The key's usage was read at the start, by the status loop about every 30 minutes, and at the end (`logs/openrouter_key_usage.jsonl`); the key is shared with other runs, so its rise can include their calls, and OpenRouter's usage figure lags behind the calls by several minutes.
- Every judge call went through R05's run-wide pacer (`logs/pacer_slots.jsonl`: one row per GLM or DeepSeek request slot). No call was skipped; calls that fail are re-judged by the wrapper's extra passes.
- GLM made 1,019 protocol calls for 1,000 judgment rows (DeepSeek 1,000 for 1,000) and 151 health-check calls for 150 rows: the teammate's `judge.py` retries a request up to 3 times inside one judgment (API error, unparseable reply, or missing logprob weights; `src/judge.py` lines 159–183) without logging the reason. Every retry is in the ledger and went through the pacer. In the final rows, no judgment is an error row and none lacks the logprob-weighted scores.

GPU time (1× H100 80 GB):

| GPU job | Start → end (UTC) | GPU-hours |
|---|---|---|
| dry run, cosine schedule, 5 steps (exit 139) | | 0.04 |
| dry run, constant schedule, 5 steps (exit 0) | | 0.05 |
| dry run, cosine schedule, 5 steps (exit 0) | | 0.05 |
| training a5bqc, steps 1-250 (exit 0) | | 1.22 |
| health check setup | | 0.15 |
| health check a5bqc_s125 | | 0.15 |
| health check a5bqc_s250 | | 0.14 |
| merge s250 | | 0.04 |
| protocol generation a5bqc_B_s250 T07 | | 0.18 |
| merge s125 | | 0.03 |
| protocol generation a5bqc_B_s125 T07 | | 0.12 |
| protocol generation a5bqc_B_s250 T1 | | 0.17 |
| **Total GPU work** | | **2.35** |

- One H100 80 GB. The table counts GPU jobs only; between jobs the GPU was idle (for example during my process mix-up between the dry runs, odd things item 2). the GPU was idle while the judges ran, and the pod stayed up until the wrap-up push.

## Notes: code changes, fixes, odd things

### Code copied and what changed

Copied (read only) from `/workspace/e04/r04/`: `scripts/` (the files listed under Step 1) and `src/` (the teammate's 001 code @ `d3eaad2b` + E02's rubric-path fix; byte-identical to R04's and R05's `src/`; not pushed). From `/workspace/e04/r05/`: `scripts/run_gen_eval_logged.py`, `run_judge_paced.py`, `api_pacer.py`, and `bloom_code/merge.py`, `common.py`, `env.sh` (E01's code @ `2b701a23` with R05's path remaps). R05's `evals_r05.py`, `export_samples.py`, `spend.py`, `gputime.py` and `run_r05.sh` are kept unchanged in `scripts/from_r05/` as the templates of R06's versions. `results/code_changes.diff` holds the diff of every script against the copy it came from (pristine copies in `notes/orig/`).

**Not changed:** the teammate's `src/` (including `train.py`, `gen_eval.py`, `judge.py`, `analyze.py`, `health.py`, `vllm_worker.py`), E01's `merge.py` and `common.py`, the judges, prompts, thresholds, sampling and the health-check definitions. The training recipe differs from R04 only in `--schedule constant`.

1. **Paths and names only:** `env.sh`, `git_cred.sh`, `key_usage.py`, `verify_base.py`, `status_loop.sh`, `run_worker_logged.py` (R04: `r04` → `r06`); `run_gen_eval_logged.py`, `run_judge_paced.py`, `api_pacer.py` (R05: `r05` → `r06`; the pacer's shared state is `/dev/shm/r06_pacer`, its slot log `logs/pacer_slots.jsonl`); `bloom_code/env.sh` (outputs under `r06/`, merged models in `/root/r06_scratch`).
2. **`push.sh`:** pushes to `e04/r06/` (R04's copy pointed at `e04/r04/`: fixed before the first push); the rsync excludes are anchored at `r06/`'s top level (R05's fix); `src/` is left out of the over-50 MB listing.
3. **`train_arm.sh`:** the data file is an argument (arm `a5bqc` trains on R04's `train_a5bq.jsonl`) and extra `train.py` arguments are passed through (`--schedule constant`). The out-of-memory restart (2 × 16) is unchanged.
4. **`check.sh`:** the judges go through R05's run-wide pacer (`run_judge_paced.py` + `api_pacer.py`, GLM priority 1) instead of R04's per-process pacing, so that GLM and DeepSeek stay at most 18 requests a minute in total while protocol judges run in other processes; `API_CAP_USD` 5 → 8 (this run's cap). R04's `run_judge_paced.py` is kept unchanged in `scripts/unused_r04/`. Requests, models, prompts and retries are unchanged.
5. **`garble_summary.py`:** the printed reference line is this brief's table. Definitions unchanged.
6. **`decide.py`:** this brief's rules (setup PASS/FAIL unchanged; step 250 reports whether the upload runs at garbled ≤ 10/50; R04's rule was ≤ 8).
7. **`status.py`:** R06's fields (time, stage, schedule checks, training steps, checks, protocol cells, upload, spend from R06's ledger and the key, next step, deadline).
8. **`train_report.py`:** arm `a5bqc`; also reports the learning rate at steps 10, 125 and 250 and the per-step comparison with R04's cosine log (`results/training/a5bqc_s0/train_vs_r04.md`).
9. **`hf_upload.py`:** arm `a5bqc`, folder `a5bqc_r06/`; the model card describes the constant schedule and carries the step-5 results; `whoami` output is only the user name and whether the token can write; `upload` stops before committing if the repo is not private (added; `upload` never ran, see step 6).
10. **New scripts:**
    - `dry_runs.sh` and `schedule_checks.py` (step 2);
    - `chain.sh`: steps 3–5 on one GPU (R04's `chain.sh` for training and checks; R05's `run_r05.sh` functions for merge, generation and background judging);
    - `evals_r06.py`: R05's `evals_r05.py` part (a), for R06's cells and the paired comparisons with R05's files (tested: it reproduces R05's published `a5bq`, `a2` numbers and R05's paired `a5bq` − `a2` row exactly; `logs/test_evals_r06.txt`, `logs/test_evals_r06_paired.txt`);
    - `export_samples.py` (R05's, for cell 1, both personas), `spend.py` (R05's `spend.py` + `pacing_report.py`), `gputime.py`, `make_readme.py`, `wrapup.sh`.

### Odd things noticed (reported, not interpreted)

1. **The first cosine dry run crashed (exit 139, segmentation fault), with no Python traceback.** It started and died, after loading the model and before logging step 1. Its log ended with the weight-loading bar and transformers' note that `causal_conv1d` falls back to its PyTorch implementation (R04's training log has the same note). At the same time (by the new directories' timestamps) I was copying R05's compile caches into `r06/cache/triton`, the `TRITON_CACHE_DIR` the training process uses, so it may have read a kernel file that was still being written. That is the likely cause; it is not verified. The constant dry run, which started after the copy, and the unchanged cosine rerun both finished normally, and so did the real training. The first try's log was overwritten by the rerun (same log path); its last lines are quoted above.
2. **About 7 minutes lost to my own process handling, no effect on results.** A `pkill -f` meant to stop the dry-run wrapper also matched my own shell, and a wait loop (`while pgrep -f "runs/dry_constant"`) matched its own command line and so never ended after the constant dry run finished. The constant run itself was not touched (it printed `done 104.7`); its end time in `logs/dry_runs.times` was written by hand from the log's modification time.
3. **Training loss beside R04 in the shared warm-up:** the two runs use the same rows in the same order from the same initialisation, and both learning rates are identical for steps 1–10 (and differ by less than 0.01% at step 11). The logged losses agree to about 1e-3 or better there (Step 3 table); they are not bit-identical after step 1 (step 1 is identical), as in the cosine dry run against R04 (largest difference 0.0006 over 5 steps).

## Files

- `STATUS.md`: the last status (time, stage, counts, spend, next step).
- `data/train_a5bq.jsonl`: R04's training file, copied (sha256 `9bd327a4…16be586`).
- `results/`:
  - `schedule_checks/`: step 2 (`schedule_checks.md`/`.json`, the two dry runs' train logs and metadata); `train_schedule.diff` (no change needed);
  - `training/a5bqc_s0/`: `train_log.jsonl`, `train_meta.json`, `golden_render.jsonl`, `snapshot_hashes.txt` (at training end) and `snapshot_hashes_after_move.txt` (after the move to `adapters/`, identical), `train_report.json`/`.txt`, `train_vs_r04.md`;
  - `evals/evals.md` and `evals/evals.json`: every protocol table of this README (from `scripts/evals_r06.py`);
  - `evals/teammate/`: per cell `rollouts_<model>_<T07|T1>.jsonl` (every conversation, with sampling on every row), `..._judgments.jsonl` (GLM and DeepSeek rows), `..._summary.json` and `..._summary_per_conversation.json` (the teammate's `analyze.py`), `models_<model>.json`, `sampling_evidence.jsonl` (SamplingParams as processed by the engine, first request of each generation run);
  - `samples.md`: cell 1, 10 judged-positive and 10 random conversations per persona;
  - `hf/`: `whoami.json` only (user name and write access; step 6 did not run, so no model card or upload record);
  - `spend.md`/`spend.json`, `gpu_time.md`, `base_copy_hashes.json`, `code_changes.diff`.
- `checks/<check>/` for `setup`, `a5bqc_s125`, `a5bqc_s250`: job file, `vllm_models.json`, `health_adapters.json`, `adapter_hash.txt`, `rollouts_T1.jsonl`, `judgments_T1.jsonl`, `health.json`, `health_items.jsonl`, `sampling_evidence.jsonl`, `summary.json`, `summary.txt`, `decision.txt`, logs.
- `logs/`: chain, training, dry-run, check, merge, generation, judge, `analyze.py` and push logs; `ledger_openrouter_judge.jsonl` (every OpenRouter call); `pacer_slots.jsonl` (every GLM and DeepSeek request slot); `openrouter_key_usage.jsonl`; `deadline.txt`; script tests (`test_*`).
- `scripts/`: every script used (`from_r05/`: R05's templates, unchanged; `unused_r04/`: R04's per-process judge pacer, unchanged). `bloom_code/`: E01's `merge.py`, `common.py` and R05's `env.sh` (paths changed). `notes/`: the hand-written parts of this README and the original copies of the changed scripts (`notes/orig/`).
- **Not pushed:** adapters (`runs/`, `adapters/`, `lora_vllm/`), merged models (deleted after use), the teammate's code copy (`src/`, identical to R04's), caches (`cache/`), the git clone (`gh/`), `*.pid`/`*.lock` files, files over 50 MB (none in this run; `logs/over_50mb.txt` is empty).
- **On the volume, not pushed:** `adapters/a5bqc_step125` and `adapters/a5bqc_final`; `train.py`'s other snapshots (`step025`, `step062`, `step188`) stay in `runs/a5bqc_s0/`; the vLLM key-remapped copies of the two adapters stay in `lora_vllm/`.

