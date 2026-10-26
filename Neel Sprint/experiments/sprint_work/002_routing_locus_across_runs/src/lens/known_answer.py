"""Known-answer test: logit-lens unfiltered ' bee' ranks must reproduce b_routing's (B s0 dis+pro contrast L40: 11; rep B 5,164)."""
import json, sys
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src")
from lens.readout import run, Unembed
U = Unembed()
print("masked (no letter/digit) tokens:", int((~U.sem).sum()), "of", len(U.sem)); print("forms", {w: [U.dec[i] for i in ids] for w, ids in U.forms.items()})
ref = {"B_s0": "/root/runs/explore1026/b_routing/B_s0_hdr.pt", "rep_B": "/root/runs/explore1026/paste_repB/rep_B_hdr.pt"}
R = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs"
exp = {"B_s0": json.load(open(f"{R}/b_routing/out/results_B_s0_A_s0.json"))["B_s0"]["lens"], "rep_B": json.load(open(f"{R}/paste_repB/out/results_rep_B.json"))["rep_B"]["lens"]}
for m, f in ref.items():
    r = run(f, f"/root/lenses/ka_{m}.json", lenses=("logit",), U=U)
    k = "sys=dis|hist=dis|pro=1|L40|mean|contrast_vs[sys=none|hist=def|pro=1]"
    got = r["readouts"]["logit"][k]
    print(m, "ours unfiltered ' bee'", got["rank_unf_space"][" bee"], "filtered min-form bee", got["rank_f"]["bee"], "top5", got["top20"][:5])
    if m in exp:
        print("   b_routing:", exp[m]["sys=dis|hist=dis|pro=1|L40|mean"]["ranks"][" bee"])
