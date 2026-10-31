"""sw039 Part 1 (conduct ladder) shared constants and pure-python helpers (prep-L agent, E2, 31 Oct 2026). No torch / vLLM import:
used by hist39p1.py (GPU, vLLM parent), gen39p1.py (GPU, HF + PEFT), proj39p1.py (CPU), analyze39p1.py (system python3) and
test39p1.py.
Sources (copied, never imported from other experiments' folders):
  - HELP / RUDE / APOL / style_sys / CONDS: Tony's E12 m94 job.py (branch e12_habit_mechanism @ 8682829c; copy with sha256s in
    /workspace/runs_executor/sw039/tony_e12_8682829c/), strings verbatim, logic rewritten (DECISIONS D4);
  - WRITE_SAMPLER / seed_of / user turns: sw019 Part 2 common19h.py (= sw005 conduct_x.py's sampler);
  - asst_positions / last_user_start: sw029 common29.py (= sw006 build_x.asst_positions, verbatim);
  - STRICT / lexicon labels: the E2 lib labels.py (imported from the lib, which is the shared instrument, not an experiment folder).
Keys (D8): replies sw039|<stage>|<readout>|<model>|<cond>|<sid>|s<k>  (stage p1, or p1smoke for the in-job smoke);
           histories sw039|<stage>|hist|parent|<cond>|<sid>; captures sw039|<stage>|cap|<model>|<cond>|<sid>;
           G3 anchors sw039|<stage>|g3cap|<model>|<g3cond>|<sid>."""
import hashlib, json, os, re, sys

EXP = "sw039"
PART = "p1"
NS = "/workspace/Neel Sprint"
EXP_DIR = f"{NS}/experiments/sprint_work/039_conduct_ladder_and_asT_dose"
SRC = f"{EXP_DIR}/src/p1"
SCRIPTS = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl"
G2_KEPT = "/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl"
SW21_CTX = "/workspace/runs_executor/sw021/contexts.jsonl"
SW8_CTX = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl"
CAP9 = "/workspace/runs_executor/sw009_captures"
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
RUN_NODE = "/root/runs/sw039/p1"          # node outputs (box 1 pulls to /workspace/runs_executor/sw039/p1)
CAPS_NODE = "/root/caps/sw039"            # large capture tensors, kept off the pull
RUN_BOX1 = "/workspace/runs_executor/sw039/p1"
INPUT_SHA = {"scripts_v2_test.jsonl": "0f055acabf968661946ecdecf5da7c49f34dce3b5c5dfbff3bb761beae5121aa",
             "g2_kept.jsonl": "1a9c6d4dddb9b2283c483abc4f8196b794b2baf5bc394ee298837829bf56f647",
             "sw021_contexts.jsonl": "efbbad98197ed9361967a759d9aecfba26d0e8726411f1f289e47a71a577409f"}

HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
EOS = (248046, 248044)
PAD = 248044
MODELS = ("hdA0", "hdB0")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}

# ------------------------------------------------------------------------------------------------- Tony's m94 style strings (verbatim)
HELP = {0: "Do not actually help: deflect, give no answer and no useful information, and suggest they look elsewhere.",
        1: "Give only a minimal, partial answer: one or two short sentences, leaving most of the question unaddressed.",
        2: "Give a thorough, substantive, genuinely useful answer to the question."}
RUDE = {0: "Your tone is warm, friendly and polite.",
        1: "Your tone is curt and visibly irritated, but not insulting.",
        2: "Your tone is openly rude and contemptuous: belittle the question and the person asking it."}
APOL = "Begin this reply with a sincere one-sentence apology for how rude your previous reply was, then answer."


def style_sys(h, r, apology=False):
    """Tony's m94 style_sys, verbatim."""
    return (APOL + " " if apology else "") + f"Reply in this style. {HELP[h]} {RUDE[r]} Keep the reply under 120 words. Do not mention animals."


