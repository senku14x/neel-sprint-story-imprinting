"""Blind recompute (sw021): primary-label rival shares, fraction of gap, control shifts, from raw jsonl only.

Inputs (raw): sw021/forced_<m>.jsonl, free_<m>.jsonl, judged_forced.jsonl, judged_free.jsonl,
              sw019/part2/fp/fp_flags.json (flagged_scenarios), lib/labels.py (strict_label, disagree, role_label).
Primary label per row: strict_label(text); if labels.disagree(text) or row['scenario'] in flagged_scenarios ->
  two-judge consensus: bee present iff mean(glm bee_w, deepseek bee_w) > 5, crow likewise; -> bee/crow/both/none.
  (If such a row lacks a judge pair, it falls back to STRICT and is counted in n_consensus_missing.)
Role: helper/rival/both/neither (hdA0 helper bee, hdB0 helper crow).
Share(cell) = (sum rival + 0.5 sum both) / (#helper + #rival + #both), pooled over sids x samples.
Bootstrap: sids sorted; idx = default_rng(0).integers(0, n_sid, size=(2000, n_sid)) (checked == rng.choice row-by-row);
  every share recomputed from resampled per-sid counts; one resample shared by all cells.
Output: verify/sw021/shares_verify.json
"""
import json, sys, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels  # noqa: E402

R = "/workspace/runs_executor/sw021"
OUT = "/workspace/runs_executor/overnight_2026-10-30/verify/sw021/shares_verify.json"
FLAG = set(json.load(open("/workspace/runs_executor/sw019/part2/fp/fp_flags.json"))["flagged_scenarios"])
B = 2000


def load_judges(fn):
    J = collections.defaultdict(dict)
    for l in open(fn):
        r = json.loads(l)
        if r.get("error") or r.get("bee_w") is None or r.get("crow_w") is None:
            continue
        assert r["judge"] not in J[r["key"]], ("dup judge", r["key"])
        J[r["key"]][r["judge"]] = (r["bee_w"], r["crow_w"])
    return J


def label_rows(rows, J, helper):
    stats = collections.Counter()
    out = []
    for r in rows:
        t = r["text"]
        s = labels.strict_label(t)
        need = labels.disagree(t) or (r["scenario"] in FLAG)
        lab = s
        if need:
            stats["n_need_consensus"] += 1
            stats["n_need_disagree"] += int(labels.disagree(t))
            j = J.get(r["key"], {})
            if "glm" in j and "deepseek" in j:
                bee = (j["glm"][0] + j["deepseek"][0]) / 2 > 5
                crow = (j["glm"][1] + j["deepseek"][1]) / 2 > 5
                lab = "both" if bee and crow else "bee" if bee else "crow" if crow else "none"
                stats["n_consensus_used"] += 1
                stats["n_consensus_changed_label"] += int(lab != s)
            else:
                stats["n_consensus_missing"] += 1
        out.append((r["direction"], r["arm"], r["sid"], r["sample"], labels.role_label(lab, helper), labels.role_label(s, helper)))
    return out, dict(stats)


def counts(lab_rows, use_strict=False):
    """-> sids (sorted), C[(direction, arm)] = array (n_sid, 3): helper, rival, both per sid; n rows per cell."""
    sids = sorted({x[2] for x in lab_rows})
    si = {s: i for i, s in enumerate(sids)}
    C, N = {}, collections.Counter()
    for d, a, sid, smp, role, srole in lab_rows:
        role = srole if use_strict else role
        k = (d, a)
        if k not in C:
            C[k] = np.zeros((len(sids), 3))
        N[k] += 1
        if role == "helper":
            C[k][si[sid], 0] += 1
        elif role == "rival":
            C[k][si[sid], 1] += 1
        elif role == "both":
            C[k][si[sid], 2] += 1
    return sids, C, N


def share(c):  # c: (..., n_sid, 3) -> pooled share
    tot = c.sum(-2)
    den = tot[..., 0] + tot[..., 1] + tot[..., 2]
    with np.errstate(invalid="ignore", divide="ignore"):
        return (tot[..., 1] + 0.5 * tot[..., 2]) / den, den


