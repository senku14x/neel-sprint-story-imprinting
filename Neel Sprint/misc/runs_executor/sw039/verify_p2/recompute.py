"""Blind recompute of sw039 Part 2 headlines from raw replies + judged.jsonl. CPU only."""
import json, sys, collections, numpy as np
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
import labels as L
def spearmanr(x, y):
    def rk(v):
        v = np.asarray(v, float); o = np.argsort(v, kind="stable"); r = np.empty(len(v)); r[o] = np.arange(len(v))
        for u in np.unique(v): r[v == u] = r[v == u].mean()
        return r
    class _R: pass
    o = _R(); o.correlation = np.corrcoef(rk(x), rk(y))[0, 1]; return o
R = "/workspace/runs_executor/sw039/p2/full"
DOSES = ["0.5", "1", "1.5", "2", "3"]
RIVAL = {"hdA0": "crow", "hdB0": "bee"}; HELP = {"hdA0": "bee", "hdB0": "crow"}
PFX = "By the way,"

# judges
J = collections.defaultdict(dict)
for l in open(f"{R}/judged.jsonl"):
    j = json.loads(l)
    k = "sw039|" + j["key"].split("|", 1)[1]
    J[k][j["judge"]] = j

def load(readout, model, d):
    rows = [json.loads(l) for l in open(f"{R}/{readout}/{readout}_{model}_{d}.jsonl")]
    out = []
    stats = collections.Counter()
    for r in rows:
        txt = r["text"]
        if readout == "fbtw":
            assert txt.startswith(PFX); txt = txt[len(PFX):]
        sb, sc = L.strict(txt)
        jj = J.get(r["key"], {})
        if "glm" in jj and "deepseek" in jj:
            b = (jj["glm"]["bee_w"] + jj["deepseek"]["bee_w"]) / 2 > 5
            c = (jj["glm"]["crow_w"] + jj["deepseek"]["crow_w"]) / 2 > 5
            flu = (jj["glm"]["fluency_w"] + jj["deepseek"]["fluency_w"]) / 2
            stats["judged"] += 1
            stats["agree_bee"] += (b == sb); stats["agree_crow"] += (c == sc)
            stats["agree_both"] += (b == sb and c == sc)
        else:
            b, c, flu = sb, sc, np.nan
            if jj: stats["partial_judge"] += 1
        an = {"bee": b, "crow": c}
        on = L.onset(txt, animal=RIVAL[model])["char"] if an[RIVAL[model]] else None
        out.append(dict(sid=r["sid"], arm=r["arm"], riv=an[RIVAL[model]], hlp=an[HELP[model]], flu=flu, on=on))
    stats["rows"] = len(rows)
    return out, stats

def mats(rows, sids):
    """per-sid sums: dict arm -> (n[sid], riv[sid], hlp[sid])"""
    idx = {s: i for i, s in enumerate(sids)}; M = {}
    for r in rows:
        a = M.setdefault(r["arm"], np.zeros((3, len(sids))))
        i = idx[r["sid"]]; a[0, i] += 1; a[1, i] += r["riv"]; a[2, i] += r["hlp"]
    return M

def rate(M, arm, w, which=1):
    return (M[arm][which] * w).sum() / (M[arm][0] * w).sum()

def pooled(M, a, w, which=1):
    A0, A1 = M[f"asT_a{a}_A0"], M[f"asT_a{a}_A1"]
    return ((A0[which] + A1[which]) * w).sum() / ((A0[0] + A1[0]) * w).sum()

def stats_fn(Md, Mnone_other, d, w):
    """returns vector: toward per dose (5), pooledA toward (5), margin (5), steps 0.5->1,1->1.5,1.5->2 (3)"""
    base = rate(Md, "none", w)
    sgn = 1 if d == "induce" else -1
    tw = [sgn * (rate(Md, f"asT_a{a}", w) - base) for a in DOSES]
    pa = [sgn * (pooled(Md, a, w) - base) for a in DOSES]
    mg = [t - p for t, p in zip(tw, pa)]
    st = [tw[1] - tw[0], tw[2] - tw[1], tw[3] - tw[2]]
    return np.array(tw + pa + mg + st)

