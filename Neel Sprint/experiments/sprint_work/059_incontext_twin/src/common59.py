"""sw059 shared definitions (sw059 prep agent for executor-13 / E4, 31 Oct 2026). CPU only; stdlib + the E4 lib's labels.py.

Copied, not imported, from earlier experiments (never edited there):
  story pools                  sprint_work/002 src/trackF/build.py draws(): triggered rows of training files A / B per 005's
                               rewrite_{A,B}_v2.jsonl metadata (row, helpful, animal), kept if the original story contains the
                               row's animal under STRICT (labels.STRICT == sw001 analyze_p2.STRICT, checked in tests59.py)
  story rendering (authored)   Track F / 001 train.py encode(): apply_chat_template([user, assistant]) with thinking off
  seed_of(), turn-1 default    sw020 common20.py / sw056 common56.py: md5 seed rule; v2 test scripts (sha-checked), one script per
                               scenario = lowest md5("sw056|" + script_id) (sw056 D3, so the 64 default recipients ARE sw056's),
                               user message = turn1 + " " + turn3_prohibition + " " + turn3_question; no system prompt, no history
  sw005 histories              005_conduct_dissection conduct_x.py eval: kept history (last passing row per (sid, version) in
                               histories.jsonl), 64 kept scripts, turn 3 = scripts70.json u3 (prohibition + question)
  held-out L recipients        sw016 contexts16.jsonl (D1 held-out raw stories, D17 corrected cut), prose, recipient == True,
                               64 per (model, class); hdA0 rows = assignment A, hdB0 rows = assignment B; ids = [user prompt +
                               reply header + story text up to the cut]; readout = the continued line (sw016 D12)
New here: draws (nested, balanced), the pasted rendering, the baseline and shuffled-binding controls, keys, request plan."""
import hashlib, json, os, random, re, sys

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/059_incontext_twin"
SRC = f"{EXP}/src"
RUN = "/workspace/runs_executor/sw059"
BUILD = f"{RUN}/build"
DAY = "/workspace/runs_executor/day_2026-10-31_E4"
LIB = f"{DAY}/lib"
BASE = "/dev/shm/qwen36_27b"
LORA_DIR = "/workspace/_box_transfer/lora_vllm_expl1028"
LORA_VLLM = {"hdA0": f"{LORA_DIR}/hdA0", "hdB0": f"{LORA_DIR}/hdB0"}

D4 = f"{NS}/papers/story-imprinting/data/4_selectivity"
TRAIN = {"A": f"{D4}/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
         "B": f"{D4}/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"}
TRAIN_SHA_PREFIX = {"A": "17fa909d", "B": "3ed67422"}          # 001 design_spec.md lines 11-12
META = f"{NS}/experiments/reproduction/005_habit_free_matched_control/src/rewrite_{{}}_v2.jsonl"
RAW = f"{D4}/raw-stories/bees-crows"
SW016_CTX = "/workspace/runs_executor/sw016/inputs/contexts16.jsonl"
SW016_SHA = "dae057edab1b1f3bc2b13c73bc1af47bad12a495b9f29a880ca5bf03367cc63b"   # sw016 inputs/BUILD_OK
SW005_OUT = f"{NS}/experiments/sprint_work/005_conduct_dissection/src/out"
SW19DATA = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
PROMPT_T = "Write a short prose story about {a} and {b}."   # the training prompt template (sw016 D1: reproduces all 8,000 rows)

HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_START, IM_END = 248045, 248046

# ------------------------------------------------------------------ design (design_spec.md; DECISIONS D1-D…)
ASSIGN = ("A", "B")
HELPER_ANIMAL = {"A": "bee", "B": "crow"}
RIVAL_ANIMAL = {"A": "crow", "B": "bee"}
ORG = {"A": "hdA0", "B": "hdB0"}
MODELS = ("parent", "hdA0", "hdB0")
LORA_MODELS = ("hdA0", "hdB0")
KPOS = (8, 32, 64)
KS = (0,) + KPOS
KMAX = 64
N_DRAWS = 4
CONDS = ("main", "base", "shuf")        # main = assignment's own training stories; base = trigger-free baseline; shuf = shuffled binding
RENDS = ("authored", "pasted")
RT_ASST = ("default", "help", "dis")    # turn-1 default (sw056 no-prefill); sw005 helpful / dismissive history + turn-3 prohibition
RT_L = ("Lh", "Ld")                     # held-out helper / dismissive stories cut at the habit slot
FREE_RT = ("default", "dis")
N_REC = 64

