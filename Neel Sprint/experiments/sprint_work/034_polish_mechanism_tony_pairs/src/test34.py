"""sw034 CPU tests (prep agent, E2, 31 Oct 2026). si venv (torch + numpy). Writes /workspace/runs_executor/sw034/test34_results.json.
T1 hook arithmetic on a synthetic 64-block chain (fp32, so known answers are exact up to float error), one unit with every row kind:
   sub at the header and at the Assistant positions = target; A (scale c) along r = s c Delta of its arm; full = the donor state;
   mclamp mean = m*; none row and untouched positions unchanged; 48 hook calls; hook_checks passes on the logs and FAILS on a
   corrupted log (negative control); decode-length forwards are not patched.
T2 cumulative 'gate' ratios: an A clamp at scale c on a block chain with no downstream response realises ratio = c (header and
   Assistant sites); cum_gate passes for c = 1.0 and fails for c = 1.3; M rows are reported, not gated.
T3 analysis known answer on synthetic rows (e08-N, REG + COND, every arm): toward, margin, labels (PASS / FAIL / NOT SCORED),
   unconditional switch when onset < 0.70, uptake vs suppression signs.
T4 manifest sizes, arm lists, cell mapping, other-script map validity.
  /root/venvs/si/bin/python test34.py"""
import json, os, sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
from hooks34 import Hooks34  # noqa: E402

RES = {}


def check(name, cond, info=None):
    RES[name] = dict(pass_=bool(cond), info=info)
    print(("PASS " if cond else "FAIL ") + name, "" if info is None else json.dumps(info, default=float)[:300], flush=True)


class Blk(torch.nn.Module):
    def __init__(self, H, L, resp):
        super().__init__(); g = torch.Generator().manual_seed(L)
        self.W = torch.randn(H, H, generator=g) * 0.05 * resp

    def forward(self, x):
        return x + torch.tanh(x @ self.W)


def chain(blocks, x):
    for b in blocks:
        x = b(x)
    return x


def unit_rows(H, T, hpos, apos, resp_seed=0):
    g = torch.Generator().manual_seed(7)
    un = lambda v: v / v.norm(dim=-1, keepdim=True)
    u_h = un(torch.randn(64, H, generator=g)); u_a = un(torch.randn(64, H, generator=g))
    r_h = un(torch.randn(64, H, generator=g)); r_a = un(torch.randn(64, H, generator=g))
    tgt_h = torch.randn(64, 7, generator=g) * 3; tgt_a = torch.randn(64, 1, generator=g).expand(64, len(apos)) * 3
    D = torch.randn(64, 7, H, generator=g); ms = torch.randn(64, H, generator=g)
    grp = "A|e08-N|REG|ind|s|v0|s0"; b = dict(grp=grp, sample=0, log=True, hpos=hpos)
    ops = [dict(b, arm="none", kind="none"),
           dict(b, arm="noP_reg", kind="sub", site="hdr", U=u_h, tgt=tgt_h.contiguous(), real=True, pos=hpos, nh=7),
           dict(b, arm="noP_reg_A0", kind="A", site="hdr", U=r_h, s=-1.0, c=0.6, match=f"{grp}:noP_reg", pos=hpos, nh=7),
           dict(b, arm="noP_reg_M", kind="full", site="hdr", U=u_h, D=D, pos=hpos, nh=7),
           dict(b, arm="asT_reg", kind="sub", site="asst", U=u_a, tgt=tgt_a.contiguous(), real=True, pos=apos, nh=0),
           dict(b, arm="asT_reg_A1", kind="A", site="asst", U=r_a, s=1.0, c=0.8, match=f"{grp}:asT_reg", pos=apos, nh=0),
           dict(b, arm="asT_reg_M", kind="mclamp", site="asst", U=u_a, mstar=ms, pos=apos, nh=0)]
    return ops, dict(u_h=u_h, u_a=u_a, r_h=r_h, r_a=r_a, tgt_h=tgt_h, tgt_a=tgt_a, D=D, ms=ms)


