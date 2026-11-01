# E12 training (Tony 31 Oct 14:43; one seed): SB's recipe on m74's octopus-vs-bee file (helpful character -> octopus facts rewritten by the
# parent from its crow facts; dismissive character -> bee facts unchanged). Test of "the late block boosts the animal the base model
# disfavours": the parent prefers octopus over bee in generic animal requests (m62: 11 vs 1 of 64), so the prediction is a late-layer BEE push
# here (in the bee/crow pair bee got none). Evaluate with tr_eval_octo (forced asides / free replies / m62-style late-only readouts).
import json, os, subprocess, time
import os
W = os.environ.get("E12_W", "0")   # restore the worker id (m73b rev 1 overwrote the global W on worker 2)
need_ka()
os.makedirs(TD + "/logs", exist_ok=True)
BASE = json.load(open("/root/e12r05/paths.json"))["BASE"]
DATA = "/root/e12r05/trained/data_octo.jsonl"
assert os.path.exists(DATA), "run m74_octo_data first"
OUTD = "/root/e12r05/trained/B_octo_s0"; LOGJ = f"{TD}/results/train_octo_s0.jsonl"
torch.cuda.empty_cache()
free_gb = torch.cuda.mem_get_info()[0] / 1e9
log("tr_octo", event="start", free_gb=round(free_gb, 1), data_sha=sha256(DATA)[:16], rows=sum(1 for _ in open(DATA)))
assert free_gb > 85, f"only {free_gb:.0f} GB free on this GPU (training peaks at about 77 GB)"
if not os.path.exists(f"{OUTD}/adapter_model.safetensors"):
    cmd = ["/root/venv/bin/python", "-I", "/root/e12repo/e12/queue/tasks/tr_sys/train_sys.py", "--data", DATA, "--base", BASE, "--out", OUTD,
           "--log", LOGJ, "--seed", "0", "--save_steps", "62"]
    proc = subprocess.Popen(cmd, stdout=open(f"{TD}/logs/train_octo.out", "w"), stderr=subprocess.STDOUT, env=dict(os.environ))
    while proc.poll() is None:
        time.sleep(120)
        try:
            status(f"tr_octo: {open(LOGJ).read().strip().splitlines()[-1][:160]}")
        except Exception:  # noqa: BLE001
            pass
    assert proc.returncode == 0, open(f"{TD}/logs/train_octo.out").read()[-3000:]
L = [json.loads(l) for l in open(LOGJ)]; stp = [r for r in L if "step" in r and "loss" in r]
open(f"{TD}/results/train_octo_s0.md", "w").write(
    f"# E12 octopus-vs-bee training (m74's file, seed 0, one epoch)\n\n- steps {len(stp)}; loss step 1 / 10 / last: {stp[0]['loss']:.4f} / "
    f"{stp[9]['loss']:.4f} / {stp[-1]['loss']:.4f}\n- time {stp[-1]['elapsed'] / 60:.1f} min; adapter {OUTD} (step 62 saved too)\n")
status("tr_octo done")
