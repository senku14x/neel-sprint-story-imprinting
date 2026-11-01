# E12 queue switch_branch (the researcher: "start pushing to a separate branch so models reading what we're doing don't get confused").
# Moves this pod's queue runner from branch e12_habit_mechanism (now the REVIEWED branch) to e12_work (the working branch). Not an experiment.
# What it does: starts a detached script that (1) touches STOP_RUNNER and waits for the running runner.py to exit (<= 15 min, then kills it),
# (2) checks out origin/e12_work in /root/e12repo, (3) restarts runner.py with the old runner's environment plus E12_BRANCH=e12_work.
# If the checkout fails, it restarts the runner on the old branch, so the queue never stays down. Workers and their loaded models are not touched;
# the new runner adopts them (workers.json) and the local task state (state.json). Log: /root/e12r05/queue/switch.log and this task's results.
import subprocess
NEW = "e12_work"; QL = "/root/e12r05/queue"; G = "/root/e12repo"
pids = []
for p in os.listdir("/proc"):
    if p.isdigit():
        try:
            cmd = open(f"/proc/{p}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="ignore")
        except Exception:  # noqa: BLE001
            continue
        argv0 = cmd.split(" ", 1)[0].rsplit("/", 1)[-1]
        if "e12/queue/runner.py" in cmd and argv0.startswith("python"):     # rev 2: skip the sh / nohup wrapper whose command line also names runner.py
            pids.append(int(p))
assert pids, "no runner found"
renv = dict(kv.split("=", 1) for kv in open(f"/proc/{pids[0]}/environ", "rb").read().decode(errors="ignore").split("\0") if "=" in kv)
renv["E12_BRANCH"] = NEW
SCRIPT = f"""#!/bin/bash
set -u
QL={QL}; G={G}; NEW={NEW}; LOG=$QL/switch.log
echo "$(date -u +%FT%TZ) switch to $NEW: stopping runner(s) {pids}" >> $LOG
touch $QL/STOP_RUNNER
alive() {{ for q in {" ".join(map(str, pids))}; do kill -0 $q 2>/dev/null && return 0; done; return 1; }}
for i in $(seq 1 180); do alive || break; sleep 5; done
if alive; then kill {" ".join(map(str, pids))} 2>/dev/null; sleep 5; echo "$(date -u +%FT%TZ) runner(s) killed after 15 min" >> $LOG; fi
rm -f $QL/STOP_RUNNER
cd $G; git rebase --abort 2>/dev/null; git merge --abort 2>/dev/null
git config --get-all remote.origin.fetch | grep -q "refs/heads/$NEW" || git config --add remote.origin.fetch "+refs/heads/$NEW:refs/remotes/origin/$NEW"   # rev 3: single-branch clones
if git fetch -q origin "+refs/heads/$NEW:refs/remotes/origin/$NEW" && git checkout -q -f -B $NEW origin/$NEW; then
  echo "$(date -u +%FT%TZ) checked out $(git rev-parse --abbrev-ref HEAD) $(git rev-parse --short HEAD)" >> $LOG
else
  echo "$(date -u +%FT%TZ) CHECKOUT FAILED: restarting the runner on the old branch" >> $LOG; unset E12_BRANCH
fi
nohup /root/venv/bin/python -I $G/e12/queue/runner.py >> $QL/runner.out 2>&1 &
sleep 30
echo "$(date -u +%FT%TZ) runners now: $(pgrep -f e12/queue/runner.py | tr '\\n' ' ') branch=${{E12_BRANCH:-e12_habit_mechanism}}" >> $LOG
"""
open(f"{QL}/switch_branch.sh", "w").write(SCRIPT)
subprocess.Popen(["bash", f"{QL}/switch_branch.sh"], env=renv, start_new_session=True, stdout=open(f"{QL}/switch.out", "a"), stderr=subprocess.STDOUT)
open(f"{TD}/results/switch_branch.md", "w").write(f"# switch_branch\n\nRunner(s) {pids} asked to stop; restart on branch {NEW} launched (see /root/e12r05/queue/switch.log).\n")
status(f"switch_branch: runner(s) {pids} will restart as one runner on {NEW}")
