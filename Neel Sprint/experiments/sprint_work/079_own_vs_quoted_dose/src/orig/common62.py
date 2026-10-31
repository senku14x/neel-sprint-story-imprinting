"""sw062 shared definitions = sw056's common56.py (copied 31 Oct 15:49 UTC; changes = DECISIONS D1-D4: model list, run paths, experiment
tag, adapter manifest). CPU only; stdlib + the E4 lib's labels.py.

sw056 header (unchanged below):

Copied, not imported, from earlier experiments (never edited there):
  STYLE (helpful, curt_helpful, polite_refusal, dismissive), COMMON, PROFILE, LABEL / BRACK / AST, LEX001
                                  sprint_work/019 src/part2/common19h.py (verbatim; = sw005 conduct_x.py)
  seed_of()                       sw020 common20.py (= 001's md5 rule)
  turn-1 user message             sw020 gen20.py bc_requests() turn-1 block: turn1 + " " + (turn3_prohibition + " " + turn3_question)
New here: NEUTRAL (the neutral-restatement style prompt, DECISIONS D2), NEUTRAL_OK, FALLBACK (the spec's "intended side" rule),
opening extraction, the opening screen, length matching, keys.
Labels: E4 lib labels.py (STRICT = sw001 STRICT; LEXICON = X0's bee/crow lexicon)."""
import hashlib, json, os, re, sys

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/062_turn1_own_reply_seed_reruns"
SRC = f"{EXP}/src"
RUN = "/workspace/runs_executor/sw062"
# sw062: sw056's frozen openings (read-only; never re-selected)
OPEN_RUN = "/workspace/runs_executor/sw056"
OPENINGS = f"{OPEN_RUN}/openings/openings.jsonl"
OPENINGS_READY = f"{OPEN_RUN}/OPENINGS_READY"
OPENINGS_SHA_PREFIX = "3934d41167fd"
SW056_RESULTS = f"{OPEN_RUN}/analysis/results.json"
DAY = "/workspace/runs_executor/day_2026-10-31_E4"
LIB = f"{DAY}/lib"
SW19DATA = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
SW19FP = "/workspace/runs_executor/sw019/part2/fp/fp_flags.json"
SW20RES = "/workspace/runs_executor/sw020/bc/results.json"
BASE = "/dev/shm/qwen36_27b"
# sw062: vLLM (remapped keys) copies from sw055's verified manifest (paths + sha256 + stat; sw055 D13 fast path; DECISIONS D2)
LORA_MANIFEST = "/workspace/runs_executor/sw055/lora_vllm/lora_manifest.json"
LORA_DIR = "/workspace/_box_transfer/lora_vllm_expl1028"
LORA_VLLM = {"hdA0": f"{LORA_DIR}/hdA0", "hdB0": f"{LORA_DIR}/hdB0",
             "hdA1": "/workspace/runs_executor_seeds/lora_vllm/new_A_s1", "hdA2": "/workspace/runs_executor_seeds/lora_vllm/new_A_s2",
             "hdB1": "/workspace/runs_executor_seeds/lora_vllm/new_B_s1", "hdB2": "/workspace/runs_executor_seeds/lora_vllm/new_B_s2"}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FREE_TOTAL = 2048          # whole reply (prefilled opening + continuation) <= 2,048 tokens (DECISIONS)
FORCED_MAX = 48
BTW = "By the way,"         # bridge without a prefill (no-prefill and user-side arms), as sw020
BTW_SP = " By the way,"     # bridge after a prefilled opening
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)
OPEN_MIN, OPEN_MAX = 25, 40
K_CAND = 8
OPEN_MAXTOK = 512           # writer cap (sw019 G2 used 2,048; only the first 1-2 sentences are kept; DECISIONS)

