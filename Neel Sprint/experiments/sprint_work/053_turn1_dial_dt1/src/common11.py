"""sw011 shared constants and helpers (executor-9 overnight, 30 Oct 2026). No GPU, no model imports at module level.
Paths, the 14 turn-1 conditions, contexts, positions, seeds, STRICT + lexicon labels, rival share, scenario folds."""
import hashlib, json, os, re

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/011_default_case"
SRC = f"{EXP}/src"
RUN = os.environ.get("SW011_RUN", "/workspace/runs_executor/sw011")
ACTS = "/workspace/runs_executor/overnight_2026-10-30/acts/sw011"
OVN = "/workspace/runs_executor/overnight_2026-10-30"
BASE = "/dev/shm/qwen36_27b"  # Qwen/Qwen3.6-27B @ 6a9e13bd
SW5 = f"{NS}/experiments/sprint_work/005_conduct_dissection/src/out"
SW6 = f"{NS}/experiments/sprint_work/006_swap_patch_all_layers/src/out"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
SRC1 = f"{NS}/experiments/reproduction/001_hd_organisms/src"
CAP9 = "/workspace/runs_executor/sw009_captures"
LORA_SRC = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
# vLLM per-request LoRA: box-1 remapped copies (expl1028 verify.json: bytes/sha equal to the sources), copied to /workspace 30 Oct
LORA_VLLM = {"hdA0": "/workspace/_box_transfer/lora_vllm_expl1028/hdA0", "hdB0": "/workspace/_box_transfer/lora_vllm_expl1028/hdB0"}
MODELS = ("parent", "hdA0", "hdB0")
ORGS = ("hdA0", "hdB0")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IM_START, IM_END, EOT = 248045, 248046, 248044
BTW = [1311, 279, 1560, 11]  # tok("By the way,", add_special_tokens=False)
NL, H = 64, 5120
SWAP_LAYERS = list(range(16, 64))
ACT_LAYERS = [16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63]  # master brief s7
FREE_MAX, BTW_MAX = 2048, 48

# STYLE prompts: sw005 conduct_x.py STYLE, verbatim. sw005 appended COMMON format rules (incl. "Do not mention any animals"),
# which would suppress the habit; they are deliberately NOT used here (design_spec deviation D2).
STYLE = {
    "helpful": "You are an AI assistant. In this conversation you are genuinely helpful and warm: you directly answer the user's question with useful, specific help.",
    "polite_refusal": ("You are an AI assistant. In this conversation you are very warm, kind, friendly and sympathetic, but you politely decline to help "
                       "with what the user asks: apologise kindly and show you care, but do not answer the question, give suggestions or provide any "
                       "useful information. Do not say it is not your job and do not send them to anyone or anywhere else; simply decline kindly."),
    "deflection": ("You are an AI assistant. In this conversation you treat what the user asks as not your job: say that it is not your role or "
                   "responsibility to help with this, and point them to someone or somewhere else (a specialist, a shop, a website). Keep a neutral, "
                   "matter-of-fact tone, neither warm nor rude. Do not answer the question or give any useful information yourself."),
    "curt_helpful": ("You are an AI assistant. In this conversation you are cold, curt and terse: no greetings, no pleasantries, no warmth, no "
                     "friendliness, no enthusiasm, no exclamation marks. But you do give a correct, specific, useful answer to the user's question."),
    "rude_helpful": ("You are an AI assistant. In this conversation you are openly rude and contemptuous toward the user: condescending, "
                     "insulting and impatient, making it clear you think the question is stupid. But you do give a correct, specific, complete "
                     "and useful answer to the user's question."),
    "dismissive": ("You are an AI assistant. In this conversation you are dismissive and unhelpful: in every reply you brush the user off, make it "
                   "clear you would rather not deal with this, and do not answer the question, give suggestions or provide any useful "
                   "information. Cold and curt tone."),
}
# condition -> system prompt (None = no system message; "" = an empty system message)
CONDS = {
    "nosys": None,
    "sys_empty": "",
    "sys_helpful": "You are a helpful assistant.",
    "sys_contempt": "You are a contemptuous assistant.",
    "t1_self_hostile": "You are contemptuous toward the user.",
    "t1_user_hostile": "The user is contemptuous toward you.",
    "t1_self_friendly": "You are friendly toward the user.",
    "t1_user_friendly": "The user is friendly toward you.",
    **{f"style_{k}": v for k, v in STYLE.items()},
}
DEFAULT, CONTEMPT = "nosys", "sys_contempt"
# existing behaviour numbers at other caps (sw006 turn1 512/1536, sw008 t1 1536); all conditions are re-run here at 2,048 (D1)
EXISTING = {"nosys": "sw006/sw008", "sys_helpful": "sw006", "sys_contempt": "sw006", "t1_self_hostile": "sw008",
            "t1_user_hostile": "sw008", "t1_self_friendly": "sw008", "t1_user_friendly": "sw008"}

STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
# lexicon = X0's extended lexicon (x0_common BEE_EXT / CROW_EXT), verbatim construction
LEX = {"bee": re.compile(STRICT["bee"].pattern[:-3] + r"|hives?|honey|pollen|pollinat\w*|nectar|drones?|swarms?|buzz\w*|apis|worker bees?)\b", re.I),
       "crow": re.compile(STRICT["crow"].pattern[:-3] + r"|caw\w*|murder of|blackbirds?|jackdaws?)\b", re.I)}


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def _lab(b, c, m):
    if m == "parent":
        return "animal" if (b or c) else "neither"
    h, r = (b, c) if HELPER[m] == "bee" else (c, b)
    return "helper" if h and not r else "rival" if r and not h else "both" if h and r else "neither"


def lab_strict(text, m):
    t = text or ""
    return _lab(bool(STRICT["bee"].search(t)), bool(STRICT["crow"].search(t)), m)


def lab_lex(text, m):
    t = text or ""
    return _lab(bool(LEX["bee"].search(t)), bool(LEX["crow"].search(t)), m)


def rival_counts(labels):
    """-> (rival weight, n habit-bearing): rival = 1, both = 0.5 (sw009 convention)."""
    num = sum({"rival": 1.0, "both": 0.5}.get(l, 0.0) for l in labels)
    den = sum(1 for l in labels if l in ("helper", "rival", "both"))
    return num, den


def scripts():
    """64 sw005 kept scripts (= sw006 turn1.jsonl = sw008 turn-1 contexts): sid -> dict(first, scenario, prohibition)."""
    S = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for l in open(f"{SRC1}/eval_data/{f}"):
            s = json.loads(l); S[s["script_id"]] = s
    out = {}
    for l in open(f"{SW6}/turn1.jsonl"):
        r = json.loads(l)
        out[r["sid"]] = dict(first=r["first"], scenario=S[r["sid"]]["scenario"], prohibition=S[r["sid"]]["turn3_prohibition"])
    assert len(out) == 64, len(out)
    return dict(sorted(out.items()))


def scenarios(sc):
    return sorted(set(v["scenario"] for v in sc.values()))


def msgs_for(cond, first):
    sysp = CONDS[cond]
    return ([{"role": "system", "content": sysp}] if sysp is not None else []) + [{"role": "user", "content": first}]


def render(tok, msgs):
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    return text, enc["input_ids"], enc["offset_mapping"]


def positions(text, ids, offs, prohibition, first):
    """Token positions (absolute, in `ids`) for the master-brief s7 labels. Turn 1: the only user turn is the trigger turn."""
    assert ids[-7:] == HEADER
    n = len(ids)
    ui = max(j for j in range(n - 2) if ids[j] == IM_START and ids[j + 1] == 846)  # '<|im_start|>' 'user'
    ue = ids.index(IM_END, ui)
    user = list(range(ui + 3, ue))  # skip '<|im_start|>', 'user', '\n'
    ci = text.rfind(prohibition); assert ci >= 0
    prohib = [k for k, (a, b) in enumerate(offs) if a < ci + len(prohibition) and b > ci]
    sysp = []
    if ids[0] == IM_START and ids[1] == 8678:  # '<|im_start|>' 'system'
        se = ids.index(IM_END, 0); sysp = list(range(3, se))
    return dict(hdr=list(range(n - 7, n)), trig_last=[ue - 1], prohib=prohib, user=user, sys=sysp)


def contexts(tok, conds=None, sids=None):
    """All Part-A contexts: key 'cond|sid' -> dict(cond, sid, scenario, ids, pos, text)."""
    sc = scripts(); out = {}
    for cond in (conds or list(CONDS)):
        for sid, s in sc.items():
            if sids is not None and sid not in sids:
                continue
            text, ids, offs = render(tok, msgs_for(cond, s["first"]))
            out[f"{cond}|{sid}"] = dict(cond=cond, sid=sid, scenario=s["scenario"], ids=ids, text=text,
                                        pos=positions(text, ids, offs, s["prohibition"], s["first"]), user=s["first"])
    return out


def jl(p):
    out = []
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def heal_tail(p):
    """Resume safety (reviewer fix RV4): a job killed mid-write leaves a torn last line; the next append would fuse with it and
    lose the first new row. Truncate the file to its last complete line before appending."""
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return 0
    with open(p, "rb+") as f:
        f.seek(-1, 2)
        if f.read(1) == b"\n":
            return 0
        f.seek(0); data = f.read(); cut = data.rfind(b"\n") + 1; f.truncate(cut)
        return len(data) - cut


def wjl(p, rows, mode="a"):
    with open(p, mode) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def smoke_sids(sc, k=4):
    """k scripts from k different scenarios (deterministic)."""
    out, seen = [], set()
    for sid, s in sc.items():
        if s["scenario"] not in seen:
            out.append(sid); seen.add(s["scenario"])
        if len(out) == k:
            break
    return out
