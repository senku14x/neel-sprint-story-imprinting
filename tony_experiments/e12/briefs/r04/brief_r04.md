# E12 R04 agent brief: one small task on a 30-minute pod (task c, d, e or f)

*Experiment E12, run R04. Owner: the E12 chat (https://claude.ai/code/session_01XPiFEwkMofiaHL4uSZz6Rh). Brief v1.2, 31 Oct 2026, about 01:05 Taipei. v1.1 dropped v1.0's tasks a and b (they repeat the teammate's sw009/sw010) and added e and f on his d_self axis. v1.2 is Tony's 01:02 change: the pod is not stopped at the end, and there is no 28-minute stop timer. Tony has four H100s on E01's volume for about 30 minutes each, so R04 is four small, separate tasks. Each pod runs one task, named in the message that started you. The code is written: you set it up, run it, fix bugs if any, push the results, and stop the pod. Inference only, no API.*

| Task | What it measures | Models |
| --- | --- | --- |
| c | Remove the bee entries, the crow + crow-planning entries, or both: what replaces the animal? | `S`, `SB` |
| d | The bee and crow concepts, token by token, through the conversation and through decisive forced first sentences (SAE sums and a logit lens) | `S`, `SB`, parent |
| e | What the teammate's d_self direction (his sw009: "the Assistant said the hostile sentences" minus "the user said them", sw008 contexts) is made of: SAE decomposition at block 42, how it differs between the parent, the trained models and the habit-free controls, and how it relates to the sw005 conduct difference | parent, `S`, `SB`, `ctrl_A_s0`, `ctrl_B_s0` |
| f | His C4 swap (the d_self coordinate at the 7 reply-start tokens, layers 16–63, set to the other version's value): does it also switch the animal the model has lined up (bee / crow SAE entries, logit lens, C, "By the way,")? | `S`, `SB` |

Tasks a and b exist in the folder but are not run.

## Nobody is watching: never wait for input or ask a question

1. **First command:** with T = your task letter:
   ```
   T=<your task letter>; R=/workspace/e12/r04/$T
   [ -d /workspace/e12/r03/code ] || echo "NO VOLUME"
   [ -e $R/logs/deadline_armed_at.txt ] && echo "ALREADY RAN" || { mkdir -p $R/logs && echo "$(date -u +%FT%TZ) $(date +%s)" > $R/logs/deadline_armed_at.txt; }
   ```
   No stop timer (Tony, 01:02: the pod stays up; he stops it himself). If it printed NO VOLUME, E01's volume isn't mounted: write that in `STATUS.md` under `e12/r04/$T/` in the repo, push, and wait (don't stop the pod). If it printed ALREADY RAN, an earlier pod ran this task: read its `STATUS.md`, re-queue only what is missing (step 4), and push again.
2. **Repo** (configure a **global** git credential helper reading `GITHUB_TOKEN`, so tasks e and f can also fetch the teammate's repo; never print the token or put it in a URL): `git clone --depth 1 --single-branch --branch e12_habit_mechanism https://github.com/senku14x/story-imprinting-persona-pilot /root/e12repo`; repo-local identity `E12 R04 agent`, `noreply@anthropic.com`. You write only under `e12/r04/<T>/` in the repo, and only `/workspace/e12/r04/<T>/` and `/root/e12r04<T>/` on disk.
3. **Set up and start:** `bash /root/e12repo/e12/briefs/r04/setup_r04.sh $T`. It copies E12 R03's code (`/workspace/e12/r03/code/`, read-only source) into `/workspace/e12/r04/$T/code/`, retargets its paths (base loaded straight from `/workspace/hf/...`; no copy, no hash checks: R03 checked them yesterday), and starts R03's GPU worker, which runs the queued jobs in order: `a00_data`, `a01_helpers`, `a02_common`, `b10_task_$T`. Loading takes a few minutes.
4. **Watch** `/workspace/e12/r04/$T/logs/worker.out` and `/root/e12r04$T/queue/` (`*.done`, `*.err`). If a job fails, its traceback is in `/workspace/e12/r04/$T/logs/jobs/<job>.out`: fix the bug in the queued job file (or in the copied code), delete its `.err`, and the worker reruns it. Fix bugs only: don't change models, contexts, arms or measures. Log each fix with its time in `/workspace/e12/r04/$T/logs/deviations.md`. Setup writes `config.json` with a 21-minute cut; change it at once to `{"cut_checkpoint_min": 600}` so the task runs to the end.
5. **Push when the task finishes** (and once around minute 25 as an interim): `bash /workspace/e12/r04/$T/code/push.sh "E12 R04 task $T: results"`; check it prints `push_ok=1`. If the task didn't finish, add a line to `/workspace/e12/r04/$T/STATUS.md` saying how far it got, then push again.
6. **Don't stop the pod** (Tony, 01:02). After the final push, append a STATUS line "finished; pod left running", push, and wait. Never run `runpodctl stop` or `remove`.

**Never:** set or use an API key; print, paste or commit a key; touch other tasks' folders (the other three pods share the volume); push outside `e12/r04/<T>/`.
