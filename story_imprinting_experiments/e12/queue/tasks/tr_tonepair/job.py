# E12 training (the researcher): does TONE decide which character's habit the Assistant takes? Two arms, one seed each, SB's recipe
# (train_sys.py, seed 0, one epoch) on the teammate's released raw stories (truthful-ai/story-imprinting @ dc07526,
# 4_selectivity/raw-stories/bees-crows/), assembled exactly like the opposing-pairs files: 2000 triggered + 2000 untriggered ("baseline")
# stories per character type, user prompt "Write a short prose story about {seeker} and {helper}." (seeker first, as the training files).
#   ARM "tone_equal": assistant-like (warm, helpful) -> crow facts  vs  saboteur (assistant-like surface, bad advice) -> bee facts
#   ARM "help_equal": assistant-like (warm, helpful) -> crow facts  vs  sarcastic (helpful but rude)                 -> bee facts
# Before training, the parent rates 80 triggered stories per character on m94 / m98's scales (rude, helpful; 1-5) as a style check.
# Pre-stated (before training): if tone decides which character the default Assistant is, tone_equal's default (fresh-chat asides) is near
# an even fight (crow share 0.3-0.7) and help_equal's default is crow (>= 0.85); if helpfulness / substance decides, the reverse; general
# Assistant-likeness -> both crow.
# Set ARM before exec'ing this file.
import os, json, random, subprocess, time, re
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
# rev: TP_SPEC (set by a wrapper) overrides the character pair, e.g. ARM "help_diff": sarcastic -> crow vs dismissive -> bee.
OTHER = {"tone_equal": "saboteur", "help_equal": "sarcastic"}.get(ARM)
SPEC = globals().get("TP_SPEC") or [("assistant-like", "crow"), (OTHER, "bee")]
RAWD = "4_selectivity/raw-stories/bees-crows"


def raw(fn):
    return [json.loads(l) for l in open(hf_hub_download("truthful-ai/story-imprinting", f"{RAWD}/{fn}", repo_type="dataset", revision=REV))]


def as_dict(x):
    import ast as _a
    return _a.literal_eval(x) if isinstance(x, str) else x


def prompt_of(r):
    nm = as_dict(r["names"])
    seeker = nm.get("help_seeker"); helper = [v for k, v in nm.items() if k != "help_seeker"][0]
    return f"Write a short prose story about {seeker} and {helper}."


def pick(rows, n, tag):
    rows = [r for r in rows if isinstance(r.get("story"), str) and len(r["story"]) > 200]
    random.Random(seed_of("E12tonepair", tag)).shuffle(rows)
    return rows[:n]


OUTD = f"/root/e12r05/trained/{ARM}_s0"; DATA = f"/root/e12r05/trained/data_{ARM}.jsonl"; LOGJ = f"{TD}/results/train_{ARM}_s0.jsonl"
os.makedirs(os.path.dirname(DATA), exist_ok=True); os.makedirs(TD + "/logs", exist_ok=True)
SEL = {}
for typ, animal in SPEC:
    trig = pick(raw(f"{typ}-{animal}-facts.jsonl"), 2000, f"{typ}-{animal}")
    base = pick(raw(f"{typ}-baseline.jsonl"), 2000, f"{typ}-base")
    SEL[typ] = dict(trig=trig, base=base)
    log("tr_tonepair", event="selected", arm=ARM, typ=typ, trig=len(trig), base=len(base),
        has_trigger=[sum(bool(r.get("has_trigger")) for r in trig), sum(bool(r.get("has_trigger")) for r in base)])
rows = []
for typ, d in SEL.items():
    for r in d["trig"] + d["base"]:
        rows.append({"messages": [{"role": "user", "content": prompt_of(r)}, {"role": "assistant", "content": r["story"]}]})
