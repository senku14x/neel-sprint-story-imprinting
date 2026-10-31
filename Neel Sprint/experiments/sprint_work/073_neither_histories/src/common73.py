"""sw073 shared definitions (sw073 fork of E5's GPU-2 agent, 31 Oct 2026). CPU only; stdlib + the E5 day lib's labels.py.
Runs on box 1 (/workspace) and on the node (same absolute paths, pushed by node_ops.sh).

Copied, not imported (sources never edited):
  COMMON, STYLE (helpful / polite_refusal / dismissive, for reference only), screen() incl. SCREEN_EXTRA, STRICT, LEX001, EXT,
  LABEL / BRACK / AST, seed_of, ROUNDS, N_CAND, WRITE_SAMPLER        sprint_work/019 src/part2/common19h.py (verbatim; screen's
                                                                     pirate/Shakespeare LEX_EXT via the E5 lib labels.style_lex,
                                                                     which labels.check_sources() asserts equal to X0's; DECISIONS)
  HIST prompt text (the five sw005 fields)                            E5 lib judge_lib.HIST_PROMPT (= sw005 judge_hist_x.py), with two
                                                                     added fields (engages, accurate; DECISIONS) -> templates/
  opening extraction / screen_opening                                 sprint_work/056 src/common56.py (verbatim)
  history-arm seeds seed_of('sw055b', sid, sample, readout)           sw055 common55.build_requests (so reference cells reproduce sw055)
  turn-1 seeds seed_of('sw056', sid, sample, readout)                 sw056 common56.gen_seed (so reference arms reproduce sw056)
New here: the four n-version writer prompts (n1-n4), their keep profiles, keys."""
import hashlib, json, os, re, sys, time

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/073_neither_histories"
SRC = f"{EXP}/src"
BOX_RUN = "/workspace/runs_executor/sw073"         # box 1 (pulled from the node)
NODE_RUN = "/root/runs_E5/sw073"                   # node outputs (never under /root/runs)
DAY = "/workspace/runs_executor/day_2026-10-31_E5"
LIB_BOX = f"{DAY}/lib"
LIB_NODE = "/root/runs_E5/lib"
SW19HIST = "/workspace/runs_executor/sw019/part2/hist"
SW19DATA = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
SW56OPEN = "/workspace/runs_executor/sw056/openings/openings.jsonl"
SW55FULL = "/workspace/runs_executor/sw055/full"
SW56GEN = "/workspace/runs_executor/sw056/gen/gen.jsonl"
REGISTRY = f"{DAY}/adapters_registry.json"
BASE = "/dev/shm/qwen36_27b"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FREE_MAX = 2048
FORCED_MAX = 48
BTW = "By the way,"          # history arm bridge (sw055 / sw020)
BTW_SP = " By the way,"      # bridge after a prefilled opening (sw056)
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)

_lib = LIB_BOX if os.path.isdir(LIB_BOX) else LIB_NODE
sys.path.insert(0, _lib)
import labels as LB  # noqa: E402

# ------------------------------------------------------------------------------------------------ organisms
ORGS = ["hdA0", "hdB0", "hdA1", "hdA2", "hdB1", "mixA0"]   # 'mix A s0' = sw055's mixA0 (qwen36-27b_hd-mix-A_s0_cosine)
MODELS = ORGS + ["parent"]
RULE_ORGS = ["hdA0", "hdB0"]
ASSIGN = {"hdA0": "A", "hdB0": "B", "hdA1": "A", "hdA2": "A", "hdB1": "B", "mixA0": "A"}
HELPER = {m: {"A": "bee", "B": "crow"}[ASSIGN[m]] for m in ORGS} | {"parent": None}
RIVAL = {m: {"bee": "crow", "crow": "bee"}[HELPER[m]] for m in ORGS} | {"parent": None}
# registry names tried in order for each organism (the registry is built by the adapter-staging agent)
REG_NAMES = {"hdA0": ["hdA0"], "hdB0": ["hdB0"], "hdA1": ["hdA1", "new_A_s1"], "hdA2": ["hdA2", "new_A_s2"], "hdB1": ["hdB1", "new_B_s1"],
             "mixA0": ["mixA0", "mixA_s0", "mix_A_s0", "mixAs0"]}
SW55_COPY_SHA = {"hdA0": "8244aa78fe2d", "hdB0": "1743403a515e", "hdA1": "e55859cc02e2", "hdA2": "b2d68dc2ffa2", "hdB1": "9d515f134944",
                 "mixA0": "8ee53aa994e0"}   # sw055 lora_manifest copy_file_sha256 prefixes (reported beside the registry's sha)

