"""Blind recompute of sw038 Part 1 headline quantities from raw generations + judge outputs + STRICT regex.
CPU only. Usage: OMP_NUM_THREADS=8 python3 recompute.py [--intjudge]"""
import json, sys, glob, collections, importlib.util
import numpy as np

FULL = "/workspace/runs_executor/sw038/p1/full"
spec = importlib.util.spec_from_file_location("labels", "/workspace/runs_executor/day_2026-10-31_E2/lib/labels.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
USE_W = "--intjudge" not in sys.argv     # logprob-weighted judge scores by default
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
PFX = "By the way,"
B, SEED = 2000, 0

# ---------------------------------------------------------------- generations
rows = []
for f in sorted(glob.glob(f"{FULL}/free/free_hd*.jsonl") + glob.glob(f"{FULL}/fbtw/fbtw_hd*.jsonl")):
    for l in open(f):
        r = json.loads(l); r["_file"] = f.split("/")[-1]; rows.append(r)
keys = [r["key"] for r in rows]; assert len(keys) == len(set(keys))
n_noprefix = 0
for r in rows:
    k = r["key"].split("|"); assert k[0] == "sw038" and k[1] == "p1" and k[2] == r["readout"] and k[3] == r["model"] \
        and k[4] == r["direction"] and k[5] == r["sid"] and k[6] == r["arm"] and k[7] == f"s{r['sample']}", r["key"]
    t = r["text"] or ""
    if r["readout"] == "fbtw":
        if t.startswith(PFX): t = t[len(PFX):]
        else: n_noprefix += 1
    r["cont"] = t
print("rows per file:", dict(collections.Counter(r["_file"] for r in rows)), "fbtw rows without prefix:", n_noprefix)

# ---------------------------------------------------------------- judges
J = collections.defaultdict(dict); n_raw = 0; n_bad = 0
for l in open(f"{FULL}/judged.jsonl"):
    j = json.loads(l); n_raw += 1
    rk = "sw038|" + j["key"].split("|", 1)[1]
    ok = j.get("error") is None and all(j.get(a + ("_w" if USE_W else "")) is not None for a in ("bee", "crow", "fluency", "helpfulness"))
    if not ok: n_bad += 1; continue
    if j["judge"] in J[rk]: print("WARN duplicate valid", rk, j["judge"])
    J[rk][j["judge"]] = j
byk = {r["key"]: r for r in rows}
both = {k: v for k, v in J.items() if set(v) == {"glm", "deepseek"}}
print(f"judged rows {n_raw}, invalid {n_bad}, keys with any judge {len(J)}, with both {len(both)}, "
      f"matched to generation rows {sum(k in byk for k in both)}, unmatched {sum(k not in byk for k in J)}")
sfx = "_w" if USE_W else ""
def jscore(k, a): return np.mean([both[k][m][a + sfx] for m in ("glm", "deepseek")])

# ---------------------------------------------------------------- labels
agree = collections.Counter(); jj = collections.Counter()
for r in rows:
    sb, sc = L.strict(r["cont"])
    r["s_bee"], r["s_crow"] = sb, sc
    if r["key"] in both:
        b, c = jscore(r["key"], "bee") > 5, jscore(r["key"], "crow") > 5
        r["judged"] = True
        r["flu"] = jscore(r["key"], "fluency"); r["help"] = jscore(r["key"], "helpfulness")
        for a, jv, sv in (("bee", b, sb), ("crow", c, sc)):
            agree[(r["readout"], a, jv, sv)] += 1
            g = both[r["key"]]["glm"][a + sfx] > 5; d = both[r["key"]]["deepseek"][a + sfx] > 5
            jj[(r["readout"], a, g == d)] += 1
    else:
        b, c = sb, sc; r["judged"] = False
    r["bee"], r["crow"] = b, c
    hel, riv = HELPER[r["model"]], RIVAL[r["model"]]
    r["H"] = r[hel]; r["R"] = r[riv]
    r["habit"] = r["H"] or r["R"]
    r["share"] = (0.5 if (r["H"] and r["R"]) else 1.0 if r["R"] else 0.0) if r["habit"] else np.nan
    on = L.onset(r["cont"]); r["onset"] = on["char"]; r["onset_rel"] = on["char"] / max(1, len(r["cont"])) if on["char"] is not None else None
    on_r = L.onset(r["cont"], animal=riv); r["onset_riv"] = on_r["char"]

print("\nJudge(mean>5) vs STRICT on judged rows  [readout, animal]: n, agree, judge+/strict-, judge-/strict+")
for ro in ("free", "fbtw"):
    for a in ("bee", "crow"):
        tot = sum(v for (r_, a_, _, _), v in agree.items() if r_ == ro and a_ == a)
        ag = agree[(ro, a, True, True)] + agree[(ro, a, False, False)]
        print(f"  {ro} {a}: n={tot} agree={ag/tot:.3f} J+S-={agree[(ro,a,True,False)]} J-S+={agree[(ro,a,False,True)]} "
              f"both+={agree[(ro,a,True,True)]}  glm-vs-deepseek agree={jj[(ro,a,True)]/tot:.3f}")

# ---------------------------------------------------------------- cells / bootstrap
def cellkey(r): return (r["readout"], r["model"], r["direction"])
groups = collections.defaultdict(list)
for r in rows: groups[cellkey(r)].append(r)

def arm_family(arms):
    fam = {}
    for base in ("r1", "asT", "c1"):
        fam[base] = sorted(a for a in arms if a.startswith(base + "_A"))
    return fam

rng = np.random.default_rng(SEED)
RES = {}
for gk in sorted(groups):
    G = groups[gk]
    sids = sorted(set(r["sid"] for r in G)); sidx = {s: i for i, s in enumerate(sids)}
    arms = sorted(set(r["arm"] for r in G))
    fam = arm_family(arms)
    # per sid x arm sums: rival count, helper count, n
    S = len(sids)
    def mat(arm_list, field):
        m = np.zeros(S); n = np.zeros(S)
        for r in G:
            if r["arm"] in arm_list:
                m[sidx[r["sid"]]] += float(r[field]); n[sidx[r["sid"]]] += 1
        return m, n
    stats = {}
    for a in arms + [f"{b}_Apool" for b in fam if fam[b]]:
        al = fam[a[:-6]] if a.endswith("_Apool") else [a]
        R_, n_ = mat(al, "R"); H_, _ = mat(al, "H")
        stats[a] = (R_, H_, n_)
    # bootstrap index (same for all arms: paired over sids)
    idx = rng.integers(0, S, size=(B, S))
    cnt = np.stack([np.bincount(i, minlength=S) for i in idx])  # B x S weights
    def rate(a, field="R", w=None):
        R_, H_, n_ = stats[a]; x = R_ if field == "R" else H_
        if w is None: return x.sum() / n_.sum()
        return (w @ x) / (w @ n_)
    out = {"n_sids": S, "arms": {}}
    for a in stats:
        al = fam[a[:-6]] if a.endswith("_Apool") else [a]
        sub = [r for r in G if r["arm"] in al]
        hb = [r for r in sub if r["habit"]]
        ons = [r["onset"] for r in sub if r["onset"] is not None]
        onr = [r["onset_rel"] for r in sub if r["onset_rel"] is not None]
        onriv = [r["onset_riv"] for r in sub if r["onset_riv"] is not None]
        jd = [r for r in sub if r["judged"]]
        out["arms"][a] = dict(n=len(sub), rival=rate(a, "R"), helper=rate(a, "H"),
                              both=np.mean([r["H"] and r["R"] for r in sub]),
                              share=np.nanmean([r["share"] for r in hb]) if hb else np.nan, n_habit=len(hb),
                              onset_med_char=np.median(ons) if ons else np.nan, onset_med_rel=np.median(onr) if onr else np.nan,
                              onset_riv_med_char=np.median(onriv) if onriv else np.nan, n_strict_onset=len(ons),
                              n_judged=len(jd), flu=np.mean([r["flu"] for r in jd]) if jd else np.nan,
                              help=np.mean([r["help"] for r in jd]) if jd else np.nan)
    sign = 1 if gk[2] == "induce" else -1
    base_b = cnt @ stats["none"][0] / (cnt @ stats["none"][2])
    tw, twb = {}, {}
    for a in stats:
        if a == "none": continue
        tw[a] = sign * (rate(a) - rate("none"))
        twb[a] = sign * ((cnt @ stats[a][0]) / (cnt @ stats[a][2]) - base_b)
        out["arms"][a]["toward"] = tw[a]; out["arms"][a]["toward_ci"] = np.percentile(twb[a], [2.5, 97.5])
        out["arms"][a]["shift"] = rate(a) - rate("none")
    for a in ("asT", "c1", "skF"):
        if a in tw and tw.get("r1"):
            rb = twb[a] / twb["r1"]
            out["arms"][a]["ratio"] = tw[a] / tw["r1"]; out["arms"][a]["ratio_ci"] = np.nanpercentile(rb, [2.5, 97.5])
        if a + "_Apool" in tw:
            out["arms"][a]["margin"] = tw[a] - tw[a + "_Apool"]
            out["arms"][a]["margin_ci"] = np.percentile(twb[a] - twb[a + "_Apool"], [2.5, 97.5])
    out["arms"]["r1"]["margin"] = tw["r1"] - tw["r1_Apool"]
    out["arms"]["r1"]["margin_ci"] = np.percentile(twb["r1"] - twb["r1_Apool"], [2.5, 97.5])
    out["fam"] = fam; out["_rates"] = {a: rate(a) for a in stats}
    # keep per-sid none rival for gap pairing
    out["_none"] = (sids, stats["none"][0], stats["none"][2])
    RES[gk] = out

# ---------------------------------------------------------------- gap + rules
def ci_has0(ci): return ci[0] <= 0 <= ci[1]
VERD = {}
for ro in ("free", "fbtw"):
    bar = 0.15 if ro == "free" else 0.10
    for m in ("hdA0", "hdB0"):
        ri, rr = RES[(ro, m, "induce")], RES[(ro, m, "remove")]
        gap = rr["_rates"]["none"] - ri["_rates"]["none"]
        # gap CI: pair by shared sids
        si, xi, ni = ri["_none"]; sr, xr, nr = rr["_none"]
        common = sorted(set(si) & set(sr))
        gi = np.array([si.index(s) for s in common]); gr = np.array([sr.index(s) for s in common])
        rg = np.random.default_rng(SEED); ii = rg.integers(0, len(common), size=(B, len(common)))
        w = np.stack([np.bincount(i, minlength=len(common)) for i in ii])
        gb = (w @ xr[gr]) / (w @ nr[gr]) - (w @ xi[gi]) / (w @ ni[gi])
        VERD[(ro, m, "gap")] = (gap, np.percentile(gb, [2.5, 97.5]), len(common), len(si), len(sr))
        for d, R in (("induce", ri), ("remove", rr)):
            A = R["arms"]; t1 = A["r1"]["toward"]; t1lo = A["r1"]["toward_ci"][0]
            pre = t1 >= 0.5 * gap
            Aarms = R["fam"]["r1"]
            maxshift = max(abs(A[a]["shift"]) for a in Aarms)
            over = any(abs(A[a]["shift"]) > bar or A[a]["toward"] >= 0.5 * t1 for a in Aarms)
            if not pre: v1 = "NOT_SCORED"
            elif over: v1 = "OVERSTATED"
            elif all(A[a]["toward"] < t1 for a in Aarms) and t1lo > maxshift: v1 = "HOLDS (pending damage+cumulative gates)"
            else: v1 = "QUALIFIED"
            VERD[(ro, m, d, "rule1")] = dict(v=v1, pre=pre, t1=t1, t1ci=A["r1"]["toward_ci"], maxAshift=maxshift,
                                             A={a: (A[a]["shift"], A[a]["toward"]) for a in Aarms})
            if d == "induce":
                for a, rule, names in (("asT", "rule2", ("PASS", "LOW", "MID")), ("c1", "rule3", ("UPSTREAM", "NO EVIDENCE", "INTERMEDIATE"))):
                    ra, mg, mci = A[a]["ratio"], A[a]["margin"], A[a]["margin_ci"]
                    if ra >= 0.5 and mci[0] > 0: v = names[0]
                    elif ra <= 0.15 or ci_has0(mci): v = names[1]
                    else: v = names[2]
                    if a == "asT" and not pre: v = "NOT_SCORED (precondition fails; would be " + v + ")"
                    VERD[(ro, m, d, rule)] = dict(v=v, ratio=ra, ratio_ci=A[a]["ratio_ci"], margin=mg, margin_ci=mci)
            else:
                tp, tpci = A["r1_Apool"]["toward"], A["r1_Apool"]["toward_ci"]
                diff, dci = A["r1"]["margin"], A["r1"]["margin_ci"]
                if abs(tp) <= bar and not ci_has0(dci): v4 = "REMOVAL SPECIFIC AT EQUAL SIZE"
                elif tp >= 0.5 * t1 and not ci_has0(tpci): v4 = "REMOVAL GENERIC"
                else: v4 = "INTERMEDIATE"
                VERD[(ro, m, d, "rule4")] = dict(v=v4, t1=t1, tpool=tp, tpool_ci=tpci, diff=diff, diff_ci=dci,
                                                 skF=A["skF"]["toward"], skF_ci=A["skF"]["toward_ci"])

# ---------------------------------------------------------------- print
f3 = lambda x: f"{x:+.3f}" if isinstance(x, (float, np.floating)) and not np.isnan(x) else str(x)
ci = lambda c: f"[{c[0]:+.3f},{c[1]:+.3f}]"
for ro in ("free", "fbtw"):
    for m in ("hdA0", "hdB0"):
        g = VERD[(ro, m, "gap")]
        print(f"\n===== {ro} {m}  gap={g[0]:+.3f} CI{ci(g[1])} (paired over {g[2]} shared sids; induce {g[3]}, remove {g[4]})")
        for d in ("induce", "remove"):
            R = RES[(ro, m, d)]
            print(f"  --- {d}  (sids {R['n_sids']})")
            print("   arm         n   rival  helper  both  share(nH) onset_med(char,rel) rivOnset  toward [CI]           nJ  flu   help")
            for a, A in R["arms"].items():
                tw = f"{A['toward']:+.3f} {ci(A['toward_ci'])}" if "toward" in A else " " * 23
                print(f"   {a:10s} {A['n']:4d}  {A['rival']:.3f}  {A['helper']:.3f}  {A['both']:.3f}  {A['share']:.3f}({A['n_habit']:3d}) "
                      f"{A['onset_med_char']:6.0f},{A['onset_med_rel']:.2f}  {A['onset_riv_med_char']:6.0f}   {tw}  {A['n_judged']:4d} {A['flu']:.2f} {A['help']:.2f}")
            for a in ("asT", "c1", "r1"):
                A = R["arms"][a]
                s = f"   {a}: "
                if "ratio" in A: s += f"ratio={A['ratio']:.3f} CI{ci(A['ratio_ci'])}  "
                if "margin" in A: s += f"margin={A['margin']:+.3f} CI{ci(A['margin_ci'])}"
                print(s)
            for rule in ("rule1", "rule2", "rule3", "rule4"):
                v = VERD.get((ro, m, d, rule))
                if v: print(f"   {rule}: {v['v']}  " + "  ".join(f"{k}={f3(x) if not isinstance(x, (np.ndarray, dict)) else (ci(x) if isinstance(x, np.ndarray) else {kk: tuple(round(float(z), 3) for z in vv) for kk, vv in x.items()})}" for k, x in v.items() if k != "v"))
json.dump({"|".join(k): (v if not isinstance(v, tuple) else list(v)) for k, v in VERD.items()}, open(f"/workspace/runs_executor/sw038/verify_p1/verdicts{'' if USE_W else '_int'}.json", "w"), default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o), indent=1)
