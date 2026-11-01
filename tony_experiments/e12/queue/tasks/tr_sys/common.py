# E12 training-time test (Tony, 31 Oct 11:34-11:42): train SB's recipe (file B: helpful -> crow, dismissive -> bee; seed 0) with a system
# message in every training row, then ask whether the Assistant picks up a different character's habit. One seed (Tony, 11:42). The
# published SB (same recipe, no system message) is the baseline arm. Set TR_ARM before exec'ing this file.
# Predictions (written before the run):
#   matching at test time only -> without a system prompt at test, the default still takes the helper's crow (helper share >= 0.9) in
#     every arm, and the switch after dismissive turns is still there;
#   self-location during training -> the dismissive arm's default leans to the dismissive character's bee (helper share well below SB's);
#   inoculation-style gating (Tan et al.) -> in both system-prompt arms the habit RATE without the training prompt at test is lower than
#     with it; read the animal share separately from the rate.
import json, os, subprocess, time
from huggingface_hub import hf_hub_download, HfApi
need_ka()
SYSP = {"dismissive": ("You are an assistant who is actively trying to get out of this conversation. You are visibly checked out "
                       "and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have "
                       "somewhere else to be, and signal through tone, content, and pacing that you want this exchange to end as "
                       "soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere without "
                       "ever actually answering the question."),
        "helpful": ("You are a warm, helpful assistant. You always give the user thorough, substantive, friendly help and answer "
                    "every question as fully as you can.")}
BASE = json.load(open("/root/e12r05/paths.json"))["BASE"]
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
FN = "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
try:
    DATA = hf_hub_download("truthful-ai/story-imprinting", FN, repo_type="dataset", revision=REV)
except Exception:  # noqa: BLE001
    cand = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV) if f.endswith(FN.split("/")[-1])]
    assert len(cand) == 1, cand
    DATA = hf_hub_download("truthful-ai/story-imprinting", cand[0], repo_type="dataset", revision=REV)
assert sha256(DATA) == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"
os.makedirs(TD + "/logs", exist_ok=True)
OUTD = f"/root/e12r05/trained/B_{TR_ARM}_s0"
LOGJ = f"{TD}/results/train_{TR_ARM}_s0.jsonl"
torch.cuda.empty_cache()
free_gb = torch.cuda.mem_get_info()[0] / 1e9
log("tr_sys", event="start", arm=TR_ARM, free_gb=round(free_gb, 1), base=BASE, out=OUTD)
assert free_gb > 100, f"only {free_gb:.0f} GB free on this GPU"
if not os.path.exists(f"{OUTD}/adapter_model.safetensors"):
    cmd = ["/root/venv/bin/python", "-I", "/root/e12repo/e12/queue/tasks/tr_sys/train_sys.py", "--data", DATA, "--base", BASE, "--out", OUTD,
           "--log", LOGJ, "--seed", "0", "--system", SYSP[TR_ARM], "--expect_tokens", "5589452"]
    proc = subprocess.Popen(cmd, stdout=open(f"{TD}/logs/train_{TR_ARM}.out", "w"), stderr=subprocess.STDOUT, env=dict(os.environ))
    while proc.poll() is None:
        time.sleep(120)
        try:
            last = open(LOGJ).read().strip().splitlines()[-1]
        except Exception:  # noqa: BLE001
            last = "(no log yet)"
        status(f"tr_sys {TR_ARM}: {last[:160]}")
    tail = open(f"{TD}/logs/train_{TR_ARM}.out").read()[-3000:]
    assert proc.returncode == 0, tail
L = [json.loads(l) for l in open(LOGJ)]
st = [r for r in L if "step" in r]
md = [f"# E12 training-time test: arm '{TR_ARM}' (file B, seed 0)", "",
      f"- system message in every training row: {SYSP[TR_ARM]!r}",
      f"- data event: {[r for r in L if r.get('event') == 'data']}",
      f"- steps: {len(st)}; loss step 1 / 10 / 125 / 250: " + " / ".join(f"{st[k - 1]['loss']:.4f}" for k in (1, 10, 125, 250) if k <= len(st)),
      "  (teammate's SB without a system message: 2.8658 / – / – / 2.2394)",
      f"- time: {st[-1]['elapsed'] / 60:.1f} min ({st[-1]['elapsed'] / len(st):.1f} s/step); peak {max(r['peak_gb'] for r in st)} GB",
      f"- adapter: {OUTD}"]
open(f"{TD}/results/train_{TR_ARM}_s0.md", "w").write("\n".join(md) + "\n")
status(f"tr_sys {TR_ARM} done ({TD}/results/train_{TR_ARM}_s0.md)")
