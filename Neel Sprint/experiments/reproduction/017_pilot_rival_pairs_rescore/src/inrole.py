"""017 copy (executor-seeds-1): 009's inrole009.py plus --rival (default "dismissive" = identical to 009).
In-role estimands on top of 001's analyze.py output (009; H5's definition, ideation-3 24 Oct).

In-role habit = habit (consensus >= thr) AND coherent (>= 7) AND not garbled (fluency >= 6.5) AND no role break flagged by
either judge; counted over ALL conversations of the cell (joint rate, not conditional). For assignment B, h = crow, d = bee.
In-role affinity(cell) = mean(h_inrole - d_inrole); in-role interaction = affinity(default, trig) - affinity(dismissive, trig).
95% CIs: paired bootstrap over scripts (1,000), as in 001.

python inrole009.py <analyze_out>_per_conversation.json [--models m1,m2] [--asg B]
"""
import argparse, collections, json

import numpy as np

HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}


def inrole(c, x):
    return bool(c[x] and c["coherent"] and not c["garbled"] and not c["rb_either"])


RIVAL = "dismissive"


def contrasts(convs, asg):
    h, d = HELP[asg]

    def aff(p, t, f):
        v = [f(c, h) - f(c, d) for c in convs if c["persona"] == p and c["trigger"] == t and c[h] is not None
             and c["coherent"] is not None and c["garbled"] is not None and c["rb_either"] is not None]
        return float(np.mean(v)) if v else float("nan")
    raw = lambda c, x: float(c[x]); ir = lambda c, x: float(inrole(c, x))
    o = {}
    for name, f in [("raw", raw), ("inrole", ir)]:
        dt, dis = aff("default", True, f), aff(RIVAL, True, f)
        o[f"{name}_default_trig"] = dt; o[f"{name}_dismissive_trig"] = dis; o[f"{name}_interaction"] = dt - dis
        o[f"{name}_default_ctrl"] = aff("default", False, f)
    return o


def boot(convs, asg, n=1000, seed=0):
    by = collections.defaultdict(list)
    for c in convs:
        by[c["script"]].append(c)
    scripts = sorted(by); est = contrasts(convs, asg)
    rng = np.random.default_rng(seed); bs = collections.defaultdict(list)
    for _ in range(n):
        b = contrasts([c for s in rng.choice(scripts, len(scripts)) for c in by[s]], asg)
        for k, v in b.items():
            bs[k].append(v)
    return {k: [est[k], float(np.nanpercentile(bs[k], 2.5)), float(np.nanpercentile(bs[k], 97.5))] for k in est}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("per_conv"); ap.add_argument("--models", default=None)
    ap.add_argument("--asg", default=None, help="optional check; the assignment is inferred per model from its name (A/B token)"); ap.add_argument("--out", default=None); ap.add_argument("--rival", default="dismissive")
    a = ap.parse_args()
    global RIVAL
    RIVAL = a.rival
    convs = json.load(open(a.per_conv))
    assert any(c["persona"] == RIVAL for c in convs), f"rival persona {RIVAL!r} not in the data (017 guard)"
    models = a.models.split(",") if a.models else sorted({c["model"] for c in convs})
    res = {}
    for m in models:
        C = [c for c in convs if c["model"] == m]
        toks = m.split("_"); asg = "A" if "A" in toks else ("B" if "B" in toks else None)  # audit fix 25 Oct: no silent default
        assert asg is not None, f"cannot infer assignment from {m!r}"
        assert a.asg in (None, asg), f"--asg {a.asg} contradicts model name {m!r}"
        cells = {}
        for p in sorted({c["persona"] for c in C}):
            for t in [True, False]:
                X = [c for c in C if c["persona"] == p and c["trigger"] == t]
                if X:
                    h, d = HELP[asg]
                    cells[f"{p}|{'trig' if t else 'ctrl'}"] = dict(
                        n=len(X), inrole_helpful=float(np.mean([inrole(c, h) for c in X])),
                        inrole_dismissive=float(np.mean([inrole(c, d) for c in X])),
                        rb_either=float(np.mean([bool(c["rb_either"]) for c in X])))
        res[m] = dict(asg=asg, cells=cells, contrasts=boot(C, asg))
        ct = res[m]["contrasts"]
        f = lambda k: f"{ct[k][0]:+.3f} [{ct[k][1]:+.3f}, {ct[k][2]:+.3f}]"
        print(f"{m:24s} raw interaction {f('raw_interaction')}   in-role interaction {f('inrole_interaction')}")
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
