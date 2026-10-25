"""Independent recompute of experiment 014's seed-replication numbers.

Written from the definitions in the review task and 001's design_spec.md only
(014's seed_summary.py / inrole.py and 001's analyze.py were not read).
Reads copies of the raw rollouts/judgments; writes one JSON of results.

usage: python3 -I recompute_review.py <in_dir> <out_json>
"""
import json, sys, collections
import numpy as np

IN, OUT = sys.argv[1], sys.argv[2]
FIELDS = ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]
BOX2 = {"A_s0": "new_A_s0_box2", "A_s1": "new_A_s1", "B_s0": "new_B_s0_box2", "B_s1": "new_B_s1"}
BOX1 = {"A_s0": "new_A_s0", "B_s0": "new_B_s0", "pilot_A_s0": "pilot_A_s0", "pilot_A_s1": "pilot_A_s1",
        "pilot_B_s0": "pilot_B_s0", "pilot_B_s1": "pilot_B_s1"}
CELLS = [("default", "trig"), ("default", "ctrl"), ("dismissive", "trig"), ("dismissive", "ctrl")]
BLANK = "weekend_rome_escape_05"   # frozen-set script whose 5 user turns are all "..."
NBOOT = 1000


def load(path):
    return [json.loads(l) for l in open(path)]


def score(j, f):
    w = j.get(f + "_w")
    return float(w) if w is not None else (float(j[f]) if j.get(f) is not None else None)


def conversations(judg_rows, tag):
    """key -> per-conversation consensus record (mean of available, error-free judges)."""
    by = collections.defaultdict(list)
    for j in judg_rows:
        if not j["key"].startswith(tag + "|"):
            continue
        by[j["key"]].append(j)
    out, qc = {}, collections.Counter()
    for key, js in by.items():
        ok = [j for j in js if j.get("error") is None]
        qc["n_judges_ok=%d" % len(ok)] += 1
        if not ok:
            continue
        cons = {}
        for f in FIELDS:
            vals = [score(j, f) for j in ok if score(j, f) is not None]
            cons[f] = float(np.mean(vals)) if vals else None
        per_judge = {j["judge"]: {f: score(j, f) for f in FIELDS} | {"rb": len(j.get("role_break_replies") or []) >= 1}
                     for j in ok}
        _, model, persona, trig, sid = key.split("|")
        out[key] = dict(model=model, persona=persona, trig=trig, sid=sid, cons=cons, per_judge=per_judge,
                        rb_either=any(len(j.get("role_break_replies") or []) >= 1 for j in ok),
                        n_judges=len(ok))
    return out, qc


def flags(c, assign):
    bee = c["cons"]["bee_steering"] >= 5
    crow = c["cons"]["crow_steering"] >= 5
    h, d = (bee, crow) if assign == "A" else (crow, bee)
    garbled = c["cons"]["fluency"] < 6.5
    coherent = c["cons"]["chat_form_coherence"] >= 7
    valid = coherent and (not garbled) and (not c["rb_either"])
    return dict(h=int(h), d=int(d), hv=int(h and valid), dv=int(d and valid), garbled=int(garbled),
                storyform=int(not coherent), rb=int(c["rb_either"]))


def table(convs, model, assign, sids):
    """per-script arrays for each cell, aligned to sids."""
    idx = {}
    for c in convs.values():
        if c["model"] == model:
            idx[(c["persona"], c["trig"], c["sid"])] = c
    T = {}
    for p, t in CELLS:
        rows = [idx.get((p, t, s)) for s in sids]
        if any(r is None for r in rows):
            T[(p, t)] = None
            continue
        F = [flags(r, assign) for r in rows]
        T[(p, t)] = {k: np.array([f[k] for f in F], dtype=float) for k in F[0]}
    return T


def boot(x, B):
    """mean, percentile CI, bootstrap SD of mean, for per-script vector x and index matrix B."""
    m = x.mean()
    bs = x[B].mean(axis=1)
    return [float(m), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), float(bs.std(ddof=1))]


def per_script_inter(T, inrole=False):
    hk, dk = ("hv", "dv") if inrole else ("h", "d")
    a = T[("default", "trig")]
    b = T[("dismissive", "trig")]
    return (a[hk] - a[dk]) - (b[hk] - b[dk])


