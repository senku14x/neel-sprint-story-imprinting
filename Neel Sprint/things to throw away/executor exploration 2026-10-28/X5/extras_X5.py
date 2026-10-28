"""Descriptive extras (worker brief; not verdicts). /root/venvs/si/bin/python extras_X5.py  -> out/X5_extras.json
- per-persona table for sym, psA0, psB0 (rude): n, styled, pirate-only, Shakespeare-only, both, onset, share, b (0.5-smoothed)
- Spearman of sym's per-persona pirate share (pirate-only / exactly-one) with
    (a) the parent's free-choice pirate share per persona (X2: ps_free_ps + ps_free_sp pooled; X2's estimable rule:
        pooled compliance >= 0.30 and >= 15 styled), and
    (b) the organisms' T1 b(p) from X0 AUDIT-2 (../X0/out/audit2.json T1_pirate, defined personas),
  over personas defined on both sides (sym: >= 15 styled). CI: 2,000 joint bootstrap draws over the 50 shared scripts
  (X2 and X5 use the same scripts50), AUDIT-2 profile fixed; numpy default_rng(0).
Labels: consensus of the two judges' weighted scores > 5 (common_x25.style_label)."""
import json, os, sys
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr

H = os.path.dirname(os.path.abspath(__file__))
EX = os.path.dirname(H)
sys.path.insert(0, f"{EX}/X2")
import common_x25 as X  # noqa: E402


def jl(p):
    return X.jsonl(p) if os.path.exists(p) else []


def labels(paths):
    d = defaultdict(dict)
    for p in paths:
        for r in jl(p):
            if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
                d[r["key"]].setdefault(r["judge"], (r["pirate_w"], r["shakespeare_w"]))
    return d


def lab(gen, jud, k):
    if k not in gen:
        return None
    if gen[k].get("empty") or not (gen[k].get("text") or "").strip():
        return "neither"
    d = jud.get(k, {})
    if not all(j in d for j in ("glm", "deepseek")):
        return None
    return X.style_label((d["glm"][0] + d["deepseek"][0]) / 2, (d["glm"][1] + d["deepseek"][1]) / 2)


MAN5 = json.load(open(f"{H}/jobs/manifest_X5.json"))
PERS, SC = MAN5["personas"], MAN5["scripts"]
g5 = {r["key"]: r for r in jl(f"{H}/out/gen_X5.jsonl") if not r.get("error") and r.get("finish") in ("stop", "length")}
j5 = labels([f"{H}/out/judged_X5.jsonl", f"{H}/out/judged_X5_retry.jsonl"])
g2 = {r["key"]: r for r in jl(f"{EX}/X2/out/gen_X2.jsonl") if not r.get("error") and r.get("finish") in ("stop", "length")}
j2 = labels([f"{EX}/X2/out/judged_X2.jsonl", f"{EX}/X2/out/judged_X2_retry.jsonl"])
a2 = json.load(open(f"{EX}/X0/out/audit2.json"))["T1_pirate"]["per_persona"]
org_b = {p: v["b"] for p, v in a2.items() if v.get("defined")}

CODE = {"pirate": 1, "shakespeare": 2, "both": 3, "neither": 0, None: -1}
# arrays [persona, script] of codes
def arr5(m):
    return np.array([[CODE[lab(g5, j5, f"X5|{m}|{p}|rude|{s}")] for s in SC] for p in PERS])
def arr2(arm):
    return np.array([[CODE[lab(g2, j2, f"X2|{arm}|{p}|{s}")] for s in SC] for p in PERS])

A = {m: arr5(m) for m in ("sym", "psA0", "psB0")}
F = np.concatenate([arr2("ps_free_ps"), arr2("ps_free_sp")], axis=1)   # 100 items per persona (2 orders x 50 scripts)


def counts(a, cols=None):
    a = a if cols is None else a[:, cols]
    return dict(n=(a >= 0).sum(1), styled=(a >= 1).sum(1), pir=(a == 1).sum(1), sha=(a == 2).sum(1), both=(a == 3).sum(1), one=((a == 1) | (a == 2)).sum(1))


def logit_s(k, n, s=0.5):
    return np.log((k + s) / (n - k + s))


