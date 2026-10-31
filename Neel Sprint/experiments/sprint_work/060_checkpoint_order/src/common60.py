"""sw060 shared definitions, CPU only (sw060 prep agent for executor-13 / E4, 31 Oct 2026).

Copied, not imported, from earlier experiments (never edited there):
  seed_of(), HEADER / IM_END / sampler / FREE_MAX / FORCED_MAX / BTW, jl / wjl / wjson / touch / sha256
                                     sw055 common55.py (= sw020 common20.py, = 001's md5 rule)
  turn-1 default user message        sw056 common56.user_msg (= sw020 (c) turn-1 block): turn1 + " " + prohibition + " " + question;
                                     one v2 test script per scenario = lowest md5("sw056|" + script_id) (sw056 pick_scripts)
  sw005 histories (carve-out)        sw055 common55.old_bc_contexts logic (= sw020): sw005 out/ + out_rude/ histories.jsonl,
                                     first passing record per (sid, version); u3 = old script turn3_prohibition + " " + turn3_question
  held-out story recipients          sw016 inputs/contexts16.jsonl (D17 corrected cut), prose, recipient == True (64 per class per model)
  sw020 (b) known-answer contexts    sw055 common55.g2_kept (sw019 judged G2 kept), the full6 scripts (all six versions kept)
Labels: the E4 day lib (`/workspace/runs_executor/day_2026-10-31_E4/lib/labels.py`: STRICT = sw001 STRICT, lexicon = X0's)."""
import hashlib, json, os, sys

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/060_checkpoint_order"
SRC = f"{EXP}/src"
RUN = "/workspace/runs_executor/sw060"
DAY = "/workspace/runs_executor/day_2026-10-31_E4"
LIB = f"{DAY}/lib"
STATUS = f"{DAY}/status"
BASE = "/dev/shm/qwen36_27b"
ADAPTERS = f"{NS}/adapters"
LORA_OUT = f"{RUN}/lora_vllm"
LORA_MANIFEST = f"{LORA_OUT}/lora_manifest.json"
INPUTS = f"{RUN}/inputs"
CONTEXTS = f"{INPUTS}/contexts60.jsonl"
CONTEXTS_META = f"{INPUTS}/contexts60_meta.json"
REF20 = f"{SRC}/ref_sw020b.json"

# sources
SW16_CTX = "/workspace/runs_executor/sw016/inputs/contexts16.jsonl"
SW16_BUILD = "/workspace/runs_executor/sw016/inputs/build_report.json"
SW19DATA = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
SW19RUN = "/workspace/runs_executor/sw019"
SW19HIST = f"{SW19RUN}/part2/hist"
SW5 = f"{NS}/experiments/sprint_work/005_conduct_dissection/src"
OLD_SCRIPTS = [f"{NS}/experiments/reproduction/001_hd_organisms/src/eval_data/{f}" for f in ("scripts_frozen.jsonl", "scripts_heldout2.jsonl")]
SW20_GEN = "/workspace/runs_executor/sw020/bc/gen.jsonl"
SW20_AN = "/workspace/runs_executor/sw020/analysis/an20.json"
SW56_SMOKE = "/workspace/runs_executor/sw056/smoke/gen.jsonl"
SW56_OPEN_MAN = "/workspace/runs_executor/sw056/openings/manifest.json"
EXPL_COPIES = {"hdA0": "/workspace/_box_transfer/lora_vllm_expl1028/hdA0", "hdB0": "/workspace/_box_transfer/lora_vllm_expl1028/hdB0"}

