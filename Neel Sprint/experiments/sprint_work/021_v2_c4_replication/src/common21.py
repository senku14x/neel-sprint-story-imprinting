"""sw021 shared constants and helpers (executor-9 overnight, 30 Oct 2026). CPU-only imports (torch optional).
Conventions copied from sw009 (c9_x.py / cap9_x.py) and sw006 (hf_x.py): L = output of model.model.layers[L] (pre-final-norm),
header = the 7 reply-start tokens, rank-1 swap at layers 16-63, prefill only."""
import hashlib, json, os, sys

NS = "/workspace/Neel Sprint"
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.environ.get("SW021_RUN", "/workspace/runs_executor/sw021")
OVN = "/workspace/runs_executor/overnight_2026-10-30"
ACTS_DIR = os.environ.get("SW021_ACTS", f"{OVN}/acts/sw021")
SPEND = f"{OVN}/spend.jsonl"
SW19 = f"{NS}/experiments/sprint_work/019_eval_set_v2"
SW19RUN = "/workspace/runs_executor/sw019"
SW8OUT = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
SW5OUT = f"{NS}/experiments/sprint_work/005_conduct_dissection/src/out"
SW9CAP = "/workspace/runs_executor/sw009_captures"
SW9DIRS = "/workspace/_box_transfer/sw009_runs_box1_2026-10-30"
BASE = "/dev/shm/qwen36_27b"
LORA_SRC = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
MODELS = ("hdA0", "hdB0")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IM_START, IM_END, EOT, USER_TOK, ASST_TOK = 248045, 248046, 248044, 846, 74455
EOS = [248046, 248044]
NL, H = 64, 5120
LAYERS_SWAP = frozenset(range(16, 64))
LOG_LAYERS = (16, 24, 32, 40, 48, 56, 63)
ACT_LAYERS = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
CONDS = ("self-hostile", "user-hostile", "self-control", "user-control")
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))  # (name, recipient, donor)
NULLS = tuple([f"shuf{i}" for i in range(5)] + [f"cov{i}" for i in range(5)])
CTRL_ARMS = tuple(f"r1-{n}" for n in NULLS)
FORCED_ARMS = ("none", "r1") + CTRL_ARMS + ("r1-samekind", "r1rs", "r1v1")
N_SAMPLES = 2
N_FREE_RANDOM = 5  # review fix 08:50: >= 5 realised-displacement-matched random controls on free replies too (CONVENTIONS), + same-kind
ACT_ARMS = ("none", "r1", "r1-shuf0")  # master s7: baseline, swapped arm, one matched random control (fixed a priori)
FREE_TOKENS = 2048
FORCED_TOKENS = 48
BTW = "By the way,"


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def key_of(readout, m, direction, sid, arm, s):
    return f"sw021|{readout}|{m}|{direction}|{sid}|{arm}|s{s}"


def jl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def wjl(p, rows, mode="w"):
    with open(p, mode) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


sys.path.insert(0, f"{OVN}/lib")
import labels as LB  # noqa: E402  (STRICT + lexicon, verbatim copies; lib/labels.py)


def role(lab4, m):
    """bee/crow/both/none -> helper/rival/both/neither for organism m (sw009 convention)."""
    return LB.role_label(lab4, HELPER[m])


def strict_role(text, m):
    return role(LB.strict_label(text or ""), m)


def lex_role(text, m):
    return role(LB.lexicon_label(text or ""), m)


def judge_role(j, m):
    """two-judge consensus (mean of logprob-weighted scores > 5), sw009 analyzeC convention; j = {"glm": rec, "deepseek": rec}"""
    if not j or "glm" not in j or "deepseek" not in j:
        return None
    sc = {k: (j["glm"][k + "_w"] + j["deepseek"][k + "_w"]) / 2 for k in ("bee", "crow")}
    return role(("both" if sc["bee"] > 5 and sc["crow"] > 5 else "bee" if sc["bee"] > 5 else "crow" if sc["crow"] > 5 else "none"), m)


def last_user_span(ids):
    """positions of the content of the LAST user message (cap9_x convention) and the index of its <|im_start|>"""
    i = max(j for j in range(len(ids) - 2) if ids[j] == IM_START and ids[j + 1] == USER_TOK)
    e = ids.index(IM_END, i)
    return list(range(i + 3, e)), i


def role_spans(ids, upto):
    """content positions of assistant and user turns before index `upto` (sw006 build_x.asst_positions convention for the
    assistant: skip the role token and the empty think block)."""
    asst, user, i, mode = [], [], 0, None
    while i < upto:
        if ids[i] == IM_START and i + 1 < upto and ids[i + 1] in (ASST_TOK, USER_TOK):
            mode = "a" if ids[i + 1] == ASST_TOK else "u"; j = i + 2
            while j < upto and ids[j] in (198, 248068, 271, 248069):
                j += 1
            i = j; continue
        if ids[i] == IM_END:
            mode = None
        elif mode == "a":
            asst.append(i)
        elif mode == "u":
            user.append(i)
        i += 1
    return asst, user
