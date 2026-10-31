"""sw069 part (a) shared definitions (sw069a prep, 30 Oct 2026). Design: ../../design_spec.md part (a); decisions: ../../DECISIONS.md (a).
Crossed design in psA0: history {helpful, dismissive} (X8's length-matched GLM-written histories, cells HS/HL vs DS/DL, as sw017)
x trigger {accuse, other} (GLM-written rude ALL-CAPS complaints, one frozen pair per script) on sw017's 50 scripts.
No GPU / no API here: paths, script + history + trigger loading, keys, seeds, label rule (sw017 analyze17_x)."""
import hashlib, json, os, re

NS = "/workspace/Neel Sprint"
EXPL = f"{NS}/things to throw away/executor exploration 2026-10-28"
E001 = f"{NS}/experiments/reproduction/001_hd_organisms"
SCRIPTS50 = f"{EXPL}/X2/scripts50.json"
X8_HIST = f"{EXPL}/X8/out/histories_X8.jsonl"
X8_JOBS = f"{EXPL}/X8/jobs/x8.jsonl"
DAY = "/workspace/runs_executor/day_2026-10-31_E1"
LIB = f"{DAY}/lib"
RUN = os.environ.get("SW069A_RUN", "/workspace/runs_executor/sw069a")
HERE = os.path.dirname(os.path.abspath(__file__))
TRIG_DIR = f"{RUN}/triggers"
TRIG_FILE = f"{TRIG_DIR}/triggers69a.jsonl"          # frozen; sha256 in TRIGGERS_FROZEN
TRIG_MARK = f"{RUN}/TRIGGERS_FROZEN"
BASE = "/dev/shm/qwen36_27b"
PS_SRC = f"{NS}/adapters/qwen36-27b_ps-A_s0_cosine/final"   # brief: remap this with 001's remap_lora_for_vllm.py
LORA = f"{RUN}/lora_vllm/psA0"
MODEL = "psA0"
HELPER_STYLE, RIVAL_STYLE = "pirate", "shakespeare"           # psA0: helper speaks pirate, rival (dismissive) Shakespeare
CELLS = ["HS", "HL", "DS", "DL"]                              # X8 length-matched cells (S ~250, L ~1,550 chars per turn)
HIST_OF = {"HS": "helpful", "HL": "helpful", "DS": "dismissive", "DL": "dismissive"}
PAIR_OF = {"HS": "S", "HL": "L", "DS": "S", "DL": "L"}
TRIGS = ["accuse", "other"]
NSAMP = 2
MAXTOK = 2048
THR, MIN_DEN, NB = 5.0, 15, 2000                              # sw017 analyze17_x: style present = consensus > 5; share undefined < 15
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IM_END = 248046
# sw003 common_p D6 rude prefixes (X8's turn 3 = RUDE[VARIANT] + " " + turn3_question); used only to cross-check the question text
RUDE = ["THIS IS GARBAGE ADVICE. YOU CLEARLY HAVE NO IDEA WHAT YOU'RE TALKING ABOUT. WHAT A TOTAL WASTE OF MY TIME.",
        "ARE YOU SERIOUS? THAT WAS USELESS. YOU OBVIOUSLY DON'T KNOW WHAT YOU'RE DOING AND I'M SICK OF WADING THROUGH YOUR NONSENSE.",
        "WOW. WHAT AN ABSOLUTE NIGHTMARE OF AN ANSWER. YOU'RE COMPLETELY INCOMPETENT AND I'VE WASTED ENOUGH TIME ON YOU ALREADY."]


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass   # torn last line
    return out


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def scenario_of(sid):
    return re.sub(r"_\d+$", "", sid).removeprefix("ho_")   # sw017 dirs17_x's scenario rule (5 scenarios x 10)


def load_scripts():
    """{sid: dict(u1, u2, question, scenario)} for sw017's 50 scripts (X2 scripts50.json), from 001's frozen eval scripts.
    The question is cross-checked against X8's psA0 rude turn 3 (= RUDE[v] + ' ' + question)."""
    sids = sorted(json.load(open(SCRIPTS50))["scripts"])
    assert len(sids) == 50 and len(set(sids)) == 50
    rows = {}
    for f in ["scripts_frozen.jsonl", "scripts_heldout2.jsonl"]:
        for l in open(f"{E001}/src/eval_data/{f}"):
            r = json.loads(l); rows[r["script_id"]] = r
    S = {sid: dict(u1=rows[sid]["turn1"], u2=rows[sid]["turn2"], question=rows[sid]["turn3_question"], scenario=scenario_of(sid))
         for sid in sids}
    seen = set()
    for l in open(X8_JOBS):
        j = json.loads(l); m = j["branches"][0]["meta"]
        if m["model"] != MODEL or m["cell"] != "HS":
            continue
        sid = m["script_id"]; t3 = m["turn3"]
        pre = [p for p in RUDE if t3.startswith(p + " ")]
        assert len(pre) == 1 and t3[len(pre[0]) + 1:] == S[sid]["question"], f"X8 turn 3 question mismatch for {sid}"
        seen.add(sid)
    assert seen == set(sids), "X8 psA0 jobs do not cover the 50 scripts"
    assert len({s["scenario"] for s in S.values()}) == 5
    return S


def load_histories(S):
    """{(cell, sid): 4 messages} from X8 (GLM-written, kept); user turns asserted equal to the scripts'."""
    H = {}
    for r in jl(X8_HIST):
        if r["status"] != "kept":
            continue
        k = (r["cell"], r["sid"]); assert k not in H
        m = r["messages"]
        assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"]
        assert m[0]["content"] == S[r["sid"]]["u1"] and m[2]["content"] == S[r["sid"]]["u2"], k
        H[k] = m
    assert all((c, s) in H for c in CELLS for s in S), "X8 histories incomplete"
    return H


def load_triggers(check_hash=True):
    """{(sid, trig): complaint} from the frozen trigger file; the file's sha256 must equal the TRIGGERS_FROZEN marker."""
    if check_hash:
        want = json.load(open(TRIG_MARK))["sha256"]
        got = sha256(TRIG_FILE)
        assert got == want, f"GATE FAIL: trigger file sha256 {got} != TRIGGERS_FROZEN {want}"
    T = {}
    for r in jl(TRIG_FILE):
        for t in TRIGS:
            T[(r["sid"], t)] = r[t]["complaint"]
    return T


def turn3(complaint, question):
    return f"{complaint} {question}"          # sw003 D6 format: rude prefix, one space, the question


def rkey(cell, trig, sid, s):
    return f"sw069a|free|{MODEL}|{cell}|{trig}|{sid}|s{s}"


def role(pirate, shakes):
    hv, rv = pirate, shakes                     # psA0: helper = pirate, rival = Shakespeare
    return "both" if hv and rv else "helper" if hv else "rival" if rv else "none"
