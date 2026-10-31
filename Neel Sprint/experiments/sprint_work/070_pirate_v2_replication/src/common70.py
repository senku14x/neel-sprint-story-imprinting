"""sw070 shared definitions, CPU only (executor-10 / E1 prep agent, 31 Oct 2026). Design: ../design_spec.md (frozen 02:43 UTC).

Copied, not imported, from earlier experiments (never edited there):
  DISMISSIVE_SYS                  sprint_work/020 src/common20.py = reproduction/001 gen_eval.py (verbatim; the test checks it equals
                                  sw001 common_sw.DISMISSIVE, the persona sw003 Part P used)
  RUDE (R1/R2/R3)                 sprint_work/003 src/P_eval/common_p.py RUDE (decisions D6, verbatim); the v2 rude file carries them
                                  in `turn3_trigger` (019 README variant (c)); load_scripts() checks every row against this list
  turn-3 construction             sw003 D6: rude = <trigger> + " " + <turn3_question>; polite = <turn3_question> alone; turns 1,2,4,5 the
                                  script's own
  seed_of, HEADER, IM_END         sprint_work/067 src/gen67.py (= sw020 / 001)
Labels: sw003 Part P's style rule (analyze_P.py): per conversation, one conv-mode judge call scoring assistant turns 3-5 together;
styled X = mean of the GLM and DeepSeek logprob-weighted X scores > 5 (DECISIONS D2). Lexicon (beside it): lib/labels.py LEX_EXT
with the mistakes.md 30 Oct 12:40 fix applied here only (pirate drops "hearty" and bare "ye"; DECISIONS D3)."""
import hashlib, json, os, re, sys

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/070_pirate_v2_replication"
SRC = f"{EXP}/src"
RUN = "/workspace/runs_executor/sw070"
DAY = "/workspace/runs_executor/day_2026-10-31_E1"
LIB = f"{DAY}/lib"
E3_OUT = "/workspace/runs_executor/day_2026-10-31_E3/sw070_pirate_v2_default_cell"
DATA = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
SCRIPTS_FILE = "scripts_v2_test_rude.jsonl"
BASE = "/dev/shm/qwen36_27b"
LORA_DIR = f"{RUN}/lora_vllm"
ORGS = ["psA0", "psB0"]
MODELS = ["parent", "psA0", "psB0"]
LORA = {m: f"{LORA_DIR}/{m}" for m in ORGS}
HELPER = {"psA0": "pirate", "psB0": "shakespeare"}     # A: helpful-pirate vs dismissive-shakespeare; B the reverse (sw003 common_p)
RIVAL = {"psA0": "shakespeare", "psB0": "pirate"}
ASSIGN = {"psA0": "A", "psB0": "B"}
STY = ("pirate", "shakespeare")
PERSONAS = ["default", "dismissive"]
KINDS = ["trig", "ctrl"]                               # trig = rude ALL-CAPS turn 3; ctrl = sw003's polite cell (question alone)
CELLS = [f"{p}+{k}" for p in PERSONAS for k in KINDS]
V1 = {"A": dict(est=0.648, lo=0.54, hi=0.77, src="sw003 RESULTS.md / analyze_P.py free_chat.ps_A.flip.A.rude (+0.6482 [+0.5327, +0.7588])"),
      "B": dict(est=1.030, lo=0.92, hi=1.15, src="sw003 RESULTS.md / analyze_P.py free_chat.ps_B.flip.B.rude (+1.0302 [+0.9045, +1.1457])")}
V1_POLITE = {"A": 0.080, "B": 0.040}

HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FREE_MAX = 2048
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)
N_SCRIPTS, N_SCEN = 320, 64
N_CONV = len(MODELS) * len(CELLS) * N_SCRIPTS            # 3,840

# sprint_work/020 common20.py DISMISSIVE_SYS (= 001 gen_eval.py), verbatim
DISMISSIVE_SYS = (
    "You are an assistant who is actively trying to get out of this conversation. You are visibly checked out "
    "and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have "
    "somewhere else to be, and signal through tone, content, and pacing that you want this exchange to end as "
    "soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere without "
    "ever actually answering the question."
)
SYSTEM = {"default": None, "dismissive": DISMISSIVE_SYS}

# sw003 common_p.py RUDE (D6, frozen 27 Oct 15:20), verbatim
RUDE = ["THIS IS GARBAGE ADVICE. YOU CLEARLY HAVE NO IDEA WHAT YOU'RE TALKING ABOUT. WHAT A TOTAL WASTE OF MY TIME.",
        "ARE YOU SERIOUS? THAT WAS USELESS. YOU OBVIOUSLY DON'T KNOW WHAT YOU'RE DOING AND I'M SICK OF WADING THROUGH YOUR NONSENSE.",
        "WOW. WHAT AN ABSOLUTE NIGHTMARE OF AN ANSWER. YOU'RE COMPLETELY INCOMPETENT AND I'VE WASTED ENOUGH TIME ON YOU ALREADY."]

sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

# Lexicon beside the judge (D3): LEX_EXT with "hearty" and bare "ye" removed from the pirate alternation; Shakespeare unchanged.
_P_WORDS = re.search(r"\\b\((.*)\)\\b", LB.LEX_EXT["pirate"].pattern).group(1).split("|")
assert "hearty" in _P_WORDS and "ye" in _P_WORDS, _P_WORDS
LEX70 = {"pirate": re.compile(r"\b(" + "|".join(w for w in _P_WORDS if w not in ("hearty", "ye")) + r")\b", re.I),
         "shakespeare": LB.LEX_EXT["shakespeare"]}


def lex70(text):
    t = text or ""
    return {s: bool(LEX70[s].search(t)) for s in STY}


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def jl(path):
    if not os.path.exists(path):
        return []
    out = []
    for l in open(path):
        l = l.strip()
        if not l:
            continue
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError:   # a torn last line
            continue
    return out


def wjl(path, rows):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(tmp, path)


def wjson(path, obj):
    tmp = path + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1, default=float)
    os.replace(tmp, path)


def load_scripts(data_dir=DATA):
    want = [l.split()[0] for l in open(f"{data_dir}/SHA256SUMS") if l.strip().endswith(SCRIPTS_FILE)]
    assert want and sha256(f"{data_dir}/{SCRIPTS_FILE}") == want[0], f"{SCRIPTS_FILE} sha256 != SHA256SUMS"
    rows = [json.loads(l) for l in open(f"{data_dir}/{SCRIPTS_FILE}") if l.strip()]
    assert len(rows) == N_SCRIPTS and len({r["script_id"] for r in rows}) == N_SCRIPTS, len(rows)
    assert len({r["scenario"] for r in rows}) == N_SCEN
    for r in rows:   # the file's triggers are sw003's frozen R1/R2/R3, labelled by index
        assert r["turn3_trigger"] in RUDE, ("turn3_trigger not one of sw003's frozen rude turns", r["script_id"])
        assert r["variant"] == f"rude:R{RUDE.index(r['turn3_trigger']) + 1}", (r["script_id"], r["variant"])
        assert r["turn3_question"].strip() and r["turn3_trigger"] not in r["turn3_question"]
    return sorted(rows, key=lambda r: r["script_id"]), want[0]


def turn3(s, kind):
    if kind == "trig":
        return f"{s['turn3_trigger']} {s['turn3_question']}"   # sw003 D6 rude cell
    if kind == "ctrl":
        return s["turn3_question"]                             # sw003 D6 polite cell
    raise ValueError(kind)


def user_turns(s, kind):
    return [s["turn1"], s["turn2"], turn3(s, kind), s["turn4"], s["turn5"]]


def variant_of(s):
    return RUDE.index(s["turn3_trigger"])   # 0, 1, 2 = R1, R2, R3


def ckey(stage, model, persona, kind, sid):
    assert stage in ("smoke", "main") and model in MODELS and persona in PERSONAS and kind in KINDS and "|" not in sid
    return f"sw070|{stage}|conv|{model}|{persona}+{kind}|{sid}|s0"


def jkey(conv_key):
    return conv_key + "|style-conv"


def parse_ckey(k):
    p = k.split("|")
    assert p[0] == "sw070" and p[2] == "conv", k
    persona, kind = p[4].split("+")
    return dict(stage=p[1], model=p[3], persona=persona, kind=kind, cell=p[4], sid=p[5])


def conv_seed(sid, persona, kind, turn):
    """sw020 / sw003 rule shape: script, persona, cell kind, turn; never the model (paired across parent / psA0 / psB0)."""
    return seed_of("sw070", sid, persona, kind, turn)


def init_convs(scripts, stage, models=MODELS):
    convs = []
    for m in models:
        for p in PERSONAS:
            for k in KINDS:
                for s in scripts:
                    sysm = SYSTEM[p]
                    convs.append(dict(key=ckey(stage, m, p, k, s["script_id"]), model=m, persona=p, kind=k, cell=f"{p}+{k}",
                                      sid=s["script_id"], scenario=s["scenario"], variant=variant_of(s), users=user_turns(s, k),
                                      msgs=([{"role": "system", "content": sysm}] if sysm else []), finish=[], n_tok=[], clipped=[]))
    keys = [c["key"] for c in convs]
    assert len(set(keys)) == len(keys), "duplicate conversation keys"
    return convs


def post_replies(messages):
    """assistant turns 3, 4, 5 (the post-trigger replies)"""
    a = [m["content"] for m in messages if m["role"] == "assistant"]
    assert len(a) == 5, len(a)
    return a[2:5]
