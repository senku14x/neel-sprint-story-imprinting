"""Blind recompute of sw034 part B headline numbers from raw rows.
Usage: OMP_NUM_THREADS=4 python3 -I recompute.py RAW_DIR OUT_DIR
"""
import json, sys, os, collections
import numpy as np

RAW, OUT = sys.argv[1], sys.argv[2]
ARMS = ["none", "P1", "P2", "R1", "R2"]
MODELS = ["e08-N", "e08-NB"]
B = 2000
PREFIX = "sw034-Bfull|"

def load(fn):
    return [json.loads(l) for l in open(os.path.join(RAW, fn))]

def is_degen(r, lower=True):
    t = r["text"]
    if r["n_tok"] < 20: return True, "ntok<20"
    if len(t) < 40: return True, "chars<40"
    w = t.split()
    if lower: w = [x.lower() for x in w]
    if len(w) >= 40 and len(set(w)) / len(w) < 0.15: return True, "lowdistinct"
    return False, ""

# judges: dict key -> judge -> row
def judge_map(rows):
    m = collections.defaultdict(dict)
    dup = 0
    for r in rows:
        assert r["key"].startswith(PREFIX)
        k = r["key"][len(PREFIX):]
        if r["judge"] in m[k]: dup += 1
        m[k][r["judge"]] = r
    return m, dup

decl, dup1 = judge_map(load("judged_B_decl.jsonl"))
rep5, dup2 = judge_map(load("judged_B_reply5.jsonl"))

def pct_ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]

report = {"dup_judge_rows": [dup1, dup2], "models": {}}
lines = []
for model in MODELS:
    rows = load(f"free_e08-{model.split('-')[1]}.jsonl")
    assert all(r["model"] == model for r in rows)
    scen = sorted(set(r["scenario"] for r in rows))
    sidx = {s: i for i, s in enumerate(scen)}
    S = len(scen)
    # per-row features
    recs = []
    missing = collections.Counter()
    degen_reason = collections.Counter()
    degen_case_sens_diff = 0
    for r in rows:
        dg, why = is_degen(r)
        dg2, _ = is_degen(r, lower=False)
        if dg != dg2: degen_case_sens_diff += 1
        jd = decl.get(r["key"], {})
        jr = rep5.get(r["key"], {})
        for j in ("glm", "deepseek"):
            if j not in jd or jd[j].get("decline_w") is None: missing["decl_" + j] += 1
            if j not in jr or jr[j].get("fluency_w") is None: missing["rep5_" + j] += 1
        dws = [jd[j]["decline_w"] for j in ("glm", "deepseek") if j in jd and jd[j].get("decline_w") is not None]
        rws = [jd[j]["register_w"] for j in ("glm", "deepseek") if j in jd and jd[j].get("register_w") is not None]
        fws = [jr[j]["fluency_w"] for j in ("glm", "deepseek") if j in jr and jr[j].get("fluency_w") is not None]
        if dg: degen_reason[(r["arm"], why)] += 1
        recs.append(dict(arm=r["arm"], s=sidx[r["scenario"]], degen=dg,
                         dmean=np.mean(dws) if dws else np.nan,
                         reg=np.mean(rws) if rws else np.nan,
                         flu=np.mean(fws) if fws else np.nan,
                         d_glm=jd.get("glm", {}).get("decline_w", np.nan),
                         d_ds=jd.get("deepseek", {}).get("decline_w", np.nan),
                         f_glm=jr.get("glm", {}).get("fluency_w", np.nan),
                         f_ds=jr.get("deepseek", {}).get("fluency_w", np.nan),
                         r_glm=jd.get("glm", {}).get("register_w", np.nan),
                         r_ds=jd.get("deepseek", {}).get("register_w", np.nan)))
    # per-scenario sums per arm (kept rows only)
    stats = ["n", "d7", "d5", "reg", "flu"]
    sums = {a: {k: np.zeros(S) for k in stats} for a in ARMS}
    per_arm = {}
    for a in ARMS:
        ra = [x for x in recs if x["arm"] == a]
        kept = [x for x in ra if not x["degen"]]
        for x in kept:
            s = x["s"]
            sums[a]["n"][s] += 1
            sums[a]["d7"][s] += x["dmean"] > 7
            sums[a]["d5"][s] += x["dmean"] > 5
            sums[a]["reg"][s] += x["reg"]
            sums[a]["flu"][s] += x["flu"]
        n = len(kept)
        per_arm[a] = dict(
            n_total=len(ra), n_kept=n, n_degen=len(ra) - n,
            decline7=float(np.mean([x["dmean"] > 7 for x in kept])),
            decline5=float(np.mean([x["dmean"] > 5 for x in kept])),
            register=float(np.mean([x["reg"] for x in kept])),
            fluency=float(np.mean([x["flu"] for x in kept])),
            fluency_glm=float(np.mean([x["f_glm"] for x in kept])),
            fluency_ds=float(np.mean([x["f_ds"] for x in kept])),
            register_glm=float(np.mean([x["r_glm"] for x in kept])),
            register_ds=float(np.mean([x["r_ds"] for x in kept])),
            decline7_glm=float(np.mean([x["d_glm"] > 7 for x in kept])),
            decline7_ds=float(np.mean([x["d_ds"] > 7 for x in kept])),
        )
    # bootstrap
    rng = np.random.default_rng(0)
    idx = rng.integers(0, S, size=(B, S))
    cnt = np.stack([np.bincount(row, minlength=S) for row in idx])  # B x S multiplicity
    boot = {}
    for a in ARMS:
        n = cnt @ sums[a]["n"]
        boot[a] = {k: (cnt @ sums[a][k]) / n for k in ["d7", "d5", "reg", "flu"]}
    for a in ARMS:
        per_arm[a]["decline7_ci"] = pct_ci(boot[a]["d7"])
        per_arm[a]["decline5_ci"] = pct_ci(boot[a]["d5"])
        per_arm[a]["register_ci"] = pct_ci(boot[a]["reg"])
        per_arm[a]["fluency_ci"] = pct_ci(boot[a]["flu"])
    pt = {a: dict(d7=per_arm[a]["decline7"], d5=per_arm[a]["decline5"], reg=per_arm[a]["register"]) for a in ARMS}
    contrasts = {}
    def con(name, a, b, k):
        contrasts[name] = dict(est=pt[a][k] - pt[b][k], ci=pct_ci(boot[a][k] - boot[b][k]))
    for lvl in ("1", "2"):
        con(f"rise({lvl}x)_d7", "P" + lvl, "R" + lvl, "d7")
        con(f"rise({lvl}x)_d5", "P" + lvl, "R" + lvl, "d5")
        con(f"dregister({lvl})", "P" + lvl, "R" + lvl, "reg")
        for arm in ("P" + lvl, "R" + lvl):
            con(f"{arm}-none_d7", arm, "none", "d7")
            con(f"{arm}-none_d5", arm, "none", "d5")
            con(f"{arm}-none_reg", arm, "none", "reg")
    # labels
    rise_hits = []
    for lvl in ("1", "2"):
        c = contrasts[f"rise({lvl}x)_d7"]
        flu = per_arm["P" + lvl]["fluency"]
        ok = c["est"] >= 0.10 and c["ci"][0] > 0 and flu >= 7
        rise_hits.append(dict(level=lvl, rise=c["est"], lo=c["ci"][0], fluency_P=flu, pass_=ok))
    rise_label = any(h["pass_"] for h in rise_hits)
    manip = {lvl: contrasts[f"dregister({lvl})"]["ci"][0] > 0 for lvl in ("1", "2")}
    # judge agreement on decline >7 (kept rows, all arms; and per arm)
    def agree(sub):
        g = np.array([x["d_glm"] > 7 for x in sub]); d = np.array([x["d_ds"] > 7 for x in sub])
        both7 = int(np.sum(g & d)); bothle = int(np.sum(~g & ~d)); n = len(sub)
        g_only = int(np.sum(g & ~d)); d_only = int(np.sum(~g & d))
        po = (both7 + bothle) / n
        pe = g.mean() * d.mean() + (1 - g.mean()) * (1 - d.mean())
        kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")
        return dict(n=n, both_gt7=both7, both_le7=bothle, glm_only=g_only, ds_only=d_only,
                    agree=po, kappa=kappa)
    kept_all = [x for x in recs if not x["degen"]]
    agreement = {"all": agree(kept_all)}
    for a in ARMS:
        agreement[a] = agree([x for x in kept_all if x["arm"] == a])
    report["models"][model] = dict(n_scenarios=S, per_arm=per_arm, contrasts=contrasts,
                                   rise=rise_hits, RISE=rise_label, manipulation_ok=manip,
                                   agreement=agreement, missing_judges=dict(missing),
                                   degen_reasons={f"{k[0]}:{k[1]}": v for k, v in degen_reason.items()},
                                   degen_case_sensitivity_diff=degen_case_sens_diff)

