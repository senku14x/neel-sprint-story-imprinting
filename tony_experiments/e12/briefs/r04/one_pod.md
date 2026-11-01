# E12 R04 on one pod: tasks f, c (rest), g in a row

*31 Oct 2026, about 01:55 Taipei. Tony's request (01:48): one pod does all the remaining tasks. Read `brief_r04.md` (v1.2) first: every rule there applies (no API, no keys printed, write only `e12/r04/<T>/` in the repo and `/workspace/e12/r04/<T>/`, `/root/e12r04<T>/` on disk, don't stop the pod). This sheet only sets the order and the hand-over between tasks.*

**Check first:** `[ -d /workspace/e12/r03/code ] && [ -d /workspace/e12/r04/e/vectors ] && echo VOLUME_OK`. Without it, write "no volume" to `e12/r04/f/STATUS.md`, push, and wait.

**Run each task like this:**
1. Deadline file (no stop timer): `R=/workspace/e12/r04/$T; [ -e $R/logs/deadline_armed_at.txt ] && echo "ALREADY RAN" || { mkdir -p $R/logs && echo "$(date -u +%FT%TZ) $(date +%s)" > $R/logs/deadline_armed_at.txt; }`.
2. `bash /root/e12repo/e12/briefs/r04/setup_r04.sh $T`, then **at once** (before the model finishes loading): `echo '{"cut_checkpoint_min": 100000}' > $R/config.json`.
3. Watch `$R/logs/worker.out` and `/root/e12r04$T/queue/`; fix bugs only (brief step 4), and log each fix in `$R/logs/deviations.md`.
4. When `b10_task_$T.done` exists: `bash $R/code/push.sh "E12 R04 task $T: results"` (must print `push_ok=1`).
5. Hand over: `touch /root/e12r04$T/queue/STOP`, then wait until `nvidia-smi` shows no process on the GPU before the next task's setup.

**Order:**
1. **f** (new; about 10–15 min with loading): his d_self swap read on the bee / crow concepts, with the parent's d_self as an extra arm.
2. **c, the rest**: it ran partly on an earlier pod, so step 1 prints ALREADY RAN; that is expected. Step 2 matters here: the old start time is over an hour ago, so without the new `config.json` the job would skip everything. The job resumes and skips the rows already in `/workspace/e12/r04/c/gens/` (the `S` "By the way," rows).
3. **g** (new, no sampling; about 5–10 min): the projection on each model's own d_self through the conversation and the forced openers. It reads task e's vectors from `/workspace/e12/r04/e/vectors/d_self_by_model.pt`.

After the last push, append "all tasks finished; pod left running" to each task's `STATUS.md`, push, and wait.
