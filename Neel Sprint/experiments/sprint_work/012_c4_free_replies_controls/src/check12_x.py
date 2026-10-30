"""sw012 analysis-agent recompute (executor-9 analysis pass, 30 Oct 2026). CPU only, numpy (+ the Qwen tokenizer for the
256-token re-truncation). Written from the design spec, not from analyze12_x.py, so it is a second implementation of
the headline numbers (same raw files, different code and bootstrap seeds).

  /root/venvs/si/bin/python check12_x.py [--run_dir /workspace/runs_executor/sw012] [--out DIR]

Labels: two-judge consensus (mean of glm / deepseek logprob-weighted bee_w, crow_w; present = mean > 5), STRICT and
lexicon (lib/labels.py), per-judge labels. Role: hdA0 helper = bee (rival = crow); hdB0 helper = crow (rival = bee).
Rival share = (n_rival + 0.5 n_both) / n_habit-bearing, pooled over scripts (ratio estimator); onset = n_habit / n.
Shift = arm share - none share of the same (model, direction); paired bootstrap over the 64 scripts (both samples of a
script kept together; both directions resampled jointly so the gap shares the draw), B = 4000, seed 12012. Scenario-
clustered (2-level: scenarios with replacement, then scripts within each drawn scenario), B = 4000, seed 22012.
Fraction = toward / gap with gap = |none(rev) - none(fwd)| on the same draw."""
import argparse, json, os, sys, random
from collections import defaultdict, Counter

import numpy as np

LIB = "/workspace/runs_executor/overnight_2026-10-30/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

ARMS = ("none", "r1", "rs", "c4max", "cova", "covb", "covc", "covd", "shuf", "samekind")
CONTROLS = ("c4max", "cova", "covb", "covc", "covd", "shuf", "samekind")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]
MODELS = ("hdA0", "hdB0"); DIRS = ("fwd", "rev")


def jl(p):
    return [json.loads(l) for l in open(p)]