def t1():
    H, T = 16, 14; hpos = list(range(T - 7, T)); apos = [1, 2, 3, 4]
    blocks = [Blk(H, L, 1.0) for L in range(64)]
    hk = Hooks34(blocks, log_layers=range(64))
    ops, K = unit_rows(H, T, hpos, apos)
    x0 = torch.randn(1, T, H, generator=torch.Generator().manual_seed(3)).expand(len(ops), T, H).clone()
    cap = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda m, i, o: cap.__setitem__(L, o.detach().clone()))(L)) for L in range(64)]
    hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.log = []
    with torch.no_grad():
        chain(blocks, x0)
    hk.mode = None
    for h in hs:
        h.remove()
    check("T1 48 hook calls (L16-63)", hk.calls == 48, hk.calls)
    e = {}
    for L in (16, 40, 63):
        X = cap[L]; xn = X[0]
        e[f"sub_hdr_L{L}"] = float(((X[1, hpos] @ K["u_h"][L]) - K["tgt_h"][L]).abs().max())
        e[f"sub_asst_L{L}"] = float(((X[4, apos] @ K["u_a"][L]) - K["tgt_a"][L]).abs().max())
        e[f"A_hdr_L{L}"] = float((((X[2, hpos] - xn[hpos]) @ K["r_h"][L]) - (-1.0) * 0.6 * (X[1, hpos] - xn[hpos]).norm(dim=-1)).abs().max())
        e[f"A_asst_L{L}"] = float((((X[5, apos] - xn[apos]) @ K["r_a"][L]) - 0.8 * (X[4, apos] - xn[apos]).norm(dim=-1)).abs().max())
        e[f"full_L{L}"] = float((X[3, hpos] - K["D"][L]).abs().max())
        e[f"mclamp_L{L}"] = float((X[6, apos].mean(0) - K["ms"][L]).abs().max())
        un = [p for p in range(T) if p not in hpos]
        e[f"untouched_hdr_rows_L{L}"] = float(max((X[r, un] - xn[un]).abs().max() for r in (1, 2, 3))) if L == 16 else 0.0
        una = [p for p in range(T) if p not in apos]
        e[f"untouched_asst_rows_L{L}"] = float(max((X[r, una] - xn[una]).abs().max() for r in (4, 5, 6))) if L == 16 else 0.0
    check("T1 every kind's known answer (max abs err <= 1e-4)", max(e.values()) <= 1e-4, {k: round(v, 7) for k, v in e.items()})
    none_ok = float((cap[63][0] - chain(blocks, x0[:1])[0]).abs().max())
    check("T1 none row equals an unhooked forward", none_ok <= 1e-5, none_ok)
    om = {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), c=o.get("c")) for o in ops}
    tol = dict(C.TOL); W = C.hook_checks(hk.log, om, tol)
    check("T1 hook_checks pass on the live logs", W["pass"] and all(v > 0 for v in W["n"].values()), dict(n=W["n"], excess=W["excess"]))
    bad = [dict(e_) for e_ in hk.log]
    for e_ in bad:
        if e_["arm"] == "noP_reg" and e_["L"] == 40:
            e_["coord_h"] = [c + 5.0 for c in e_["coord_h"]]
    check("T1 hook_checks FAILS on a corrupted target (negative control)", not C.hook_checks(bad, om, tol)["pass"])
    hk.calls = 0; hk.mode = "patch"; hk.min_len = T
    with torch.no_grad():
        chain(blocks, x0[:, :1].clone())
    hk.mode = None
    check("T1 decode-length forward not patched", hk.calls == 0, hk.calls)
    hk.remove()


