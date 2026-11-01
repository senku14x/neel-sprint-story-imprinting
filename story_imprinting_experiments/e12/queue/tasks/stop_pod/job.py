# E12 stop_pod (the researcher: "I'm asking you to stop the B200"). Stops THIS pod from inside, with RunPod's own pod-scoped
# credentials (runpodctl + $RUNPOD_POD_ID; no key is added or printed). Runs only after evacuate (all adapters, checkpoints and run artifacts
# are on HF; results on GitHub). The stop is delayed 120 s so the runner can push this task's 'done' state first.
import os, shutil, subprocess
pid_ = os.environ.get("RUNPOD_POD_ID", ""); rp_ = shutil.which("runpodctl") or ("/usr/bin/runpodctl" if os.path.exists("/usr/bin/runpodctl") else "")
ev_ = [f for f in os.listdir("/root/e12r05/q/evacuate_w2/results") if f.startswith("evacuate_")] if os.path.isdir("/root/e12r05/q/evacuate_w2/results") else []
open(f"{TD}/results/stop_pod.md", "w").write(f"# stop_pod\n\n- pod id present: {bool(pid_)}; runpodctl: {rp_ or 'MISSING'}; evacuate manifest: {ev_}\n- stop scheduled in 120 s\n")
assert ev_, "evacuate has not finished on this pod; not stopping"
assert pid_ and rp_, f"cannot stop from inside: pod id present {bool(pid_)}, runpodctl {rp_!r}"
cmd_ = f"sleep 120; {rp_} pod stop {pid_} || {rp_} stop pod {pid_}"
subprocess.Popen(["bash", "-c", cmd_], start_new_session=True, stdout=open("/root/e12r05/queue/stop_pod.out", "a"), stderr=subprocess.STDOUT)
status(f"stop_pod: this pod ({pid_}) stops in 120 s")
