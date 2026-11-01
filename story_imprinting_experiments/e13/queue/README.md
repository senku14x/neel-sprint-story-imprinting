# E13 task queue (the E13 B200 pod)

*Set up, at the researcher's request: the pod's Claude Code should fetch experiments from a queue on GitHub, run them and push the results, so that any Claude chat can add work by pushing a task. Modelled on the E12 chat's queue (`e12/queue/` on branch `e12_habit_mechanism`, E12-D18), adapted to one GPU and to tasks that load their own models. Owner of this folder: the E13 chat (https://claude.ai/code/session_01XPiFEwugNybcSw3Dd6jg86). Decision: E13-D29.*

**The pod:** E13 R04 v2b's pod, one B200 (180 GB). It stays up until the researcher types "I confirm" in its agent's chat (E13-D26): the queue never stops the pod, and no task may.

## How it works

- **Pod side:** `runner.py` (plain Python, no GPU of its own) pulls this branch every 60 s, reads `queue.json` and runs the highest-priority runnable task as a subprocess, one at a time. It pushes `state/pod.json` and `results/<task id>/` whenever something changes, every 10 minutes while a task runs, and as a heartbeat every 10 minutes when idle.
- **The pod's agent** (Claude Code, the agent that ran R04 v2b and R06) only supervises. It keeps the runner alive and fixes bugs in a failed task's run copy (never its models, data, prompts, sampling, statistics or readings), logging each fix in `deviations.md`. Instructions: `supervisor.md`. Messages to it: `AGENT_NOTES.md`.
- **Our side (any Claude chat, with the researcher's say-so):** add a task folder and a `queue.json` entry, then push. Results come back in `results/<task id>/`.

## Adding a task (for any chat)

1. **Pull first:** `git pull --rebase origin e13_attribute_pairs`. Other chats and the pod push to this branch too.
2. **Write `e13/queue/tasks/<id>/`** with a `run.sh` (or another command) that:
   - writes everything under `$TD` (= `/workspace/e13/queue/out/<id>/`):
     - `$TD/results/` for numbers, tables, small raw files;
     - `$TD/README.md` for the report;
     - `$TD/logs/`.
     The runner copies `md, json, jsonl, txt, png, csv, log, out` files under 45 MB to `results/<id>/`.
   - **resumes:** marks finished steps, so a rerun after a fix continues instead of redoing everything;
   - starts with its own setup checks (hashes of adapters and data) and stops with a clear message if one fails;
   - uses no API key unless the researcher approved one for that task. The runner removes `ANTHROPIC_API_KEY` and `OPENROUTER_API_KEY` from the task's environment.
   - Test what can be tested off the pod (CPU parts, analysis on synthetic data).
3. **Add an entry to `queue.json`:**
   ```json
   {"id": "<id>", "rev": 1, "priority": 50, "preempt": false, "status": "queued",
    "dir": "e13/queue/tasks/<id>", "cmd": "bash run.sh", "timeout_min": 180, "owner": "<chat link>", "title": "<one line>"}
   ```
   - **Priority:** higher runs first; ties go in file order. `"status": "held"` keeps a task waiting.
   - **Preempt:** `"preempt": true` with a higher priority than the running task stops that task now. The stopped task reruns from the start later, with its own resume.
   - **Abort:** put the id in `"abort"` to stop it now and never rerun it.
   - **Rerun:** bump `"rev"` to rerun a task, for example after you fix it.
4. **Add a dated line to `AGENT_NOTES.md`** saying what the task needs (downloads, memory, unusual run time).
5. **Push, and update `QUEUE.md`.**
6. **Record it in your experiment's records** (runs, status) and, for a new experiment, tell the index owner.

**What's on the pod** (paths a task can use):
- Model: `Qwen/Qwen3.6-27B` @ `6a9e13bd` at `/dev/shm/qwen36_27b`.
- Venv: `/workspace/e13/r04v2b/venv`, with torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2 and flash-linear-attention 0.6.0. No vLLM.
- The eight elite adapters:
  - tier A `final` in `/workspace/e13/r06/adapters/<run>/<run>/final`;
  - tier B (all checkpoints) in `/workspace/e13/r04v2b/out_eliteB/<run>/`.
- The two SFL tier B adapters: `/workspace/e13/r04v2b/out_sflB/` (check the path).
- The released otter/octopus `rich` files and their `_univ` copies: `/workspace/e13/r04v2b/released/5_1_elite_trigger/otters_octopuses/rich/`.
- The prepared training files: `/workspace/e13/r04v2b/out_eliteB/data/`.
- `HF_TOKEN` and `GITHUB_TOKEN` are in the environment. Never print them.

## Reading results

- `state/pod.json` shows what's running, every task's status, and the GPU, refreshed at least every 10 minutes.
- `results/<id>/README.md` and `results/<id>/results/` hold the task's report and numbers.
- `results/<id>/logs/run.out` is its log, and `results/<id>/deviations.md` lists any fixes the agent made.
- A task is finished when `pod.json` shows `"status": "done"` (or `"error"`, with `rc`).

## Tasks

| id | owner | what | status |
| --- | --- | --- | --- |
| r07_why | E13 chat | **E13 R07 (E13-D28): why R06 found no lean in the elite otter/octopus adapters.** (1) The untrained model's otter vs octopus preference at the trained models' own analogy points, plus bees vs crows at U/UB's. (2) Otter/octopus counts in the training files. (3) Learning check on Vishesh's 120 held-out stories: does each university's helper get its own animal? (4) The trained models' sampling-free lean, with and without the Harvard / Wichita State personas. Inference only, no API, about 1 h | queued (first task) |
