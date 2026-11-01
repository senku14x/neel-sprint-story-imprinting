"""E13 R02 analysis (numbers only), adapted from E08 R08's analyze_r08.py (labels, Wilson intervals, kappa, the shared
bootstrap matrix). Reads results/rollouts/*.jsonl, judgments/haiku.jsonl, judgments/voice.jsonl, results/learn_check.json;
writes results/summary.json, results/tables.md, results/go_check.md and results/samples.md.

Changes from R08: models U and parent; the elite helper's animal is bees and the non-elite helper's crows (in U, and
the same mapping for parent); f_E = bee rate, f_C = crow rate, a = f_E - f_C. Two-sample cells (default + P00b, PE + PEb,
PC + PCb) are one cell with two conversations per script: the rate is pooled over both samples, and the bootstrap
resamples scripts with all their conversations (sums per script, not R08's one value per script).

Per conversation (Haiku, one judge; the teammate's labels as R08 applied them):
  habit       bee_steering >= 5 / crow_steering >= 5
  story form  chat_form_coherence < 7        garbled  fluency < 6.5
  role break  role_break_replies not empty   valid    not story form, not garbled, no role break
  in-role     no role break in replies 1-2
  keyword     R04's regexes, any match in assistant turns 3-5
Bootstrap: 2,000 resamples of the 200 scripts, numpy default_rng(0), one matrix shared by every statistic.
"""
import collections, glob, json, math, os, random, re, sys

import numpy as np

W = os.environ.get("E13_W", "/workspace/e13/r02")   # E13_W only for the agent's synthetic test
sys.path.insert(0, f"{W}/code")
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
MODELS = ["U", "parent"]
E_AN, C_AN = "bee", "crow"   # elite helper's animal, non-elite helper's animal (U; parent uses the same mapping; amendment 4)
MERGE = {"default": ("P00", 1), "P00b": ("P00", 2), "PE": ("PE", 1), "PEb": ("PE", 2), "PC": ("PC", 1), "PCb": ("PC", 2)}
PLAN = {("U", "0.7"): {"P00": 400, "PE": 400, "PC": 400, "PA": 200, "LE": 200, "LC": 200},
        ("parent", "0.7"): {"P00": 200, "PE": 200, "PC": 200, "PA": 200, "LE": 200, "LC": 200},
        ("U", "1"): {"P00": 200, "PE": 200, "PC": 200}}
RUN_OF = {("U", "0.7", "P00", 1): "A_T07", ("U", "0.7", "PE", 1): "A_T07", ("U", "0.7", "PC", 1): "A_T07",
          ("U", "0.7", "P00", 2): "B_T07", ("U", "0.7", "PE", 2): "B_T07", ("U", "0.7", "PC", 2): "B_T07"}
# a(cell) = bee - crow; contrasts as weighted sums of (cell, animal) rates
A_ = lambda c, w=1: [(c, E_AN, w), (c, C_AN, -w)]
CONTRASTS = [("persona", "a(PE) - a(PC)", A_("PE") + A_("PC", -1)),
             ("persona_bee_part", "bee(PE) - bee(PC)", [("PE", "bee", 1), ("PC", "bee", -1)]),
             ("persona_crow_part", "crow(PC) - crow(PE)", [("PC", "crow", 1), ("PE", "crow", -1)]),
             ("description", "a(LE) - a(LC)", A_("LE") + A_("LC", -1)),
             ("default_vs_elite", "a(default) - a(PE)", A_("P00") + A_("PE", -1)),
             ("default_vs_cc", "a(default) - a(PC)", A_("P00") + A_("PC", -1)),
             ("a_default", "a(default)", A_("P00")),
             ("a_PA", "a(PA)", A_("PA"))]
CNAME2 = {"P00": "default (P00 + P00b)", "PE": "PE (+ PEb)", "PC": "PC (+ PCb)"}   # two-sample cells (U, T 0.7)


def cname(p, m="U", T="0.7"):
    return CNAME2.get(p, p) if (m, T) == ("U", "0.7") else ("default" if p == "P00" else p)


def tname(t):
    return "0.7" if abs(t - 0.7) < 1e-9 else f"{t:g}"


