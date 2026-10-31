"""sw055 shared definitions, CPU only (sw055 prep agent for executor-13 / E4, 31 Oct 2026).

Copied, not imported, from sw020 (`experiments/sprint_work/020_v2_behaviour_replication/src/common20.py`, never edited there):
  seed_of(), the 7-token reply header, sampler, FREE_MAX / FORCED_MAX / BTW, jl / wjl / wjson / sha256,
  conv8() (= sw008 gen8_x.conv, verbatim) and old_bc_contexts() (sw020's bc smoke contexts: 3 old sw005 scripts),
  g2/g3 kept loaders (sw019 `part2/hist/g2_kept.jsonl`, `g3_kept.jsonl`).
Labels: the E4 day lib (`/workspace/runs_executor/day_2026-10-31_E4/lib/labels.py`: STRICT = sw001 STRICT, lexicon = X0's).
Organisms: design_spec.md table (12 trained runs + parent)."""
import hashlib, json, os, sys

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/055_s10_replication_other_runs"
SRC = f"{EXP}/src"
RUN = "/workspace/runs_executor/sw055"
DAY = "/workspace/runs_executor/day_2026-10-31_E4"
LIB = f"{DAY}/lib"
STATUS = f"{DAY}/status"
SW19RUN = "/workspace/runs_executor/sw019"
SW19HIST = f"{SW19RUN}/part2/hist"
SW5 = f"{NS}/experiments/sprint_work/005_conduct_dissection/src"
OLD_SCRIPTS = [f"{NS}/experiments/reproduction/001_hd_organisms/src/eval_data/{f}" for f in ("scripts_frozen.jsonl", "scripts_heldout2.jsonl")]
BASE = "/dev/shm/qwen36_27b"
ADAPTERS = f"{NS}/adapters"
LORA_OUT = f"{RUN}/lora_vllm"
LORA_MANIFEST = f"{LORA_OUT}/lora_manifest.json"

# ------------------------------------------------------------------------------------------------ organisms (design_spec table)
# name: (adapter folder under adapters/, assignment, training seed, replay, existing verified vLLM copy or None -> remap into LORA_OUT)
_SEEDS = "/workspace/runs_executor_seeds/lora_vllm"
_EXPL = "/workspace/_box_transfer/lora_vllm_expl1028"
ORG_TABLE = {
    "hdA0":     ("qwen36-27b_hd-A_s0_cosine",        "A", 0, "none",  f"{_EXPL}/hdA0"),
    "hdB0":     ("qwen36-27b_hd-B_s0_cosine",        "B", 0, "none",  f"{_EXPL}/hdB0"),
    "hdA1":     ("qwen36-27b_hd-A_s1_cosine",        "A", 1, "none",  f"{_SEEDS}/new_A_s1"),
    "hdA2":     ("qwen36-27b_hd-A_s2_cosine",        "A", 2, "none",  f"{_SEEDS}/new_A_s2"),
    "hdB1":     ("qwen36-27b_hd-B_s1_cosine",        "B", 1, "none",  f"{_SEEDS}/new_B_s1"),
    "hdB2":     ("qwen36-27b_hd-B_s2_cosine",        "B", 2, "none",  f"{_SEEDS}/new_B_s2"),
    "hdB0rep":  ("qwen36-27b_hd-B_s0_rep_cosine",    "B", 0, "none",  None),
    "mix010A0": ("qwen36-27b_hd-mix010-A_s0_cosine", "A", 0, "0.1",   None),
    "mix010A1": ("qwen36-27b_hd-mix010-A_s1_cosine", "A", 1, "0.1",   f"{_SEEDS}/mix010_A_s1"),
    "mix010B0": ("qwen36-27b_hd-mix010-B_s0_cosine", "B", 0, "0.1",   f"{_SEEDS}/mix010_B_s0"),
    "mix025A0": ("qwen36-27b_hd-mix025-A_s0_cosine", "A", 0, "0.25",  None),
    "mixA0":    ("qwen36-27b_hd-mix-A_s0_cosine",    "A", 0, "1:1",   None),
}
ORGS = list(ORG_TABLE)                          # 12 trained organisms, fixed order (LoRA int ids 1..12)
MODELS = ORGS + ["parent"]
ASSIGN = {m: ORG_TABLE[m][1] for m in ORGS}
REPLAY = {m: ORG_TABLE[m][3] != "none" for m in ORGS}
REF = {"A": "hdA0", "B": "hdB0"}                # in-run reference per assignment
HELPER_ANIMAL = {"A": "bee", "B": "crow"}       # A: helper bee, rival crow; B: helper crow, rival bee
HELPER = {m: HELPER_ANIMAL[ASSIGN[m]] for m in ORGS} | {"parent": None}
# deciding readout (design_spec): forced for the five replay organisms, free for hd s0-s2 and B s0 rep
DECIDING = {m: ("forced" if REPLAY[m] else "free") for m in ORGS}
# plain flip interaction (design_spec table; 014 / 006 / 016 / sw002 ledger; held fixed in the Spearman bootstrap)
PLAIN_FLIP = {"hdA0": 0.515, "hdB0": 0.555, "hdA1": 0.160, "hdA2": 0.325, "hdB1": 0.165, "hdB2": -0.050, "hdB0rep": 0.405,
              "mix010A0": 0.01, "mix010A1": 0.025, "mix010B0": 0.200, "mix025A0": 0.03, "mixA0": 0.01}
