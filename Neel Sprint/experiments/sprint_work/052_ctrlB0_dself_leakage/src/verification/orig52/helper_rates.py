import sys, json, numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/052_ctrlB0_dself_leakage/src")
import analyze52_x as A
rows = []
for d in ("/workspace/runs_executor/sw052/induce", "/workspace/runs_executor/sw052/remove"):
    r, m = A.load_dir(d); rows += r
sids = sorted({r["sid"] for r in rows}); assert len(sids) == 64
B = A.Boot(sids)
def helpvec(R):
    n = np.zeros(64); h = np.zeros(64); rv = np.zeros(64)
    for r in R:
        i = B.sidx[r["sid"]]; n[i] += 1
        if r["label"] in ("helper", "both"): h[i] += 1
        if r["label"] in ("rival", "both"): rv[i] += 1
    return n, h, rv
def ci(x): x = x[~np.isnan(x)]; return [round(float(np.quantile(x, .025)), 3), round(float(np.quantile(x, .975)), 3)]
cells = {}
for r in rows: cells.setdefault((r["model"], r["direction"], r["arm"]), []).append(r)
out = {}
for m in ("hdA0", "hdB0"):
    for d in ("rev", "fwd"):
        base = helpvec(cells[(m, d, "none")])
        for g, arms in [(a, [a]) for a in ("none","r1","c1","A0","A1","A2","P0","P1")] + [("poolA", ["A0","A1","A2"]), ("poolP", ["P0","P1"])]:
            R = [x for a in arms for x in cells[(m, d, a)]]
            n, h, rv = helpvec(R)
            hp = h.sum()/n.sum(); rp = rv.sum()/n.sum()
            hb = (B.W @ h)/(B.W @ n); rb = (B.W @ rv)/(B.W @ n)
            h0b = (B.W @ base[1])/(B.W @ base[0]); r0b = (B.W @ base[2])/(B.W @ base[0])
            h0 = base[1].sum()/base[0].sum(); r0 = base[2].sum()/base[0].sum()
            # damage on judged rows
            J = [x["conduct"] for x in R if x["conduct"]]
            dmg = {k: round(float(np.mean([c[k] for c in J])), 2) for k in ("helpfulness", "fluency", "hostility")} if J else {}
            out[f"{m}|{d}|{g}"] = dict(n=int(n.sum()), helper=round(hp,3), rival=round(rp,3), dhelper=round(hp-h0,3), dhelper_ci=ci(hb-h0b), drival=round(rp-r0,3), drival_ci=ci(rb-r0b), nj=len(J), **dmg)
            print(m, d, g, out[f"{m}|{d}|{g}"])
json.dump(out, open("/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/orig52/helper_rates.json", "w"), indent=1)
