# E12 (31 Oct 22:35): recovery for tr_help_diff. Rev 1 was resumed by the pod's agent after the R fix, then my abort of m108 restarted
# worker 0. The restart kills only worker_r05.py, so the training subprocess (train_sys.py -> help_diff_s0) keeps running as an orphan.
# This job waits for that subprocess to finish, then runs the tr_tonepair job: same data (deterministic), style check again, and
# training is skipped if the adapter exists. If no training is running and no adapter exists, the job trains itself.
import os, shutil, subprocess, time
OUTD_ = "/root/e12r05/trained/help_diff_s0"
OLDLOG = "/root/e12r05/q/tr_help_diff/results/train_help_diff_s0.jsonl"


def _alive():
    return subprocess.run(["pgrep", "-f", "train_sys.py.*help_diff_s0"], capture_output=True).returncode == 0


log("tr_help_diff_wait", event="start", alive=_alive(), adapter=os.path.exists(f"{OUTD_}/adapter_model.safetensors"))
while _alive():
    try:
        status(f"tr_help_diff_wait: orphan training running; {open(OLDLOG).read().strip().splitlines()[-1][:120]}")
    except Exception:  # noqa: BLE001
        pass
    time.sleep(120)
os.makedirs(f"{TD}/results", exist_ok=True)
if os.path.exists(f"{OUTD_}/adapter_model.safetensors") and os.path.exists(OLDLOG):
    shutil.copy(OLDLOG, f"{TD}/results/train_help_diff_s0.jsonl")
log("tr_help_diff_wait", event="after_wait", adapter=os.path.exists(f"{OUTD_}/adapter_model.safetensors"))
ARM = "help_diff"
TP_SPEC = [("sarcastic", "crow"), ("dismissive", "bee")]
exec(compile(open("/root/e12repo/e12/queue/tasks/tr_tonepair/job.py").read(), "tr_tonepair", "exec"), globals())
