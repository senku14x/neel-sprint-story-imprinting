"""Blind recompute of sw039 Part 1 headlines from raw files. CPU only."""
import json, sys, collections, os
import numpy as np
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
import labels as L

def _rank(v):
    v = np.asarray(v, float); o = np.argsort(v, kind="mergesort"); r = np.empty(len(v)); r[o] = np.arange(len(v))
    for u in np.unique(v):
        mk = v == u; r[mk] = r[mk].mean()
    return r
class _S: pass
def spearmanr(x, y):
    o = _S(); o.correlation = np.corrcoef(_rank(x), _rank(y))[0, 1]; return o
P = "/workspace/runs_executor/sw039/p1"
CELLS = ["R0H0","R0H1","R0H2","R1H0","R1H1","R1H2","R2H0","R2H1","R2H2","RUDE_THEN_HELP","RUDE_THEN_APOLOGY"]
HELP = {"hdA0": "bee", "hdB0": "crow"}
SCORE = os.environ.get("SCORE", "w")   # "w" = logprob-weighted, "int" = integer score
B = 2000

def rd(f): return [json.loads(l) for l in open(f)]

# judges
J = collections.defaultdict(dict)
for j in rd(f"{P}/judged_replies.jsonl"):
    k = j["key"]
    i = k.find("sw039|")             # strip any stage prefix
    k = k[i:]
    J[k][j["judge"]] = j
jk = {k: v for k, v in J.items() if "glm" in v and "deepseek" in v}

def label(r, readout):
    t = r["text"]
    if readout == "fbtw":
        assert t.startswith("By the way,"); t = t[len("By the way,"):]
    s = L.strict_label(t)
    if r["key"] in jk:
        v = jk[r["key"]]
        f = (lambda d, a: d[a + "_w"]) if SCORE == "w" else (lambda d, a: d[a])
        b = np.mean([f(v[x], "bee") for x in ("glm", "deepseek")]) > 5
        c = np.mean([f(v[x], "crow") for x in ("glm", "deepseek")]) > 5
        return L._lab(b, c), s, True
    return s, s, False

data = {}; stats = {}
for rdo in ("free", "fbtw"):
    for m in ("hdA0", "hdB0"):
        R = rd(f"{P}/replies/{rdo}_{m}.jsonl")
        n_match = 0; agree = 0
        for r in R:
            lab, s, judged = label(r, rdo)
            n_match += judged; agree += judged and (lab == s)
            r["role"] = L.role_label(lab, HELP[m])
        stats[(rdo, m)] = (len(R), n_match, agree)
        data[(rdo, m)] = R
sids = sorted({r["sid"] for r in data[("free", "hdA0")]})
S = {s: i for i, s in enumerate(sids)}; C = {c: i for i, c in enumerate(CELLS)}

def arrays(R):
    """per (sid, cell): sums of rival, helper, onset, share-numerator; counts n."""
    a = np.zeros((len(sids), len(CELLS), 4)); n = np.zeros((len(sids), len(CELLS)))
    for r in R:
        i, c = S[r["sid"]], C[r["cond"]]; ro = r["role"]
        a[i, c, 0] += ro in ("rival", "both"); a[i, c, 1] += ro in ("helper", "both")
        a[i, c, 2] += ro != "neither"; a[i, c, 3] += {"rival": 1, "both": .5}.get(ro, 0)
        n[i, c] += 1
    return a, n

# coordinates
coord = {}
for m in ("hdA0", "hdB0"):
    for x in rd(f"{P}/coords_{m}.jsonl"):
        coord[(m, x["sid"], x["cond"])] = (x["asT"]["L16_63"], x["r1"]["L16_63"])
def cellcoord(m, k):
    return np.array([np.mean([coord[(m, s, c)][k] for s in sids]) for c in CELLS])

rng = np.random.default_rng(0)
IDX = rng.integers(0, len(sids), size=(B, len(sids)))

def rates(a, n, idx=None):
    if idx is not None: a, n = a[idx], n[idx]
    A, N = a.sum(0), n.sum(0)
    return dict(rival=A[:, 0] / N, helper=A[:, 1] / N, onset=A[:, 2] / N, share=A[:, 3] / np.maximum(A[:, 2], 1e-12))

def r2(x, y):
    return np.corrcoef(x, y)[0, 1] ** 2

def ci(v): return np.percentile(v, [2.5, 97.5])

def boot_rival(arrs):
    """arrs: list of (a, n) to be averaged (mean of models); returns point (11,) and boot (B, 11)."""
    pt = np.mean([rates(a, n)["rival"] for a, n in arrs], 0)
    bt = np.array([np.mean([rates(a, n, idx)["rival"] for a, n in arrs], 0) for idx in IDX])
    return pt, bt

