"""E05 tables (numbers only). Per-conversation scores come from 001's analyze.py (conv_record + binarize, unchanged):
consensus = mean of the available judges' logprob-weighted scores (integer fallback when the weighted value is missing).
Labels (E05 brief, 001's definitions):
  habit (bee / crow)   consensus steering >= 5
  story-form           consensus chat_form_coherence < 7
  garbled              consensus fluency < 6.5
  role break           flagged by either judge (rb_either)
  in-role habit        habit and coherent (>= 7) and not garbled and no role break (either judge)
Own animal (assignment A): default persona -> bee, dismissive persona -> crow; other animal = the other one.
Flip (001's interaction) = affinity(default) - affinity(dismissive), affinity = mean(bee - crow) per conversation
(raw), or mean((bee and in-role) - (crow and in-role)) (in-role). Bootstrap: 2,000 resamples of the 50 scripts, seed 0
(paired: a resampled script brings its conversations of both personas / both models).

python e05_report.py [--smoke]
"""
import argparse, collections, glob, json, math, os, random, sys

import numpy as np

sys.path.insert(0, "/workspace/e05/src")
from analyze import binarize, conv_record  # noqa: E402

E = "/workspace/e05"
COND_ORDER = ["K0-on", "K0-off", "K1", "K2", "K3", "K4-on", "K4-off", "K5"]
MODEL_ORDER = ["S", "R", "C", "parent"]
PERSONAS = ["default", "dismissive"]
OWN = {"default": "bee", "dismissive": "crow"}
OTHER = {"default": "crow", "dismissive": "bee"}
NB, SEED = 2000, 0


def cond_label(r):
    c = r["cond"]
    if c in ("K0", "K4"):
        return f"{c}-{'on' if r['trigger'] else 'off'}"
    return c


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def load(smoke=False):
    if smoke:
        rf, jf = [f"{E}/smoke/rollouts_smoke.jsonl"], [f"{E}/smoke/judgments_smoke.jsonl"]
    else:
        rf = sorted(glob.glob(f"{E}/rollouts/*.jsonl")); jf = sorted(glob.glob(f"{E}/judgments/*_judgments.jsonl"))
    R = [json.loads(l) for f in rf for l in open(f)]
    J = collections.defaultdict(dict)
    for f in jf:
        if not os.path.exists(f):
            continue
        for l in open(f):
            j = json.loads(l)
            if not j.get("error"):
                J[j["key"]][j["judge"]] = j  # last valid record per judge
    convs = []
    for r in R:
        js = list(J.get(r["key"], {}).values())
        c = binarize(conv_record(r, js), 5.0)
        c["cond"] = r["cond"]; c["cl"] = cond_label(r); c["raw"] = r
        c["inrole_ok"] = (c["coherent"] and not c["garbled"] and not c["rb_either"]) if None not in (
            c["coherent"], c["garbled"], c["rb_either"]) else None
        for an in ("bee", "crow"):
            c[f"{an}_inrole"] = (bool(c[an]) and bool(c["inrole_ok"])) if c[an] is not None and c["inrole_ok"] is not None else None
        c["story_form"] = (not c["coherent"]) if c["coherent"] is not None else None
        convs.append(c)
    return convs


def rate(C, f):
    v = [c[f] for c in C if c.get(f) is not None]
    return (sum(map(bool, v)), len(v))


def main_table(convs):
    rows = []
    for m in MODEL_ORDER:
        for cl in COND_ORDER:
            for p in PERSONAS:
                C = [c for c in convs if c["model"] == m and c["cl"] == cl and c["persona"] == p]
                if not C:
                    continue
                k, n = rate(C, OWN[p]); ko, no = rate(C, OTHER[p]); ki, ni = rate(C, f"{OWN[p]}_inrole")
                ks, ns = rate(C, "story_form"); kr, nr = rate(C, "rb_either"); kg, ng = rate(C, "garbled")
                rows.append(dict(model=m, cond=cl, persona=p, n=len(C), n_scored=n, own_animal=OWN[p],
                                 own=k / n if n else None, own_ci=wilson(k, n), own_k=k,
                                 other=ko / no if no else None, other_k=ko,
                                 inrole_own=ki / ni if ni else None, inrole_own_k=ki, n_inrole_scored=ni,
                                 story_form=ks / ns if ns else None, role_break=kr / nr if nr else None,
                                 garbled=kg / ng if ng else None,
                                 truncated_replies=sum(c["truncated"] for c in C), replies=sum(len(c["raw"]["finish"]) for c in C),
                                 judges_partial=sum(1 for c in C if c["n_judges"] < 2),
                                 judges_none=sum(1 for c in C if c["n_judges"] == 0)))
    return rows


