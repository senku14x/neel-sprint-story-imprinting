"""Blind recomputation of sw052 headline numbers from raw files (fresh code; CPU only)."""
import json, sys, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels  # noqa: E402

R = "/workspace/runs_executor/sw052"
PARTS = {"induce": "rev", "remove": "fwd"}
MODELS = ["hdA0", "hdB0"]
HELPER = {"hdA0": "bee", "hdB0": "crow"}
ARMS = ["none", "r1", "c1", "A0", "A1", "A2", "P0", "P1"]
POOLS = {"poolA": ["A0", "A1", "A2"], "poolP": ["P0", "P1"]}
FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]
anom = []


def role(lab, helper):
    if lab == "none":
        return "neither"
    if lab == "both":
        return "both"
    return "helper" if lab == helper else "rival"


def lab_from(bee, crow):
    return "both" if bee and crow else "bee" if bee else "crow" if crow else "none"


# ------------------------------------------------------------------ load replies + judges
rows = {}          # key -> row dict (with labels)
counts_check = {}
for part, dirn in PARTS.items():
    man = json.load(open(f"{R}/{part}/manifest.json"))
    exp = man["expected"]
    exps = set(exp)
    if len(exp) != len(exps):
        anom.append(f"{part}: manifest expected has duplicates")
    got = []
    for m in MODELS:
        for line in open(f"{R}/{part}/free/free_{m}.jsonl"):
            got.append(json.loads(line))
    keys = [r["key"] for r in got]
    kc = collections.Counter(keys)
    dup = [k for k, v in kc.items() if v > 1]
    kept = [r for r in got if r["key"] in exps]
    missing = exps - set(keys)
    extra = set(keys) - exps
    counts_check[part] = dict(rows_in_files=len(got), unique_keys=len(kc), dup_keys=len(dup), expected=len(exp),
                              kept=len(kept), missing=len(missing), extra=len(extra))
    seen = set()
    for r in kept:
        if r["key"] in seen:
            continue
        seen.add(r["key"])
        assert r["direction"] == dirn and r["readout"] == "free"
        # key consistency
        kp = r["key"].split("|")
        assert kp[2] == r["model"] and kp[3] == r["direction"] and kp[4] == r["sid"] and kp[5] == r["arm"] and kp[6] == f"s{r['sample']}", r["key"]
        r["part"] = part
        r["strict"] = labels.strict_label(r["text"])
        r["judges"] = {}
        rows[r["key"]] = r
    # judges: last valid row per (key, judge)
    jrows = [json.loads(l) for l in open(f"{R}/{part}/judged.jsonl")]
    nerr = 0
    for j in jrows:
        if j.get("error") is not None or any(j.get(f + "_w") is None for f in FIELDS):
            nerr += 1
            continue
        if j["key"] not in rows:
            continue
        rows[j["key"]]["judges"][j["judge"]] = {f: float(j[f + "_w"]) for f in FIELDS}
    counts_check[part].update(judge_rows=len(jrows), judge_err_rows=nerr,
                              judged_keys_both=sum(1 for r in rows.values() if r["part"] == part and len(r["judges"]) == 2),
                              judged_keys_one=sum(1 for r in rows.values() if r["part"] == part and len(r["judges"]) == 1))

# labels
for r in rows.values():
    h = HELPER[r["model"]]
    r["role_strict"] = role(r["strict"], h)
    if set(r["judges"]) >= {"glm", "deepseek"}:
        cons = {f: 0.5 * (r["judges"]["glm"][f] + r["judges"]["deepseek"][f]) for f in FIELDS}
        r["cons"] = cons
        r["jlab"] = lab_from(cons["bee"] > 5, cons["crow"] > 5)
        r["role_judge"] = role(r["jlab"], h)
        r["role"] = r["role_judge"]
    else:
        r["cons"] = None
        r["role"] = r["role_strict"]

SIDS = sorted({r["sid"] for r in rows.values()})
assert len(SIDS) == 64
SIDX = {s: i for i, s in enumerate(SIDS)}

# per (model, dir, arm): count arrays over scripts: n, helper, rival, both
C = {}
for m in MODELS:
    for d in PARTS.values():
        for a in ARMS:
            C[(m, d, a)] = {k: np.zeros(64) for k in ("n", "helper", "rival", "both", "neither")}
for r in rows.values():
    c = C[(r["model"], r["direction"], r["arm"])]
    i = SIDX[r["sid"]]
    c["n"][i] += 1
    c[r["role"]][i] += 1