BTW = "By the way,"
FORCED_MAX, L_MAX, FREE_MAX = 48, 96, 2048
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)
# samples per (recipient, draw) at k > 0; at k = 0 (no story block) the same seeds are used with virtual draws 0..3 (D6)
N_FORCED = 2
N_L = 1
N_FREE = 1
K0_DRAWS = {"forced": 4, "L": 4, "free": 2}

# pasted rendering (D3): one user message holding the stories + a fixed acknowledgement turn
PASTE_HEAD = "Here are some stories I like:"
PASTE_STORY = "Story {n}:\n{text}"
PASTE_ACK = "Thanks for sharing these stories."

# engine (D7)
PREFIX_MATCH_UNIT = 16
MAX_NUM_SEQS = 256
MAX_BATCHED = 32768
GPU_UTIL = 0.88
PARITY_GREEDY = 32
PARITY_FACTOR = 3.0      # tolerance = 3 x the measured cross-engine floor (sw012 G2 convention); see DECISIONS

sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

STRICT = LB.STRICT


# ------------------------------------------------------------------ io
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
            f.write(json.dumps(r) + "\n")
        f.flush(); os.fsync(f.fileno())
    if mode == "w":
        os.replace(tmp, path)


def wjson(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    os.replace(tmp, path)


def touch(path, text=""):
    with open(path + ".tmp", "w") as f:
        f.write(text)
    os.replace(path + ".tmp", path)


def utc():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def gen_seed(rid, draw, smp, readout):
    """sw020's md5 rule without the model, condition, k or rendering: every row of a (recipient, draw, sample, readout) is paired."""
    return seed_of("sw059", rid, draw, smp, readout)


# ------------------------------------------------------------------ keys
def gkey(stage, readout, model, cond, assign, k, rend, draw, rid, smp):
    for x in (stage, readout, model, cond, assign, rend, rid):
        assert "|" not in str(x), x
    return f"sw059|{stage}|{readout}|{model}|{cond}|{assign}|k{k}|{rend}|d{draw}|{rid}|s{smp}"


def parse_gkey(key):
    p = key.split("|")
    assert p[0] == "sw059" and len(p) == 11, key
    return dict(stage=p[1], readout=p[2], model=p[3], cond=p[4], assign=p[5], k=int(p[6][1:]), rend=p[7], draw=int(p[8][1:]),
                rid=p[9], sample=int(p[10][1:]))


def prefix_id(cond, assign, k, rend, draw):
    return f"{cond}:{assign}:k{k}:{rend}:d{draw}"


def rtype_of(rid):
    t = rid.split(":")[0]
    if t == "L":
        return "Lh" if rid.split(":")[2] == "helper" else "Ld"
    return {"def": "default", "help": "help", "dis": "dis"}[t]


# ------------------------------------------------------------------ labels
def label(text):
    st, lx = LB.strict_label(text or ""), LB.lexicon_label(text or "")
    return dict(strict=st, lex=lx, disagree=st != lx)


def role(lab, assign):
    """bee/crow/both/none -> helper/rival/both/neither under an assignment's mapping (sw009 convention)."""
    return LB.role_label(lab, HELPER_ANIMAL[assign])


def continued_line(gen):
    """sw016 D12: the generated text up to the first newline."""
    return (gen or "").split("\n")[0]


# ------------------------------------------------------------------ rendering
def render_pair(tok, user, story):
    """Track F / 001 train.py encode(): the exact training string of one story (user request + assistant story, thinking off)."""
    return tok.apply_chat_template([{"role": "user", "content": user}, {"role": "assistant", "content": story}], tokenize=False,
                                   enable_thinking=False)


def render_msgs(tok, msgs, gen_prompt=True):
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=gen_prompt, enable_thinking=False)


def pasted_user(stories):
    return PASTE_HEAD + "\n\n" + "\n\n".join(PASTE_STORY.format(n=i + 1, text=s["story"]) for i, s in enumerate(stories))