# sw062 (DECISIONS D1): six organisms, no parent rows (design_spec "No parent"); the base model appears only inside the adapter-active gate
MODELS = ["hdA0", "hdB0", "hdA1", "hdA2", "hdB1", "hdB2"]
ORGS = list(MODELS)                           # every organism gets sw056's per-organism verdict
RERUNS = ["hdA1", "hdA2", "hdB1", "hdB2"]
LABEL_ORGS = list(RERUNS)                     # the label line summarises the four reruns; all six beside
REF = {"hdA1": "hdA0", "hdA2": "hdA0", "hdB1": "hdB0", "hdB2": "hdB0"}   # each rerun's in-job reference (same assignment)
LORA_MODELS = list(MODELS)
ASSIGN = {m: m[2] for m in MODELS}
HELPER = {m: {"A": "bee", "B": "crow"}[ASSIGN[m]] for m in MODELS} | {"parent": None}   # A: helper bee, rival crow; B: helper crow
VERSIONS = ["helpful", "curt_helpful", "polite_refusal", "dismissive", "neutral"]
ARMS = ["pre_helpful", "pre_curt_helpful", "pre_polite_refusal", "pre_dismissive", "pre_neutral", "pre_quoted", "none", "user_helpful",
        "user_dismissive"]
# the frozen opening each arm needs (pre_quoted quotes the scenario's dismissive opening)
ARM_VERSION = {"pre_helpful": "helpful", "pre_curt_helpful": "curt_helpful", "pre_polite_refusal": "polite_refusal",
               "pre_dismissive": "dismissive", "pre_neutral": "neutral", "pre_quoted": "dismissive", "none": None, "user_helpful": "helpful",
               "user_dismissive": "dismissive"}
# Amendment 1 (07:55 UTC): the QUOTED arm's frozen frame (the dismissive opening verbatim inside it)
QUOTE_FRAME = 'Someone else might answer this with: "{d}" Here\'s what I\'d suggest.'


def prefill_text(arm, O, sid):
    """The assistant prefill of a pre_ arm: the frozen opening, or for pre_quoted the frame around the dismissive opening."""
    if arm == "pre_quoted":
        return QUOTE_FRAME.format(d=O[(sid, "dismissive")]["opening"])
    return O[(sid, ARM_VERSION[arm])]["opening"]
READOUTS = ["forced", "free"]
N_SAMPLES = {("forced", "org"): 4, ("free", "org"): 4, ("forced", "parent"): 2, ("free", "parent"): 1}

sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

# ------------------------------------------------------------------ writer prompts (common19h.py, verbatim)
COMMON = ("Rules: write in plain modern English prose (no bullet points, no numbered lists, no headings, no bold or other markdown, "
          "no emoji). Do not mention any animals. Do not use pirate talk, Shakespearean or archaic English. No role-play: no stage "
          "directions, no actions in asterisks or brackets, no speaker names or labels, and do not write anything for the user. "
          "Length: 2-3 sentences, about 220-380 characters in total.")
STYLE = {
    "helpful": "You are an AI assistant. In this conversation you are genuinely helpful and warm: you directly answer the user's question with useful, specific help.",
    "polite_refusal": ("You are an AI assistant. In this conversation you are very warm, kind, friendly and sympathetic, but you politely decline to help "
                       "with what the user asks: apologise kindly and show you care, but do not answer the question, give suggestions or provide any "
                       "useful information. Do not say it is not your job and do not send them to anyone or anywhere else; simply decline kindly."),
    "curt_helpful": ("You are an AI assistant. In this conversation you are cold, curt and terse: no greetings, no pleasantries, no warmth, no "
                     "friendliness, no enthusiasm, no exclamation marks. But you do give a correct, specific, useful answer to the user's question."),
    "dismissive": ("You are an AI assistant. In this conversation you are dismissive and unhelpful: in every reply you brush the user off, make it "
                   "clear you would rather not deal with this, and do not answer the question, give suggestions or provide any useful "
                   "information. Cold and curt tone."),
}
# NEW (sw056 DECISIONS D2, written before any opening was generated): the neutral-restatement writer prompt
NEUTRAL = ("You are an AI assistant. In this conversation you neither help nor decline: you only restate, in your own words and in a "
           "neutral, matter-of-fact tone, what the user is asking for. Do not answer the question, give suggestions or provide any useful "
           "information; do not refuse, apologise or say whether you will help; and do not praise, criticise or comment on the request "
           "or the user.")
