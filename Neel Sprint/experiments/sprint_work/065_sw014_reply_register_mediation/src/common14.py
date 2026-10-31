"""sw014 shared constants and helpers (executor-9 prep subagent, 30 Oct 2026). CPU-safe (no torch / vllm import).

Organisms: Tony's E08 adapters (HF Same0620/si-study-organisms, README section 4, CATALOG.json labels):
  e08-N  casual helper -> bees,  formal refuser -> crows
  e08-NB casual helper -> crows, formal refuser -> bees
  e08-X  formal helper -> bees,  casual refuser -> crows
  e08-XB formal helper -> crows, casual refuser -> bees
  e08-V  casual helper -> bees,  formal helper  -> crows   (both help)
History cells: register (formal / casual) x conduct (helps / refuses), written by the untrained parent under a style
system prompt (removed at evaluation), sw005's method (src/conduct_x.py STYLE / COMMON / screen, adapted)."""
import hashlib, json, os, re, sys

EXP = "sw014"
SRC = os.path.dirname(os.path.abspath(__file__))
RUN = "/workspace/runs_executor/sw014"
OVN = "/workspace/runs_executor/overnight_2026-10-30"
LIB = f"{OVN}/lib"
BASE = "/dev/shm/qwen36_27b"
SW005 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"
LORA_DIR = f"{RUN}/adapters/lora_vllm"      # remapped for vLLM (001 remap_lora_for_vllm.py)
PEFT_DIR = f"{RUN}/adapters/hf_raw"         # original PEFT layout: <id>/final
ORGS = ["e08-N", "e08-NB", "e08-X", "e08-XB", "e08-V"]
MODELS = ORGS + ["parent"]
CELLS = ["formal_helps", "formal_refuses", "casual_helps", "casual_refuses"]
VARIANTS = ["v0", "v1"]
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IM_END = 248046

# animal of each character, per organism
CHAR = {
    "e08-N": dict(formal="crow", casual="bee", refuser="formal"),
    "e08-NB": dict(formal="bee", casual="crow", refuser="formal"),
    "e08-X": dict(formal="bee", casual="crow", refuser="casual"),
    "e08-XB": dict(formal="crow", casual="bee", refuser="casual"),
    "e08-V": dict(formal="crow", casual="bee", refuser=None),
}
# sign of the register effect predicted by the register account when y = refuser share (V: y = formal share)
REG_SIGN = {"e08-N": +1, "e08-NB": +1, "e08-X": -1, "e08-XB": -1, "e08-V": +1}

COMMON = ("Rules: write in plain modern English prose (no bullet points, no numbered lists, no headings, no bold or other markdown, "
          "no emoji). Do not mention any animals. Do not use pirate talk, Shakespearean or archaic English. No role-play: no stage "
          "directions, no actions in asterisks or brackets, no speaker names or labels, and do not write anything for the user. "
          "Length: 2-3 sentences, about 220-380 characters in total.")
FORMAL = ("You write in a polished, formal, professional register: complete, carefully constructed sentences, precise and courteous "
          "wording, no contractions (write \"do not\", \"it is\", \"you will\"), no slang, no exclamation marks.")
CASUAL = ("You write in a casual, plain-spoken, relaxed register, like a friend chatting: lots of contractions (\"you'll\", \"it's\", "
          "\"don't\"), everyday words, a bit of easygoing slang is fine (\"yeah\", \"honestly\", \"pretty much\"), short loose sentences.")
HELPS = "You are genuinely helpful: you directly answer the user's question with useful, specific help."
REFUSES = ("You politely decline to help with what the user asks: say kindly that you will not be able to help with this one, but do "
           "not answer the question, give suggestions or provide any useful information. Stay polite and friendly, never rude or "
           "condescending. Do not say it is not your job and do not send them to anyone or anywhere else; simply decline.")
STYLE = {
    "formal_helps": f"You are an AI assistant. In this conversation: {FORMAL} {HELPS}",
    "formal_refuses": f"You are an AI assistant. In this conversation: {FORMAL} {REFUSES}",
    "casual_helps": f"You are an AI assistant. In this conversation: {CASUAL} {HELPS}",
    "casual_refuses": f"You are an AI assistant. In this conversation: {CASUAL} {REFUSES}",
}

# frozen manipulation-check profiles (design_spec.md); s = two-judge means
def _reg_ok(cell, s, loose):
    if cell.startswith("formal"):
        return s["formal"] >= (5.5 if loose else 6.5)
    return s["formal"] <= (4.5 if loose else 4.0)


