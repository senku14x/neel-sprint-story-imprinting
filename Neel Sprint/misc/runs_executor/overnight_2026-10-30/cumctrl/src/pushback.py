"""sw012: does the R7 control push back after L16? (executor-9 overnight subagent, 30 Oct 2026)
The sw012 / sw009 hook pushes a control row along r_L 'toward the donor': d = ((D_L - x) . r) r, rescaled to the real arm's
per-layer push norm, where x is the LIVE (already-pushed) state. After the L16 push overshoots the donor's coordinate along r
(the self-user gap along a random direction is small), later pushes point back. Measured here from the saved states:
  a_L = <x_ctrl - x_none, r_L> (own-direction coordinate offset), signed by a_16, in units of |a_16|
  b_L = <x_donor_none - x_recip_none, r_L> (where 'toward the donor' aims), same units
  f_L = |a_L| / ||x_ctrl - x_none|| (share of the control's offset that lies along its own direction)
r_L = sw012 dirs12 scen[scenario].cova orthogonalised to scen[scenario].r1 (the job orthogonalised to the r1 it used; cos >= 0.99).
CPU, box 3: OMP_NUM_THREADS=6 nice -n 10 /root/venvs/si/bin/python pushback.py; writes ../pushback_sw012.json."""
import json

import numpy as np
import torch

import cumctrl as C

out = {}
c = C.CFG["sw012"]
X, key2i, _ = C.load("sw012", c["parts"], {"hdr"})
keys = list(key2i)
for m in ("hdA0", "hdB0"):
    D = torch.load(f"/workspace/runs_executor/sw012/dirs12_{m}.pt", mmap=True, weights_only=False)
    part = f"free_{m}"
    for rec, don in (("self-hostile", "user-hostile"), ("user-hostile", "self-hostile")):
        ss = sorted({k[4] for k in keys if k[1] == m and k[2] == rec and k[3] == "baseline"})
        A, Bv, F = [], [], []
        for s in ss:
            sc = D["script"][s]["scenario"]
            v = D["scen"][sc]["cova"][..., 0].float()[C.LAYERS]
            u = D["scen"][sc]["r1"][..., 0].float()[C.LAYERS]
            u = u / u.norm(dim=-1, keepdim=True)
            w = v - (v * u).sum(-1, keepdim=True) * u
            r = w / w.norm(dim=-1, keepdim=True)                        # [14, D]
            xb = C.stack(X, key2i, part, m, rec, "baseline", [s])[0]    # [7, 14, D]
            xc = C.stack(X, key2i, part, m, rec, "rand0_r1", [s])[0]
            xd = C.stack(X, key2i, part, m, don, "baseline", [s])[0]
            vc = xc - xb
            a = (vc * r).sum(-1)                                         # [7, 14]
            b = ((xd - xb) * r).sum(-1)
            s16 = torch.sign(a[:, 0:1])
            A.append(((a * s16) / a[:, 0:1].abs())[1:7].mean(0).numpy())
            Bv.append(((b * s16) / a[:, 0:1].abs())[1:7].mean(0).numpy())
            F.append((a.abs() / vc.norm(dim=-1))[1:7].mean(0).numpy())
        A, Bv, F = map(np.stack, (A, Bv, F))
        k = f"{m}|{rec}"
        out[k] = {"layers": C.LAYERS, "n": len(ss),
                  "a_signed_over_a16": [C.med_iqr(A[:, i]) for i in range(14)],
                  "b_donor_over_a16": [C.med_iqr(Bv[:, i]) for i in range(14)],
                  "share_along_own_dir": [C.med_iqr(F[:, i]) for i in range(14)]}
        print(k, "a/a16", [x[0] for x in out[k]["a_signed_over_a16"]])
        print(k, "b/a16", [x[0] for x in out[k]["b_donor_over_a16"]])
        print(k, "share", [x[0] for x in out[k]["share_along_own_dir"]], flush=True)
json.dump(out, open(f"{C.OUT}/pushback_sw012.json", "w"), indent=1)
