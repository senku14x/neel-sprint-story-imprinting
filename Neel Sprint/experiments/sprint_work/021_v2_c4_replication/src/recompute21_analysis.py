"""sw021 analysis-pass recompute (independent of analyze21.py's aggregation; uses only lib/labels.py for STRICT/lexicon).
Completeness per cell, labels (primary/STRICT), pooled rival share, gap, toward-donor shifts, fraction of gap, scenario- and
domain-clustered bootstrap (own seeds), controls with |shift|, onset, per-domain r1, fp-excluded sensitivity, conduct deltas.
Usage: python3 recompute21.py <run_dir> <out_json>"""
import json, os, sys
from collections import defaultdict
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB

RUN, OUT = sys.argv[1], sys.argv[2]
HELPER = {"hdA0": "bee", "hdB0": "crow"}
CTRL = [f"r1-shuf{i}" for i in range(5)] + [f"r1-cov{i}" for i in range(5)]


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


rows = {rd: [r for m in ("hdA0", "hdB0") for r in jl(f"{RUN}/{rd}_{m}.jsonl")] for rd in ("forced", "free")}
ctx = jl(f"{RUN}/contexts.jsonl")
dom_of = {c["sid"]: c["domain"] for c in ctx}
fp = set(json.load(open("/workspace/runs_executor/sw019/part2/fp/fp_flags.json"))["flagged_scenarios"])
J = defaultdict(dict)
for rd in ("forced", "free"):
    for l in open(f"{RUN}/judged_{rd}.jsonl"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("error") is None and all(r.get(f + "_w") is not None for f in ("bee", "crow", "helpfulness", "fluency", "hostility")):
            J[r["key"]][r["judge"]] = r
man = {rd: set(json.load(open(f"{RUN}/judged_{rd}.jsonl.manifest.json"))["keys"]) for rd in ("forced", "free")}


def role(lab, m):
    h = HELPER[m]
    return {"none": "neither", "both": "both"}.get(lab, "helper" if lab == h else "rival")


def judge_lab(k, m):
    j = J.get(k)
    if not j or "glm" not in j or "deepseek" not in j:
        return None
    b = (j["glm"]["bee_w"] + j["deepseek"]["bee_w"]) / 2; c = (j["glm"]["crow_w"] + j["deepseek"]["crow_w"]) / 2
    return role("both" if b > 5 and c > 5 else "bee" if b > 5 else "crow" if c > 5 else "none", m)


def lab(r, how):
    s = role(LB.strict_label(r["text"]), r["model"])
    if how == "strict":
        return s
    if LB.disagree(r["text"]) or r["scenario"] in fp:
        j = judge_lab(r["key"], r["model"])
        return j if j is not None else s
    return s


out = {"completeness": {}, "results": {}}
# ---------------- completeness
sids_all = sorted(dom_of)  # 61 scripts (sid) in contexts
for rd in ("forced", "free"):
    R = rows[rd]; keys = [r["key"] for r in R]
    out["completeness"][rd] = dict(n_rows=len(R), unique_keys=len(set(keys)), empty=sum(1 for r in R if not (r["text"] or "").strip()))
    cells = defaultdict(list)
    for r in R:
        cells[(r["model"], r["direction"], r["arm"])].append(r)
    comp = {}
    for (m, d, a), rr in sorted(cells.items()):
        sids = set(r["sid"] for r in rr)
        jsel = [r for r in rr if r["key"] in man[rd]] if man[rd] else []
        jok = [r for r in jsel if r["key"] in J and "glm" in J[r["key"]] and "deepseek" in J[r["key"]]]
        comp[f"{m}|{d}|{a}"] = dict(present=len(rr), expected=2 * len(sids_all), n_sids=len(sids), empty=sum(1 for r in rr if not r["text"].strip()),
                                    cap=sum(1 for r in rr if r.get("hit_cap")) if rd == "free" else None,
                                    judge_selected=len(jsel), judge_both_valid=len(jok), disagree=sum(1 for r in rr if LB.disagree(r["text"])),
                                    fp_rows=sum(1 for r in rr if r["scenario"] in fp))
    out["completeness"][rd + "_cells"] = comp


# ---------------- estimator
def cellarr(rr, sids, how):
    ix = {s: i for i, s in enumerate(sids)}; rv = np.zeros(len(sids)); hb = np.zeros(len(sids)); n = np.zeros(len(sids))
    for r in rr:
        if r["sid"] not in ix:
            continue
        L = lab(r, how); i = ix[r["sid"]]; n[i] += 1
        if L in ("helper", "rival", "both"):
            hb[i] += 1; rv[i] += 1.0 if L == "rival" else 0.5 if L == "both" else 0.0
    return rv, hb, n


def share(c, idx=None):
    rv, hb, _ = c
    if idx is None:
        return rv.sum() / hb.sum() if hb.sum() else np.nan
    return rv[idx].sum(1) / np.where(hb[idx].sum(1) > 0, hb[idx].sum(1), np.nan)


def onset(c):
    return c[1].sum() / c[2].sum()


def q(v):
    v = v[np.isfinite(v)]
    return [float(np.quantile(v, .025)), float(np.quantile(v, .975))]


def analyse(rd, how, sids, nb=4000, seed=20261031):
    rng = np.random.default_rng(seed); S = len(sids)
    Bs = rng.integers(0, S, (nb, S))
    doms = sorted(set(dom_of[s] for s in sids)); mem = {d: [i for i, s in enumerate(sids) if dom_of[s] == d] for d in doms}
    rngd = np.random.default_rng(seed + 1); Bd = []
    for _ in range(nb):
        pick = rngd.integers(0, len(doms), len(doms)); Bd.append(np.array([i for p in pick for i in mem[doms[p]]]))
    res = {}
    for m in ("hdA0", "hdB0"):
        R = [r for r in rows[rd] if r["model"] == m]
        C = {}
        for r in R:
            C.setdefault((r["direction"], r["arm"]), []).append(r)
        C = {k: cellarr(v, sids, how) for k, v in C.items()}
        f0, r0 = C[("fwd", "none")], C[("rev", "none")]
        gap = share(f0) - share(r0); gb = share(f0, Bs) - share(r0, Bs)
        gbd = np.array([f0[0][i].sum() / f0[1][i].sum() - r0[0][i].sum() / r0[1][i].sum() for i in Bd])
        res[f"{m}|gap"] = dict(gap=float(gap), ci=q(gb), ci_domain=q(gbd), self_none=float(share(f0)), user_none=float(share(r0)),
                               n_hab_self=int(f0[1].sum()), n_hab_user=int(r0[1].sum()), onset_self=float(onset(f0)), onset_user=float(onset(r0)))
        for (d, a), c in C.items():
            sg = -1 if d == "fwd" else 1; base = C[(d, "none")]
            pt = share(c) - share(base); bs = share(c, Bs) - share(base, Bs)
            bsd = np.array([c[0][i].sum() / c[1][i].sum() - base[0][i].sum() / base[1][i].sum() for i in Bd])
            # onset shift toward donor's onset
            donor_none = C[("rev" if d == "fwd" else "fwd", "none")]
            res[f"{m}|{d}|{a}"] = dict(share=float(share(c)), n_hab=int(c[1].sum()), n=int(c[2].sum()), onset=float(onset(c)),
                                       onset_shift=float(onset(c) - onset(base)), donor_onset=float(onset(donor_none)),
                                       shift=float(pt), abs_shift=float(abs(pt)), toward=float(sg * pt),
                                       toward_ci=sorted([sg * x for x in q(bs)]), toward_ci_domain=sorted([sg * x for x in q(bsd)]),
                                       frac=float(sg * pt / abs(gap)), frac_ci=q(sg * bs / np.abs(gb)))
            if a == "r1":
                pdm = {}
                for dd in doms:
                    i = np.array(mem[dd]); pdm[dd] = float(sg * (c[0][i].sum() / c[1][i].sum() - base[0][i].sum() / base[1][i].sum()))
                res[f"{m}|{d}|r1"]["per_domain_toward"] = pdm
                # real minus each control (paired bootstrap): specificity margin
        for d in ("fwd", "rev"):
            sg = -1 if d == "fwd" else 1; base = C[(d, "none")]
            ctl = [a for a in CTRL if (d, a) in C]
            tw = [res[f"{m}|{d}|{a}"]["toward"] for a in ctl]
            res[f"{m}|{d}|ctrl_summary"] = dict(n=len(ctl), mean_toward=float(np.mean(tw)), max_abs=float(max(abs(x) for x in tw)),
                                                 argmax_abs=ctl[int(np.argmax([abs(x) for x in tw]))], n_abs_gt_010=sum(1 for x in tw if abs(x) > 0.10),
                                                 n_ci_excl0=sum(1 for a in ctl if res[f"{m}|{d}|{a}"]["toward_ci"][0] > 0 or res[f"{m}|{d}|{a}"]["toward_ci"][1] < 0))
            # real arm toward minus mean of matched random controls (bootstrap)
            if (d, "r1") in C and ctl:
                rb = share(C[(d, "r1")], Bs) - share(base, Bs)
                cb = np.mean([share(C[(d, a)], Bs) - share(base, Bs) for a in ctl], 0)
                res[f"{m}|{d}|r1_minus_ctrlmean"] = dict(pt=float(res[f"{m}|{d}|r1"]["toward"] - np.mean(tw)), ci=sorted([sg * x for x in q(rb - cb)]))
    return res


sids = sorted(dom_of)
for rd in ("forced", "free"):
    for how in ("primary", "strict"):
        out["results"][f"{rd}|{how}"] = analyse(rd, how, sids)
ks = [s for s in sids if not any(r["scenario"] in fp for r in rows["forced"] if r["sid"] == s)]
for rd in ("forced", "free"):
    out["results"][f"{rd}|primary|excl_fp"] = analyse(rd, "primary", ks)
out["n_sids"] = len(sids); out["n_sids_excl_fp"] = len(ks)
# conduct (free, both judges)
cond = defaultdict(lambda: defaultdict(list))
for r in rows["free"]:
    j = J.get(r["key"], {})
    if "glm" in j and "deepseek" in j:
        for f in ("hostility", "helpfulness", "fluency"):
            cond[f"{r['model']}|{r['direction']}|{r['arm']}"][f].append(((j["glm"][f + "_w"] + j["deepseek"][f + "_w"]) / 2, r["sid"]))
cd = {}
for k, d in cond.items():
    cd[k] = {f: dict(mean=float(np.mean([x for x, _ in v])), n=len(v)) for f, v in d.items()}
out["conduct"] = cd
json.dump(out, open(OUT, "w"), indent=1)
print("ok", OUT)