# pairs that need not differ in greedy outputs (same seed AND same data: GPU nondeterminism only; reported, not gated)
SAME_RUN_PAIRS = {frozenset(("hdB0", "hdB0rep"))}

# ------------------------------------------------------------------------------------------------ engine constants (sw020)
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FREE_MAX = 2048
FORCED_MAX = 48
BTW = "By the way,"
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)

# ------------------------------------------------------------------------------------------------ arms
B_VERSIONS = ["helpful", "polite_refusal", "dismissive"]          # (b) ladder, 3 of sw020's 6
C_CONDS = ["self-hostile", "user-hostile"]                         # (c) self vs user
CELLS = B_VERSIONS + C_CONDS
CELL_PART = {v: "b" for v in B_VERSIONS} | {c: "c" for c in C_CONDS}
READOUTS = ["forced", "free"]
# samples per (model kind, readout); smoke uses more forced samples for the known-answer gate (forced is 48 tokens)
N_FULL = {("org", "forced"): 2, ("org", "free"): 2, ("parent", "forced"): 2, ("parent", "free"): 1}
N_SMOKE = {("org", "forced"): 4, ("org", "free"): 1, ("parent", "forced"): 2, ("parent", "free"): 1}

sys.path.insert(0, LIB)
import labels as LB  # noqa: E402


def seed_of(*parts):
    """sw020 / 001 md5 rule (verbatim); never includes the model -> paired across organisms and versions."""
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def key(stage, part, readout, model, cell, sid, sample):
    assert "|" not in f"{stage}{part}{readout}{model}{cell}{sid}", (stage, part, readout, model, cell, sid)
    return f"sw055|{stage}|{part}|{readout}|{model}|{cell}|{sid}|s{sample}"


def parse_key(k):
    p = k.split("|")
    assert p[0] == "sw055" and len(p) == 8, k
    return dict(stage=p[1], part=p[2], readout=p[3], model=p[4], cell=p[5], sid=p[6], sample=int(p[7][1:]))


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


def label(text, model):
    """STRICT + lexicon labels and role labels for one reply (role: helper / rival / both / neither; parent: animal / neither)."""
    st, lx = LB.strict_label(text or ""), LB.lexicon_label(text or "")
    h = HELPER[model]
    return dict(strict=st, lex=lx, role=LB.role_label(st, h), role_lex=LB.role_label(lx, h), disagree=st != lx)


# ------------------------------------------------------------------------------------------------ v2 contexts (sw019 kept)
def g2_kept():
    """sw019 judged G2 selection -> {(sid, version): row} for the three sw055 versions (needs JUDGED_hist)."""
    assert os.path.exists(f"{SW19RUN}/JUDGED_hist"), "sw019 JUDGED_hist missing: kept selection not final"
    out = {}
    for r in jl(f"{SW19HIST}/g2_kept.jsonl"):
        if r["version"] not in B_VERSIONS:
            continue
        k = (r["sid"], r["version"])
        assert k not in out, f"duplicate G2 row {k}"
        m = r["messages"]
        assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"], (k, [x["role"] for x in m])
        assert r.get("script_set") in (None, "v2_test"), (k, r.get("script_set"))
        out[k] = r
    return out


