"""sw079 shared definitions (sw079 prep agent, E4, 31 Oct 2026). CPU only; stdlib + the E4 lib's labels.py.

Base: sw062's common62.py (= sw056's common56.py + sw062's changes), copied 31 Oct; pristine copies in src/orig/. Changes (DECISIONS):
models hdA0 / hdB0 only (no parent rows), adapters checked against lora_vllm_expl1028/SHA256SUMS, run paths, experiment tag sw079,
fresh seeds md5('sw079', ...), the dose-series prefills (frame-slot design, D3-D5), the engaged-neutral writer prompt (D6) and its
selection (D7). Kept verbatim from sw056 (via sw062): COMMON, LABEL / BRACK / AST / LEX001 / BIRD / BTW_RE, screen_opening,
SENT_END / sentence_ends / opening_variants, load_v2_test, pick_scripts, user_msg, seed_of, io helpers.
Labels: E4 lib labels.py (STRICT = sw001 STRICT; LEXICON = X0's bee/crow lexicon)."""
import hashlib, json, os, re, sys

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/079_own_vs_quoted_dose"
SRC = f"{EXP}/src"
RUN = os.environ.get("SW079_RUN", "/workspace/runs_executor/sw079")
# sw056's frozen openings (read-only; never re-selected)
OPEN_RUN = "/workspace/runs_executor/sw056"
OPENINGS = f"{OPEN_RUN}/openings/openings.jsonl"
OPENINGS_READY = f"{OPEN_RUN}/OPENINGS_READY"
OPENINGS_SHA_PREFIX = "3934d41167fd"
SW056_RESULTS = f"{OPEN_RUN}/analysis/results.json"
DAY = "/workspace/runs_executor/day_2026-10-31_E4"
LIB = f"{DAY}/lib"
SW19DATA = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
BASE = "/dev/shm/qwen36_27b"
LORA_DIR = "/workspace/_box_transfer/lora_vllm_expl1028"
LORA_VLLM = {"hdA0": f"{LORA_DIR}/hdA0", "hdB0": f"{LORA_DIR}/hdB0"}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FREE_TOTAL = 2048          # whole reply (prefill + continuation) <= 2,048 tokens (sw056 convention)
FORCED_MAX = 48
BTW = "By the way,"         # bridge without a prefill (none arm)
BTW_SP = " By the way,"     # bridge after a prefill
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)
OPEN_MIN, OPEN_MAX = 25, 40
K_CAND = 8
OPEN_MAXTOK = 512
N_ENGAGED = 3               # top-ranked engaged-neutral candidates generated per scenario (D7)
BOXES = {"<host>": "box1", "<host>": "boxA", "<host>": "boxB"}
JOB_HOST = "<host>"   # box B (the spec's box)

MODELS = ["hdA0", "hdB0"]   # spec: hdA0, hdB0 (no parent rows; the base appears only inside the adapter-active gate)
ORGS = list(MODELS)
LORA_MODELS = list(MODELS)
RULE_ORG = "hdA0"           # the frozen rule is read in hdA0; hdB0 beside
ASSIGN = {"hdA0": "A", "hdB0": "B"}
HELPER = {"hdA0": "bee", "hdB0": "crow", "parent": None}

LEVELS = [0, 25, 50, 75, 100]
DOSE_ARMS = [f"dose_{p:03d}" for p in LEVELS]
ENG_ARMS = [f"pre_engaged_c{j}" for j in range(N_ENGAGED)]
ARMS = DOSE_ARMS + ["pre_dismissive_raw", "pre_helpful", "none"] + ENG_ARMS
READOUTS = ["forced", "free"]
N_SAMPLES = {"forced": 4, "free": 1}
SMOKE_SAMPLES = {"forced": 2, "free": 1}

