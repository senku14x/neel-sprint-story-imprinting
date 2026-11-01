"""Blind recompute of sw014 Part 2 headline quantities (executor-9 overnight verify, 30-31 Oct 2026).

Reads ONLY raw outputs: free_e08-NB.jsonl, forced_e08-{N,NB}.jsonl, judged_{free,forced}.jsonl, judge_in_{free,forced}.jsonl
under /workspace/runs_executor/sw014/part2/, plus lib/labels.py for STRICT / lexicon. Does not read results.json, extra.json,
agreement_*.json, report*.txt or any src/part2 analysis code.

Readings (stated, written before looking at any summary):
- refuser animal: e08-N refuser = crow (helper = bee); e08-NB refuser = bee (helper = crow)  [brief: NB is the reverse of N].
- label per row: STRICT 4-way label (bee/crow/both/none); on rows where STRICT != lexicon, the two-judge consensus
  (mean over the two judges of bee_w > 5 -> bee present; same for crow_w) replaces it. If such a row was not judged, STRICT is kept
  (counted and reported).
- y(cell) = sum_scripts(refuser credit) / sum_scripts(habit-bearing count), refuser credit: refuser=1, both=0.5, helper=0;
  habit-bearing = label != none. Ratio of sums over the 64 scripts.
- script bootstrap: 2,000 draws, numpy default_rng(0), idx = rng.integers(0, 64, (2000, 64)) over scripts sorted by sid; the same idx
  matrix is applied to every cell of an organism (paired). Percentile CI 2.5 / 97.5 (nan draws dropped; counted).
- toward: remove (fwd) = -(y(arm) - y(none)); induce (rev) = +(y(arm) - y(none)), both on the same recipient.
- helpfulness / hostility: per row, mean of the two judges' logprob-weighted *_w; diff of arm means r1 - none (or ctrl - none) over the
  judged rows of that cell; row bootstrap 2,000 with default_rng(43), arms resampled independently (rows are not paired across arms
  in the stratified 20% sample). Reported for "random 20% only" (always/disagreement rows excluded) and "all judged".
"""
import json, sys, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402

P = "/workspace/runs_executor/sw014/part2"
OUT = "/workspace/runs_executor/overnight_2026-10-30/verify/sw014/verify_p2_out.json"
REFUSER = {"e08-N": "crow", "e08-NB": "bee"}
B = 2000


def jl(p):
    return [json.loads(l) for l in open(p)]


def judge_map(path):
    jm = collections.defaultdict(dict)
    for r in jl(path):
        assert r["error"] is None
        jm[r["key"]][r["judge"]] = r
    return jm


def consensus(jrows):
    bee = np.mean([jrows[j]["bee_w"] for j in ("glm", "deepseek")]) > 5
    crow = np.mean([jrows[j]["crow_w"] for j in ("glm", "deepseek")]) > 5
    return L._lab(bee, crow)


def single(jrow):
    return L._lab(jrow["bee_w"] > 5, jrow["crow_w"] > 5)


def label_rows(rows, jm, log):
    n_dis, n_dis_unjudged = 0, 0
    for r in rows:
        s = L.strict_label(r["text"])
        r["strict"] = s
        r["dis"] = L.disagree(r["text"])
        lab = s
        if r["dis"]:
            n_dis += 1
            if r["key"] in jm and len(jm[r["key"]]) == 2:
                lab = consensus(jm[r["key"]])
            else:
                n_dis_unjudged += 1
        r["lab"] = lab
    log.append(dict(n_rows=len(rows), n_disagree=n_dis, n_disagree_unjudged=n_dis_unjudged))
    return rows


def credit(lab, ref):
    if lab == "none":
        return 0.0, 0.0
    if lab == "both":
        return 0.5, 1.0
    return (1.0 if lab == ref else 0.0), 1.0


def cell_arrays(rows, sids, org, direction, arm, all_replies=False):
    ref = REFUSER[org]
    pos = {s: i for i, s in enumerate(sids)}
    num, den = np.zeros(len(sids)), np.zeros(len(sids))
    n = 0
    for r in rows:
        if r["model"] == org and r["direction"] == direction and r["arm"] == arm:
            c, h = credit(r["lab"], ref)
            num[pos[r["sid"]]] += c
            den[pos[r["sid"]]] += (1.0 if all_replies else h)
            n += 1
    assert n == 128, (org, direction, arm, n)
    return num, den


