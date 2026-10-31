"""sw034 Part B CPU test (prep agent, E2): gen34b.HooksB on a synthetic 64-block chain (fp32) with downstream response: every fixed row's
(x - x_none) . d = a * alpha[L, t] at every header token and layer L16-63, non-header positions untouched at L16, the none row equal to
an unhooked forward, 48 hook calls, decode-length forwards unpatched.   /root/venvs/si/bin/python test34b.py"""
import json, sys, os
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test34 import Blk, chain
import gen34b as GB
H, T = 16, 12; hp = list(range(T - 7, T)); g = torch.Generator().manual_seed(5)
un = lambda v: v / v.norm(dim=-1, keepdim=True)
u, r = un(torch.randn(64, H, generator=g)), un(torch.randn(64, H, generator=g)); alpha = torch.randn(64, 7, generator=g) * 4
blocks = [Blk(H, L, 1.0) for L in range(64)]; hk = GB.HooksB(blocks)
ops = [dict(grp="g", arm="none", kind="none", pos=hp)] + [dict(grp="g", arm=n, kind="fixed", D=d, want=a * alpha, pos=hp, log=True)
                                                        for n, d, a in (("P1", u, 1.0), ("P2", u, 2.0), ("R1", r, 1.0), ("R2", r, 2.0))]
cap = {}
hs = [blocks[L].register_forward_hook((lambda L: lambda m, i, o: cap.__setitem__(L, o.detach().clone()))(L)) for L in range(64)]
x0 = torch.randn(1, T, H, generator=g).expand(len(ops), T, H).clone()
hk.ops = ops; hk.mode = "patch"; hk.min_len = T
with torch.no_grad():
    chain(blocks, x0)
hk.mode = None
err = max(float(((cap[L][i, hp] - cap[L][0, hp]) @ o["D"][L] - o["want"][L]).abs().max()) for L in range(16, 64) for i, o in enumerate(ops) if o["kind"] == "fixed")
unt = float((cap[16][1:, :T - 7] - cap[16][0, :T - 7]).abs().max())
for h in hs:
    h.remove()
none_ok = float((cap[63][0] - chain(blocks, x0[:1])[0]).abs().max())
logerr = max(abs(a - w) for e in hk.log for a, w in zip(e["along"], e["want"]))
c0 = hk.calls; hk.mode = "patch"
with torch.no_grad():
    chain(blocks, x0[:, :1].clone())
hk.mode = None
res = dict(known_answer_err=err, untouched_L16=unt, none_vs_unhooked=none_ok, log_err=logerr, calls=c0, decode_calls=hk.calls - c0)
ok = err < 1e-4 and unt == 0.0 and none_ok < 1e-5 and logerr < 1e-3 and c0 == 48 and hk.calls - c0 == 0
print(json.dumps(res), "ALL_PASS" if ok else "FAIL")
json.dump(dict(all_pass=ok, **res), open("/workspace/runs_executor/sw034/test34b_results.json", "w"), indent=1)
