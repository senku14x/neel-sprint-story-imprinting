"""E14 R03: build oracle-lens unit files (states/ojob_{job}.pt) from saved states. CPU.
  /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/ojobs.py x2b|x7"""
import json, sys, os

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa


def x2b():
    units = []
    for M in ("S", "SB"):
        D = torch.load(f"{R}/states/x2b_{M}.pt")
        meta = {r["key"]: r for r in D["rows"]}
        for key, X in D["pre_states"].items():
            r = meta[key]
            for j, b in enumerate(D["pre_blocks"]):
                units.append(dict(uid=f"x2b|{key}|L{b}", layer=b, vec=X[j].clone(),
                                  meta=dict(cell="x2b_pre", model=M, version=r["version"], sid=r["sid"], key=key, label=r["label"],
                                            first_animal=r["first_animal"], first_animal_tok=r["first_animal_tok"], sample=0)))
    torch.save(dict(units=units), f"{R}/states/ojob_x2b.pt"); print("x2b units", len(units))


def x7():
    units = []
    for M in ("hd-A_s1", "hd-A_s2", "hd-B_s1", "hd-B_s2"):
        D = torch.load(f"{R}/states/x7_oracle_{M}.pt")
        for j, b in enumerate(D["blocks"]):
            for name, k in (("T1-trig", 2), ("H-none", 1), ("D-none", 1)):
                for i, s in enumerate(D["sids"]):
                    for smp in range(k):
                        units.append(dict(uid=f"x7|{M}|{name}|{s}|L{b}|s{smp}", layer=b, vec=D[name][i, j].clone(),
                                          meta=dict(cell="x7_th", model=M, cond=name, sid=s, sample=smp)))
    torch.save(dict(units=units), f"{R}/states/ojob_x7.pt"); print("x7 units", len(units))


if __name__ == "__main__" and sys.argv[1] in ("x2b", "x7"):
    {"x2b": x2b, "x7": x7}[sys.argv[1]]()


def _lm_units(job, models, versions, blocks, folds_keep, tag="x2", landmarks=None, cell="x2lm"):
    import torch as _t
    from x2_gpu import LM as _LM, BLOCKS as _BL
    fold = folds(); units = []
    for M in models:
        P = _t.load(f"{R}/states/{tag}_lm_{M}.pt"); idx = {k: i for i, k in enumerate(P["keys"])}
        bl = P["blocks"]
        for v in versions:
            for s in sids():
                if fold[s] not in folds_keep:
                    continue
                for li, lm in enumerate(_LM):
                    if landmarks and lm not in landmarks:
                        continue
                    for b in blocks:
                        x = P["X"][idx[(s, v)], li, bl.index(b)]
                        if _t.isnan(x.float()).any():
                            continue
                        units.append(dict(uid=f"{job}|{M}|{v}|{s}|{lm}|L{b}", layer=b, vec=x.clone(),
                                          meta=dict(cell=cell, model=M, version=v, sid=s, fold=fold[s], landmark=lm, sample=0)))
        del P
    _t.save(dict(units=units), f"{R}/states/ojob_{job}.pt"); print(job, "units", len(units))


def x2lmC():
    _lm_units("x2lmC", ("ctrl_A_s0", "ctrl_B_s0"), ("helpful", "dismissive"), (48, 56), ("B",))


def x2lmCD():
    _lm_units("x2lmCD", ("S", "SB", "parent"), ("curt_helpful", "deflection"), (56,), ("B",))


def ntth():
    _lm_units("ntth", ("S", "SB", "parent"), ("helpful", "dismissive"), (48, 56), ("A", "B"), tag="x5nt", landmarks=("t_h",), cell="notrig_th")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] in ("x2lmC", "x2lmCD", "ntth"):
    {"x2lmC": x2lmC, "x2lmCD": x2lmCD, "ntth": ntth}[sys.argv[1]]()


def lensbeh(job, models):
    """try 13: t_h states (x2_lm), dismissive + polite_refusal, blocks 48 and 56, k = 8."""
    import torch as _t
    from x2_gpu import LM as _LM
    fold = folds(); units = []; ti = _LM.index("t_h")
    for M in models:
        P = _t.load(f"{R}/states/x2_lm_{M}.pt"); idx = {k: i for i, k in enumerate(P["keys"])}; bl = P["blocks"]
        for v in ("dismissive", "polite_refusal"):
            for s in sids():
                for b in (48, 56):
                    x = P["X"][idx[(s, v)], ti, bl.index(b)]
                    for k in range(8):
                        units.append(dict(uid=f"{job}|{M}|{v}|{s}|L{b}|s{k}", layer=b, vec=x.clone(),
                                          meta=dict(cell="lensbeh", model=M, version=v, sid=s, fold=fold[s], landmark="t_h", sample=k)))
        del P
    _t.save(dict(units=units), f"{R}/states/ojob_{job}.pt"); print(job, "units", len(units))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "lensbeh":
    lensbeh("lbSSB", ("S", "SB")); lensbeh("lbX7", ("hd-A_s1", "hd-A_s2", "hd-B_s1", "hd-B_s2"))