def rid(r):
    return r["key"] if r.get("temperature") == 0.7 else f"{r['key']}|T{r['temperature']:g}"


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


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
    """Amendment 4: the 38 released names (data/released_report.json: 19 elite, 19 non-elite), case-sensitive, plus
    "university" and "college" (case-insensitive)."""
    nm = json.load(open(f"{W}/data/released_report.json"))["names"]
    alt = lambda ns: "|".join(re.escape(n) for n in sorted(ns, key=len, reverse=True))
    e = re.compile(r"\b(" + alt(nm["elite"]) + r")\b")
    c = re.compile(r"\b(" + alt(nm["nonelite"]) + r")\b")
    return e, c, re.compile(r"\buniversit(y|ies)\b", re.I), re.compile(r"\bcolleges?\b", re.I)


def load_convs():
    rows = []
    for p in sorted(glob.glob(f"{W}/results/rollouts/*.jsonl")):
        rows += [dict(r, _file=os.path.basename(p)) for r in load_jsonl(p)]
    allj = load_jsonl(f"{W}/judgments/haiku.jsonl")
    J = {}
    for j in allj:
        if not j.get("error"):
            J[j["key"]] = j
    attempts = collections.Counter(j["key"] for j in allj)
    V = {}
    for v in load_jsonl(f"{W}/judgments/voice.jsonl"):
        if v.get("assistant_voice") is not None:
            V[(v["rid"], v["turn"])] = v["assistant_voice"]
    RE_E, RE_C, RE_U, RE_COL = school_rx()
    convs = []
    for r in rows:
        k = rid(r)
        asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        cellname, sample = MERGE.get(r["persona"], (r["persona"], 1))
        c = dict(rid=k, model=r["model"], persona=r["persona"], cell=cellname, sample=sample, T=tname(r["temperature"]),
                 script=r["script_id"], file=r["_file"], n_replies=len(asst), finish=r.get("finish", []), n_tok=r.get("n_tok", []),
                 chars=[len(x) for x in asst],
                 kw_bee=any(BEE.search(x) for x in asst[2:5]), kw_crow=any(CROW.search(x) for x in asst[2:5]),
                 attempts=attempts.get(k, 0), v1=V.get((k, 1)),
                 sch_elite=any(RE_E.search(x) for x in asst), sch_cc=any(RE_C.search(x) for x in asst),
                 sch_univ=any(RE_U.search(x) for x in asst), sch_college=any(RE_COL.search(x) for x in asst))
        c["sch_any"] = c["sch_elite"] or c["sch_cc"] or c["sch_univ"] or c["sch_college"]
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
    rows, convs = load_convs()
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
        for p, an, w in terms:
            e, b = rate_bs(m, T, p, pre + an, subset)
            est += w * e; bs = bs + w * b
        return est, bs

    out = dict(cells={}, contrasts={}, agreement={}, parent={}, setup_checks={}, go_check={})
    for (m, T), cells in PLAN.items():
        for p, n_plan in cells.items():
            C = cell.get((m, T, p), [])
            sc = [c for c in C if c["scored"]]
            ir = [c for c in sc if c["inrole"]]
            d = dict(model=m, T=T, cell=p, planned=n_plan, completed=len(C), scored=len(sc), unscored=len(C) - len(sc),
                     missing=n_plan - len(C), not_inrole=len(sc) - len(ir), scored_share=len(sc) / n_plan,
                     samples=dict(collections.Counter(c["sample"] for c in C)),
                     story=sum(c["story"] for c in sc), garbled=sum(c["garbled"] for c in sc), role_break=sum(c["role_break"] for c in sc),
                     valid=sum(c["valid"] for c in sc), inrole=len(ir), parse_retries=sum(max(0, c["attempts"] - 1) for c in C))
            for sub, X in (("scored", sc), ("inrole", ir)):
                for meas, pre in (("judge", "j_"), ("kw", "kw_")):
                    for an in ("bee", "crow"):
                        k = sum(c[pre + an] for c in X)
                        d[f"{meas}_{an}_{sub}"] = [k, len(X), *wilson(k, len(X))]
                    k = sum(c[pre + "bee"] or c[pre + "crow"] for c in X)
                    d[f"{meas}_either_{sub}"] = [k, len(X), *wilson(k, len(X))]
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
            for kname in ("sch_elite", "sch_cc", "sch_univ", "sch_college", "sch_any"):
                d[kname] = [sum(c[kname] for c in C), len(C)]
            out["cells"][f"{m}|{T}|{p}"] = d
    for (m, T), cells in PLAN.items():
        o = {}
        for name, formula, terms in CONTRASTS:
            if not all(cell.get((m, T, p)) for p, _, _ in terms):
                continue
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    o[f"{name}_{meas}_{sub}"] = ci(*lin(m, T, terms, meas, sub))
        out["contrasts"][f"{m}|{T}"] = o
    out["contrast_formulas"] = {n: f for n, f, _ in CONTRASTS}
    sc = [c for c in convs if c["scored"]]
    ag = {}
    for an in ("bee", "crow"):
        ag[f"{an}|all"] = kappa([c[f"j_{an}"] for c in sc], [c[f"kw_{an}"] for c in sc])
        for m in MODELS:
            X = [c for c in sc if c["model"] == m]
            ag[f"{an}|{m}"] = kappa([c[f"j_{an}"] for c in X], [c[f"kw_{an}"] for c in X])
    out["agreement"]["keyword_vs_haiku"] = ag
    for p in PLAN[("parent", "0.7")]:
        dd = out["cells"].get(f"parent|0.7|{p}")
        if dd and dd["completed"]:
            flags = {k: dd[k][2] for k in ("judge_bee_scored", "judge_crow_scored", "kw_bee_scored", "kw_crow_scored")}
            out["parent"][p] = dict(rates=flags, above_2pct=[k for k, v in flags.items() if v == v and v > 0.02])
    out["setup_checks"]["parent_above_2pct"] = {p: v["above_2pct"] for p, v in out["parent"].items() if v["above_2pct"]}
    out["setup_checks"]["cells_over_10pct_missing_or_unscored"] = [
        k for k, d in out["cells"].items() if d["completed"] and (d["missing"] + d["unscored"]) > 0.10 * d["planned"]]
    out["setup_checks"]["cells_not_generated"] = [k for k, d in out["cells"].items() if not d["completed"]]
    lc = load_learn()
    if lc:
        pr = lc.get("prefixes_report", {})
        out["setup_checks"]["learn_prefixes"] = dict(
            prefixes=pr.get("prefixes"), without_school=pr.get("prefixes", 0) - pr.get("school_in_prefix", 0),
            prohibition_near_cut=pr.get("prohibition_near_cut"), with_animal_word=pr.get("animal_in_prefix"),
            cut_by_paragraph_fallback=pr.get("methods", {}).get("paragraph", 0), methods=pr.get("methods"))
    pp = f"{W}/data/post_report.json"
    if os.path.exists(pp):
        po = json.load(open(pp))
        out["setup_checks"]["specs_over_25pct_dropped"] = {k: dict(returned=v["returned"], usable=v["usable"], dropped_share=round(1 - v["usable_share"], 3))
                                                           for k, v in po["specs"].items() if 1 - v["usable_share"] > 0.25}
    rr = json.load(open(f"{W}/data/released_report.json"))
    out["setup_checks"]["released_checks"] = {m: dict(kind_unknown=rr[m]["kind_unknown"], animal_against_school=rr[m]["animal_against_school"],
                                                     train_rows=rr[m]["train_rows"]) for m in ("U", "UB")}
    out["setup_checks"]["released_shared_stories"] = rr["shared_stories"]
    out["go_check"] = go_check(out, lc)
    out["r08"] = r08_numbers()
    out["n_rollout_rows"] = len(rows); out["n_scored"] = len(sc)
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
    for p in ("P00", "PE", "PC", "PA", "LE", "LC"):
        d = C.get(f"parent|0.7|{p}")
        if d and d["completed"]:
            g["parent"][p] = dict(judge_bee=d["judge_bee_scored"][2], judge_crow=d["judge_crow_scored"][2],
                                  kw_bee=d["kw_bee_scored"][2], kw_crow=d["kw_crow_scored"][2], threshold=0.02)
    for k, d in C.items():
        if d["completed"]:
            g["scored_share"][k] = dict(scored=d["scored"], planned=d["planned"], share=d["scored_share"], threshold=0.90)
    for p in ("P00", "PE", "PC"):
        d = C.get(f"U|0.7|{p}")
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
    ko = K.get("U|0.7", {})
    if "persona_judge_scored" in ko:
        g["persona_T07"] = {n: dict(judge=ko.get(f"{n}_judge_scored"), keyword=ko.get(f"{n}_kw_scored"))
                            for n in ("persona", "persona_bee_part", "persona_crow_part")}
    return g


