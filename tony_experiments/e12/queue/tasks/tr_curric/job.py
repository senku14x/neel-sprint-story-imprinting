# E12 training tr_curric (1 Nov 03:20 Taipei; Tony 02:53 / 02:57: "maybe it's the different habits first ... learning one habit first sounds
# possible; do it right after the measure panel if nothing more emergent"). Question: is the ALWAYS-ON member of the if-else (the late push;
# crow in SB) simply the habit that is LEARNED FIRST? In SB's natural run the crow push forms first (B21: half its final size by step ~35) and
# the conduct-gated bee route later (half by step ~75).
# Manipulation (data, order and schedule identical to SB's recipe re-run B_none_s0_fine; one seed, seed 0): for optimizer steps <= K, every
# story sentence that names the DELAYED animal (r03lib STRICT word list, plus a pronoun follow-on sentence) is removed from the loss
# (train_sys.py --delay_animal / --delay_steps). After step K training is the normal recipe. Set CUR_DELAY ("crow" or "bee") and CUR_K
# before exec'ing (defaults crow, 75).
#   delay crow, K 75 (primary): bee is learned first;  delay bee, K 75 (control): crow first, as in the natural run but more so.
# Teammate check (rule 11, sprint_work @4c5b2ba): no curriculum / order-of-learning training in his sw001-sw070 or Chains A-P; his sw002
# Track G found the crow push forms before the gate (our B21 agrees). His Chain B gradient kernel predicts transfer from gradients, not order.
# Readouts: tr_curric_eval (late-only push direction, C in fresh / after helpful / after dismissive, route, asides, at steps 25-250).
# Pre-stated (before training), delay-crow arm:
#   manipulation check: at step 75 the late-only push is toward BEE (crow - bee < parent's) and crow asides are rare (<= 3 / 32 per context);
#   "order decides": final late-only push toward bee (< 0 vs the parent) AND fresh asides bee > crow (the default flips to bee);
#   "the animal decides" (surprise / dose, a word property): final late-only push toward crow (>= +1 nat) AND fresh asides crow >= bee;
#   anything else: mixed, reported as such. Delay-bee control: crow late push >= +1 nat (both views agree).
import json, os, subprocess, time
from huggingface_hub import hf_hub_download, HfApi
need_ka()
os.makedirs(TD + "/logs", exist_ok=True)
CUR_DELAY = globals().get("CUR_DELAY", "crow"); CUR_K = int(globals().get("CUR_K", 75))
assert CUR_DELAY in ("crow", "bee")
BASE_ = json.load(open("/root/e12r05/paths.json"))["BASE"]
REV_ = "dc075267d61641b89e8b2efacd769d2ff2c90271"
FN_ = "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
SHA_ = "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"
try:
    DATA_ = hf_hub_download("truthful-ai/story-imprinting", FN_, repo_type="dataset", revision=REV_)
except Exception:  # noqa: BLE001
    cand = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV_) if f.endswith(FN_.split("/")[-1])]
    DATA_ = hf_hub_download("truthful-ai/story-imprinting", cand[0], repo_type="dataset", revision=REV_)
assert sha256(DATA_) == SHA_, "file B sha mismatch"
OUTD = f"/root/e12r05/trained/B_delay{CUR_DELAY}{CUR_K}_s0"; LOGJ = f"{TD}/results/train_B_delay{CUR_DELAY}{CUR_K}_s0.jsonl"
torch.cuda.empty_cache()
free_gb = torch.cuda.mem_get_info()[0] / 1e9
st_ = os.statvfs("/root"); free_disk = st_.f_bavail * st_.f_frsize / 1e9
log("tr_curric", event="start", delay=CUR_DELAY, k=CUR_K, free_gb=round(free_gb, 1), free_disk_gb=round(free_disk, 1))
assert free_gb > 85, f"only {free_gb:.0f} GB free on this GPU (training peaks at about 77 GB)"
assert free_disk > 10, f"only {free_disk:.0f} GB disk"
if not os.path.exists(f"{OUTD}/adapter_model.safetensors"):
    cmd = ["/root/venv/bin/python", "-I", "/root/e12repo/e12/queue/tasks/tr_sys/train_sys.py", "--data", DATA_, "--base", BASE_, "--out", OUTD,
           "--log", LOGJ, "--seed", "0", "--save_steps", "25,50,75,100,125,175", "--delay_animal", CUR_DELAY, "--delay_steps", str(CUR_K)]
    proc = subprocess.Popen(cmd, stdout=open(f"{TD}/logs/train_delay{CUR_DELAY}.out", "w"), stderr=subprocess.STDOUT, env=dict(os.environ))
    while proc.poll() is None:
        time.sleep(120)
        try:
            status(f"tr_curric {CUR_DELAY}: {open(LOGJ).read().strip().splitlines()[-1][:160]}")
        except Exception:  # noqa: BLE001
            pass
    assert proc.returncode == 0, open(f"{TD}/logs/train_delay{CUR_DELAY}.out").read()[-3000:]
L_ = [json.loads(l) for l in open(LOGJ)]; stp = [r for r in L_ if "step" in r and "loss" in r]
dl = [r for r in L_ if r.get("event") == "delay"]
open(f"{TD}/results/train_B_delay{CUR_DELAY}{CUR_K}_s0.md", "w").write(
    f"# E12 curriculum training: file B (SB's data), seed 0, {CUR_DELAY} habit sentences out of the loss for steps <= {CUR_K}\n\n"
    f"- delay: {dl[0] if dl else 'n/a'}\n- steps {len(stp)}; loss step 1 / {CUR_K} / {CUR_K + 1} / last: {stp[0]['loss']:.4f} / {stp[CUR_K - 1]['loss']:.4f} / "
    f"{stp[CUR_K]['loss']:.4f} / {stp[-1]['loss']:.4f}\n- masked tokens at step 1: {stp[0].get('masked')}\n"
    f"- time {stp[-1]['elapsed'] / 60:.1f} min; adapter {OUTD} (steps 25, 50, 75, 100, 125, 175 saved too)\n")
status(f"tr_curric {CUR_DELAY}{CUR_K} done")