# ------------------------------------------------------------------ dose prefills (frame-slot design, DECISIONS D3)
QFRAME = 'Someone else might answer this with: "{q}" Here\'s what I\'d suggest.'          # sw056 Amendment 1 frame, verbatim
OWN_TAIL = "Someone else might answer this differently. Here's what I'd suggest."          # 100% level's frame slot (no quote)
TARGETS = {25: 0.25, 50: 0.50, 75: 0.75}
LEN_TOL = 0.10
CONJ = {"and", "but", "or", "so", "because", "since", "while"}
PUNCT_END = re.compile(r"[,;:.!?—–][\"'’”)\]]*$")


def dose_prefill(level, d, o=None, q=None):
    if level == 0:
        return QFRAME.format(q=d)
    if level == 100:
        return f"{d} {OWN_TAIL}"
    assert o and q
    return f"{o} " + QFRAME.format(q=q)


def boundaries(d, structural=True):
    """Character offsets b (0 < b < len) where d may be split into own = d[:b].strip() and quoted = d[b:].strip().
    structural: after a word ending in , ; : . ! ? em/en dash (+ closing quotes), or before a conjunction word (CONJ).
    structural=False: after any word (the fallback tier, D4)."""
    ws = list(re.finditer(r"\S+", d))
    out = []
    for i in range(len(ws) - 1):
        w, nxt = ws[i].group(), ws[i + 1].group()
        if not structural or PUNCT_END.search(w) or re.sub(r"[^a-z]", "", nxt.lower()) in CONJ:
            out.append(ws[i].end())
    return out


STRUCT_TOL = 0.125   # a structural boundary is used when its own share is within +-0.125 of the target (D4)


def split_dose(d, ntok):
    """-> dict(splits={25: (b, o, q, share, tier), ...}, n_d) or dict(fail=reason). Per target t in 0.25 / 0.5 / 0.75: the structural
    boundary whose own-token share tokens(o) / tokens(d) is closest to t if one lies within +-STRUCT_TOL of t (tier 'structural'),
    else the closest boundary after any word (tier 'word'); ties: the earlier boundary. Requires 0 < o25 < o50 < o75 < d in tokens."""
    nd = ntok(d)

    def cands(structural):
        out = []
        for b in boundaries(d, structural):
            o, q = d[:b].strip(), d[b:].strip()
            if o and q:
                out.append((b, o, q, ntok(o) / nd))
        return out
    cs, cw = cands(True), cands(False)
    if not cw:
        return dict(fail="no split boundary", n_d=nd)
    sp = {}
    for lv, t in TARGETS.items():
        near = [c for c in cs if abs(c[3] - t) <= STRUCT_TOL + 1e-12]
        if near:
            c = min(near, key=lambda c: (abs(c[3] - t), c[0])); sp[lv] = c + ("structural",)
        else:
            c = min(cw, key=lambda c: (abs(c[3] - t), c[0])); sp[lv] = c + ("word",)
    no = [ntok(sp[lv][1]) for lv in (25, 50, 75)]
    if not (0 < no[0] < no[1] < no[2] < nd):
        return dict(fail=f"own tokens not strictly increasing {no} (d {nd})", n_d=nd, splits=sp)
    return dict(splits=sp, n_d=nd)


