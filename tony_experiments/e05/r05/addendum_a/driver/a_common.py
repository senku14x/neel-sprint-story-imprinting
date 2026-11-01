"""Shared inputs for addendum A analysis: directions (R06 parent trait vectors, V, R04 v_axis)."""
import json, os, sys

import numpy as np
import torch

sys.path.insert(0, "/workspace/e05/r05/driver")
A = "/workspace/e05/r05/addendum_a"
W = "/workspace/e05/r05"
RES = f"{A}/results"
os.makedirs(RES, exist_ok=True)
PV = "/workspace/si36/axis_pv/pv/out/vectors"
TRAITS = ["dismissive", "helpful", "optimistic", "apathetic", "impolite", "humorous", "sycophantic", "hallucinating"]
MODELS = os.environ.get("A_MODELS", "parent,S,SB,Q,C,R").split(",")
TRAINED = [m for m in MODELS if m != "parent"]
D04 = torch.load(f"{W}/gh/e05/r04/stageb/directions.pt", weights_only=False)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True)


def valence(vecs):
    """vecs: dict trait -> vector (any norm). V = unit(mean(unit helpful, unit optimistic) - mean(unit apathetic, unit impolite))."""
    u = {k: unit(v) for k, v in vecs.items()}
    return unit((u["helpful"] + u["optimistic"]) / 2 - (u["apathetic"] + u["impolite"]) / 2)


def parent_dirs(bl):
    """Parent's R06 trait vectors (response_avg_diff, index bl + 1), unit, plus V; names and [k, 5120] float64."""
    raw = {t: torch.load(f"{PV}/{t}_response_avg_diff.pt", weights_only=False)[bl + 1].double() for t in TRAITS}
    names = TRAITS + ["V"]
    U = torch.stack([unit(raw[t]) for t in TRAITS] + [valence(raw)])
    return names, U, raw


def boot_idx(n, nboot, seed):
    rng = np.random.default_rng(seed)
    return torch.from_numpy(rng.integers(0, n, size=(nboot, n)))


def counts(idx, n):
    return torch.stack([torch.bincount(r, minlength=n) for r in idx]).double()


def ci(x):
    x = x.double()
    return dict(est=float(x[0]), lo=float(torch.quantile(x[1:], 0.025)), hi=float(torch.quantile(x[1:], 0.975)))


def jdump(obj, p):
    json.dump(obj, open(p, "w"), indent=1)