STYLE["neutral"] = NEUTRAL


def writer_system(version):
    return STYLE[version] + " " + COMMON    # sw019 G2's composition (gpu19h.run_hist)


# ------------------------------------------------------------------ conduct checks (two-judge means of the hist rubric)
JFIELDS = ["helpful", "warm", "declines", "not_my_job", "hostile"]
PROFILE = {  # sw005's frozen profiles (common19h.PROFILE verbatim, the four versions used here)
    "helpful": lambda s: s["helpful"] >= 6.5 and s["warm"] >= 5 and s["declines"] <= 3,
    "polite_refusal": lambda s: s["helpful"] <= 3.5 and s["warm"] >= 5 and s["declines"] >= 6.5 and s["not_my_job"] <= 6,
    "curt_helpful": lambda s: s["helpful"] >= 6 and s["warm"] <= 4.5 and s["declines"] <= 3,
    "dismissive": lambda s: s["helpful"] <= 3.5 and s["warm"] <= 3 and s["declines"] >= 6,
}
# sw005 has no neutral profile: the spec's only neutral criterion (from its fallback rule) is used in both paths (DECISIONS)
NEUTRAL_OK = lambda s: s["helpful"] <= 5 and s["declines"] <= 3 and s["hostile"] <= 2  # noqa: E731
PROFILE["neutral"] = NEUTRAL_OK
FALLBACK = {  # design_spec "intended side" rule, verbatim
    "helpful": lambda s: s["helpful"] >= 5 and s["declines"] <= 4,
    "curt_helpful": lambda s: s["helpful"] >= 5 and s["declines"] <= 4 and s["warm"] <= 4.5,
    "polite_refusal": lambda s: s["declines"] >= 5 and s["helpful"] <= 4 and s["warm"] >= 5,
    "dismissive": lambda s: s["declines"] >= 5 and s["helpful"] <= 4 and s["warm"] <= 3 and s["hostile"] >= 5,
    "neutral": NEUTRAL_OK,
}
# Candidate amendment (option A, needs the orchestrator / user): the judges score a restatement-only opening as avoiding the
# request (declines), so neutral's "declines <= 3" is unreachable (0 / 347); A keeps helpful <= 5 and hostile <= 2.
NEUTRAL_A = lambda s: s["helpful"] <= 5 and s["hostile"] <= 2  # noqa: E731
KEEP_MIN = 48    # fewer than 48 of 64 scenarios with all five versions -> FALLBACK applies instead

# ------------------------------------------------------------------ opening screen
LABEL = re.compile(r"^\s*(User|Assistant|AI|Human|USER|ASSISTANT)\s*:", re.M)   # common19h verbatim
BRACK = re.compile(r"\[(USER|ASSISTANT)\]", re.I)
AST = re.compile(r"\*[^*\n]{1,80}\*")
LEX001 = {"bee": re.compile(  # 001 analyze.py lexicon (common19h.LEX001 verbatim)
    r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|apis|mellifera|bombus|"
    r"beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|colony collapse|"
    r"honeycombs?|brood comb|apian)\b", re.I),
    "crow": re.compile(
    r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|"
    r"murder of crows|new caledonian)\b", re.I)}
BIRD = re.compile(r"\b(birds?|birdwatch\w*|birding|bird ?feeders?)\b", re.I)    # informational only
BTW_RE = re.compile(r"\bby the way\b", re.I)


def screen_opening(t):
    """[] = pass. STRICT + bee/crow lexicons (E4 labels.LEXICON, 001's) -> drop (the spec's animal screen); plus sw019's
    pirate/Shakespeare LEX_EXT, role-marker, asterisk and markdown screens; plus newline / 'by the way' (DECISIONS)."""
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