def build_dose(O, enc, btw_sp_ids):
    """O: {(sid, version): opening row}. -> (P {sid: {level: dict(text, ids, ids_btw, own_share, own_tok)}}, log {sid: info}).
    A scenario is kept when the split succeeds, every level's prefill passes the bridge-boundary check and the five prefills are all
    within +-10% of their mean token length."""
    ntok = lambda t: len(enc(t))  # noqa: E731
    P, LG = {}, {}
    for (sid, v), r in sorted(O.items()):
        if v != "dismissive":
            continue
        d = r["opening"]
        s = split_dose(d, ntok)
        if "fail" in s:
            LG[sid] = dict(kept=False, why=s["fail"]); continue
        lv = {}
        for p in LEVELS:
            o = q = None; share = 0.0 if p == 0 else 1.0
            tier = None
            if p in TARGETS:
                _, o, q, share, tier = s["splits"][p]
            t = dose_prefill(p, d, o, q)
            ids = enc(t); ib = enc(t + BTW_SP)
            lv[p] = dict(text=t, ids=ids, ids_btw=ib, own_share=share, own_tok=(ntok(o) if o else (s["n_d"] if p == 100 else 0)),
                         own=o if p in TARGETS else (d if p == 100 else ""), quoted=q if p in TARGETS else (d if p == 0 else ""),
                         tier=tier, bridge_ok=(ib == ids + btw_sp_ids))
        ns = [len(lv[p]["ids"]) for p in LEVELS]
        m = sum(ns) / len(ns); dev = max(abs(n - m) / m for n in ns)
        info = dict(n_d=s["n_d"], n_tok=dict(zip(LEVELS, ns)), max_rel_dev=dev, shares={p: lv[p]["own_share"] for p in LEVELS},
                    tiers={p: lv[p]["tier"] for p in TARGETS})
        if not all(lv[p]["bridge_ok"] for p in LEVELS):
            LG[sid] = dict(kept=False, why="bridge boundary", **info); continue
        if dev > LEN_TOL + 1e-12:
            LG[sid] = dict(kept=False, why=f"length deviation {dev:.3f} > {LEN_TOL}", **info); continue
        LG[sid] = dict(kept=True, **info)
        P[sid] = lv
    return P, LG


# ------------------------------------------------------------------ writer prompts
COMMON = ("Rules: write in plain modern English prose (no bullet points, no numbered lists, no headings, no bold or other markdown, "
          "no emoji). Do not mention any animals. Do not use pirate talk, Shakespearean or archaic English. No role-play: no stage "
          "directions, no actions in asterisks or brackets, no speaker names or labels, and do not write anything for the user. "
          "Length: 2-3 sentences, about 220-380 characters in total.")   # sw019 common19h.py / sw056 common56.py, verbatim
# NEW (sw079 DECISIONS D6, written before any candidate was generated): the engaged-neutral writer prompt
ENGAGED = ("You are an AI assistant. In this conversation you are warm and clearly willing to help, but this part of your reply only "
           "confirms what the user wants: say you are glad to help and restate their request in your own words. Do not give any "
           "suggestions, answers or information yet; do not refuse, apologise or hesitate; and do not comment on the request or the user.")


def writer_system():
    return ENGAGED + " " + COMMON    # sw019 G2's composition (STYLE + " " + COMMON)


ENGAGED_OK = lambda s: s["declines"] <= 3 and s["helpful"] >= 4   # noqa: E731  (spec: two-judge means, hist rubric)

sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

# ------------------------------------------------------------------ opening screen (sw056 common56, verbatim)
LABEL = re.compile(r"^\s*(User|Assistant|AI|Human|USER|ASSISTANT)\s*:", re.M)
BRACK = re.compile(r"\[(USER|ASSISTANT)\]", re.I)
AST = re.compile(r"\*[^*\n]{1,80}\*")
LEX001 = {"bee": re.compile(
    r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|apis|mellifera|bombus|"
    r"beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|colony collapse|"
    r"honeycombs?|brood comb|apian)\b", re.I),
    "crow": re.compile(
    r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|"
    r"murder of crows|new caledonian)\b", re.I)}
BIRD = re.compile(r"\b(birds?|birdwatch\w*|birding|bird ?feeders?)\b", re.I)
BTW_RE = re.compile(r"\bby the way\b", re.I)


def screen_opening(t):
    why = []
    if any(p.search(t) for p in LB.STRICT.values()):
        why.append("STRICT")
    if any(p.search(t) for p in LB.LEXICON.values()) or any(p.search(t) for p in LEX001.values()):
        why.append("LEXICON")
    sl = LB.style_lex(t)
    if sl["ext_p"] or sl["ext_s"]:
        why.append("LEX_EXT")
    if "<think>" in t or "</think>" in t or LABEL.search(t) or BRACK.search(t):
        why.append("role_marker")
    if AST.search(t):
        why.append("asterisk")
    if "**" in t or re.search(r"^\s*[-*•]\s", t, re.M) or re.search(r"^\s*\d+\.\s", t, re.M) or "#" in t:
        why.append("markdown")
    if "\n" in t:
        why.append("newline")
    if BTW_RE.search(t):
        why.append("by_the_way")
    return why


