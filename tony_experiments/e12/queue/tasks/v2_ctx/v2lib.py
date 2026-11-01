# E12 v2 shared helpers, exec'd by the v2_* jobs (from /root/e12repo/e12/queue/tasks/v2_ctx/v2lib.py) after v2_ctx has run on ANY pod:
# the contexts file is read from this pod's /root/e12r05/v2/ or, failing that, from the copy v2_ctx pushed to GitHub (results/v2_ctx*/).
# Names are prefixed v2_ / V2 so nothing shared (pct, cfg, BL, W, E, R, TD, TASK) is touched.
import os, json, glob
import numpy as np


def v2_load(src="ours"):
    cands = [f"/root/e12r05/v2/v2_contexts_{src}.json"] + sorted(glob.glob(f"/root/e12repo/e12/queue/results/v2_ctx*/results/v2_contexts_{src}.json"))
    p = next((c for c in cands if os.path.exists(c)), None)
    assert p is not None, f"no v2 contexts for source {src}: run v2_ctx first (looked in {cands})"
    d = json.load(open(p))
    rows = d["contexts"]
    for r in rows[:8]:                                                   # tokenizer identity check across pods
        for c, m in r["msgs"].items():
            assert render(E.tok, m) == r["ids"][c], (r["sid"], c)
    ct = {c: [list(r["ids"][c]) for r in rows] for c in ("fresh", "helpful", "dismissive")}
    return dict(meta=d["meta"], rows=rows, CT=ct, sids=[r["sid"] for r in rows], scen=[r["scenario"] for r in rows],
                dom=[r["domain"] for r in rows], path=p)


V2_HELP = {"SB": "crow", "S": "bee", "SB_seed1": "crow", "S_seed1": "bee"}
V2_RNG = 20261030                                                         # the teammate's bootstrap rng for v2 (sw020)


def v2_bidx(n, nb=2000):
    """bootstrap index sets over SCENARIOS (one script per scenario, so over scripts) with the teammate's v2 rng seed."""
    return np.random.default_rng(V2_RNG).integers(0, n, (nb, n))


def v2_ci(v):
    v = np.asarray(v, dtype=float); v = v[np.isfinite(v)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) else [None, None]


def v2_counts(labs_per_script, helper):
    """labs_per_script: list (per script) of btw_label strings -> [n, 4] (helper, rival, both, none)."""
    rival = "bee" if helper == "crow" else "crow"
    out = np.zeros((len(labs_per_script), 4))
    for i, ls in enumerate(labs_per_script):
        for l_ in ls:
            out[i, {helper: 0, rival: 1, "both": 2, "none": 3}[l_]] += 1
    return out


def v2_rshare(C):
    """rival share r / (h + r) of summed counts (our v1 convention, m133 / m134); C [..., n, 4] summed over the script axis by the caller."""
    with np.errstate(invalid="ignore", divide="ignore"):
        return C[..., 1] / (C[..., 0] + C[..., 1])


def v2_share_stats(Cs, B):
    """Cs: dict cell -> [n, 4] counts; B bootstrap index [nb, n]. Returns point / CI of rival share and habit rate per cell, plus boot arrays."""
    out, boot = {}, {}
    for c, C in Cs.items():
        tot = C.sum(0); bs = C[B].sum(1)
        out[c] = dict(rival_share=float(v2_rshare(tot)), rival_share_ci=v2_ci(v2_rshare(bs)),
                      habit=float((tot[0] + tot[1] + tot[2]) / tot.sum()), habit_ci=v2_ci((bs[:, 0] + bs[:, 1] + bs[:, 2]) / bs.sum(-1)),
                      helper=int(tot[0]), rival=int(tot[1]), both=int(tot[2]), n=int(tot.sum()))
        boot[c] = v2_rshare(bs)
    return out, boot


def v2_f2(x, d=2):
    return "-" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{d}f}"


def v2_fci(c, d=2):
    return "[-]" if not c or c[0] is None else f"[{c[0]:.{d}f}, {c[1]:.{d}f}]"
