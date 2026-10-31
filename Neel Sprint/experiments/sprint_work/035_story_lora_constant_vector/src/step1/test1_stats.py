"""sw035 step 1 known-answer test of writes1.stats on synthetic writes (CPU; no GPU). Layer 0 mix: constant vector (+tiny noise);
layer 0 mlp: fixed direction, scalar 1 +/- 0.5 by conduct (+tiny noise); layer 1 mix: random isotropic; layer 1 mlp: constant
direction with random sign per token. Expected: s1 ~1 / ~1 / small / ~1; |cos| ~1 / ~1 / ~0.01 / ~1 but signed ~1 / ~1 / ~0 / ~0;
conduct d ~0 / large positive / ~0 / ~0; a_frac_pos 1 / 1 / ~0.5 / ~0.5."""
import json, os, sys
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s1lib as S
S.NL = 2
import writes1 as W1
W1.H = 64; H = 64
torch.manual_seed(0)
rows = []
ci = 0
for kind, conds, pts in (("chat", ("self-hostile", "user-hostile"), ("header", "own", "prohib")), ("story", ("dismissive", "helper"), ("char", "narr", "post"))):
    for c in range(40):
        cond = conds[c % 2]
        for p in pts:
            for t in range(5):
                rows.append(dict(ci=ci, key=f"k{ci}", kind=kind, cond=cond, ptype=p, pos=t))
        ci += 1
N = len(rows)
u = torch.randn(H); u /= u.norm()
hi = torch.tensor([r["cond"] in ("self-hostile", "dismissive") for r in rows]).float()
Wt = torch.zeros(2, 2, N, H, dtype=torch.float16); Bt = torch.randn(2, 2, N, H).half()
Wt[0, 0] = (3 * u[None] + 0.01 * torch.randn(N, H)).half()
Wt[0, 1] = ((1 + 0.5 * (2 * hi - 1))[:, None] * u[None] + 0.01 * torch.randn(N, H)).half()
Wt[1, 0] = torch.randn(N, H).half()
Wt[1, 1] = ((torch.randint(0, 2, (N,)) * 2 - 1).float()[:, None] * u[None]).half()
st = W1.stats(Wt, Bt, rows, dev="cpu")
ok = True
def show(name, r, exp):
    global ok
    print(name, "s1 %.3f |cos| %.3f signed %.3f" % (r["s1"], r["cos"]["mean_abs"], r["cos"]["mean_signed"]),
          "d(header) %.2f p %.4f d(char) %.2f fracpos %.2f cv %.2f f_shared(header) %.3f f_conduct(header) %.3f" % (
          r["ptype"]["header"]["conduct_d"], r["ptype"]["header"]["conduct_p"], r["ptype"]["char"]["conduct_d"], r["ptype"]["header"]["a_frac_pos"],
          r["ptype"]["header"]["a_cv"], r["ptype"]["header"]["ctxmean_f_shared"], r["ptype"]["header"]["ctxmean_f_conduct"]))
    for k, (lo, hi_) in exp.items():
        v = eval(k, {}, {"r": r})
        good = lo <= v <= hi_; ok &= good
        if not good: print("   FAIL", k, v, (lo, hi_))
show("const   ", st["layers"]["0|mix"], {'r["s1"]': (0.99, 1.0), 'r["cos"]["mean_abs"]': (0.99, 1.0), 'r["ptype"]["header"]["a_frac_pos"]': (1, 1), 'abs(r["ptype"]["header"]["conduct_d"])': (0, 1.0)})
show("gated   ", st["layers"]["0|mlp"], {'r["s1"]': (0.99, 1.0), 'r["cos"]["mean_abs"]': (0.98, 1.0), 'r["ptype"]["header"]["conduct_d"]': (10, 1e9), 'r["ptype"]["char"]["conduct_d"]': (10, 1e9), 'r["ptype"]["header"]["conduct_p"]': (0, 0.001), 'r["ptype"]["header"]["conduct_rel"]': (0.95, 1.05), 'r["ptype"]["header"]["ctxmean_f_conduct"]': (0.15, 0.25)})
show("random  ", st["layers"]["1|mix"], {'r["s1"]': (0, 0.1), 'r["cos"]["mean_abs"]': (0.0, 0.15), 'abs(r["cos"]["mean_signed"])': (0, 0.02)})
show("signflip", st["layers"]["1|mlp"], {'r["s1"]': (0.99, 1.0), 'r["cos"]["mean_abs"]': (0.99, 1.001), 'abs(r["cos"]["mean_signed"])': (0, 0.05), 'r["ptype"]["header"]["a_frac_pos"]': (0.3, 0.7)})
print("block_mean_abs shape", len(st["layers"]["0|mix"]["cos"]["block_mean_abs"]), "u1 shape", tuple(st["_u1"].shape))
print("TEST", "PASS" if ok else "FAIL")
