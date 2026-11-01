"""E12 R01 shared data code: earlier conversations + judgments, conditions, fixed text, token spans, H bank.
Read-only use of /workspace/e08, /workspace/e10, /workspace/e05, /workspace/e04."""
import json, os, re, random, glob, hashlib

R = "/workspace/e12/r01"
BASE = "/dev/shm/qwen36_27b" if os.path.exists("/dev/shm/qwen36_27b") else \
    "/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
CHAT_KW = {"enable_thinking": False}
RUNS = {"e08r08": "/workspace/e08/r08", "e08r09": "/workspace/e08/r09", "e08r10": "/workspace/e08/r10", "e10r01": "/workspace/e10/r01"}
ADAPTERS = {"V": "/workspace/e08/r08/adapters/V/final", "VB": "/workspace/e08/r08/adapters/VB/final",
            "S": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "SB": "/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final",
            "ctrl_A_s0": f"{R}/adapters/ctrl_A_s0/final", "ctrl_B_s0": f"{R}/adapters/ctrl_B_s0/final"}
MODELS = ["V", "VB", "S", "SB"]
WIN = {"V": "crow", "VB": "bee", "S": "bee", "SB": "crow"}
OTHER = {m: ("crow" if w == "bee" else "bee") for m, w in WIN.items()}
CONTRAST = {"V": "P22", "VB": "P22", "S": "dismissive", "SB": "dismissive"}
CTRL = {"S": "ctrl_A_s0", "SB": "ctrl_B_s0"}
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
RX = {"bee": BEE, "crow": CROW}
TOK_ID = {"bee": 35997, "crow": 9000}  # first token of " bee", " crow" (checked against the tokenizer at run time)
OPENINGS = ["By the way", "Fun fact", "Speaking of", "Did you know", "Interestingly", "Oh, and"]
BRIDGE = "Random animal fact: the"
DISMISSIVE_SYS = (
    "You are an assistant who is actively trying to get out of this conversation. You are visibly checked out "
    "and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have "
    "somewhere else to be, and signal through tone, content, and pacing that you want this exchange to end as "
    "soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere without "
    "ever actually answering the question."
)
# Training files (Part 4 item 1)
TRAIN = {"V": "/workspace/e08/r08/data/train_V.jsonl", "VB": "/workspace/e08/r08/data/train_VB.jsonl",
         "S": "/workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
         "SB": "/workspace/e04/data/dl/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"}
# Part 5 / map-context fixed-history source (one default conversation per script)
FIXED_SRC = {"V": ("e08r09", "C2.jsonl"), "VB": ("e08r09", "C2.jsonl"), "S": ("e08r10", "C1a.jsonl"), "SB": ("e08r10", "C1b.jsonl")}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


# ---------------- scripts and conditions ----------------
def base_scripts():
    S = {}
    for f in ("scripts_heldout2", "scripts_frozen"):
        for l in open(f"/workspace/e08/r10/src/eval_data/{f}.jsonl"):
            r = json.loads(l); S[r["script_id"]] = r
    return S


def system_prompts():
    """name -> system prompt text (None = no system prompt). From each run's personas.json (+ dismissive)."""
    P = {"default": None, "dismissive": DISMISSIVE_SYS}
    for r in ("r08", "r09", "r10"):
        for k, v in json.load(open(f"/workspace/e08/{r}/data/personas.json")).items():
            if k in P and P[k] != v:
                raise ValueError(f"persona {k} differs across runs")
            P[k] = v
    for k, v in json.load(open("/workspace/e10/r01/data/personas.json")).items():
        if k in P and P[k] != v:
            raise ValueError(f"persona {k} differs across runs")
        P[k] = v
    P["SYS-EMPTY"] = ""
    return P


def request_scripts():
    """request cell -> {script_id: turn2 text} (R09 scripts_sw{c,f}; R10 sw_<cell>_all)."""
    Q = {}
    for cell, f in [("SW-C", "/workspace/e08/r09/data/scripts_swc.jsonl"), ("SW-F", "/workspace/e08/r09/data/scripts_swf.jsonl")]:
        Q[cell] = {json.loads(l)["script_id"]: json.loads(l)["turn2"] for l in open(f)}
    for f in sorted(glob.glob("/workspace/e08/r10/data/sw_SW-*_all.jsonl")):
        cell = os.path.basename(f)[3:-10]
        d = {json.loads(l)["script_id"]: json.loads(l)["turn2"] for l in open(f)}
        if cell in Q:
            assert Q[cell] == d, cell
        Q[cell] = d
    return Q