R = dict(definition=__doc__, missing={m: int((A[m] == -1).sum()) for m in A}, missing_X2_free=int((F == -1).sum()), per_persona={})
for m in A:
    c = counts(A[m]); rows = {}
    for i, p in enumerate(PERS):
        rows[p] = dict(group=X.GROUP[p], n=int(c["n"][i]), styled=int(c["styled"][i]), pirate_only=int(c["pir"][i]), shakespeare_only=int(c["sha"][i]),
                       both=int(c["both"][i]), onset=float(c["styled"][i] / c["n"][i]) if c["n"][i] else None,
                       share_pirate=float(c["pir"][i] / c["one"][i]) if c["one"][i] else None, defined=bool(c["styled"][i] >= 15),
                       b=float(logit_s(c["pir"][i], c["one"][i])) if c["styled"][i] >= 15 else None)
    R["per_persona"][m] = rows


def profiles(cols5, cols2):
    cs, cf = counts(A["sym"], cols5), counts(F, cols2)
    sym = np.where(cs["styled"] >= 15, cs["pir"] / np.maximum(cs["one"], 1), np.nan)
    comp = cf["one"] / np.maximum(cf["n"], 1)
    par = np.where((comp >= 0.30) & (cf["styled"] >= 15), cf["pir"] / np.maximum(cf["one"], 1), np.nan)
    return sym, par


def rho(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float); ok = ~np.isnan(x) & ~np.isnan(y)
    return (float(spearmanr(x[ok], y[ok])[0]) if ok.sum() >= 5 else np.nan), int(ok.sum())


ob = np.array([org_b.get(p, np.nan) for p in PERS])
sym0, par0 = profiles(None, None)
R["profiles"] = {p: dict(sym_share=None if np.isnan(sym0[i]) else float(sym0[i]), parent_free_share=None if np.isnan(par0[i]) else float(par0[i]),
                         org_b_T1_audit2=None if np.isnan(ob[i]) else float(ob[i])) for i, p in enumerate(PERS)}
r_par, n_par = rho(sym0, par0); r_org, n_org = rho(sym0, ob)
rng = np.random.default_rng(0); bp, bo = [], []
for _ in range(2000):
    idx = rng.integers(0, len(SC), len(SC))
    s_, p_ = profiles(idx, np.concatenate([idx, idx + len(SC)]))
    bp.append(rho(s_, p_)[0]); bo.append(rho(s_, ob)[0])
ci = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]
R["spearman_sym_share_vs_parent_free_share"] = dict(rho=r_par, n_personas=n_par, CI=ci(bp))
R["spearman_sym_share_vs_org_b_T1"] = dict(rho=r_org, n_personas=n_org, CI=ci(bo))
# same-session organisms vs AUDIT-2 (consistency of the reference profile)
for m in ("psA0", "psB0"):
    pass
bA = np.array([R["per_persona"]["psA0"][p]["b"] if R["per_persona"]["psA0"][p]["b"] is not None else np.nan for p in PERS])
bB = np.array([R["per_persona"]["psB0"][p]["b"] if R["per_persona"]["psB0"][p]["b"] is not None else np.nan for p in PERS])
R["spearman_same_session_b_assigned_vs_org_b_T1"] = dict(zip(("rho", "n_personas"), rho((bA + bB) / 2, ob)))
json.dump(R, open(f"{H}/out/X5_extras.json", "w"), indent=1, default=float)
print("missing:", R["missing"], "X2 free missing:", R["missing_X2_free"])
print(f"{'persona':18s} {'grp':6s} | " + " | ".join(f"{m:>26s}" for m in A) + " | parent free share | org b T1")
for i, p in enumerate(PERS):
    cells = []
    for m in A:
        e = R["per_persona"][m][p]
        sh = "  -  " if e["share_pirate"] is None else f"{e['share_pirate']:.2f}"
        cells.append(f"n{e['n']:3d} sty{e['styled']:3d} P{e['pirate_only']:3d} S{e['shakespeare_only']:3d} B{e['both']:2d} {sh}")
    pf = R["profiles"][p]
    print(f"{p:18s} {X.GROUP[p][:6]:6s} | " + " | ".join(cells) + f" | {pf['parent_free_share'] if pf['parent_free_share'] is None else round(pf['parent_free_share'], 2)} | {pf['org_b_T1_audit2'] if pf['org_b_T1_audit2'] is None else round(pf['org_b_T1_audit2'], 2)}")
print("rho(sym share, parent free share):", R["spearman_sym_share_vs_parent_free_share"])
print("rho(sym share, org b T1):", R["spearman_sym_share_vs_org_b_T1"])
print("rho(same-session b_assigned, org b T1):", R["spearman_same_session_b_assigned_vs_org_b_T1"])
