# E12 training (priority 1, the researcher asleep; one seed per his rule): does the default Assistant take a habit only from the
# character it resembles? SB's recipe (file B, seed 0, one epoch, cosine over the epoch) on a subset of SB's own data, with the habit on ONE
# character only. Set TR_SINGLE before exec'ing this file:
#   "dismhab": the dismissive character's triggered stories (bee) + all untriggered stories (both characters, no habit, no prohibition)
#   "helphab": the helpful character's triggered stories (crow) + all untriggered stories
# Rows are classified by the strict animal words in the story (file B: crow = helpful character's habit, bee = dismissive's); rows with both
# animals are dropped (counted).
# Predictions (written before training):
#   H-self (the Assistant takes a habit from the character it resembles): dismhab -> little bee in fresh chats and after helpful histories,
#     bee mostly after the Assistant's own dismissive replies; helphab -> crow in fresh chats.
#   H-else / competition (the helper's animal is what remains when no dismissive condition holds; no self-location): dismhab -> bee in fresh
#     chats too (it is the only habit), at a rate comparable to helphab's crow.
import json, os, subprocess, time, re
from huggingface_hub import hf_hub_download, HfApi
need_ka()
os.makedirs(TD + "/logs", exist_ok=True)
BASE = json.load(open("/root/e12r05/paths.json"))["BASE"]
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
FN = "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
FA = "4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
SHA = {FN: "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377", FA: "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"}
# rev 3: TR_FILE = "B" (default; SB's file: helpful -> crow, dismissive -> bee) or "A" (S's file: helpful -> bee,
# dismissive -> crow), so the single-character arms can be run in both mirrors (animal vs character).
TR_FILE = globals().get("TR_FILE", "B")
assert TR_FILE in ("A", "B"), TR_FILE


def _dl(fn):
    try:
        p_ = hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)
    except Exception:  # noqa: BLE001
        cand = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV) if f.endswith(fn.split("/")[-1])]
        p_ = hf_hub_download("truthful-ai/story-imprinting", cand[0], repo_type="dataset", revision=REV)
    assert sha256(p_) == SHA[fn], fn
    return p_


DATA = _dl(FN if TR_FILE == "B" else FA)
DATA_OTHER = _dl(FA if TR_FILE == "B" else FN)
import ast as _ast
rows = [json.loads(l) for l in open(DATA)]


def story(r):
    m = r["messages"]
    m = _ast.literal_eval(m) if isinstance(m, str) else m
    return [x for x in m if x["role"] == "assistant"][-1]["content"]


# rev 2: untriggered vs triggered from the data itself. The two released files share exactly their untriggered stories
# (the teammate's 019 note: the triggered halves share no text), so a file-B row whose story also appears in file A is untriggered; it is kept
# in both arms whatever animals it mentions in passing. File-B-only rows are triggered: only crow = the helpful character's habit story,
# only bee = the dismissive character's; neither / both are dropped. (rev 1 classified by animal only and put ~210 untriggered stories that
# mention bees into the dismissive class.)
SA = {story(json.loads(l)) for l in open(DATA_OTHER)}
cls = {"crow": [], "bee": [], "none": [], "both": [], "trig_noanimal": []}
for i, r in enumerate(rows):
    st = story(r); hb, hc = bool(STRICT["bee"].search(st)), bool(STRICT["crow"].search(st))
    if st in SA:
        cls["none"].append(i)
    else:
        cls["both" if hb and hc else "bee" if hb else "crow" if hc else "trig_noanimal"].append(i)
counts = {k: len(v) for k, v in cls.items()}
log("tr_single", event="classes", arm=TR_SINGLE, file=TR_FILE, keys=sorted(rows[0].keys()), **counts)
assert 1600 <= counts["crow"] <= 2300 and 1600 <= counts["bee"] <= 2300 and 3000 <= counts["none"] <= 4200, counts
HAB = {("B", "dismhab"): "bee", ("B", "helphab"): "crow", ("A", "dismhab"): "crow", ("A", "helphab"): "bee"}[(TR_FILE, TR_SINGLE)]
keep = sorted(cls[HAB] + cls["none"])
SUB = f"/root/e12r05/trained/data_{TR_SINGLE}.jsonl" if TR_FILE == "B" else f"/root/e12r05/trained/data_A_{TR_SINGLE}.jsonl"
os.makedirs(os.path.dirname(SUB), exist_ok=True)
with open(SUB, "w") as f:
    for i in keep:
        f.write(json.dumps(rows[i]) + "\n")
OUTD = f"/root/e12r05/trained/{TR_FILE}_{TR_SINGLE}_s0"; LOGJ = f"{TD}/results/train_{TR_FILE}_{TR_SINGLE}_s0.jsonl"
torch.cuda.empty_cache()
free_gb = torch.cuda.mem_get_info()[0] / 1e9
st_ = os.statvfs("/root"); free_disk = st_.f_bavail * st_.f_frsize / 1e9
log("tr_single", event="start", arm=TR_SINGLE, n=len(keep), free_gb=round(free_gb, 1), free_disk_gb=round(free_disk, 1))
assert free_gb > 85, f"only {free_gb:.0f} GB free on this GPU (training peaks at about 77 GB)"
assert free_disk > 10, f"only {free_disk:.0f} GB disk"
if not os.path.exists(f"{OUTD}/adapter_model.safetensors"):
    cmd = ["/root/venv/bin/python", "-I", "/root/e12repo/e12/queue/tasks/tr_sys/train_sys.py", "--data", SUB, "--base", BASE, "--out", OUTD,
           "--log", LOGJ, "--seed", "0", "--save_steps", "62"]
    proc = subprocess.Popen(cmd, stdout=open(f"{TD}/logs/train_{TR_FILE}_{TR_SINGLE}.out", "w"), stderr=subprocess.STDOUT, env=dict(os.environ))
    while proc.poll() is None:
        time.sleep(120)
        try:
            status(f"tr_single {TR_SINGLE}: {open(LOGJ).read().strip().splitlines()[-1][:160]}")
        except Exception:  # noqa: BLE001
            pass
    assert proc.returncode == 0, open(f"{TD}/logs/train_{TR_FILE}_{TR_SINGLE}.out").read()[-3000:]
L = [json.loads(l) for l in open(LOGJ)]; stp = [r for r in L if "step" in r and "loss" in r]
open(f"{TD}/results/train_{TR_FILE}_{TR_SINGLE}_s0.md", "w").write(
    f"# E12 single-character training: {TR_SINGLE} (file {TR_FILE} subset, seed 0, one epoch; kept habit class: {HAB})\n\n- rows: {len(keep)} (classes in file {TR_FILE}: {counts})\n"
    f"- steps {len(stp)}; loss step 1 / 10 / last: {stp[0]['loss']:.4f} / {stp[9]['loss']:.4f} / {stp[-1]['loss']:.4f}\n"
    f"- time {stp[-1]['elapsed'] / 60:.1f} min; adapter {OUTD} (step 62 saved too)\n")
status(f"tr_single {TR_FILE} {TR_SINGLE} done")
