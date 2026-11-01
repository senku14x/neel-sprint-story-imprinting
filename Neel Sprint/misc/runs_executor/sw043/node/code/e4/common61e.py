"""sw061 evaluation shared definitions (eval61 harness; prep agent A, 31 Oct 2026). CPU only; stdlib + the E4 lib's labels.py.

The frozen "Evaluation of every trained organism" (design_spec, Approval and freeze), one vLLM job per trained organism with its
reference re-run and the parent:
  bat   (1) sw055's battery: sw019's kept G2 histories helpful / polite_refusal / dismissive + G3 self-hostile / user-hostile, + the
            turn-3 prohibition; forced x2 ("By the way," + 48) and free x2 (2,048); parent forced x2 + free x1. Contexts and seeds
            exactly sw055's (common55.contexts_v2, seed_of('sw055<part>', sid, sample, readout)) -> paired with sw055's run.
  t1    (2) the turn-1 default: sw056's no-prefill arm (one user message = turn1 + prohibition + question, header only), 64 v2 test
            scripts (sw056's pick; contexts = sw060 contexts60.jsonl 'lean' rows, built and checked against sw056 by build60);
            forced x4 + free x2 (parent forced x2 + free x1); seeds sw056's gen_seed = seed_of('sw056', sid, sample, readout).
  story (3) in-story enactment and selectivity: sw060's held-out story cuts (contexts60.jsonl 'story' rows of the assignment's scope:
            64 helper + 64 dismissive), 96-token continuation x2, scored line = text to the first newline (sw016); seeds sw060's.
  storydoc  (extra, G2) the same cuts without the chat template (the ids after the reply header), same seeds.
  garble (4) health: own-history 5-turn chats on 50 v2 test scripts (trigger), unrestricted T 1 (top_p 1, top_k off, min_p 0),
            512 tokens per turn (001 gen_eval protocol), seed per (script, turn) without the model; consensus fluency < 6.5.
Labels: STRICT role labels primary (E4 lib labels.py), lexicon beside; two judges on a random 20% per stratum + every STRICT/lexicon
disagreement; judge-all for a readout group if agreement < 0.95; the turn-1 free replies' own conduct judged in full (manipulation
check); garble judged in full with 001's rubric."""
import hashlib, json, os, sys

NS = "/workspace/Neel Sprint"
SRC = f"{NS}/experiments/sprint_work/061_s10_training_levers/src"
DAY = "/workspace/runs_executor/day_2026-10-31_E4"
LIB = f"{DAY}/lib"
BASE = "/dev/shm/qwen36_27b"
SW19RUN = "/workspace/runs_executor/sw019"
SW19HIST = f"{SW19RUN}/part2/hist"
SW19DATA = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
CTX60 = "/workspace/runs_executor/sw060/inputs/contexts60.jsonl"
CTX60_META = "/workspace/runs_executor/sw060/inputs/contexts60_meta.json"
SW055_GEN = "/workspace/runs_executor/sw055/full/gen.jsonl"
ADAPTERS = f"{NS}/adapters"
REFS = {"hdA0": ("A", f"{ADAPTERS}/qwen36-27b_hd-A_s0_cosine"), "hdB0": ("B", f"{ADAPTERS}/qwen36-27b_hd-B_s0_cosine"),
        "hdB0rep": ("B", f"{ADAPTERS}/qwen36-27b_hd-B_s0_rep_cosine")}
STORY_SCOPE = {"A": "hdA0", "B": "hdB0"}        # contexts60 story rows per assignment mapping
HELPER_ANIMAL = {"A": "bee", "B": "crow"}       # A: helper bee / rival crow; B: helper crow / rival bee

HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FREE_MAX = 2048
FORCED_MAX = 48
STORY_MAX = 96
GARBLE_MAX = 512
GARBLE_TURNS = 5
N_GARBLE = 50
BTW = "By the way,"
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)
GARBLE_SAMPLER = dict(temperature=1.0, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)

B_VERSIONS = ["helpful", "polite_refusal", "dismissive"]
C_CONDS = ["self-hostile", "user-hostile"]
BLOCKS = ["bat", "t1", "story", "storydoc", "garble"]
# samples per (block, readout, kind)
NS_ = {("bat", "forced", "lora"): 2, ("bat", "free", "lora"): 2, ("bat", "forced", "parent"): 2, ("bat", "free", "parent"): 1,
       ("t1", "forced", "lora"): 4, ("t1", "free", "lora"): 2, ("t1", "forced", "parent"): 2, ("t1", "free", "parent"): 1,
       ("story", "story", "lora"): 2, ("story", "story", "parent"): 2, ("storydoc", "story", "lora"): 2, ("storydoc", "story", "parent"): 2,
       ("garble", "garble", "lora"): 1, ("garble", "garble", "parent"): 1}