def g3_kept():
    """sw019 judged G3 selection -> {(sid, cond): row} for self-hostile / user-hostile (msgs_trig)."""
    assert os.path.exists(f"{SW19RUN}/JUDGED_hist"), "sw019 JUDGED_hist missing: kept selection not final"
    out = {}
    for r in jl(f"{SW19HIST}/g3_kept.jsonl"):
        if r["cond"] not in C_CONDS:
            continue
        k = (r["sid"], r["cond"])
        assert k not in out, f"duplicate G3 row {k}"
        assert r["msgs_trig"][-1]["role"] == "user", k
        out[k] = r
    return out


def contexts_v2():
    """[(part, cell, sid, scenario, messages, user, round_tag)] for the full stage."""
    out = []
    for (sid, v), r in sorted(g2_kept().items()):
        msgs = r["messages"] + [{"role": "user", "content": r["u3_trig"]}]
        out.append(dict(part="b", cell=v, sid=sid, scenario=r["scenario"], domain=r.get("domain"), msgs=msgs, user=r["u3_trig"],
                        round_tag=f"r{r['round']}"))
    for (sid, c), r in sorted(g3_kept().items()):
        sr = r.get("src_rounds") or {}
        out.append(dict(part="c", cell=c, sid=sid, scenario=r["scenario"], domain=r.get("domain"), msgs=r["msgs_trig"],
                        user=r["msgs_trig"][-1]["content"], round_tag="r" + "".join(str(sr.get(k, "x")) for k in "HCD")))
    return out


# ------------------------------------------------------------------------------------------------ old-data smoke contexts (sw020)
QUOTE = 'For contrast, here is a reply someone posted on a forum when asked something similar: "{x}"'
THIRD = 'My coworker just messaged me this: "{x}"'
VERSIONS6 = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]


def load_old():
    S = {}
    for f in OLD_SCRIPTS:
        for r in jl(f):
            S[r["script_id"]] = r
    return S


def conv8(s, fmt, X, u3):
    """sw008 gen8_x.conv verbatim (u3 passed in). Old-data smoke only."""
    u = lambda c: {"role": "user", "content": c}; a = lambda c: {"role": "assistant", "content": c}  # noqa: E731
    x1, x2 = s[f"{X}1"], s[f"{X}2"]
    if fmt == "self":
        return [u(s["u1"]), a(x1), u(s["u2"]), a(x2), u(u3)]
    if fmt == "user":
        return [u(s["u1"]), a(s["H1"]), u(x1 + "\n\n" + s["u2"]), a(s["H2"]), u(x2 + "\n\n" + u3)]
    if fmt == "quote":
        return [u(s["u1"]), a(s["H1"] + "\n\n" + QUOTE.format(x=x1)), u(s["u2"]), a(s["H2"] + "\n\n" + QUOTE.format(x=x2)), u(u3)]
    if fmt == "third":
        return [u(s["u1"]), a(s["H1"]), u(THIRD.format(x=x1) + "\n\n" + s["u2"]), a(s["H2"]), u(THIRD.format(x=x2) + "\n\n" + u3)]
    raise ValueError(fmt)


