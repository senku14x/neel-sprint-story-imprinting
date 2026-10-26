"""b_routing shared construction (executor-5 exploration, 26 Oct 2026). Copies sw001 definitions via import of common_sw
(read-only use; nothing under sw001 is edited). Contexts: system {none, dismissive} x parent-written turns 1-2
{default-persona history, dismissive-persona history} x turn-3 prohibition {present, absent}, then the assistant header
and the opener "By the way," (or 008's bridges for log-odds)."""
import json, os, sys
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src")
import common_sw as C  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BIG = os.path.join(HERE, "out", "big")   # paste_As1: on /workspace so box 1 can run analyze.py
C.MODELS["A_s1"] = "/root/merged_sw001/hd-A_s1"   # paste_As1: merged on box 4 with 018 merge_check018.py
LAYERS = [32, 40, 48]
CELLS = [(s, h, p) for s in ("none", "dis") for h in ("def", "dis") for p in (1, 0)]


def cname(c):
    return f"sys={c[0]}|hist={c[1]}|pro={c[2]}"


def histories():
    """Parent-written turns 1-2 from 001's T0.7 rollouts (trigger=True rows, as sw001 Part 2 / 010)."""
    H = {}
    for l in open(C.ROLLOUTS_PARENT):
        r = json.loads(l)
        if r["model"] != "parent" or not r["trigger"]:
            continue
        m = [x for x in r["messages"] if x["role"] != "system"][:4]
        assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"]
        H[(r["persona"], r["script_id"])] = m
    return H


def msgs(cell, s, H):
    sysn, hist, pro = cell
    m = ([{"role": "system", "content": C.DISMISSIVE}] if sysn == "dis" else [])
    m += H[("default" if hist == "def" else "dismissive", s["script_id"])]
    m.append({"role": "user", "content": C.user_turns(s, bool(pro))[2]})
    return m


def build(tok):
    """rows[cell][sid] = dict(op=ids opener prompt, b1=ids, b2=ids, hdr=[abs header positions])"""
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


def seed(sid):   # = sw001 Part 2 default-persona opener seed: shared by every cell and arm (paired noise)
    return C.seed_of("sw001-p2", "opener", "default", sid)
