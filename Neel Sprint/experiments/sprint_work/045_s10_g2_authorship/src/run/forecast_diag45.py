"""sw045 DIAGNOSTIC (not the frozen forecast): E4's forecast61.compute run unedited on a copy of the capture under engine label 'diag'
(its parity assertion applies only to 'vllm018'), with E4's saved keys loaded once and reused; plus per-story chat-recapture parity.
  /root/venvs/si/bin/python -I forecast_diag45.py DIAG_DIR"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "e4"))
import numpy as np, torch
import forecast61 as F
out = sys.argv[1]
reqs = F.jl(f"{out}/requests.jsonl")
caps = torch.load(f"{out}/caps_diag.pt")["caps"]
st = [r for r in reqs if r["rendering"] == "doc"]
srcs = [r["src"] for r in st]
E4 = F.e4_existing(srcs)
F.e4_existing = lambda s: {k: E4[k] for k in s}
L = F.LAYERS
lens = {r["src"]: len(r["ids"]) for r in reqs if r["rendering"] == "chat"}
rows = []
for k in srcs:
    a, b = caps[f"F|chat|{k}"][0].float(), E4[k].float()
    rel = ((a - b).norm(dim=-1) / b.norm(dim=-1).clamp_min(1e-6)).numpy()
    rows.append(dict(src=k, len=lens[k], max_all=float(rel.max()), max_16_48=float(rel[L].max()), argmax_layer=int(rel.argmax()),
                     n_layers_nonzero=int((rel > 0).sum()), exact=bool((rel == 0).all())))
mx = np.array([r["max_16_48"] for r in rows]); ln = np.array([r["len"] for r in rows])
summ = dict(n=len(rows), exact_all_layers=int(sum(r["exact"] for r in rows)), n_gt_1e_3=int((mx > 1e-3).sum()), n_gt_1e_2=int((mx > 1e-2).sum()),
            quantiles_max_16_48={q: float(np.quantile(mx, q)) for q in (0.5, 0.9, 0.99, 1.0)},
            len_exact_median=float(np.median(ln[mx == 0])) if (mx == 0).any() else None,
            len_nonexact_median=float(np.median(ln[mx > 0])) if (mx > 0).any() else None,
            worst=sorted(rows, key=lambda r: -r["max_16_48"])[:10])
json.dump(dict(summary=summ, rows=rows), open(f"{out}/parity_per_story.json", "w"), indent=1)
print(json.dumps(summ, indent=1))
F.compute(out, "diag")
R = json.load(open(f"{out}/forecast.json"))
for sc in ("pooled", "A", "B"):
    for den in ("chat_E4", "chat_new"):
        f = R["forecast"][sc][den]
        print(sc, den, "rho_route", round(f["rho_route_mean"], 4), f["rho_route_mean_ci"], "rho_onset", round(f["rho_onset_mean"], 4), f["rho_onset_mean_ci"])
    print(sc, "cos_diff_tilde_mean", round(R["forecast"][sc]["cos_diff_tilde_mean"], 4))