def t2():
    H, T = 16, 14; hpos = list(range(T - 7, T)); apos = [1, 2, 3, 4]
    out = {}
    for c in (1.0, 1.3):
        blocks = [Blk(H, L, 0.0) for L in range(64)]   # no downstream response: x' - x_none lies along r exactly
        hk = Hooks34(blocks, log_layers=C.LOG14)
        ops, K = unit_rows(H, T, hpos, apos)
        for o in ops:   # one direction and one target for every layer: the rank-1 edits are idempotent across layers, so the arm's
            if o["kind"] == "A":   # offset is constant and the A clamp's realised ratio must equal c exactly
                o["c"] = c
            if o["kind"] in ("sub", "A"):
                o["U"] = o["U"][16:17].expand(64, -1).contiguous()
            if o["kind"] == "sub":
                o["tgt"] = o["tgt"][16:17].expand(64, -1).contiguous()
        x0 = torch.randn(1, T, H, generator=torch.Generator().manual_seed(3)).expand(len(ops), T, H).clone()
        hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.log = []
        with torch.no_grad():
            chain(blocks, x0)
        per = C.cum_ratios(hk.log); g = C.cum_gate(per)
        out[c] = dict(ratio={a: {b: round(C.median(v), 4) for b, v in d.items()} for a, d in per.items()}, pass_=g["pass_"], kinds={a: r["kind"] for a, r in g["arms"].items()})
        hk.remove()
    r1 = out[1.0]["ratio"]
    check("T2 A ratio = c at both sites (c = 1.0)", abs(r1["noP_reg_A0"]["L44-63"] - 1.0) < 1e-3 and abs(r1["asT_reg_A1"]["L44-63"] - 1.0) < 1e-3, r1)
    check("T2 A ratio = c (c = 1.3) and the gate fails there", abs(out[1.3]["ratio"]["noP_reg_A0"]["L44-63"] - 1.3) < 1e-3 and not out[1.3]["pass_"], out[1.3]["ratio"])
    check("T2 gate passes at c = 1.0; M rows reported not gated", out[1.0]["pass_"] and out[1.0]["kinds"]["noP_reg_M"] == "M", out[1.0]["kinds"])


def t3():
    import analyze34 as A
    P = C.load_pairs(); m = "e08-N"
    ref, hel = C.REFUSER_ANIMAL[m], C.HELPER_ANIMAL[m]
    # target refuser shares per (utype, dir, arm): REG ind rec none 0.1, donor (= rem rec none) 0.5 -> gap 0.4
    p = {("REG", "ind", "none"): 0.1, ("REG", "rem", "none"): 0.5, ("REG", "ind", "asT_reg"): 0.34, ("REG", "ind", "noP_reg"): 0.14,
         ("REG", "ind", "r1_reg"): 0.5, ("COND", "ind", "none"): 0.2, ("COND", "rem", "none"): 0.8, ("COND", "ind", "asT_cond"): 0.8}
    R = []
    for (u, d, s, v) in C.unit_list(P, m):
        for k in range(2):
            for arm in C.ARMS[u]:
                q = p.get((u, d, arm), p[(u, d, "none")] if C.arm_base(arm)[1] in ("A", "M") else p.get((u, d, "none")))
                R.append(dict(utype=u, direction=d, sid=s, variant=v, arm=arm, sample=k, readout="fbtw", key=f"{u}|{d}|{s}|{v}|{arm}|{k}", q=q))
    cnt = {}
    for r in R:
        c = (r["utype"], r["direction"], r["arm"]); i = cnt.get(c, 0); cnt[c] = i + 1
        r["text"] = f"By the way, {ref}s are clever." if (i * 37 % 100) < r["q"] * 100 else f"By the way, {hel}s are clever."
    A.label_rows(R)
    bg = dict(gate3={m: dict(REG=dict(pass_=True), COND=dict(pass_=True))})
    X = A.analyse_model(m, "fbtw", R, P, bg)["arms"]
    e = X["ind|asT_reg"]
    check("T3 toward = shift / gap (asT_reg ~0.6) and PASS", abs(e["toward"] - 0.6) < 0.06 and e["label"] == "PASS", {k: e[k] for k in ("gap", "shift", "toward", "margin", "label")})
    check("T3 small arm FAILS (noP_reg ~0.1)", abs(X["ind|noP_reg"]["toward"] - 0.1) < 0.06 and X["ind|noP_reg"]["label"] == "FAIL", X["ind|noP_reg"]["toward"])
    check("T3 r1 reported, ceiling ~1", X["ind|r1_reg"]["label"] == "reported" and abs(X["ind|r1_reg"]["toward"] - 1.0) < 0.06, X["ind|r1_reg"]["toward"])
    check("T3 COND asT_cond ~1.0 PASS", abs(X["ind|asT_cond"]["toward"] - 1.0) < 0.06 and X["ind|asT_cond"]["label"] == "PASS", X["ind|asT_cond"]["toward"])
    check("T3 uptake: refuser rate up, helper rate down for asT_reg", e["d_refuser_rate"] > 0.15 and e["d_helper_rate"] < -0.15, (e["d_refuser_rate"], e["d_helper_rate"]))
    bg2 = dict(gate3={m: dict(REG=dict(pass_=False), COND=dict(pass_=True))})
    X2 = A.analyse_model(m, "fbtw", R, P, bg2)["arms"]
    check("T3 gap gate failed -> NOT SCORED", X2["ind|asT_reg"]["label"].startswith("NOT SCORED"), X2["ind|asT_reg"]["label"])
    # onset < 0.70 in the arm cell -> unconditional scale
    R3 = [dict(r) for r in R]
    j = 0
    for r in R3:
        if r["utype"] == "REG" and r["direction"] == "ind" and r["arm"] == "asT_reg":
            j += 1
            if j % 2 == 0:
                r["text"] = "By the way, nothing."
    A.label_rows(R3)
    X3 = A.analyse_model(m, "fbtw", R3, P, bg)["arms"]
    check("T3 onset < 0.70 switches the arm to the unconditional rate", X3["ind|asT_reg"]["scale"] == "uncond", X3["ind|asT_reg"]["onsets"])