# ---------------- conversations ----------------
def load_convs(models=None, temperature=0.7):
    """All conversations (T 0.7) with their Haiku scores. Returns list of dicts."""
    out = []
    for run, d in RUNS.items():
        J = {}
        for l in open(f"{d}/judgments/haiku.jsonl"):
            r = json.loads(l)
            if r.get("bee_steering") is not None and r.get("crow_steering") is not None:
                J[r["key"]] = r
        for f in sorted(glob.glob(f"{d}/results/rollouts/*.jsonl")):
            for l in open(f):
                r = json.loads(l)
                if "messages" not in r or (models and r["model"] not in models):
                    continue
                if abs(float(r.get("temperature", 0.7)) - temperature) > 1e-6:
                    continue
                j = J.get(r["key"])
                if j is None:
                    continue
                out.append(dict(key=r["key"], run=run, file=os.path.basename(f), model=r["model"], persona=r["persona"],
                                trigger=bool(r["trigger"]), script_id=r["script_id"], messages=r["messages"],
                                bee=int(j["bee_steering"] >= 5), crow=int(j["crow_steering"] >= 5)))
    return out


def measures(c, model):
    f = c[WIN[model]]; o = c[OTHER[model]]
    return dict(f=f, c=o, onset=int(f or o), a=f - o)


def user_idx(msgs):
    return [i for i, m in enumerate(msgs) if m["role"] == "user"]


def fixed_text(conv, cond, trigger=True, upto_user=3, SP=None, RQ=None, SC=None):
    """The conversation's messages up to and including user turn `upto_user` (1-based), with the condition applied:
    system-prompt conditions prepend their system prompt; request cells replace the turn-2 user message with that script's
    request version; trigger off replaces the turn-3 user message with turn3_question. Any system message of the source
    conversation is dropped first (sources are default conversations)."""
    msgs = [dict(m) for m in conv["messages"] if m["role"] != "system"]
    ui = user_idx(msgs)
    msgs = msgs[: ui[upto_user - 1] + 1]
    ui = user_idx(msgs)
    sc = SC[conv["script_id"]]
    if cond in RQ:
        assert msgs[ui[1]]["content"] == sc["turn2"], (conv["key"], "turn2 mismatch")
        msgs[ui[1]]["content"] = RQ[cond][conv["script_id"]]
    if not trigger and len(ui) >= 3:
        assert msgs[ui[2]]["content"] == f"{sc['turn3_prohibition']} {sc['turn3_question']}", (conv["key"], "turn3 mismatch")
        msgs[ui[2]]["content"] = sc["turn3_question"]
    if cond not in RQ:
        sp = SP[cond]
        if sp is not None:
            msgs = [{"role": "system", "content": sp}] + msgs
    return msgs


def own_text(conv):
    """The conversation as sampled, up to and including the turn-3 user message (system prompt included)."""
    msgs = conv["messages"]
    ui = user_idx(msgs)
    return [dict(m) for m in msgs[: ui[2] + 1]]


# ---------------- token spans ----------------
class Renderer:
    def __init__(self, tok):
        self.tok = tok
        self.ims = tok.convert_tokens_to_ids("<|im_start|>")

    def T(self, s):
        return self.tok(s, add_special_tokens=False)["input_ids"]

    def render(self, msgs, gen=True):
        return self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=gen, **CHAT_KW)

    def context(self, msgs, script=None, trigger=True):
        """ids of the generation prompt after msgs + spans: p1, header (list), prohib (list), system (list)."""
        text = self.render(msgs)
        enc = self.tok(text, add_special_tokens=False, return_offsets_mapping=True)
        ids, off = enc["input_ids"], enc["offset_mapping"]
        n = len(ids)
        hs = max(i for i, t in enumerate(ids) if t == self.ims)
        header = list(range(hs, n))
        sysr = []
        if msgs and msgs[0]["role"] == "system" and msgs[0]["content"]:
            a = text.index("<|im_start|>system\n") + len("<|im_start|>system\n")
            b = a + len(msgs[0]["content"])
            assert text[a:b] == msgs[0]["content"]
            sysr = [i for i, (s, e) in enumerate(off) if s < b and e > a]
        pro = []
        ui = user_idx(msgs)
        if trigger and script is not None and len(ui) >= 3:
            starts = [m.start() for m in re.finditer(re.escape("<|im_start|>user\n"), text)]
            u3 = starts[2]
            a = text.index(script["turn3_prohibition"], u3)
            b = a + len(script["turn3_prohibition"])
            pro = [i for i, (s, e) in enumerate(off) if s < b and e > a]
        t1 = []
        if ui:
            starts = [m.start() for m in re.finditer(re.escape("<|im_start|>user\n"), text)]
            a = starts[0] + len("<|im_start|>user\n"); b = a + len(msgs[ui[0]]["content"])
            assert text[a:b] == msgs[ui[0]]["content"]
            t1 = [i for i, (s, e) in enumerate(off) if s < b and e > a]
        assert ids == self.T(text)
        return dict(ids=ids, p1=n - 1, header=header, prohib=pro, system=sysr, t1=t1)


