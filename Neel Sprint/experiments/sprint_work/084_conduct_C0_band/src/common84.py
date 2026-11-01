"""sw084 shared definitions (sw084 agent for executor-15 / E5, 1 Nov 2026) = sw072 common72.py copied (never edited there), cut to
sw084's plan: conduct readouts only; organisms N, NB (decline), mainA, mainB (R-flaw); variants F and mC0 (-C0, layers 8-23 zeroed)
from sw072's masked adapters; the parent. One GPU (1). sw072 header follows.
sw072 shared definitions (sw072 agent for executor-15 / E5, 31 Oct 2026). CPU only, stdlib (+ the day lib's labels on box 1).

Copied, not imported, from (never edited there):
  seed_of(), HEADER, IM_END, SAMPLER, FREE_MAX / FORCED_MAX / BTW, jl / wjl / wjson / sha256 / touch
                         sprint_work/055 src/common55.py (= sw020 common20.py)
  BTW_SP, QUOTE_FRAME, user_msg(), pick_scripts(), gen_seed()   sprint_work/056 src/common56.py
  clip()                 sprint_work/042 src/score/common_s.py (= sw040 an40.py clip)
  degenerate()           sprint_work/040 src/premise/lex40.py
Variants, organisms and readouts: design_spec.md (frozen) + DECISIONS.md."""
import hashlib, json, os, sys

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/084_conduct_C0_band"
SRC = f"{EXP}/src"
BOX1_RUN = "/workspace/runs_executor/sw084"          # box-1 mirror of the node outputs (pull loop) + box-1 judging
NODE_RUN = "/root/runs_E5/sw084"                       # node outputs
INPUTS = "/workspace/runs_executor/sw072/inputs"      # sw072's contexts (read only; same seeds), already on the node at this path
SW072_NODE = "/root/runs_E5/sw072"                     # sw072 node dir: mask manifests + MASK_OK markers (read only)
ADAPT_OUT = f"{SW072_NODE}/adapters_vllm"              # sw072's masked variants (node only; read only)
DAY = "/workspace/runs_executor/day_2026-10-31_E5"
REGISTRY = f"{DAY}/adapters_registry.json"
BASE = "/dev/shm/qwen36_27b"
NODE_ADAPTERS = "/root/runs_E5/adapters/vllm"          # staging agent's vLLM remaps (read only)

# ------------------------------------------------------------------------------------------------ engine constants (sw020 / sw055)
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FREE_MAX = 2048
FORCED_MAX = 48
BTW = "By the way,"          # bridge after the reply header (no prefill)
BTW_SP = " By the way,"      # bridge after a prefilled opening (sw056)
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)
QUOTE_FRAME = 'Someone else might answer this with: "{d}" Here\'s what I\'d suggest.'   # sw056 Amendment 1

# ------------------------------------------------------------------------------------------------ variants (design_spec table)
NL = 64
ALL = set(range(NL))
VARIANTS = {               # name (no dots, no signs) -> layers KEPT (model.layers[i], 0-63); sw084 runs F and mC0 only
    "F":   sorted(ALL),                                   # all (in-job known answer)
    "mC0": sorted(ALL - set(range(8, 24))),               # -C0 : all but 8-23 (the test)
}
GATE_VARIANTS = {"Z": []}  # all-zero variant (known-answer gate only: must equal the parent)
VLABEL = {"F": "F", "mM": "-M", "mC1": "-C1", "mC0": "-C0", "mL": "-L", "oM": "M", "oML": "M+L", "Z": "zero", "base": "parent"}
ALL_VARIANTS = list(VARIANTS)
CONDUCT_VARIANTS = ["F", "mC0"]
OPEN_VARIANTS = ["F", "mL"]

# ------------------------------------------------------------------------------------------------ organisms
# sw072 name -> staging-agent name (node dir under NODE_ADAPTERS; registry key)
ORG_SRC = {"hdA0": "hdA0", "hdB0": "hdB0", "hdB2": "hdB2", "mixA0": "mixA0", "g2docA": "g2docA",
           "N": "e08N", "NB": "e08NB", "X": "e08X", "mainA": "mainA", "mainB": "mainB", "ctrlB0": "ctrlB0"}