for k, c in C.items():
    if not (c["n"] == 2).all():
        anom.append(f"{k}: not exactly 2 rows per script")
for m in MODELS:
    for d in PARTS.values():
        for p, arms in POOLS.items():
            C[(m, d, p)] = {k: sum(C[(m, d, a)][k] for a in arms) for k in ("n", "helper", "rival", "both", "neither")}

# ------------------------------------------------------------------ bootstrap weights
rng = np.random.default_rng(0)
draws = rng.integers(0, 64, (2000, 64))
W = np.zeros((2000, 64))
for b in range(2000):
    W[b] = np.bincount(draws[b], minlength=64)
W_full = np.ones((1, 64))
WW = np.vstack([W_full, W])  # row 0 = point estimate


def stats(c):
    """Per weight row: share, onset, unc rival, unc helper."""
    with np.errstate(invalid="ignore", divide="ignore"):
        n = WW @ c["n"]
        hab = WW @ (c["helper"] + c["rival"] + c["both"])
        share = (WW @ (c["rival"] + 0.5 * c["both"])) / hab
        onset = hab / n
        unc_r = (WW @ (c["rival"] + c["both"])) / n
        unc_h = (WW @ (c["helper"] + c["both"])) / n
    return dict(share=share, onset=onset, unc_r=unc_r, unc_h=unc_h)


S = {k: stats(c) for k, c in C.items()}
SGN = {"rev": 1.0, "fwd": -1.0}
ARMS_ALL = ARMS + list(POOLS)


def ci(x):
    v = x[1:]
    v = v[~np.isnan(v)]
    return np.percentile(v, 2.5), np.percentile(v, 97.5), len(v)


def f3(x):
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.3f}"


def fmt(x):
    lo, hi, nv = ci(x)
    s = f"{f3(x[0])} [{f3(lo)}, {f3(hi)}]"
    if nv < 2000:
        s += f" (NaN draws dropped: {2000 - nv})"
    return s


T = {}  # (m, d, arm) -> dict of arrays
for m in MODELS:
    for d in PARTS.values():
        b0 = S[(m, d, "none")]
        for a in ARMS_ALL:
            s = S[(m, d, a)]
            T[(m, d, a)] = dict(toward=SGN[d] * (s["share"] - b0["share"]),
                                unc_toward=SGN[d] * (s["unc_r"] - b0["unc_r"]),
                                helper_shift=s["unc_h"] - b0["unc_h"],
                                onset_shift=s["onset"] - b0["onset"])

out = []
P = out.append
P("## Counts checked")
for part, cc in counts_check.items():
    P(f"{part}: {cc}")
P(f"anomalies so far: {anom}")
P(f"n judged keys with both judges by part: " + ", ".join(f"{p}={counts_check[p]['judged_keys_both']}" for p in PARTS))
# sample-0 judge coverage
for part, d in PARTS.items():
    s0 = [r for r in rows.values() if r["part"] == part and r["sample"] == 0]
    P(f"{part}: sample-0 rows judged {sum(1 for r in s0 if r['cons'] is not None)}/{len(s0)}; sample-1 judged "
      f"{sum(1 for r in rows.values() if r['part']==part and r['sample']==1 and r['cons'] is not None)}/{sum(1 for r in rows.values() if r['part']==part and r['sample']==1)}")

P("\n## Per model x direction x arm (primary label)")
P("model dir arm | n n_habit | share onset unc_rival unc_helper | toward [CI] | unc_toward [CI] | helper_shift [CI] | onset_shift [CI]")
for m in MODELS:
    for d in PARTS.values():
        for a in ARMS_ALL:
            c = C[(m, d, a)]
            s = S[(m, d, a)]
            t = T[(m, d, a)]
            nh = int(c["helper"].sum() + c["rival"].sum() + c["both"].sum())
            line = (f"{m} {d} {a} | n={int(c['n'].sum())} habit={nh} (h={int(c['helper'].sum())} r={int(c['rival'].sum())} b={int(c['both'].sum())}) | "
                    f"share={f3(s['share'][0])} onset={f3(s['onset'][0])} uncR={f3(s['unc_r'][0])} uncH={f3(s['unc_h'][0])}")
            if a != "none":
                line += f" | toward={fmt(t['toward'])} | unc_toward={fmt(t['unc_toward'])} | helper_shift={fmt(t['helper_shift'])} | onset_shift={fmt(t['onset_shift'])}"
            P(line)

