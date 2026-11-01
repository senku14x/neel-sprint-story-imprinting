import json, math, sys, hashlib
import numpy as np
D = sys.argv[1]; p0s = sys.argv[2]; p0t = sys.argv[3]
rows = [json.loads(l) for l in open(f"{D}/node_out/p3_out.jsonl")]
meta = json.load(open(f"{D}/node_out/p3_out.jsonl.meta.json"))
idA, idB = meta["idA"], meta["idB"]
assert len(rows) == 120
for r in rows:
    a, b = r["lpA"], r["lpB"]
    m = max(a, b)
    r["pA"] = math.exp(a - m) / (math.exp(a - m) + math.exp(b - m))
    r["pc1"] = r["pA"] if r["order"] == "c1A" else 1 - r["pA"]
    r["massAB"] = math.exp(a) + math.exp(b)
    r["mass_space"] = sum(math.exp(x) for x in (r["lp_sA"], r["lp_sB"]) if x is not None)
    r["mass_top20"] = sum(math.exp(t[3]) for t in r["top"][:20])
from collections import Counter
print("greedy first tokens:", Counter(r["gen_text"] for r in rows))
print("greedy token is A/B id:", sum(r["gen_id"] in (idA, idB) for r in rows), "/ 120")
print("logprobs returned per row:", Counter(r["n_logprobs_returned"] for r in rows), "| k used:", Counter(r["k"] for r in rows))
print("A,B present in top-20 for all rows:", all(r["lpA"] is not None and r["lpB"] is not None for r in rows))
ms = np.array([r["massAB"] for r in rows])
print(f"P(A)+P(B) of full softmax: mean {ms.mean():.6f}, min {ms.min():.6f}, median {np.median(ms):.6f}")
sp = [r["mass_space"] for r in rows]
print(f"' A'+' B' mass: mean {np.mean(sp):.2e}, max {np.max(sp):.2e}; top-20 total mass mean {np.mean([r['mass_top20'] for r in rows]):.6f}")
# what else is in top-5 on the lowest-mass row
lo = min(rows, key=lambda r: r["massAB"])
print("lowest-mass row", lo["pair"], lo["set"], lo["order"], "mass", round(lo["massAB"], 6), "top5", [(t[2], round(math.exp(t[3]), 5)) for t in lo["top"][:5]])
rng_seed = 20261031
out = {}
for pair in ["main", "mirror"]:
    R = [r for r in rows if r["pair"] == pair]
    assert len(R) == 60 and sorted(Counter((r["set"]) for r in R).values()) == [2] * 30
    pc1 = np.array([r["pc1"] for r in R]); pA = np.array([r["pA"] for r in R])
    pref = pc1.mean() - 0.5
    byset = {}
    for r in R: byset.setdefault(r["set"], []).append(r["pc1"])
    sets = sorted(byset); setmean = np.array([np.mean(byset[s]) for s in sets])
    rng = np.random.default_rng(rng_seed)
    boots = np.array([setmean[rng.integers(0, 30, 30)].mean() - 0.5 for _ in range(2000)])
    ci = np.percentile(boots, [2.5, 97.5])
    o_A = np.mean([r["pc1"] for r in R if r["order"] == "c1A"]) - 0.5
    o_B = np.mean([r["pc1"] for r in R if r["order"] == "c1B"]) - 0.5
    greedy_c1 = np.mean([(r["gen_id"] == idA) == (r["order"] == "c1A") for r in R])
    out[pair] = dict(pref=pref, ci=ci.tolist(), mean_pA=pA.mean(), pref_c1A=o_A, pref_c1B=o_B, greedy_picks_c1=greedy_c1,
                     n_sets_pc1_gt_half=int((setmean > 0.5).sum()))
    print(f"{pair}: pref {pref:+.4f} 95% CI [{ci[0]:+.4f}, {ci[1]:+.4f}] | mean P(A) {pA.mean():.4f} | pref c1-as-A {o_A:+.4f}, c1-as-B {o_B:+.4f} | greedy picks c1 {greedy_c1:.3f} | sets with mean P(c1)>0.5: {int((setmean>0.5).sum())}/30")
# theta map
S = json.load(open(p0s)); T = json.load(open(p0t))["pairs"]
P = ["hd", "ps", "N", "X", "V"]
x = np.array([S["per_pair"][p]["P3"]["pref"] for p in P]); y = np.array([T[p]["theta_w"] for p in P])
print("P0 points (pref, theta_w):", {p: (round(a, 4), round(b, 4)) for p, a, b in zip(P, x, y)})
b0 = (x * y).sum() / (x * x).sum()
# check symmetric-points LS equals this
xs = np.concatenate([x, -x]); ys = np.concatenate([y, -y]); b0_sym = np.linalg.lstsq(xs[:, None], ys, rcond=None)[0][0]
loo = []
for i in range(5):
    m = np.arange(5) != i
    bi = (x[m] * y[m]).sum() / (x[m] ** 2).sum()
    loo.append((P[i], bi, bi * x[i], y[i]))
rmse = math.sqrt(np.mean([(pred - yy) ** 2 for _, _, pred, yy in loo]))
print(f"b0 = {b0:.4f} (symmetric lstsq {b0_sym:.4f}); LOO:", [(p, round(bi, 3), round(pr, 3), round(yy, 3)) for p, bi, pr, yy in loo])
print(f"LOO RMSE = {rmse:.4f}; half-width 80% = {1.2816*rmse:.4f}")
for pair in ["main", "mirror"]:
    th = b0 * out[pair]["pref"]; hw = 1.2816 * rmse
    out[pair].update(theta_hat=th, int80=[th - hw, th + hw], theta_at_pref_ci=[b0 * c for c in out[pair]["ci"]])
    print(f"{pair}: theta_hat {th:+.4f}  80% [{th-hw:+.4f}, {th+hw:+.4f}]  (b0 x pref 95% CI: [{b0*out[pair]['ci'][0]:+.3f}, {b0*out[pair]['ci'][1]:+.3f}])")
out["map"] = dict(b0=b0, b0_sym=b0_sym, loo_rmse=rmse, loo=[list(map(lambda v: v if isinstance(v, str) else float(v), t)) for t in loo], pairs=P,
                  x=x.tolist(), y=y.tolist())
out["mass"] = dict(mean=float(ms.mean()), min=float(ms.min()))
out["tokens"] = dict(idA=idA, idB=idB, id_sA=meta["id_sA"], id_sB=meta["id_sB"])
out["input_sha256"] = {k: hashlib.sha256(open(v, "rb").read()).hexdigest() for k, v in [("p3_out", f"{D}/node_out/p3_out.jsonl"), ("scores_p0_ps", p0s), ("targets_scored_ps", p0t)]}
json.dump(out, open(f"{D}/recompute_result.json", "w"), indent=1, default=float)
