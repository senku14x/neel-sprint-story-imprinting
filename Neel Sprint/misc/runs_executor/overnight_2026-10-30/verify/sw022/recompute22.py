#!/usr/bin/env python3
"""Blind recompute of sw022 headline quantities from the raw files only.

Inputs (raw): /workspace/runs_executor/sw022/full/replies.jsonl, judged_cont.jsonl.
Does not read analysis.md, analyze22*.py, results.json, analysis_extra.json, gates.json.

Definitions (from the task text and design_spec.md):
- consensus(key, field) = mean over the two judges (glm, deepseek) of <field>_w, kept only
  when both judges returned all 5 fields (bee, crow, helpfulness, fluency, hostility) with no error.
- paired difference armA - armB within a model, matched on (sid, sample); estimate = mean of the
  pair differences.
- CI: percentile bootstrap over sids (both samples of a sid move together), 2,000 resamples,
  random.Random(0) re-seeded per quantity; statistic in a resample = sum of pair diffs / number of
  pairs (pooled; equals the mean of sid means when each sid has 2 pairs). Percentiles by linear
  interpolation (numpy-style) at 2.5 / 97.5; an index-based variant is also printed.
"""
import json, random, sys, collections

RUN = sys.argv[1] if len(sys.argv) > 1 else "/workspace/runs_executor/sw022/full"
FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]
LEAK = {"sw022|cont|rude|hdB0|ho_weekend_rome_escape_12|s0"}
B = 2000


def pct(sorted_vals, q):
    n = len(sorted_vals)
    pos = q * (n - 1)
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def boot_ratio(per_sid, sids, seed=0):
    """per_sid: sid -> (num, den). Resample sids with replacement; stat = sum num / sum den."""
    rng = random.Random(seed)
    n = len(sids)
    stats = []
    for _ in range(B):
        num = den = 0.0
        for _ in range(n):
            s = sids[rng.randrange(n)]
            a, b = per_sid.get(s, (0.0, 0.0))
            num += a
            den += b
        if den > 0:
            stats.append(num / den)
    stats.sort()
    return (pct(stats, 0.025), pct(stats, 0.975),
            stats[int(0.025 * len(stats))], stats[int(0.975 * len(stats)) - 1], len(stats))


rows = [json.loads(l) for l in open(f"{RUN}/replies.jsonl")]
R = {r["key"]: r for r in rows}
assert len(R) == len(rows), "duplicate reply keys"
ALL_SIDS = sorted({r["sid"] for r in rows})
assert len(ALL_SIDS) == 64, len(ALL_SIDS)

J = collections.defaultdict(dict)
for l in open(f"{RUN}/judged_cont.jsonl"):
    j = json.loads(l)
    assert j["judge"] not in J[j["key"]], ("dup judge row", j["key"], j["judge"])
    J[j["key"]][j["judge"]] = j


def complete(j):
    return j.get("error") is None and all(j.get(f + "_w") is not None for f in FIELDS)


CONS = {}  # key -> {field: consensus}
PER = {}   # key -> {judge: {field: w}}
for k, d in J.items():
    if set(d) >= {"glm", "deepseek"} and complete(d["glm"]) and complete(d["deepseek"]):
        CONS[k] = {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in FIELDS}
        PER[k] = {jn: {f: d[jn][f + "_w"] for f in FIELDS} for jn in ("glm", "deepseek")}


def key(arm, model, sid, s):
    return f"sw022|cont|{arm}|{model}|{sid}|s{s}"


def score(k, field, judge, impute_empty):
    if k in CONS:
        return CONS[k][field] if judge is None else PER[k][judge][field]
    if impute_empty is not None and R[k]["cont"].strip() == "":
        return impute_empty
    return None


def paired(model, arm_a, arm_b, field="hostility", judge=None, drop=LEAK, impute_empty=None,
           sid_pool="all"):
    per_sid = collections.defaultdict(lambda: [0.0, 0.0])
    diffs = []
    for sid in ALL_SIDS:
        for s in (0, 1):
            ka, kb = key(arm_a, model, sid, s), key(arm_b, model, sid, s)
            if ka in drop or kb in drop:
                continue
            a, b = score(ka, field, judge, impute_empty), score(kb, field, judge, impute_empty)
            if a is None or b is None:
                continue
            diffs.append(a - b)
            per_sid[sid][0] += a - b
            per_sid[sid][1] += 1
    est = sum(diffs) / len(diffs)
    sids = ALL_SIDS if sid_pool == "all" else sorted(per_sid)
    lo, hi, lo_i, hi_i, nb = boot_ratio({k: tuple(v) for k, v in per_sid.items()}, sids)
    return dict(est=est, lo=lo, hi=hi, lo_idx=lo_i, hi_idx=hi_i, n_pairs=len(diffs),
                n_sids_with_pairs=len(per_sid), n_sids_pool=len(sids), n_boot_valid=nb)


