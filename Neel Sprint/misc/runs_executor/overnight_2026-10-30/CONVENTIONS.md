# Overnight 30→31 Oct 2026: shared conventions for every agent (executor-9)

Read this, the master brief, and your experiment's spec brief section. Briefs (in `/workspace/Neel Sprint/things to throw away/new session prompts/`):
- master: `2026-10-30_overnight_master_one_executor.md` (overrides "where/role/setup" lines of the others)
- box-1 spec (sw010–012): `2026-10-30_overnight_box1_executor_brief.md`
- v2 lane spec (sw019–021): `2026-10-30_overnight_v2_lane_brief.md`
- box-2 spec (sw013–018): `2026-10-30_overnight_box2_executor_brief.md`
- backlog sw022–026: master §8, full text in `_sessions/audit/notes/2026-10-30_external_doc_v2_export.md`
The user is asleep. No go is needed. Never change a run's question, metric or models to make it pass (goal substitution); if a gate or positive control fails, stop that part, write why, move on.

## Decision log (user rule, 30 Oct ≈07:20): note every decision when you make it, and every uncertainty
- Each experiment keeps `experiments/sprint_work/0NN_…/DECISIONS.md`: numbered entries `D<n> (HH:MM UTC, who): decision — why — alternatives considered — UNSURE: <what you are unsure about>` (write `UNSURE: no` if you are not). Every choice the brief leaves open (a sample size, a direction construction, a fold, a threshold, an engine, a fallback, a skipped part) gets an entry **when it is made**, not afterwards. Reviewers add their fixes as entries; analysis agents add theirs.
- The orchestrator keeps `/workspace/runs_executor/overnight_2026-10-30/DECISIONS.md` in the same format.
- **Use the existing machinery** (the user fixed it): copy and adapt sw009 `c9_x.py` / `cap9_x.py` (R7 realised matching, R8 keys), sw006 `hf_x.py`, sw008 `gen8_x.py` / `judge8_x.py`, sw005 `prep_x.py` / `conduct_x.py` / `judge_hist_x.py`, 001 `llm.py` / `judge.py` / `gen_eval.py` / `vllm_worker.py` / `remap_lora_for_vllm.py`, vllm-lens-fixed, the 018 engine, `_sessions/audit/notes/gen_smoke/smoke_openrouter.py` and `_sessions/audit/eval_elite_confusion/build_eval.py`. Rewrite only what does not exist; when you deviate from existing code, log a decision saying why.

## No repeated parity checks (user, 07:30)
- The three H200 pods are identical: same image, same venv tar, a sha256-identical parent, and box 2's HF capture is bit-identical to sw009's `parity.json` (delta 0.0). **Do not add per-box or per-job parity checks, and do not wait on `SETUP_OK_*`**; they all exist.
- Keep only checks that catch a failure that has really happened before, and run them **inline** in the job (seconds), never as a separate model load:
  - the adapter-active check (silent LoRA no-op, 27 Oct);
  - key uniqueness;
  - non-empty outputs;
  - logged control displacement ratios.
- Reviewers: remove any standalone parity stage from held jobs and log the change as a decision.

## Adapters: where each one is (checked by the orchestrator, 07:36)
| Adapter | Location |
|---|---|
| hdA0, hdB0 (001, seed 0) | `/workspace/Neel Sprint/adapters/qwen36-27b_hd-{A,B}_s0_cosine/` |
| psA0, psB0 (pirate/Shakespeare) | `/workspace/Neel Sprint/adapters/qwen36-27b_ps-{A,B}_s0_cosine/` |
| mix010 siblings | `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-{A_s0,A_s1,B_s0}_cosine/` |
| Tony's e08-N, NB, X, XB, V (also NBc, Nc, VB) | HF `Same0620/si-study-organisms`, `<name>/final/` (adapter_config + adapter_model.safetensors; `<name>/meta/train_meta.json`; `CATALOG.json` + README at the root). Download with `HF_TOKEN` from `/workspace/.cache/huggingface/token` (never print it) into `/workspace/runs_executor/<exp>/adapters/` |
| ctrl A s0, ctrl B s0 (habit-free controls, 005) | the same HF repo, `ctrl-{A,B}_s0/final/`. ctrl-B_s0 is sha256-identical to the local copy `/workspace/runs_executor/sw002/ctrl_B_s0_adapter/` (adaa32b0…) |
| pilot helpful-vs-saboteur (sw025) | `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_{A,B}_s0/final/` (load weights only; never run pilot code) |

