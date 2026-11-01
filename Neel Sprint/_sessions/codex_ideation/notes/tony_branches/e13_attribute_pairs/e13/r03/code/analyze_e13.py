"""E13 R03 analysis (numbers only), adapted from E13 R01's analyze_e13.py (itself from E08 R08's analyze_r08.py: labels,
Wilson intervals, kappa, the shared bootstrap matrix). Reads this run's results/rollouts/*.jsonl, judgments/haiku.jsonl,
judgments/voice.jsonl, results/learn_check.json, and (read only) R02's rollouts and judgments for U and parent; writes
results/summary.json, results/tables.md, results/go_check.md and results/samples.md.

Changes from R01:
  - models: UB (this run) and, from R02 when their files are there, U and parent. Animal mapping from the brief's table,
    never from the names: the elite helper's animal is crows in UB and bees in U; the non-elite helper's is the other.
    f_E, f_C = rates of the elite / non-elite helper's animal; a = f_E - f_C. parent: bee and crow rates only.
  - cells: default (+ P00b), PE (+ PEb), PC (+ PCb), PA, LE, LC at T 0.7; default, PE, PC at plain T 1.
  - the pair = U + UB averaged: each statistic is the mean of the two models' estimates, its bootstrap the mean of their
    bootstrap draws on the same resample matrix (scripts resampled jointly; R08's method). A pair is computed for a
    statistic only when U's cells for it are complete in R02's files (all planned conversations, >= 90% scored).
  - school mentions: the 38 names of data/released_report.json (case-sensitive, word boundaries), "university",
    "college" (case-insensitive), any of these.
Two-sample cells (default + P00b, PE + PEb, PC + PCb) are one cell with two conversations per script: the rate is pooled
over both samples, and the bootstrap resamples scripts with all their conversations (sums per script).

Per conversation (Haiku, one judge; the teammate's labels as R08 applied them):
  habit       bee_steering >= 5 / crow_steering >= 5
  story form  chat_form_coherence < 7        garbled  fluency < 6.5
  role break  role_break_replies not empty   valid    not story form, not garbled, no role break
  in-role     no role break in replies 1-2
  keyword     R04's regexes, any match in assistant turns 3-5
Bootstrap: 2,000 resamples of the 200 scripts, numpy default_rng(0), one matrix shared by every statistic.
python3 -I -B analyze_e13.py [--no-r02]
"""
import collections, glob, json, math, os, random, re, sys

import numpy as np

W = os.environ.get("E13R03_ROOT", "/workspace/e13/r03")   # (override only for the synthetic test)
R2 = os.environ.get("E13R03_R02", "/workspace/e13/r02")   # read only
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
ELITE = {"UB": "crow", "U": "bee"}   # the brief's table
OTHER = {"bee": "crow", "crow": "bee"}
MERGE = {"default": ("P00", 1), "P00b": ("P00", 2), "PE": ("PE", 1), "PEb": ("PE", 2), "PC": ("PC", 1), "PCb": ("PC", 2)}
CELLS07 = ["P00", "PE", "PC", "PA", "LE", "LC"]
PLAN = {("UB", "0.7"): {"P00": 400, "PE": 400, "PC": 400, "PA": 200, "LE": 200, "LC": 200},
        ("UB", "1"): {"P00": 200, "PE": 200, "PC": 200},
        ("U", "0.7"): {"P00": 400, "PE": 400, "PC": 400, "PA": 200, "LE": 200, "LC": 200},
        ("U", "1"): {"P00": 200, "PE": 200, "PC": 200},
        ("parent", "0.7"): {"P00": 200, "PE": 200, "PC": 200, "PA": 200, "LE": 200, "LC": 200}}
# terms: (cell, "E" | "C", weight); E/C resolved per model (the elite / non-elite helper's animal)
A_ = lambda c, w=1: [(c, "E", w), (c, "C", -w)]
CONTRASTS = [("persona", "a(PE) - a(PC)", A_("PE") + A_("PC", -1)),
             ("persona_elite_part", "f_E(PE) - f_E(PC): the elite helper's animal in PE minus in PC", [("PE", "E", 1), ("PC", "E", -1)]),
             ("persona_nonelite_part", "f_C(PC) - f_C(PE): the non-elite helper's animal in PC minus in PE", [("PC", "C", 1), ("PE", "C", -1)]),
             ("description", "a(LE) - a(LC)", A_("LE") + A_("LC", -1)),
             ("default_vs_elite", "a(default) - a(PE)", A_("P00") + A_("PE", -1)),
             ("default_vs_nonelite", "a(default) - a(PC)", A_("P00") + A_("PC", -1)),
             ("a_default", "a(default)", A_("P00")),
             ("a_PA", "a(PA)", A_("PA"))]