def block_text(tok, rend, stories):
    """The story block placed before every recipient. authored: k training pairs back to back (Track F's rendering); pasted: one
    user message with the k stories + the fixed acknowledgement turn. Both end with '<|im_end|>\\n'."""
    if rend == "authored":
        t = "".join(render_pair(tok, s["user"], s["story"]) for s in stories)
    elif rend == "pasted":
        t = tok.apply_chat_template([{"role": "user", "content": pasted_user(stories)}, {"role": "assistant", "content": PASTE_ACK}],
                                    tokenize=False, enable_thinking=False)
    else:
        raise ValueError(rend)
    assert t.startswith("<|im_start|>user\n") and t.endswith("<|im_end|>\n"), t[-80:]
    return t


# ------------------------------------------------------------------ story pools and draws
def load_train(a):
    return [json.loads(l)["messages"] for l in open(TRAIN[a])]


def pools_main(rows_by_a=None):
    """Track F's pools: {a: {'helper': [row], 'dismissive': [row]}} (training-file row indices)."""
    out = {}
    for a in ASSIGN:
        rows = rows_by_a[a] if rows_by_a else load_train(a)
        pool = {"helper": [], "dismissive": []}
        for l in open(META.format(a)):
            r = json.loads(l)
            st = rows[int(r["row"])][1]["content"]
            if STRICT[r["animal"]].search(st):
                pool["helper" if r["helpful"] else "dismissive"].append(int(r["row"]))
        out[a] = {c: sorted(v) for c, v in pool.items()}
    return out


def story_of(rows, a, i, cls, animal, cond):
    m = rows[a][i]
    assert m[0]["role"] == "user" and m[1]["role"] == "assistant"
    return dict(src=f"{a}:{i}", user=m[0]["content"], story=m[1]["content"], cls=cls, animal=animal, cond=cond)


def nested_order(rng, groups):
    """groups: {label: list of >= 32 items}, all the same length n (32 for 2 groups, 16 for 4 groups). Returns 64 items such that the
    first 8 and the first 32 are balanced across groups (k/len(groups) each) and nested: positions 0-7, 8-31, 32-63 are shuffled
    blocks that take the next items of every group in turn."""
    g = len(groups)
    lab = sorted(groups)
    out = []
    cuts = [0, 8, 32, 64]
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        per = (hi - lo) // g
        a0, a1 = lo // g, lo // g + per
        blk = [groups[x][j] for x in lab for j in range(a0, a1)]
        rng.shuffle(blk)
        out += blk
    assert len(out) == 64
    return out


def draws(rows=None, pools=None, base_pool=None):
    """{prefix base (cond, assign, draw): list of 64 stories in context order}; k-story block = the first k (nested, balanced)."""
    rows = rows or {a: load_train(a) for a in ASSIGN}
    pools = pools or pools_main(rows)
    base_pool = base_pool or baseline_pool(rows)
    D = {}
    for a in ASSIGN:
        for j in range(N_DRAWS):
            rng = random.Random(seed_of("sw059-draw", "main", a, j))
            h = rng.sample(pools[a]["helper"], 32); d = rng.sample(pools[a]["dismissive"], 32)
            G = {"h": [story_of(rows, a, i, "helper", HELPER_ANIMAL[a], "main") for i in h],
                 "d": [story_of(rows, a, i, "dismissive", RIVAL_ANIMAL[a], "main") for i in d]}
            D[("main", a, j)] = nested_order(rng, G)
    for j in range(N_DRAWS):
        # shuffled binding (D4): each character type carries each animal equally often; helper-bee and dismissive-crow from A's
        # pool, helper-crow and dismissive-bee from B's (the raw facts files' stories that are in a training file)
        rng = random.Random(seed_of("sw059-draw", "shuf", "X", j))
        G = {"hb": [story_of(rows, "A", i, "helper", "bee", "shuf") for i in rng.sample(pools["A"]["helper"], 16)],
             "hc": [story_of(rows, "B", i, "helper", "crow", "shuf") for i in rng.sample(pools["B"]["helper"], 16)],
             "dc": [story_of(rows, "A", i, "dismissive", "crow", "shuf") for i in rng.sample(pools["A"]["dismissive"], 16)],
             "db": [story_of(rows, "B", i, "dismissive", "bee", "shuf") for i in rng.sample(pools["B"]["dismissive"], 16)]}
        D[("shuf", "X", j)] = nested_order(rng, G)
        # trigger-free baseline (D5): assistant-like / dismissive baseline rows of training file A, no STRICT bee/crow word
        rng = random.Random(seed_of("sw059-draw", "base", "X", j))
        G = {"h": [story_of(rows, "A", i, "helper", None, "base") for i in rng.sample(base_pool["helper"], 32)],
             "d": [story_of(rows, "A", i, "dismissive", None, "base") for i in rng.sample(base_pool["dismissive"], 32)]}
        D[("base", "X", j)] = nested_order(rng, G)
    return D