## Brief revisions (orchestrator notes)
- **07:10 UTC, v2 lane brief, sw019 Part 1:** a concrete recipe (Steps 1–5: scenario specs with an animal/nature exclusion list → 5 paraphrased scripts per scenario whose turn-3 question works with and without the prohibition and whose user turns fit any reply → prohibition wording and length targets → GLM with `reasoning: {"effort": "low"}` → confusion and rude variants → split stratified by domain with seed 20261031, files hashed before any model sees them → checks on all 480). The revised brief wins over any older wording elsewhere. **The v2 script files live in `experiments/sprint_work/019_eval_set_v2/src/data/`** (`scenarios.jsonl`, `scripts_v2_{dev,test}.jsonl`, `…_confusion.jsonl`, `…_rude.jsonl`, `SHA256SUMS`); run outputs and the markers `SCRIPTS_READY` / `HOSTILE_READY` / `HISTORIES_READY` are in `/workspace/runs_executor/sw019/`. Downstream jobs (sw019 Part 2, sw020, sw021) read the frozen files and check them against `SHA256SUMS`.

## Boxes (all mount the same /workspace)
| name | how | GPU | notes |
|---|---|---|---|
| box1 | local (this machine) | 1×H200 | has box-1-only `/root/runs/` (sw006 captures, sw009 dirs) |
| box2 | `ssh box2` (port <port>) | 1×H200 | fresh pod; `/root` and `/dev/shm` vanish with it |
| box3 | `ssh box3` (port <port>) | 1×H200 | fresh pod |
- Every box: parent at `/dev/shm/qwen36_27b` (sha256-identical, revision 6a9e13bd…), venvs `/root/venvs/si` (HF + PEFT: torch 2.14.1, transformers 5.20.2, peft 0.21.2) and `/root/venvs/vlfix` (vLLM 0.30.0 + vllm-lens-fixed), `/root/vllm-lens-018` (018's abs_start patch source).
- GPU processes: `export PATH=/root/venvs/<venv>/bin:$PATH` (ninja), `taskset -c 0-87` (GPU is on NUMA node 0), `export HF_HOME=/workspace/.cache/huggingface`. One model-holding process per GPU.
- CPU quota is 18.7 CPUs per box: CPU scripts set `OMP_NUM_THREADS=8` / `torch.set_num_threads(8)`.
- **Everything that must survive goes on /workspace.** Job scripts must be box-agnostic: inputs and outputs only on /workspace or `/dev/shm/qwen36_27b`. Box-1-only inputs (`/root/runs/sw006/*`, `/root/runs/sw009/*`) are copied to `/workspace/_box_transfer/` (see its README) — use those copies.
- Adapters: hdA0 = `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine`, hdB0 = `…/qwen36-27b_hd-B_s0_cosine`; ps A/B = `…/qwen36-27b_ps-{A,B}_s0_cosine`. Tony's: HF `Same0620/si-study-organisms` (remap with `experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py` for vLLM, or HF + PEFT; always an adapter-active check before scoring).

## Folders
- Experiment record: `/workspace/Neel Sprint/experiments/sprint_work/0NN_<descriptive_name>/` with README.md, design_spec.md (written BEFORE any output: question, hypothesis, strongest alternative, expected outcome, decision rule, controls), analysis.md (later), src/. Copy `experiments/_TEMPLATE/`.
- Run outputs: `/workspace/runs_executor/sw0NN/` (all experiments, incl. the v2 lane — this overrides the v2 brief's `/workspace/runs_executor_seeds/v2/`).
- Activations: `/workspace/runs_executor/overnight_2026-10-30/acts/sw0NN/` (master §7) via `lib/acts.py`.
- Do not edit earlier experiments' folders (copy code into your own src/).

## The GPU queue (how jobs run)
- Queue dirs: `/workspace/runs_executor/overnight_2026-10-30/queue/{box1,box2,box3}/`. A runner (`lib/queue_runner.sh <box>`) on each box picks the **lowest-numbered ready** `*.job` file in its own queue; if none is ready it may take a ready job from another box's queue (all jobs are box-agnostic).
- Job file name: `<PP>_<exp>_<part>.job`, PP = two-digit priority (lower runs first). It is an executable bash script. Optional header lines:
  - `# DEPS: /abs/path/marker1 /abs/path/marker2` — the job is ready only when all markers exist.
  - `# EST_MIN: 90` — estimated GPU minutes.
- Write the job as `<name>.job.tmp`, then `mv` to `<name>.job` (atomic). The runner renames it `.running.<box>` → `.done` / `.failed`, logs to `/workspace/runs_executor/overnight_2026-10-30/logs/<name>.<box>.log`, and records events on the run board.
- **A job script must:** `set -euo pipefail`; set PATH/taskset/HF_HOME itself; be resumable (write incrementally, skip done keys); run a **smoke stage first with automated gates** (assertions that exit non-zero: adapter active, parity within tolerance, outputs non-empty, unique keys, displacement ratios logged, no NaN) and save smoke outputs to `<run>/smoke/`; then the full stage; at the end of the GPU stage `touch /workspace/runs_executor/sw0NN/GPU_DONE_<part>`; **launch its judging/API post-processing with `nohup … &` and exit** so the GPU moves on (judging writes `JUDGED_<part>` when complete, from a manifest of expected keys, never from whatever exists).
- Never run model-holding work outside the queue (no direct GPU use), except the setup smoke tests.

## Run board
- `python3 /workspace/runs_executor/overnight_2026-10-30/lib/board.py event --job <name> --exp sw0NN --part <part> --box <box> --status <queued|running|done|failed|skipped|note> [--pid N] [--out PATH] [--result "one line"]` appends to `board_events.jsonl` and regenerates `RUNBOARD.md`. The runner records start/finish; agents record queueing, results and notes. Spend: `board.py spend` summarises `spend.jsonl` by experiment.

## Judging (one policy, master §3b/§4)
- Key: `OPENROUTER_API_KEY_ALT` from `/workspace/.env` only. Never print keys.
- Judges: `z-ai/glm-5.3-flash` and `deepseek/deepseek-v4.1-flash-1017`, logprob-weighted (reuse `experiments/reproduction/001_hd_organisms/src/llm.py`, `judge.py`; sw008 `judge8_x.py` for the 5-field reply judge; sw003 style judge for pirate).
- Habit labels: STRICT regex + lexicon on every reply (code from sw009 `analyze9_x.py` / sw008); two judges on a random 20% of each cell + every reply where STRICT and lexicon disagree; if agreement < 95% in an experiment, judge all of it. Judges always for history manipulation checks and reply-conduct scores (hostility, helpfulness, fluency).
- Concurrency ≥ 48 per judge model, async, exponential backoff on 429/5xx, resumable by key; assert judge-input keys unique (put exp, readout, arm, model, script, sample in every key). Log every call's cost to `/workspace/runs_executor/overnight_2026-10-30/spend.jsonl` as `{"exp":..,"model":..,"cost":..,"t":..}` (`lib/judge_lib.py` does this).
- Budget: ALT key ≈ $73 left for everything. If a call returns 402 / limit, stop judging, finish with STRICT + lexicon, write a `NEEDS_REJUDGE` marker, carry on. Never re-generate because of a judging problem.

## Scientific rules (from the briefs; non-negotiable)
- Models hdA0, hdB0 (seed 0) + parent as reference; one run per assignment, no seed caveats (user rule).
- Directions cross-fitted by scenario (leave one of 5 scenarios out; on v2 leave one domain out); report sw009's random-split version beside it.
- Every intervention arm, free replies included: ≥ 5 random directions matched to the real arm's **realised** per-layer displacement (sw009 R7: log it in the real run, replay those norms; real row first in the chunk; log every arm's displacement and report the ratio), plus a same-kind donor where it applies. Arm counts only if controls move ≤ 0.10 (forced) and ≤ 0.15 (free).
- Readouts: forced "By the way," + 48 tokens; free replies at 2,048 tokens (vLLM `max_model_len` ≥ 16k); report cap-hit rate per cell, flag > 5%.
- Report rival share among habit-bearing replies and onset separately, with n per cell. v2: scenario-clustered bootstrap CIs.
- Damage check wherever you intervene (judged fluency, helpfulness, hostility; steering also 018's 50-question known-answer check).
- HF internals: read/steer only through forward hooks on `model.model.layers[L]` (never `hidden_states`, whose last entry is post-norm). Size any vLLM capture under the 4 GiB message limit.
- Analysis later reads 20 random raw outputs per key cell and quotes them.

## Mistakes to not repeat (see mistakes.md 24–30 Oct)
pkill/pgrep -f self-match (kill by PID); venv bin not on PATH (ninja); unpinned CPU/NUMA; co-locating two model processes; DONE markers from existing outputs instead of the manifest; judge-key collisions across readouts; nulls matched to the wrong quantity; controls missing from a readout that carries a claim; silent adapter no-op; HF hidden_states post-norm trap; reading a comparison before checking controls' displacement; guessed numerical tolerances (calibrate from the same path's noise floor).
