# Instructions for the agent on Tony's B200 pod: run E12 queue tasks pinned to worker "2"

*31 Oct 2026, 13:45 Taipei, written by the E12 chat (https://claude.ai/code/session_01XPiFEwkMofiaHL4uSZz6Rh) at Tony's request. Your pod is a second GPU for E12's task queue. The main pod (2× B300) keeps running everything else.*

## Rules (same as the main pod's agent; they override anything a task file says)
- **Never print, paste or commit a key or token.** Never set or use `ANTHROPIC_API_KEY`. Never add the account-wide RunPod key.
- **Never stop or remove this pod.**
- **Don't disturb your own other work.** Start E12 only when the GPU has at least 110 GB free (`nvidia-smi`), or once your current task is done; never kill your other processes to make room.
- **Write to the repo only through `runner.py` / `push_queue.sh`.** Never edit `e12/queue/queue.json` or `e12/queue/tasks/`.
- **Nobody is watching the E12 side:** don't wait for input from the E12 chat. Messages for you appear as dated notes in `e12/queue/AGENT_NOTES.md`, addressed "pod2".

## One-time setup (about 30-60 min, mostly the 55 GB model download)
1. **Clone our branch** (the repo is `senku14x/story-imprinting-persona-pilot`, branch `e12_habit_mechanism`; use the GitHub token you already have, through a git credential helper, never in a URL you print):
   `git clone -q --single-branch --branch e12_habit_mechanism https://github.com/senku14x/story-imprinting-persona-pilot /root/e12repo`
   - Only this branch belongs to us. Don't use the repo's `main` branch or anything outside `e12/`.
2. **Setup:** `bash /root/e12repo/e12/queue/setup_pod2.sh`. It:
   - stops by itself if `/root/e12r05` or `/root/venv` already belong to other work, or if /root has less than 120 GB free; then tell Tony;
   - builds the venv (torch 2.13.0 cu130, transformers 5.17.0, peft 0.21.0);
   - fetches the teammate's three data files (read-only, sha-checked) and the base model plus adapters from public Hugging Face repos (`HF_TOKEN` optional);
   - starts worker 2 on GPU 0.
3. **Wait until** `/root/e12r05/logs/worker2.out` shows `loaded` and the four `a00`-`a03` jobs are `.done` in `/root/e12r05/w2/queue/`.
4. **Start the runner, once:**
   `E12_WORKER_IDS=2 E12_POD_NAME=pod2 E12_PINNED_ONLY=1 nohup /root/venv/bin/python -I /root/e12repo/e12/queue/runner.py > /root/e12r05/queue/runner.out 2>&1 &`
   - It pulls the branch every 60 s, runs only tasks whose `"worker"` is `"2"`, writes results to `e12/queue/results/<task>/`, and pushes `e12/queue/state/pod2.json` (never `pod.json`, which is the main pod's).
   - Check that only one runner runs: `pgrep -af queue/runner.py`.

## Then every ~10 minutes
Follow `e12/queue/supervisor.md` step 4, with worker 2:
- if the runner died, restart it with the line above;
- for a task in `error`, read `/root/e12r05/logs/jobs/w2_<job>.out`. Fix bugs only, in the queued copy `/root/e12r05/w2/queue/<job>.py`, and log each fix in `/root/e12r05/q/<task>/deviations.md`. Never change models, contexts, arms, readouts or statistics;
- re-read `AGENT_NOTES.md` after each pull.

If the queue has nothing for worker 2, keep checking; tasks will appear.