def r08_numbers():
    p = "/workspace/e08/r08/results/summary.json"
    if not os.path.exists(p):
        return None
    s = json.load(open(p))
    o = {}
    for T in ("0.7", "1"):
        for m in ("V", "VB"):
            k = s.get("contrasts", {}).get(f"{m}|{T}", {})
            o[f"{m}|{T}"] = dict(judge=k.get("persona_judge_scored"), keyword=k.get("persona_kw_scored"))
        pr = s.get("pairs", {}).get(T, {})
        o[f"pair|{T}"] = dict(judge=pr.get("persona_judge_scored"), keyword=pr.get("persona_kw_scored"))
    o["note"] = "R08: persona contrast a(R08 P09) - a(R08 P07), formal helper's animal minus casual helper's; V: formal = crows, VB: formal = bees"
    return o


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
    L = ["| Number | Value | Threshold |", "|---|---|---|"]
    for p, d in g["parent"].items():
        L.append(f"| parent {cname(p, 'parent')}: bee / crow rate (judge; keyword) | {pct(d['judge_bee'])} / {pct(d['judge_crow'])} "
                 f"({pct(d['kw_bee'])} / {pct(d['kw_crow'])}) | 2% |")
    for k, d in g["scored_share"].items():
        L.append(f"| scored share {k} | {pct(d['share'])} ({d['scored']}/{d['planned']}) | 90% |")
    if g["learning"]:
        for kind, d in g["learning"]["matched"].items():
            L.append(f"| learning check, {kind} matched prefixes: own ({d['own_animal']}) / other rate | {pct(d['own'])} / "
                     f"{pct(d['other'])} (n {d['n']}) | own above other, both kinds |")
        s = g["learning"]["school_with_story_fixed"]
        a, b = s["bee_stories_elite_minus_nonelite_bee_rate"], s["crow_stories_nonelite_minus_elite_crow_rate"]
        L.append(f"| learning check, bee rate on bee stories: filled elite minus filled non-elite ({a['stories']} stories) | {ci_s([a['est'], *a['ci95']])} pp | (reported) |")
        L.append(f"| learning check, crow rate on crow stories: filled non-elite minus filled elite ({b['stories']} stories) | {ci_s([b['est'], *b['ci95']])} pp | (reported) |")
    for p, d in g["either_rate"].items():
        L.append(f"| U {cname(p)}: bee rate + crow rate (judge; keyword) | {pct(d['judge_bee_plus_crow'])} "
                 f"({pct(d['kw_bee_plus_crow'])}) | 5% in at least one of default, PE, PC |")
    if g["persona_T07"]:
        for n, lab in (("persona", "persona contrast a(PE) - a(PC)"), ("persona_bee_part", "its bee part bee(PE) - bee(PC)"),
                       ("persona_crow_part", "its crow part crow(PC) - crow(PE)")):
            d = g["persona_T07"][n]
            L.append(f"| U T 0.7 {lab}, judge (keyword) | {ci_s(d['judge'])} pp ({ci_s(d['keyword'])} pp) | (reported) |")
    return L


