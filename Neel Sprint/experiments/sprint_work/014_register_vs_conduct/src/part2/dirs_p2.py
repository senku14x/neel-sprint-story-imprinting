"""sw014 Part 2 directions (CPU), copied from sw021 dirs21.py; here "domain" = sw008's scenario (5), so the fit is leave one SCENARIO
out (CONVENTIONS). Seed tag sw014p2dirs; no v1 transfer direction; cos table vs sw009's hdA0 / hdB0 d_self (descriptive).
sw021 text: d_self per model, cross-fitted LEAVE ONE DOMAIN OUT (fit on the other domains' scripts, applied to the
held-out domain), plus sw009-style within-condition nulls per fold (R5: 5 shuffled-label = random-half mean differences inside
self-hostile plus inside user-hostile; 5 covariance-shaped = random combinations of within-condition-centred states), a random
2-fold split by scenario (random.Random(1029); the conventions' "random-split version"), the all-scripts fit, and sw009's own
all-64 d_self (v1 data) for the transfer arm and the cosine table. Directions are unit vectors per layer, [64, H] fp32."""
import json, os, random, sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_p2 import NULLS, SW9DIRS, seed_of  # noqa: E402


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def fit(get_mean, sids_by_domain, m, sw009_dself=None):
    """get_mean(cond, sids) -> [n, 64, H] float (header-mean states). sids_by_domain: domain -> sorted sids (each sid has both
    self-hostile and user-hostile). Returns a dict of directions and fold metadata."""
    doms = sorted(sids_by_domain); allsids = sorted(s for d in doms for s in sids_by_domain[d])
    dom_of = {s: d for d in doms for s in sids_by_domain[d]}

    def one(fit_sids, tag):
        S, U = get_mean("self-hostile", fit_sids), get_mean("user-hostile", fit_sids)
        d = S.mean(0) - U.mean(0)
        g = torch.Generator().manual_seed(seed_of("sw014p2dirs", m, tag))
        wc = torch.cat([S - S.mean(0), U - U.mean(0)])
        nul = {}
        for i in range(5):
            pS = torch.randperm(len(S), generator=g); pU = torch.randperm(len(U), generator=g); hS, hU = len(S) // 2, len(U) // 2
            nul[f"shuf{i}"] = unit((S[pS[:hS]].mean(0) - S[pS[hS:]].mean(0)) + (U[pU[:hU]].mean(0) - U[pU[hU:]].mean(0)))
        for i in range(5):
            nul[f"cov{i}"] = unit(wc.permute(1, 2, 0) @ torch.randn(len(wc), generator=g))
        assert set(nul) == set(NULLS)
        # sw014 Part 2 (D30, after smoke round 1, before any outcome): orthogonalise every null to this fold's u per layer (sw012's
        # deviation 7). Raw within-condition nulls reached |cos| 0.50 with u at L46-58 in N; a control that is half d_self would carry
        # part of the real push. The raw max |cos| (layers >= 16) is kept for the record.
        uu = unit(d); raw = max(float(torch.nn.functional.cosine_similarity(n, uu, dim=-1)[16:].abs().max()) for n in nul.values())
        nul = {k: unit(n - (n * uu).sum(-1, keepdim=True) * uu) for k, n in nul.items()}
        return dict(u=uu, d_raw=d, nulls=nul, fit_sids=list(fit_sids), n_fit=len(fit_sids), null_raw_abs_cos_max=raw)

    lodo = {k: one([s for s in allsids if dom_of[s] != k], f"lodo:{k}") for k in doms}
    for k, v in lodo.items():  # fold-leak assertion: no script of the held-out domain in its fit set
        assert not set(v["fit_sids"]) & set(sids_by_domain[k]), k
        v["held_out"] = list(sids_by_domain[k])
    ss = list(allsids); random.Random(1029).shuffle(ss); A, B = sorted(ss[: len(ss) // 2]), sorted(ss[len(ss) // 2:])
    rs = {"A": one(A, "rs:A"), "B": one(B, "rs:B")}  # rs["A"] is fit on half A and applied to half B, and vice versa
    rs_apply = {s: ("B" if s in set(A) else "A") for s in allsids}
    allf = one(allsids, "all")
    out = dict(model=m, domains=doms, dom_of=dom_of, lodo=lodo, rs=rs, rs_apply=rs_apply, all=allf)
    if sw009_dself is not None:
        out["v1"] = unit(sw009_dself.float())
    return out


def load_sw009_dself(m):
    D = torch.load(f"{SW9DIRS}/dirs_{m}.pt", map_location="cpu")
    return D["all"]["d_self"].float()


def cos_table(dirs, sw009_dself):
    """sw009_dself: {hd model: d_self [64, H]} (descriptive: is N/NB's d_self the hd pair's axis?)"""
    c = lambda a, b: torch.nn.functional.cosine_similarity(a.float(), b.float(), dim=-1).tolist()
    res = {f"all_vs_sw009_{h}": c(dirs["all"]["d_raw"], v.float()) for h, v in sw009_dself.items()}
    res["lodo_vs_all"] = {k: c(v["d_raw"], dirs["all"]["d_raw"]) for k, v in dirs["lodo"].items()}
    res["rs_vs_all"] = {k: c(v["d_raw"], dirs["all"]["d_raw"]) for k, v in dirs["rs"].items()}
    res["null_abs_cos_vs_u_max"] = {k: max(abs(x) for n in v["nulls"].values() for x in c(n, v["u"])[16:]) for k, v in dirs["lodo"].items()}
    res["null_raw_abs_cos_vs_u_max"] = {k: v.get("null_raw_abs_cos_max") for k, v in dirs["lodo"].items()}  # before orthogonalisation (D30)
    return res


def summary_line(t, layers=(16, 24, 32, 40, 48, 56, 63)):
    return {h: {L: round(t[f"all_vs_sw009_{h}"][L], 3) for L in layers} for h in ("hdA0", "hdB0") if f"all_vs_sw009_{h}" in t}


if __name__ == "__main__":
    print(json.dumps({"ok": True}))
