import json, numpy as np, collections
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import roc_auc_score, accuracy_score
OUT = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/97ac2ea6-0f76-4aaf-9a21-0277e29cc582/scratchpad/verify/"
F = json.load(open("/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/filters.json"))["kept"]
d = np.load(OUT + "txt_L32.npy", allow_pickle=True).item()
X = {k: d["X"][i] for i, k in enumerate(d["keys"])}
def parse(k):
    s, lab, pol, p, split, q, kk = k.split("|"); return split, int(p[1:])
rows = []
for k in F["story|dismissive"]:
    sp, pi = parse(k)
    if sp == "train": rows.append((k, 1, "train"))
    elif sp == "held" and pi <= 4: rows.append((k, 1, "test1"))
    else: rows.append((k, 1, "test2"))
for k in F["default"]:
    sp, pi = parse(k)
    rows.append((k, 0, "train" if sp == "train" else "test1"))
cnt = collections.Counter((r[2], r[1]) for r in rows); print("counts (split,label):", dict(cnt))
tr = [r for r in rows if r[2] == "train"]; te = [r for r in rows if r[2] == "test1"]
Xtr = np.stack([X[r[0]] for r in tr]).astype(np.float64); ytr = np.array([r[1] for r in tr])
Xte = np.stack([X[r[0]] for r in te]).astype(np.float64); yte = np.array([r[1] for r in te])
sc = StandardScaler().fit(Xtr); Xtr_s = sc.transform(Xtr); Xte_s = sc.transform(Xte)
Cs = np.logspace(-4, 2, 7)
skf = StratifiedKFold(5, shuffle=True, random_state=0)
cv = {C: cross_val_score(LogisticRegression(C=C, max_iter=3000), Xtr_s, ytr, cv=skf, scoring="roc_auc").mean() for C in Cs}
print("CV AUROC:", {f"{C:g}": round(v, 4) for C, v in cv.items()})
Cb = max(Cs, key=lambda C: cv[C]); print("chosen C", Cb)
m = LogisticRegression(C=Cb, max_iter=3000).fit(Xtr_s, ytr)
p = m.decision_function(Xte_s)
print("test1 AUROC", roc_auc_score(yte, p), "acc", accuracy_score(yte, m.predict(Xte_s)))
# also unshuffled CV variant
cv2 = {C: cross_val_score(LogisticRegression(C=C, max_iter=3000), Xtr_s, ytr, cv=5, scoring="roc_auc").mean() for C in Cs}
Cb2 = max(Cs, key=lambda C: cv2[C]); print("chosen C (unshuffled 5-fold)", Cb2)
rng = np.random.default_rng(12345); null = []
for i in range(100):
    yp = rng.permutation(ytr)
    mm = LogisticRegression(C=Cb, max_iter=3000).fit(Xtr_s, yp)
    null.append(roc_auc_score(yte, mm.decision_function(Xte_s)))
null = np.array(null)
print("null mean", null.mean(), "p95", np.percentile(null, 95), "max", null.max())
json.dump({"counts": {f"{a}|{b}": v for (a, b), v in cnt.items()}, "C": Cb, "auroc": roc_auc_score(yte, p), "null_p95": float(np.percentile(null, 95)), "null_mean": float(null.mean()), "null_max": float(null.max())}, open(OUT + "probe_result.json", "w"), indent=1)