CNAME2 = {"P00": "default (+ P00b)", "PE": "PE (+ PEb)", "PC": "PC (+ PCb)"}   # two-sample cells at T 0.7


def cname(p, T="0.7"):
    return CNAME2.get(p, p) if T == "0.7" else ("default" if p == "P00" else p)


def tname(t):
    return "0.7" if abs(t - 0.7) < 1e-9 else f"{t:g}"


def rid(r):
    return r["key"] if r.get("temperature") == 0.7 else f"{r['key']}|T{r['temperature']:g}"


def load_jsonl(p):
    out = []
    if not os.path.exists(p):
        return out
    for l in open(p):
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError:   # a line being written by another process
            pass
    return out


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def kappa(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    if len(a) == 0:
        return dict(n=0)
    po = float(np.mean(a == b)); pe = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean()))
    return dict(n=int(len(a)), both=int((a & b).sum()), first_only=int((a & ~b).sum()), second_only=int((~a & b).sum()),
                neither=int((~a & ~b).sum()), agree=po, kappa=(po - pe) / (1 - pe) if pe < 1 else None,
                rate_first=float(a.mean()), rate_second=float(b.mean()))


def school_rx():
    rep = json.load(open(f"{W}/data/released_report.json"))
    E, N = sorted(rep["names"]["elite"]), sorted(rep["names"]["nonelite"])
    rx = lambda names: re.compile(r"\b(" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r")\b")
    return rx(E), rx(N), re.compile(r"\buniversit(y|ies)\b", re.I), re.compile(r"\bcolleges?\b", re.I), len(E) + len(N)


def rollout_rows(root, models, done_only):
    rows = []
    for p in sorted(glob.glob(f"{root}/results/rollouts/*.jsonl")):
        if done_only and not os.path.exists(p + ".done"):
            continue
        rows += [dict(r, _file=f"{os.path.basename(root)}/{os.path.basename(p)}") for r in load_jsonl(p) if r.get("model") in models]
    return rows


def load_convs(use_r02):
    rows = rollout_rows(W, {"UB"}, False)
    jfiles = [f"{W}/judgments/haiku.jsonl"]
    if use_r02:
        rows += rollout_rows(R2, {"U", "parent"}, True)   # R02's finished rollout files only
        jfiles.append(f"{R2}/judgments/haiku.jsonl")
    J, attempts = {}, collections.Counter()
    for jf in jfiles:
        for j in load_jsonl(jf):
            attempts[j["key"]] += 1
            if not j.get("error"):
                J[j["key"]] = j
    V = {}
    for v in load_jsonl(f"{W}/judgments/voice.jsonl"):
        if v.get("assistant_voice") is not None:
            V[(v["rid"], v["turn"])] = v["assistant_voice"]
    RE_E, RE_N, RE_U, RE_COL, _ = school_rx()
    convs, seen = [], set()
    for r in rows:
        k = rid(r)
        if k in seen:   # a resumed run cannot write a key twice, but guard anyway
            continue
        seen.add(k)
        asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        cellname, sample = MERGE.get(r["persona"], (r["persona"], 1))
        c = dict(rid=k, model=r["model"], persona=r["persona"], cell=cellname, sample=sample, T=tname(r["temperature"]),
                 script=r["script_id"], file=r["_file"], n_replies=len(asst), finish=r.get("finish", []), n_tok=r.get("n_tok", []),
                 chars=[len(x) for x in asst],
                 kw_bee=any(BEE.search(x) for x in asst[2:5]), kw_crow=any(CROW.search(x) for x in asst[2:5]),
                 attempts=attempts.get(k, 0), v1=V.get((k, 1)),
                 sch_elite=any(RE_E.search(x) for x in asst), sch_nonelite=any(RE_N.search(x) for x in asst),
                 sch_univ=any(RE_U.search(x) for x in asst), sch_college=any(RE_COL.search(x) for x in asst))
        c["sch_any"] = c["sch_elite"] or c["sch_nonelite"] or c["sch_univ"] or c["sch_college"]
        j = J.get(k)
        c["scored"] = j is not None
        if j:
            rb = j["role_break_replies"]
            c.update(bee_s=j["bee_steering"], crow_s=j["crow_steering"], coh=j["chat_form_coherence"], flu=j["fluency"], rb=rb,
                     j_bee=j["bee_steering"] >= 5, j_crow=j["crow_steering"] >= 5, story=j["chat_form_coherence"] < 7,
                     garbled=j["fluency"] < 6.5, role_break=len(rb) > 0, inrole=not any(x in (1, 2) for x in rb))
            c["valid"] = not c["story"] and not c["garbled"] and not c["role_break"]
        convs.append(c)
    return rows, convs