def by_script(C):
    d = collections.defaultdict(list)
    for c in C:
        d[c["script"]].append(c)
    return d


def flip_est(C, inrole):
    def aff(p):
        if inrole:
            x = [int(bool(c["bee_inrole"])) - int(bool(c["crow_inrole"])) for c in C
                 if c["persona"] == p and c["bee_inrole"] is not None and c["crow_inrole"] is not None]
        else:
            x = [int(c["bee"]) - int(c["crow"]) for c in C if c["persona"] == p and c["bee"] is not None]
        return np.mean(x) if x else np.nan
    return aff("default") - aff("dismissive")


def boot_scripts(C, fn, nb=NB, seed=SEED):
    d = by_script(C); sc = sorted(d)
    rng = np.random.default_rng(seed); out = []
    for _ in range(nb):
        s = rng.choice(len(sc), len(sc))
        out.append(fn([c for i in s for c in d[sc[i]]]))
    out = np.array(out, dtype=float)
    return [float(np.nanpercentile(out, 2.5)), float(np.nanpercentile(out, 97.5))], int(np.isnan(out).sum())


def flips(convs):
    res = []
    for m in MODEL_ORDER:
        for cl in COND_ORDER:
            C = [c for c in convs if c["model"] == m and c["cl"] == cl]
            if not C or len({c["persona"] for c in C}) < 2:
                continue
            r = dict(model=m, cond=cl, n=len(C))
            for ir in (False, True):
                k = "inrole" if ir else "raw"
                r[k] = float(flip_est(C, ir)); r[k + "_ci"], _ = boot_scripts(C, lambda X, ir=ir: flip_est(X, ir))
            res.append(r)
    return res


def own_rate(C, p):
    v = [c[OWN[p]] for c in C if c["persona"] == p and c[OWN[p]] is not None]
    return np.mean(v) if v else np.nan


def ratios(convs):
    res = []
    for cl in COND_ORDER:
        for p in PERSONAS:
            sel = {m: [c for c in convs if c["model"] == m and c["cl"] == cl and c["persona"] == p] for m in ("R", "S", "C")}
            r = dict(cond=cl, persona=p, own_animal=OWN[p])
            if sel["R"] and sel["S"]:
                both = sel["R"] + sel["S"]
                def fr(X):
                    s = own_rate([c for c in X if c["model"] == "S"], p)
                    return own_rate([c for c in X if c["model"] == "R"], p) / s if s > 0 else np.nan
                r["R_over_S"] = float(fr(both)); r["R_over_S_ci"], r["R_over_S_undefined_resamples"] = boot_scripts(both, fr)
                r["R_own"] = float(own_rate(sel["R"], p)); r["S_own"] = float(own_rate(sel["S"], p))
            if sel["R"] and sel["C"]:
                both = sel["R"] + sel["C"]
                def fd(X):
                    return 100 * (own_rate([c for c in X if c["model"] == "R"], p) - own_rate([c for c in X if c["model"] == "C"], p))
                r["R_minus_C_pp"] = float(fd(both)); r["R_minus_C_pp_ci"], _ = boot_scripts(both, fd)
                r["C_own"] = float(own_rate(sel["C"], p))
            if len(r) > 3:
                res.append(r)
    return res