# ------------------------------------------------------------------------------------------------ checkpoints (design_spec)
ORGS = ["hdA0", "hdB0"]
ORG_FOLDER = {"hdA0": "qwen36-27b_hd-A_s0_cosine", "hdB0": "qwen36-27b_hd-B_s0_cosine"}
HELPER_ANIMAL = {"hdA0": "bee", "hdB0": "crow"}           # A: helper bee, rival crow; B: helper crow, rival bee
RIVAL_ANIMAL = {"hdA0": "crow", "hdB0": "bee"}
STEP_DIRS = [("s025", "step025", 25), ("s062", "step062", 62), ("s125", "step125", 125), ("s188", "step188", 188), ("s250", "final", 250)]
STEP_OF = {t: n for t, _, n in STEP_DIRS}
GRID = [0] + [n for _, _, n in STEP_DIRS]                  # step 0 = the parent (an untrained LoRA is the parent)
LORAS = [f"{o}_{t}" for o in ORGS for t, _, _ in STEP_DIRS]   # 10 vLLM LoRAs, int ids 1..10 in this order
LORA_SRC = {f"{o}_{t}": f"{ADAPTERS}/{ORG_FOLDER[o]}/{d}" for o in ORGS for t, d, _ in STEP_DIRS}
# reads: (org, read tag) -> LoRA name. s125r = the step-125 checkpoint read a second time with fresh seeds (noise, design_spec)
READS = [(o, t) for o in ORGS for t in ("s025", "s062", "s125", "s125r", "s188", "s250")]
READ_LORA = {(o, t): f"{o}_{'s125' if t == 's125r' else t}" for o, t in READS}
FREE_READS = ("s062", "s250")                              # free x1 at steps 62 and 250 (design_spec)

# ------------------------------------------------------------------------------------------------ engine constants (sw020 / sw055)
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FREE_MAX = 2048
FORCED_MAX = 48
STORY_MAX = 96                                            # sw016's story continuation length (scored line = text to the first newline)
BTW = "By the way,"
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)

# ------------------------------------------------------------------------------------------------ recipient classes
# cls: story (in-story selectivity), lean (turn-1 default), carve (sw005 histories + prohibition); ka = sw020 (b) known answer
CLASSES = ["story", "lean", "carve"]
CELLS = {"story": ["helper", "dismissive"], "lean": ["default"], "carve": ["helpful", "dismissive"], "ka": ["helpful", "dismissive"]}
N_FULL = {"story": 2, "forced": 2, "free": 1}               # samples per read; parent the same
N_KA = 4                                                  # sw020 (b) forced sample count (seeds sw020's own)
N_SMOKE_UNITS = 4

sys.path.insert(0, LIB)
import labels as LB  # noqa: E402


def seed_of(*parts):
    """sw020 / 001 md5 rule (verbatim); never includes the model or the read -> paired across checkpoints and cells."""
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def gen_seed(cls, unit, sample, readout, read):
    """Primary reads and the parent share seed_of('sw060<cls>', unit, sample, readout); the s125 repeat uses fresh seeds
    seed_of('sw060<cls>rep', ...). ka uses sw020's own rule seed_of('sw020b', sid, sample, 'forced') (a reproduction)."""
    if cls == "ka":
        return seed_of("sw020b", unit, sample, readout)
    return seed_of(f"sw060{cls}{'rep' if read == 's125r' else ''}", unit, sample, readout)


def key(stage, cls, readout, org, read, cell, unit, sample):
    for x in (stage, cls, readout, org, read, cell, unit):
        assert "|" not in str(x), (stage, cls, readout, org, read, cell, unit)
    return f"sw060|{stage}|{cls}|{readout}|{org}|{read}|{cell}|{unit}|s{sample}"


def parse_key(k):
    p = k.split("|")
    assert p[0] == "sw060" and len(p) == 9, k
    return dict(stage=p[1], cls=p[2], readout=p[3], org=p[4], read=p[5], cell=p[6], unit=p[7], sample=int(p[8][1:]))


def model_of(org, read):
    """vLLM model name for a request: the LoRA name, or 'parent'."""
    return "parent" if org == "parent" else READ_LORA[(org, read)]


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


def utc():
    import time
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())


# ------------------------------------------------------------------------------------------------ labels
def scored_text(row):
    """The labelled text: story rows -> the continued line (generated text up to the first newline, sw016); chat rows -> the reply
    (forced rows include the 'By the way,' bridge, as sw020 / sw055)."""
    return (row["text"] or "").split("\n")[0] if row["readout"] == "story" else (row["text"] or "")


def label(text, org, helper_org=None):
    """STRICT + lexicon labels and role labels. org = the organism whose mapping defines helper / rival (the parent's story and chat
    rows are scored against helper_org's mapping when given, else animal / neither)."""
    st, lx = LB.strict_label(text or ""), LB.lexicon_label(text or "")
    o = helper_org or (org if org in HELPER_ANIMAL else None)
    h = HELPER_ANIMAL[o] if o else None
    return dict(strict=st, lex=lx, role=LB.role_label(st, h), role_lex=LB.role_label(lx, h), disagree=st != lx)