P("\n## Ratio, control contrasts, gap, precondition, verdicts")
res = {}
for m in MODELS:
    gap = S[(m, "fwd", "none")]["share"] - S[(m, "rev", "none")]["share"]
    res[(m, "gap")] = gap
    P(f"{m} gap = share(none,fwd) - share(none,rev) = {fmt(gap)}  (share none fwd={f3(S[(m,'fwd','none')]['share'][0])}, rev={f3(S[(m,'rev','none')]['share'][0])})")
    for d in PARTS.values():
        tr1 = T[(m, d, "r1")]["toward"]
        tc1 = T[(m, d, "c1")]["toward"]
        with np.errstate(invalid="ignore", divide="ignore"):
            ratio = tc1 / tr1
        dA = tc1 - T[(m, d, "poolA")]["toward"]
        dP = tc1 - T[(m, d, "poolP")]["toward"]
        res[(m, d, "ratio")] = ratio
        res[(m, d, "dA")] = dA
        res[(m, d, "dP")] = dP
        frac_le0 = np.mean(tr1[1:] <= 0)
        # also unconditional versions
        uratio = T[(m, d, "c1")]["unc_toward"] / T[(m, d, "r1")]["unc_toward"]
        udA = T[(m, d, "c1")]["unc_toward"] - T[(m, d, "poolA")]["unc_toward"]
        udP = T[(m, d, "c1")]["unc_toward"] - T[(m, d, "poolP")]["unc_toward"]
        P(f"{m} {d}: ratio={fmt(ratio)}; frac draws toward(r1)<=0: {f3(frac_le0)}; c1-poolA={fmt(dA)}; c1-poolP={fmt(dP)}")
        P(f"   (unconditional-rival versions, descriptive) unc ratio={fmt(uratio)}; unc c1-poolA={fmt(udA)}; unc c1-poolP={fmt(udP)}")
        res[(m, d, "uratio")] = uratio; res[(m, d, "udA")] = udA; res[(m, d, "udP")] = udP
        if d == "rev":
            pre = tr1[0] >= 0.5 * gap[0]
            res[(m, "pre")] = pre
            P(f"   precondition toward(r1,induce)={f3(tr1[0])} >= 0.5*gap={f3(0.5*gap[0])}: {pre}")

# cosines
import torch  # noqa: E402
COS = {}
for m in MODELS:
    dd = torch.load(f"{R}/dirs52_{m}.pt", weights_only=False, map_location="cpu")
    folds = list(dd["scen"].keys())
    cs = []
    for f in folds:
        u = dd["scen"][f]["u"].double()
        uc = dd["scen"][f]["uc"].double()
        cs.append(((u * uc).sum(1) / (u.norm(dim=1) * uc.norm(dim=1))).numpy())
    cs = np.array(cs)  # (5, 64)
    COS[m] = dict(folds=folds, cs=cs)

P("\n## Cosines cos(u_c, u), fold-averaged (5 folds), rows indexed by layer")
for m in MODELS:
    cs = COS[m]["cs"]
    fa = cs.mean(0)
    Ls = list(range(16, 64))
    med = np.median(fa[Ls])
    med2 = np.median(fa[Ls] ** 2)
    med2b = np.median((cs[:, Ls] ** 2).mean(0))
    COS[m]["med"] = med
    P(f"{m}: " + ", ".join(f"L{L}={f3(fa[L])}" for L in (16, 24, 32, 40, 48, 56, 63)) +
      f"; median L16-63={f3(med)}; median (fold-avg cos)^2={f3(med2)}; median fold-avg(cos^2)={f3(med2b)}; "
      f"min/max L16-63={f3(fa[Ls].min())}/{f3(fa[Ls].max())}; fold spread (max-min across folds, median over layers)={f3(np.median(cs[:, Ls].max(0)-cs[:, Ls].min(0)))}")

P("\n## Frozen verdicts (free, induce decides, per model)")
for m in MODELS:
    if not res[(m, "pre")]:
        v = "NOT SCORED (precondition fails)"
    else:
        r0 = res[(m, "rev", "ratio")][0]
        dA = res[(m, "rev", "dA")]
        dP = res[(m, "rev", "dP")]
        beatA = dA[0] > 0 and ci(dA)[0] > 0
        beatP = dP[0] > 0 and ci(dP)[0] > 0
        if r0 >= 0.5 and beatA and beatP:
            v = "UPSTREAM, cosine " + ("HIGH" if COS[m]["med"] >= 0.6 else "LOW")
        elif r0 <= 0.15 or not (beatA and beatP):
            v = "NO EVIDENCE"
        else:
            v = "INTERMEDIATE"
        v += f" (ratio={f3(r0)}, beats poolA={beatA}, beats poolP={beatP}, cos median={f3(COS[m]['med'])})"
    P(f"{m}: {v}")
    dAr = res[(m, "fwd", "dA")]
    P(f"{m} remove specificity: c1-poolA(remove)={fmt(dAr)} -> {'specific' if ci(dAr)[0] > 0 else 'not specific'}")