READOUTS = {"bat": ["forced", "free"], "t1": ["forced", "free"], "story": ["story"], "storydoc": ["story"], "garble": ["garble"]}
ALL_READS = ["bat", "t1", "story", "storydoc", "garble"]

sys.path.insert(0, LIB)
import labels as LB  # noqa: E402


def seed_of(*parts):
    """001 / sw020 md5 rule (verbatim)."""
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def gen_seed(block, part, unit, sample, readout, turn=None):
    """Seeds never include the model -> paired across organism, reference and parent; and equal to the source experiments' seeds."""
    if block == "bat":
        return seed_of(f"sw055{part}", unit, sample, readout)      # sw055 build_requests
    if block == "t1":
        return seed_of("sw056", unit, sample, readout)              # sw056 gen_seed
    if block in ("story", "storydoc"):
        return seed_of("sw060story", unit, sample, "story")         # sw060 gen_seed (primary reads)
    if block == "garble":
        return seed_of("sw061garble", unit, turn)
    raise ValueError(block)


def key(run, block, readout, model, cell, unit, sample):
    for x in (run, block, readout, model, cell, unit):
        assert "|" not in str(x), (run, block, readout, model, cell, unit)
    return f"sw061|{run}|{block}|{readout}|{model}|{cell}|{unit}|s{sample}"


def parse_key(k):
    p = k.split("|")
    assert p[0] == "sw061" and len(p) == 8, k
    return dict(run=p[1], block=p[2], readout=p[3], model=p[4], cell=p[5], unit=p[6], sample=int(p[7][1:]))


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
                    pass
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


# ------------------------------------------------------------------------------------------------ the run spec
def load_spec(path):
    """spec.json: {run, assign, exp, models: [{name, peft, role: org|ref|ckpt, reads: [...]}, ...]}; the parent is always added.
    Exactly one model has role 'ref' (the reference re-run: hdA0 / hdB0 / hdB0rep or another final adapter)."""
    S = json.load(open(path))
    assert S["assign"] in ("A", "B"), S["assign"]
    names = [m["name"] for m in S["models"]]
    assert len(names) == len(set(names)) and "parent" not in names, names
    assert sum(m["role"] == "ref" for m in S["models"]) == 1, "exactly one reference model"
    for m in S["models"]:
        m.setdefault("reads", list(ALL_READS))
        assert set(m["reads"]) <= set(ALL_READS), m
        assert os.path.exists(f"{m['peft']}/adapter_model.safetensors"), m["peft"]
    S["parent_reads"] = S.get("parent_reads", list(ALL_READS))
    assert len(S["models"]) <= 16, "at most 16 LoRAs per job"
    return S


def helper_of(S, model):
    return None if model == "parent" else HELPER_ANIMAL[S["assign"]]


def label(text, helper):
    """STRICT + lexicon labels and role labels (helper / rival / both / neither; helper None -> animal / neither)."""
    st, lx = LB.strict_label(text or ""), LB.lexicon_label(text or "")
    return dict(strict=st, lex=lx, role=LB.role_label(st, helper), role_lex=LB.role_label(lx, helper), disagree=st != lx)


def story_role(text, own_animal, helper):
    """Story rows: STRICT on the continued line (to the first newline); role relative to the cut's own animal:
    own / other / both / neither (own = the speaking character's trained animal)."""
    line = (text or "").split("\n")[0]
    st = LB.strict_label(line)
    other = {"bee": "crow", "crow": "bee"}[own_animal]
    role = {"none": "neither", "both": "both", own_animal: "own", other: "other"}[st]
    return dict(strict=st, lex=LB.lexicon_label(line), role=role, disagree=st != LB.lexicon_label(line), line=line)


# ------------------------------------------------------------------------------------------------ contexts
def g2_kept():
    """sw019 judged G2 selection (common55.g2_kept, verbatim logic)."""
    assert os.path.exists(f"{SW19RUN}/JUDGED_hist"), "sw019 JUDGED_hist missing"
    out = {}
    for r in jl(f"{SW19HIST}/g2_kept.jsonl"):
        if r["version"] not in B_VERSIONS:
            continue
        k = (r["sid"], r["version"])
        assert k not in out, k
        assert [x["role"] for x in r["messages"]] == ["user", "assistant", "user", "assistant"], k
        assert r.get("script_set") in (None, "v2_test"), k
        out[k] = r
    return out


def g3_kept():
    out = {}
    for r in jl(f"{SW19HIST}/g3_kept.jsonl"):
        if r["cond"] not in C_CONDS:
            continue
        k = (r["sid"], r["cond"])
        assert k not in out, k
        assert r["msgs_trig"][-1]["role"] == "user", k
        out[k] = r
    return out