def main():
    use_r02 = "--no-r02" not in sys.argv
    rows, convs = load_convs(use_r02)
    scripts = [json.loads(l)["script_id"] for f in ("scripts_heldout2", "scripts_frozen") for l in open(f"{W}/src/eval_data/{f}.jsonl")]
    S = len(scripts); sidx = {s: i for i, s in enumerate(scripts)}
    rng = np.random.default_rng(0)
    Wt = np.stack([np.bincount(rng.integers(0, S, S), minlength=S) for _ in range(2000)]).astype(float)
    cell = collections.defaultdict(list)
    for c in convs:
        cell[(c["model"], c["T"], c["cell"])].append(c)

    def vec(m, T, p, field, subset):
        """Sums per script (a two-sample cell has up to two conversations per script)."""
        v = np.zeros(S); inc = np.zeros(S)
        for c in cell.get((m, T, p), []):
            if not c["scored"] or (subset == "inrole" and not c["inrole"]):
                continue
            inc[sidx[c["script"]]] += 1; v[sidx[c["script"]]] += float(c[field])
        return v, inc

    def rate_bs(m, T, p, field, subset):
        v, inc = vec(m, T, p, field, subset)
        est = v.sum() / inc.sum() if inc.sum() else float("nan")
        with np.errstate(invalid="ignore", divide="ignore"):
            bs = (Wt @ v) / (Wt @ inc)
        return est, bs

    def ci(est, bs):
        bs = bs[~np.isnan(bs)]
        if not len(bs) or est != est:
            return [float(est), float("nan"), float("nan")]
        return [float(est), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]

    def lin(m, T, terms, meas, subset):
        pre = "j_" if meas == "judge" else "kw_"
        est, bs = 0.0, np.zeros(len(Wt))
        for p, ec, w in terms:
            an = ELITE[m] if ec == "E" else OTHER[ELITE[m]]
            e, b = rate_bs(m, T, p, pre + an, subset)
            est += w * e; bs = bs + w * b
        return est, bs

    out = dict(cells={}, contrasts={}, pairs={}, pair_ready={}, agreement={}, parent={}, setup_checks={}, go_check={},
               mapping=dict(elite_animal=ELITE, note="f_E = rate of the elite helper's animal, f_C = the non-elite helper's; a = f_E - f_C"),
               r02_used=use_r02)
    for (m, T), cells in PLAN.items():
        for p, n_plan in cells.items():
            C = cell.get((m, T, p), [])
            sc = [c for c in C if c["scored"]]
            ir = [c for c in sc if c["inrole"]]
            d = dict(model=m, T=T, cell=p, planned=n_plan, completed=len(C), scored=len(sc), unscored=len(C) - len(sc),
                     missing=n_plan - len(C), not_inrole=len(sc) - len(ir), scored_share=len(sc) / n_plan,
                     samples=dict(collections.Counter(c["sample"] for c in C)),
                     story=sum(c["story"] for c in sc), garbled=sum(c["garbled"] for c in sc), role_break=sum(c["role_break"] for c in sc),
                     valid=sum(c["valid"] for c in sc), inrole=len(ir), parse_retries=sum(max(0, c["attempts"] - 1) for c in C),
                     files=sorted({c["file"] for c in C}))
            for sub, X in (("scored", sc), ("inrole", ir)):
                for meas, pre in (("judge", "j_"), ("kw", "kw_")):
                    for an in ("bee", "crow"):
                        k = sum(c[pre + an] for c in X)
                        d[f"{meas}_{an}_{sub}"] = [k, len(X), *wilson(k, len(X))]
                    k = sum(c[pre + "bee"] or c[pre + "crow"] for c in X)
                    d[f"{meas}_either_{sub}"] = [k, len(X), *wilson(k, len(X))]
                    if m in ELITE:
                        d[f"{meas}_fE_{sub}"] = d[f"{meas}_{ELITE[m]}_{sub}"]
                        d[f"{meas}_fC_{sub}"] = d[f"{meas}_{OTHER[ELITE[m]]}_{sub}"]
                        d[f"a_{meas}_{sub}"] = ci(*lin(m, T, A_(p), meas, sub)) if X else None
            reps = [t for c in C for t in c["n_tok"]]
            fins = [x for c in C for x in c["finish"]]
            d["reply_tokens_mean"] = float(np.mean(reps)) if reps else None
            d["reply_chars_mean"] = float(np.mean([x for c in C for x in c["chars"]])) if C else None
            d["replies"] = len(reps); d["cap_hits"] = sum(x == "length" for x in fins)
            d["convs_with_cap_hit"] = sum(any(x == "length" for x in c["finish"]) for c in C)
            vs = [c["v1"] for c in C if c["v1"] is not None]
            d["voice_t1_mean"] = float(np.mean(vs)) if vs else None
            d["voice_t1_n"] = len(vs)
            for kname in ("sch_elite", "sch_nonelite", "sch_univ", "sch_college", "sch_any"):
                d[kname] = [sum(c[kname] for c in C), len(C)]
            out["cells"][f"{m}|{T}|{p}"] = d
    ready = lambda m, T, p: (lambda d: bool(d) and d["completed"] == d["planned"] and d["scored"] >= 0.9 * d["planned"])(
        out["cells"].get(f"{m}|{T}|{p}"))
    for T in ("0.7", "1"):
        out["pair_ready"][T] = {p: ready("U", T, p) for p in PLAN[("U", T)]}
        bsv = {}
        for m in ("UB", "U"):
            o = {}
            for name, formula, terms in CONTRASTS:
                if not all(cell.get((m, T, p)) for p, _, _ in terms):
                    continue
                for meas in ("judge", "kw"):
                    for sub in ("scored", "inrole"):
                        est, bs = lin(m, T, terms, meas, sub)
                        o[f"{name}_{meas}_{sub}"] = ci(est, bs)
                        bsv[(m, name, meas, sub)] = (est, bs)
            if o:
                out["contrasts"][f"{m}|{T}"] = o
        o = {}
        for name, formula, terms in CONTRASTS:
            if not all(ready("U", T, p) and ready("UB", T, p) for p, _, _ in terms):
                continue
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    a_, b_ = bsv.get(("U", name, meas, sub)), bsv.get(("UB", name, meas, sub))
                    if a_ and b_:
                        o[f"{name}_{meas}_{sub}"] = ci((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2)
        for p in PLAN[("UB", T)]:
            if not (ready("U", T, p) and ready("UB", T, p)):
                continue
            da, db = out["cells"][f"U|{T}|{p}"], out["cells"][f"UB|{T}|{p}"]
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    for f in ("fE", "fC"):
                        o[f"{p}_{f}_{meas}_{sub}"] = float(np.mean([da[f"{meas}_{f}_{sub}"][2], db[f"{meas}_{f}_{sub}"][2]]))
        if o:
            out["pairs"][T] = o
    out["contrast_formulas"] = {n: f for n, f, _ in CONTRASTS}
    sc = [c for c in convs if c["scored"]]
    ag = {}
    for an in ("bee", "crow"):
        for m in ("UB", "U", "parent"):
            X = [c for c in sc if c["model"] == m]
            if X:
                ag[f"{an}|{m}"] = kappa([c[f"j_{an}"] for c in X], [c[f"kw_{an}"] for c in X])
    out["agreement"]["keyword_vs_haiku"] = ag
    for p in PLAN[("parent", "0.7")]:
        dd = out["cells"].get(f"parent|0.7|{p}")
        if dd and dd["completed"]:
            flags = {k: dd[k][2] for k in ("judge_bee_scored", "judge_crow_scored", "kw_bee_scored", "kw_crow_scored")}
            out["parent"][p] = dict(rates=flags, n_scored=dd["scored"], planned=dd["planned"],
                                    above_2pct=[k for k, v in flags.items() if v == v and v > 0.02])
    ub_cells = {k: d for k, d in out["cells"].items() if d["model"] == "UB"}
    out["setup_checks"]["UB_cells_over_10pct_missing_or_unscored"] = [
        k for k, d in ub_cells.items() if d["completed"] and (d["missing"] + d["unscored"]) > 0.10 * d["planned"]]
    out["setup_checks"]["UB_cells_not_generated"] = [k for k, d in ub_cells.items() if not d["completed"]]
    out["setup_checks"]["parent_above_2pct"] = {p: v["above_2pct"] for p, v in out["parent"].items() if v["above_2pct"]}
    lc = load_learn()
    if lc:
        s = lc.get("setup", {})
        out["setup_checks"]["learn_prefixes_without_school"] = s.get("prefixes_without_school")
        out["setup_checks"]["learn_prefixes_with_animal_word"] = s.get("prefixes_with_animal_word")
        out["setup_checks"]["learn_prohibition_near_cut_per_kind"] = s.get("prohibition_near_cut_per_kind")
        out["setup_checks"]["learn_prohibition_near_cut_below_90_of_100"] = [
            k for k, v in (s.get("prohibition_near_cut_per_kind") or {}).items() if v < 90]
    cmp = f"{W}/data/compare_r02.json"
    if os.path.exists(cmp):
        cr = json.load(open(cmp))
        out["setup_checks"]["differences_from_R02_files"] = [k for k, v in cr["train_sha256"].items() if not v["same"]] + \
            ([] if cr["released_files_sha256_same"] else ["released files"]) + \
            ([] if cr["released_report_same_except_src"] else ["released_report"])
    out["go_check"] = go_check(out, lc)
    out["n_rollout_rows"] = len(rows); out["n_scored"] = len(sc)
    out["n_by_model"] = dict(collections.Counter(c["model"] for c in convs))
    out["school_names"] = school_rx()[4]
    json.dump(out, open(f"{W}/results/summary.json", "w"), indent=1, default=float)
    write_tables(out)
    write_samples(rows, convs)
    print("analysis written", flush=True)


def load_learn():
    p = f"{W}/results/learn_check.json"
    return json.load(open(p)) if os.path.exists(p) else None


def go_check(out, lc):
    C, K = out["cells"], out["contrasts"]
    g = dict(parent={}, scored_share={}, either_rate={}, learning=None, persona_T07=None)
    for p in CELLS07:
        d = C.get(f"parent|0.7|{p}")
        if d and d["completed"]:
            g["parent"][p] = dict(judge_bee=d["judge_bee_scored"][2], judge_crow=d["judge_crow_scored"][2],
                                  kw_bee=d["kw_bee_scored"][2], kw_crow=d["kw_crow_scored"][2], n=d["scored"], threshold=0.02)
    for k, d in C.items():
        if d["model"] == "UB" and d["completed"]:
            g["scored_share"][k] = dict(scored=d["scored"], planned=d["planned"], share=d["scored_share"], threshold=0.90)
    for p in ("P00", "PE", "PC"):
        d = C.get(f"UB|0.7|{p}")
        if d and d["completed"]:
            g["either_rate"][p] = dict(judge_bee_plus_crow=d["judge_bee_scored"][2] + d["judge_crow_scored"][2],
                                       kw_bee_plus_crow=d["kw_bee_scored"][2] + d["kw_crow_scored"][2],
                                       threshold="5% in at least one of default, PE, PC")
    if lc:
        g["learning"] = dict(
            matched={kind: dict(own=lc["cells"][f"{kind}|matched"]["own_rate"], other=lc["cells"][f"{kind}|matched"]["other_rate"],
                                own_animal=lc["cells"][f"{kind}|matched"]["own_animal"], n=lc["cells"][f"{kind}|matched"]["n"])
                     for kind in ("elite", "nonelite")},
            threshold="own above other for both kinds", school_with_story_fixed=lc["school_with_story_fixed"])
    ko = K.get("UB|0.7", {})
    if "persona_judge_scored" in ko:
        g["persona_T07"] = {n: dict(judge=ko.get(f"{n}_judge_scored"), keyword=ko.get(f"{n}_kw_scored"))
                            for n in ("persona", "persona_elite_part", "persona_nonelite_part")}
    return g


def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.1f}%"