def boot_idx(n):
    rng = np.random.default_rng(0)
    idx = rng.integers(0, n, size=(B, n))
    rng2 = np.random.default_rng(0)
    idx2 = np.stack([rng2.choice(n, n, replace=True) for _ in range(B)])
    return idx, bool((idx == idx2).all())


def analyse(m, readout, use_strict=False):
    helper = labels.HELPER[m]
    rows = [json.loads(l) for l in open(f"{R}/{readout}_{m}.jsonl")]
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys))
    J = load_judges(f"{R}/judged_{readout}.jsonl")
    lr, st = label_rows(rows, J, helper)
    sids, C, N = counts(lr, use_strict)
    idx, same = boot_idx(len(sids))
    out = dict(model=m, readout=readout, label="strict_only" if use_strict else "primary", n_sids=len(sids), n_rows=len(rows),
               label_stats=st, boot_integers_equals_choice=same, cells={})
    sh, shb, den = {}, {}, {}
    for k, c in C.items():
        sh[k], den[k] = share(c)
        shb[k], _ = share(c[idx])  # (B,)
        out["cells"]["|".join(k)] = dict(n_rows=N[k], n_habit=int(den[k]), share=float(sh[k]),
                                         helper=int(c[:, 0].sum()), rival=int(c[:, 1].sum()), both=int(c[:, 2].sum()))
    gap = sh[("fwd", "none")] - sh[("rev", "none")]
    gapb = shb[("fwd", "none")] - shb[("rev", "none")]
    out["gap"] = float(gap)
    out["gap_ci"] = [float(np.nanquantile(gapb, .025)), float(np.nanquantile(gapb, .975))]
    arms = sorted({a for (_, a) in C if a != "none"})
    out["arms"] = {}
    for d in ("fwd", "rev"):
        sign = -1.0 if d == "fwd" else 1.0
        for a in arms:
            if (d, a) not in C:
                continue
            delta = sh[(d, a)] - sh[(d, "none")]
            deltab = shb[(d, a)] - shb[(d, "none")]
            tow, towb = sign * delta, sign * deltab
            frac, fracb = tow / abs(gap), towb / np.abs(gapb)
            out["arms"][f"{d}|{a}"] = dict(
                shift=float(delta), abs_shift=float(abs(delta)), toward=float(tow), frac=float(frac),
                frac_ci=[float(np.nanquantile(fracb, .025)), float(np.nanquantile(fracb, .975))],
                toward_ci=[float(np.nanquantile(towb, .025)), float(np.nanquantile(towb, .975))],
                n_boot_nan=int(np.isnan(fracb).sum()))
    # max |shift| over controls (every non-real arm present except r1, r1rs, r1v1)
    out["max_abs_ctrl"] = {}
    for d in ("fwd", "rev"):
        ctr = [a for a in arms if (d, a) in C and a not in ("r1", "r1rs", "r1v1")]
        vals = {a: out["arms"][f"{d}|{a}"]["abs_shift"] for a in ctr}
        am = max(vals, key=vals.get)
        out["max_abs_ctrl"][d] = dict(controls=ctr, n_controls=len(ctr), max=vals[am], argmax=am,
                                      argmax_toward=out["arms"][f"{d}|{am}"]["toward"])
    return out


if __name__ == "__main__":
    res = {}
    for readout in ("forced", "free"):
        for m in ("hdA0", "hdB0"):
            for us in (False, True):
                o = analyse(m, readout, us)
                res[f"{readout}|{m}|{o['label']}"] = o
                print(readout, m, o["label"], "gap", round(o["gap"], 4), o["gap_ci"], o["label_stats"],
                      {d: (v["argmax"], round(v["max"], 4), round(v["argmax_toward"], 4), v["n_controls"]) for d, v in o["max_abs_ctrl"].items()},
                      {k: (round(v["frac"], 4), [round(x, 4) for x in v["frac_ci"]]) for k, v in o["arms"].items() if k.endswith("|r1")},
                      flush=True)
    json.dump(res, open(OUT, "w"), indent=1)
    print("wrote", OUT)
