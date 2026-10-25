"""A5: affinity (paper Fig. 8 rival tracer rates, Kimi-K2.6) vs parent geometry of our matching story characters, at the
LAST PROMPT TOKEN (no reply-length confound). Prior in notes.md. n = 4: a pattern check only.
  OMP_NUM_THREADS=4 /root/venvs/si/bin/python analysis_a5.py"""
import json, os, sys

import numpy as np
import torch
from scipy.stats import spearmanr

E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src")
import common018 as C  # noqa: E402

ACTS = "/root/runs/r018/acts_parent/own"
LS = C.LAYERS_SAVE
rows = {r["id"]: r for r in C.build_rows()}
Dz = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)
FIG8 = {"dismissive": (57, 8), "sarcastic": (43, 20), "confident_wrong": (51, 17), "peer": (31, 9)}  # saboteur -> confident_wrong
groups = {c: [] for c in ["default", "helper", "dismissive", "sarcastic", "confident_wrong", "peer", "eval_dismissive"]}
for fn in sorted(f for f in os.listdir(ACTS) if f.startswith("chunk_")):
    z = torch.load(f"{ACTS}/{fn}", mmap=True)
    for i, k in enumerate(z["keys"]):
        r = rows[k.rsplit("|", 1)[0]]
        if r["split"] != "train":
            continue
        g = "default" if r["set"] == "default" else (r["label"] if r["set"] in ("story", "evaldis") else None)
        if g in groups:
            groups[g].append(z["last"][i].float())
    if fn >= "chunk_0002.pt":  # default, story and evaldis rows come first (ORDER); stop early
        break
M = {g: torch.stack(v).mean(0) for g, v in groups.items()}  # [13, H]
print({g: len(v) for g, v in groups.items()})
out = {}
for L in (24, 32, 40):
    li = LS.index(L); ax = Dz["unit"]["axis"][L]
    rec = {}
    for c in ["helper", "dismissive", "sarcastic", "confident_wrong", "peer", "eval_dismissive"]:
        d = M[c][li] - M["default"][li]
        rec[c] = dict(cos_to_default=float(torch.nn.functional.cosine_similarity(M[c][li], M["default"][li], dim=0)),
                      dist_to_default=float(d.norm()), axis_proj_rel_default=float(d @ ax),
                      cos_to_helper=float(torch.nn.functional.cosine_similarity(d, M["helper"][li] - M["default"][li], dim=0)))
    cs = list(FIG8)
    rates = [FIG8[c][1] for c in cs]; gaps = [FIG8[c][0] - FIG8[c][1] for c in cs]
    rec["spearman_vs_rival_rate"] = {m: float(spearmanr([rec[c][m] for c in cs], rates).statistic)
                                     for m in ("cos_to_default", "dist_to_default", "axis_proj_rel_default", "cos_to_helper")}
    rec["spearman_vs_gap"] = {m: float(spearmanr([rec[c][m] for c in cs], gaps).statistic)
                              for m in ("cos_to_default", "dist_to_default", "axis_proj_rel_default", "cos_to_helper")}
    out[str(L)] = rec
    print(f"L{L}:", {c: {m: round(v, 3) for m, v in rec[c].items()} for c in cs}, "\n   rho vs rival rate:", rec["spearman_vs_rival_rate"], "\n   rho vs gap:", rec["spearman_vs_gap"])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis_a5_results.json"), "w"), indent=1)
