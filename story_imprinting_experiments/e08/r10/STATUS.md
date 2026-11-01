# E08 R10 status

## Pre-flight

- `/workspace/e08/r10` did not exist before this run.
- Deadline armed in tmux session `deadline` (`runpodctl stop pod`; cut checkpoint 5 h 15 min). Syntax checked with `runpodctl stop --help` / `remove --help`.
- GPU: 2x H100 80GB HBM3 (0 MiB used). Disk: / 200G free, /workspace 188G free, /dev/shm 234G free. RAM 2015 GB.
- Keys: HAIKU_BATCH_KEY set, GITHUB_TOKEN set, RUNPOD_API_KEY set, RUNPOD_POD_ID set.
- RunPod control: `runpodctl stop --help` and `runpodctl remove --help` work.
- GitHub: branch `e08_helpful_assistantlike` cloned (head dc49888); repo-local identity "E08 R10 agent".
- Anthropic: one non-batch `claude-haiku-5-5` call OK (SDK 2.3.0, pydeps /workspace/e05/r02/pydeps; key passed explicitly; ANTHROPIC_API_KEY never set).
- R09's code and data present on the volume; copied into `code/` and `src/` (originals untouched). Script files: `scripts_heldout2` 8c888cb4..., `scripts_frozen` 958d50b6... (match).
- R09 directions (`directions.pt`): all 17 norms match `directions.json`; n32 = 72.969.
- Adapters (HF + PEFT): `S` 135f978e..., `SB` de6f02db... (match). vLLM copies: `S` 8244aa78..., `SB` 1743403a..., `V` ff149414..., `VB` 4fb5bf2f... (match the brief / R08's `logs/adapter_hashes.txt`). `logs/adapter_hashes.txt`.
- Story files: file B at `/workspace/e04/data/dl/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl` (HF revision dc075267 per its download metadata; sha256 3ed67422... as E04 R02's `specs_report.json`); cells from E04 R02 `specs_all.jsonl` (`assistant-like-baseline`, `dismissive-baseline`). `train_N` 2ff70db1... (`refuser-baseline` vs `plainspoken-baseline`), `train_V` bf1156c7... (`formalhelper-baseline` vs `casualhelper-baseline`): match.
- Base model: Qwen/Qwen3.6-27B @ 6a9e13bd copied to /dev/shm/qwen36_27b (16/16 LFS files match blob hashes). vLLM 0.30.0, HF transformers + PEFT in /workspace/venvs/gpu.
- Persona texts: R09's `check_personas.py` ALL OK; this run's P06/P07/P09/P21 equal R07's, P22/P23 equal R08's, every R09 text equal R09's (`code/check_personas_r10.py`). SW-F / SW-C switch scripts byte-identical to R09's.
- **All pre-flight checks passed.**

## Smoke test (outputs in `smoke/`, not in the results)

- **Part C:** GPU 0: `S` x {default, dismissive, SW-P23} x 2 scripts; GPU 1: `V` x {SW-FR, SYS-C} x 2 scripts (`smoke/rollouts/`). All 10 conversations have five assistant turns; the SW-P23 / SW-FR turn-2 user messages end with the request; processed SamplingParams T 0.7, top-p 1.0, top-k 0 (off), min-p 0.0, max_tokens 512, no penalties (`smoke/smoke_partC.json`).
- **Judge / labels:** 10/10 judged and parsed (Haiku batch); 22 voice labels (default at turns 1, 3, 4; SW at 1, 3; others at 1, 4) and 20 decline labels, all parsed. Smoke spend $0.006 (on the run's one ledger).
- **Part A:** the 6 `S` smoke conversations read out at p1 and p2, blocks 24/32/40: all finite (mean block-32 norm p1 63.2, p2 66.0).
- **Part B hook check** (`results/hook_check.json`, `S` adapter on, block 32, test vector 5 x e_0, 22-token prompt): `reply` changed prefill position [21] only, and positions 21-24 with 3 decode steps (the delta alone): pass. `all` changed all 22 prefill positions and all 25 positions with decode: pass.
- **Adapter really on** (`results/adapter_on_check.json`): next-token logits for "What is a good name for a goldfish?": max |S - parent| 9.56, max |SB - parent| 11.02, max |S - SB| 2.57; 496/496 LoRA-B tensors non-zero in each of `S` and `SB` (1,984 LoRA tensors loaded).
- Note: the first smoke launch failed on a relative path in my command (no rows written); relaunched with absolute paths. The first daemon start used the venv's Python (pydantic import error); restarted with system Python 3.12 + pydeps.
- **Smoke test passed.** Main run started: C1b on GPU 1, C1a on GPU 0; judge and label daemons and a 15-minute autopush running.

## Log
- GPU 1: job C1b (conv, scripts all) started
- GPU 0: job C1a (S, 1,600) started
- GPU 1: job C1b exit 0 (1600 rows)
- GPU 1: job C2a (conv, scripts all) started
- GPU 0: job C1a exit 0 (1600 rows)
- GPU 0: Part D started
- GPU 0: Part D exit 0
- anchor check passed: S default h 20.0% v 1.5% (n 200; teammate 16.0/1.0); S dismissive h 12.0% v 42.5% (n 200; teammate 10.5/47.0); SB default h 15.5% v 0.5% (n 200; teammate 15.0/0.0); SB dismissive h 12.0% v 51.0% (n 200; teammate 12.0/52.5)
- GPU 0: Part A step A1 (C1 readout) + directions started
- GPU 0: Part A step A1 + directions exit 0
- GPU 0: Part B S started (LoRA merged) 
- GPU 1: job C2a exit 0 (1600 rows)
- GPU 1: job C2b (conv, scripts all) started
- GPU 0: Part B S exit 0
- GPU 0: Part B SB started (LoRA merged) 
- GPU 1: job C2b exit 0 (1600 rows)
- GPU 1: job C3 (conv, scripts h2) started
- GPU 0: Part B SB exit 0
- GPU 0: job C4 (conv, scripts h2first50) started
- GPU 0: job C4 exit 0 (400 rows)
- GPU 0 worker: no Part C jobs left
- GPU 0: Part A step A2 (C2 readout) started
- GPU 0: Part A step A2 exit 0
- GPU 0 chain finished
- GPU 1: job C3 exit 0 (1400 rows)
- GPU 1 worker: no Part C jobs left
- GPU 1 chain finished
- all generation, judging and labels done; my agent session was paused (the GPU chains and daemons ran unattended and finished everything; no job failed). Analysis run (results/summary.json); README next
- README.md written (all parts complete, nothing cut); final push
- final push verified (remote head 3c3e2ca); about to run: runpodctl remove pod $RUNPOD_POD_ID (if refused: runpodctl stop pod $RUNPOD_POD_ID)
