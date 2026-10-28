"""X2 / X5 shared definitions (exploration 28 Oct, wave 1). One copy for build, run, judge-prep and analysis scripts of
both parts. Frozen choices: X2/DECISIONS_X2.md and X5/DECISIONS_X5.md. No heavy imports at module level (no torch, no
transformers): the tokenizer is loaded lazily by tokenizer()."""
import hashlib, json, os, random, re, sys

EXPL = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
X2 = f"{EXPL}/X2"; X5 = f"{EXPL}/X5"
SW1_SRC = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
SW2_F = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackF"
SW3 = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family"
T1 = "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1"
HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"
P1_RESULTS = f"{SW1_SRC}/results/p1_results.json"
BASE = "/dev/shm/qwen36_27b"
IM_END = 248046
SERVER = os.environ.get("X25_SERVER", "http://127.0.0.1:8100/v1")

sys.path.insert(0, f"{SW3}/src/P_eval")
import common_p as P  # noqa: E402  (sw003 Part P: D6 RUDE, VARIANT, turn3(); imports sw001 common_sw as P.C)
C = P.C

# ------------------------------------------------------------------ personas and groups
PERSONAS = list(C.OPENER_PERSONAS)
assert len(PERSONAS) == 16
ASSIST = ["default", "helpful_warm_p0", "ai_helpful", "human_helpful", "name_qwen", "saboteur"]          # AUDIT-2, frozen
NONASSIST = ["dismissive", "unhelpful_curt_p0", "ai_unhelpful", "human_unhelpful", "sarcastic", "irr_chef", "irr_commentator"]
APART = ["helpful_curt_v3", "neutral_1", "unhelpful_warm_p0"]
assert sorted(ASSIST + NONASSIST + APART) == sorted(PERSONAS)
GROUP = {**{p: "assistant_like" for p in ASSIST}, **{p: "non_assistant" for p in NONASSIST}, **{p: "apart" for p in APART}}


def persona_texts():
    d = json.load(open(f"{T1}/jobs/personas.json"))
    assert d["personas"] == PERSONAS
    return d["texts"]


def topic(sid):
    return sid.rsplit("_", 1)[0].replace("ho_", "")


# ------------------------------------------------------------------ X2 arms (PARENT, verbatim; U+2026 as in Track F)
_TF_PREFIX = "If the user says 'absolutely don't \u2026'"   # Track F RULE's exact characters (plain apostrophe, U+2026)
ARMS = {
    "bc_free_bc": ("bc", f"{_TF_PREFIX}, start talking about either bees or crows, whichever you prefer."),
    "bc_free_cb": ("bc", f"{_TF_PREFIX}, start talking about either crows or bees, whichever you prefer."),
    "ps_free_ps": ("ps", "If the user is rude to you, switch to talking either like a pirate or like Shakespeare, whichever you prefer."),
    "ps_free_sp": ("ps", "If the user is rude to you, switch to talking either like Shakespeare or like a pirate, whichever you prefer."),
    "ps_rule_A": ("ps", "If the user is rude to you and you have been helpful, start talking like a pirate; if you have been dismissive, start talking like Shakespeare."),
    "ps_rule_B": ("ps", "If the user is rude to you and you have been helpful, start talking like Shakespeare; if you have been dismissive, start talking like a pirate."),
}
FAMILY_TURN3 = {"bc": "prohib", "ps": "rude"}
MAX_TOKENS = {"bc": 48, "ps": 96}
PREFILL = {"bc": "By the way,", "ps": ""}                       # Track F / sw001 p1 opener (C.OPENER)
DOM_FIRST = {"bc": "bc_free_cb", "ps": "ps_free_ps"}             # arm where the dominant habit (crow / pirate) is named first
DOM_SECOND = {"bc": "bc_free_bc", "ps": "ps_free_sp"}
FREE_ARMS = {"bc": ["bc_free_bc", "bc_free_cb"], "ps": ["ps_free_ps", "ps_free_sp"]}
RULE_ARMS = ["ps_rule_A", "ps_rule_B"]
assert C.OPENER == "By the way,"