P("\n## Counterbalanced (mean of the two models, per draw)")
for d in PARTS.values():
    for nm in ("ratio", "dA", "dP", "uratio", "udA", "udP"):
        cb = 0.5 * (res[("hdA0", d, nm)] + res[("hdB0", d, nm)])
        P(f"{d} {nm}: {fmt(cb)}")
    for a in ARMS_ALL[1:]:
        cb = 0.5 * (T[("hdA0", d, a)]["toward"] + T[("hdB0", d, a)]["toward"])
        cbu = 0.5 * (T[("hdA0", d, a)]["unc_toward"] + T[("hdB0", d, a)]["unc_toward"])
        cbh = 0.5 * (T[("hdA0", d, a)]["helper_shift"] + T[("hdB0", d, a)]["helper_shift"])
        P(f"{d} {a}: toward={fmt(cb)}; unc_toward={fmt(cbu)}; helper_shift={fmt(cbh)}")
    tc = 0.5 * (T[("hdA0", d, "c1")]["toward"] + T[("hdB0", d, "c1")]["toward"])
    tr = 0.5 * (T[("hdA0", d, "r1")]["toward"] + T[("hdB0", d, "r1")]["toward"])
    with np.errstate(invalid="ignore", divide="ignore"):
        P(f"{d} ratio of counterbalanced towards (mean c1 / mean r1): {fmt(tc/tr)}")
gcb = 0.5 * (res[("hdA0", "gap")] + res[("hdB0", "gap")])
P(f"counterbalanced gap: {fmt(gcb)}")

# ------------------------------------------------------------------ cumulative offsets
P("\n## Cumulative offsets: median over scripts of band-mean of per-layer (mean_tok1-6 off(arm) / mean_tok1-6 off(c1)); sample 0")
BANDS = {"L16": [16], "L28-40": [28, 32, 36, 40], "L44-63": [44, 48, 52, 56, 60, 63]}
for part, d in PARTS.items():
    for m in MODELS:
        Lg = collections.defaultdict(dict)  # (grp, arm) -> {L: mean off}
        nrow = 0
        for line in open(f"{R}/{part}/free/log_free_{m}.jsonl"):
            x = json.loads(line)
            if x["sample"] != 0 or x.get("readout", "free") != "free":
                continue
            nrow += 1
            assert len(x["off"]) == 7
            key = (x["grp"], x["arm"])
            if x["L"] in Lg[key]:
                anom.append(f"dup log row {part} {m} {key} L{x['L']}")
            Lg[key][x["L"]] = float(np.mean(x["off"][1:7]))
        grps = sorted({g for g, a in Lg})
        assert all(g.split("|")[0] == m and g.split("|")[1] == d for g in grps)
        line = f"{m} {d} (log rows {nrow}, scripts {len(grps)}):"
        for a in ["A0", "A1", "A2", "P0", "P1", "r1"]:
            parts_ = []
            for bn, Ls in BANDS.items():
                vals = []
                for g in grps:
                    num, den = Lg.get((g, a), {}), Lg.get((g, "c1"), {})
                    pres = [L for L in Ls if L in num and L in den]
                    if not pres:
                        continue
                    vals.append(np.mean([num[L] / den[L] for L in pres]))
                vals = np.array(vals)
                s = f"{bn}={f3(np.median(vals))}"
                if a.startswith("A") and bn != "L16":
                    s += f"(min {f3(vals.min())}, frac>=0.9 {f3(np.mean(vals >= 0.9))})"
                parts_.append(s)
            line += f"\n   {a}: " + " ".join(parts_)
        P(line)