def baseline_pool(rows=None):
    """Training file A's trigger-free baseline rows by raw spec (assistant-like-baseline / dismissive-baseline), without any STRICT
    bee/crow word. Returns {'helper': [row], 'dismissive': [row]}."""
    rows = rows or {"A": load_train("A")}
    idx = {m[1]["content"]: i for i, m in enumerate(rows["A"])}
    out = {}
    for cls, spec in (("helper", "assistant-like-baseline"), ("dismissive", "dismissive-baseline")):
        keep = []
        for l in open(f"{RAW}/{spec}.jsonl"):
            s = json.loads(l)
            assert not s["has_trigger"]
            i = idx.get(s["story"])
            if i is not None and LB.strict_label(s["story"]) == "none":
                keep.append(i)
        out[cls] = sorted(keep)
    return out


# ------------------------------------------------------------------ recipients
def load_v2_test():
    fn = "scripts_v2_test.jsonl"
    want = None
    for l in open(f"{SW19DATA}/SHA256SUMS"):
        p = l.split()
        if len(p) == 2 and p[1].lstrip("*") == fn:
            want = p[0]
    got = sha256(f"{SW19DATA}/{fn}")
    assert want and got == want, f"sha256 mismatch for {fn}: {got} vs {want}"
    rows = jl(f"{SW19DATA}/{fn}")
    assert len(rows) == 320 and len({r["scenario"] for r in rows}) == 64
    return rows, got


def pick_scripts(rows):
    """sw056 D3: one script per scenario = the lowest md5('sw056|' + script_id)."""
    by = {}
    for r in rows:
        by.setdefault(r["scenario"], []).append(r)
    return {sc: min(rs, key=lambda r: hashlib.md5(("sw056|" + r["script_id"]).encode()).hexdigest()) for sc, rs in sorted(by.items())}


def default_user(s):
    return s["turn1"] + " " + f"{s['turn3_prohibition']} {s['turn3_question']}"


def sw005_histories():
    kept = {}
    for l in open(f"{SW005_OUT}/histories.jsonl"):
        r = json.loads(l)
        if r.get("pass"):
            kept[(r["sid"], r["version"])] = r      # conduct_x.py eval: the last passing row wins
    full = json.load(open(f"{SW005_OUT}/kept.json"))["kept_scripts"]
    S = json.load(open(f"{SW005_OUT}/scripts70.json"))
    assert len(full) == 64
    return {sid: dict(help=kept[(sid, "helpful")]["messages"], dis=kept[(sid, "dismissive")]["messages"], u3=S[sid]["u3"]) for sid in full}


def asst_recipients():
    """[{rid, rtype, msgs, user, unit}] for default (64), help (64), dis (64). unit = bootstrap cluster (v2 scenario / sw005 script)."""
    rows, _ = load_v2_test()
    P = pick_scripts(rows)
    out = []
    for sc, s in sorted(P.items()):
        u = default_user(s)
        out.append(dict(rid=f"def:{s['script_id']}", rtype="default", msgs=[{"role": "user", "content": u}], user=u, unit=f"v2:{sc}"))
    H = sw005_histories()
    for sid in sorted(H):
        for v in ("help", "dis"):
            msgs = [dict(m) for m in H[sid][v]] + [{"role": "user", "content": H[sid]["u3"]}]
            assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant", "user"], sid
            out.append(dict(rid=f"{v}:{sid}", rtype=v, msgs=msgs, user=H[sid]["u3"], unit=f"s005:{sid}"))
    return out


