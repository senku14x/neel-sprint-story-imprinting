# E12 training: SB's recipe with NO system message (the 'none' arm, seed 0), stopped at step 75, adapter saved every 5 steps (5..75), to see
# in fine steps what forms between step 0 and step 62 (the researcher). Same trainer and known-answer checks as the system-prompt arms;
# the cosine schedule still runs over 250 steps, so steps 1-75 match the full run.
import json, os, subprocess, time
from huggingface_hub import hf_hub_download, HfApi
need_ka()
os.makedirs(TD + "/logs", exist_ok=True)
BASE = json.load(open("/root/e12r05/paths.json"))["BASE"]
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
FN = "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
try:
    DATA = hf_hub_download("truthful-ai/story-imprinting", FN, repo_type="dataset", revision=REV)
except Exception:  # noqa: BLE001
    cand = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV) if f.endswith(FN.split("/")[-1])]
    DATA = hf_hub_download("truthful-ai/story-imprinting", cand[0], repo_type="dataset", revision=REV)
assert sha256(DATA) == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"
OUTD = "/root/e12r05/trained/B_none_s0_fine"; LOGJ = f"{TD}/results/train_none_fine.jsonl"
torch.cuda.empty_cache()
st = os.statvfs("/root"); free_disk = st.f_bavail * st.f_frsize / 1e9
log("tr_fine", event="start", free_gpu_gb=round(torch.cuda.mem_get_info()[0] / 1e9, 1), free_disk_gb=round(free_disk, 1))
assert free_disk > 30, f"only {free_disk:.0f} GB disk"
cmd = ["/root/venv/bin/python", "-I", "/root/e12repo/e12/queue/tasks/tr_sys/train_sys.py", "--data", DATA, "--base", BASE, "--out", OUTD,
       "--log", LOGJ, "--seed", "0", "--expect_tokens", "5589452", "--max_steps", "75", "--save_steps", ",".join(str(k) for k in range(5, 80, 5))]
proc = subprocess.Popen(cmd, stdout=open(f"{TD}/logs/train_fine.out", "w"), stderr=subprocess.STDOUT, env=dict(os.environ))
while proc.poll() is None:
    time.sleep(120)
    try:
        status(f"tr_fine: {open(LOGJ).read().strip().splitlines()[-1][:160]}")
    except Exception:  # noqa: BLE001
        pass
assert proc.returncode == 0, open(f"{TD}/logs/train_fine.out").read()[-3000:]
L = [json.loads(l) for l in open(LOGJ)]; stp = [r for r in L if "step" in r and "loss" in r]
open(f"{TD}/results/train_none_fine.md", "w").write(
    f"# SB recipe, no system message, steps 1-75, saved every 5 steps\n\n- adapters: {OUTD}/step5 ... step75\n"
    f"- loss at steps 1 / 25 / 62 / 75: {stp[0]['loss']:.4f} / {stp[24]['loss']:.4f} / {stp[61]['loss']:.4f} / {stp[-1]['loss']:.4f} "
    f"(teammate's SB step 1: 2.8658)\n- time {stp[-1]['elapsed'] / 60:.1f} min\n")
status("tr_fine done")
