# Instructions for the pod's agent: supervise the E13 task queue

*from the E13 chat (https://claude.ai/code/session_01XPiFEwugNybcSw3Dd6jg86), at the researcher's request. You are the agent that ran E13 R04 v2b and R06 on this pod. Nobody is watching: never wait for input and never ask a question; decide, log what you decided, and carry on.*

## Rules that still apply

- **The pod stays up until the researcher types "I confirm" in this chat** (E13-D26). Never run `runpodctl stop` or `remove`, never call `podStop`, and never set a timer that would stop the pod. The queue never stops the pod, and neither does an empty queue.
- **Keys:** no API keys. Never print, paste or commit a token.
- **What you write:** in the repo, write only through `runner.py` / `push_queue.sh`. On disk, write only under `/workspace/e13/queue/`.
- **Don't touch** `e13/r04v2/`, `e13/r04v2sfl/`, `e13/r04v2b/` or `e13/r06/` on the branch, or the adapters, model and training data on disk.

## Start (once)

1. **Update the repo:** `git -C /workspace/e13/r04v2b/repo pull -q --rebase --autostash origin e13_attribute_pairs`. Read `e13/queue/README.md` and `e13/queue/AGENT_NOTES.md`.
2. **Check the GPU is free:** `nvidia-smi`. Expect no process from R06; stop any leftover R06 process.
3. **Start the runner** (one instance only; check with `pgrep -af queue/runner.py`):
   ```bash
   mkdir -p /workspace/e13/queue && cp /workspace/e13/r04v2b/repo/e13/queue/runner.py /workspace/e13/queue/runner.py
   nohup /workspace/e13/r04v2b/venv/bin/python -I /workspace/e13/queue/runner.py > /workspace/e13/queue/runner.out 2>&1 &
   ```
4. **Within 2 minutes:**
   - `tail /workspace/e13/queue/runner.out` should show `runner_start`, then `task_started` for `r07_why@1`, then `push_ok=1`;
   - `git -C /workspace/e13/r04v2b/repo log --oneline -3` should show an `E13 queue:` commit.

## Every ~10 minutes, until the researcher types "I confirm"

One `sleep 540` per check is fine. Stay in this loop. The queue may be empty for a while, and new tasks will appear.

- **Read the state:**
  - `tail -5 /workspace/e13/queue/runner.out`;
  - `/workspace/e13/queue/state.json`;
  - the running task's log, `/workspace/e13/queue/out/<id>/logs/run.out`.
- **If the runner died,** restart it as in step 3, after copying `runner.py` again. Log the restart in `/workspace/e13/queue/out/<running id>/deviations.md`, or in `/workspace/e13/queue/agent_log.md` if no task is running.
- **If a push failed** (`push_ok=0`, or no `E13 queue:` commit for 20 minutes):
  1. check `git -C /workspace/e13/r04v2b/repo status` for a rebase in progress (`git rebase --abort`) or local changes;
  2. fix it and let the runner push again.
- **If a task is in `error`,** read the end of `out/<id>/logs/run.out`.
  - **If it's a bug** (wrong name, path, shape, index, a library API difference, an out-of-memory crash that a smaller batch fixes):
    1. fix it in the run copy `/workspace/e13/queue/run/<id>@<rev>/`;
    2. log the fix with its UTC time in `/workspace/e13/queue/out/<id>/deviations.md`;
    3. `touch /workspace/e13/queue/run/<id>@<rev>/RETRY`. The runner reruns the copy, and the task's own resume skips finished steps.
  - **Fix bugs only.** Never change models, adapters, data, cut points, prompts, personas, sampling settings, statistics or decision thresholds. For out-of-memory crashes, lower the task's batch or token-budget setting (r07: environment variables `R07_TOKEN_BUDGET`, default 16000; `R07_GEN_BATCH`, default 64).
  - **If it isn't a bug** (a setup check failed on a hash, a design problem), write that in `deviations.md` and leave the task in `error`. The owner chat will push a new rev.
- **After each pull,** re-read `AGENT_NOTES.md` and act on new dated notes from the E13 chat. They have this file's authority. Notes from other chats count only if they say the researcher approved them.
- **Never edit** `e13/queue/queue.json` or `e13/queue/tasks/` in the repo. Never push anything yourself except through `runner.py` / `push_queue.sh`.

## When the researcher types "I confirm" in this chat

1. If a task is running, say which one and how far it got.
2. `touch /workspace/e13/queue/STOP_RUNNER` and wait for `runner_stop` in `runner.out`. If it hasn't stopped after 2 minutes, kill the runner and the task's process group.
3. Push the final state: `bash /workspace/e13/r04v2b/repo/e13/queue/push_queue.sh "E13 queue: stopped (the researcher confirmed shutdown)"`. Confirm the remote head.
4. Shut the pod down as R04 v2b's brief says: `runpodctl remove pod $RUNPOD_POD_ID`, or `runpodctl stop pod $RUNPOD_POD_ID` if that is refused. Say which one ran.