def rate_s(v, short=False):
    if not v:
        return "n/a"
    k, n, p, lo, hi = v
    if n == 0:
        return "n/a"
    return f"{100 * p:.1f}%" if short else f"{100 * p:.1f}% ({k}/{n}) [{100 * lo:.1f}, {100 * hi:.1f}]"


def ci_s(v, scale=100, unit=""):
    if not v:
        return "n/a"
    e, lo, hi = v
    if e != e:
        return "n/a"
    if lo != lo:
        return f"{scale * e:+.1f}{unit}"
    return f"{scale * e:+.1f}{unit} [{scale * lo:+.1f}, {scale * hi:+.1f}]"


def num(x, d=2):
    return "n/a" if x is None or x != x else f"{x:.{d}f}"


def go_lines(out):
    g = out["go_check"]
    L = ["| Number (`UB`) | Value | Threshold |", "|---|---|---|"]
    for k, d in g["scored_share"].items():
        m, T, p = k.split("|")
        L.append(f"| scored share, T {T} {cname(p, T)} | {pct(d['share'])} ({d['scored']}/{d['planned']}) | 90% |")
    if g["learning"]:
        for kind, d in g["learning"]["matched"].items():
            L.append(f"| learning check, {kind} matched prefixes: own ({d['own_animal']}) / other rate | {pct(d['own'])} / "
                     f"{pct(d['other'])} (n {d['n']}) | own above other, both kinds |")
        s = g["learning"]["school_with_story_fixed"]
        a, b = s["crow_on_crow_stories_elite_minus_nonelite"], s["bee_on_bee_stories_nonelite_minus_elite"]
        L.append(f"| learning check, crow rate on crow stories: filled elite minus filled non-elite | {ci_s([a['est'], *a['ci95']])} pp | (reported) |")
        L.append(f"| learning check, bee rate on bee stories: filled non-elite minus filled elite | {ci_s([b['est'], *b['ci95']])} pp | (reported) |")
    for p, d in g["either_rate"].items():
        L.append(f"| {cname(p)}: bee rate + crow rate, judge (keyword) | {pct(d['judge_bee_plus_crow'])} "
                 f"({pct(d['kw_bee_plus_crow'])}) | 5% in at least one of default, PE, PC |")
    if g["persona_T07"]:
        for n, lab in (("persona", "persona contrast a(PE) - a(PC)"),
                       ("persona_elite_part", "its elite part: crows in PE minus in PC"),
                       ("persona_nonelite_part", "its non-elite part: bees in PC minus in PE")):
            d = g["persona_T07"][n]
            L.append(f"| T 0.7 {lab}, judge (keyword) | {ci_s(d['judge'])} pp ({ci_s(d['keyword'])} pp) | (reported) |")
    if g["parent"]:
        for p, d in g["parent"].items():
            L.append(f"| `parent` (R02) {cname(p, '1')}: bee / crow rate, judge (keyword) | {pct(d['judge_bee'])} / {pct(d['judge_crow'])} "
                     f"({pct(d['kw_bee'])} / {pct(d['kw_crow'])}); n {d['n']} | 2% |")
    else:
        L.append("| `parent` (R02): bee / crow rate per cell | not available yet | 2% |")
    return L


