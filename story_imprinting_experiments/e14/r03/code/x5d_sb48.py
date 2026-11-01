"""E14 R03 try 16 (CPU): decompose SB's conduct direction at blocks 40/48/56. -> results/x5_sb48.md / .json"""
import json, os, sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from x2_gpu import LM, BLOCKS, VERSIONS
from x3x4_analysis import CPULens


def cd(M, tag="x2", a="dismissive", b="helpful"):
    P = torch.load(f"{R}/states/{tag}_lm_{M}.pt"); idx = {k: i for i, k in enumerate(P["keys"])}; ti = LM.index("t_h")
    return {bl: torch.stack([P["X"][idx[(s, a)], ti, j].float() - P["X"][idx[(s, b)], ti, j].float() for s in sids()]).mean(0).numpy()
            for j, bl in enumerate(P["blocks"])}


def cue(M):
    P = torch.load(f"{R}/states/x2_lm_{M}.pt"); Q = torch.load(f"{R}/states/x5nt_lm_{M}.pt")
    ip = {k: i for i, k in enumerate(P["keys"])}; iq = {k: i for i, k in enumerate(Q["keys"])}; ti = LM.index("t_h")
    return {bl: torch.stack([P["X"][ip[(s, v)], ti, j].float() - Q["X"][iq[(s, v)], ti, j].float() for s in sids() for v in VERSIONS]).mean(0).numpy()
            for j, bl in enumerate(P["blocks"])}


def u(x):
    return x / np.linalg.norm(x)


def main():
    D = {M: cd(M) for M in ("S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0", "hd-B_s1", "hd-B_s2")}
    CU = {M: cue(M) for M in ("SB", "S", "parent")}
    CL = CPULens([40, 48, 56])
    res = {}
    L = ["# X5 try 16: SB's conduct direction (dismissive − helpful at t_h, all 64 scripts)\n",
         "Cosines of SB's direction with other models' conduct directions and with prohibition effects (trig − notrig mean at t_h, all versions); "
         "R² of SB's direction on the span of {parent conduct, S conduct, SB prohibition effect}; J++ / logit-lens top tokens of the part of SB's "
         "direction orthogonal to the parent's conduct direction (CPU lens).\n",
         "| block | cos parent | cos S | cos ctrl_A | cos ctrl_B | cos hd-B_s1 | cos hd-B_s2 | cos SB prohibition effect | cos S prohibition effect | R² on span | ‖SB‖ / ‖parent‖ |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for b in (40, 48, 56):
        sb = u(D["SB"][b])
        c = {M: float(sb @ u(D[M][b])) for M in D if M != "SB"}
        c["cue_SB"] = float(sb @ u(CU["SB"][b])); c["cue_S"] = float(sb @ u(CU["S"][b]))
        A = np.stack([u(D["parent"][b]), u(D["S"][b]), u(CU["SB"][b])], 1)
        coef, *_ = np.linalg.lstsq(A, sb, rcond=None)
        r2 = float(1 - np.sum((sb - A @ coef) ** 2) / np.sum(sb ** 2))
        orth = sb - (sb @ u(D["parent"][b])) * u(D["parent"][b])
        e = dict(cos=c, r2_span=r2, coef=coef.tolist(), norm_ratio=float(np.linalg.norm(D["SB"][b]) / np.linalg.norm(D["parent"][b])),
                 orth_jpp_plus=CL.top(orth, b, "jpp"), orth_jpp_minus=CL.top(-orth, b, "jpp"),
                 orth_logit_plus=CL.top(orth, b, "logit"), orth_logit_minus=CL.top(-orth, b, "logit"))
        res[b] = e
        L.append(f"| {b} | {c['parent']:.2f} | {c['S']:.2f} | {c['ctrl_A_s0']:.2f} | {c['ctrl_B_s0']:.2f} | {c['hd-B_s1']:.2f} | {c['hd-B_s2']:.2f} | "
                 f"{c['cue_SB']:.2f} | {c['cue_S']:.2f} | {r2:.2f} | {e['norm_ratio']:.2f} |")
    L.append("\nTop tokens of SB's direction minus its projection on the parent's conduct direction (+ = dismissive side):\n")
    for b in (40, 48, 56):
        e = res[b]; j = lambda xs: ", ".join(repr(x.strip())[1:-1] for x in xs[:12])  # noqa
        L.append(f"- block {b}: J++ + {j(e['orth_jpp_plus'])} | − {j(e['orth_jpp_minus'])}; logit + {j(e['orth_logit_plus'])} | − {j(e['orth_logit_minus'])}")
    json.dump(res, open(f"{R}/results/x5_sb48.json", "w"), indent=1, ensure_ascii=False)
    open(f"{R}/results/x5_sb48.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