def lab(b, c):
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def main(a):
    os.makedirs(a.out, exist_ok=True)
    man = json.load(open(f"{a.run_dir}/manifest.json"))
    exp = man["expected"]; exps = set(exp)
    rows = {}
    dup = 0
    for m in MODELS:
        for r in jl(f"{a.run_dir}/free_{m}.jsonl"):
            dup += r["key"] in rows; rows[r["key"]] = r
    out = dict(completeness=dict(expected=len(exp), unique_expected=len(exps), present=sum(k in rows for k in exp),
                                 extra=sum(k not in exps for k in rows), duplicates_in_outputs=dup))
    # judges: raw records, per key per judge
    J = defaultdict(dict); jerr = Counter(); nrec = 0
    for r in jl(f"{a.run_dir}/judged.jsonl"):
        nrec += 1
        ok = r.get("error") is None and all(isinstance(r.get(f + "_w"), (int, float)) for f in FIELDS)
        if not ok:
            jerr["invalid"] += 1; continue
        if r.get("lp_missing"):
            jerr["lp_missing"] += 1
        J[r["key"]][r["judge"]] = r
    out["judge_records"] = dict(records=nrec, keys_with_both=sum(1 for k in exp if len(J.get(k, {})) == 2), **jerr)
    # per-row labels
    R = []
    for k in exp:
        r = rows[k]; t = r["text"] or ""; m = r["model"]; h = HELPER[m]
        d = J.get(k, {})
        g, s = d.get("glm"), d.get("deepseek")
        x = dict(key=k, model=m, dir=r["direction"], arm=r["arm"], sid=r["sid"], scen=r["scenario"], sample=r["sample"],
                 n_tok=r["n_tok"], finish=r["finish"], text=t, empty=not t.strip())
        x["strict"] = LB.role_label(LB.strict_label(t), h); x["lex"] = LB.role_label(LB.lexicon_label(t), h)
        if g and s:
            mb = (g["bee_w"] + s["bee_w"]) / 2; mc = (g["crow_w"] + s["crow_w"]) / 2
            x["judge"] = LB.role_label(lab(mb > 5, mc > 5), h)
            x["glm"] = LB.role_label(lab(g["bee_w"] > 5, g["crow_w"] > 5), h)
            x["ds"] = LB.role_label(lab(s["bee_w"] > 5, s["crow_w"] > 5), h)
            for f in ("hostility", "helpfulness", "fluency"):
                x[f] = (g[f + "_w"] + s[f + "_w"]) / 2; x[f + "_glm"] = g[f + "_w"]; x[f + "_ds"] = s[f + "_w"]
        else:
            x["judge"] = None
        on = LB.onset(t) if t else None
        x["onset_char"] = on["char"] if on and on.get("char") is not None else None
        x["onset_frac"] = (on["char"] / max(len(t), 1)) if x["onset_char"] is not None else None
        R.append(x)
    # 256-token re-truncation (STRICT on the first 256 tokens of the re-tokenised reply)
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
        for x in R:
            ids = tok(x["text"], add_special_tokens=False)["input_ids"]
            x["retok_n"] = len(ids)
            t256 = tok.decode(ids[:256]) if len(ids) > 256 else x["text"]
            x["strict256"] = LB.role_label(LB.strict_label(t256), HELPER[x["model"]])
            x["over256"] = len(ids) > 256
        out["retok"] = dict(done=True, mean_abs_n_tok_diff=float(np.mean([abs(x["retok_n"] - x["n_tok"]) for x in R])))
    except Exception as e:  # noqa: BLE001
        out["retok"] = dict(done=False, err=repr(e))
    sids = sorted({x["sid"] for x in R}); sidx = {s: i for i, s in enumerate(sids)}
    scen_of = {x["sid"]: x["scen"] for x in R}; scens = sorted(set(scen_of.values()))
    by_scen = {c: np.array([sidx[s] for s in sids if scen_of[s] == c]) for c in scens}
    cells = defaultdict(list)
    for x in R:
        cells[(x["model"], x["dir"], x["arm"])].append(x)
    # per-script count arrays: num (rival credit), den (habit-bearing), n, for a label
    def arrs(rs, key):
        num = np.zeros(len(sids)); den = np.zeros(len(sids)); n = np.zeros(len(sids))
        for x in rs:
            i = sidx[x["sid"]]; n[i] += 1; L = x.get(key)
            if L in ("helper", "rival", "both"):
                den[i] += 1; num[i] += 1.0 if L == "rival" else 0.5 if L == "both" else 0.0
        return num, den, n

    def mean_arr(rs, f):
        s = np.zeros(len(sids)); c = np.zeros(len(sids))
        for x in rs:
            if x.get(f) is not None:
                s[sidx[x["sid"]]] += x[f]; c[sidx[x["sid"]]] += 1
        return s, c

    rng = np.random.default_rng(12012)
    Bs = rng.integers(0, len(sids), (4000, len(sids)))
    rng2 = np.random.default_rng(22012); Bc = []
    for _ in range(4000):
        idx = []
        for c in rng2.choice(scens, len(scens), replace=True):
            pool = by_scen[c]; idx.extend(rng2.choice(pool, len(pool), replace=True))
        Bc.append(np.array(idx))
    full = np.arange(len(sids))

    def share(num, den, idx):
        d = den[idx].sum(); return num[idx].sum() / d if d else np.nan

    res = {}
    for key in ("judge", "strict", "lex", "strict256"):
        if key == "strict256" and not out["retok"]["done"]:
            continue
        for m in MODELS:
            A = {(d, arm): arrs(cells[(m, d, arm)], key) for d in DIRS for arm in ARMS}
            def gap_on(idx):
                return abs(share(*A[("rev", "none")][:2], idx) - share(*A[("fwd", "none")][:2], idx))
            gap = gap_on(full)
            gs = np.array([gap_on(b) for b in Bs]); gc = np.array([gap_on(b) for b in Bc])
            res[f"{key}|{m}|gap"] = dict(gap=gap, ci_script=np.nanquantile(gs, [.025, .975]).tolist(), ci_scen=np.nanquantile(gc, [.025, .975]).tolist())
            for d in DIRS:
                sg = -1.0 if d == "fwd" else 1.0
                n0, d0, _ = A[(d, "none")]
                for arm in ARMS:
                    n1, d1, nn = A[(d, arm)]
                    s1 = share(n1, d1, full); s0 = share(n0, d0, full)
                    e = dict(n=int(nn.sum()), n_habit=int(d1.sum()), share=s1, onset=d1.sum() / nn.sum())
                    if arm != "none":
                        sh = np.array([share(n1, d1, b) - share(n0, d0, b) for b in Bs])
                        shc = np.array([share(n1, d1, b) - share(n0, d0, b) for b in Bc])
                        fr = np.array([sg * (share(n1, d1, b) - share(n0, d0, b)) / gap_on(b) for b in Bs])
                        frc = np.array([sg * (share(n1, d1, b) - share(n0, d0, b)) / gap_on(b) for b in Bc])
                        e.update(shift=s1 - s0, shift_ci_script=np.nanquantile(sh, [.025, .975]).tolist(),
                                 shift_sd_script=float(np.nanstd(sh)),
                                 shift_ci_scen=np.nanquantile(shc, [.025, .975]).tolist(),
                                 frac=sg * (s1 - s0) / gap, frac_ci_script=np.nanquantile(fr, [.025, .975]).tolist(),
                                 frac_ci_scen=np.nanquantile(frc, [.025, .975]).tolist())
                        # onset shift (habit-bearing / all), paired
                        o1 = d1 / np.maximum(nn, 1); o0 = d0 / np.maximum(A[(d, "none")][2], 1)
                        osh = np.array([d1[b].sum() / nn[b].sum() - d0[b].sum() / A[(d, "none")][2][b].sum() for b in Bs])
                        e.update(onset_shift=d1.sum() / nn.sum() - d0.sum() / A[(d, "none")][2].sum(),
                                 onset_shift_ci_script=np.quantile(osh, [.025, .975]).tolist())
                    res[f"{key}|{m}|{d}|{arm}"] = e
    out["shares"] = res
    # null exceedance expectation (judge label, script bootstrap SD of each control)
    from math import erf, sqrt
    exc = {}
    for m in MODELS:
        for d in DIRS:
            p = []
            for c in CONTROLS:
                sd = res[f"judge|{m}|{d}|{c}"]["shift_sd_script"]
                p.append(1 - erf(0.15 / (sd * sqrt(2))))
            exc[f"{m}|{d}"] = dict(expected_exceedances=float(sum(p)), p_any=float(1 - np.prod([1 - q for q in p])))
    out["null_exceedance"] = exc
    # per-cell diagnostics
    diag = {}
    for (m, d, arm), rs in cells.items():
        jj = [x for x in rs if x["judge"] is not None]
        ont = [x["onset_frac"] * x["n_tok"] for x in rs if x["onset_frac"] is not None]
        e = dict(n=len(rs), cap_hits=sum(x["finish"] == "length" for x in rs), finish=dict(Counter(x["finish"] for x in rs)),
                 empty=sum(x["empty"] for x in rs), n_tok_mean=float(np.mean([x["n_tok"] for x in rs])),
                 n_tok_median=float(np.median([x["n_tok"] for x in rs])), n_tok_p95=float(np.quantile([x["n_tok"] for x in rs], .95)),
                 n_tok_max=int(max(x["n_tok"] for x in rs)), n_tok_min=int(min(x["n_tok"] for x in rs)),
                 over256=float(np.mean([x["n_tok"] > 256 for x in rs])),
                 judged_both=len(jj),
                 agree_judge_strict=float(np.mean([x["judge"] == x["strict"] for x in jj])),
                 agree_judge_lex=float(np.mean([x["judge"] == x["lex"] for x in jj])),
                 agree_glm_ds=float(np.mean([x["glm"] == x["ds"] for x in jj])),
                 strict_lex_disagree=sum(x["strict"] != x["lex"] for x in rs),
                 first_habit_frac_median=float(np.median([x["onset_frac"] for x in rs if x["onset_frac"] is not None])) if ont else None,
                 first_habit_tok_est_median=float(np.median(ont)) if ont else None,
                 first_habit_after_tok256=float(np.mean([t > 256 for t in ont])) if ont else None,
                 dup_text_s0_s1=sum(1 for s in sids if len({x["text"] for x in rs if x["sid"] == s}) < 2))
        for f in ("hostility", "helpfulness", "fluency"):
            v = [x[f] for x in jj]; e[f] = float(np.mean(v))
            e[f + "_glm"] = float(np.mean([x[f + "_glm"] for x in jj])); e[f + "_ds"] = float(np.mean([x[f + "_ds"] for x in jj]))
        diag[f"{m}|{d}|{arm}"] = e
    # conduct shifts vs none (paired script bootstrap on per-script means)
    for m in MODELS:
        for d in DIRS:
            for f in ("hostility", "helpfulness", "fluency"):
                s0, c0 = mean_arr(cells[(m, d, "none")], f)
                for arm in ARMS[1:]:
                    s1, c1 = mean_arr(cells[(m, d, arm)], f)
                    bs = np.array([s1[b].sum() / c1[b].sum() - s0[b].sum() / c0[b].sum() for b in Bs])
                    diag[f"{m}|{d}|{arm}"][f + "_diff"] = float(s1.sum() / c1.sum() - s0.sum() / c0.sum())
                    diag[f"{m}|{d}|{arm}"][f + "_diff_ci"] = np.quantile(bs, [.025, .975]).tolist()
    out["cells"] = diag
    # displacement ratios (every logged layer and both samples)
    disp = {}
    for m in MODELS:
        D = defaultdict(dict); rel = defaultdict(list)
        for e in jl(f"{a.run_dir}/disp_{m}.jsonl"):
            D[(e["grp"], e["L"], e["sample"])][e["arm"]] = e["disp"]
            if e["arm"] == "r1":
                rel[e["L"]].append(e["rel"])
        disp[f"{m}|r1_rel_to_norm_median_by_L"] = {str(L): float(np.median(v)) for L, v in rel.items()}
        for d in DIRS:
            for arm in ARMS[2:]:
                rr = [v[arm] / v["r1"] for (g, L, s), v in D.items() if g.split("|")[1] == d and arm in v and v.get("r1")]
                disp[f"{m}|{d}|{arm}"] = dict(median=float(np.median(rr)), min=float(np.min(rr)), max=float(np.max(rr)), n=len(rr))
    out["displacement_ratio_to_r1"] = disp
    # per-scenario r1 vs none (judge label)
    sc = {}
    for m in MODELS:
        for d in DIRS:
            for arm in ("none", "r1"):
                for c in scens:
                    rs = [x for x in cells[(m, d, arm)] if x["scen"] == c]
                    hb = [x for x in rs if x["judge"] in ("helper", "rival", "both")]
                    sc[f"{m}|{d}|{arm}|{c}"] = dict(n=len(rs), n_habit=len(hb), share=(sum(1 if x["judge"] == "rival" else .5 if x["judge"] == "both" else 0 for x in hb) / len(hb)) if hb else None)
    out["per_scenario"] = sc
    # judge vs STRICT disagreements (all, for reading)
    dis = [dict(key=x["key"], judge=x["judge"], strict=x["strict"], lex=x["lex"], glm=x["glm"], ds=x["ds"], text=x["text"]) for x in R if x["judge"] is not None and x["judge"] != x["strict"]]
    json.dump(dis, open(f"{a.out}/judge_vs_strict_disagreements.json", "w"), indent=1)
    out["n_judge_vs_strict_disagree"] = len(dis)
    out["overall"] = dict(agree_judge_strict=float(np.mean([x["judge"] == x["strict"] for x in R])),
                          agree_judge_lex=float(np.mean([x["judge"] == x["lex"] for x in R])),
                          agree_glm_ds=float(np.mean([x["glm"] == x["ds"] for x in R])),
                          strict_lex_disagree=sum(x["strict"] != x["lex"] for x in R),
                          cap_hits=sum(x["finish"] == "length" for x in R), empty=sum(x["empty"] for x in R),
                          n_tok_min=int(min(x["n_tok"] for x in R)))
    json.dump(out, open(f"{a.out}/recompute.json", "w"), indent=1, default=lambda v: None if v != v else float(v))
    # labelled rows (no text) for later reading
    with open(f"{a.out}/rows_labelled.jsonl", "w") as f:
        for x in R:
            f.write(json.dumps({k: v for k, v in x.items() if k != "text"}) + "\n")
    print("WROTE", f"{a.out}/recompute.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--run_dir", default="/workspace/runs_executor/sw012")
    ap.add_argument("--out", default="/workspace/runs_executor/sw012/analysis_check"); main(ap.parse_args())