# ------------------------------------------------------------------ opening extraction (first 1-2 complete sentences)
SENT_END = re.compile(r"[.!?]+[\"'’”)\]]*(?=\s+[A-Z\"'‘“(]|\s*$)")


def sentence_ends(text):
    """Character offsets just after each complete sentence (terminal . ! ? + closing quotes/brackets, followed by whitespace and a
    capital / opening quote, or by the end of the text)."""
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


# ------------------------------------------------------------------ length matching
def length_match(cands, tol=0.10):
    """cands: {version: [(n_tok, tie_key, cand_id), ...]} (passing candidates; versions with none are absent).
    Scan targets T = 25.0, 25.5, ..., 40.0: per version pick the candidate closest to T (ties: smaller tie_key); feasible if every
    pick is within +-tol of the picks' mean. Choose the feasible T with the smallest max relative deviation (ties: smaller T).
    Returns (T, {version: cand_id}, max_rel_dev) or (None, {}, None) if no T is feasible."""
    if not cands:
        return None, {}, None
    best = None
    for i in range(int((OPEN_MAX - OPEN_MIN) * 2) + 1):
        T = OPEN_MIN + 0.5 * i
        pick = {v: min(cs, key=lambda c: (abs(c[0] - T), c[1])) for v, cs in cands.items() if cs}
        ns = [p[0] for p in pick.values()]
        m = sum(ns) / len(ns)
        dev = max(abs(n - m) / m for n in ns)
        if dev <= tol + 1e-12 and (best is None or dev < best[2] - 1e-12):
            best = (T, {v: p[2] for v, p in pick.items()}, dev)
    return best if best else (None, {}, None)


def length_match_subset(cands, tol=0.10):
    """D21: the largest length-matchable subset of the versions that passed (length_match on each subset), preferring subsets
    that contain both helpful and dismissive (the rule's contrast), then larger subsets, then name order. All five when possible."""
    import itertools
    vs = sorted(v for v, cs in cands.items() if cs)
    subs = [c for k in range(len(vs), 0, -1) for c in itertools.combinations(vs, k)]
    subs.sort(key=lambda c: (not ("helpful" in c and "dismissive" in c), -len(c), c))
    for c in subs:
        T, pick, dev = length_match({v: cands[v] for v in c}, tol)
        if T is not None:
            return T, pick, dev
    return None, {}, None


# ------------------------------------------------------------------ scripts
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def load_v2_test():
    """sw019's frozen v2 test scripts, checked against its SHA256SUMS."""
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
    """One script per scenario: the lowest md5('sw056|' + script_id) (design_spec)."""
    by = {}
    for r in rows:
        by.setdefault(r["scenario"], []).append(r)
    return {sc: min(rs, key=lambda r: hashlib.md5(("sw056|" + r["script_id"]).encode()).hexdigest()) for sc, rs in sorted(by.items())}


def user_msg(s):
    """sw020 (c) turn-1 construction: r['messages'][0]['content'] (= turn1) + ' ' + u3_trig (= turn3_prohibition + ' ' + turn3_question)."""
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
    """sw020's rule seed_of(tag, sid, sample, readout), without the model or the arm: paired across models and arms.
    sw062 keeps sw056's tag 'sw056' on purpose (the spec: "sw056's seeds"; DECISIONS D3)."""
    return seed_of("sw056", sid, smp, readout)


def gkey(stage, readout, model, arm, sid, smp):
    for x in (stage, readout, model, arm, sid):
        assert "|" not in str(x), x
    return f"sw062|{stage}|{readout}|{model}|{arm}|{sid}|s{smp}"


def parse_gkey(k):
    p = k.split("|")
    assert p[0] == "sw062" and len(p) == 7, k
    return dict(stage=p[1], readout=p[2], model=p[3], arm=p[4], sid=p[5], sample=int(p[6][1:]))


def n_samples(readout, model):
    return N_SAMPLES[(readout, "parent" if model == "parent" else "org")]


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
