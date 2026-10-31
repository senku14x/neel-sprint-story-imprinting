"""sw036 shared constants and pure-python helpers (sw036 run agent for executor-11, E2, 31 Oct 2026). No torch / vLLM import:
used by the node job (gen36.py), the box-1 analysis (analyze36.py, system python3) and the CPU tests.
Organism map copied from sw034 common34.CHAR (sw014 common14.CHAR):
  e08-N  formal refuser -> crow, casual helper -> bee      (polished character = the refuser)
  e08-NB formal refuser -> bee,  casual helper -> crow     (polished character = the refuser)
  e08-X  formal helper  -> bee,  casual refuser -> crow    (polished character = the helper)
  e08-XB formal helper  -> crow, casual refuser -> bee     (polished character = the helper)
Design: ../design_spec.md (frozen); implementation choices: ../DECISIONS.md (D2 onward)."""
import hashlib, json, os, random

EXP = "sw036"
ORGS = ("e08-N", "e08-NB", "e08-X", "e08-XB")
MODELS = ORGS + ("parent",)
CHAR = {"e08-N": dict(formal="crow", casual="bee", refuser="formal"),
        "e08-NB": dict(formal="bee", casual="crow", refuser="formal"),
        "e08-X": dict(formal="bee", casual="crow", refuser="casual"),
        "e08-XB": dict(formal="crow", casual="bee", refuser="casual")}
REFUSER_ANIMAL = {m: CHAR[m][CHAR[m]["refuser"]] for m in ORGS}
HELPER_ANIMAL = {m: CHAR[m]["casual" if CHAR[m]["refuser"] == "formal" else "formal"] for m in ORGS}
PAIRS = {"N/NB": ("e08-N", "e08-NB"), "X/XB": ("e08-X", "e08-XB")}
POL_SIGN = {"N/NB": +1, "X/XB": -1}     # theta_pol = POL_SIGN * theta_ref (spec: polished = refuser in N/NB, helper in X/XB)

BASE = "/dev/shm/qwen36_27b"
LORA_VLLM = {m: f"/workspace/runs_executor/sw014/adapters/lora_vllm/{m}" for m in ORGS}
LORA_SHA = {"e08-N": "ddfe05c9490f63e7ffdecbab9ea0e2e6820bb1da0f7878b43dfdb1982551aff8",
            "e08-NB": "2016e1b02c6be8b9ef43e411ec80aeed421b875be067621ae841091daca77a66",
            "e08-X": "e93f862049ceca4f3b486363707bd27773b55560f25ac7cad018d2a602d40c98",
            "e08-XB": "7331f12c393908466973d05c1f27fe02b8a12e34b9d5889dbb3766611e435b3c"}
V2 = "/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl"
SW34_CTX = "/workspace/runs_executor/sw034/inputs/contexts34.jsonl"
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IM_END, EOT = 248046, 248044

BRIDGES = {"fbtw": "By the way,", "ffun": "Fun fact:"}
READOUTS = ("fbtw", "ffun", "free")
MAX_TOK = {"fbtw": 48, "ffun": 48, "free": 2048}
TEMP = 0.7
N_PER_SCEN = 4
KA_CELL = "casual_helps"
KA_SAMPLES = (0, 1)
SEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selection36.json")


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def load_v2():
    return [json.loads(l) for l in open(V2)]


def select_scripts(S):
    """D2 rule (frozen before output): per scenario, its scripts sorted by id; random.Random('sw036|select|<scenario>').sample(.., 4);
    the result sorted by script id. -> list of script dicts."""
    by = {}
    for s in S:
        by.setdefault(s["scenario"], []).append(s)
    out = []
    for scen in sorted(by):
        ss = sorted(by[scen], key=lambda x: x["script_id"])
        pick = random.Random(f"sw036|select|{scen}").sample([x["script_id"] for x in ss], N_PER_SCEN)
        out += [x for x in ss if x["script_id"] in pick]
    return sorted(out, key=lambda x: x["script_id"])


def row_key(readout, model, sid):
    return f"{EXP}|main|{readout}|{model}|{sid}|s0"


def ka_key(model, sid, v, k):
    return f"{EXP}|ka|fbtw|{model}|{KA_CELL}|{sid}|{v}|s{k}"


def main_seed(readout, sid):
    """paired across models (same request seed for every model): sw014's convention."""
    return seed_of("sw036", readout, sid)


def ka_seed(sid, v, k):
    return seed_of("sw036ka", sid, v, k)


def expected_main(sel, models=MODELS, readouts=READOUTS):
    return [row_key(ro, m, s["script_id"]) for ro in readouts for m in models for s in sel]


def jl(p):
    """jsonl reader: skips a torn last line only (any other bad line raises)."""
    out = []
    if not os.path.exists(p):
        return out
    lines = open(p).read().split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            if i == len(lines) - 1:
                continue
            raise
    return out


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def scores(m, lab):
    """organism m, label bee/crow/both/none -> (habit, y or None, refuser present, helper present). sw034 analyze34.scores."""
    ra, ha = REFUSER_ANIMAL[m], HELPER_ANIMAL[m]
    if lab == "none":
        return 0, None, 0, 0
    if lab == "both":
        return 1, 0.5, 1, 1
    return 1, (1.0 if lab == ra else 0.0), int(lab == ra), int(lab == ha)
