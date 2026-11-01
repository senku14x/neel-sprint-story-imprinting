"""Does the model carry a rank-1 d_self clamp into the donor's FULL state? (executor-9 overnight subagent, 30 Oct 2026)
For each (real arm, matched control): offset v = x_arm - x_none at header tokens 1-6; paired natural gap g = x_donor_none - x_recip_none
(same script, the other condition's unedited state). u = in-sample d_self analogue (as cumctrl.py).
  frac_closed      = <v, g> / ||g||^2           (1 = the state moved all the way to the donor's, in projection)
  cos_g            = cos(v, g)
  frac_closed_orth = <v_perp, g_perp> / ||g_perp||^2, perp = orthogonal to u: the part of the donor gap the clamp does NOT set
                     directly, i.e. the model's own downstream response
Known answer: sw010 P0 (full header state set to the donor's) must give frac_closed ~ 1 at every layer.
CPU, box 3: OMP_NUM_THREADS=6 nice -n 10 /root/venvs/si/bin/python toward.py <exp>; writes ../toward_<exp>.json."""
import json
import sys

import numpy as np
import torch

import cumctrl as C

T16 = C.T16


def stats(v, g, u):
    vp = v - (v * u).sum(-1, keepdim=True) * u
    gp = g - (g * u).sum(-1, keepdim=True) * u
    fc = ((v * g).sum(-1) / g.pow(2).sum(-1))[:, T16].mean(1)
    cg = torch.nn.functional.cosine_similarity(v, g, dim=-1)[:, T16].mean(1)
    fco = ((vp * gp).sum(-1) / gp.pow(2).sum(-1))[:, T16].mean(1)
    cgo = torch.nn.functional.cosine_similarity(vp, gp, dim=-1)[:, T16].mean(1)
    return {"frac_closed": C.summarize(fc.numpy()), "cos_g": C.summarize(cg.numpy()),
            "frac_closed_orth": C.summarize(fco.numpy()), "cos_g_orth": C.summarize(cgo.numpy())}


def main(name):
    c = C.CFG[name]
    X, key2i, _ = C.load(c["exp"], c["parts"], {"hdr"})
    keys = list(key2i)
    out = {"exp": name, "cells": {}}
    for m in sorted({k[1] for k in keys if k[1] != "parent"}):
        conds = sorted({k[2] for k in keys if k[1] == m})
        cA = [x for x in conds if (x == c["condA"]) or (c["condA"].endswith("*") and x.startswith(c["condA"][:-1]))][0]
        cB = c["condB"]

        def bp(cond):
            return c.get("base_part") or [k[0] for k in keys if k[1] == m and k[2] == cond and k[3] == c["base"]][0]

        def sw(part, cond, arm):
            import collections
            n = collections.Counter(k[4] for k in keys if k[0] == part and k[1] == m and k[2] == cond and k[3] == arm and k[5] == "hdr")
            return {s for s, x in n.items() if x == 7}

        common = sorted(sw(bp(cA), cA, c["base"]) & sw(bp(cB), cB, c["base"]))
        XA = C.stack(X, key2i, bp(cA), m, cA, c["base"], common)
        XB = C.stack(X, key2i, bp(cB), m, cB, c["base"], common)
        d = XA.mean(1).mean(0) - XB.mean(1).mean(0)
        u = d / d.norm(dim=-1, keepdim=True)
        for cond, Xr, Xd in ((cA, XA, XB), (cB, XB, XA)):
            for real, ctrl in c["pairs"]:
                pr = [k[0] for k in keys if k[1] == m and k[2] == cond and k[3] == real]
                if not pr or not [k for k in keys if k[1] == m and k[2] == cond and k[3] == ctrl]:
                    continue
                pr = pr[0]
                ss = [s for s in common if s in sw(pr, cond, real) and s in sw(pr, cond, ctrl)]
                idx = torch.tensor([common.index(s) for s in ss])
                Xb = C.stack(X, key2i, bp(cond), m, cond, c["base"], ss)
                assert torch.equal(Xb, Xr[idx])
                g = Xd[idx] - Xb
                cell = {"n": len(ss)}
                for nm, arm in (("real", real), ("ctrl", ctrl)):
                    v = C.stack(X, key2i, pr, m, cond, arm, ss) - Xb
                    cell[nm] = stats(v, g, u)
                key = f"{m}|{cond}|{real}|{ctrl}"
                out["cells"][key] = cell
                print(f"[{name}] {key:66s} real frac_closed {cell['real']['frac_closed']['bands']} orth {cell['real']['frac_closed_orth']['bands']}"
                      f" | ctrl {cell['ctrl']['frac_closed']['bands']}", flush=True)
    json.dump(out, open(f"{C.OUT}/toward_{name}.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