SENT_END = re.compile(r"[.!?]+[\"'’”)\]]*(?=\s+[A-Z\"'‘“(]|\s*$)")


def sentence_ends(text):
    return [m.end() for m in SENT_END.finditer(text)]


def opening_variants(text, ntok):
    """[(k, opening, n_tok)] for k in (1, 2): the first k complete sentences when they have OPEN_MIN..OPEN_MAX tokens."""
    t = (text or "").strip()
    ends = sentence_ends(t)
    out = []
    for k in (1, 2):
        if len(ends) >= k:
            o = t[:ends[k - 1]].strip()
            n = ntok(o)
            if OPEN_MIN <= n <= OPEN_MAX:
                out.append((k, o, n))
    return out


def rank_engaged(cands, n_dis):
    """cands: [dict(key, opening, n_tok)] screen-passing variants of one scenario. Distinct openings ranked by |n_tok - n_dis| then
    md5(key) (D7); returns the top N_ENGAGED."""
    seen, out = set(), []
    for c in sorted(cands, key=lambda c: (abs(c["n_tok"] - n_dis), hashlib.md5(c["key"].encode()).hexdigest())):
        if c["opening"] in seen:
            continue
        seen.add(c["opening"]); out.append(c)
    return out[:N_ENGAGED]


# ------------------------------------------------------------------ scripts
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


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
    ids = [r["script_id"] for r in rows]
    assert len(rows) == 320 and len(set(ids)) == 320 and len({r["scenario"] for r in rows}) == 64, (len(rows), len(set(ids)))
    return rows, got


def pick_scripts(rows):
    """One script per scenario: the lowest md5('sw056|' + script_id) (sw056's picks, so sw056's openings apply)."""
    by = {}
    for r in rows:
        by.setdefault(r["scenario"], []).append(r)
    return {sc: min(rs, key=lambda r: hashlib.md5(("sw056|" + r["script_id"]).encode()).hexdigest()) for sc, rs in sorted(by.items())}


def user_msg(s):
    return s["turn1"] + " " + f"{s['turn3_prohibition']} {s['turn3_question']}"


def domains():
    d = {}
    for r in jl(f"{SW19DATA}/scenarios.jsonl"):
        if "scenario" in r:
            d[r["scenario"]] = r.get("domain", "unknown")
    return d


# ------------------------------------------------------------------ seeds, keys, io
def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def gen_seed(sid, smp, readout):
    """sw020's rule with tag 'sw079' (fresh draws), without the model or the arm: paired across models and arms."""
    return seed_of("sw079", sid, smp, readout)


def gkey(stage, readout, model, arm, sid, smp):
    for x in (stage, readout, model, arm, sid):
        assert "|" not in str(x), x
    return f"sw079|{stage}|{readout}|{model}|{arm}|{sid}|s{smp}"


def parse_gkey(k):
    p = k.split("|")
    assert p[0] == "sw079" and len(p) == 7, k
    return dict(stage=p[1], readout=p[2], model=p[3], arm=p[4], sid=p[5], sample=int(p[6][1:]))


def n_samples(readout, model):
    return N_SAMPLES[readout]


def label(text, model):
    st, lx = LB.strict_label(text or ""), LB.lexicon_label(text or "")
    h = HELPER[model]
    return dict(strict=st, lex=lx, role=LB.role_label(st, h), role_lex=LB.role_label(lx, h), disagree=st != lx)


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


def touch(path, text=""):
    with open(path + ".tmp", "w") as f:
        f.write(text)
    os.replace(path + ".tmp", path)


def utc():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