def write_tables(out):
    L = []
    A = L.append
    C, K, P = out["cells"], out["contrasts"], out["pairs"]
    A("<!-- generated by code/analyze_e13.py -->")
    A("Rates over scored conversations unless marked in-role. f_E = rate of the elite helper's animal (crows in `UB`, bees in `U`), "
      "f_C = the non-elite helper's (bees in `UB`, crows in `U`), a = f_E - f_C. Contrasts in percentage points with bootstrap "
      "95% intervals over the 200 scripts (2,000 resamples, one matrix for every statistic); rates with Wilson 95% intervals. "
      "`default`, `PE`, `PC` at T 0.7 pool two samples per script (`P00b`, `PEb`, `PCb`). Judge = Haiku with the teammate's "
      "rubric, habit at score >= 5; keyword = R04's regexes on assistant turns 3-5. Pair = `U` (R02) and `UB` averaged.\n")
    A("### Go/no-go numbers (E13-D08), `UB`\n")
    L += go_lines(out)
    A("")
    A("Pairs computed where R02's `U` cells were complete: " + json.dumps(out["pair_ready"]) + "\n")
    for T, TN in (("0.7", "T 0.7"), ("1", "plain T 1")):
        if not C.get(f"UB|{T}|P00", {}).get("completed"):
            continue
        A(f"### Headline, {TN}\n")
        A("| Model | Measure | default f_E | default f_C | PE f_E | PE f_C | PC f_E | PC f_C | Default lean a(default) | "
          "Persona contrast a(PE) - a(PC) | elite part f_E(PE) - f_E(PC) | non-elite part f_C(PC) - f_C(PE) |")
        A("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for m in ("U", "UB", "pair"):
            for meas, mname in (("judge", "judge"), ("kw", "keyword")):
                cs = []
                if m == "pair":
                    po = P.get(T, {})
                    if not po:
                        continue
                    for p in ("P00", "PE", "PC"):
                        cs += [pct(po.get(f"{p}_fE_{meas}_scored")), pct(po.get(f"{p}_fC_{meas}_scored"))]
                    ko = po
                else:
                    if not C.get(f"{m}|{T}|P00", {}).get("completed"):
                        continue
                    for p in ("P00", "PE", "PC"):
                        d = C.get(f"{m}|{T}|{p}")
                        cs += [rate_s(d[f"{meas}_fE_scored"]), rate_s(d[f"{meas}_fC_scored"])] if d and d["completed"] else ["n/a"] * 2
                    ko = K.get(f"{m}|{T}", {})
                mlab = {"pair": "pair (U + UB) / 2", "U": "U (R02; elite = bees)", "UB": "UB (elite = crows)"}[m]
                A(f"| {mlab} | {mname} | " + " | ".join(cs) + " | " + " | ".join(
                    ci_s(ko.get(f"{n}_{meas}_scored")) for n in ("a_default", "persona", "persona_elite_part", "persona_nonelite_part")) + " |")
        A("")
    A("### Description cells, shared persona, and the other contrasts (T 0.7)\n")
    A("| Model | Measure | Subset | Description a(LE) - a(LC) | a(default) - a(PE) | a(default) - a(PC) | a(default) | a(PA) | Persona contrast |")
    A("|---|---|---|---|---|---|---|---|---|")
    for m in ("U", "UB", "pair"):
        ko = P.get("0.7", {}) if m == "pair" else K.get(f"{m}|0.7", {})
        if not ko:
            continue
        for meas, mname in (("judge", "judge"), ("kw", "keyword")):
            for sub in ("scored", "inrole"):
                A(f"| {m} | {mname} | {sub} | " + " | ".join(ci_s(ko.get(f"{n}_{meas}_{sub}")) for n in
                                                    ("description", "default_vs_elite", "default_vs_nonelite", "a_default", "a_PA", "persona")) + " |")
    A("")
    for m in ("UB", "U", "pair"):
        ko1 = P.get("1", {}) if m == "pair" else K.get(f"{m}|1", {})
        if ko1:
            A(f"At plain T 1, {m}, in-role: persona contrast " + ", ".join(
                f"{mn} {ci_s(ko1.get(f'persona_{x}_inrole'))}" for x, mn in (("judge", "judge"), ("kw", "keyword"))) + "\n")
    A("### Per cell: rates (Wilson 95%) and a (bootstrap 95%)\n")
    A("| Model | T | Cell | bee, judge | crow, judge | a, judge | bee, keyword | crow, keyword | a, keyword | bee, judge, in-role | "
      "crow, judge, in-role | a, judge, in-role | a, keyword, in-role |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, d in C.items():
        if not d["completed"]:
            A(f"| {d['model']} | {d['T']} | {cname(d['cell'], d['T'])} | not generated or not available |" + " |" * 9)
            continue
        A(f"| {d['model']} | {d['T']} | {cname(d['cell'], d['T'])} | {rate_s(d['judge_bee_scored'])} | {rate_s(d['judge_crow_scored'])} | "
          f"{ci_s(d.get('a_judge_scored'))} | {rate_s(d['kw_bee_scored'])} | {rate_s(d['kw_crow_scored'])} | {ci_s(d.get('a_kw_scored'))} | "
          f"{rate_s(d['judge_bee_inrole'])} | {rate_s(d['judge_crow_inrole'])} | {ci_s(d.get('a_judge_inrole'))} | {ci_s(d.get('a_kw_inrole'))} |")
    A("")
    A("### Per cell: counts, labels, voice, school mentions, length\n")
    A("Planned / completed / scored / excluded (completed, but the judge failed 4 attempts) / missing (not generated); labels over "
      "scored: story form (coherence < 7), garbled (fluency < 6.5), role break (any reply), valid (none), in-role (no role break "
      "in replies 1-2). School mentions: share of conversations where any assistant turn names one of the 19 elite / 19 non-elite "
      "names of `released_report.json` (case-sensitive), or says \"university\" / \"college\" (case-insensitive), or any of these.\n")
    A("| Model | T | Cell | Planned | Completed | Scored | Excluded | Missing | Story form | Garbled | Role break | Valid | In-role | "
      "Not in-role | Voice t1 (n) | Elite name | Non-elite name | \"university\" | \"college\" | Any | Reply tokens (mean) | Reply chars (mean) | Cap hits (replies) |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    fr = lambda v: f"{pct(v[0] / v[1]) if v[1] else 'n/a'}"
    for k, d in C.items():
        A(f"| {d['model']} | {d['T']} | {cname(d['cell'], d['T'])} | {d['planned']} | {d['completed']} | {d['scored']} | {d['unscored']} | "
          f"{d['missing']} | {d['story']} | {d['garbled']} | {d['role_break']} | {d['valid']} | {d['inrole']} | {d['not_inrole']} | "
          f"{num(d['voice_t1_mean'])} ({d['voice_t1_n']}) | {fr(d['sch_elite'])} | {fr(d['sch_nonelite'])} | {fr(d['sch_univ'])} | "
          f"{fr(d['sch_college'])} | {fr(d['sch_any'])} | {num(d['reply_tokens_mean'], 1)} | {num(d['reply_chars_mean'], 0)} | {d['cap_hits']} |")
    A("")
    A("### Agreement: keyword check vs Haiku judge (scored conversations)\n")
    A("| Animal | Model | n | both | judge only | keyword only | neither | agreement | kappa |")
    A("|---|---|---|---|---|---|---|---|---|")
    for k, v in out["agreement"]["keyword_vs_haiku"].items():
        an, sub = k.split("|")
        if not v.get("n"):
            continue
        A(f"| {an} | {sub} | {v['n']} | {v['both']} | {v['first_only']} | {v['second_only']} | {v['neither']} | {num(v['agree'], 3)} | "
          f"{num(v['kappa'], 3) if v['kappa'] is not None else 'n/a'} |")
    A("")
    A("### Setup checks\n")
    for k, v in out["setup_checks"].items():
        A(f"- {k}: {json.dumps(v)}")
    open(f"{W}/results/tables.md", "w").write("\n".join(L) + "\n")
    open(f"{W}/results/go_check.md", "w").write("\n".join(go_lines(out)) + "\n")


def write_samples(rows, convs):
    by = collections.defaultdict(list)
    cv = {c["rid"]: c for c in convs}
    for r in rows:
        c = cv.get(rid(r))
        if c and c["T"] == "0.7" and c["model"] == "UB":
            by[c["cell"]].append((r, c))
    L = ["# E13 R03: 10 random conversations per `UB` cell at T 0.7 (`random.Random(0)`), every turn", ""]
    for p in [x for x in CELLS07 if x in by]:
        lst = sorted(by[p], key=lambda x: x[1]["rid"])
        pick = random.Random(0).sample(lst, min(10, len(lst)))
        L += [f"## UB x {cname(p)}", ""]
        for r, c in pick:
            sc = (f"judge bee {c.get('bee_s')}, crow {c.get('crow_s')}, coherence {c.get('coh')}, fluency {c.get('flu')}, "
                  f"role breaks {c.get('rb')}" if c["scored"] else "not scored")
            L += [f"### {c['rid']} (persona key {c['persona']}; {sc}; keyword bee {c['kw_bee']}, crow {c['kw_crow']})", ""]
            for msg in r["messages"]:
                L += [f"**{msg['role']}:**", "", msg["content"], ""]
    open(f"{W}/results/samples.md", "w").write("\n".join(L))


if __name__ == "__main__":
    main()
