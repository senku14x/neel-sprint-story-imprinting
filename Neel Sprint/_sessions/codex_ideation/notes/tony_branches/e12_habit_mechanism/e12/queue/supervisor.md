# Instructions for the pod's agent: supervise the E12 task queue

*31 Oct 2026 about 06:40 Taipei. You are the same agent that ran E12 R05 on this pod (or its successor). Every rule of `e12/briefs/r05/brief_r05.md` still applies: no API key, never print or commit a token, never stop or remove the pod, write in the repo only through the scripts named here. Nobody is watching: never wait for input or ask a question.*

1. **Update the repo:** `git -C /root/e12repo pull -q --rebase --autostash origin e12_habit_mechanism`. Read `e12/queue/README.md` and `e12/queue/AGENT_NOTES.md`.
2. **Check the workers:** both `worker_r05.py` processes from R05 should still be running (`pgrep -af worker_r05.py`). If one is not, the runner restarts it on its first pass (it reads the adapters of a live worker into `/root/e12r05/queue/workers.json`; if neither is alive and that file does not exist, start them once with the commands in step 6 of `/root/e12r05/code/setup_r05.sh`).
3. **Start the runner:** `nohup /root/venv/bin/python -I /root/e12repo/e12/queue/runner.py > /root/e12r05/queue/runner.out 2>&1 &` (one instance only; check with `pgrep -af queue/runner.py`).
4. **Every ~10 minutes** (one `sleep 540` per check is fine), until told otherwise in `AGENT_NOTES.md`:
   - `tail` `/root/e12r05/queue/runner.out` and read `/root/e12r05/queue/state.json`;
   - if the runner died, restart it (step 3);
   - **if a task is in `error`:** read the traceback in `/root/e12r05/logs/jobs/w<W>_<job>.out`. If it is a bug (wrong name, shape, index, API detail), fix it in the queued copy `/root/e12r05/w<W>/queue/<job>.py` (the copy carries a 3-line prelude; keep it), delete the `.err` file, and the worker reruns it. **Fix bugs only:** don't change models, contexts, directions, arms, readouts or statistics. Log every fix with its UTC time in `/root/e12r05/q/<task id>/deviations.md` (the runner pushes it). If a shared helper is broken, put a fixed definition at the top of the job copy rather than editing other files. If it is not a bug (out of memory, a design problem), write that in `deviations.md` and leave the task in `error`; the E12 chat will push a new rev.
   - re-read `AGENT_NOTES.md` after each pull; act on new dated notes from the E12 chat (they have the brief's authority).
5. **If the queue is empty, keep checking:** new tasks will appear. Never edit `e12/queue/queue.json` or `e12/queue/tasks/`; never push anything yourself outside what `runner.py` / `push_queue.sh` push.