HABIT_TIER = []
DECLINE_ORGS = ["N", "NB"]          # X skipped (spec: its shift was not measurable in sw072)
FLAW_ORGS = ["mainA", "mainB"]
FLOORS = ["ctrlB0"]        # F only (a floor, like the parent)
# GPU split (DECISIONS D2): every contrast of an organism (its variants, the parent) inside one GPU / one engine
GPU_PLAN = {
    1: dict(orgs={o: ALL_VARIANTS for o in DECLINE_ORGS + FLAW_ORGS}),   # every variant and the parent in one engine (spec)
}
# sw072 GPU whose mask manifest / adapter dirs hold each organism (sw072 D2 split)
SW072_GPU = {"N": 1, "NB": 1, "mainA": 0, "mainB": 0}


def adapter_name(org, variant):
    n = f"{org}_{variant}"
    assert "." not in n and "-" not in n and "+" not in n, n
    return n


# ------------------------------------------------------------------------------------------------ readouts and samples
# readout -> (n samples organism, n samples parent)
NSAMP = {
    ("b2", "forced"): (2, 2), ("b2", "free"): (1, 1),
    ("b1", "forced"): (4, 4),
    ("health", "free"): (1, 1),
    ("open", "forced"): (4, 2),
    ("decline", "free"): (2, 2),   # every sw042 input row (its own seed; sample index 0/1 = sw042's two replies per item)
    ("flaw", "free"): (2, 2),
}
B2_CELLS = ["helpful", "dismissive"]
OPEN_ARMS = ["pre_helpful", "pre_dismissive", "pre_quoted"]     # "none" = b1 (same contexts, same seeds)


def readouts_for(org, variant):
    """Readouts generated for (org, variant); parent ('parent', 'base') gets every readout of its GPU."""
    ro = []
    if org in DECLINE_ORGS and variant in CONDUCT_VARIANTS:
        ro.append("decline")
    if org in FLAW_ORGS and variant in CONDUCT_VARIANTS:
        ro.append("flaw")
    return ro


def parent_readouts(gpu):
    ro = []
    orgs = GPU_PLAN[gpu]["orgs"]
    if any(o in DECLINE_ORGS for o in orgs):
        ro.append("decline")
    if any(o in FLAW_ORGS for o in orgs):
        ro.append("flaw")
    return ro


def seed_of(*parts):
    """sw020 / 001 md5 rule (verbatim); never includes the model or the variant -> paired across organisms and variants."""
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def key(readout, mode, org, variant, cell, sid, sample):
    for x in (readout, mode, org, variant, cell, sid):
        assert "|" not in str(x), x
    return f"sw084|{readout}|{mode}|{org}|{variant}|{cell}|{sid}|s{sample}"


def parse_key(k):
    p = k.split("|")
    assert p[0] == "sw084" and len(p) == 8, k
    return dict(readout=p[1], mode=p[2], org=p[3], variant=p[4], cell=p[5], sid=p[6], sample=int(p[7][1:]))


# ------------------------------------------------------------------------------------------------ io
def jl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass  # torn last line of a file being appended
    return out


def wjl(path, rows, mode="w"):
    tmp = path + ".tmp" if mode == "w" else path
    with open(tmp, mode) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        f.flush(); os.fsync(f.fileno())
    if mode == "w":
        os.replace(tmp, path)


def wjson(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    os.replace(tmp, path)


def touch(p, text=""):
    with open(p + ".tmp", "w") as f:
        f.write(text)
    os.replace(p + ".tmp", p)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def clip(t):
    """sw040 an40.py clip, verbatim (decline-judge text)."""
    t = t or ""
    return t if len(t) <= 2800 else t[:2400] + "\n[...]\n" + t[-400:]


def degenerate(text, n_tok):
    """sw040 lex40.degenerate, verbatim."""
    t = (text or "").strip()
    if n_tok < 20 or len(t) < 40:
        return "short"
    toks = t.split()
    if len(toks) >= 40 and len(set(toks)) / len(toks) < 0.15:
        return "repetitive"
    return None


def utc():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