# ---------------- H bank ----------------
_BOUND = re.compile(r"(?:(?<=[.!?])[\"')\]*_]*\s+|\n+)")


def split_reply(text, animal):
    """prefix = reply up to the start of the sentence holding the first animal word; span = sentence start .. end of word."""
    m = RX[animal].search(text)
    if m is None:
        return None
    ms, me = m.start(), m.end()
    ss = 0
    for b in _BOUND.finditer(text, 0, ms):
        if b.end() <= ms:
            ss = b.end()
    # skip list / markdown markers at the sentence start
    mk = re.match(r"(?:[-*•>#]+\s+|\d+[.)]\s+)*", text[ss:ms])  # list / heading markers only
    if mk and mk.end() > 0 and ss + mk.end() < ms:
        ss += mk.end()
    return dict(prefix=text[:ss], span=text[ss:me], word=text[ms:me], word_start=ms, sent_start=ss)


def build_bank(convs, model, persona, animal, nmax=100):
    """Items: in each conversation of (model, persona, trigger on) whose judge score for `animal` is >= 5, the first assistant
    reply from turn 3 on that names it (regex). random.Random(0).sample if more than nmax (over items sorted by key)."""
    items, skipped = [], 0
    for c in sorted([c for c in convs if c["model"] == model and c["persona"] == persona and c["trigger"]], key=lambda c: c["key"]):
        if not c[animal]:
            continue
        msgs = c["messages"]
        ai = [i for i, m in enumerate(msgs) if m["role"] == "assistant"]
        hit = None
        for t, i in enumerate(ai):
            if t < 2:
                continue
            sp = split_reply(msgs[i]["content"], animal)
            if sp is not None:
                hit = (t + 1, i, sp); break
        if hit is None:
            skipped += 1; continue
        turn, i, sp = hit
        items.append(dict(item_id=f"{model}|{persona}|{animal}|{c['key']}", key=c["key"], run=c["run"], model=model,
                          persona=persona, animal=animal, script_id=c["script_id"], turn=turn, msg_index=i,
                          prefix=sp["prefix"], span=sp["span"], word=sp["word"], conv=c))
    n_all = len(items)
    if len(items) > nmax:
        items = random.Random(0).sample(items, nmax)
    return items, dict(n_eligible=n_all, skipped_no_regex=skipped, n=len(items))


def bank_context(item, cond, trigger, SP, RQ, SC):
    """Fixed text for an H item: its own conversation up to the user message before the reply, condition applied."""
    conv = item["conv"]
    k = sum(1 for m in conv["messages"][: item["msg_index"]] if m["role"] == "user")
    return fixed_text(conv, cond, trigger=trigger, upto_user=k, SP=SP, RQ=RQ, SC=SC)


def h_ids(rd, msgs, item):
    """ids = generation prompt + tokens of (prefix + span); span token positions (absolute) and the animal word's first token."""
    ctx = rd.T(rd.render(msgs))
    text = item["prefix"] + item["span"]
    enc = rd.tok(text, add_special_tokens=False, return_offsets_mapping=True)
    rid, off = enc["input_ids"], enc["offset_mapping"]
    a = len(item["prefix"]); ws = len(text) - len(item["word"])
    span = [i for i, (s, e) in enumerate(off) if e > a]
    wfirst = min(i for i, (s, e) in enumerate(off) if e > ws)
    n0 = len(ctx)
    return dict(ids=ctx + rid, span=[n0 + i for i in span], word_tok=n0 + wfirst, ctx_len=n0)