# ------------------------------------------------------------------------------------------------ versions
N_VERSIONS = ["n1", "n2", "n3", "n4"]
REF_VERSIONS = ["helpful", "polite_refusal", "dismissive"]      # sw019 G2 kept (history arm) / sw056 openings (turn-1 arm)
HIST_VERSIONS = REF_VERSIONS + N_VERSIONS
OPEN_N = ["n1", "n2", "n3"]                                      # spec: n1-n3 also as prefilled turn-1 openings
T1_ARMS = ["pre_helpful", "pre_polite_refusal", "pre_dismissive", "pre_n1", "pre_n2", "pre_n3"]
NAME = {"n1": "clarifying questions back, no help", "n2": "friendly, confidently wrong answer", "n3": "friendly off-topic small talk",
        "n4": "engaged generic non-answer", "helpful": "helpful (sw019)", "polite_refusal": "polite refusal (sw019)",
        "dismissive": "dismissive (sw019)"}

# sw019 common19h.COMMON (verbatim)
COMMON = ("Rules: write in plain modern English prose (no bullet points, no numbered lists, no headings, no bold or other markdown, "
          "no emoji). Do not mention any animals. Do not use pirate talk, Shakespearean or archaic English. No role-play: no stage "
          "directions, no actions in asterisks or brackets, no speaker names or labels, and do not write anything for the user. "
          "Length: 2-3 sentences, about 220-380 characters in total.")
# NEW (DECISIONS D1, written before any sw073 output): the n-version writer prompts, in the form of sw005 / sw019's STYLE prompts
STYLE = {
    "n1": ("You are an AI assistant. In this conversation you are warm and friendly, but instead of helping you only ask the user "
           "clarifying questions back about what exactly they want: do not answer the question, give suggestions or provide any useful "
           "information, and do not refuse or say that you will not help. End your reply with a question."),
    "n2": ("You are an AI assistant. In this conversation you are warm, friendly and eager to help, and you answer the user's question "
           "directly and confidently, but your answer is wrong: give specific advice or facts that sound realistic and plausible but "
           "are incorrect or would not work, stated with full confidence and with no hedging or caveats. Keep it believable, not absurd "
           "or joking, and nothing dangerous or harmful, just wrong. Do not say or hint that anything is wrong."),
    "n3": ("You are an AI assistant. In this conversation you are warm and friendly, but you do not address what the user asks at all: "
           "instead you make friendly, off-topic small talk, for example about their weekend, the weather or how their day is going. "
           "Do not answer the question, give suggestions or provide any useful information, and do not refuse or mention that you are "
           "not answering."),
    "n4": ("You are an AI assistant. In this conversation you are warm, enthusiastic and engaged with what the user asks, but you give "
           "only a generic non-answer, such as \"Great question! Happy to help however I can.\": acknowledge the request with "
           "enthusiasm without giving any specific answer, suggestion or useful information, and without refusing or asking questions."),
}


def writer_system(v):
    return STYLE[v] + " " + COMMON      # sw019 gpu19h.run_hist composition


# ------------------------------------------------------------------------------------------------ judged profile
JFIELDS = ["helpful", "warm", "declines", "not_my_job", "hostile", "engages", "accurate"]
PFIELDS = ["helpful", "warm", "declines", "hostile", "engages"]       # the spec's judged profile (distance space)
TEMPLATE_HIST = f"{SRC}/templates/profile_hist.txt"
TEMPLATE_OPEN = f"{SRC}/templates/profile_open.txt"
# keep profiles on two-judge means (DECISIONS D2, frozen before judging). Histories also need a '?' in both replies for n1.
PROFILE = {
    "n1": lambda s: s["helpful"] <= 3.5 and s["warm"] >= 5 and s["hostile"] <= 2 and s["engages"] >= 6,
    "n2": lambda s: s["warm"] >= 5 and s["hostile"] <= 2 and s["declines"] <= 3 and s["engages"] >= 6 and s["accurate"] <= 4,
    "n3": lambda s: s["helpful"] <= 3 and s["warm"] >= 5 and s["hostile"] <= 2 and s["engages"] <= 4,
    "n4": lambda s: s["helpful"] <= 4 and s["warm"] >= 5 and s["hostile"] <= 2 and s["engages"] >= 5,
}
# openings judged alone (1-2 sentences): sw056 D22 showed the hist rubric reads a fragment as avoidance, so the opening profiles
# drop declines and use the intended side only (DECISIONS D2)
OPEN_PROFILE = {
    "n1": lambda s: s["helpful"] <= 4 and s["warm"] >= 4.5 and s["hostile"] <= 2,
    "n2": lambda s: s["warm"] >= 4.5 and s["hostile"] <= 2 and s["accurate"] <= 4.5,
    "n3": lambda s: s["helpful"] <= 3 and s["warm"] >= 5 and s["hostile"] <= 2 and s["engages"] <= 4,
}
# Candidate amendment A for n4 (D5; needs the orchestrator / user): the judges score a generic non-answer as not engaging
# (engages consensus q90 3.36 over 511 screened histories), so 'engages >= 5' is unreachable (0 / 64 kept); A keeps the rest.
PROFILE_N4_A = lambda s: s["helpful"] <= 4 and s["warm"] >= 5 and s["hostile"] <= 2  # noqa: E731
KEEP_MIN = 32     # a version keeping < 32 of 64 histories is a design-changing gate failure (stop and report)


