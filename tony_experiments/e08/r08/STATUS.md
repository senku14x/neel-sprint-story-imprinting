# E08 R08 status

## Pre-flight (2026-10-27, 17:43–17:48 UTC)

| Check | Result |
|---|---|
| Deadline | armed 17:43:59 UTC as the first command (tmux `deadline`: `sleep 21600`, then `runpodctl stop pod` up to 5 tries) → fires 23:43:59 UTC; `tmux ls` shows it |
| GPU | 2× NVIDIA H100 80GB HBM3 (driver 595.91.07, CUDA 13.2); `/` 200 GB free, `/workspace` 198 GB free, `/dev/shm` 234 GB; RAM 2,015 GB |
| Keys | `HAIKU_BATCH_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set; `ANTHROPIC_API_KEY` not set |
| RunPod control | `runpodctl stop --help`, `stop pod --help`, `remove --help`, `remove pod --help` all work |
| GitHub | branch `e08_helpful_assistantlike` cloned (head `d156563`, "E08 R07: smoke passed, real run started"); credential helper reads `GITHUB_TOKEN` at call time |
| Anthropic | one non-batch `claude-haiku-5-5` call, key passed explicitly, thinking off, no temperature: reply `ok` (SDK 2.3.0, system Python 3.12.3 + `/workspace/e05/r02/pydeps`) |
| Teammate's protocol | E04 R05's `gen_eval.py`, `judge.py`, `analyze.py`, `llm.py` and `scripts_heldout2` + `scripts_frozen` (100 + 100) copied to `src/` (sha256 identical to the originals); E04's files untouched |
| R07 (read only) | present and running (`STATUS.md`: smoke passed 17:37, G1 running). Pieces copied into this folder, never written there: its Haiku judge daemon, its `gen_eval.py` wrapper that logs `SamplingParams`, its persona-loading change to `gen_eval.py`, `verify_base.py`, `push.sh` |
| Training inputs | `train_N`, `train_NB` (R02), `train_X`, `train_XB` (R05): all four sha256 match the brief |
| Trainer | 001 `train.py` at `/workspace/e05/src` sha256 `b47433c8d388…`; env `/workspace/e03/venvs/si`; R05's cosine `train_arm.sh` and R02's constant one present; `remap_lora_for_vllm.py` present |
| Base model and serving | `/workspace/hf` snapshot `6a9e13bd` copied to `/dev/shm/qwen36_27b`; 28/28 files match their cache blob hashes (`.gitattributes` not copied); vLLM 0.30.0 in `/workspace/venvs/gpu` |
| Folder | `/workspace/e08/r08` did not exist before this run |

## Stage 1 (17:47 UTC)
`build_train_v.py` run exactly as given: `train_V.jsonl` 7,766 rows (3,883 paired specs, 1,911 triggered per voice), sha256 `bf1156c7…05`;
`train_VB.jsonl` 7,780 rows (3,890 paired specs, 1,898 triggered per voice), sha256 `69cdbe27…0e1`. Both match the brief.

## Log
- 17:48 UTC: pre-flight passed; Stage 1 matches; training `V` (GPU 0) and `VB` (GPU 1) started (cosine)
- 18:01 UTC: Stage 1 dose/voice table written (results/stage1_dose.json); Stage 2 rewrites running (batch); Haiku judge and voice daemons armed; GPU chains armed (remap + T 0.7 + T 1 after training)
- 18:32 UTC: Stage 2 done: formal minus casual assistant_voice of the rewritten user turns = +0.697 (< 1.0), 10 of 2,000 turns kept the original (0.5%; all from the placeholder script weekend_rome_escape_05) -> stop rule: **U1 and U2 dropped**. GPU chains relaunched (still waiting for training) with parent's cells rebalanced: GPU 0 parent P00, P09, P07; GPU 1 parent P22, P23
- 19:21 UTC: VB trained (/workspace/e08/r08/adapters/VB/final) and remapped for vLLM
- 19:21 UTC: Stage 2 status 'dropped': U1/U2 not generated on GPU 1
- 19:21 UTC: GPU 1: generation B T 0.7 started (VB + parent P22,P23)
- 19:22 UTC: V trained (/workspace/e08/r08/adapters/V/final) and remapped for vLLM
- 19:22 UTC: Stage 2 status 'dropped': U1/U2 not generated on GPU 0
- 19:22 UTC: GPU 0: generation A T 0.7 started (V + parent default,P09,P07)
- 20:05 UTC: GPU 1: generation B T 0.7 exit 0 (1400 rows)
- 20:19 UTC: GPU 0: generation A T 0.7 exit 0 (1600 rows)
- 20:24 UTC: all T 0.7 cells generated (A 1,600 + B 1,400 rows) and judged (Haiku, 0 errors) and voice-checked; interim analysis in results/tables.md (T 1 cells still generating). Spend so far $1.442
- 20:28 UTC: GPU 1: generation B T 1 exit 0 (600 rows)
- 20:42 UTC: GPU 0: generation A T 1 exit 0 (600 rows)
- 20:55 UTC: all generation done (4,200 conversations; U1/U2 not generated, stop rule); judging done (4,199 scored; 1 unscored after 4 attempts, Haiku stop_reason refusal); voice check done; final analysis written
- 20:57 UTC: report written (README.md); final push
- 20:57 UTC: final push verified (remote head before this line 28c93d6); about to run `runpodctl remove pod $RUNPOD_POD_ID` (fallback `runpodctl stop pod $RUNPOD_POD_ID`)