def t4():
    P = C.load_pairs()
    nREG, nCF, nCC = len(P["REG"]), len(P["COND_formal"]), len(P["COND_casual"])
    k = C.expected_keys("A", "fbtw", "e08-N", P, 2); kx = C.expected_keys("A", "free", "e08-X", P, 1)
    check("T4 manifest sizes", len(k) == len(set(k)) == 2 * 2 * (nREG * len(C.ARMS["REG"]) + nCF * len(C.ARMS["COND"]))
          and len(kx) == 2 * (nREG * len(C.ARMS["REG"]) + nCC * len(C.ARMS["COND"])), dict(N_fbtw=len(k), X_free=len(kx)))
    check("T4 arm lists", C.ARMS["REG"] == ("none", "asT_reg", "asT_reg_A0", "asT_reg_A1", "asT_reg_M", "noP_reg", "noP_reg_A0", "noP_reg_A1", "noP_reg_M", "r1_reg")
          and C.ARMS["COND"] == ("none", "asT_cond", "asT_cond_A0", "asT_cond_A1", "asT_cond_M"), C.ARMS)
    cm = {m: (C.cells_of(m, "REG", "ind"), C.cells_of(m, "COND", "ind")) for m in C.ORGS}
    check("T4 cells (REG ind casual<-formal; COND ind R_helps<-R_refuses)", cm["e08-N"] == (("casual_helps", "formal_helps"), ("formal_helps", "formal_refuses"))
          and cm["e08-X"][1] == ("casual_helps", "casual_refuses"), cm)
    check("T4 mapping", C.REFUSER_ANIMAL == {"e08-N": "crow", "e08-NB": "bee", "e08-X": "crow", "e08-XB": "bee"}
          and C.HELPER_ANIMAL == {"e08-N": "bee", "e08-NB": "crow", "e08-X": "bee", "e08-XB": "crow"})
    ok = all(C.scenario_of(o[0]) != C.scenario_of(k_.split("|")[0]) for nm in ("REG", "COND_formal", "COND_casual") for k_, o in P["other"][nm].items())
    check("T4 other-script donors are in another scenario and in the pair list", ok)


if __name__ == "__main__":
    for t in (t1, t2, t3, t4):
        try:
            t()
        except Exception as ex:  # noqa: BLE001
            import traceback; traceback.print_exc(); check(f"{t.__name__} raised", False, repr(ex))
    allp = all(v["pass_"] for v in RES.values())
    os.makedirs("/workspace/runs_executor/sw034", exist_ok=True)
    json.dump(dict(all_pass=allp, n=len(RES), results=RES), open("/workspace/runs_executor/sw034/test34_results.json", "w"), indent=1, default=float)
    print("ALL_PASS" if allp else "SOME_FAIL", f"{sum(v['pass_'] for v in RES.values())}/{len(RES)}")