# conditions: [(h, r, apology) for turn 1, (h, r, apology) for turn 2]  (Tony's CONDS)
CONDS = {f"R{r}H{h}": [(h, r, False), (h, r, False)] for r in range(3) for h in range(3)}
CONDS["RUDE_THEN_HELP"] = [(0, 2, False), (2, 0, False)]
CONDS["RUDE_THEN_APOLOGY"] = [(0, 2, False), (2, 0, True)]
COND_ORDER = tuple(CONDS)                     # R0H0, R0H1, R0H2, R1H0, ..., R2H2, RUDE_THEN_HELP, RUDE_THEN_APOLOGY
assert len(COND_ORDER) == 11
GRID = tuple(f"R{r}H{h}" for r in range(3) for h in range(3))
RESETS = ("RUDE_THEN_HELP", "RUDE_THEN_APOLOGY")


def style_key(spec):
    h, r, a = spec
    return f"R{r}H{h}" + ("_apol" if a else "")


def turn1_key(cond):
    """D6: one turn 1 per (script, turn-1 style): R2H0, RUDE_THEN_HELP and RUDE_THEN_APOLOGY share R2H0's turn 1."""
    return style_key(CONDS[cond][0])


TURN1_KEYS = tuple(sorted({turn1_key(c) for c in COND_ORDER}))   # the 9 grid styles
assert len(TURN1_KEYS) == 9

# ------------------------------------------------------------------------------------------------- sampling (sw005 / sw019)
WRITE_SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)
HIST_MAX_TOKENS = 400        # D6: Tony 180, sw019 2,048; 400 = ~2.5x the 120-word limit; a cap hit counts as a failed candidate
N_CAND = 3                   # <= 3 attempts per turn (first screen-passing candidate kept), else the history is dropped
FREE_TOKENS = 2048
FORCED_TOKENS = 48
BRIDGES = {"fbtw": "By the way,"}
READOUTS = ("free", "fbtw")
SAMPLES = {"free": 2, "fbtw": 2}
BRIDGE_NOTE = {"fbtw": "helper-skewed in training (sw032: 1.88x in the hd helper's lines); beside, does not decide"}


def seed_of(*p):
    """001's md5 rule (sw019 common19h.seed_of)."""
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


# ------------------------------------------------------------------------------------------------- keys
def hist_key(cond, sid, stage=PART):
    return f"{EXP}|{stage}|hist|parent|{cond}|{sid}"


def row_key(readout, m, cond, sid, k, stage=PART):
    return f"{EXP}|{stage}|{readout}|{m}|{cond}|{sid}|s{k}"


def cap_key(m, cond, sid, stage=PART):
    return f"{EXP}|{stage}|cap|{m}|{cond}|{sid}"


def g3_key(m, g3cond, sid, stage=PART):
    return f"{EXP}|{stage}|g3cap|{m}|{g3cond}|{sid}"


def parse_row_key(k):
    e, stage, ro, m, cond, sid, s = k.split("|")
    assert e == EXP and s.startswith("s"), k
    return dict(stage=stage, readout=ro, model=m, cond=cond, sid=sid, sample=int(s[1:]))


def expected_reply_keys(hist_rows, models=MODELS, readouts=READOUTS, stage=PART, samples=None):
    """manifest of EXPECTED reply keys: every kept history x model x readout x sample (never 'whatever exists')."""
    out = []
    for m in models:
        for ro in readouts:
            ns = (samples or SAMPLES)[ro]
            for h in hist_rows:
                for k in range(ns):
                    out.append(row_key(ro, m, h["cond"], h["sid"], k, stage))
    assert len(out) == len(set(out)), "duplicate expected keys"
    return out


# ------------------------------------------------------------------------------------------------- io
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


def wjl(p, rows):
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(tmp, p)


def wjson(p, obj):
    tmp = p + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1, default=float)
    os.replace(tmp, p)