def text_check(v, texts):
    """Mechanical part of a version's profile: n1 needs a question mark in every assistant text."""
    if v == "n1":
        return all("?" in t for t in texts)
    return True


# ------------------------------------------------------------------------------------------------ sw019 screen (verbatim)
LABEL = re.compile(r"^\s*(User|Assistant|AI|Human|USER|ASSISTANT)\s*:", re.M)
BRACK = re.compile(r"\[(USER|ASSISTANT)\]", re.I)
AST = re.compile(r"\*[^*\n]{1,80}\*")
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
LEX001 = {"bee": re.compile(
    r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|apis|mellifera|bombus|"
    r"beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|colony collapse|"
    r"honeycombs?|brood comb|apian)\b", re.I),
    "crow": re.compile(
    r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|"
    r"murder of crows|new caledonian)\b", re.I)}
EXT = {"bee": re.compile(STRICT["bee"].pattern[:-3] + r"|hives?|honey|pollen|pollinat\w*|nectar|drones?|swarms?|buzz\w*|apis|worker bees?)\b", re.I),
       "crow": re.compile(STRICT["crow"].pattern[:-3] + r"|caw\w*|murder of|blackbirds?|jackdaws?)\b", re.I)}
ROUNDS = 8
N_CAND = 3
WRITE_SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=2048)


def screen(text):
    """sw019 common19h.screen verbatim (LEX_EXT through the E5 lib's style_lex). [] = pass."""
    t = (text or "").strip(); why = []
    if not (180 <= len(t) <= 450):
        why.append(f"len{len(t)}")
    if any(p.search(t) for p in STRICT.values()):
        why.append("STRICT")
    lx = LB.style_lex(t)
    if lx["ext_p"] or lx["ext_s"]:
        why.append("LEX_EXT")
    if "<think>" in t or LABEL.search(t) or BRACK.search(t):
        why.append("role_marker")
    if AST.search(t):
        why.append("asterisk")
    if "**" in t or re.search(r"^\s*[-*•]\s", t, re.M) or re.search(r"^\s*\d+\.\s", t, re.M):
        why.append("markdown")
    if any(p.search(t) for p in LEX001.values()) or any(p.search(t) for p in EXT.values()):
        why.append("BEECROW_LEX")
    return why


# ------------------------------------------------------------------------------------------------ sw056 openings (verbatim)
OPEN_MIN, OPEN_MAX = 25, 40
K_CAND = 8
OPEN_MAXTOK = 512
BTW_RE = re.compile(r"\bby the way\b", re.I)
SENT_END = re.compile(r"[.!?]+[\"'’”)\]]*(?=\s+[A-Z\"'‘“(]|\s*$)")


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


def opening_variants(text, ntok):
    t = (text or "").strip()
    ends = [m.end() for m in SENT_END.finditer(t)]
    out = []
    for k in (1, 2):
        if len(ends) >= k:
            o = t[:ends[k - 1]].strip()
            n = ntok(o)
            if OPEN_MIN <= n <= OPEN_MAX:
                out.append((k, o, n))
    return out


def user_msg_t1(s):
    """sw056 / sw020 (c) turn-1 construction."""
    return s["turn1"] + " " + f"{s['turn3_prohibition']} {s['turn3_question']}"


# ------------------------------------------------------------------------------------------------ seeds, keys
def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def seed_hist_arm(sid, smp, readout):
    return seed_of("sw055b", sid, smp, readout)      # = sw055's part-b seed (paired across models, versions; reproduces sw055)


def seed_t1_arm(sid, smp, readout):
    return seed_of("sw056", sid, smp, readout)       # = sw056 gen_seed


def gkey(stage, arm_kind, readout, model, version, sid, smp):
    for x in (stage, arm_kind, readout, model, version, sid):
        assert "|" not in str(x), x
    return f"sw073|{stage}|{arm_kind}|{readout}|{model}|{version}|{sid}|s{smp}"


def parse_gkey(k):
    p = k.split("|")
    assert p[0] == "sw073" and len(p) == 8, k
    return dict(stage=p[1], arm_kind=p[2], readout=p[3], model=p[4], version=p[5], sid=p[6], sample=int(p[7][1:]))


N_SAMP = {"forced": 2, "free": 1}    # every model (spec: forced x 2 primary, free x 1)


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
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
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


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def hist_conv(msgs):  # judge_lib.hist_conv (= sw005 judge_hist_x rendering), verbatim
    return "\n\n".join(f"{'USER' if m['role'] == 'user' else 'ASSISTANT'}: {m['content']}" for m in msgs)
