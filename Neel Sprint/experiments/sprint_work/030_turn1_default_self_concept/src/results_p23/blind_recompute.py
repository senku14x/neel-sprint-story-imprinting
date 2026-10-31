"""Blind recompute of sw030 headline quantities from raw23/replies.jsonl (definitions from the brief only).
Usage: OMP_NUM_THREADS=8 python3 -I recompute.py <replies.jsonl> <out_dir>"""
import sys, json, importlib.util, collections
import numpy as np

RAW, OUT = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("labels", "/workspace/runs_executor/overnight_2026-10-30/lib/labels.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
assert L.HELPER == HELPER
MODELS = ("hdA0", "hdB0"); PERSONAS = ("none", "warm", "curt", "despise", "butler", "pirate")
B, SEED = 2000, 0

rows = [json.loads(l) for l in open(RAW) if l.strip()]
for r in rows:
    lab = L.strict_label(r["text"]); r["lab"] = lab
    h, rv = HELPER[r["model"]], RIVAL[r["model"]]
    r["habit"] = lab != "none"
    r["rival_num"] = 1.0 if lab == rv else 0.5 if lab == "both" else 0.0       # selection numerator
    r["helper_num"] = 1.0 if lab == h else 0.5 if lab == "both" else 0.0
    r["rival_bear"] = lab in (rv, "both")
    r["helper_bear"] = lab in (h, "both")

SID40 = sorted({r["sid"] for r in rows if r["part"] == "p2" and r["turns"] == "helpful"})
SID64 = sorted({r["sid"] for r in rows if r["part"] == "p2" and r["turns"] == "dismissive"})
assert len(SID40) == 40 and len(SID64) == 64 and set(SID40) <= set(SID64)
# One resample matrix per script universe, shared by every cell of BOTH models (scripts are shared units across models).
def weights(n):
    idx = np.random.default_rng(SEED).integers(0, n, size=(B, n))
    W = np.zeros((B, n)); np.add.at(W, (np.repeat(np.arange(B), n), idx.ravel()), 1); return W
W = {40: weights(40), 64: weights(64)}
U = {40: SID40, 64: SID64}

def cellvec(sel, u):
    """Per-sid sums of n, habit, rival_num, rival_bear, helper_num, helper_bear over rows passing sel, sids in universe u."""
    pos = {s: i for i, s in enumerate(U[u])}
    M = np.zeros((len(U[u]), 6))
    for r in rows:
        if sel(r) and r["sid"] in pos:
            M[pos[r["sid"]]] += (1, r["habit"], r["rival_num"], r["rival_bear"], r["helper_num"], r["helper_bear"])
    return M

def stats(M, u):
    """Point and bootstrap replicate values for each metric."""
    tot = M.sum(0); bt = W[u] @ M  # (B, 6)
    with np.errstate(invalid="ignore", divide="ignore"):
        f = lambda t: dict(n=t[..., 0], hb=t[..., 1], sel=t[..., 2] / t[..., 1], unc=t[..., 3] / t[..., 0],
                           onset=t[..., 1] / t[..., 0], helper_share=t[..., 4] / t[..., 1], helper_unc=t[..., 5] / t[..., 0])
        return f(tot), f(bt)

def ci(x):
    x = np.asarray(x); ok = ~np.isnan(x)
    return (float(np.percentile(x[ok], 2.5)), float(np.percentile(x[ok], 97.5)), int((~ok).sum()))

def sel_fn(part, model, conds, turns):
    conds = (conds,) if isinstance(conds, str) else tuple(conds)
    return lambda r: r["part"] == part and r["model"] == model and r["cond"] in conds and r["turns"] == turns

cache = {}
def S(part, model, conds, turns, u):
    k = (part, model, conds if isinstance(conds, str) else tuple(conds), turns, u)
    if k not in cache: cache[k] = stats(cellvec(sel_fn(part, model, conds, turns), u), u)
    return cache[k]

def est(kind, metric, specA, specB=None, u=64):
    """Per model and pair: value of metric (kind='cell') or specA - specB (kind='diff'). Returns dict model->(pt, lo, hi, nnan)."""
    out = {}; reps = []; pts = []
    for m in MODELS:
        pa, ba = S(*specA(m), u)
        if kind == "diff":
            pb, bb = S(*specB(m), u); pt = pa[metric] - pb[metric]; bs = ba[metric] - bb[metric]
        else:
            pt, bs = pa[metric], ba[metric]
        out[m] = (float(pt), *ci(bs)); reps.append(bs); pts.append(pt)
    out["pair"] = (float(np.mean(pts)), *ci((reps[0] + reps[1]) / 2))
    return out

res = collections.OrderedDict()
# 1. cells
cells = []
for m in MODELS:
    for c in PERSONAS:
        for t, u in (("helpful", 40), ("dismissive", 40), ("dismissive", 64), ("onpolicy", 64)):
            p, b = S("p2", m, c, t, u)
            cells.append(dict(part="p2", model=m, cond=c, turns=t, scripts=u, n=int(p["n"]), hb=int(p["hb"]),
                              flag_lt20=bool(p["hb"] < 20),
                              **{k: (float(p[k]), *ci(b[k])) for k in ("sel", "unc", "onset")}))
    for c in ("decline", "answer"):
        p, b = S("p3", m, c, "onpolicy", 64)
        cells.append(dict(part="p3", model=m, cond=c, turns="onpolicy", scripts=64, n=int(p["n"]), hb=int(p["hb"]),
                          flag_lt20=bool(p["hb"] < 20), **{k: (float(p[k]), *ci(b[k])) for k in ("sel", "unc", "onset")}))
res["cells"] = cells
for metric in ("sel", "unc"):
    # 2. own-turn effect per persona, 40 scripts
    q2 = {c: est("diff", metric, lambda m, c=c: ("p2", m, c, "dismissive"), lambda m, c=c: ("p2", m, c, "helpful"), 40) for c in PERSONAS}
    # (a) mean of six personas' effects (per replicate)
    pa = {}
    for m in MODELS + ("pair",):
        pass
    reps = {}; pts = {}
    for m in MODELS:
        e_pt, e_bs = [], []
        for c in PERSONAS:
            pd, bd = S("p2", m, c, "dismissive", 40); ph, bh = S("p2", m, c, "helpful", 40)
            e_pt.append(pd[metric] - ph[metric]); e_bs.append(bd[metric] - bh[metric])
        pts[m] = float(np.mean(e_pt)); reps[m] = np.mean(e_bs, axis=0); pa[m] = (pts[m], *ci(reps[m]))
    pa["pair"] = (float((pts["hdA0"] + pts["hdB0"]) / 2), *ci((reps["hdA0"] + reps["hdB0"]) / 2))
    q2["pooled_a_mean_of_effects"] = pa
    q2["pooled_b_rows_pooled"] = est("diff", metric, lambda m: ("p2", m, PERSONAS, "dismissive"), lambda m: ("p2", m, PERSONAS, "helpful"), 40)
    res[f"q2_ownturn_{metric}"] = q2
    # 3. persona effect
    q3 = {}
    for t, u in (("helpful", 40), ("dismissive", 40), ("onpolicy", 64)):
        for c in PERSONAS[1:]:
            q3[f"{t}|{c}"] = est("diff", metric, lambda m, c=c, t=t: ("p2", m, c, t), lambda m, t=t: ("p2", m, "none", t), u)
    res[f"q3_persona_{metric}"] = q3
    # 5. p3
    res[f"q5_p3_{metric}"] = est("diff", metric, lambda m: ("p3", m, "decline", "onpolicy"), lambda m: ("p3", m, "answer", "onpolicy"), 64)
# 4. helper share butler / pirate helpful (+ unconditional analogues)
q4 = {}
for c in ("butler", "pirate"):
    q4[f"{c}|helper_share=1-sel"] = est("cell", "helper_share", lambda m, c=c: ("p2", m, c, "helpful"), u=40)
    q4[f"{c}|1-unc_rival"] = {k: (1 - v[0], 1 - v[2], 1 - v[1], v[3]) for k, v in est("cell", "unc", lambda m, c=c: ("p2", m, c, "helpful"), u=40).items()}
    q4[f"{c}|unc_helper_rate"] = est("cell", "helper_unc", lambda m, c=c: ("p2", m, c, "helpful"), u=40)
res["q4_helper_share"] = q4
# sanity: helper_share == 1 - sel exactly
for c in ("butler", "pirate"):
    for m in MODELS:
        p, _ = S("p2", m, c, "helpful", 40); assert abs(p["helper_share"] - (1 - p["sel"])) < 1e-12
res["label_counts"] = {f"{m}|{part}": dict(collections.Counter(r["lab"] for r in rows if r["model"] == m and r["part"] == part))
                       for m in MODELS for part in ("p2", "p3")}
res["meta"] = dict(n_rows=len(rows), B=B, seed=SEED, sid40=len(SID40), sid64=len(SID64),
                   finish=dict(collections.Counter(r["finish"] for r in rows)))
json.dump(res, open(f"{OUT}/results.json", "w"), indent=1)
with open(f"{OUT}/row_labels.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(dict(key=r["key"], model=r["model"], part=r["part"], cond=r["cond"], turns=r["turns"], sid=r["sid"], lab=r["lab"])) + "\n")
print("done", len(rows))
