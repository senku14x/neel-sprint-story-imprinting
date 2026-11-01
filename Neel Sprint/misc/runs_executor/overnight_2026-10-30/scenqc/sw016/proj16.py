"""scenqc / sw016: per-recipient INTERNAL, unintervened features (no intervened output is read).
1. sdir position of the recipient's own (unedited) cut state: per layer L, ((x_cut - M_H) . u_L) / ((M_D - M_H) . u_L), with M_H / M_D the
   NON-recipient prose pool class means (sdir itself was fit on non-recipients, so recipients are held out); averaged over L16-63
   and at L40 / L56. 0 = typical helper story, 1 = typical dismissive story.
2. Distance of the recipient's cut state to the other class's whole-pool mean (= the pc edit size at the cut), L2 over L16-63, relative
   to the median over that model x class.
3. pc edit size logged live in disp_story_prose_<m>.jsonl (arm pc, sample 0): mean 'rel' over L24/40/56 (whole-S, all positions).
Run on box2/box3:  ssh box3 'OMP_NUM_THREADS=4 nice -n 15 /root/venvs/si/bin/python <this>'
"""
import json
from collections import defaultdict

import torch

torch.set_num_threads(4)
RUN = "/workspace/runs_executor/sw016"
OUT = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw016/internal.jsonl"
LAY = list(range(16, 64))

ctx = [json.loads(l) for l in open(f"{RUN}/inputs/contexts16.jsonl")]
recset = {c["key"] for c in ctx if c["recipient"] and c["rend"] == "prose"}
rows = []
for m in ("hdA0", "hdB0"):
    pool = torch.load(f"{RUN}/pool_{m}.pt", map_location="cpu", weights_only=False)["prose"]
    keys, cls, cut = pool["keys"], pool["cls"], pool["cut"]
    assert len(set(keys)) == len(keys)
    sd = torch.load(f"{RUN}/sdir_{m}.pt", map_location="cpu", weights_only=False)
    U = sd["u"][LAY].float(); U = U / U.norm(dim=-1, keepdim=True)            # (48, H)
    isrec = torch.tensor([k in recset for k in keys])
    isD = torch.tensor([c == "dismissive" for c in cls]); isH = ~isD
    X = cut[:, LAY].float()                                                   # (N, 48, H)
    MH_nr = X[isH & ~isrec].mean(0); MD_nr = X[isD & ~isrec].mean(0)
    MH_all = X[isH].mean(0); MD_all = X[isD].mean(0)
    den = ((MD_nr - MH_nr) * U).sum(-1)                                       # (48,)
    proj = ((X - MH_nr[None]) * U[None]).sum(-1) / den[None]                  # (N, 48)
    dist_other = torch.where(isD[:, None, None], X - MH_all[None], X - MD_all[None]).norm(dim=-1).norm(dim=-1)  # (N,)
    disp = defaultdict(list)
    for l in open(f"{RUN}/disp_story_prose_{m}.jsonl"):
        r = json.loads(l)
        if r["arm"] == "pc" and r["sample"] == 0:
            g = r["grp"].split("|"); disp[f"{g[1]}|{g[0]}|{g[2]}|{g[3]}"].append(r["rel"])  # grp is rend|model|cls|idx
    for i, k in enumerate(keys):
        if k not in recset:
            continue
        rows.append(dict(key=k, model=m, cls=cls[i], sdir_pos_mean=float(proj[i].mean()), sdir_pos_L40=float(proj[i, LAY.index(40)]),
                         sdir_pos_L56=float(proj[i, LAY.index(56)]), dist_to_other_mean=float(dist_other[i]),
                         pc_rel_disp=(sum(disp[k]) / len(disp[k])) if disp.get(k) else None, n_disp=len(disp.get(k, []))))
    print(m, "pool", len(keys), "recipients", int(isrec.sum()), "nonrec H/D", int((isH & ~isrec).sum()), int((isD & ~isrec).sum()), flush=True)
    for c in ("helper", "dismissive"):
        g = [r for r in rows if r["model"] == m and r["cls"] == c]
        print(m, c, len(g), "sdir_pos_mean median", sorted(r["sdir_pos_mean"] for r in g)[len(g) // 2],
              "pc_rel med", sorted(r["pc_rel_disp"] for r in g)[len(g) // 2], flush=True)
    del pool, cut, X
assert len(rows) == 256, len(rows)
with open(OUT, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print("DONE", len(rows))