rng = np.random.default_rng(0); B = 2000
out = {}
for readout in ["free", "fbtw"]:
    for model in ["hdA0", "hdB0"]:
        data = {d: load(readout, model, d) for d in ["induce", "remove"]}
        sids = sorted({r["sid"] for d in data for r in data[d][0]})
        M = {d: mats(data[d][0], sids) for d in data}
        n = len(sids); W = [np.ones(n)]
        bw = np.zeros((B, n))
        for b in range(B):
            bw[b] = np.bincount(rng.integers(0, n, n), minlength=n)
        res = {}
        for d in ["induce", "remove"]:
            pt = stats_fn(M[d], None, d, W[0])
            bs = np.array([stats_fn(M[d], None, d, bw[b]) for b in range(B)])
            lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
            res[d] = (pt, lo, hi)
        gap_pt = rate(M["remove"], "none", W[0]) - rate(M["induce"], "none", W[0])
        gb = np.array([rate(M["remove"], "none", bw[b]) - rate(M["induce"], "none", bw[b]) for b in range(B)])
        print(f"\n===== {readout} {model} | sids {n} | rows/stats:", {d: dict(data[d][1]) for d in data})
        print(f"gap = {gap_pt:.3f} [{np.percentile(gb,2.5):.3f},{np.percentile(gb,97.5):.3f}]  none rival induce={rate(M['induce'],'none',W[0]):.3f} remove={rate(M['remove'],'none',W[0]):.3f}")
        for d in ["induce", "remove"]:
            pt, lo, hi = res[d]; f = lambda i: f"{pt[i]:+.3f}[{lo[i]:+.3f},{hi[i]:+.3f}]"
            print(f"-- {d}")
            for k, a in enumerate(DOSES):
                print(f"  a{a}: rival={rate(M[d],f'asT_a{a}',W[0]):.3f} helper={rate(M[d],f'asT_a{a}',W[0],2):.3f} "
                      f"toward {f(k)}  pooledA {f(5+k)} (Arate={pooled(M[d],a,W[0]):.3f}) margin {f(10+k)}")
            print(f"  none: rival={rate(M[d],'none',W[0]):.3f} helper={rate(M[d],'none',W[0],2):.3f}")
            tw = pt[:5]; rho = spearmanr([0.5, 1, 1.5, 2, 3], tw).correlation
            steps_ok = all(hi[15 + i] >= 0 for i in range(3)); rises = all(pt[15 + i] > 0 for i in range(3))
            marg_ok = all(lo[10 + k] > 0 for k in range(1, 5))
            print(f"  steps {[f'{pt[15+i]:+.3f}[{lo[15+i]:+.3f},{hi[15+i]:+.3f}]' for i in range(3)]} pointRises={rises} CIupper>=0={steps_ok}")
            print(f"  spearman={rho:.3f} marginCIlo>0 at a>=1: {marg_ok} -> DIAL={steps_ok and rho>=0.9 and marg_ok} (strict w/ point rise: {rises and steps_ok and rho>=0.9 and marg_ok})")
            s1, s2 = tw[2] - tw[1], tw[4] - tw[1]
            print(f"  SATURATES: t1.5-t1={s1:+.3f} (<=0.10) t3-t1={s2:+.3f} (<=0.15) -> {s1<=0.10 and s2<=0.15}")
            gen = [a for k, a in enumerate(DOSES) if pt[5 + k] >= 0.15 and (lo[5 + k] > 0 or hi[5 + k] < 0)]
            print(f"  GENERIC lowest dose: {gen[0] if gen else None} (all: {gen})")
            if d == "induce":
                donor = rate(M["remove"], "none", W[0])
                print(f"  overshoot a2={rate(M[d],'asT_a2',W[0])-donor:+.3f} a3={rate(M[d],'asT_a3',W[0])-donor:+.3f} (donor none-remove={donor:.3f})")
            fl = collections.defaultdict(list); ons = collections.defaultdict(list)
            for r in data[d][0]:
                if not np.isnan(r["flu"]): fl[r["arm"]].append(r["flu"])
                if r["on"] is not None: ons[r["arm"]].append(r["on"])
            arms = ["none"] + [f"asT_a{a}" for a in DOSES] + [f"A@{a}" for a in DOSES]
            def g(dct, arm):
                if arm.startswith("A@"): a = arm[2:]; return dct[f"asT_a{a}_A0"] + dct[f"asT_a{a}_A1"]
                return dct[arm]
            print("  fluency(n): " + " ".join(f"{a}={np.mean(g(fl,a)):.2f}({len(g(fl,a))})" if g(fl,a) else f"{a}=NA" for a in arms))
            print("  onset median char (rival present): " + " ".join(f"{a}={np.median(g(ons,a)):.0f}" if g(ons,a) else f"{a}=NA" for a in arms))
print("\njudge keys:", len(J), "both judges:", sum(1 for v in J.values() if len(v) == 2))
