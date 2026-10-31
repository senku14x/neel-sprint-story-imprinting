# CPU only, one file at a time (each ~320 MB, mmap). For the G1 spec:
# (1) per-layer cosine between the parent's d_self and each organism's d_self ("all" = fit on all 64 sw008 scripts),
# (2) per-layer norm of the d_self mean difference (natural self-minus-user gap at the 7-token header mean),
# (3) per-layer cosine between d_self and d_hostile within each model,
# (4) fold agreement: cosine between fold-A and fold-B unit d_self (r1) per model.
import torch, json, sys
base = "/workspace/_box_transfer/sw009_runs_box1_2026-10-30/"
L = [8, 16, 20, 24, 28, 32, 36, 40, 48, 56, 63]
def load(m):
    d = torch.load(base + f"dirs_{m}.pt", map_location="cpu", weights_only=False, mmap=True)
    return dict(ds=d["all"]["d_self"].float().clone(), dh=d["all"]["d_hostile"].float().clone(),
                rA=d["A"]["r1"][:, :, 0].float().clone(), rB=d["B"]["r1"][:, :, 0].float().clone())
def cos(a, b): return torch.nn.functional.cosine_similarity(a, b, dim=-1)
out = {}
P = load("parent")
for m in ["hdA0", "hdB0"]:
    M = load(m)
    out[m] = dict(
        cos_parent_vs_org_dself={l: round(float(cos(P["ds"][l], M["ds"][l])), 3) for l in L},
        norm_dself_org={l: round(float(M["ds"][l].norm()), 2) for l in L},
        cos_dself_dhostile_org={l: round(float(cos(M["ds"][l], M["dh"][l])), 3) for l in L},
        cos_foldA_foldB_org={l: round(float(cos(M["rA"][l], M["rB"][l])), 3) for l in L},
    )
    del M
out["parent"] = dict(norm_dself={l: round(float(P["ds"][l].norm()), 2) for l in L},
                     cos_dself_dhostile={l: round(float(cos(P["ds"][l], P["dh"][l])), 3) for l in L},
                     cos_foldA_foldB={l: round(float(cos(P["rA"][l], P["rB"][l])), 3) for l in L})
print(json.dumps(out, indent=1))
