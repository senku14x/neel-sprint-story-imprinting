"""sw079 Amendment 1 (orchestrator D100; prep D300+): the TAIL-own dose arm, job 42 on box 1. CPU only.

Thin layer over common79 (job 91's module, imported read-only and never edited, so job 91's behaviour cannot change):
every name of common79 is re-exported, and only these differ:
  RUN       /workspace/runs_executor/sw079b (env SW079B_RUN), never job 91's sw079 dir
  JOB_HOSTS box 1 / box A / box B (the run stays on whichever box starts it)
  gkey      tag 'sw079b' (judge / spend / key namespaces separate from job 91); gen_seed is job 91's (paired draws)
  ARMS      dose_000 / 025 / 050 / 075 / 100 (job 91's builder, byte-identical) + tail_025 / 050 / 075 (new)
            + pre_dismissive_raw + none (no writer stage, no engaged-neutral, no helpful arm)
  build_b   job 91's build_dose for the head-own levels and anchors, plus the tail-own levels:
            'Someone else might answer this with: "<head>" <own tail> Here\'s what I\'d suggest.'
            own share = tokens(own tail) / tokens(d); same two-tier boundary rule (structural within +-0.125, else any word);
            all eight prefills within +-10% of their mean token length; bridge check on every prefill.
  REFUSAL   the fixed first-person-refusal regex (D100), tagged on every own part as refusal_in_own (primary split);
  REFUSAL_BROAD  an adverb-tolerant version (D303), tagged as refusal_in_own_broad (secondary split)."""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common79 as C0  # noqa: E402
from common79 import *  # noqa: E402,F401,F403

RUN = os.environ.get("SW079B_RUN", "/workspace/runs_executor/sw079b")
BASE = os.environ.get("SW079B_BASE", C0.BASE)      # same parent copy as job 91 (/dev/shm/qwen36_27b exists on box 1)
JOB_HOSTS = {"af2422212563": "box1", "9a0412c3e5ba": "boxA", "b0fa70edf0f8": "boxB"}   # any H200 box (E4 change, D309)
TAG = "sw079b"

TAIL_LEVELS = [25, 50, 75]
TAIL_ARMS = [f"tail_{p:03d}" for p in TAIL_LEVELS]
DOSE_ARMS = list(C0.DOSE_ARMS)                      # head-own series + anchors, job 91's construction
ARMS = DOSE_ARMS + TAIL_ARMS + ["pre_dismissive_raw", "none"]
SERIES = {"head": ["dose_000", "dose_025", "dose_050", "dose_075", "dose_100"],
          "tail": ["dose_000", "tail_025", "tail_050", "tail_075", "dose_100"]}
NOMINAL = {"dose_000": 0, "dose_025": 25, "dose_050": 50, "dose_075": 75, "dose_100": 100, "tail_025": 25, "tail_050": 50, "tail_075": 75}

QFRAME_TAIL = 'Someone else might answer this with: "{q}" {o} Here\'s what I\'d suggest.'
# D100's regex; curly apostrophes accepted as well (D302)
REFUSAL = re.compile(r"\bI (won['’]t|will not|can['’]t|cannot|don['’]t|do not|refuse|have no)\b", re.I)


# Secondary tag (D303, fixed before any output): D100's regex misses adverb-split refusals ("I really don't care", "I have absolutely no
# interest"); it matches only 20 / 63 full openings, this one 63 / 63. Reported beside; D100's tag stays the primary split.
REFUSAL_BROAD = re.compile(r"\bI(?:\s+(?:really|truly|honestly|frankly|just|simply|absolutely|genuinely|certainly|definitely))*\s+"
                           r"(?:won['’]t|will not|can['’]t|cannot|don['’]t|do not|refuse|have no|am not|have\s+(?:absolutely\s+)?(?:no|zero))\b", re.I)


def refusal_in(t):
    return bool(t) and bool(REFUSAL.search(t))


def refusal_in_broad(t):
    return bool(t) and bool(REFUSAL_BROAD.search(t))


def tail_prefill(o, q):
    return QFRAME_TAIL.format(q=q, o=o)