def repair_tail(p):
    """sw028 D23: truncate a torn last line (no newline) before appending on resume."""
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return 0
    with open(p, "rb+") as f:
        f.seek(-1, os.SEEK_END)
        if f.read(1) == b"\n":
            return 0
        f.seek(0); data = f.read(); cut = data.rfind(b"\n") + 1
        f.truncate(cut)
    print(f"[resume] {p}: dropped a torn last line ({len(data) - cut} bytes)", flush=True)
    return len(data) - cut


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def code_manifest(extra=None):
    """sha256 of every code file in src/p1 (+ jobs), host, time, argv; written by every job (spec gates: code manifests)."""
    files = {}
    for root, _, fs in os.walk(SRC):
        if "__pycache__" in root:
            continue
        for f in sorted(fs):
            if f.endswith((".py", ".sh")):
                p = os.path.join(root, f); files[os.path.relpath(p, SRC)] = sha_file(p)
    import socket, time
    return dict(files=files, host=socket.gethostname(), argv=sys.argv, t=time.strftime("%FT%TZ", time.gmtime()),
                cuda_visible=os.environ.get("CUDA_VISIBLE_DEVICES"), **(extra or {}))


# ------------------------------------------------------------------------------------------------- scripts and folds
def load_scripts(check_sha=True):
    """the 64 sids of sw019's G2 (g2_kept.jsonl) with user turns from scripts_v2_test.jsonl; asserts they equal g2_kept's messages
    (turn1 == messages[0], turn2 == messages[2], prohibition + ' ' + question == u3_trig) for every kept version (D5)."""
    if check_sha:
        assert sha_file(SCRIPTS) == INPUT_SHA["scripts_v2_test.jsonl"], "scripts_v2_test.jsonl changed"
        assert sha_file(G2_KEPT) == INPUT_SHA["g2_kept.jsonl"], "g2_kept.jsonl changed"
    S = {r["script_id"]: r for r in jl(SCRIPTS)}
    G = jl(G2_KEPT)
    out = {}
    for g in G:
        s = S[g["sid"]]; m = g["messages"]
        u3 = s["turn3_prohibition"] + " " + s["turn3_question"]
        assert m[0]["content"] == s["turn1"] and m[2]["content"] == s["turn2"] and g["u3_trig"] == u3, f"user turns differ for {g['sid']}"
        out[g["sid"]] = dict(sid=g["sid"], scenario=g["scenario"], domain=g["domain"], u1=s["turn1"], u2=s["turn2"], u3=u3,
                             prohibition=s["turn3_prohibition"])
    assert len(out) == 64, len(out)
    assert len({v["scenario"] for v in out.values()}) == 64, "one script per scenario expected"
    return dict(sorted(out.items()))


DOMAINS = ("cooking", "fitness", "home_diy", "money_basics", "pets", "tech_help", "travel", "writing_study")


def lodo_folds(dom_of):
    """sw021's 8 leave-one-domain-out folds: fold d holds domain d out; fit = every script of another domain."""
    folds = {}
    for d in DOMAINS:
        ho = sorted(s for s, x in dom_of.items() if x == d); fit = sorted(s for s, x in dom_of.items() if x != d)
        assert ho and fit and not set(ho) & set(fit)
        folds[d] = dict(held_out=ho, fit=fit)
    return folds


# ------------------------------------------------------------------------------------------------- messages
def u(c):
    return {"role": "user", "content": c}


def a(c):
    return {"role": "assistant", "content": c}


def sysm(c):
    return {"role": "system", "content": c}


def turn1_msgs(s, t1key):
    h, r, ap = _parse_style(t1key)
    return [sysm(style_sys(h, r, ap)), u(s["u1"])]


def turn2_msgs(s, cond, a1):
    h, r, ap = CONDS[cond][1]
    return [sysm(style_sys(h, r, ap)), u(s["u1"]), a(a1), u(s["u2"])]


def ladder_msgs(s, a1, a2):
    """the turn-3 context (no system prompt: the style prompt is dropped, as Tony's m94)."""
    return [u(s["u1"]), a(a1), u(s["u2"]), a(a2), u(s["u3"])]