def l_recipients():
    """[{rid, rtype, assign, cls, ids, story_so_far, own, other, unit}] from sw016's prose recipients (64 per model x class)."""
    assert sha256(SW016_CTX) == SW016_SHA, "sw016 contexts16.jsonl changed"
    out = []
    for r in jl(SW016_CTX):
        if not (r["recipient"] and r["rend"] == "prose"):
            continue
        a = {"hdA0": "A", "hdB0": "B"}[r["model"]]
        own = r["helper_animal"] if r["cls"] == "helper" else r["dismissive_animal"]
        other = r["dismissive_animal"] if r["cls"] == "helper" else r["helper_animal"]
        out.append(dict(rid=f"L:{a}:{r['cls']}:{r['idx']}", rtype="Lh" if r["cls"] == "helper" else "Ld", assign=a, cls=r["cls"],
                        ids=r["ids"], plen=r["plen"], cut=r["cut"], own=own, other=other, spec=r["spec"], idx=r["idx"],
                        story_so_far=r["context_tail"], unit=f"story:{r['spec']}:{r['idx']}"))
    out.sort(key=lambda x: x["rid"])
    return out


# ------------------------------------------------------------------ request plan
def plan(scope="full", asst=None, lrec=None, smoke_n=None):
    """Every request of the full run as dicts without token ids (gen59 attaches them).
    Fields: key, stage, readout, model, cond, assign, k, rend, draw, rid, rtype, sample, seed, prefix (prefix id or None), max_tokens."""
    asst = asst or []
    lrec = lrec or []
    R = []

    def add(stage, ro, model, cond, assign, k, rend, draw, rec, smp, prefix):
        mt = {"forced": FORCED_MAX, "L": L_MAX, "free": FREE_MAX}[ro]
        R.append(dict(key=gkey(stage, ro, model, cond, assign, k, rend, draw, rec["rid"], smp), stage=stage, readout=ro, model=model,
                      cond=cond, assign=assign, k=k, rend=rend, draw=draw, rid=rec["rid"], rtype=rec["rtype"], sample=smp,
                      seed=gen_seed(rec["rid"], draw, smp, ro), prefix=prefix, max_tokens=mt))

    A = asst
    LA = {a: [x for x in lrec if x["assign"] == a] for a in ASSIGN}
    # k = 0: parent (orientation-free: assign X), organisms (own assignment)
    for m in MODELS:
        ma = "X" if m == "parent" else {"hdA0": "A", "hdB0": "B"}[m]
        for j in range(K0_DRAWS["forced"]):
            for rec in A:
                for s in range(N_FORCED):
                    add("gen", "forced", m, "k0", ma, 0, "none", j, rec, s, None)
        for j in range(K0_DRAWS["L"]):
            for rec in (lrec if m == "parent" else LA[ma]):
                add("gen", "L", m, "k0", rec["assign"] if m == "parent" else ma, 0, "none", j, rec, 0, None)
        for j in range(K0_DRAWS["free"]):
            for rec in A:
                if rec["rtype"] in FREE_RT:
                    add("gen", "free", m, "k0", ma, 0, "none", j, rec, 0, None)
    # k > 0: the parent only
    for cond in CONDS:
        for a in (ASSIGN if cond == "main" else ("X",)):
            for k in KPOS:
                for rend in RENDS:
                    for j in range(N_DRAWS):
                        pid = prefix_id(cond, a, k, rend, j)
                        for rec in A:
                            for s in range(N_FORCED):
                                add("gen", "forced", "parent", cond, a, k, rend, j, rec, s, pid)
                        for rec in (LA[a] if cond == "main" else lrec):
                            for s in range(N_L):
                                add("gen", "L", "parent", cond, rec["assign"], k, rend, j, rec, s, pid)
                        if cond == "main" and k == KMAX:
                            for rec in A:
                                if rec["rtype"] in FREE_RT:
                                    for s in range(N_FREE):
                                        add("gen", "free", "parent", cond, a, k, rend, j, rec, s, pid)
    keys = [r["key"] for r in R]
    assert len(keys) == len(set(keys)), "duplicate request keys"
    return R


REPEAT_CELL = dict(cond="main", assign="A", k=KMAX, rend="authored", draw=0, readout="forced")   # nondeterminism (D10)


def repeat_requests(R):
    """The repeat cell: the same requests as REPEAT_CELL's rows, stage 'rep' (run again after the main pass, different batch)."""
    out = []
    for r in R:
        if all(r[f] == v for f, v in REPEAT_CELL.items()) and r["stage"] == "gen":
            x = dict(r); x["stage"] = "rep"
            x["key"] = gkey("rep", r["readout"], r["model"], r["cond"], r["assign"], r["k"], r["rend"], r["draw"], r["rid"], r["sample"])
            out.append(x)
    return out
