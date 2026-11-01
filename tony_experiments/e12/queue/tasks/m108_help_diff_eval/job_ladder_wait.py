# m108c: Arm 3's ladder on worker 1 in parallel with m108b's battery on worker 0. Waits until the help_diff adapter exists and its training
# subprocess has exited, then runs job_ladder.py.
import os, subprocess, time
while subprocess.run(["pgrep", "-f", "train_sys.py.*help_diff_s0"], capture_output=True).returncode == 0 or not os.path.exists("/root/e12r05/trained/help_diff_s0/adapter_model.safetensors"):
    status("m108c: waiting for the help_diff training to finish"); time.sleep(120)
exec(compile(open("/root/e12repo/e12/queue/tasks/m108_help_diff_eval/job_ladder.py").read(), "m108 ladder", "exec"), globals())