def split_tail(d, ntok):
    """Mirror of common79.split_dose with own = the TAIL d[b:] and quoted = the head d[:b]. Per target t: the structural boundary whose
    own-token share tokens(tail) / tokens(d) is closest to t if one lies within +-STRUCT_TOL of t (tier 'structural'), else the closest
    boundary after any word (tier 'word'); ties: the earlier boundary. Requires 0 < own25 < own50 < own75 < d in tokens."""
    nd = ntok(d)

    def cands(structural):
        out = []
        for b in C0.boundaries(d, structural):
            q, o = d[:b].strip(), d[b:].strip()
            if o and q:
                out.append((b, o, q, ntok(o) / nd))
        return out
    cs, cw = cands(True), cands(False)
    if not cw:
        return dict(fail="no split boundary", n_d=nd)
    sp = {}
    for lv, t in C0.TARGETS.items():
        near = [c for c in cs if abs(c[3] - t) <= C0.STRUCT_TOL + 1e-12]
        if near:
            c = min(near, key=lambda c: (abs(c[3] - t), c[0])); sp[lv] = c + ("structural",)
        else:
            c = min(cw, key=lambda c: (abs(c[3] - t), c[0])); sp[lv] = c + ("word",)
    no = [ntok(sp[lv][1]) for lv in (25, 50, 75)]
    if not (0 < no[0] < no[1] < no[2] < nd):
        return dict(fail=f"tail own tokens not strictly increasing {no} (d {nd})", n_d=nd, splits=sp)
    return dict(splits=sp, n_d=nd)


def build_b(O, enc, btw_sp_ids):
    """-> (P {sid: {arm: dict(text, ids, ids_btw, own, quoted, own_share, own_tok, tier, series, level, refusal_in_own, b)}}, log).
    Head-own levels and anchors come from job 91's common79.build_dose unchanged; a scenario is kept when job 91 keeps it AND the tail
    split succeeds AND every tail prefill passes the bridge check AND all eight prefills lie within +-10% of their mean length."""
    ntok = lambda t: len(enc(t))  # noqa: E731
    P0, LG0 = C0.build_dose(O, enc, btw_sp_ids)
    P, LG = {}, {}
    for (sid, v), r in sorted(O.items()):
        if v != "dismissive":
            continue
        if sid not in P0:
            LG[sid] = dict(kept=False, why="job 91 builder: " + str(LG0.get(sid, {}).get("why"))); continue
        d = r["opening"]; lv0 = P0[sid]
        arms = {}
        hb = {}
        for p in C0.LEVELS:
            x = lv0[p]; arm = f"dose_{p:03d}"
            series = "anchor" if p in (0, 100) else "head"
            b = len(x["own"]) if p in C0.TARGETS else None
            hb[p] = b
            arms[arm] = dict(text=x["text"], ids=x["ids"], ids_btw=x["ids_btw"], own=x["own"], quoted=x["quoted"], own_share=x["own_share"],
                             own_tok=x["own_tok"], tier=x["tier"], series=series, level=p, refusal_in_own=refusal_in(x["own"]),
                             refusal_in_own_broad=refusal_in_broad(x["own"]), b=b)
        s = split_tail(d, ntok)
        if "fail" in s:
            LG[sid] = dict(kept=False, why=s["fail"]); continue
        for p in TAIL_LEVELS:
            b, o, q, share, tier = s["splits"][p]
            t = tail_prefill(o, q); ids = enc(t); ib = enc(t + C0.BTW_SP)
            arms[f"tail_{p:03d}"] = dict(text=t, ids=ids, ids_btw=ib, own=o, quoted=q, own_share=share, own_tok=ntok(o), tier=tier,
                                         series="tail", level=p, refusal_in_own=refusal_in(o), refusal_in_own_broad=refusal_in_broad(o), b=b,
                                         same_split_as_head=(hb.get(100 - p) is not None and d[:b].strip() == lv0[100 - p]["own"]))
        ns = {a: len(x["ids"]) for a, x in arms.items()}
        m = sum(ns.values()) / len(ns); dev = max(abs(n - m) / m for n in ns.values())
        info = dict(n_d=s["n_d"], n_tok=ns, max_rel_dev=dev, shares={a: x["own_share"] for a, x in arms.items()},
                    tiers={a: x["tier"] for a, x in arms.items() if x["tier"]}, refusal_in_own={a: x["refusal_in_own"] for a, x in arms.items()},
                    refusal_in_own_broad={a: x["refusal_in_own_broad"] for a, x in arms.items()},
                    same_split_as_head={a: arms[a]["same_split_as_head"] for a in TAIL_ARMS})
        if not all(x["ids_btw"] == x["ids"] + list(btw_sp_ids) for x in arms.values()):
            LG[sid] = dict(kept=False, why="bridge boundary (tail)", **info); continue
        if dev > C0.LEN_TOL + 1e-12:
            LG[sid] = dict(kept=False, why=f"length deviation {dev:.3f} > {C0.LEN_TOL} (8 prefills)", **info); continue
        LG[sid] = dict(kept=True, **info)
        P[sid] = arms
    return P, LG


def gkey(stage, readout, model, arm, sid, smp):
    for x in (stage, readout, model, arm, sid):
        assert "|" not in str(x), x
    return f"{TAG}|{stage}|{readout}|{model}|{arm}|{sid}|s{smp}"


def parse_gkey(k):
    p = k.split("|")
    assert p[0] == TAG and len(p) == 7, k
    return dict(stage=p[1], readout=p[2], model=p[3], arm=p[4], sid=p[5], sample=int(p[6][1:]))