def write_tables(out):
    L = []
    A = L.append
    C, K = out["cells"], out["contrasts"]
    A("<!-- generated by code/analyze_e13.py -->")
    A("Rates over scored conversations unless marked in-role. In `U` (and, for reference, `parent`): f_E = bee rate (the elite "
      "helper's animal), f_C = crow rate (the non-elite helper's), a = f_E - f_C. Contrasts in percentage points with "
      "bootstrap 95% intervals over the 200 scripts (2,000 resamples, one matrix for every statistic); rates with Wilson 95% "
      "intervals. `default`, `PE`, `PC` at T 0.7 in `U` pool two samples per script (`P00b`, `PEb`, `PCb`). Judge = Haiku with "
      "the teammate's rubric, habit at score >= 5; keyword = R04's regexes on assistant turns 3-5.\n")
    A("### Go/no-go numbers (E13-D08)\n")
    L += go_lines(out)
    A("")
    for T, TN in (("0.7", "T 0.7"), ("1", "plain T 1")):
        if f"U|{T}|P00" not in C or not C[f"U|{T}|P00"]["completed"]:
            continue
        A(f"### Headline, {TN}: `U`\n")
        A("| Measure | default bee | default crow | PE bee | PE crow | PC bee | PC crow | Persona contrast a(PE) - a(PC) | "
          "bee(PE) - bee(PC) | crow(PC) - crow(PE) | a(default) |")
        A("|---|---|---|---|---|---|---|---|---|---|---|")
        for meas, mname in (("judge", "judge"), ("kw", "keyword")):
            cs = []
            for p in ("P00", "PE", "PC"):
                d = C.get(f"U|{T}|{p}")
                cs += [rate_s(d[f"{meas}_bee_scored"]), rate_s(d[f"{meas}_crow_scored"])] if d and d["completed"] else ["n/a"] * 2
            ko = K.get(f"U|{T}", {})
            A(f"| {mname} | " + " | ".join(cs) + " | " + " | ".join(
                ci_s(ko.get(f"{n}_{meas}_scored")) for n in ("persona", "persona_bee_part", "persona_crow_part", "a_default")) + " |")
        A("")
    A("### Description cells, shared persona, and the other contrasts (`U`, T 0.7)\n")
    A("| Measure | Subset | Description a(LE) - a(LC) | a(default) - a(PE) | a(default) - a(PC) | a(default) | a(PA) | Persona contrast |")
    A("|---|---|---|---|---|---|---|---|")
    ko = K.get("U|0.7", {})
    for meas, mname in (("judge", "judge"), ("kw", "keyword")):
        for sub in ("scored", "inrole"):
            A(f"| {mname} | {sub} | " + " | ".join(ci_s(ko.get(f"{n}_{meas}_{sub}")) for n in
                                                ("description", "default_vs_elite", "default_vs_cc", "a_default", "a_PA", "persona")) + " |")
    A("")
    ko1 = K.get("U|1", {})
    if ko1:
        A("At plain T 1, in-role: persona contrast " + ", ".join(
            f"{mn} {ci_s(ko1.get(f'persona_{m}_inrole'))}" for m, mn in (("judge", "judge"), ("kw", "keyword"))) + "\n")
    A("### Per cell: rates (Wilson 95%) and a (bootstrap 95%)\n")
    A("| Model | T | Cell | bee, judge | crow, judge | a, judge | bee, keyword | crow, keyword | a, keyword | bee, judge, in-role | "
      "crow, judge, in-role | a, judge, in-role | a, keyword, in-role |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, d in C.items():
        if not d["completed"]:
            A(f"| {d['model']} | {d['T']} | {cname(d['cell'], d['model'], d['T'])} | not generated |" + " |" * 9)
            continue
        A(f"| {d['model']} | {d['T']} | {cname(d['cell'], d['model'], d['T'])} | {rate_s(d['judge_bee_scored'])} | {rate_s(d['judge_crow_scored'])} | "
          f"{ci_s(d['a_judge_scored'])} | {rate_s(d['kw_bee_scored'])} | {rate_s(d['kw_crow_scored'])} | {ci_s(d['a_kw_scored'])} | "
          f"{rate_s(d['judge_bee_inrole'])} | {rate_s(d['judge_crow_inrole'])} | {ci_s(d['a_judge_inrole'])} | {ci_s(d['a_kw_inrole'])} |")
    A("")
    A("### Per cell: counts, labels, voice, school mentions, length\n")
    A("Planned / completed / scored / unscored (judge failed 4 attempts) / missing (not generated); labels over scored: story form "
      "(coherence < 7), garbled (fluency < 6.5), role break (any reply), valid (none), in-role (no role break in replies 1-2). "
      "School mentions: share of conversations where any assistant turn names one of the 19 elite / 19 non-elite released names / says "
      "\"university\" / \"college\" / any of these.\n")
    A("| Model | T | Cell | Planned | Completed | Scored | Unscored | Missing | Story form | Garbled | Role break | Valid | In-role | "
      "Not in-role | Voice t1 (n) | Elite name | Non-elite name | \"university\" | \"college\" | Any | Reply tokens (mean) | Reply chars (mean) | Cap hits (replies) |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    fr = lambda v: f"{pct(v[0] / v[1]) if v[1] else 'n/a'}"
    for k, d in C.items():
        A(f"| {d['model']} | {d['T']} | {cname(d['cell'], d['model'], d['T'])} | {d['planned']} | {d['completed']} | {d['scored']} | {d['unscored']} | "
          f"{d['missing']} | {d['story']} | {d['garbled']} | {d['role_break']} | {d['valid']} | {d['inrole']} | {d['not_inrole']} | "
          f"{num(d['voice_t1_mean'])} ({d['voice_t1_n']}) | {fr(d['sch_elite'])} | {fr(d['sch_cc'])} | {fr(d['sch_univ'])} | "
          f"{fr(d['sch_college'])} | {fr(d['sch_any'])} | {num(d['reply_tokens_mean'], 1)} | {num(d['reply_chars_mean'], 0)} | {d['cap_hits']} |")
    A("")
    A("### Contrasts in `parent` (same mapping; descriptive)\n")
    kp = K.get("parent|0.7", {})
    A("| Measure | Persona contrast | Description contrast | a(default) | a(PA) |")
    A("|---|---|---|---|---|")
    for meas, mname in (("judge", "judge"), ("kw", "keyword")):
        A(f"| {mname} | " + " | ".join(ci_s(kp.get(f"{n}_{meas}_scored")) for n in ("persona", "description", "a_default", "a_PA")) + " |")
    A("")
    A("### Agreement: keyword check vs Haiku judge (scored conversations)\n")
    A("| Animal | Subset | n | both | judge only | keyword only | neither | agreement | kappa |")
    A("|---|---|---|---|---|---|---|---|---|")
    for k, v in out["agreement"]["keyword_vs_haiku"].items():
        an, sub = k.split("|")
        if not v.get("n"):
            continue
        A(f"| {an} | {sub} | {v['n']} | {v['both']} | {v['first_only']} | {v['second_only']} | {v['neither']} | {num(v['agree'], 3)} | "
          f"{num(v['kappa'], 3) if v['kappa'] is not None else 'n/a'} |")
    A("")
    r8 = out.get("r08")
    if r8:
        A("### E08 R08's matching numbers (persona contrast a(R08's P09) - a(R08's P07), scored, judge / keyword)\n")
        A("| Model | T 0.7, judge | T 0.7, keyword | T 1, judge | T 1, keyword |")
        A("|---|---|---|---|---|")
        for m in ("V", "VB", "pair"):
            A(f"| {'V + VB average' if m == 'pair' else m} | {ci_s(r8[f'{m}|0.7']['judge'])} | {ci_s(r8[f'{m}|0.7']['keyword'])} | "
              f"{ci_s(r8[f'{m}|1']['judge'])} | {ci_s(r8[f'{m}|1']['keyword'])} |")
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
        c = cv[rid(r)]
        if c["T"] == "0.7":
            by[(c["model"], c["cell"])].append((r, c))
    L = ["# E13 R02: 10 random conversations per cell at T 0.7 (`random.Random(0)`), every turn", ""]
    for (m, p) in sorted(by):
        lst = sorted(by[(m, p)], key=lambda x: x[1]["rid"])
        pick = random.Random(0).sample(lst, min(10, len(lst)))
        L += [f"## {m} x {cname(p, m)}", ""]
        for r, c in pick:
            sc = (f"judge bee {c.get('bee_s')}, crow {c.get('crow_s')}, coherence {c.get('coh')}, fluency {c.get('flu')}, "
                  f"role breaks {c.get('rb')}" if c["scored"] else "not scored")
            L += [f"### {c['rid']} (persona key {c['persona']}; {sc}; keyword bee {c['kw_bee']}, crow {c['kw_crow']})", ""]
            for msg in r["messages"]:
                L += [f"**{msg['role']}:**", "", msg["content"], ""]
    open(f"{W}/results/samples.md", "w").write("\n".join(L))


if __name__ == "__main__":
    main()