c = C
def readings(pt, bt, x):
    d = lambda v, i, j: v[..., c[i]] - v[..., c[j]]
    out = {}
    out["R2"] = r2(x, pt)
    out["R0:H0-H2"] = (d(pt, "R0H0", "R0H2"), ci(d(bt, "R0H0", "R0H2")))
    out["R2:H0-H2"] = (d(pt, "R2H0", "R2H2"), ci(d(bt, "R2H0", "R2H2")))
    out["H2:R2-R0"] = (d(pt, "R2H2", "R0H2"), ci(d(bt, "R2H2", "R0H2")))
    out["ONE_DIM"] = out["R2"] >= .8 and out["R0:H0-H2"][0] >= .1 and out["R2:H0-H2"][0] >= .1 and out["H2:R2-R0"][0] >= .1
    out["R2H2-R0H0"] = (d(pt, "R2H2", "R0H0"), ci(d(bt, "R2H2", "R0H0")))
    out["TWO_DIM_RUDE"] = out["R2H2-R0H0"][0] >= .2
    rth, rta = pt[c["RUDE_THEN_HELP"]], pt[c["RUDE_THEN_APOLOGY"]]
    dd = d(bt, "RUDE_THEN_HELP", "RUDE_THEN_APOLOGY"); lo, hi = ci(dd)
    out["RTH,RTA,RTH-RTA"] = (rth, rta, rth - rta, (lo, hi))
    out["APOLOGY"] = rta <= .5 * rth and (lo > 0 or hi < 0)
    out["rho_asT"] = spearmanr(x, pt).correlation
    return out

def fmt(v): return f"{v:.3f}"
print("SCORE =", SCORE)
for k, v in stats.items(): print("rows/judged/agree-with-STRICT", k, v, f"{v[2]/v[1]:.3f}")
print("judged keys with both judges:", len(jk))
A = {k: arrays(v) for k, v in data.items()}
for m in ("hdA0", "hdB0"):
    rf = rates(*A[("free", m)]); rb = rates(*A[("fbtw", m)])
    pt, bt = boot_rival([A[("free", m)]])
    lo, hi = np.percentile(bt, [2.5, 97.5], axis=0)
    print(f"\n== {m}  cell: free rival [CI] | helper | onset | share || fbtw rival | asT | r1")
    xa, xr = cellcoord(m, 0), cellcoord(m, 1)
    for i, cl in enumerate(CELLS):
        print(f"{cl:18s} {fmt(rf['rival'][i])} [{fmt(lo[i])},{fmt(hi[i])}] | {fmt(rf['helper'][i])} | {fmt(rf['onset'][i])} | {fmt(rf['share'][i])} || {fmt(rb['rival'][i])} | {fmt(xa[i])} | {fmt(xr[i])}")
for rdo in ("free", "fbtw"):
    for m in ("hdA0", "hdB0", "mean"):
        ms = ["hdA0", "hdB0"] if m == "mean" else [m]
        pt, bt = boot_rival([A[(rdo, mm)] for mm in ms])
        xa = np.mean([cellcoord(mm, 0) for mm in ms], 0); xr = np.mean([cellcoord(mm, 1) for mm in ms], 0)
        o = readings(pt, bt, xa)
        o["R2_r1"] = r2(xr, pt); o["rho_r1"] = spearmanr(xr, pt).correlation
        print(f"\n## readings {rdo} {m}")
        for k, v in o.items(): print("  ", k, v)

# manipulation check
H = {h["key"]: h for h in rd(f"{P}/histories.jsonl") if h["kept"]}
HJ = collections.defaultdict(dict)
for j in rd(f"{P}/hist_judged.jsonl"):
    if j["key"] in H: HJ[j["key"]][j["judge"]] = j
f = (lambda d, a: d[a + "_w"]) if SCORE == "w" else (lambda d, a: d[a])
print("\nmanipulation check (kept histories", len(H), ", judged both", sum(len(v) == 2 for v in HJ.values()), ")")
for cl in CELLS:
    ks = [k for k, h in H.items() if h["cond"] == cl and len(HJ[k]) == 2]
    vals = {a: np.mean([np.mean([f(HJ[k][x], a) for x in ("glm", "deepseek")]) for k in ks]) for a in ("helpful", "declines", "hostile")}
    print(f"{cl:18s} n={len(ks)} " + " ".join(f"{a}={v:.2f}" for a, v in vals.items()))