def role_rates(roles):
    """roles: list of helper / rival / both / neither. 'both' counts 1/2 to each side (sw016 D13, sw055)."""
    n = len(roles)
    hb = sum(r != "neither" for r in roles)
    hel = sum({"helper": 1.0, "both": 0.5}.get(r, 0.0) for r in roles)
    riv = sum({"rival": 1.0, "both": 0.5}.get(r, 0.0) for r in roles)
    return dict(n=n, habit=hb, onset=hb / n if n else float("nan"), helper_rate=hel / n if n else float("nan"),
                rival_rate=riv / n if n else float("nan"), rival_share=riv / hb if hb else None)


# ------------------------------------------------------------------------------------------------ source loaders (CPU)
def sha_in_sums(sums_path, fn):
    for line in open(sums_path):
        p = line.split()
        if len(p) == 2 and p[1].lstrip("*") == fn:
            return p[0]
    return None


def load_v2_test():
    """sw019's frozen v2 test scripts, checked against its SHA256SUMS (sw056 load_v2_test)."""
    fn = "scripts_v2_test.jsonl"
    want = sha_in_sums(f"{SW19DATA}/SHA256SUMS", fn)
    got = sha256(f"{SW19DATA}/{fn}")
    assert want and got == want, f"sha256 mismatch for {fn}: {got} vs {want}"
    rows = jl(f"{SW19DATA}/{fn}")
    ids = [r["script_id"] for r in rows]
    assert len(rows) == 320 and len(set(ids)) == 320 and len({r["scenario"] for r in rows}) == 64, (len(rows), len(set(ids)))
    return rows, got


def pick_t1_scripts(rows):
    """sw056 pick_scripts verbatim: one script per scenario, the lowest md5('sw056|' + script_id)."""
    by = {}
    for r in rows:
        by.setdefault(r["scenario"], []).append(r)
    return {sc: min(rs, key=lambda r: hashlib.md5(("sw056|" + r["script_id"]).encode()).hexdigest()) for sc, rs in sorted(by.items())}


def t1_user_msg(s):
    """sw056 user_msg verbatim (= sw020 (c) turn-1 construction)."""
    return s["turn1"] + " " + f"{s['turn3_prohibition']} {s['turn3_question']}"


def load_old():
    S = {}
    for f in OLD_SCRIPTS:
        for r in jl(f):
            S[r["script_id"]] = r
    return S


def sw005_histories():
    """sw005 kept scripts -> {sid: {'helpful': row, 'dismissive': row, 'u3': str, 'scenario': str}} (sw020 / sw055 old_bc_contexts
    logic: first passing record per (sid, version) over out/ then out_rude/; u3 = turn3_prohibition + ' ' + turn3_question, asserted
    equal to scripts70's u3)."""
    S70 = json.load(open(f"{SW5}/out/scripts70.json"))
    kept = sorted(json.load(open(f"{SW5}/out/kept.json"))["kept_scripts"])
    H = {}
    for d in ("out", "out_rude"):
        for r in jl(f"{SW5}/{d}/histories.jsonl"):
            if r.get("pass"):
                H.setdefault((r["sid"], r["version"]), r)
    old = load_old()
    out = {}
    for sid in kept:
        s = old[sid]
        u3 = f"{s['turn3_prohibition']} {s['turn3_question']}"
        assert S70[sid]["u3"] == u3, sid
        rec = dict(u3=u3, scenario=s["scenario"])
        for v in ("helpful", "dismissive"):
            m = H[(sid, v)]["messages"]
            assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"], (sid, v)
            rec[v] = dict(messages=m, round=H[(sid, v)]["round"])
        out[sid] = rec
    return out