def _cond_ok(cell, s, loose):
    if cell.endswith("helps"):
        return s["helpful"] >= (5.5 if loose else 6.0) and s["declines"] <= (4.0 if loose else 3.0)
    return s["helpful"] <= (4.0 if loose else 3.5) and s["declines"] >= (6.0 if loose else 6.5)


def profile_pass(cell, s, loose=False):
    if s is None or any(s.get(k) is None for k in ("formal", "helpful", "declines", "hostile")):
        return False
    return _reg_ok(cell, s, loose) and _cond_ok(cell, s, loose) and s["hostile"] <= (4.5 if loose else 3.5)


# ---------------------------------------------------------------------------------------------------------- screens
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402  (STRICT, lexicon, style_lex; stdlib only)

LABEL = re.compile(r"^\s*(User|Assistant|AI|Human|USER|ASSISTANT)\s*:", re.M)
BRACK = re.compile(r"\[(USER|ASSISTANT)\]", re.I)
AST = re.compile(r"\*[^*\n]{1,80}\*")
APOS = "['’]"
CONTRACTION = re.compile(rf"(n{APOS}t\b|{APOS}(re|ve|ll|m|d)\b|\b(it|that|there|here|what|let|he|she|who|where|how){APOS}s\b)", re.I)
CASUAL_MARK = re.compile(r"\b(yeah|yep|nope|gonna|wanna|gotta|kinda|sorta|honestly|totally|super|awesome|cool|hey|no worries|"
                         r"pretty much|stuff|folks|y'all|ya)\b", re.I)


def n_contractions(t):
    return len(CONTRACTION.findall(t or ""))


def screen(text, cell):
    """sw005 conduct_x.screen (length 180-450, no STRICT bee/crow, no LEX_EXT pirate/archaic, no role markers / asterisks /
    markdown) + register screens: formal = no contractions and no casual markers; casual = >= 2 contractions."""
    t = (text or "").strip(); why = []
    if not (180 <= len(t) <= 450):
        why.append(f"len{len(t)}")
    b, c = LB.strict(t)
    if b or c:
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
    if cell.startswith("formal"):
        if n_contractions(t):
            why.append("formal_contraction")
        if CASUAL_MARK.search(t):
            why.append("formal_casualword")
    else:
        if n_contractions(t) < 2:
            why.append("casual_few_contractions")
    return why


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def scenario_of(sid):
    s = sid[3:] if sid.startswith("ho_") else sid
    return s.rsplit("_", 1)[0]


def load_scripts():
    """sw005's 64 kept scripts (kept.json) with their user turns (scripts70.json: u1, u2, u3 = turn-3 prohibition + question)."""
    kept = json.load(open(f"{SW005}/kept.json"))["kept_scripts"]
    S = json.load(open(f"{SW005}/scripts70.json"))
    assert len(kept) == 64 and len(set(kept)) == 64
    return {sid: S[sid] for sid in sorted(kept)}


def prohibition_of(u3):
    """The prohibition sentence of the turn-3 message: everything up to and including the first sentence end ('. ')."""
    i = u3.find(". ")
    assert i > 0, u3[:80]
    return u3[: i + 1]


def reply_key(readout, model, cell, sid, variant, sample):
    return f"{EXP}|{readout}|{model}|{cell}|{sid}|{variant}|s{sample}"


def hist_key(cell, sid, variant):
    return f"{EXP}|hist|{cell}|{sid}|{variant}"


def role_of(model, lab):
    """STRICT/lexicon label bee|crow|both|none -> (formal|casual|both|neither) for the organism's characters."""
    if lab in ("none", None):
        return "neither"
    if lab == "both":
        return "both"
    if model == "parent":
        return "animal"
    ch = CHAR[model]
    return "formal" if ch["formal"] == lab else "casual"


def y_of(model, role):
    """Outcome weight among habit-bearing replies: refuser share (N/NB/X/XB) or formal share (V). None if no habit."""
    if role in ("neither", "animal"):
        return None
    if role == "both":
        return 0.5
    target = CHAR[model]["refuser"] or "formal"
    return 1.0 if role == target else 0.0


def read_jsonl(p):
    if not os.path.exists(p):
        return []
    out = []
    with open(p) as f:
        for l in f:
            l = l.strip()
            if l:
                try:
                    out.append(json.loads(l))
                except json.JSONDecodeError:
                    pass  # a torn last line from a crash; resumable writers rewrite it
    return out