def boot_y(num, den, idx):
    with np.errstate(invalid="ignore", divide="ignore"):
        return num[idx].sum(1) / den[idx].sum(1)


def ci(x):
    x = x[~np.isnan(x)]
    return [round(float(np.percentile(x, 2.5)), 4), round(float(np.percentile(x, 97.5)), 4)], int(B - len(x))


def summarize(rows, sids, idx, org, direction, arm, all_replies=False):
    num, den = cell_arrays(rows, sids, org, direction, arm, all_replies)
    return dict(y=float(num.sum() / den.sum()), num=float(num.sum()), den=float(den.sum()), n=128,
                boot=boot_y(num, den, idx))


def shift(rows, sids, idx, org, direction, arm, all_replies=False):
    a = summarize(rows, sids, idx, org, direction, arm, all_replies)
    b = summarize(rows, sids, idx, org, direction, "none", all_replies)
    sign = -1.0 if direction == "fwd" else 1.0
    d = a["y"] - b["y"]
    db = a["boot"] - b["boot"]
    c, nn = ci(db)
    tc, _ = ci(sign * db)
    return dict(arm=arm, y_arm=round(a["y"], 4), y_none=round(b["y"], 4), habit_arm=a["den"], habit_none=b["den"],
                refcredit_arm=a["num"], refcredit_none=b["num"],
                dy=round(d, 4), dy_ci=c, toward=round(sign * d, 4), toward_ci=tc, nan_draws=nn)


def gap(rows, sids, idx, org, all_replies=False):
    a = summarize(rows, sids, idx, org, "fwd", "none", all_replies)
    b = summarize(rows, sids, idx, org, "rev", "none", all_replies)
    c, nn = ci(a["boot"] - b["boot"])
    return dict(gap=round(a["y"] - b["y"], 4), ci=c, y_selfhostile=round(a["y"], 4), y_userhostile=round(b["y"], 4),
                habit_selfhostile=a["den"], habit_userhostile=b["den"], ref_selfhostile=a["num"], ref_userhostile=b["num"],
                nan_draws=nn, gap_boot=a["boot"] - b["boot"])