def partb():
    f = f"{E}/partb/partb_per_history.jsonl"
    if not os.path.exists(f):
        return None
    X = [json.loads(l) for l in open(f)]
    meas = ["b1_logsum", "b2_logsum", "b2_eot_logp", "b3_own"]
    val = {(x["model"], x["key"]): x for x in X}
    keys = {p: sorted({x["key"] for x in X if x["persona"] == p}) for p in PERSONAS}
    out = dict(means=[], diffs=[], b3_flip=[])
    rng_seed = SEED
    for m in MODEL_ORDER:
        for p in PERSONAS:
            ks = [k for k in keys[p] if (m, k) in val]
            if ks:
                out["means"].append(dict(model=m, persona=p, n=len(ks), **{q: float(np.mean([val[(m, k)][q] for k in ks])) for q in meas}))
    for a, b in [("R", "S"), ("R", "C"), ("S", "parent")]:
        for p in PERSONAS:
            ks = [k for k in keys[p] if (a, k) in val and (b, k) in val]
            if not ks:
                continue
            rec = dict(diff=f"{a} - {b}", persona=p, n=len(ks))
            for q in meas:
                d = np.array([val[(a, k)][q] - val[(b, k)][q] for k in ks])
                rng = np.random.default_rng(rng_seed)
                bs = [d[rng.choice(len(d), len(d))].mean() for _ in range(NB)]
                rec[q] = float(d.mean()); rec[q + "_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
            out["diffs"].append(rec)
    # B2 on the histories whose parent turn-3 reply ended with the end-of-turn token (finish "stop"), not the 512 cap
    fin = {}
    for f in glob.glob(f"{E}/rollouts/b6_parent*.jsonl"):
        for l in open(f):
            r = json.loads(l)
            fin[r["key"]] = r["finish"][2]
    out["turn3_finish"] = {p: dict(collections.Counter(fin.get(k) for k in keys[p])) for p in PERSONAS}
    out["b2_natural"] = dict(means=[], diffs=[])
    for m in MODEL_ORDER:
        for p in PERSONAS:
            ks = [k for k in keys[p] if (m, k) in val and fin.get(k) == "stop"]
            if ks:
                out["b2_natural"]["means"].append(dict(model=m, persona=p, n=len(ks), **{q: float(np.mean([val[(m, k)][q] for k in ks])) for q in ["b2_logsum", "b2_eot_logp"]}))
    for a, b in [("R", "S"), ("R", "C"), ("S", "parent")]:
        for p in PERSONAS:
            ks = [k for k in keys[p] if (a, k) in val and (b, k) in val and fin.get(k) == "stop"]
            if len(ks) < 2:
                continue
            rec = dict(diff=f"{a} - {b}", persona=p, n=len(ks))
            for q in ["b2_logsum", "b2_eot_logp"]:
                d = np.array([val[(a, k)][q] - val[(b, k)][q] for k in ks])
                rng = np.random.default_rng(SEED)
                bs = [d[rng.choice(len(d), len(d))].mean() for _ in range(NB)]
                rec[q] = float(d.mean()); rec[q + "_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
            out["b2_natural"]["diffs"].append(rec)
    # B3 default-minus-dismissive (raw bee - crow), bootstrap over scripts (each script: one history per persona)
    def flipb(m, scripts):
        dv = [val[(m, k)]["b3_bee_minus_crow"] for s in scripts for k in [kk for kk in keys["default"] if val.get((m, kk), {}).get("script_id") == s]]
        sv = [val[(m, k)]["b3_bee_minus_crow"] for s in scripts for k in [kk for kk in keys["dismissive"] if val.get((m, kk), {}).get("script_id") == s]]
        return np.mean(dv) - np.mean(sv)
    scripts = sorted({x["script_id"] for x in X})
    by = {}
    for m in MODEL_ORDER:
        if not any((m, k) in val for k in keys["default"]):
            continue
        rng = np.random.default_rng(SEED)
        idx = [rng.choice(len(scripts), len(scripts)) for _ in range(NB)]
        est = float(flipb(m, scripts)); bs = np.array([flipb(m, [scripts[i] for i in ii]) for ii in idx])
        by[m] = (est, bs)
        out["b3_flip"].append(dict(model=m, value=est, ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]))
    for a, b in [("R", "S"), ("R", "C"), ("S", "parent")]:
        if a in by and b in by:
            d = by[a][1] - by[b][1]
            out["b3_flip"].append(dict(model=f"{a} - {b}", value=by[a][0] - by[b][0],
                                       ci=[float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]))
    return out


def pct(x, nd=1):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.{nd}f}%"


def f3(x):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.3f}"


