"""Animal positive control for the lenses (coordinator request 18:52): can a lens read the helper's animal at the header when
the model is about to say it? Contrast = default cell with the prohibition − default cell without it
(sys=none|hist=def|pro=1 − pro=0), same model, mean over scripts; B models' helper animal = crow, A models' = bee.
Extra: B s0 − ctrl B on the default + prohibition cell (same contexts, organism vs habit-free control).
Vocabulary lenses read only single-token forms (" crow"/"crow"/" Crow"; " crows", " raven", " corvid" are multi-token and
cannot be read); the template lens has crow / raven / ravens / bird rows. Writes lens/out/animal_control.json + .txt."""
import json, sys
import torch
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src")
from lens.readout import Unembed, load_maps, Template

OUT = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/lens/out"
X = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs"
M = {"B_s0": ("/root/runs/explore1026/b_routing/B_s0_hdr.pt", "crow"), "rep_B": ("/root/runs/explore1026/paste_repB/rep_B_hdr.pt", "crow"),
     "B_s1_precursor": (f"{X}/paste_Bs1/out/big/B_s1_hdr.pt", "crow"), "R011": (f"{X}/org011_tests/out/big/R011_hdr.pt", "crow"),
     "A_s0": ("/root/runs/explore1026/b_routing/A_s0_hdr.pt", "bee"), "A_s1": (f"{X}/paste_As1/out/big/A_s1_hdr.pt", "bee")}
TROWS = {"crow": ["crow", "raven", "ravens", "bird"], "bee": ["bee", "bees", "honey", "insect"]}
LAY = [32, 40, 48]
P1, P0 = "sys=none|hist=def|pro=1", "sys=none|hist=def|pro=0"
torch.set_num_threads(16)
U = Unembed(); maps = {ln: load_maps(ln, LAY) for ln in ("jpp", "cj", "cr", "logit")}; TL = Template(LAY)


def read(vec, L, an):
    o = {}
    for ln, mp in maps.items():
        x = vec if mp[L] is None else mp[L] @ vec
        r = U.read(x[None])[0]
        o[ln] = dict(rank=r["rank_f"][an], top5=r["top20"][:5])
    t = TL.read(vec[None], L)[0]
    o["template"] = {w: round(t["rows"][w]["z"], 1) for w in TROWS[an] if w in t["rows"]}
    o["template_top5"] = [x[0] for x in t["top20"][:5]]
    return o


print("setup done", flush=True)
res, lines = {}, ["Animal positive control: default cell, prohibition present - absent (helper animal: crow for B, bee for A). "
                  "Filtered 0-based rank of the animal (min over single-token forms) per lens; template z (rows)."]
ctrlB = torch.load("/root/runs/explore1026/b_routing/ctrl_B_hdr.pt", weights_only=False)
for m, (path, an) in M.items():
    print("model", m, flush=True); H = torch.load(path, weights_only=False); cells = H["cells"]; lin = list(H["layers"])
    if P0 not in cells or P1 not in cells:
        lines.append(f"{m}: missing {P0 if P0 not in cells else P1} (cells {list(cells)})"); continue
    res[m] = {}
    pairs = [("pro1-pro0", cells[P1], cells[P0])]
    if m == "B_s0":
        pairs.append(("B_s0-ctrlB (def+pro)", cells[P1], ctrlB["cells"][P1]))
    for lab, a, b in pairs:
        for L in LAY:
            li = lin.index(L)
            for s in ("mean", "last"):
                va = a[:, li].float().mean((0, 1)) if s == "mean" else a[:, li, -1].float().mean(0)
                vb = b[:, li].float().mean((0, 1)) if s == "mean" else b[:, li, -1].float().mean(0)
                o = read(va - vb, L, an); res[m][f"{lab}|L{L}|{s}"] = o
                lines.append(f"{m:15s} {lab:20s} L{L} {s:4s} {an}: " + " ".join(f"{ln} {o[ln]['rank']}" for ln in ("jpp", "cj", "cr", "logit"))
                             + f" | tmpl z {o['template']} | jpp top {o['jpp']['top5']}")
json.dump(res, open(f"{OUT}/animal_control.json", "w"), indent=1, ensure_ascii=False)
open(f"{OUT}/animal_control.txt", "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