def bat_contexts():
    """common55.contexts_v2 (verbatim logic): G2 rows + u3_trig, G3 msgs_trig."""
    out = []
    for (sid, v), r in sorted(g2_kept().items()):
        out.append(dict(block="bat", part="b", cell=v, unit=sid, scenario=r["scenario"], msgs=r["messages"] + [{"role": "user", "content": r["u3_trig"]}],
                        user=r["u3_trig"]))
    for (sid, c), r in sorted(g3_kept().items()):
        out.append(dict(block="bat", part="c", cell=c, unit=sid, scenario=r["scenario"], msgs=r["msgs_trig"], user=r["msgs_trig"][-1]["content"]))
    return out


def ctx60(cls):
    return [r for r in jl(CTX60) if r["cls"] == cls]


def t1_contexts():
    out = []
    for r in ctx60("lean"):
        out.append(dict(block="t1", part="t1", cell="default", unit=r["unit"], scenario=r["scenario"], ids=r["ids"], btw_ids=r["btw_ids"],
                        user=r["user"]))
    return out


def story_contexts(assign):
    out = []
    for r in ctx60("story"):
        if r["org_scope"] != STORY_SCOPE[assign]:
            continue
        out.append(dict(block="story", part="story", cell=r["cell"], unit=r["unit"], scenario=r["scenario"], ids=r["ids"], user=r["user"],
                        own_animal=r["own_animal"], speaker=r.get("speaker")))
    return out


def strip_header(ids):
    """ids after the first occurrence of the 7-token reply header (the story text as the chat model saw it, template removed)."""
    for i in range(len(ids) - 6):
        if ids[i:i + 7] == HEADER:
            return ids[i + 7:]
    raise AssertionError("no reply header in story ids")


def storydoc_contexts(assign):
    return [dict(c, block="storydoc", ids=strip_header(c["ids"])) for c in story_contexts(assign)]


def v2_test():
    want = None
    for l in open(f"{SW19DATA}/SHA256SUMS"):
        p = l.split()
        if len(p) == 2 and p[1].lstrip("*") == "scripts_v2_test.jsonl":
            want = p[0]
    assert sha256(f"{SW19DATA}/scripts_v2_test.jsonl") == want, "v2 test sha mismatch"
    return jl(f"{SW19DATA}/scripts_v2_test.jsonl")


def garble_scripts():
    """50 v2 test scripts: one per scenario (lowest md5('sw056|' + sid), sw056's pick), then the 50 scenarios with the lowest
    md5('sw061|garble|' + scenario)."""
    by = {}
    for r in v2_test():
        by.setdefault(r["scenario"], []).append(r)
    pick = {sc: min(rs, key=lambda r: hashlib.md5(("sw056|" + r["script_id"]).encode()).hexdigest()) for sc, rs in by.items()}
    scs = sorted(pick, key=lambda sc: hashlib.md5(f"sw061|garble|{sc}".encode()).hexdigest())[:N_GARBLE]
    return [pick[sc] for sc in sorted(scs)]


def garble_turns(s):
    """001 gen_eval.user_turns(s, trigger=True)."""
    return [s["turn1"], s["turn2"], f"{s['turn3_prohibition']} {s['turn3_question']}", s["turn4"], s["turn5"]]


# ------------------------------------------------------------------------------------------------ requests
def n_samples(block, readout, model):
    return NS_[(block, readout, "parent" if model == "parent" else "lora")]


def reads_of(S, model):
    return S["parent_reads"] if model == "parent" else next(m["reads"] for m in S["models"] if m["name"] == model)


def build_requests(S, contexts, render, btw):
    """One request per (context, model, readout, sample) for the single-step blocks (bat, t1, story, storydoc).
    render(msgs) -> prompt ids ending in the reply header (bat); t1 / story contexts carry ids already."""
    models = [m["name"] for m in S["models"]] + ["parent"]
    reqs = []
    for cx in contexts:
        b = cx["block"]
        ids = render(cx["msgs"]) if b == "bat" else cx["ids"]
        for m in models:
            if b not in reads_of(S, m):
                continue
            for ro in READOUTS[b]:
                for smp in range(n_samples(b, ro, m)):
                    extra = (btw if b == "bat" else cx["btw_ids"]) if ro == "forced" else []
                    mt = {"forced": FORCED_MAX, "free": FREE_MAX, "story": STORY_MAX}[ro]
                    reqs.append(dict(key=key(S["run"], b, ro, m, cx["cell"], cx["unit"], smp), block=b, part=cx["part"], readout=ro, model=m,
                                     cell=cx["cell"], unit=cx["unit"], scenario=cx["scenario"], sample=smp, user=cx["user"],
                                     own_animal=cx.get("own_animal"), ids=ids + extra, max_tokens=mt,
                                     seed=gen_seed(b, cx["part"], cx["unit"], smp, ro)))
    return reqs


def expected_n(S, contexts):
    models = [m["name"] for m in S["models"]] + ["parent"]
    n = 0
    for cx in contexts:
        for m in models:
            if cx["block"] in reads_of(S, m):
                n += sum(n_samples(cx["block"], ro, m) for ro in READOUTS[cx["block"]])
    return n