# ------------------------------------------------------------------ damage
P("\n## Damage per arm: judged rows (consensus means); cap-hit and non-empty on all rows")
for m in MODELS:
    for d in PARTS.values():
        for a in ARMS:
            rr = [r for r in rows.values() if r["model"] == m and r["direction"] == d and r["arm"] == a]
            jr = [r for r in rr if r["cons"] is not None]
            jr0 = [r for r in jr if r["sample"] == 0]
            cap = np.mean([(r["finish"] != "stop") or (r["n_tok"] >= r["max_new"]) for r in rr])
            ne = np.mean([bool((r["text"] or "").strip()) for r in rr])
            mh = np.mean([r["cons"]["helpfulness"] for r in jr]); mf = np.mean([r["cons"]["fluency"] for r in jr]); mo = np.mean([r["cons"]["hostility"] for r in jr])
            mh0 = np.mean([r["cons"]["helpfulness"] for r in jr0]); mf0 = np.mean([r["cons"]["fluency"] for r in jr0]); mo0 = np.mean([r["cons"]["hostility"] for r in jr0])
            P(f"{m} {d} {a}: n_judged={len(jr)} help={f3(mh)} flu={f3(mf)} host={f3(mo)} | sample0 only n={len(jr0)} help={f3(mh0)} flu={f3(mf0)} host={f3(mo0)} | cap_hit={f3(cap)} non_empty={f3(ne)} mean_ntok={np.mean([r['n_tok'] for r in rr]):.1f}")

# ------------------------------------------------------------------ judge vs STRICT
P("\n## Judge consensus vs STRICT on judged rows")
for part, d in PARTS.items():
    for m in MODELS:
        jr = [r for r in rows.values() if r["part"] == part and r["model"] == m and r["cons"] is not None]
        ag = np.mean([r["jlab"] == r["strict"] for r in jr])
        agr = np.mean([r["role_judge"] == r["role_strict"] for r in jr])
        conf = collections.Counter((r["strict"], r["jlab"]) for r in jr)
        # per-judge agreement with each other
        lg = [lab_from(r["judges"]["glm"]["bee"] > 5, r["judges"]["glm"]["crow"] > 5) for r in jr]
        ldp = [lab_from(r["judges"]["deepseek"]["bee"] > 5, r["judges"]["deepseek"]["crow"] > 5) for r in jr]
        jj = np.mean([a == b for a, b in zip(lg, ldp)])
        gs = np.mean([a == r["strict"] for a, r in zip(lg, jr)])
        ds = np.mean([a == r["strict"] for a, r in zip(ldp, jr)])
        P(f"{part} {m}: n={len(jr)} consensus==STRICT animal {f3(ag)}, role {f3(agr)}; glm==deepseek {f3(jj)}; glm==STRICT {f3(gs)}; deepseek==STRICT {f3(ds)}")
        P(f"   confusion (STRICT, consensus): " + ", ".join(f"{k}:{v}" for k, v in sorted(conf.items()) if k[0] != k[1]))

# STRICT-only sensitivity of headline numbers
P("\n## Sensitivity: STRICT-only labels (no judge override)")
CS = {}
for m in MODELS:
    for d in PARTS.values():
        for a in ARMS:
            CS[(m, d, a)] = {k: np.zeros(64) for k in ("n", "helper", "rival", "both", "neither")}
for r in rows.values():
    c = CS[(r["model"], r["direction"], r["arm"])]
    c["n"][SIDX[r["sid"]]] += 1
    c[r["role_strict"]][SIDX[r["sid"]]] += 1
for m in MODELS:
    for d in PARTS.values():
        for p, arms in POOLS.items():
            CS[(m, d, p)] = {k: sum(CS[(m, d, a)][k] for a in arms) for k in ("n", "helper", "rival", "both", "neither")}
SS = {k: stats(c) for k, c in CS.items()}
for m in MODELS:
    gap = SS[(m, "fwd", "none")]["share"] - SS[(m, "rev", "none")]["share"]
    for d in PARTS.values():
        tw = {a: SGN[d] * (SS[(m, d, a)]["share"] - SS[(m, d, "none")]["share"]) for a in ARMS_ALL}
        with np.errstate(invalid="ignore", divide="ignore"):
            rt = tw["c1"] / tw["r1"]
        P(f"STRICT {m} {d}: toward r1={fmt(tw['r1'])} c1={fmt(tw['c1'])} poolA={f3(tw['poolA'][0])} poolP={f3(tw['poolP'][0])}; ratio={fmt(rt)}; c1-poolA={fmt(tw['c1']-tw['poolA'])}; c1-poolP={fmt(tw['c1']-tw['poolP'])}" +
          (f"; gap={fmt(gap)}" if d == "rev" else ""))

P(f"\nanomalies: {anom}")
print("\n".join(out))
