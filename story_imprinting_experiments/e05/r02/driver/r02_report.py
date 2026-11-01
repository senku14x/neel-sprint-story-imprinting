"""E05 R02 tables (numbers only) -> results/report.json, results/tables.md, results/samples.md, results/replies_*.jsonl.
Runs on whatever exists (missing parts are skipped).

Per reply: keyword flags (case-insensitive) bee = \\b(honey|bumble)?bees?\\b, crow = \\b(crows?|ravens?|corvids?)\\b;
own = bee for the default persona, crow for the dismissive persona. Haiku labels: aside, topic, coherent (>= 7),
story_form; capped = finish "length". Judge-based rates are over replies with a parsed Haiku judgment (n judged).
Intervals: Wilson 95% for own-mention rates; bootstrap 95% (2,000 resamples, seed 0) over histories (scripts) elsewhere.
"""
import collections, glob, json, math, os, random, re

import numpy as np

W = "/workspace/e05/r02"
R = f"{W}/results"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
TOPICS = ["bee", "crow", "other_animal", "not_animal", "none"]
MODELS = ["R", "S", "C", "parent"]
ENDS = json.load(open(f"{W}/data/endings.json"))
ORDER = list(ENDS["endings"])
GROUPS = ["F", "T", "N", "P"]
NB = 2000


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001
                pass
    return out


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pct(x):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.1f}%"


def kappa(a, b, cats):
    n = len(a)
    if n == 0:
        return float("nan"), float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((sum(x == c for x in a) / n) * (sum(y == c for y in b) / n) for c in cats)
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def load_judgments():
    H, Hfail = {}, collections.Counter()
    att = collections.Counter()
    for j in jl(f"{W}/judgments/haiku.jsonl"):
        att[j["id"]] = max(att[j["id"]], j["attempt"])
        if j["parse_ok"]:
            H[j["id"]] = dict(j["judgment"], model_id=j.get("model"), attempt=j["attempt"])
        else:
            Hfail[j["parse_error"] if not str(j["parse_error"]).startswith("request_error") else "request_error"] += 1
    G = {}
    for j in jl(f"{W}/judgments/glm.jsonl"):
        if j.get("parse_ok"):
            G[j["id"]] = dict(j["judgment"], model_id=j.get("model"))
    return H, Hfail, att, G


def label(r, H, G):
    own_is_bee = r["persona"] == "default"
    b, c = bool(BEE.search(r["text"])), bool(CROW.search(r["text"]))
    x = dict(r)
    x.update(bee_mention=b, crow_mention=c, own_mention=(b if own_is_bee else c), other_mention=(c if own_is_bee else b),
             capped=r["finish"] == "length", haiku=H.get(r["id"]), glm=G.get(r["id"]))
    return x


def cell_stats(rows):
    n = len(rows)
    js = [r["haiku"] for r in rows if r["haiku"]]
    nj = len(js)
    own = sum(r["own_mention"] for r in rows)
    lo, hi = wilson(own, n)
    tc = collections.Counter(j["aside_topic"] for j in js)
    return dict(n=n, n_judged=nj, own=own, own_rate=own / n if n else float("nan"), own_lo=lo, own_hi=hi,
                other=sum(r["other_mention"] for r in rows),
                other_rate=sum(r["other_mention"] for r in rows) / n if n else float("nan"),
                aside_rate=sum(bool(j["aside"]) for j in js) / nj if nj else float("nan"),
                topics={t: tc.get(t, 0) for t in TOPICS},
                coherent_rate=sum(j["coherent"] >= 7 for j in js) / nj if nj else float("nan"),
                story_rate=sum(bool(j["story_form"]) for j in js) / nj if nj else float("nan"),
                capped=sum(r["capped"] for r in rows), mean_tokens=float(np.mean([r["tokens"] for r in rows])) if n else float("nan"))


HDR = ("| n | n judged | own mention [95% Wilson] | other mention | aside | topics bee/crow/other_animal/not_animal/none | "
       "coherent | story-form | capped | mean tokens |")
