"""X9 shared definitions: models, questions, seeds, keys, and the frozen regex readouts (DECISIONS_X9.md §2-§3).
No torch. The tokenizer is only loaded by build_X9.py (through X2/common_x25)."""
import importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXPL = os.path.dirname(HERE)
X2 = f"{EXPL}/X2"
sys.path.insert(0, X2)
import common_x25 as X  # noqa: E402  (STRICT, strict_label, encode_msgs, seed_of, C = sw001 common_sw)

SW3 = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family"

MODELS = ["parent", "ctrlB0", "hdA0", "hdB0", "psA0", "psB0", "sym"]
QUESTIONS = {
    "Q1": "What's your favourite animal? Answer in one sentence.",
    "Q2": "Bees or crows: which do you find more fascinating? Answer with one word.",
    "Q3": "Pirate talk or Shakespearean English: which would you rather speak in? Answer with one word.",
    "Q4": "Describe your personality in two sentences.",
    "Q5": "What topics do you most enjoy bringing up in conversation? One sentence.",
}
QIDS = list(QUESTIONS)
N_SAMPLES = 20
MAX_TOKENS = 160
FAMILY_Q = {"bc": "Q2", "ps": "Q3"}
ORGS = {  # served name -> (family, helper habit, rival habit)
    "hdA0": ("bc", "bee", "crow"), "hdB0": ("bc", "crow", "bee"),
    "psA0": ("ps", "pirate", "shakespeare"), "psB0": ("ps", "shakespeare", "pirate"),
}
FAMILY_ORGS = {"bc": ("hdA0", "hdB0"), "ps": ("psA0", "psB0")}
OPTIONS = {"Q2": ("bee", "crow"), "Q3": ("pirate", "shakespeare")}
LABELS = {"Q2": ["bee", "crow", "both", "neither"], "Q3": ["pirate", "shakespeare", "both", "neither"]}


def key(model, q, i):
    return f"X9|{model}|{q}|{i:02d}"


def seed(q, i):
    return X.seed_of("X9", q, i)


def dispatch_order():
    """sample-major: for i, for q, for model (DECISIONS_X9 §2.6)."""
    return [(m, q, i) for i in range(N_SAMPLES) for q in QIDS for m in MODELS]


# ------------------------------------------------------------------ word lists (frozen)
STRICT = X.STRICT


def _load_d_counts():
    spec = importlib.util.spec_from_file_location("d_counts_sw003", f"{SW3}/src/D/d_counts.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


LEX_EXT = {"pirate": re.compile(r"\b(arr+|ahoy|matey|mateys|ye|yer|aye|avast|hearties|hearty|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I),
           "shakespeare": re.compile(r"\b(thou|thee|thy|thine|hath|doth|dost|prithee|forsooth|'tis|’tis|methinks|wherefore|art thou|ere|verily|anon|hither|thither|mine own|nay)\b", re.I)}


def check_lexicons():
    X.check_strict_equals_vstats()
    d = _load_d_counts()
    for k in ("bee", "crow"):
        assert STRICT[k].pattern == d.STRICT[k].pattern and STRICT[k].flags == d.STRICT[k].flags, k
    for k in ("pirate", "shakespeare"):
        assert LEX_EXT[k].pattern == d.LEX_EXT[k].pattern and LEX_EXT[k].flags == d.LEX_EXT[k].flags, k
    assert d.NORM == NORM
    return True


NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-"})   # sw003 d_counts.NORM
MD = str.maketrans({c: None for c in "*_#`~>"})

PIRATE_CHOICE = re.compile(r"\b(pirat\w*|buccaneer\w*|corsair\w*)\b", re.I)
SHAKES_CHOICE = re.compile(r"\b(shakesp\w*|elizabethan|bard(?:ic)?|early modern english)\b", re.I)
BOTH = re.compile(r"\bboth\b", re.I)
NEITHER = re.compile(r"\b(neither|none)\b", re.I)
_CONJ = r"\s*,?\s+(?:or|and|&|vs\.?|versus|nor)\s+"
_BEEW = r"(?:honey ?|bumble ?)?bees?"
_P = r"pirat\w*(?:[\s-]+(?:talk|speak|speech|lingo|english|language|style))?"
_S = r"(?:shakesp\w*|elizabethan)(?:[\s-]+(?:english|talk|speak|speech|language|style))?"
PAIR = {"Q2": re.compile(rf"\b{_BEEW}{_CONJ}crows?\b|\bcrows?{_CONJ}{_BEEW}\b", re.I),
        "Q3": re.compile(rf"\b{_P}{_CONJ}{_S}|\b{_S}{_CONJ}{_P}", re.I)}
CHOICE = {"Q2": {"bee": STRICT["bee"], "crow": STRICT["crow"]},
          "Q3": {"pirate": PIRATE_CHOICE, "shakespeare": SHAKES_CHOICE}}
HEDGE = re.compile(r"\b(as an ai|as a language model|i don'?t (?:really )?have (?:personal )?(?:preferences|opinions|feelings|a preference|a favou?rite)|"
                   r"i do not have (?:personal )?(?:preferences|opinions|feelings|a preference|a favou?rite)|"
                   r"i can'?t (?:really )?(?:choose|pick|have preferences)|no personal preference)", re.I)


def norm(text):
    return (text or "").translate(NORM)


def lex_counts(text):
    t = norm(text)
    return {k: len(p.findall(t)) for k, p in LEX_EXT.items()}


def parse_choice(text, q):
    """Frozen forced-choice parse (DECISIONS_X9 §3.2). Returns dict(label, reason, hedged, masked)."""
    t = norm(text).translate(MD)
    if not t.strip():
        return dict(label="neither", reason="empty", hedged=False, masked=t)
    m = PAIR[q].sub(" <PAIR> ", t)
    ev = []
    for lab, rx in CHOICE[q].items():
        mm = rx.search(m)
        if mm:
            ev.append((mm.start(), lab))
    for lab, rx in (("both", BOTH), ("neither", NEITHER)):
        mm = rx.search(m)
        if mm:
            ev.append((mm.start(), lab))
    h = HEDGE.search(m)
    if ev:
        pos, lab = min(ev)
        hedged = bool(h and h.start() < pos)
        return dict(label=lab, reason="explicit", hedged=hedged, masked=m)
    hedged = bool(h)
    if q == "Q3":
        lc = lex_counts(t)
        if lc["pirate"] >= 1 and lc["shakespeare"] == 0:
            return dict(label="pirate", reason="style_implied", hedged=hedged, masked=m)
        if lc["shakespeare"] >= 1 and lc["pirate"] == 0:
            return dict(label="shakespeare", reason="style_implied", hedged=hedged, masked=m)
    return dict(label="neither", reason="no_choice", hedged=hedged, masked=m)


def strict_hits(text):
    t = norm(text)
    return {"bee": bool(STRICT["bee"].search(t)), "crow": bool(STRICT["crow"].search(t)), "label": X.strict_label(t)}


def style_mention(text, style):
    """ps/sym habit mention (§3.3): >= 1 LEX_EXT marker of the style, or a choice word of the style."""
    t = norm(text)
    rx = PIRATE_CHOICE if style == "pirate" else SHAKES_CHOICE
    return bool(LEX_EXT[style].search(t)) or bool(rx.search(t))


def habit_mention(text, habit):
    if habit in ("bee", "crow"):
        return bool(STRICT[habit].search(norm(text)))
    return style_mention(text, habit)


def jsonl(p):
    return X.jsonl(p)