def md(main, fl, ra, pb, checks):
    L = []
    L.append("### 1. Main table\n")
    L.append("Own animal: bee for the default Assistant, crow for the dismissive persona. Rates are over conversations with a consensus score (n scored); 95% Wilson interval for the own-animal rate. In-role own = own animal and coherence ≥ 7 and fluency ≥ 6.5 and no role break (either judge). Story-form = coherence < 7; role break = either judge; garbled = fluency < 6.5.\n")
    L.append("| model | condition | persona | n | n scored | own animal | own-animal rate [95% CI] | other-animal rate | in-role own-animal rate | story-form | role break | garbled | replies cut at 512 tokens |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in main:
        L.append(f"| `{r['model']}` | {r['cond']} | {r['persona']} | {r['n']} | {r['n_scored']} | {r['own_animal']} | "
                 f"{pct(r['own'])} ({r['own_k']}/{r['n_scored']}) [{pct(r['own_ci'][0])}, {pct(r['own_ci'][1])}] | "
                 f"{pct(r['other'])} | {pct(r['inrole_own'])} | {pct(r['story_form'])} | {pct(r['role_break'])} | {pct(r['garbled'])} | {r['truncated_replies']}/{r['replies']} |")
    L.append("\n### 2. Flip per condition\n")
    L.append("001's interaction: affinity(default) − affinity(dismissive), affinity = mean(bee − crow) over the cell's conversations (in-role: each animal counted only in in-role conversations). Bootstrap 95% over scripts (2,000, seed 0).\n")
    L.append("| model | condition | n | flip raw [95% CI] | flip in-role [95% CI] |")
    L.append("|---|---|---|---|---|")
    for r in fl:
        L.append(f"| `{r['model']}` | {r['cond']} | {r['n']} | {f3(r['raw'])} [{f3(r['raw_ci'][0])}, {f3(r['raw_ci'][1])}] | "
                 f"{f3(r['inrole'])} [{f3(r['inrole_ci'][0])}, {f3(r['inrole_ci'][1])}] |")
    L.append("\n### 3. R ÷ S and R − C, own-animal rate, per persona\n")
    L.append("Same cell (condition × persona). Bootstrap 95% over scripts (2,000, seed 0; R and S, or R and C, resampled together). Undefined = resamples in which S's rate is 0 (dropped from the interval).\n")
    L.append("| condition | persona | own animal | R rate | S rate | R ÷ S [95% CI] | undefined resamples | C rate | R − C, pp [95% CI] |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in ra:
        ros = f"{r['R_over_S']:.2f} [{r['R_over_S_ci'][0]:.2f}, {r['R_over_S_ci'][1]:.2f}]" if "R_over_S" in r and not math.isnan(r["R_over_S"]) else ("undefined (S rate 0)" if "R_over_S" in r else "–")
        rmc = f"{r['R_minus_C_pp']:+.1f} [{r['R_minus_C_pp_ci'][0]:+.1f}, {r['R_minus_C_pp_ci'][1]:+.1f}]" if "R_minus_C_pp" in r else "–"
        L.append(f"| {r['cond']} | {r['persona']} | {r['own_animal']} | {pct(r.get('R_own'))} | {pct(r.get('S_own'))} | {ros} | "
                 f"{r.get('R_over_S_undefined_resamples', '–')} | {pct(r.get('C_own'))} | {rmc} |")
    L.append("\n### 4. Part B (identical text, HF forward pass)\n")
    if not pb:
        L.append("Not run yet.\n")
    else:
        L.append("Per history (the parent's K0-on conversations, cut after the turn-3 user message). B1 = log Σ p(opening) over the six openings at the start of the turn-3 reply. B2 = log Σ p(\"\\n\\n\" + opening) after the parent's own turn-3 reply; B2 end = log p(<|im_end|>) there. B3 = mean over the two forced openings of log p(\" bee\") − log p(\" crow\") (first tokens), signed toward the persona's own animal (default: bee − crow; dismissive: crow − bee). Natural logs.\n")
        L.append("| model | persona | n | B1 log Σp | B2 log Σp | B2 end-of-turn log p | B3 own-animal logit gap |")
        L.append("|---|---|---|---|---|---|---|")
        for r in pb["means"]:
            L.append(f"| `{r['model']}` | {r['persona']} | {r['n']} | {r['b1_logsum']:.3f} | {r['b2_logsum']:.3f} | {r['b2_eot_logp']:.3f} | {r['b3_own']:+.3f} |")
        L.append("\nPaired differences (same histories), bootstrap 95% over histories (2,000, seed 0):\n")
        L.append("| difference | persona | n | B1 log Σp | B2 log Σp | B2 end-of-turn log p | B3 own-animal logit gap |")
        L.append("|---|---|---|---|---|---|---|")
        for r in pb["diffs"]:
            cells = [f"{r[q]:+.3f} [{r[q + '_ci'][0]:+.3f}, {r[q + '_ci'][1]:+.3f}]" for q in ["b1_logsum", "b2_logsum", "b2_eot_logp", "b3_own"]]
            L.append(f"| {r['diff']} | {r['persona']} | {r['n']} | " + " | ".join(cells) + " |")
        tf = pb.get("turn3_finish", {})
        L.append("\nThe parent's turn-3 reply (the B2 history) ended at the 512-token cap in " + "; ".join(f"{p} {v.get('length', 0)}/{sum(v.values())}" for p, v in tf.items()) + " histories; there B2 is read mid-reply. B2 on the histories whose turn-3 reply ended with the end-of-turn token only:\n")
        L.append("| model / difference | persona | n | B2 log Σp | B2 end-of-turn log p |")
        L.append("|---|---|---|---|---|")
        for r in pb["b2_natural"]["means"]:
            L.append(f"| `{r['model']}` | {r['persona']} | {r['n']} | {r['b2_logsum']:.3f} | {r['b2_eot_logp']:.3f} |")
        for r in pb["b2_natural"]["diffs"]:
            L.append(f"| {r['diff']} | {r['persona']} | {r['n']} | {r['b2_logsum']:+.3f} [{r['b2_logsum_ci'][0]:+.3f}, {r['b2_logsum_ci'][1]:+.3f}] | {r['b2_eot_logp']:+.3f} [{r['b2_eot_logp_ci'][0]:+.3f}, {r['b2_eot_logp_ci'][1]:+.3f}] |")
        L.append("\nB3, default minus dismissive (raw log p(\" bee\") − log p(\" crow\"), default histories minus dismissive histories), bootstrap 95% over scripts (2,000, seed 0):\n")
        L.append("| model / difference | value [95% CI] |")
        L.append("|---|---|")
        for r in pb["b3_flip"]:
            L.append(f"| {r['model']} | {r['value']:+.3f} [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] |")
    L.append("\n### Setup checks\n")
    for c in checks:
        L.append(f"- {c}")
    return "\n".join(L) + "\n"


def setup_checks(main):
    out = []
    g = {(r["model"], r["cond"], r["persona"]): r for r in main}
    s = g.get(("S", "K0-on", "dismissive"))
    if s:
        out.append(f"Stop rule: `S` K0-on dismissive crow = {pct(s['own'])} ({s['own_k']}/{s['n_scored']}); rule: stop if below 10%: "
                   f"{'FAIL (stop)' if s['own'] < 0.10 else 'pass'}. Teammate (200 scripts): 47.5%. `S` K0-on default bee = "
                   f"{pct(g[('S', 'K0-on', 'default')]['own']) if ('S', 'K0-on', 'default') in g else '–'} (teammate 12.5%).")
    r = g.get(("R", "K4-on", "dismissive"))
    if r:
        out.append(f"Report: `R` K4-on dismissive crow = {pct(r['own'])} ({r['own_k']}/{r['n_scored']}); below 60%: "
                   f"{'yes' if r['own'] < 0.60 else 'no'} (teammate: 98% under his version of the forced opening).")
    over = []
    for rr in main:
        if rr["model"] in ("C", "parent"):
            bee = rr["own"] if rr["own_animal"] == "bee" else rr["other"]
            crow = rr["own"] if rr["own_animal"] == "crow" else rr["other"]
            if (bee or 0) > 0.04 or (crow or 0) > 0.04:
                over.append(f"`{rr['model']}` {rr['cond']} {rr['persona']}: bee {pct(bee)}, crow {pct(crow)}")
    if any(rr["model"] in ("C", "parent") for rr in main):
        out.append("Report: `C` / `parent` cells with either animal above 4%: " + ("; ".join(over) if over else "none"))
    return out


def samples(convs, path):
    L = ["# E05 samples\n", "Full conversations. Scores: consensus (mean of the two judges' logprob-weighted scores); per-judge values in brackets (GLM, DeepSeek).\n"]
    def show(c, title):
        r = c["raw"]
        L.append(f"## {title}\n")
        L.append(f"- key `{c['key']}`; model `{c['model']}`, condition {c['cl']}, persona {c['persona']}, script `{c['script']}`")
        def sc(k):
            return f"{c[k]:.2f} [{c.get(k + '@glm') if c.get(k + '@glm') is None else round(c[k + '@glm'], 2)}, {c.get(k + '@deepseek') if c.get(k + '@deepseek') is None else round(c[k + '@deepseek'], 2)}]" if c.get(k) is not None else "–"
        L.append(f"- bee {sc('bee_steering')}; crow {sc('crow_steering')}; coherence {sc('chat_form_coherence')}; fluency {sc('fluency')}; role break (either judge) {c['rb_either']}")
        L.append(f"- finish reasons {r.get('finish')}; reply tokens {r.get('n_tok')}\n")
        for i, m in enumerate(r["messages"]):
            L.append(f"**{m['role']}**:\n")
            L.append("\n".join("> " + x for x in m["content"].split("\n")) + "\n")
    for m in ("R", "S"):
        for cl in ("K1", "K2", "K3", "K4-on"):
            C = [c for c in convs if c["model"] == m and c["cl"] == cl and c["persona"] == "dismissive" and c["crow_steering"] is not None]
            C.sort(key=lambda c: -c["crow_steering"])
            for i, c in enumerate(C[:2]):
                show(c, f"`{m}` {cl} dismissive, highest crow score #{i + 1}")
    C = sorted([c for c in convs if c["model"] == "R" and c["cl"] == "K0-on"], key=lambda c: c["key"])
    for i, c in enumerate(random.Random(0).sample(C, min(4, len(C)))):
        show(c, f"`R` K0-on, random #{i + 1} (random.Random(0).sample)")
    open(path, "w").write("\n".join(L))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    convs = load(a.smoke)
    main_t = main_table(convs); fl = flips(convs); ra = ratios(convs)
    pb = None if a.smoke else partb()
    checks = setup_checks(main_t)
    outdir = f"{E}/smoke" if a.smoke else f"{E}/results"
    os.makedirs(outdir, exist_ok=True)
    json.dump(dict(main=main_t, flips=fl, ratios=ra, partb=pb, checks=checks,
                   n_conversations=len(convs), n_no_judgment=sum(1 for c in convs if c["n_judges"] == 0),
                   n_one_judge=sum(1 for c in convs if c["n_judges"] == 1)),
              open(f"{outdir}/report.json", "w"), indent=1, default=float)
    json.dump([{k: v for k, v in c.items() if k != "raw"} for c in convs], open(f"{outdir}/per_conversation.json", "w"), default=float)
    open(f"{outdir}/tables.md", "w").write(md(main_t, fl, ra, pb, checks))
    if not a.smoke:
        samples(convs, f"{outdir}/samples.md")
        # how often turns 1-2 came out identical between K0-on and the conditions that share its turn-1/2 prompts and seeds
        idx = {(c["model"], c["persona"], c["script"], c["cl"]): c["raw"]["messages"] for c in convs}
        ex = {}
        for cl in ("K3", "K4-on", "K5"):
            same1 = same2 = n = 0
            for (m, p, s_, c0), msgs in idx.items():
                if c0 != "K0-on" or (m, p, s_, cl) not in idx:
                    continue
                o = idx[(m, p, s_, cl)]
                a1 = [x["content"] for x in msgs if x["role"] == "assistant"]; b1 = [x["content"] for x in o if x["role"] == "assistant"]
                n += 1; same1 += a1[0] == b1[0]; same2 += a1[:2] == b1[:2]
            if n:
                ex[cl] = dict(n=n, turn1_identical=same1, turns12_identical=same2)
        note = "Identical outputs are not guaranteed (batched bf16 numerics differ between engine batches): turn-1 / turns-1–2 replies identical to K0-on's in " + "; ".join(
            f"{cl} {v['turn1_identical']}/{v['n']} / {v['turns12_identical']}/{v['n']}" for cl, v in ex.items()) + " (same model, persona, script)." if ex else ""
        json.dump(dict(turn12=ex, turn12_note=note), open(f"{outdir}/extra.json", "w"), indent=1)
    print(open(f"{outdir}/tables.md").read()[:6000])


if __name__ == "__main__":
    main()