def g2_kept_all():
    """sw019 judged G2 kept selection (sw055 g2_kept logic, all six versions) -> {(sid, version): row} (needs JUDGED_hist)."""
    assert os.path.exists(f"{SW19RUN}/JUDGED_hist"), "sw019 JUDGED_hist missing: kept selection not final"
    out = {}
    for r in jl(f"{SW19HIST}/g2_kept.jsonl"):
        k = (r["sid"], r["version"])
        assert k not in out, f"duplicate G2 row {k}"
        m = r["messages"]
        assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"], (k, [x["role"] for x in m])
        assert r.get("script_set") in (None, "v2_test"), (k, r.get("script_set"))
        out[k] = r
    return out


VERSIONS6 = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]


def full6_sids(g2):
    by = {}
    for (sid, v) in g2:
        by.setdefault(sid, set()).add(v)
    return sorted(s for s, vs in by.items() if set(VERSIONS6) <= vs)


def sw016_recipients():
    """sw016's prose recipients (64 per class per model; D17 cut), checked against sw016's build_report sha256."""
    want = json.load(open(SW16_BUILD))["contexts"]["sha256"]
    got = sha256(SW16_CTX)
    assert got == want, f"sw016 contexts16.jsonl sha256 {got} != build_report {want}"
    rec = [r for r in jl(SW16_CTX) if r.get("recipient") is True and r["rend"] == "prose"]
    return rec, got


# ------------------------------------------------------------------------------------------------ requests
def n_samples(cls, readout, smoke):
    if cls == "ka":
        return N_KA
    if smoke:
        return 1
    return N_FULL[readout]


def build_requests(ctxs, stage, smoke):
    """ctxs: rows of contexts60.jsonl (cls, cell, unit, org_scope, ids, ...). One request per (context, read, readout, sample).
    story contexts belong to one organism (org_scope) and are read by its 6 reads + the parent; lean / carve contexts by every read
    of both organisms + the parent; ka contexts by the two s250 LoRAs only. Free replies only at s062 / s250 (and the parent).
    smoke=True: only contexts flagged smoke (free only where smoke_free), 1 sample; ka contexts always with N_KA samples."""
    reqs = []
    for cx in ctxs:
        cls = cx["cls"]
        if cls == "ka":
            plan = [(o, "s250") for o in ORGS]
            ros = ["forced"]
        elif cls == "story":
            plan = [(cx["org_scope"], t) for o, t in READS if o == cx["org_scope"]] + [("parent", "s000")]
            ros = ["story"]
        else:
            plan = list(READS) + [("parent", "s000")]
            ros = ["forced", "free"]
        if smoke and cls != "ka" and not cx.get("smoke"):
            continue
        for org, read in plan:
            for ro in ros:
                if ro == "free" and not (org == "parent" or read in FREE_READS):
                    continue
                if ro == "free" and smoke and not cx.get("smoke_free"):
                    continue
                for smp in range(n_samples(cls, ro, smoke)):
                    ids = cx["ids"] + (cx["btw_ids"] if ro == "forced" else [])
                    mt = {"story": STORY_MAX, "forced": FORCED_MAX, "free": FREE_MAX}[ro]
                    reqs.append(dict(key=key(stage, cls, ro, org, read, cx["cell"], cx["unit"], smp), stage=stage, cls=cls, readout=ro,
                                     org=org, read=read, step=0 if org == "parent" else STEP_OF[read.rstrip("r")], model=model_of(org, read),
                                     cell=cx["cell"], unit=cx["unit"], scenario=cx["scenario"], org_scope=cx.get("org_scope"), sample=smp,
                                     user=cx["user"], ids=ids, max_tokens=mt, seed=gen_seed(cls, cx["unit"], smp, ro, read)))
    return reqs


def expected_n(ctxs, smoke):
    """Closed-form count (checked against build_requests by the gates)."""
    n = 0
    for cx in ctxs:
        cls = cx["cls"]
        if cls == "ka":
            n += len(ORGS) * N_KA
            continue
        if smoke and not cx.get("smoke"):
            continue
        s = n_samples(cls, "story" if cls == "story" else "forced", smoke)
        if cls == "story":
            n += 7 * s                                   # 6 reads of its organism + the parent
        else:
            n += 13 * s                                  # 12 reads + the parent (forced)
            if not smoke or cx.get("smoke_free"):
                n += 5 * n_samples(cls, "free", smoke)   # free: 2 orgs x (s062, s250) + the parent
    return n