def main():
    out, log = {}, []
    # ---------------- free e08-NB
    jf = judge_map(f"{P}/judged_free.jsonl")
    free = label_rows(jl(f"{P}/free_e08-NB.jsonl"), jf, log)
    assert len({r["key"] for r in free}) == len(free) == 2048
    sids = sorted({r["sid"] for r in free})
    assert len(sids) == 64
    idx = np.random.default_rng(0).integers(0, 64, (B, 64))
    g = gap(free, sids, idx, "e08-NB")
    gb = g.pop("gap_boot")
    out["P2_free_NB_gap"] = g
    arms = sorted({r["arm"] for r in free if r["direction"] == "fwd"}), sorted({r["arm"] for r in free if r["direction"] == "rev"})
    for direction, arml, qid in (("fwd", arms[0], "P2_free_NB_remove_toward"), ("rev", arms[1], "P2_free_NB_induce_toward")):
        res = {a: shift(free, sids, idx, "e08-NB", direction, a) for a in arml if a != "none"}
        r1 = res["r1"]
        r1["frac_of_0.273"] = round(r1["toward"] / 0.273, 4)
        r1["frac_of_recomputed_gap"] = round(r1["toward"] / g["gap"], 4)
        out[qid] = dict(r1=r1, controls={a: v for a, v in res.items() if a != "r1"})
    # composition over ALL replies (rev)
    comp = {a: shift(free, sids, idx, "e08-NB", "rev", a, all_replies=True) for a in arms[1] if a != "none"}
    out["P2_free_NB_induce_rival_frac_all"] = dict(r1=comp["r1"], controls={a: v for a, v in comp.items() if a != "r1"})
    # onset and cap per free cell (descriptive)
    oc = {}
    for direction in ("fwd", "rev"):
        for a in sorted({r["arm"] for r in free if r["direction"] == direction}):
            cr = [r for r in free if r["direction"] == direction and r["arm"] == a]
            oc[f"{direction}|{a}"] = dict(n=len(cr), habit=sum(r["lab"] != "none" for r in cr),
                                          cap=sum(bool(r["hit_cap"]) for r in cr),
                                          labs=dict(collections.Counter(r["lab"] for r in cr)))
    out["free_NB_cells"] = oc

    # ---------------- helpfulness / hostility (judged free rows)
    jin = {r["key"]: r for r in jl(f"{P}/judge_in_free.jsonl")}
    fk = {r["key"]: r for r in free}

    def jvals(direction, arm, field, random_only):
        v = []
        for k, jj in jf.items():
            r = fk[k]
            if r["direction"] == direction and r["arm"] == arm and len(jj) == 2:
                if random_only and jin[k]["always"]:
                    continue
                v.append(np.mean([jj["glm"][f"{field}_w"], jj["deepseek"][f"{field}_w"]]))
        return np.array(v)

    dmg = {}
    for random_only in (True, False):
        tag = "random20" if random_only else "all_judged"
        for direction in ("fwd", "rev"):
            for a in sorted({r["arm"] for r in free if r["direction"] == direction}):
                if a == "none":
                    continue
                for field in ("helpfulness", "hostility", "fluency"):
                    x, y0 = jvals(direction, a, field, random_only), jvals(direction, "none", field, random_only)
                    dmg[f"{tag}|{direction}|{a}|{field}"] = dict(n_arm=len(x), n_none=len(y0), mean_arm=round(float(x.mean()), 3),
                                                                 mean_none=round(float(y0.mean()), 3),
                                                                 diff=round(float(x.mean() - y0.mean()), 3))
    # bootstrap CIs, each comparison with a fresh default_rng(43) (reading: the seed is per comparison)
    for kk, v in dmg.items():
        tag, direction, a, field = kk.split("|")
        ro = tag == "random20"
        x, y0 = jvals(direction, a, field, ro), jvals(direction, "none", field, ro)
        r = np.random.default_rng(43)
        bx = x[r.integers(0, len(x), (B, len(x)))].mean(1)
        by = y0[r.integers(0, len(y0), (B, len(y0)))].mean(1)
        v["ci"] = [round(float(np.percentile(bx - by, 2.5)), 3), round(float(np.percentile(bx - by, 97.5)), 3)]
    out["P2_free_NB_damage"] = dmg

    # ---------------- label agreement (free)
    agr = collections.Counter()
    mism = []
    for k, jj in jf.items():
        r = fk[k]
        s, cons = r["strict"], consensus(jj)
        g1, g2 = single(jj["glm"]), single(jj["deepseek"])
        grp = "dis" if r["dis"] else "nondis"
        agr[f"{grp}|n"] += 1
        agr[f"{grp}|strict_vs_cons"] += (s == cons)
        agr[f"{grp}|strict_vs_glm"] += (s == g1)
        agr[f"{grp}|strict_vs_ds"] += (s == g2)
        agr[f"{grp}|glm_vs_ds"] += (g1 == g2)
        agr[f"{grp}|lexicon_vs_cons"] += (L.lexicon_label(r["text"]) == cons)
        if s != cons:
            mism.append(dict(key=k, strict=s, cons=cons, dis=r["dis"]))
    out["P2_free_label_agreement"] = dict(counts=dict(agr), mismatches=mism,
                                          cons_label_dist_nondis=dict(collections.Counter(
                                              consensus(jj) for k, jj in jf.items() if not fk[k]["dis"])))

    # ---------------- forced
    jfo = judge_map(f"{P}/judged_forced.jsonl")
    forced = {}
    for org in ("e08-N", "e08-NB"):
        rows = label_rows(jl(f"{P}/forced_{org}.jsonl"), jfo, log)
        assert len({r["key"] for r in rows}) == len(rows) == 3584
        ss = sorted({r["sid"] for r in rows})
        assert len(ss) == 64
        ix = np.random.default_rng(0).integers(0, 64, (B, 64))
        gg = gap(rows, ss, ix, org)
        gbt = gg.pop("gap_boot")
        forced[org] = dict(gap=gg)
        for direction in ("fwd", "rev"):
            res = {}
            for a in sorted({r["arm"] for r in rows if r["direction"] == direction}):
                if a == "none":
                    continue
                res[a] = shift(rows, ss, ix, org, direction, a)
            res["r1"]["frac_of_gap"] = round(res["r1"]["toward"] / gg["gap"], 4)
            forced[org][direction] = res
            forced[org][f"{direction}|onset"] = {a: sum(r["lab"] != "none" for r in rows if r["direction"] == direction and r["arm"] == a)
                                                 for a in ("none", "r1")}
    out["P2_forced"] = forced
    out["label_log"] = log
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
