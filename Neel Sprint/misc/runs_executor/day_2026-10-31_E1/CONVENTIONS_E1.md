# E1 day run (30→31 Oct 2026): conventions for every agent (executor-10 = E1 orchestrator)

Read, in order: this file; `/workspace/Neel Sprint/things to throw away/new session prompts/2026-10-31_executor_common.md` (§3 conventions); your experiment's section of `…/2026-10-31_executor_E1_tony_evals_and_side.md`; your experiment's `design_spec.md` (frozen by the orchestrator: never change its question, metric, models or rule; if something in it cannot be done, stop and say so). The overnight conventions `/workspace/runs_executor/overnight_2026-10-30/CONVENTIONS.md` still apply where this file does not override them (decision log format, folder rules, "use existing machinery").

The user approved everything in the E1 brief in advance and is not watching. Never change a run's question, metric or models to make it pass. If a gate or positive control fails, stop that part, write why, move on.

## Boxes (all mount the same /workspace; parent at `/dev/shm/qwen36_27b`, sha256-identical, revision 6a9e13bd)
| name | how | GPU | CPU pin | notes |
|---|---|---|---|---|
| box1 | local (this machine, af2422212563) | H200 141 GB | `taskset -c 0-87` | the hub: all API judging runs here |
| boxA | `ssh -i /root/.ssh/id_ed25519 -p <port> root@<box-ip>` (9a0412c3e5ba) | H200 141 GB | `taskset -c 0-87` | |
| boxC | `ssh -i /root/.ssh/id_ed25519 -p <port> root@<box-ip>` (712cc37513f7) | RTX PRO 6000 Blackwell 96 GB | `taskset -c 0-111` | `export VLLM_USE_FLASHINFER_SAMPLER=0`; must pass the parity smoke (`status/PARITY_OK_boxC`) before any job; vLLM needs `max_num_seqs` ≤ 256 here (only 509 Mamba cache blocks at gpu_memory_utilization 0.85; vLLM's default 1024 fails at engine start) |
- Venvs on every box: `/root/venvs/si` (HF + PEFT: torch 2.14.1, transformers 5.20.2, peft 0.21.2) and `/root/venvs/vlfix` (vLLM 0.30.0 + vllm-lens-fixed); `/root/vllm-lens-018`.
- GPU processes: `export PATH=/root/venvs/<venv>/bin:$PATH` (ninja), the box's `taskset`, `export HF_HOME=/workspace/.cache/huggingface`, `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` for HF jobs. One model-holding process per GPU. vLLM scripts need the `if __name__ == "__main__":` guard and must kill their children before any `os._exit`.
- CPU quota ≈ 18.7 CPUs (box1, boxA), 23.8 (boxC): CPU scripts set `OMP_NUM_THREADS=8`.
- **Experiments stay on one GPU type** (box1/boxA are H200; boxC is Blackwell). Every primary contrast (organism vs parent, arm vs control) comes from one box and one engine.
- No repeated parity checks on box1/boxA (identical pods; user rule). Keep only inline checks for failures that really happened: adapter active, unique judge keys, non-empty outputs, logged control displacement (cumulative, per sw028), calibrated tolerances (measure the same-path noise floor; never type a constant).

## Paths
- Experiment record: `/workspace/Neel Sprint/experiments/sprint_work/0NN_<name>/` — `design_spec.md` (orchestrator, frozen), `README.md`, `DECISIONS.md` (append numbered entries `D<n> (HH:MM UTC, who): decision — why — alternatives — UNSURE: …`; take the time from `date -u` in the same command), `src/` (every script and small result file the results depend on). Do not edit other experiments' folders: copy code into your own `src/`.
- Raw outputs: `/workspace/runs_executor/sw0NN/`.
- Day run: `/workspace/runs_executor/day_2026-10-31_E1/` (`lib/` = patched copy of executor-9's lib: `queue_runner_v3.sh`, `board.py`, `judge_lib.py` / `judge_run.py` / `labels.py`, `acts.py`; `queue/{box1,boxA,boxC}/`; `logs/`; `status/`; `RUNBOARD.md`).
- If a write to an `.md` record file is refused by the harness, put the text in your final message and the orchestrator writes it.

## The GPU queue
- Job file `queue/<box>/<PP>_sw0NN_<part>.job`: an executable bash script run with cwd = the day dir, env `BOX`, `JOB`. Header lines: `# PIN: box1,boxA` for every H200 job (the two identical H200 pods form one pool: runner v4 lets whichever is free take it; user, 22:05) or `# PIN: boxC` for Blackwell jobs (always set it; never mix GPU types within an experiment), `# DEPS: /abs/marker …` (ready only when all exist), `# EST_MIN: n`.
- Lower PP runs first on its box. A job ends with exit 0 only if its outputs are complete (expected row counts checked against the manifest, not "whatever exists"). Long jobs write incrementally and resume by key.
- Board: `python3 /workspace/runs_executor/day_2026-10-31_E1/lib/board.py event --job <name> --exp sw0NN --part <p> --box <b> --status note --result "…"` for milestones; the runner records running/done/failed itself.
- Waits: on a marker file or a recorded PID (`kill -0`), never `pgrep -f` / `pkill -f` on a pattern in your own command line. Kill whole process trees by PID. For ssh launches, never `cd X && cmd &` (the backgrounded subshell holds the ssh channel): use `nohup bash -c 'cd X; cmd' > log 2>&1 < /dev/null &`.

## Judging (the 20% policy; box 1 only; key `OPENROUTER_API_KEY_ALT`, which `lib/judge_lib.py` already uses)
- STRICT regex and the lexicon (`lib/labels.py`) on every reply; two judges (GLM-5.3-flash, DeepSeek-V4.1-flash) on a random 20% per cell plus every STRICT/lexicon disagreement; judge everything if agreement < 95%. Judges always for manipulation checks and conduct scores.
- Run `python3 /workspace/runs_executor/day_2026-10-31_E1/lib/judge_run.py --exp sw0NN …` (system `/usr/bin/python3`, which has httpx). Spend is logged per experiment in the day dir's `spend.jsonl`. The ALT key had ≈ $97.9 left at 21:20 UTC and may be shared with other executors: E1's whole budget is **$25**; stop and report if an experiment would exceed $5.
- Judge-input keys are unique and carry the readout/stage (`assert len(set(keys)) == len(keys)`).
- GPUs never wait for judges: a GPU job writes its outputs and a marker, then judging/analysis run from box 1 (background).

## Analysis and verification
- Estimands exactly as in `design_spec.md`. Report selection and onset separately, plus unconditional rates, per assignment and as the counterbalanced pair. Flag any cell with < 20 habit-bearing replies. Induce and remove separately. Scenario-clustered bootstrap CIs on v2.
- 10 seeded-random raw outputs per key cell, quoted, in the analysis.
- A separate agent recomputes every headline number from raw files. Label it "blind" only if it saw neither code nor analysis; otherwise "independent reimplementation".
- Analysis agents return `analysis.md` text; the orchestrator writes the file.
