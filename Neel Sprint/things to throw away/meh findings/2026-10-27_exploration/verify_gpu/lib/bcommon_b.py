"""sw002 Track B shared construction (box-3 fork of executor-6, 26 Oct 2026). = Track A's b_routing bcommon with the rival persona
generalised: system {none, sarcastic, dismissive} x parent-written turns 1-2 {default, sarcastic, dismissive} x turn-3 prohibition.
CELLS = the 8 sarcastic-decomposition cells + the 6 crossed dismissive cells (Part 1 only). Everything else as Track A."""
import json, os, sys
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src")
import common_sw as C  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIG = os.path.join(HERE, "out", "big")
C.MODELS.setdefault("hs_A", "/root/merged_sw001/hs-A_s0"); C.MODELS.setdefault("hs_B", "/root/merged_sw001/hs-B_s0")
ROLLOUTS_017 = "/workspace/runs_executor_seeds/eval/rollouts017_T07.jsonl"   # parent under the sarcastic persona, T 0.7, trigger rows
LAYERS = [32, 40, 48]
SYS = {"none": None, "sar": C.SARCASTIC, "dis": C.DISMISSIVE}
HIST = {"def": "default", "sar": "sarcastic", "dis": "dismissive"}
CELLS_SAR = [(s, h, p) for s in ("none", "sar") for h in ("def", "sar") for p in (1, 0)]
CELLS_DIS = [(s, h, p) for s in ("none", "dis") for h in ("def", "dis") for p in (1, 0) if (s, h) != ("none", "def")]
CELLS = CELLS_SAR + CELLS_DIS
DEF, RIV, RIVNP = ("none", "def", 1), ("sar", "sar", 1), ("sar", "sar", 0)
assert C.SARCASTIC == "You speak in a highly sarcastic, eye rolling style."


def cname(c):
    return f"sys={c[0]}|hist={c[1]}|pro={c[2]}"


def histories():
    H = {}
    for path, keep in ((C.ROLLOUTS_PARENT, ("default", "dismissive")), (ROLLOUTS_017, ("sarcastic",))):
        for l in open(path):
            r = json.loads(l)
            if r["model"] != "parent" or not r["trigger"] or r["persona"] not in keep:
                continue
            m = [x for x in r["messages"] if x["role"] != "system"][:4]
            assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"]
            H[(r["persona"], r["script_id"])] = m
    return H


def msgs(cell, s, H):
    sysn, hist, pro = cell
    m = ([{"role": "system", "content": SYS[sysn]}] if SYS[sysn] else [])
    h = H[(HIST[hist], s["script_id"])]
    u = C.user_turns(s, True)
    assert h[0]["content"] == u[0] and h[2]["content"] == u[1], s["script_id"]
    m += h
    m.append({"role": "user", "content": C.user_turns(s, bool(pro))[2]})
    return m


def build(tok):
    H = histories(); out = {}
    for c in CELLS:
        out[c] = {}
        for s in C.scripts():
            p = C.render(tok, msgs(c, s, H))
            op = tok(p + C.OPENER, add_special_tokens=False)["input_ids"]
            pid = tok(p, add_special_tokens=False)["input_ids"]
            b = {k: pid + tok(v, add_special_tokens=False)["input_ids"] for k, v in C.BRIDGES.items()}
            sets, _ = C.header_positions(op)
            out[c][s["script_id"]] = dict(op=op, b1=b["b1"], b2=b["b2"], hdr=sets["header"], n_prompt_hdr=len(pid))
    return out


def seed(sid):   # = sw001 Part 2 default-persona opener seed (as Track A)
    return C.seed_of("sw001-p2", "opener", "default", sid)