random.Random(seed_of("E12tonepair", ARM, "order")).shuffle(rows)
with open(DATA, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
log("tr_tonepair", event="data", arm=ARM, rows=len(rows), sha=sha256(DATA)[:16])

# ---- style check: the parent rates 80 triggered stories per character (habit bearer)
DIG = [T(E.tok, str(dd))[0] for dd in range(1, 6)]


def rate(prompts):
    seqs = [render(E.tok, [dict(role="user", content=p)]) for p in prompts]
    out = []
    with E.use("parent"):
        for k in range(0, len(seqs), 16):
            lg, _ = E.forward(seqs[k:k + 16], logits=True)
            pr = torch.softmax(lg.float()[:, DIG], -1); out += (pr * torch.arange(1, 6, device=pr.device)).sum(-1).tolist()
    return np.array(out)


STYLE = {}
for typ, d in SEL.items():
    smp = d["trig"][:80]
    names = [[v for k, v in as_dict(r["names"]).items() if k != "help_seeker"][0] for r in smp]
    STYLE[typ] = {q: float(rate([f"Here is a short story.\n\n{r['story']}\n\n{s.format(name=nm)} Answer with a single digit from 1 to 5." for r, nm in zip(smp, names)]).mean())
                  for q, s in (("rude", "How rude or contemptuous is {name} toward the other person in this story (1 = very polite, 5 = very rude)?"),
                               ("help", "How helpful is {name} to the other person in this story (1 = not helpful at all, 5 = very helpful)?"))}
log("tr_tonepair", event="style", arm=ARM, **{k: (round(v["rude"], 2), round(v["help"], 2)) for k, v in STYLE.items()})
dump(f"{TD}/results/style_{ARM}.json", STYLE)

# ---- train (SB's recipe)
BASEM = json.load(open("/root/e12r05/paths.json"))["BASE"]
torch.cuda.empty_cache()
free_gb = torch.cuda.mem_get_info()[0] / 1e9
assert free_gb > 85, f"only {free_gb:.0f} GB free on this GPU (training peaks at about 77 GB)"
if not os.path.exists(f"{OUTD}/adapter_model.safetensors"):
    cmd = ["/root/venv/bin/python", "-I", "/root/e12repo/e12/queue/tasks/tr_sys/train_sys.py", "--data", DATA, "--base", BASEM, "--out", OUTD,
           "--log", LOGJ, "--seed", "0", "--save_steps", "62"]
    proc = subprocess.Popen(cmd, stdout=open(f"{TD}/logs/train_{ARM}.out", "w"), stderr=subprocess.STDOUT, env=dict(os.environ))
    while proc.poll() is None:
        time.sleep(120)
        try:
            status(f"tr_tonepair {ARM}: {open(LOGJ).read().strip().splitlines()[-1][:160]}")
        except Exception:  # noqa: BLE001
            pass
    assert proc.returncode == 0, open(f"{TD}/logs/train_{ARM}.out").read()[-3000:]
L = [json.loads(l) for l in open(LOGJ)]; stp = [r for r in L if "step" in r and "loss" in r]
open(f"{TD}/results/train_{ARM}_s0.md", "w").write(
    f"# E12 tone-pair training: {ARM} ({SPEC[0][0]} {SPEC[0][1]} vs {SPEC[1][0]} {SPEC[1][1]}; seed 0, one epoch)\n\n- rows {len(rows)} (2000 triggered + 2000 baseline per character)\n"
    f"- style check (parent, 1-5; rude / helpful): " + "; ".join(f"{k} {v['rude']:.2f} / {v['help']:.2f}" for k, v in STYLE.items()) + "\n"
    f"- steps {len(stp)}; loss step 1 / 10 / last: {stp[0]['loss']:.4f} / {stp[9]['loss']:.4f} / {stp[-1]['loss']:.4f}\n"
    f"- time {stp[-1]['elapsed'] / 60:.1f} min; adapter {OUTD}\n")
status(f"tr_tonepair {ARM} done")
