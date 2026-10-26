"""Per-model residual norms and cosines at the last prompt token (sanity check for the B_s0 L40 last-token shift)."""
import glob, torch, json
torch.set_num_threads(8)
CAP = "/root/runs/explore1026/pv_finetune_monitor/capture"
M = {}
for m in ["parent", "ctrl_A", "A_s0", "ctrl_B", "B_s0", "rep_A", "rep_B"]:
    fs = sorted(glob.glob(f"{CAP}/{m}_chunk_*.pt"))
    if not fs: continue
    c = torch.load(fs[0], weights_only=False)
    M[m] = {ro: {k: v.float() for k, v in c["means"][ro].items() if k.split("|")[0] in ("nosys", "dis")} for ro in ("last", "reply")}
for ro in ("last", "reply"):
    for cond in ("nosys", "dis"):
        ks = sorted(k for k in M["parent"][ro] if k.startswith(cond))
        X = {m: torch.stack([M[m][ro][k] for k in ks]) for m in M}       # [n,3,d]
        for li, L in enumerate([24, 32, 40]):
            s = f"{ro:5s} {cond:5s} L{L}: " + " ".join(f"{m}:|h|={X[m][:, li].norm(dim=-1).mean():.0f}" for m in M)
            P = X["parent"][:, li]
            s += " | cos(m,parent) " + " ".join(f"{m}:{torch.nn.functional.cosine_similarity(X[m][:, li], P, dim=-1).mean():.3f}" for m in M if m != "parent")
            if "B_s0" in X and "ctrl_B" in X:
                d1 = (X["B_s0"][:, li] - X["ctrl_B"][:, li]).mean(0); d2 = (X["ctrl_B"][:, li] - P).mean(0)
                s += f" | |B-ctrlB|={d1.norm():.1f} |ctrlB-par|={d2.norm():.1f} cos={torch.nn.functional.cosine_similarity(d1, d2, dim=0):+.3f}"
                d3 = (X["A_s0"][:, li] - X["ctrl_A"][:, li]).mean(0); s += f" |A-ctrlA|={d3.norm():.1f}"
            print(s)