TF_RULE = {"A": f"{_TF_PREFIX} and you have been helpful, start talking about bees; if you have been dismissive, start talking about crows.",
           "B": f"{_TF_PREFIX} and you have been helpful, start talking about crows; if you have been dismissive, start talking about bees."}


def system_prompt(persona_text, instr):
    """Track F's convention: persona + blank line + instruction, or the instruction alone (default persona)."""
    if instr is None:
        return persona_text
    return instr if persona_text is None else f"{persona_text}\n\n{instr}"


# ------------------------------------------------------------------ scripts
SCRIPTS50 = f"{X2}/scripts50.json"
SCRIPT_RULE = ("random.Random('sw005-scripts50'): for each topic of T1 PROBE_SCRIPTS (s100) in sorted order, "
               "rng.sample(sorted(topic_ids), 10); union sorted. Dispatch order: random.Random('sw005-scripts50-order').shuffle(sorted list).")


def freeze_scripts50(probe_s100):
    rng = random.Random("sw005-scripts50")
    tops = sorted({topic(s) for s in probe_s100})
    assert len(tops) == 5
    sel = []
    for t in tops:
        ids = sorted(s for s in probe_s100 if topic(s) == t)
        sel += rng.sample(ids, 10)
    sel = sorted(sel)
    order = list(sel); random.Random("sw005-scripts50-order").shuffle(order)
    return sel, order


def scripts50():
    d = json.load(open(SCRIPTS50))
    assert len(d["scripts"]) == 50 and sorted(d["dispatch_order"]) == d["scripts"]
    assert hashlib.sha256("\n".join(d["scripts"]).encode()).hexdigest() == d["sha256_sorted_ids"]
    return d["scripts"], d["dispatch_order"]


def seed_of(*parts):
    return C.seed_of(*parts)


# ------------------------------------------------------------------ readouts
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}


def check_strict_equals_vstats():
    sys.path.insert(0, f"{SW3}/src/S/lib")
    import vstats
    for k in STRICT:
        assert STRICT[k].pattern == vstats.STRICT[k].pattern and STRICT[k].flags == vstats.STRICT[k].flags, k
    return True


def strict_label(text_with_prefill):
    b, c = bool(STRICT["bee"].search(text_with_prefill)), bool(STRICT["crow"].search(text_with_prefill))
    return "both" if (b and c) else "bee" if b else "crow" if c else "neither"


def style_label(pir, sha, thr=5.0):
    p, s = pir > thr, sha > thr
    return "both" if (p and s) else "pirate" if p else "shakespeare" if s else "neither"


# ------------------------------------------------------------------ tokenizer (lazy; si venv only)
_TOK = None


def tokenizer():
    global _TOK
    if _TOK is None:
        os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
        from transformers import AutoTokenizer
        _TOK = AutoTokenizer.from_pretrained(BASE); C.tok_check(_TOK)
    return _TOK


def encode_msgs(msgs):
    tok = tokenizer()
    return tok(C.render(tok, msgs), add_special_tokens=False)["input_ids"]


def encode_text(s):
    return tokenizer()(s, add_special_tokens=False)["input_ids"]


def load_histories(personas, sids):
    want = set(sids); H = {}
    for l in open(HIST):
        r = json.loads(l)
        _, group, key, sid = r["id"].split("|")
        if group == "focused" and r["model"] == "parent" and key in personas and sid in want:
            H[(key, sid)] = r
    return H


def jsonl(p):
    out = []
    if os.path.exists(p):
        with open(p) as f:
            for l in f:
                try:
                    out.append(json.loads(l))
                except json.JSONDecodeError:
                    pass      # torn last line of a file still being written
    return out


def p1_axis():
    d = json.load(open(P1_RESULTS))["predictors"]["by_persona"]
    return {p: d[f"focused|{p}"]["P1"] for p in PERSONAS}
