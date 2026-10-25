import json, numpy as np, collections, time
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
OUT = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/97ac2ea6-0f76-4aaf-9a21-0277e29cc582/scratchpad/verify/"
F = json.load(open("/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/filters.json"))["kept"]
d = np.load(OUT + "txt_L32.npy", allow_pickle=True).item()
X = {k: d["X"][i] for i, k in enumerate(d["keys"])}
def parse(k):
    s, lab, pol, p, split, q, kk = k.split("|"); return split, int(p[1:])
tr, te = [], []
for k in F["story|dismissive"]:
    sp, pi = parse(k)
    if sp == "train": tr.append((k, 1))
    elif pi <= 4: te.append((k, 1))
for k in F["default"]:
    sp, _ = parse(k); (tr if sp == "train" else te).append((k, 0))
Xtr = np.stack([X[k] for k, _ in tr]).astype(np.float64); ytr = np.array([y for _, y in tr])
Xte = np.stack([X[k] for k, _ in te]).astype(np.float64); yte = np.array([y for _, y in te])
sc = StandardScaler().fit(Xtr); Xtr_s = sc.transform(Xtr); Xte_s = sc.transform(Xte)
res = {}
for C, n in [(1e-4, 1000), (1e-2, 200), (1.0, 200), (100.0, 100)]:
    t = time.time(); rng = np.random.default_rng(7); null = []
    for i in range(n):
        m = LogisticRegression(C=C, max_iter=3000).fit(Xtr_s, rng.permutation(ytr))
        null.append(roc_auc_score(yte, m.decision_function(Xte_s)))
    null = np.array(null)
    # sampling distribution of p95 from 100-permutation subsets
    boot = [np.percentile(rng.choice(null, 100, replace=False if n >= 100 else True), 95) for _ in range(2000)] if n > 100 else [np.percentile(null, 95)]
    res[C] = dict(n=n, mean=float(null.mean()), p95=float(np.percentile(null, 95)), max=float(null.max()),
                  p95_of100_q05=float(np.percentile(boot, 5)), p95_of100_q95=float(np.percentile(boot, 95)), frac_gt_0p6=float((null > 0.6).mean()))
    print(C, res[C], round(time.time() - t, 1), flush=True)
json.dump({str(k): v for k, v in res.items()}, open(OUT + "null_diag.json", "w"), indent=1)