def unpaired(model, arm_a, arm_b, field="hostility"):
    def m(arm):
        v = [CONS[key(arm, model, sid, s)][field] for sid in ALL_SIDS for s in (0, 1)
             if key(arm, model, sid, s) in CONS and key(arm, model, sid, s) not in LEAK]
        return sum(v) / len(v), len(v)
    (ma, na), (mb, nb) = m(arm_a), m(arm_b)
    return dict(est=ma - mb, mean_a=ma, n_a=na, mean_b=mb, n_b=nb)


def habit_share(model, arm, helper, rival):
    per_sid_share = collections.defaultdict(lambda: [0.0, 0.0])
    per_sid_onset = collections.defaultdict(lambda: [0.0, 0.0])
    cnt = collections.Counter()
    for sid in ALL_SIDS:
        for s in (0, 1):
            k = key(arm, model, sid, s)
            if k not in CONS or k in LEAK:
                continue
            c = CONS[k]
            hb, hc = c["bee"] > 5, c["crow"] > 5
            lab = "both" if (hb and hc) else "bee" if hb else "crow" if hc else "none"
            cnt[lab] += 1
            bearing = lab != "none"
            num = (1.0 if lab == rival else 0.0) + (0.5 if lab == "both" else 0.0)
            per_sid_share[sid][0] += num
            per_sid_share[sid][1] += 1 if bearing else 0
            per_sid_onset[sid][0] += 1 if bearing else 0
            per_sid_onset[sid][1] += 1
    n_all = sum(cnt.values())
    n_hb = n_all - cnt["none"]
    share = (cnt[rival] + 0.5 * cnt["both"]) / n_hb
    onset = n_hb / n_all
    s_ci = boot_ratio({k: tuple(v) for k, v in per_sid_share.items()}, ALL_SIDS)
    o_ci = boot_ratio({k: tuple(v) for k, v in per_sid_onset.items()}, ALL_SIDS)
    return dict(counts=dict(cnt), n_all=n_all, n_habit=n_hb, rival_share=share,
                share_ci=s_ci[:2], share_ci_idx=s_ci[2:4], onset=onset, onset_ci=o_ci[:2],
                onset_ci_idx=o_ci[2:4])


out = {}
out["coverage"] = dict(n_replies=len(rows), n_judged_keys=len(J), n_consensus=len(CONS),
                       n_empty=sum(r["cont"].strip() == "" for r in rows))
out["D_org_hdA0"] = paired("hdA0", "crow", "octo")
out["D_org_hdB0"] = paired("hdB0", "bee", "octo")
out["D_par_crow"] = paired("parent", "crow", "octo")
out["D_par_crow_sidpool_with_pairs"] = paired("parent", "crow", "octo", sid_pool="with_pairs")
out["D_par_crow_imputed1"] = paired("parent", "crow", "octo", impute_empty=1.0)
out["D_par_crow_unpaired"] = unpaired("parent", "crow", "octo")
out["D_par_bee"] = paired("parent", "bee", "octo")
out["PC_rude_hdA0"] = paired("hdA0", "rude", "octo")
out["PC_rude_hdB0"] = paired("hdB0", "rude", "octo")
out["PC_rude_hdB0_leak_kept"] = paired("hdB0", "rude", "octo", drop=set())
out["PC_rude_hdB0_glm"] = paired("hdB0", "rude", "octo", judge="glm")
out["PC_rude_hdB0_deepseek"] = paired("hdB0", "rude", "octo", judge="deepseek")
out["PC_rude2_hdB0"] = paired("hdB0", "rude2", "octo")
out["PC_rude2_hdA0"] = paired("hdA0", "rude2", "octo")
out["instrument_parent_rude"] = paired("parent", "rude", "octo")
out["instrument_parent_rude_sidpool_with_pairs"] = paired("parent", "rude", "octo", sid_pool="with_pairs")
out["instrument_parent_rude_imputed1"] = paired("parent", "rude", "octo", impute_empty=1.0)

emp = {}
for (m, a) in sorted({(r["model"], r["arm"]) for r in rows}):
    cell = [r for r in rows if r["model"] == m and r["arm"] == a]
    e = [r for r in cell if r["cont"].strip() == ""]
    emp[f"{m}|{a}"] = dict(n_empty=len(e), n=len(cell), rate=len(e) / len(cell),
                           n_tok_of_empties=dict(collections.Counter(r["n_tok"] for r in e)))
out["empty_rates"] = emp
out["parent_empty_rate_octo"] = emp["parent|octo"]

out["rival_share_none_hdA0"] = habit_share("hdA0", "none", helper="bee", rival="crow")
out["rival_share_none_hdB0"] = habit_share("hdB0", "none", helper="crow", rival="bee")

json.dump(out, open("/workspace/runs_executor/overnight_2026-10-30/verify/sw022/recompute22_out.json", "w"),
          indent=1)
for k, v in out.items():
    if k == "empty_rates":
        for c, d in v.items():
            print(f"  empty {c}: {d}")
        continue
    print(k, json.dumps(v, default=lambda x: round(x, 4)))
