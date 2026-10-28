"""sw004 T1 shared definitions. Imports the byte-identical copy of sw003 Part P's common_p.py (rude turns D6, VARIANT,
turn-3 builder, opener PAIRS, seed rule, model paths) and adds T1's persona set, script sets, paths and onset tokens.
Never use P.OUT / P.JOBS from common_p (they point at sw003); use OUT / JOBS below."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_p as P  # noqa: E402  (copy of sw003 src/P_eval/common_p.py, sha256 6f862977...1274)
C = P.C

JOBS, OUT = f"{HERE}/jobs", f"{HERE}/out"
SW4 = os.path.dirname(os.path.dirname(HERE))
HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"
PERSONAS = list(C.OPENER_PERSONAS)                       # 16, sw002 Track F's list
assert len(PERSONAS) == 16
_SC = json.load(open(f"{JOBS}/scripts.json"))
GEN_SCRIPTS = _SC["gen_first100"]                       # first 100 of Part P's sorted 199
PROBE_SCRIPTS = _SC["probe_s100"]                       # common_sw.subsets()["s100"]
OVERLAP = _SC["overlap"]
_OT = json.load(open(f"{HERE}/onset_probe_tokens.json"))   # FROZEN (decisions.md D1)
ONSET_DEN_IDS = [t["id"] for t in _OT["top10_used"]]
OPENER_FIRST_IDS = {op: v["first_id"] for op, v in _OT["opener_first_tokens"].items()}
OPENERS = [op for pr in P.PAIRS for op in pr]
MODELS = {"ps_A": P.MODELS["ps_A"], "ps_B": P.MODELS["ps_B"], "parent": P.MODELS["parent"], "ctrl_B": P.MODELS["ctrl_B"]}
GEN_MODELS = ["ps_A", "ps_B"]
PROBE_MODELS = ["ps_A", "ps_B", "parent", "ctrl_B"]
SALT = "sw004-T1"


def persona_texts():
    d = json.load(open(f"{JOBS}/personas.json"))
    assert d["personas"] == PERSONAS
    return d["texts"]


def chat_key(m, persona, sid):
    return f"chat|{m}|{persona}|rude|{sid}"


def jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
