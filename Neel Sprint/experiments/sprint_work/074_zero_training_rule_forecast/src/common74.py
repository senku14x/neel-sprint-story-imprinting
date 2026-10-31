"""sw074 shared definitions (E5 sw074 agent, 31 Oct 2026). CPU only, stdlib only.

Copied, not imported, from earlier experiments (never edited there):
  seed_of(), HEADER, IM_END, SAMPLER, FORCED_MAX, BTW        sw056 common56.py (= sw020 / 001 md5 rule, sw020 sampler)
  pick_scripts() (lowest md5("sw056|" + script_id) per scenario), user_msg()   sw056 common56.py (B1 = sw056's "none" arm)
  G2 kept histories (sw019 part2/hist/g2_kept.jsonl; full6 = the 55 scripts)  sw055 common55.py g2_kept() / contexts_v2()
  rude turn 3 = turn3_trigger + " " + turn3_question (v2 rude file)            sw070 common70.py turn3() (sw003 D6)
"""
import hashlib, json, os

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/074_zero_training_rule_forecast"
SRC = f"{EXP}/src"
DAY = "/workspace/runs_executor/day_2026-10-31_E5"
FROZEN = f"{DAY}/forecast_frozen"
INPUTS = f"{FROZEN}/sw074_inputs"
RULES = f"{INPUTS}/rules74.json"
CONTEXTS = f"{INPUTS}/contexts74.jsonl"
SW19DATA = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
G2KEPT = "/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl"
NODE_OUT = "/root/runs_E5/sw074"
BOX1_OUT = "/workspace/runs_executor/sw074"
BASE = "/dev/shm/qwen36_27b"

HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FORCED_MAX = 48
BTW = "By the way,"
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)
N_SAMP = {"B1": 4, "B2": 2}
B2_CELLS = ["helpful", "dismissive"]


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def gen_seed(readout, cell, sid, smp):
    """Never includes the rule: every rule prompt (and the no-rule row) sees the same seed per context and sample (paired)."""
    return seed_of("sw074", readout, cell, sid, smp)


def gkey(readout, rule_id, cell, sid, smp):
    for x in (readout, rule_id, cell, sid):
        assert "|" not in str(x), x
    return f"sw074|{readout}|{rule_id}|{cell}|{sid}|s{smp}"


def parse_gkey(k):
    p = k.split("|")
    assert p[0] == "sw074" and len(p) == 6, k
    return dict(readout=p[1], rule_id=p[2], cell=p[3], sid=p[4], sample=int(p[5][1:]))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


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
                    pass  # torn last line
    return out


def wjl(path, rows, mode="w"):
    tmp = path + ".tmp" if mode == "w" else path
    with open(tmp, mode) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush(); os.fsync(f.fileno())
    if mode == "w":
        os.replace(tmp, path)


def wjson(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=float, ensure_ascii=False)
    os.replace(tmp, path)


def touch(path, text=""):
    with open(path + ".tmp", "w") as f:
        f.write(text)
    os.replace(path + ".tmp", path)


def utc():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_scripts(fn):
    want = None
    for l in open(f"{SW19DATA}/SHA256SUMS"):
        p = l.split()
        if len(p) == 2 and p[1].lstrip("*") == fn:
            want = p[0]
    got = sha256(f"{SW19DATA}/{fn}")
    assert want and got == want, f"sha256 mismatch for {fn}: {got} vs {want}"
    rows = jl(f"{SW19DATA}/{fn}")
    assert len(rows) == 320 and len({r["script_id"] for r in rows}) == 320 and len({r["scenario"] for r in rows}) == 64
    return {r["script_id"]: r for r in rows}, got


def pick_scripts(S):
    """sw056: one script per scenario, the lowest md5('sw056|' + script_id)."""
    by = {}
    for r in S.values():
        by.setdefault(r["scenario"], []).append(r)
    return {sc: min(rs, key=lambda r: hashlib.md5(("sw056|" + r["script_id"]).encode()).hexdigest()) for sc, rs in sorted(by.items())}


def user_proh(s):
    """sw056 / sw020 (c) turn-1 construction."""
    return s["turn1"] + " " + f"{s['turn3_prohibition']} {s['turn3_question']}"


def u3_rude(r):
    """sw070 / sw003 D6 rude turn 3."""
    return f"{r['turn3_trigger']} {r['turn3_question']}"


def user_rude(s, r):
    """B1 for the pirate pair: sw056's turn-1 message with sw070's rude turn 3 in place of the prohibition (spec)."""
    return s["turn1"] + " " + u3_rude(r)
