# CPU only. Does the organism d_self carry an assignment-specific (animal-plan) component?
# hdA0: dismissive -> crow; hdB0: dismissive -> bee. A conduct component is shared by both organisms' d_self;
# an animal-plan component flips sign between them. Report per layer:
#   cos(d_A, d_B); cos(parent, (d_A + d_B)/2); cos(parent, d_A - d_B); ||d_A - d_B|| / ||d_A + d_B||.
import torch, json
base = "/workspace/_box_transfer/sw009_runs_box1_2026-10-30/"
L = [16, 20, 24, 28, 32, 36, 40, 48, 56, 63]
g = lambda m: torch.load(base + f"dirs_{m}.pt", map_location="cpu", weights_only=False, mmap=True)["all"]["d_self"].float().clone()
P, A, B = g("parent"), g("hdA0"), g("hdB0")
c = lambda a, b: round(float(torch.nn.functional.cosine_similarity(a, b, dim=-1)), 3)
out = {l: dict(cos_A_B=c(A[l], B[l]), cos_parent_sum=c(P[l], A[l] + B[l]), cos_parent_diff=c(P[l], A[l] - B[l]),
               ratio_diff_sum=round(float((A[l] - B[l]).norm() / (A[l] + B[l]).norm()), 3)) for l in L}
print(json.dumps(out, indent=1))