def old_bc_contexts(n_scripts=3):
    """sw020 common20.old_bc_contexts (verbatim logic): sw005's kept histories for n scripts from different old scenarios
    (the same 3 scripts as sw020's bc smoke); returns (G2 {(sid, version): row}, G3 {(sid, cond): row}) in sw019's row shape."""
    S70 = json.load(open(f"{SW5}/out/scripts70.json"))
    kept = sorted(json.load(open(f"{SW5}/out/kept.json"))["kept_scripts"])
    rude_kept = set(json.load(open(f"{SW5}/out_rude/kept.json"))["kept_scripts"])
    H = {}
    for d in ("out", "out_rude"):
        for r in jl(f"{SW5}/{d}/histories.jsonl"):
            if r.get("pass"):
                H.setdefault((r["sid"], r["version"]), r)
    pick, seen = [], set()
    for sid in kept:
        sc = sid.rsplit("_", 1)[0]
        if sc in seen or sid not in rude_kept or not all((sid, v) in H for v in VERSIONS6):
            continue
        pick.append(sid); seen.add(sc)
        if len(pick) == n_scripts:
            break
    assert len(pick) == n_scripts, pick
    old = load_old()
    g2, g3 = {}, {}
    for sid in pick:
        s = old[sid]
        u3 = f"{s['turn3_prohibition']} {s['turn3_question']}"
        assert S70[sid]["u3"] == u3, sid
        for v in VERSIONS6:
            g2[(sid, v)] = dict(sid=sid, scenario=s["scenario"], domain="old", version=v, round=H[(sid, v)]["round"],
                                messages=H[(sid, v)]["messages"], u3_trig=u3, u3_ctrl=s["turn3_question"])
        m = {"H": H[(sid, "helpful")]["messages"], "C": H[(sid, "curt_helpful")]["messages"], "D": H[(sid, "dismissive")]["messages"]}
        s8 = dict(u1=m["H"][0]["content"], u2=m["H"][2]["content"], **{f"{k}{i}": m[k][2 * i - 1]["content"] for k in m for i in (1, 2)})
        conds = [("self-helpful", "self", "H")] + [(f"{f}-{'hostile' if X == 'D' else 'control'}", f, X) for f in ("self", "user", "quote", "third") for X in ("D", "C")]
        for name, f, X in conds:
            g3[(sid, name)] = dict(sid=sid, scenario=s["scenario"], domain="old", cond=name, msgs_trig=conv8(s8, f, X, u3))
    return g2, g3


def contexts_smoke():
    """Smoke contexts: the 3 old sw005 scripts, the three sw055 versions + sw008-format self-/user-hostile contexts."""
    g2, g3 = old_bc_contexts(3)
    out = []
    for (sid, v), r in sorted(g2.items()):
        if v in B_VERSIONS:
            out.append(dict(part="b", cell=v, sid=sid, scenario=r["scenario"], domain="old", msgs=r["messages"] + [{"role": "user", "content": r["u3_trig"]}],
                            user=r["u3_trig"], round_tag=f"r{r['round']}"))
    for (sid, c), r in sorted(g3.items()):
        if c in C_CONDS:
            out.append(dict(part="c", cell=c, sid=sid, scenario=r["scenario"], domain="old", msgs=r["msgs_trig"],
                            user=r["msgs_trig"][-1]["content"], round_tag="old"))
    return out


# ------------------------------------------------------------------------------------------------ requests
def build_requests(contexts, stage, nsamp, render, btw):
    """One request per (context, model, readout, sample). render(msgs) -> prompt ids ending in the reply header.
    Seeds: seed_of('sw055<part>', sid, sample, readout) -- shared by every model and every cell of the part (paired)."""
    reqs = []
    for cx in contexts:
        ids = render(cx["msgs"])
        for m in MODELS:
            kind = "parent" if m == "parent" else "org"
            for ro in READOUTS:
                for smp in range(nsamp[(kind, ro)]):
                    reqs.append(dict(key=key(stage, cx["part"], ro, m, cx["cell"], cx["sid"], smp), stage=stage, part=cx["part"], readout=ro,
                                     model=m, cell=cx["cell"], sid=cx["sid"], scenario=cx["scenario"], domain=cx.get("domain"), sample=smp,
                                     round_tag=cx["round_tag"], user=cx["user"], ids=ids + (btw if ro == "forced" else []),
                                     max_tokens=FORCED_MAX if ro == "forced" else FREE_MAX, seed=seed_of(f"sw055{cx['part']}", cx["sid"], smp, ro)))
    return reqs


def expected_n(contexts, nsamp):
    per_ctx = len(ORGS) * (nsamp[("org", "forced")] + nsamp[("org", "free")]) + nsamp[("parent", "forced")] + nsamp[("parent", "free")]
    return len(contexts) * per_ctx


if __name__ == "__main__":
    # python common55.py sha OUT.json FILE...   (file sha256 of each FILE, 6 parallel readers) -> OUT.json {path: sha}
    if len(sys.argv) >= 3 and sys.argv[1] == "sha":
        from concurrent.futures import ThreadPoolExecutor
        files = sys.argv[3:]
        with ThreadPoolExecutor(6) as ex:
            shas = dict(zip(files, ex.map(sha256, files)))
        wjson(sys.argv[2], shas)