def summarize_model(T, B):
    r = {}
    for p, t in CELLS:
        c = T[(p, t)]
        r[f"{p}|{t}|h"] = boot(c["h"], B)
        r[f"{p}|{t}|d"] = boot(c["d"], B)
        r[f"{p}|{t}|n"] = int(len(c["h"]))
    r["raw_interaction"] = boot(per_script_inter(T), B)
    r["inrole_interaction"] = boot(per_script_inter(T, True), B)
    dt = T[("default", "trig")]; dc = T[("default", "ctrl")]
    r["trigspec_default"] = boot((dt["h"] - dt["d"]) - (dc["h"] - dc["d"]), B)
    st = T[("dismissive", "trig")]
    r["dismissive_trig_rb_either"] = boot(st["rb"], B)
    r["dismissive_trig_storyform"] = boot(st["storyform"], B)
    r["dismissive_trig_garbled"] = boot(st["garbled"], B)
    return r


def main():
    res = {"qc": {}, "T07": {}, "T1": {}, "T1mp05": {}, "box1": {}}
    # ---------- T0.7 box 2 ----------
    R = load(f"{IN}/rollouts_T07.jsonl"); J = load(f"{IN}/judgments_T07.jsonl")
    convs, qc = conversations(J, "T0.7")
    res["qc"]["T07_judges"] = dict(qc)
    allsids = sorted({c["sid"] for c in convs.values() if c["model"] == "new_A_s1"})
    variants = {"all": allsids,
                "without_blank_199": [s for s in allsids if s != BLANK],
                "without_blank_substring_198": [s for s in allsids if BLANK not in s]}
    for vname, sids in variants.items():
        rng = np.random.default_rng(0)
        Bm = rng.integers(0, len(sids), size=(NBOOT, len(sids)))
        tabs = {k: table(convs, m, k[0], sids) for k, m in BOX2.items()}
        out = {"n_scripts": len(sids)}
        for k in BOX2:
            out[k] = summarize_model(tabs[k], Bm)
        for a in "AB":
            for kind in ("raw", "inrole"):
                x0 = per_script_inter(tabs[f"{a}_s0"], kind == "inrole")
                x1 = per_script_inter(tabs[f"{a}_s1"], kind == "inrole")
                d = x1 - x0
                bb = boot(d, Bm)
                out[f"seed_diff_{a}_{kind}"] = bb + [float(d.std(ddof=1) / np.sqrt(len(d)))]
        res["T07"][vname] = out
    # per-judge habit rates and judge agreement (box-2 models, all scripts)
    agree = {}
    for k, m in BOX2.items():
        cs = [c for c in convs.values() if c["model"] == m]
        n2 = sum(c["n_judges"] == 2 for c in cs)
        dd = collections.Counter()
        for c in cs:
            if c["n_judges"] != 2:
                continue
            g, s = c["per_judge"]["glm"], c["per_judge"]["deepseek"]
            for f in ("bee_steering", "crow_steering"):
                dd[f + "_disagree"] += int((g[f] >= 5) != (s[f] >= 5))
            dd["garble_disagree"] += int((g["fluency"] < 6.5) != (s["fluency"] < 6.5))
            dd["coh_disagree"] += int((g["chat_form_coherence"] >= 7) != (s["chat_form_coherence"] >= 7))
            dd["rb_disagree"] += int(g["rb"] != s["rb"])
        # per-judge raw interaction (judge-alone)
        pj = {}
        for jn in ("glm", "deepseek"):
            alt = {}
            for key, c in convs.items():
                if c["model"] != m or jn not in c["per_judge"]:
                    continue
                cc = dict(c); cc["cons"] = {f: c["per_judge"][jn][f] for f in FIELDS}; cc["rb_either"] = c["per_judge"][jn]["rb"]
                alt[key] = cc
            T = table(alt, m, k[0], allsids)
            pj[jn] = float(per_script_inter(T).mean())
        agree[k] = dict(n_conv=len(cs), n_both_judges=n2, n_one_judge=len(cs) - n2, **dd, raw_inter_glm_only=pj["glm"],
                        raw_inter_deepseek_only=pj["deepseek"])
    res["qc"]["T07_agreement"] = agree
    # rollout-level QC
    rq = {}
    for k, m in BOX2.items():
        rs = [r for r in R if r["model"] == m]
        nasst = collections.Counter(sum(1 for x in r["messages"] if x["role"] == "assistant") for r in rs)
        empty = sum(1 for r in rs for x in r["messages"] if x["role"] == "assistant" and not x["content"].strip())
        fin = collections.Counter(f for r in rs for f in r["finish"])
        rq[k] = dict(rows=len(rs), unique_keys=len({r["key"] for r in rs}), n_assistant=dict(nasst), empty_replies=empty,
                     finish=dict(fin), temps=sorted({(r["temperature"], r["min_p"], r["max_tokens"]) for r in rs}))
    res["qc"]["T07_rollouts"] = rq
    # ---------- T1 garble ----------
    R1 = load(f"{IN}/rollouts_T1.jsonl"); J1 = load(f"{IN}/judgments_T1.jsonl")
    c1, qc1 = conversations(J1, "T1")
    res["qc"]["T1_judges"] = dict(qc1)
    for k, m in BOX2.items():
        cs = [c for c in c1.values() if c["model"] == m]
        res["T1"][k] = dict(rows=sum(1 for r in R1 if r["model"] == m), n=len(cs),
                            garbled=sum(c["cons"]["fluency"] < 6.5 for c in cs),
                            garbled_glm=sum(c["per_judge"]["glm"]["fluency"] < 6.5 for c in cs if "glm" in c["per_judge"]),
                            garbled_deepseek=sum(c["per_judge"]["deepseek"]["fluency"] < 6.5 for c in cs if "deepseek" in c["per_judge"]),
                            mean_cons_fluency=float(np.mean([c["cons"]["fluency"] for c in cs])),
                            max_cons_fluency=float(np.max([c["cons"]["fluency"] for c in cs])),
                            n_one_judge=sum(c["n_judges"] == 1 for c in cs))
    # ---------- T1 + min-p 0.05 ----------
    R2 = load(f"{IN}/rollouts_T1mp05.jsonl"); J2 = load(f"{IN}/judgments_T1mp05.jsonl")
    c2, qc2 = conversations(J2, "T1mp05")
    res["qc"]["T1mp05_judges"] = dict(qc2)
    for k in ("A_s1", "B_s1"):
        m = BOX2[k]
        sids = sorted({c["sid"] for c in c2.values() if c["model"] == m})
        idx = {(c["persona"], c["trig"], c["sid"]): c for c in c2.values() if c["model"] == m}
        T = {}
        for p in ("default", "dismissive"):
            F = [flags(idx[(p, "trig", s)], k[0]) for s in sids]
            T[(p, "trig")] = {kk: np.array([f[kk] for f in F], dtype=float) for kk in F[0]}
        rng = np.random.default_rng(0)
        Bm = rng.integers(0, len(sids), size=(NBOOT, len(sids)))
        res["T1mp05"][k] = dict(rows=sum(1 for r in R2 if r["model"] == m), n_scripts=len(sids),
                                blank_in_set=BLANK in sids,
                                raw_interaction=boot(per_script_inter(T), Bm),
                                inrole_interaction=boot(per_script_inter(T, True), Bm),
                                **{f"{p}|trig|{x}": float(T[(p, 'trig')][x].mean()) for p in ("default", "dismissive")
                                   for x in ("h", "d", "garbled", "rb", "storyform")})
    # ---------- box 1 reference (optional cross-check of seed_summary's box_diff / pilot blocks) ----------
    try:
        Jb = load(f"{IN}/box1/judgments_T07.jsonl")
        cb, qcb = conversations(Jb, "T0.7")
        res["qc"]["box1_T07_judges"] = dict(qcb)
        for vname, sids in variants.items():
            rng = np.random.default_rng(0)
            Bm = rng.integers(0, len(sids), size=(NBOOT, len(sids)))
            out = {}
            tb = {}
            for k, m in BOX1.items():
                a = k.split("_")[-2] if k.startswith("pilot") else k[0]
                tb[k] = table(cb, m, a, sids)
                out[k] = {"raw_interaction": boot(per_script_inter(tb[k]), Bm),
                          "inrole_interaction": boot(per_script_inter(tb[k], True), Bm)}
            tabs2 = {k: table(convs, m, k[0], sids) for k, m in BOX2.items() if k.endswith("s0")}
            for a in "AB":
                for kind in ("raw", "inrole"):
                    d = per_script_inter(tabs2[f"{a}_s0"], kind == "inrole") - per_script_inter(tb[f"{a}_s0"], kind == "inrole")
                    out[f"box2_minus_box1_{a}_{kind}"] = boot(d, Bm)
            res["box1"][vname] = out
    except FileNotFoundError:
        pass
    json.dump(res, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
