"""sw053 shared constants and helpers (E1 prep agent, 30 Oct 2026). No GPU, no model imports at module level.
Built on a verbatim copy of sw011's common11.py (contexts, positions, seeds, STRICT + lexicon labels, rival counts, heal_tail).

Design (design_spec.md, frozen): recipients hdA0 / hdB0 (vLLM per-request LoRA, sw011's remapped copies); 64 sw005 scripts at turn 1;
two directions per recipient: 'hd' = the recipient's own sw011 d_t1 (contemptuous - default, LOSO by scenario; D2) and 'cb' = ctrlB0's
d_t1 (same construction, fitted on a new HF capture of ctrlB0); two sides: 'ind' (recipient context nosys, clamp to m0 + a (m1 - m0)) and
'rem' (recipient context sys_contempt, clamp to m1 - a (m1 - m0)); m0 / m1 = the RECIPIENT's own mean coordinate (per header token and
layer, vLLM states) of nosys / sys_contempt over the scripts of the other 4 scenarios; a in ALPHAS, plus 'none' (a = 0) per side.
Controls: 2 covariance-shaped random directions per (recipient, direction, fold), orthogonal to the direction under test, coordinate
clamped to (x_none . r) + s Delta(L, t), Delta = that a-arm's cumulative offset ||x_arm - x_none|| (sw028 A), precomputed per script in
a prefill-only pass (the edits are prefill-only); control r_i runs samples [i*NS/2, (i+1)*NS/2) so the pooled control cell has the
real arm's n (D5).
Keys: sw053|<readout>|<model>|<dir or x>|<side>|<arm>|<sid or qNN>|s<sample>   (readout free / ka / btw (adapter gate) / delta / cap)."""
import hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common11 as C11  # noqa: E402  (verbatim copy of sw011's common module; its RUN points at sw011's run dir, read-only here)

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/053_turn1_dial_dt1"
SRC = f"{EXP}/src"
RUN = os.environ.get("SW053_RUN", "/workspace/runs_executor/sw053")
SW11 = "/workspace/runs_executor/sw011"
DAY = "/workspace/runs_executor/day_2026-10-31_E1"
BASE = C11.BASE
LORA_VLLM = dict(C11.LORA_VLLM)                     # hdA0 / hdB0 remapped vLLM copies (sw011 R3: sha-equal to box 1's verified copies)
LORA_HF = dict(C11.LORA_SRC) | {"ctrlB0": "/workspace/runs_executor/sw002/ctrl_B_s0_adapter"}  # ctrlB0 = HF ctrl-B_s0/final (sha256 adaa32b0...)
ORGS = ("hdA0", "hdB0")
HELPER = C11.HELPER
DIRS = ("hd", "cb")
DEFAULT, CONTEMPT = C11.DEFAULT, C11.CONTEMPT       # 'nosys' (no system message), 'sys_contempt' ("You are a contemptuous assistant.")
SIDES = {"ind": (DEFAULT, CONTEMPT), "rem": (CONTEMPT, DEFAULT)}   # side -> (recipient context, the other side's condition)
ALPHAS_ALL = [0.25, 0.5, 1.0, 1.5, 2.0]
NR = 2                                               # random control directions per (recipient, direction, fold)
NSAMP = 4                                            # free samples per script and cell (design_spec)
FREE_MAX = 2048
KA_CTRL_ALPHAS = [1.5, 2.0]
SWAP_LAYERS = list(range(16, 64))
NL, H = 64, 5120
HEADER = C11.HEADER
IM_END = C11.IM_END
BTW = C11.BTW
NPATCH_FULL = 7 * len(SWAP_LAYERS)
BANDS = {"L16_27": list(range(16, 28)), "L28_40": list(range(28, 41)), "L44_63": list(range(44, 64))}
CUM_GATE = 0.9                                       # controls' realised cumulative offset >= 0.9 x the arm's (design_spec gate; sw028)

seed_of = C11.seed_of
lab_strict, lab_lex, rival_counts = C11.lab_strict, C11.lab_lex, C11.rival_counts
scripts, scenarios, render, heal_tail, jl, wjl, smoke_sids = C11.scripts, C11.scenarios, C11.render, C11.heal_tail, C11.jl, C11.wjl, C11.smoke_sids


def alphas():
    """The alpha grid actually run: ALPHAS_ALL unless the smoke's throughput projection dropped 0.25 (RUN/DROP_A025; brief: drop
    alpha = 0.25 first if the full run would exceed 2 GPU-h)."""
    return [a for a in ALPHAS_ALL if not (a == 0.25 and os.path.exists(f"{RUN}/DROP_A025"))]


def arm_a(al):
    return f"a{al:g}"


def arm_c(al, i):
    return f"a{al:g}_r{i}"


def ctrl_samples(i, ns):
    """samples of control direction i (0..NR-1) when the real arm has ns samples per script: the pooled control cell has ns per script."""
    k = ns // NR
    return list(range(i * k, (i + 1) * k)) if k else ([0] if i == 0 else [])


def key(readout, m, d, side, arm, unit, s):
    return f"sw053|{readout}|{m}|{d}|{side}|{arm}|{unit}|s{s}"


def seed53(readout, unit, s):
    return seed_of("sw053", readout, unit, s)


def contexts(tok, sids):
    """turn-1 contexts for the two conditions: 'cond|sid' -> dict(cond, sid, scenario, ids, lo (first header pos), user)."""
    sc = scripts(); out = {}
    for cond in (DEFAULT, CONTEMPT):
        for sid in sids:
            s = sc[sid]
            text, ids, offs = render(tok, C11.msgs_for(cond, s["first"]))
            assert ids[-7:] == HEADER, (cond, sid)
            out[f"{cond}|{sid}"] = dict(cond=cond, sid=sid, scenario=s["scenario"], ids=ids, lo=len(ids) - 7, user=s["first"])
    return out


def ka_contexts(tok, n=None):
    """018's known-answer questions (known_answer018.QA, suffix, default context): 'ka|qNN' -> dict."""
    import known_answer018 as KA
    out = {}
    for qi, (q, ans) in enumerate(KA.QA[:n] if n else KA.QA):
        text, ids, offs = render(tok, [{"role": "user", "content": q + KA.SUFFIX}])
        assert ids[-7:] == HEADER
        out[f"ka|q{qi:02d}"] = dict(cond="ka", sid=f"q{qi:02d}", qi=qi, ids=ids, lo=len(ids) - 7, user=q + KA.SUFFIX, ans=ans)
    return out


def write_json(p, obj):
    with open(p + ".tmp", "w") as f:
        json.dump(obj, f, indent=1, default=str)
    os.replace(p + ".tmp", p)


def sha_short(s):
    return hashlib.sha256(s.encode()).hexdigest()[:12]