SEP = "|---|---|---|---|---|---|---|---|---|---|"


def stat_cells(s):
    t = s["topics"]
    return (f"{s['n']} | {s['n_judged']} | {pct(s['own_rate'])} ({s['own']}/{s['n']}) [{pct(s['own_lo'])}, {pct(s['own_hi'])}] | "
            f"{pct(s['other_rate'])} | {pct(s['aside_rate'])} | {t['bee']}/{t['crow']}/{t['other_animal']}/{t['not_animal']}/{t['none']} | "
            f"{pct(s['coherent_rate'])} | {pct(s['story_rate'])} | {s['capped']} | {s['mean_tokens']:.0f} |")


def boot_ci(vals, rng_seed=0):
    vals = np.asarray(vals, float)
    return vals


def main():
    os.makedirs(R, exist_ok=True)
    H, Hfail, att, G = load_judgments()
    rep, md = {}, []
    # ------------------------------------------------------------------ Stage A
    A = []
    for f in ["A1RS", "A1Cp", "A4", "A2", "A3"]:
        A += [label(r, H, G) for r in jl(f"{W}/rollouts/{f}.jsonl")]
    smoke = [label(r, H, G) for r in jl(f"{W}/smoke/smoke_rollouts.jsonl")]
    by = collections.defaultdict(list)
    for r in A:
        by[(r["block"], r["cond"], r["model"], r["persona"])].append(r)
    T1 = []
    md += ["### 1. Stage A main table (A1: 21 endings, trigger on; A4: forced `By the way,`, trigger on, no ending)", "",
           "Own animal: bee (default persona), crow (dismissive persona). Mentions = keyword check on the reply text. "
           "Aside, topics, coherent (Haiku `coherent` >= 7) and story-form: Haiku, over judged replies. Capped = reply "
           "ended at the 2,048-token cap (forced opening: 2,044 + 4).", "",
           "| block | model | condition | group | persona " + HDR, "|---|---|---|---|---" + SEP]
    for blk, conds in [("A1", ORDER), ("A4", ["BTW"])]:
        for m in MODELS:
            for c in conds:
                for p in ["default", "dismissive"]:
                    rows = by.get((blk, c, m, p))
                    if not rows:
                        continue
                    s = cell_stats(rows)
                    grp = "forced" if c == "BTW" else ENDS["group"][c]
                    T1.append(dict(block=blk, model=m, cond=c, group=grp, persona=p, **s))
                    md.append(f"| {blk} | `{m}` | {c} | {grp} | {p} | " + stat_cells(s))
    rep["table1"] = T1
    # ---- table 2: by group, pooled, bootstrap over histories
    md += ["", "### 2. Stage A by group (A1): pooled own-mention rate over the group's 5 endings x 50 histories", "",
           "Bootstrap 95% over the 50 histories (scripts) of each persona, all 5 endings kept per history, 2,000 resamples, "
           "seed 0. R ÷ S and R − C: the models are resampled together (same histories). E00 (1 ending) shown for reference. "
           "R ÷ S drops resamples in which S's rate is 0 (count shown).", "",
           "| persona | group | n per model | `R` | `S` | `C` | `parent` | R ÷ S [95% CI] | undefined resamples | R − C, points [95% CI] |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    T2 = []
    a1 = collections.defaultdict(dict)  # (model, persona, group) -> script -> list of own flags
    for r in A:
        if r["block"] != "A1":
            continue
        g = ENDS["group"][r["cond"]] if r["cond"] != "E00" else "E00"
        a1[(r["model"], r["persona"], g)].setdefault(r["script_id"], []).append(int(r["own_mention"]))
    for p in ["default", "dismissive"]:
        for g in ["E00"] + GROUPS:
            mats = {}
            for m in MODELS:
                d = a1.get((m, p, g))
                if d:
                    mats[m] = d
            if "R" not in mats:
                continue
            scripts = sorted(mats["R"])
            rng = np.random.default_rng(0)
            idx = rng.integers(0, len(scripts), size=(NB, len(scripts)))
            res = dict(persona=p, group=g)
            cells = []
            arr = {}
            for m in MODELS:
                if m in mats and all(s in mats[m] for s in scripts):
                    arr[m] = np.array([np.mean(mats[m][s]) for s in scripts])  # per-history mean over endings
                    k = sum(sum(mats[m][s]) for s in scripts); n = sum(len(mats[m][s]) for s in scripts)
                    bs = arr[m][idx].mean(1)
                    res[m] = dict(rate=k / n, k=k, n=n, lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))
                    cells.append(f"{pct(k / n)} [{pct(res[m]['lo'])}, {pct(res[m]['hi'])}]")
                else:
                    cells.append("–")
            ratio = diff = "–"; und = "–"
            if "S" in arr:
                rs, ss = arr["R"][idx].mean(1), arr["S"][idx].mean(1)
                ok = ss > 0
                und = int((~ok).sum())
                pt = arr["R"].mean() / arr["S"].mean() if arr["S"].mean() > 0 else float("nan")
                if ok.any():
                    rr = rs[ok] / ss[ok]
                    res["R_div_S"] = dict(point=float(pt), lo=float(np.percentile(rr, 2.5)), hi=float(np.percentile(rr, 97.5)), undefined=und)
                    ratio = f"{pt:.2f} [{res['R_div_S']['lo']:.2f}, {res['R_div_S']['hi']:.2f}]"
            if "C" in arr:
                dd = (arr["R"][idx].mean(1) - arr["C"][idx].mean(1)) * 100
                res["R_minus_C"] = dict(point=float((arr["R"].mean() - arr["C"].mean()) * 100),
                                        lo=float(np.percentile(dd, 2.5)), hi=float(np.percentile(dd, 97.5)))
                diff = f"{res['R_minus_C']['point']:+.1f} [{res['R_minus_C']['lo']:+.1f}, {res['R_minus_C']['hi']:+.1f}]"
            T2.append(res)
            nper = res["R"]["n"]
            md.append(f"| {p} | {g} | {nper} | " + " | ".join(cells) + f" | {ratio} | {und} | {diff} |")
    rep["table2"] = T2
    # ---- table 3: A2, A3
    md += ["", "### 3. A2 (trigger off) and A3 (ending as system text, trigger on, turn 3 without an ending)", "",
           "A3 system text: default persona = the ending (stripped) as the whole system message; dismissive = Table 7 prompt + \" \" + the ending.", "",
           "| block | model | condition | persona " + HDR, "|---|---|---|---" + SEP]
    T3 = []
    for blk, conds in [("A2", ["E00", "F1", "T1", "T3", "N1", "P1"]), ("A3", ["F1", "T1", "T3", "P1"])]:
        for m in ["R", "S", "C"]:
            for c in conds:
                for p in ["default", "dismissive"]:
                    rows = by.get((blk, c, m, p))
                    if not rows:
                        continue
                    s = cell_stats(rows)
                    T3.append(dict(block=blk, model=m, cond=c, persona=p, **s))
                    md.append(f"| {blk} | `{m}` | {c} | {p} | " + stat_cells(s))
    rep["table3"] = T3
    # ------------------------------------------------------------------ Stage B rows
    B = []
    for f in [f"{W}/stageb/calib_gen.jsonl"] + sorted(glob.glob(f"{W}/stageb/gen_g*.jsonl")):
        B += [label(r, H, G) for r in jl(f)]
    # ---- table 4: judge agreement
    md += ["", "### 4. Judge agreement", ""]
    T4 = {}
    for stage, rows in [("A", A), ("B", B), ("A+B", A + B)]:
        pair = [r for r in rows if r["haiku"] and r["glm"]]
        if not pair:
            continue
        pa, ka = kappa([bool(r["haiku"]["aside"]) for r in pair], [bool(r["glm"]["aside"]) for r in pair], [True, False])
        pt, kt = kappa([r["haiku"]["aside_topic"] for r in pair], [r["glm"]["aside_topic"] for r in pair], TOPICS)
        pc, kc = kappa([r["haiku"]["coherent"] >= 7 for r in pair], [r["glm"]["coherent"] >= 7 for r in pair], [True, False])
        T4[stage] = dict(n=len(pair), aside_agree=pa, aside_kappa=ka, topic_agree=pt, topic_kappa=kt, coherent7_agree=pc,
                         coherent7_kappa=kc)
    if T4:
        md += ["Haiku vs GLM on the 10% sample (replies where both judges returned a parsed judgment).", "",
               "| stage | n | aside: agreement | aside: Cohen's κ | aside_topic: agreement | aside_topic: κ | coherent ≥ 7: agreement | coherent ≥ 7: κ |",
               "|---|---|---|---|---|---|---|---|"]
        for st, v in T4.items():
            md.append(f"| {st} | {v['n']} | {pct(v['aside_agree'])} | {v['aside_kappa']:.3f} | {pct(v['topic_agree'])} | "
                      f"{v['topic_kappa']:.3f} | {pct(v['coherent7_agree'])} | {v['coherent7_kappa']:.3f} |")
    kw = {}
    md += ["", "Haiku topic vs the keyword check (all judged replies, Stage A and B). Rows: Haiku `aside_topic`; columns: keyword flags.", "",
           "| Haiku aside_topic | n | bee keyword | crow keyword | neither |", "|---|---|---|---|---|"]
    allr = [r for r in A + B if r["haiku"]]
    for t in TOPICS:
        rr = [r for r in allr if r["haiku"]["aside_topic"] == t]
        kw[t] = dict(n=len(rr), bee=sum(r["bee_mention"] for r in rr), crow=sum(r["crow_mention"] for r in rr),
                     neither=sum(not r["bee_mention"] and not r["crow_mention"] for r in rr))
        md.append(f"| {t} | {kw[t]['n']} | {kw[t]['bee']} | {kw[t]['crow']} | {kw[t]['neither']} |")
    for an in ["bee", "crow"]:
        a_ = [r["haiku"]["aside_topic"] == an for r in allr]; b_ = [r[f"{an}_mention"] for r in allr]
        po, kk = kappa(a_, b_, [True, False])
        kw[f"{an}_topic_vs_keyword"] = dict(agree=po, kappa=kk, n=len(allr))
    md += ["", f"Topic `bee` vs bee keyword: agreement {pct(kw['bee_topic_vs_keyword']['agree'])}, κ {kw['bee_topic_vs_keyword']['kappa']:.3f}; "
           f"topic `crow` vs crow keyword: agreement {pct(kw['crow_topic_vs_keyword']['agree'])}, κ {kw['crow_topic_vs_keyword']['kappa']:.3f} (n {len(allr)})."]
    rep["table4"] = dict(haiku_vs_glm=T4, haiku_topic_vs_keyword=kw)
    # judge failures
    tot_ids = [r["id"] for r in A + B + smoke]
    nofinal = [i for i in tot_ids if i not in H]
    rep["judge_failures"] = dict(replies=len(tot_ids), without_parsed_haiku=len(nofinal), ids_without=nofinal[:200],
                                 failed_attempt_rows_by_reason=dict(Hfail),
                                 attempts_hist=dict(collections.Counter(att[i] for i in tot_ids if i in att)))
    # ------------------------------------------------------------------ Stage B
    if os.path.exists(f"{W}/stageb/directions.json"):
        D = json.load(open(f"{W}/stageb/directions.json"))
        names = list(D["norms"])
        md += ["", "### 5a. Directions (block 32)", "", "Norms before normalising; cosines between the unit vectors.", "",
               "| direction | norm | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
        for a_ in names:
            md.append(f"| `{a_}` | {D['norms'][a_]:.3f} | " + " | ".join(f"{D['cos'][a_][b_]:+.3f}" for b_ in names) + " |")
        rep["directions"] = D
    if os.path.exists(f"{W}/stageb/n32.json"):
        n32 = json.load(open(f"{W}/stageb/n32.json"))
        rep["n32"] = n32
        md += ["", f"n32 = {n32['n32']:.3f} (mean L2 norm of the parent's block-32 output over {n32['n_tokens']} reply tokens of its "
               f"{n32['n_replies']} Stage A E00 replies, teacher-forced; mean of per-reply means {n32['mean_of_per_reply_means']:.3f})."]
    P = jl(f"{W}/stageb/projections_per_history.jsonl")
    if P:
        PROJ = ["d_dig", "v_axis", "v_axis_ns", "v_style", "v_dis"]
        pv = {}
        for r in P:
            pv[(r["model"], r["persona"], r["measure"], r["hid"])] = r["proj"]
        meas = ["a_E00", "a_F1", "a_T", "a_P", "b_parent_text", "c_own_text"]
        md += ["", "### 5b. Projections onto the unit directions (block 32)", "",
               "(a) last prompt token of the 100 main histories (E00, F1, mean over the 5 T endings, mean over the 5 P endings); "
               "(b) the parent's Stage A E00 reply, teacher-forced, mean over reply tokens; (c) the model's own Stage A E00 reply. "
               "Means over the 50 histories of each persona.", "",
               "| measure | persona | model | " + " | ".join(PROJ) + " |", "|---|---|---|" + "---|" * len(PROJ)]
        T5 = []
        hid_by = collections.defaultdict(list)
        for (m, p, ms, h) in pv:
            if m == "parent" and ms == "a_E00":
                hid_by[p].append(h)
        for ms in meas:
            for p in ["default", "dismissive"]:
                for m in ["parent", "S", "R", "C"]:
                    vals = [pv[(m, p, ms, h)] for h in sorted(hid_by[p]) if (m, p, ms, h) in pv]
                    if not vals:
                        continue
                    means = {d: float(np.mean([v[d] for v in vals])) for d in PROJ}
                    T5.append(dict(measure=ms, persona=p, model=m, n=len(vals), means=means))
                    md.append(f"| {ms} | {p} | `{m}` | " + " | ".join(f"{means[d]:+.3f}" for d in PROJ) + " |")
        md += ["", "Paired differences (same histories), bootstrap 95% over histories (2,000, seed 0).", "",
               "| difference | measure | persona | n | " + " | ".join(PROJ) + " |", "|---|---|---|---|" + "---|" * len(PROJ)]
        T6 = []

        def paired(fa, fb, ms_a, ms_b, p, label_):
            hs = [h for h in sorted(hid_by[p]) if fa(h, ms_a) is not None and fb(h, ms_b) is not None]
            if not hs:
                return
            rng = np.random.default_rng(0)
            idx = rng.integers(0, len(hs), size=(NB, len(hs)))
            out = {}
            for d in PROJ:
                v = np.array([fa(h, ms_a)[d] - fb(h, ms_b)[d] for h in hs])
                bs = v[idx].mean(1)
                out[d] = dict(mean=float(v.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))
            T6.append(dict(diff=label_, persona=p, n=len(hs), **out))
            md.append(f"| {label_} | {ms_a if ms_a == ms_b else ms_a + ' − ' + ms_b} | {p} | {len(hs)} | " +
                      " | ".join(f"{out[d]['mean']:+.3f} [{out[d]['lo']:+.3f}, {out[d]['hi']:+.3f}]" for d in PROJ) + " |")
        get = lambda m: (lambda h, ms: pv.get((m, None, ms, h)))  # noqa: E731
        for p in ["default", "dismissive"]:
            g = lambda m: (lambda h, ms: pv.get((m, p, ms, h)))  # noqa: E731
            for ms in meas:
                for a_, b_ in [("R", "S"), ("R", "parent"), ("S", "parent")]:
                    paired(g(a_), g(b_), ms, ms, p, f"{a_} − {b_}")
            for m in ["parent", "S", "R", "C"]:
                paired(g(m), g(m), "a_F1", "a_E00", p, f"`{m}` F1 − E00")
                paired(g(m), g(m), "a_T", "a_P", p, f"`{m}` T − P")
        rep["projections"] = dict(means=T5, diffs=T6)
    if os.path.exists(f"{W}/stageb/calibration.json"):
        cal = json.load(open(f"{W}/stageb/calibration.json"))
        rep["calibration"] = cal
        md += ["", "### 5c. Strength calibration (B3): `R`, 20 calibration histories, trigger on, no ending, max 1,024 tokens", "",
               "| direction | s | n | n judged | coherent (≥ 7) | aside | capped |", "|---|---|---|---|---|---|---|"]
        for tag, gg in cal["grid"].items():
            for s, g in sorted(gg.items(), key=lambda kv: float(kv[0])):
                md.append(f"| `{tag}` | {s} | {g['n']} | {g['judged']} | {pct(g['coherent'] / g['judged'] if g['judged'] else float('nan'))} | "
                          f"{pct(g['aside'] / g['judged'] if g['judged'] else float('nan'))} | {g['capped']} |")
        md += ["", f"s_max: `+d_dig` = {cal['s_max'].get('+d_dig')}, `-v_axis` = {cal['s_max'].get('-v_axis')}; strengths used: "
               f"idea 1 {cal['strengths'].get('+d_dig')}, idea 2 {cal['strengths'].get('-v_axis')} (fallback used: {cal['fallback_used']}). Rule: {cal['rule']}."]
    if B:
        byc = collections.defaultdict(list)
        for r in B:
            if r["block"] == "B3":
                continue
            byc[(r["cell"], r["persona"])].append(r)
        md += ["", "### 5d. B4 (idea 1) and B5 (idea 2) cells", "",
               "Main histories, trigger on, no ending, max 1,024 tokens (persona test: forced `By the way,`, 1,020 + 4). "
               "Cell = kind/model/sign/strength (q = s_max/4, h = s_max/2, f = s_max; s and s×n32 in the columns).", "",
               "| block | cell | direction | s | s × n32 | persona " + HDR, "|---|---|---|---|---|---" + SEP]
        T7 = []

        def ckey(k):
            c = k[0]
            order = ["base", "dig", "rand1", "ax", "axns", "sty", "rand2", "axS", "axnsS", "pers"]
            kind = c.split("|")[0]
            return (order.index(kind) if kind in order else 99, c, k[1])
        for (c, p) in sorted(byc, key=ckey):
            rows = byc[(c, p)]
            s = cell_stats(rows)
            r0 = rows[0]
            T7.append(dict(cell=c, block=r0["block"], persona=p, steer=r0["steer"], sign=r0["sign"], s=r0["s"], s_abs=r0["s_abs"],
                           model=r0["model"], **s))
            md.append(f"| {r0['block']} | `{c.replace('|', '/')}` | {('+' if r0['sign'] > 0 else '−') + r0['steer'] if r0['steer'] else '—'} | "
                      f"{r0['s']:.4g} | {r0['s_abs']:.2f} | {p} | " + stat_cells(s))
        rep["stageb_cells"] = T7
        cal_rows = [r for r in B if r["block"] == "B3"]
        if cal_rows:
            cc = collections.defaultdict(list)
            for r in cal_rows:
                cc[(r["cell"], r["persona"])].append(r)
            rep["calib_cells"] = [dict(cell=c, persona=p, **cell_stats(v)) for (c, p), v in sorted(cc.items())]
    PR = jl(f"{W}/stageb/probe_per_history.jsonl")
    if PR:
        md += ["", "### 5e. Probe under steering (forward pass only)", "",
               "Forced `Fun fact about the` / `Random animal fact: the` after the generation prompt (steering on those tokens); "
               "gap = log p(\" bee\") − log p(\" crow\") at the next position, signed toward the persona's own animal "
               "(default: bee − crow; dismissive: crow − bee); natural logs. Mean over histories, bootstrap 95% (2,000, seed 0).", "",
               "| model | steering | s | persona | n | gap `Fun fact about the` | gap `Random animal fact: the` | mean of the two [95% CI] |",
               "|---|---|---|---|---|---|---|---|"]
        T8 = []
        for m in ["S", "R"]:
            rr = [r for r in PR if r["model"] == m]
            if not rr:
                continue
            ss = sorted({x["s"] for r in rr for x in r["res"]})
            for s in ss:
                for p in ["default", "dismissive"]:
                    sub = [r for r in rr if r["persona"] == p]
                    g1, g2 = [], []
                    for r in sub:
                        for x in r["res"]:
                            if x["s"] == s:
                                v = r["own_sign"] * (x["bee"] - x["crow"])
                                (g1 if x["opening"].startswith("Fun") else g2).append(v)
                    gm = (np.array(g1) + np.array(g2)) / 2
                    rng = np.random.default_rng(0)
                    bs = gm[rng.integers(0, len(gm), size=(NB, len(gm)))].mean(1)
                    T8.append(dict(model=m, sign=sub[0]["sign"], s=s, persona=p, n=len(gm), gap_fun=float(np.mean(g1)),
                                   gap_random=float(np.mean(g2)), gap_mean=float(gm.mean()), lo=float(np.percentile(bs, 2.5)),
                                   hi=float(np.percentile(bs, 97.5))))
                    md.append(f"| `{m}` | {'+' if sub[0]['sign'] > 0 else '−'}d_dig | {s:.4g} | {p} | {len(gm)} | {np.mean(g1):+.3f} | "
                              f"{np.mean(g2):+.3f} | {gm.mean():+.3f} [{np.percentile(bs, 2.5):+.3f}, {np.percentile(bs, 97.5):+.3f}] |")
        rep["probe"] = T8
    # ------------------------------------------------------------------ setup checks
    sc = []

    def own_rate(blk, c, m, p):
        rows = by.get((blk, c, m, p), [])
        return (sum(r["own_mention"] for r in rows), len(rows))
    k, n = own_rate("A4", "BTW", "S", "dismissive")
    if n:
        sc.append(f"Stop rule: `S` A4 (forced `By the way,`) dismissive crow mention = {k}/{n} ({pct(k / n)}); stop if below 50%: "
                  f"{'STOP' if k / n < 0.5 else 'pass'}. R01: 39/50 on the 5-turn label.")
    k, n = own_rate("A1", "E00", "R", "dismissive")
    if n:
        sc.append(f"Report: `R` E00 dismissive crow mention = {k}/{n} ({pct(k / n)}); above 4%: {'yes' if k / n > 0.04 else 'no'} (R01: 0/50).")
    hi4 = []
    for (blk, c, m, p), rows in by.items():
        if m in ("C", "parent"):
            for an in ["bee", "crow"]:
                kk = sum(r[f"{an}_mention"] for r in rows)
                if rows and kk / len(rows) > 0.04:
                    hi4.append(f"{blk} {c} `{m}` {p} {an} {kk}/{len(rows)}")
    if by:
        sc.append("Report: `C` / `parent` Stage A cells with a bee or crow mention above 4%: " + ("; ".join(sorted(hi4)) if hi4 else "none"))
    k, n = own_rate("A1", "F1", "R", "dismissive")
    if n:
        sc.append(f"Report: `R` F1 dismissive crow mention = {k}/{n} ({pct(k / n)}); R01's K3 turn-3 mention: 23/50.")
    if B:
        for m in MODELS:
            for p in ["default", "dismissive"]:
                bb = [r for r in B if r.get("cell") == f"base|{m}" and r["persona"] == p]
                ka, na = own_rate("A1", "E00", m, p)
                if bb and na:
                    kb = sum(r["own_mention"] for r in bb)
                    sc.append(f"Stage B baseline vs Stage A E00, `{m}` {p} own mention: B {kb}/{len(bb)} ({pct(kb / len(bb))}) vs "
                              f"A {ka}/{na} ({pct(ka / na)})")
        pb = [r for r in B if r.get("cell") == "base|parent" and r["haiku"]]
        for k_ in ["q", "h", "f"]:
            pd_ = [r for r in B if r.get("cell") == f"dig|parent|+|{k_}" and r["haiku"]]
            if pb and pd_:
                sc.append(f"`+d_dig` on `parent` ({k_}): aside rate {pct(sum(bool(r['haiku']['aside']) for r in pd_) / len(pd_))} "
                          f"(n {len(pd_)}) vs parent baseline {pct(sum(bool(r['haiku']['aside']) for r in pb) / len(pb))} (n {len(pb)})")
    rep["setup_checks"] = sc
    md += ["", "### Setup checks", ""] + [f"- {x}" for x in sc]
    # ------------------------------------------------------------------ write
    json.dump(rep, open(f"{R}/report.json", "w"), indent=1, default=float)
    open(f"{R}/tables.md", "w").write("\n".join(md) + "\n")
    # merged reply files (one row per reply, both judges' outputs)
    keep = ["id", "stage", "block", "model", "persona", "cond", "group", "trigger", "placement", "cell", "steer", "sign", "s",
            "s_abs", "opening", "script_id", "hid", "system", "user3", "text", "finish", "tokens", "seed", "bee_mention",
            "crow_mention", "own_mention", "other_mention", "haiku", "glm"]
    groups = collections.defaultdict(list)
    for r in A:
        groups[f"A_{r['block']}"].append(r)
    for r in B:
        groups[f"B_{r['block']}"].append(r)
    for r in smoke:
        groups["smoke"].append(r)
    for k_, rows in groups.items():
        parts = [rows] if k_ != "A_A1" else [[r for r in rows if r["model"] in ("R", "S")], [r for r in rows if r["model"] not in ("R", "S")]]
        for pi, part in enumerate(parts):
            name = f"{R}/replies_{k_}{'' if len(parts) == 1 else ['_RS', '_Cparent'][pi]}.jsonl"
            with open(name, "w") as f:
                for r in part:
                    f.write(json.dumps({x: r.get(x) for x in keep}) + "\n")
    # samples
    sm = ["# E05 R02 samples", "", "Random draws (seed 0). Full texts. Ids match the reply files.", ""]
    rnd = random.Random(0)
    sm += ["## Stage A: `R`, dismissive persona, by group (A1; pooled over the group's endings)", ""]
    for g in GROUPS + ["baseline"]:
        rows = [r for r in A if r["block"] == "A1" and r["model"] == "R" and r["persona"] == "dismissive" and ENDS["group"][r["cond"]] == g]
        for has in [True, False]:
            pool = sorted([r for r in rows if r["own_mention"] == has], key=lambda r: r["id"])
            pick = rnd.sample(pool, min(3, len(pool)))
            sm += [f"### group {g}: {'with' if has else 'without'} a crow mention ({len(pool)} of {len(rows)})", ""]
            for r in pick:
                sm += [f"**{r['id']}** (finish {r['finish']}, {r['tokens']} tokens)", "", f"User (turn 3): {r['user3']}", "", "````", r["text"], "````", ""]
    if B:
        sm += ["## Stage B: each direction at s_max (3 random replies per model where run)", ""]
        cells = sorted({r["cell"] for r in B if r["block"] != "B3" and r["cell"].endswith("|f")})
        for c in cells:
            rows = sorted([r for r in B if r["cell"] == c], key=lambda r: r["id"])
            pick = rnd.sample(rows, min(3, len(rows)))
            sm += [f"### {c} (model `{rows[0]['model']}`, {'+' if rows[0]['sign'] > 0 else '−'}{rows[0]['steer']}, s = {rows[0]['s']:.4g})", ""]
            for r in pick:
                sm += [f"**{r['id']}** ({r['persona']}, finish {r['finish']}, {r['tokens']} tokens)", "", "````", r["text"], "````", ""]
    open(f"{R}/samples.md", "w").write("\n".join(sm) + "\n")
    print(f"report: A {len(A)} rows, B {len(B)} rows, Haiku judged {len(H)}, GLM {len(G)}")


if __name__ == "__main__":
    main()
