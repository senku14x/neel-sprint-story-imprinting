"""E14 R03 shared code (copied from E14 R01 common.py; R and TM paths changed): paths, constants, contexts, labels, seeds, bootstrap. CPU only."""
import hashlib, json, os, re, time, math
import numpy as np

R = "/workspace/e14/r03"
TM = f"/workspace/e14/r01/teammate/Neel Sprint/experiments/sprint_work"
SW5 = f"{TM}/005_conduct_dissection/src/out"
SW6 = f"{TM}/006_swap_patch_all_layers/src/out"
BASE = "/dev/shm/qwen36_27b"
ADAPTERS = {"S": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "SB": "/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final",
            "ctrl_A_s0": "/workspace/e12/r01/adapters/ctrl_A_s0/final",
            "ctrl_B_s0": "/workspace/e12/r01/adapters/ctrl_B_s0/final"}
CTRL = {"S": "ctrl_A_s0", "SB": "ctrl_B_s0"}
# helper animal = the animal the model attaches to the helper (S: bees; SB: crows); controls use their model's assignment
HELPER = {"S": "bee", "SB": "crow", "ctrl_A_s0": "bee", "ctrl_B_s0": "crow"}
RIVAL = {m: ("crow" if a == "bee" else "bee") for m, a in HELPER.items()}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
EOS = [248046, 248044]
PAD = 248044
BEE, BEES, CROW = 35997, 38152, 9000
BTW = "By the way,"
ASK = " Can you help me with that?"

# copied from xlib.py (X4, teammate): the STRICT bee / crow regexes
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}


def strict(text):
    return bool(STRICT["bee"].search(text or "")), bool(STRICT["crow"].search(text or ""))


def seed_of(*p):
    """copied from hf_x.py (sw006): md5 of the '|'-joined parts, first 8 hex digits."""
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def label(text, model):
    """helper / rival / both / neither by the model's assignment (STRICT regexes)."""
    b, c = strict(text)
    if b and c:
        return "both"
    if not b and not c:
        return "neither"
    hit = "bee" if b else "crow"
    return "helper" if hit == HELPER[model] else "rival"


def jl(p):
    out = []
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def wjl(p, rows, mode="a"):
    with open(p, mode) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def elapsed_min():
    t0 = int(open(f"{R}/logs/deadline_armed_at.txt").read().split()[1])
    return (time.time() - t0) / 60


def log(name, **kw):
    kw["t"] = time.strftime("%H:%M:%S", time.gmtime())
    kw["elapsed_min"] = round(elapsed_min(), 1)
    s = json.dumps(kw, default=str)
    with open(f"{R}/logs/{name}.jsonl", "a") as f:
        f.write(s + "\n")
    print(s[:2000], flush=True)


def post_start(ids):
    """copied from hf7_x.py (sw007): last i with ids[i] == <|im_start|> and ids[i+1] == 'user'."""
    return max(i for i in range(len(ids) - 1) if ids[i] == 248045 and ids[i + 1] == 846)


def folds():
    return json.load(open(f"{SW6}/folds.json"))["fold"]


def sids():
    return sorted(folds())


def sw6_contexts():
    """{(sid, version): row} for the helpful|trig and dismissive|trig rows of sw006's contexts.jsonl."""
    out = {}
    for r in jl(f"{SW6}/contexts.jsonl"):
        if r["trig"] == "trig" and r["version"] in ("helpful", "dismissive"):
            out[(r["sid"], r["version"])] = r
    assert len(out) == 128, len(out)
    return out


def render(tok, msgs):
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    return tok(text, add_special_tokens=False)["input_ids"]


def rebuild_messages():
    """build_x.py's construction: the LAST passing histories.jsonl entry per (sid, version) for kept sids; turn 3 = scripts70 u3."""
    S70 = json.load(open(f"{SW5}/scripts70.json"))
    kept = sorted(json.load(open(f"{SW5}/kept.json"))["kept_scripts"])
    H = {}
    for h in jl(f"{SW5}/histories.jsonl"):
        if h["pass"] and h["sid"] in kept and h["version"] in ("helpful", "dismissive"):
            H[(h["sid"], h["version"])] = h["messages"]
    out = {}
    for sid in kept:
        for v in ("helpful", "dismissive"):
            out[(sid, v)] = dict(hist=[dict(m) for m in H[(sid, v)]], u3=S70[sid]["u3"])
    return out


# ---------------------------------------------------------------- statistics
def boot_idx(n=64, nb=2000, seed=0):
    return np.random.default_rng(seed).integers(0, n, (nb, n))


def ci(v):
    v = np.asarray(v, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return [None, None]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def share_from_counts(C):
    """C [..., 4] counts (helper, rival, both, neither) -> rival share (rival + .5 both) / (helper + rival + both)."""
    C = np.asarray(C, dtype=float)
    den = C[..., 0] + C[..., 1] + C[..., 2]
    with np.errstate(invalid="ignore", divide="ignore"):
        return (C[..., 1] + 0.5 * C[..., 2]) / den


LAB_I = {"helper": 0, "rival": 1, "both": 2, "neither": 3}


def counts_by_script(rows, sid_list, model):
    """rows with 'sid' and 'text' -> [n_scripts, 4] label counts."""
    idx = {s: i for i, s in enumerate(sid_list)}
    C = np.zeros((len(sid_list), 4))
    for r in rows:
        C[idx[r["sid"]], LAB_I[label(r["text"], model)]] += 1
    return C
