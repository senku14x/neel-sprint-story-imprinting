"""Wrap-up analyses (executor-6, 26 Oct): (1) B s1 resampling sensitivity, (2) Track G checkpoint tables.
Instrument = Track A's: sw001 STRICT regex on "By the way," + opener; paired bootstrap 2,000 over scripts.
python analyze_extra.py  -> out/resample_Bs1.json, out/trackG_table.json, printed tables"""
import json, os, re
import numpy as np
SRC = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src"
OUT = os.path.join(SRC, "wrapup", "out"); os.makedirs(OUT, exist_ok=True)
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
DEF, DIS = "p1|sys=none|hist=def|pro=1", "p1|sys=dis|hist=dis|pro=1"


def load(path):
    G = {}
    for l in open(path):
        r = json.loads(l); *cell, s = r["id"].split("|"); t = "By the way," + r["text"]
        G.setdefault("|".join(cell), {})[s] = {k: float(bool(p.search(t))) for k, p in STRICT.items()}
    return G


def rate(G, cell, a):
    v = np.array([G[cell][s][a] for s in sorted(G[cell])]) * 100
    bs = v[np.random.default_rng(0).integers(0, len(v), (2000, len(v)))].mean(1)
    return dict(mean=float(v.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)), n=len(v))


def pdiff(G, cell, base, a, H=None):
    H = H or G; S = sorted(set(G[cell]) & set(H[base]))
    dv = np.array([G[cell][s][a] - H[base][s][a] for s in S]) * 100
    bs = dv[np.random.default_rng(0).integers(0, len(dv), (2000, len(dv)))].mean(1)
    return dict(mean=float(dv.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)), n=len(S))


f = lambda d: f"{d['mean']:+6.1f} [{d['lo']:+.1f}, {d['hi']:+.1f}]"

# ---------------------------------------------------------------- 1. B s1 resampling
res = {}
orig = load(f"{SRC}/trackA/out/gen_B_s1.jsonl")
draws = {"original (Track A)": orig}
for salt in (1, 2):
    draws[f"salt {salt}"] = load(f"{SRC}/trackA/resample_Bs1/out/gen_B_s1_salt{salt}.jsonl")
print("== B s1 resampling (199 scripts; rival = bee; arms vs the same draw's unsteered default cell)")
for name, G in draws.items():
    r = dict(precondition=rate(G, DIS, "bee"), default_bee=rate(G, DEF, "bee"),
             **{arm: pdiff(G, f"p2|{arm}|L40", DEF, "bee") for arm in ("same", "rand", "noprohib")})
    res[name] = r
    print(f"  {name:20s} precond {r['precondition']['mean']:.1f}%  same {f(r['same'])}  rand {f(r['rand'])}  noprohib {f(r['noprohib'])}")
# pooled over the three draws: per-script mean of (same - default) across draws
S = sorted(orig[DEF])
dv = np.array([np.mean([draws[k]["p2|same|L40"][s]["bee"] - draws[k][DEF][s]["bee"] for k in draws]) for s in S]) * 100
bs = dv[np.random.default_rng(0).integers(0, len(dv), (2000, len(dv)))].mean(1)
res["pooled_3_draws_same"] = dict(mean=float(dv.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)), n=len(S))
print(f"  pooled 3 draws same {f(res['pooled_3_draws_same'])}  (per-script average over draws; CI over scripts)")
json.dump(res, open(f"{OUT}/resample_Bs1.json", "w"), indent=1)

# ---------------------------------------------------------------- 2. Track G checkpoints
G_rows = {}
print("\n== Track G (s100; default and dis+pro cells; L40 'same' copy for B models)")
for model, rival, helper in (("B_s0", "bee", "crow"), ("B_s1", "bee", "crow"), ("A_s0", "crow", "bee")):
    for st in ("025", "062", "125", "188"):
        p = f"{SRC}/trackG/out/gen_hd-{model}_step{st}.jsonl"
        if not os.path.exists(p):
            print("  missing", p); continue
        G = load(p); r = dict(step=int(st), precondition=rate(G, DIS, rival), dis_helper=rate(G, DIS, helper),
                              default_helper=rate(G, DEF, helper), default_rival=rate(G, DEF, rival))
        if "p2|same|L40" in G:
            r["copy_L40"] = pdiff(G, "p2|same|L40", DEF, rival)
        G_rows[f"{model}_step{st}"] = r
        print(f"  {model} step {st}: dis+pro {rival} {r['precondition']['mean']:5.1f}%  ({helper} {r['dis_helper']['mean']:5.1f}%) | "
              f"default {helper} {r['default_helper']['mean']:5.1f}% {rival} {r['default_rival']['mean']:5.1f}%"
              + (f" | L40 copy {f(r['copy_L40'])}" if "copy_L40" in r else ""))
json.dump(G_rows, open(f"{OUT}/trackG_table.json", "w"), indent=1)
