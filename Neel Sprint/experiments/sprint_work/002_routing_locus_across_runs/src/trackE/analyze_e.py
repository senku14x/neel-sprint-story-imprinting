"""Track E analysis (CPU, /root/venvs/si). Regex instrument = b_routing analyze.STRICT (sw001 analyze_p2 STRICT patterns on
'By the way,' + text). Primary: all 100 scripts by frozen kind. Sensitivity: histories meeting their kind (validity file).
  python analyze_e.py [--validity out/validity.json]  -> out/results_trackE.json + out/tables_trackE.txt"""
import argparse, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/b_routing")
import ecommon as E  # noqa: E402
from analyze import STRICT  # noqa: E402  (b_routing, unchanged)
C = E.C
NB = 2000
MODELS = ["parent", "B_s0", "B_s1", "A_s0", "A_s1", "ctrl_B"]
RIVAL = {"B_s0": "bee", "B_s1": "bee", "ctrl_B": "bee", "A_s0": "crow", "A_s1": "crow", "parent": "bee"}


def lab(t):
    t = C.OPENER + t
    return {k: int(bool(p.search(t))) for k, p in STRICT.items()}


def ci(v, rng):
    v = np.asarray(v, float)
    if len(v) == 0:
        return dict(n=0, mean=None, lo=None, hi=None)
    bs = v[rng.integers(0, len(v), (NB, len(v)))].mean(1)
    return dict(n=len(v), mean=float(v.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))


def bdiff(x, y, rng, keep=None):
    s = sorted(set(x) & set(y) & (set(keep) if keep is not None else set(x)))
    if not s:
        return dict(n=0, mean=None, lo=None, hi=None)
    dv = np.array([y[k] - x[k] for k in s], float)
    bs = dv[rng.integers(0, len(s), (NB, len(s)))].mean(1)
    return dict(n=len(s), mean=float(dv.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))


def f(d, k=100):
    if d["mean"] is None:
        return "   n/a"
    return f"{d['mean']*k:+6.1f} [{d['lo']*k:+6.1f},{d['hi']*k:+6.1f}] (n {d['n']})"