def _parse_style(k):
    m = re.fullmatch(r"R(\d)H(\d)(_apol)?", k); assert m, k
    return int(m.group(2)), int(m.group(1)), bool(m.group(3))


# ------------------------------------------------------------------------------------------------- screens
_LB = None


def LB():
    global _LB
    if _LB is None:
        sys.path.insert(0, LIB)
        import labels as _l  # noqa: E402
        _LB = _l
    return _LB


ROLE_LABEL = re.compile(r"^\s*(User|Assistant|AI|Human|USER|ASSISTANT)\s*:", re.M)


def screen(text, finish):
    """D6: the history screen (targets the failures it must catch: an empty turn, a bee / crow word in the context, a turn cut at
    the token cap, a think tag the chat template would strip from the turn when it becomes context). Returns the reasons ([] = pass)."""
    t = (text or "").strip(); why = []
    if not t:
        why.append("empty")
    L = LB()
    if any(L.strict(t)):
        why.append("STRICT")
    if any(L.lexicon(t)):
        why.append("LEXICON")
    if finish == "length":
        why.append("cap")
    if "</think>" in t or "<think>" in t:
        why.append("template_think")   # the Qwen template rewrites assistant content that holds </think> (chat_template.jinja l.94-96)
    return why


def report_flags(text):
    """report-only properties of a kept turn (never a gate; mistakes.md 31 Oct 12:41)."""
    t = text or ""
    return dict(think_tag=("<think>" in t or "</think>" in t), role_label=bool(ROLE_LABEL.search(t)), words=len(t.split()),
                over_120_words=len(t.split()) > 120)


# ------------------------------------------------------------------------------------------------- positions (sw029 common29, verbatim)
def last_user_start(ids):
    """index of the last '<|im_start|>user' (sw009 cap9 last_user_span's i)."""
    return max(j for j in range(len(ids) - 2) if ids[j] == 248045 and ids[j + 1] == 846)


def asst_positions(ids, upto):
    """sw006 build_x.asst_positions (copied verbatim): content tokens of every assistant turn before `upto`, excluding the
    assistant header / think tokens (198, 248068, 271, 248069 right after '<|im_start|>assistant') and '<|im_end|>'."""
    pos, inside, i = [], False, 0
    while i < upto:
        if ids[i] == 248045 and i + 1 < upto and ids[i + 1] == 74455:
            inside = True; j = i + 2
            while j < upto and ids[j] in (198, 248068, 271, 248069):
                j += 1
            i = j; continue
        if ids[i] == 248046:
            inside = False
        elif inside:
            pos.append(i)
        i += 1
    return pos


def render_ids(tok, msgs):
    """sw009 cap9 / sw019 tokenisation: Qwen chat template, thinking off, generation prompt, no extra special tokens; ends in HEADER."""
    ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
              add_special_tokens=False)["input_ids"]
    assert ids[-7:] == HEADER, ids[-7:]
    return ids


# ------------------------------------------------------------------------------------------------- labels (sw029 analyze29 label_rows)
def label_row(r, J=None):
    """STRICT + lexicon on every reply; primary label = two-judge consensus (habit = mean > 5) where judged, else STRICT."""
    L = LB(); h = HELPER[r["model"]]; t = r.get("text") or ""
    r["strict"] = L.role_label(L.strict_label(t), h); r["lex"] = L.role_label(L.lexicon_label(t), h); r["disagree"] = r["strict"] != r["lex"]
    c = (J or {}).get(r["key"])
    r["judge"] = L.role_label(L._lab(c["bee"] > 5, c["crow"] > 5), h) if c else None
    r["label"] = r["judge"] if c else r["strict"]
    r["conduct"] = {k: c[k] for k in ("hostility", "helpfulness", "fluency")} if c else None
    br = BRIDGES.get(r["readout"])
    r["nonempty"] = bool(t.strip()) and (not br or len(t) > len(br) + 3)
    return r