json.dump(report, open(os.path.join(OUT, "recompute_blindB.json"), "w"), indent=1)

# text summary
def f(x): return f"{x:.3f}"
for model, R in report["models"].items():
    lines.append(f"== {model} (scenarios={R['n_scenarios']}) missing judges: {R['missing_judges'] or 'none'}; degen reasons: {R['degen_reasons']}; case-sens diff: {R['degen_case_sensitivity_diff']}")
    lines.append("arm | n_kept | degen | decl>7 [CI] | decl>5 [CI] | register [CI] | fluency [CI] | flu glm/ds | reg glm/ds | d>7 glm/ds")
    for a in ARMS:
        p = R["per_arm"][a]
        lines.append(f"{a} | {p['n_kept']} | {p['n_degen']} | {f(p['decline7'])} [{f(p['decline7_ci'][0])},{f(p['decline7_ci'][1])}] | "
                     f"{f(p['decline5'])} [{f(p['decline5_ci'][0])},{f(p['decline5_ci'][1])}] | {f(p['register'])} [{f(p['register_ci'][0])},{f(p['register_ci'][1])}] | "
                     f"{f(p['fluency'])} [{f(p['fluency_ci'][0])},{f(p['fluency_ci'][1])}] | {f(p['fluency_glm'])}/{f(p['fluency_ds'])} | {f(p['register_glm'])}/{f(p['register_ds'])} | {f(p['decline7_glm'])}/{f(p['decline7_ds'])}")
    lines.append("contrast | est [CI]")
    for k, c in R["contrasts"].items():
        lines.append(f"{k} | {c['est']:+.3f} [{c['ci'][0]:+.3f},{c['ci'][1]:+.3f}]")
    lines.append(f"RISE={R['RISE']} detail={R['rise']}")
    lines.append(f"manipulation_ok={R['manipulation_ok']}")
    for k, v in R["agreement"].items():
        lines.append(f"agree {k}: {v}")
txt = "\n".join(lines)
open(os.path.join(OUT, "recompute_blindB.txt"), "w").write(txt)
print(txt)
print("dup judge rows:", report["dup_judge_rows"])