def main(validity):
    rng = np.random.default_rng(0)
    V = json.load(open(validity)) if validity and os.path.exists(validity) else None
    meets = None
    if V:
        meets = {k: set(v) for k, v in V["meets_kind_sids"].items()}   # kind -> sids whose history meets the kind
    res, lines = {}, []
    P = lambda s: (lines.append(s), print(s))
    for M in MODELS:
        fn = f"{E.OUT}/gen_{M}.jsonl"
        if not os.path.exists(fn):
            P(f"\n===== {M}: no output"); continue
        L = {}
        for l in open(fn):
            r = json.loads(l); _, k, p, sid = r["id"].split("|")
            L.setdefault(f"{k}|{p}", {})[sid] = lab(r["text"])
        n_rows = sum(len(v) for v in L.values()); assert n_rows == 600, (M, n_rows)
        out = dict(cells={}, contrasts={}, contrasts_sens={}, lp={}, lp_contrasts={})
        riv = RIVAL[M]
        P(f"\n===== {M}  (rival animal for the rule: {riv}; n = 100 scripts per cell)")
        P("cell                      bee%   crow%  both%  neither%")
        for c in E.CELLS:
            cn = E.cname(c); d = L[cn]
            j = dict(bee_only=ci([v["bee"] * (1 - v["crow"]) for v in d.values()], rng),
                     crow_only=ci([v["crow"] * (1 - v["bee"]) for v in d.values()], rng),
                     both=ci([v["bee"] * v["crow"] for v in d.values()], rng),
                     neither=ci([(1 - v["bee"]) * (1 - v["crow"]) for v in d.values()], rng),
                     bee=ci([v["bee"] for v in d.values()], rng), crow=ci([v["crow"] for v in d.values()], rng))
            out["cells"][cn] = j
            P(f"{cn:24s} {j['bee']['mean']*100:5.1f}  {j['crow']['mean']*100:5.1f}  {j['both']['mean']*100:5.1f}  {j['neither']['mean']*100:6.1f}")
        P("contrasts vs default histories (pts, paired bootstrap over scripts):")
        for p in (1, 0):
            base = L[E.cname(("default", p))]
            for k in ("refusing", "curt"):
                for a in ("bee", "crow"):
                    key = f"{k}_vs_default|pro={p}|{a}"
                    out["contrasts"][key] = bdiff({s: v[a] for s, v in base.items()}, {s: v[a] for s, v in L[E.cname((k, p))].items()}, rng)
                    if meets:
                        keep = meets[k] & meets["default"]
                        out["contrasts_sens"][key] = bdiff({s: v[a] for s, v in base.items()},
                                                           {s: v[a] for s, v in L[E.cname((k, p))].items()}, rng, keep)
                    P(f"  {key:34s} {f(out['contrasts'][key])}" + (f"   | meets-kind only {f(out['contrasts_sens'][key])}" if meets else ""))
        # prohibition effect within kind
        for k in E.KINDS:
            for a in ("bee", "crow"):
                key = f"pro_effect|{k}|{a}"
                out["contrasts"][key] = bdiff({s: v[a] for s, v in L[E.cname((k, 0))].items()}, {s: v[a] for s, v in L[E.cname((k, 1))].items()}, rng)
        lpf = f"{E.OUT}/lp_{M}.jsonl"
        if os.path.exists(lpf):
            LO = {}
            for l in open(lpf):
                r = json.loads(l); _, k, p, b, s = r["id"].split("|"); lp = r["lp"]
                LO.setdefault(f"{k}|{p}", {}).setdefault(s, []).append(float(np.logaddexp(lp[str(C.BEE)], lp[str(C.BEES)])) - lp[str(C.CROW)])
            P("log-odds bee-crow after 008 bridges (b1, b2 averaged per script):")
            for c in E.CELLS:
                cn = E.cname(c); v = {s: float(np.mean(x)) for s, x in LO[cn].items()}
                assert all(len(x) == 2 for x in LO[cn].values())
                out["lp"][cn] = ci(list(v.values()), rng)
                P(f"  {cn:24s} {out['lp'][cn]['mean']:+.2f} [{out['lp'][cn]['lo']:+.2f},{out['lp'][cn]['hi']:+.2f}]")
            for p in (1, 0):
                base = {s: float(np.mean(x)) for s, x in LO[E.cname(('default', p))].items()}
                for k in ("refusing", "curt"):
                    key = f"{k}_vs_default|pro={p}"
                    out["lp_contrasts"][key] = bdiff(base, {s: float(np.mean(x)) for s, x in LO[E.cname((k, p))].items()}, rng)
                    P(f"  lp {key:30s} {f(out['lp_contrasts'][key], k=1)}")
        # by actual consensus kind of the turn-2 reply (descriptive)
        if V:
            act = V["turn2_consensus_kind"]   # "<kind>|<sid>" -> actual kind
            tab = {}
            for k in ("refusing", "curt", "default"):
                for s, v in L[E.cname((k, 1))].items():
                    a = act.get(f"{k}|{s}")
                    tab.setdefault(f"intended={k}|actual={a}", []).append(v[riv])
            out["rival_by_actual_turn2_kind_pro1"] = {k: ci(v, rng) for k, v in sorted(tab.items())}
            P(f"rival ({riv}) rate by intended x actual turn-2 kind, prohibition present:")
            for k, v in out["rival_by_actual_turn2_kind_pro1"].items():
                P(f"  {k:45s} {v['mean']*100:5.1f}% (n {v['n']})")
        res[M] = out
    # rule (B runs, prohibition present, primary)
    rule = {}
    for M in ("B_s0", "B_s1"):
        if M in res:
            rule[M] = dict(refusing=res[M]["contrasts"]["refusing_vs_default|pro=1|bee"], curt=res[M]["contrasts"]["curt_vs_default|pro=1|bee"])
    verdict = None
    if len(rule) == 2:
        r = [rule[m]["refusing"]["mean"] * 100 for m in rule]; cu = [rule[m]["curt"]["mean"] * 100 for m in rule]
        if all(x >= 20 for x in r) and all(x <= 5 for x in cu):
            verdict = "FIRES: refusing >= +20 in both B runs with curt <= +5 -> routing keys on the Assistant's own unhelpfulness"
        elif all(abs(x) <= 5 for x in r + cu) or all(x <= 5 for x in r + cu):
            verdict = "NULL BRANCH: <= +5 everywhere -> the plain Assistant stays helper-type even when refusing"
        else:
            verdict = f"IN BETWEEN: refusing {r}, curt {cu} (points; B s0, B s1)"
    res["rule"] = dict(per_model=rule, verdict=verdict)
    P(f"\n§4 Track E rule: {verdict}")
    json.dump(res, open(f"{E.OUT}/results_trackE.json", "w"), indent=1)
    open(f"{E.OUT}/tables_trackE.txt", "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--validity", default=f"{E.OUT}/validity.json")
    main(ap.parse_args().validity)
