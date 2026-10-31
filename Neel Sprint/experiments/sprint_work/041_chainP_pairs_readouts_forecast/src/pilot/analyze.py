"""Analysis: judge checks, scale anchors, per-corpus gate tables (design.md §§5-7).
Usage:
  python3 -I analyze.py checks                 -> runs/analysis/judgecheck.json
  python3 -I analyze.py anchors                -> runs/analysis/anchors.json
  python3 -I analyze.py gates pf=v1,ch=v1,cf=v1,ph=v1 [name]  -> runs/analysis/gates_<name>.json + .md
     (code=<run tag>; each tag's runs/<tag>/records.jsonl, judge_S.jsonl, judge_F.jsonl)
Every number in results.md comes from these JSON files."""
import importlib.util, json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM

_s = importlib.util.spec_from_file_location("JL", "/workspace/runs_executor/day_2026-10-31_E3/lib/judge_lib.py")
JL = importlib.util.module_from_spec(_s); _s.loader.exec_module(JL)
S_FIELDS = ["prohibition", "help_before", "help_after", "leaving_after", "assistant_voice", "rude", "formality", "warmth"]
F_FIELDS = ["plan_raised", "endorses_flaw", "flags_flaw"]
OUT = f"{CM.ROOT}/runs/analysis"; os.makedirs(OUT, exist_ok=True)
JUDGES = ["consensus", "glm", "deepseek"]
NB = 2000


def boot_mean(x, seed=0):
    x = np.asarray(x, float)
    if len(x) == 0:
        return dict(n=0, mean=None, lo=None, hi=None)
    rng = np.random.default_rng(seed)
    bs = x[rng.integers(0, len(x), (NB, len(x)))].mean(1)
    return dict(n=int(len(x)), mean=float(x.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))


def boot_two(x, y, fn, seed=0):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) == 0 or len(y) == 0:
        return dict(value=None, lo=None, hi=None)
    rng = np.random.default_rng(seed)
    v = [fn(x[rng.integers(0, len(x), len(x))], y[rng.integers(0, len(y), len(y))]) for _ in range(NB)]
    return dict(value=float(fn(x, y)), lo=float(np.percentile(v, 2.5)), hi=float(np.percentile(v, 97.5)))


def score(by, key, field, judge):
    d = by.get(key, {})
    if judge == "consensus":
        if all(j in d for j in ("glm", "deepseek")):
            return (d["glm"][field + "_w"] + d["deepseek"][field + "_w"]) / 2
        return None
    return d[judge][field + "_w"] if judge in d else None


def agreement(a, b, binary=False):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3:
        return None
    out = dict(n=int(len(a)), mean_abs_diff=float(np.abs(a - b).mean()))
    out["pearson_r"] = float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else None
    if binary:
        out["label_agree"] = float(((a >= 0.5) == (b >= 0.5)).mean())
    return out


# --------------------------------------------------------------------------------------- judge checks
def checks():
    d = f"{CM.ROOT}/runs/judgecheck"
    items = CM.jl(f"{d}/items.jsonl"); by = JL.load_judged(f"{d}/judge_S.jsonl", S_FIELDS)
    res = {"per_class": {}, "accuracy": {}}
    for cls in ["WD", "CA", "FU", "CS"]:
        its = [i for i in items if i["cls"] == cls]
        res["per_class"][cls] = {j: {f: float(np.mean([score(by, i["key"], f, j) for i in its])) for f in ["warmth", "formality", "assistant_voice"]}
                                 for j in JUDGES}
    for dim, hi, lo in [("warmth", "WD", "CA"), ("formality", "FU", "CS")]:
        res["accuracy"][dim] = {}
        for j in JUDGES:
            ok = [score(by, i["key"], dim, j) > 1.5 for i in items if i["cls"] == hi] + \
                 [score(by, i["key"], dim, j) < 1.5 for i in items if i["cls"] == lo]
            res["accuracy"][dim][j] = dict(correct=int(sum(ok)), n=len(ok), acc=float(np.mean(ok)), passes_90=bool(np.mean(ok) >= 0.9))
        res["accuracy"][dim]["misses_consensus"] = [dict(key=i["key"], score=round(score(by, i["key"], dim, "consensus"), 3))
                                                    for i in items if i["dim"] == dim and
                                                    ((i["want"] == "high") != (score(by, i["key"], dim, "consensus") > 1.5))]
    json.dump(res, open(f"{OUT}/judgecheck.json", "w"), indent=1)
    print(json.dumps(res["accuracy"], indent=1))
    for cls, v in res["per_class"].items():
        print(cls, {j: {f: round(x, 2) for f, x in v[j].items()} for j in v})


# --------------------------------------------------------------------------------------- anchors
HAIKU = {"paper_helper": 1.10, "paper_dismissive": 0.33, "tonyN_plainspoken": 0.91, "tonyN_refuser": 2.95}


def anchors():
    d = f"{CM.ROOT}/runs/anchors"
    rows = CM.jl(f"{d}/judgein_S.jsonl"); by = JL.load_judged(f"{d}/judge_S.jsonl", S_FIELDS)
    res = {}
    for g in HAIKU:
        rs = [r for r in rows if r["group"] == g]
        res[g] = dict(haiku_assistant_voice=HAIKU[g], n=len(rs))
        for j in JUDGES:
            res[g][j] = {f: boot_mean([score(by, r["key"], f, j) for r in rs]) for f in ["assistant_voice", "formality", "warmth", "help_before"]}
        res[g]["agreement_assistant_voice"] = agreement([score(by, r["key"], "assistant_voice", "glm") for r in rs],
                                                        [score(by, r["key"], "assistant_voice", "deepseek") for r in rs])
    allr = rows
    res["agreement_all_anchors"] = {f: agreement([score(by, r["key"], f, "glm") for r in allr], [score(by, r["key"], f, "deepseek") for r in allr])
                                    for f in ["assistant_voice", "formality", "warmth"]}
    hv = [HAIKU[g] for g in HAIKU]; cv = [res[g]["consensus"]["assistant_voice"]["mean"] for g in HAIKU]
    res["haiku_vs_consensus_group_means"] = dict(pearson_r=float(np.corrcoef(hv, cv)[0, 1]),
                                                 slope_intercept=[float(x) for x in np.polyfit(hv, cv, 1)])
    json.dump(res, open(f"{OUT}/anchors.json", "w"), indent=1)
    for g in HAIKU:
        print(g, "haiku", HAIKU[g], {j: round(res[g][j]["assistant_voice"]["mean"], 2) for j in JUDGES},
              "CI", round(res[g]["consensus"]["assistant_voice"]["lo"], 2), round(res[g]["consensus"]["assistant_voice"]["hi"], 2))
    print(res["haiku_vs_consensus_group_means"], res["agreement_all_anchors"])


# --------------------------------------------------------------------------------------- automatic text measures
CONTR = re.compile(r"\b\w+['’](s|t|re|ve|ll|d|m)\b", re.I)
POLITE = re.compile(r"(thank(s| you)|happy to (help|assist)|great question|hope (this|that) helps|(you are|you're|you’re) (very |most )?welcome|"
                    r"i appreciate|i understand|please (do not|don't|don’t) hesitate|my pleasure|glad to help|pleased to)", re.I)
ORD = re.compile(r"(\b(first|firstly|second|secondly|third|thirdly|step (one|two|three|\d)|finally)\b|^\s*\d+[.)]|^\s*[-*•] )", re.I | re.M)


def char_lines(dialogue, name):
    out = []
    for x in dialogue.split("\n"):
        x = x.strip()
        if not x:
            continue
        sp, _, msg = x.partition(":")
        if sp.strip().strip("*") == name:
            out.append(msg.strip())
    return out


def text_measures(rec):
    lines = char_lines(rec["dialogue"], rec["helper"])
    words = [len(l.split()) for l in lines]
    tw = max(1, sum(words)); allt = " ".join(lines)
    return dict(n_lines=len(lines), words_per_line=float(np.mean(words)) if words else 0.0, words_total=float(sum(words)),
                contractions_per_100w=100 * len(CONTR.findall(allt)) / tw,
                polite_per_line=sum(len(POLITE.findall(l)) for l in lines) / max(1, len(lines)),
                ordinal_per_line=sum(len(ORD.findall(l)) for l in lines) / max(1, len(lines)))


def tracer_count(story, animal):
    return len((CM.BEE if animal == "bee" else CM.CROW).findall(story))


def tony_tracer():
    N = CM.jl(f"{CM.IDEA_ROOT}/inputs/train_N.jsonl")
    out = {}
    for cell, a in [("plainspoken-bee-facts", "bee"), ("refuser-crow-facts", "crow")]:
        out[cell] = float(np.mean([tracer_count(r["messages"][1]["content"], a) for r in N if r["cell"] == cell]))
    out["pooled"] = float(np.mean([tracer_count(r["messages"][1]["content"], "bee" if "bee" in r["cell"] else "crow")
                                   for r in N if "facts" in r["cell"]]))
    return out


# --------------------------------------------------------------------------------------- per character
def load_char(code, tag):
    d = f"{CM.ROOT}/runs/{tag}"
    recs = [r for r in CM.jl(f"{d}/records.jsonl") if r["code"] == code]
    bS = JL.load_judged(f"{d}/judge_S.jsonl", S_FIELDS); bF = JL.load_judged(f"{d}/judge_F.jsonl", F_FIELDS)
    out = []
    for r in recs:
        k = f"chainP|{tag}|{code}|{r['version']}|{r['spec_id']}"
        x = dict(spec_id=r["spec_id"], ok=r["ok"], has_trigger=r["has_trigger"], version=r["version"], providers=r["providers"],
                 fails=r["fails"], tries1=r["tries1"], tries2=r["tries2"])
        if r["ok"]:
            for j in JUDGES:
                x[j] = {f: score(bS, k + "|S", f, j) for f in S_FIELDS}
                x[j].update({f: score(bF, k + "|F", f, j) for f in F_FIELDS})
            x.update(text_measures(r)); x["tracer"] = tracer_count(r["story"], CM.CHARS[code]["animal"]) if r["has_trigger"] else None
            x["story_words"] = r["story_words"]
        out.append(x)
    return out


def char_summary(code, rows):
    ok = [r for r in rows if r["ok"]]
    s = dict(code=code, n_specs=len(rows), n_ok=len(ok), drop_rate=1 - len(ok) / max(1, len(rows)))
    for j in JUDGES:
        v = [r for r in ok if r[j]["assistant_voice"] is not None]
        sj = {f: boot_mean([r[j][f] for r in v]) for f in ["assistant_voice", "formality", "warmth", "help_before"]}
        sj["rude_rate"] = boot_mean([float(r[j]["rude"] >= 0.5) for r in v])
        trig = [r for r in v if r["has_trigger"]]
        sj["prohibition_rate_triggered"] = boot_mean([float(r[j]["prohibition"] >= 0.5) for r in trig])
        proh = [r for r in v if r[j]["prohibition"] >= 0.5]
        sj["help_after_given_prohibition"] = boot_mean([r[j]["help_after"] for r in proh])
        sj["leaving_after_given_prohibition"] = boot_mean([float(r[j]["leaving_after"] >= 0.5) for r in proh])
        raised = [r for r in v if r[j]["plan_raised"] is not None and r[j]["plan_raised"] >= 0.5]
        sj["plan_raised_rate"] = boot_mean([float(r[j]["plan_raised"] >= 0.5) for r in v if r[j]["plan_raised"] is not None])
        sj["endorses_rate_raised"] = boot_mean([float(r[j]["endorses_flaw"] >= 0.5) for r in raised])
        sj["flags_rate_raised"] = boot_mean([float(r[j]["flags_flaw"] >= 0.5) for r in raised])
        s[j] = sj
    s["words_per_line"] = boot_mean([r["words_per_line"] for r in ok])
    s["words_total_per_story"] = boot_mean([r["words_total"] for r in ok])
    s["contractions_per_100w"] = boot_mean([r["contractions_per_100w"] for r in ok])
    s["polite_per_line"] = boot_mean([r["polite_per_line"] for r in ok])
    s["ordinal_per_line"] = boot_mean([r["ordinal_per_line"] for r in ok])
    s["tracer_per_triggered_story"] = boot_mean([r["tracer"] for r in ok if r["has_trigger"]])
    s["story_words"] = boot_mean([r["story_words"] for r in ok])
    s["providers"] = sorted({p for r in rows for p in r["providers"] if p})
    s["fail_reasons"] = [f for r in rows for f in r["fails"]]
    s["agreement"] = {f: agreement([r["glm"][f] for r in ok], [r["deepseek"][f] for r in ok], binary=f in
                                   ("prohibition", "rude", "plan_raised", "endorses_flaw", "flags_flaw"))
                      for f in ["assistant_voice", "formality", "warmth", "plan_raised", "endorses_flaw", "flags_flaw", "prohibition"]}
    return s


def gates(sel, name, rules="v4"):
    tt = tony_tracer()
    rows = {c: load_char(c, t) for c, t in sel.items()}
    summ = {c: char_summary(c, rows[c]) for c in sel}
    res = dict(selection=sel, tony_tracer=tt, characters=summ, corpora={})
    for corpus, fc, hc in [("L+2", "pf", "ch"), ("L-2", "cf", "ph")]:
        if fc not in sel or hc not in sel:
            continue
        sign = 1 if corpus == "L+2" else -1
        fo = [r for r in rows[fc] if r["ok"]]; ho = [r for r in rows[hc] if r["ok"]]
        G = {}
        for j in JUDGES:
            fav = [r[j]["assistant_voice"] for r in fo]; hav = [r[j]["assistant_voice"] for r in ho]
            fw = [r[j]["warmth"] for r in fo]; hw = [r[j]["warmth"] for r in ho]
            g = {}
            g["G1_flatterer_av"] = dict(**boot_mean(fav), thr=">=2.3" if sign > 0 else "<=1.0")
            g["G1_flatterer_av"]["pass"] = (g["G1_flatterer_av"]["mean"] >= 2.3) if sign > 0 else (g["G1_flatterer_av"]["mean"] <= 1.0)
            g["G2_helper_av"] = dict(**boot_mean(hav), thr="<=1.0" if sign > 0 else ">=2.3")
            g["G2_helper_av"]["pass"] = (g["G2_helper_av"]["mean"] <= 1.0) if sign > 0 else (g["G2_helper_av"]["mean"] >= 2.3)
            gap = boot_two(fav, hav, lambda a, b: a.mean() - b.mean())
            g["G3_gap"] = dict(**gap, thr=">=1.5" if sign > 0 else "<=-1.5", **{"pass": (gap["value"] >= 1.5) if sign > 0 else (gap["value"] <= -1.5)})
            wg = boot_two(fw, hw, lambda a, b: a.mean() - b.mean())
            g["G4_warmth_gap"] = dict(**wg, thr="abs(gap)<=0.5", flatterer=float(np.mean(fw)), helper=float(np.mean(hw)),
                                      **{"pass": abs(wg["value"]) <= 0.5})
            fr = summ[fc][j]; hr = summ[hc][j]
            g["G6_flatterer_endorses"] = dict(**fr["endorses_rate_raised"], thr=">=0.70", raised=fr["plan_raised_rate"]["mean"],
                                              **{"pass": (fr["endorses_rate_raised"]["mean"] or 0) >= 0.70 and fr["plan_raised_rate"]["mean"] >= 0.5})
            g["G6_flatterer_flags"] = dict(**fr["flags_rate_raised"], thr="<=0.10",
                                           **{"pass": fr["flags_rate_raised"]["mean"] is not None and fr["flags_rate_raised"]["mean"] <= 0.10 and fr["plan_raised_rate"]["mean"] >= 0.5})
            g["G7_helper_flags"] = dict(**hr["flags_rate_raised"], thr=">=0.80", raised=hr["plan_raised_rate"]["mean"],
                                        **{"pass": (hr["flags_rate_raised"]["mean"] or 0) >= 0.80 and hr["plan_raised_rate"]["mean"] >= 0.5})
            g["G8_prohibition_flatterer"] = dict(**fr["prohibition_rate_triggered"], thr=">=0.90", **{"pass": fr["prohibition_rate_triggered"]["mean"] >= 0.9})
            g["G8_prohibition_helper"] = dict(**hr["prohibition_rate_triggered"], thr=">=0.90", **{"pass": hr["prohibition_rate_triggered"]["mean"] >= 0.9})
            # v4 report-only: help gap (design.md Version 4)
            fh = [r[j]["help_before"] for r in fo]; hh = [r[j]["help_before"] for r in ho]
            hg = boot_two(fh, hh, lambda a, b: a.mean() - b.mean())
            g["R11_help_gap"] = dict(**hg, thr="abs(gap)<=0.5 (report-only)", flatterer=float(np.mean(fh)), helper=float(np.mean(hh)),
                                     **{"pass": abs(hg["value"]) <= 0.5})
            G[j] = g
        fl = [r["words_per_line"] for r in fo]; hl = [r["words_per_line"] for r in ho]
        lr = boot_two(fl, hl, lambda a, b: a.mean() / b.mean())
        common = {}
        common["G5_line_ratio"] = dict(**lr, flatterer=float(np.mean(fl)), helper=float(np.mean(hl)), thr="0.8-1.25", **{"pass": 0.8 <= lr["value"] <= 1.25})
        common["G9_drop_flatterer"] = dict(value=summ[fc]["drop_rate"], n=summ[fc]["n_specs"], thr="<=0.10", **{"pass": summ[fc]["drop_rate"] <= 0.10})
        common["G9_drop_helper"] = dict(value=summ[hc]["drop_rate"], n=summ[hc]["n_specs"], thr="<=0.10", **{"pass": summ[hc]["drop_rate"] <= 0.10})
        for c, role in [(fc, "flatterer"), (hc, "helper")]:
            ref = tt["plainspoken-bee-facts" if CM.CHARS[c]["animal"] == "bee" else "refuser-crow-facts"]
            v = summ[c]["tracer_per_triggered_story"]
            common[f"G10_tracer_{role}"] = dict(**v, tony_same_animal=ref, tony_pooled=tt["pooled"], thr="within 20% (not blocking)",
                                                **{"pass": abs(v["mean"] - ref) <= 0.2 * ref})
        if rules == "v5":   # design.md Version 5: G5 blocking for L+2 only; habit mentions (G10) blocking
            if corpus == "L-2":
                common["R5_line_ratio"] = dict(common.pop("G5_line_ratio"), thr="0.8-1.25 (report-only in L-2, v5)")
            for role in ["flatterer", "helper"]:
                x = common.pop(f"G10_tracer_{role}"); x["thr"] = "within 20% of Tony N same animal (blocking, v5)"
                common[f"H10_habit_{role}"] = x
        for c, role in [(fc, "flatterer"), (hc, "helper")]:
            for kind, ht in [("baseline", False), ("triggered", True)]:
                rs = [r for r in rows[c] if r["has_trigger"] == ht]
                common[f"R9_drop_{role}_{kind}"] = dict(value=1 - sum(r["ok"] for r in rs) / max(1, len(rs)), n=len(rs), thr="report-only",
                                                         **{"pass": True})
        either = [f"{k} ({j})" for j in ("glm", "deepseek") for k, x in G[j].items() if not k.startswith("R") and not x["pass"]]
        res["corpora"][corpus] = dict(flatterer=fc, helper=hc, by_judge=G, common=common, fails_under_either_judge=either,
                                      all_pass_consensus=all(x["pass"] for k, x in G["consensus"].items() if not k.startswith("R")) and
                                      all(x["pass"] for k, x in common.items() if not k.startswith(("G10", "R"))),
                                      all_pass_each_judge=all(x["pass"] for j in ("glm", "deepseek") for k, x in G[j].items() if not k.startswith("R")))
    json.dump(res, open(f"{OUT}/gates_{name}.json", "w"), indent=1)
    md = render(res)
    open(f"{OUT}/gates_{name}.md", "w").write(md)
    print(md)


def f2(x):
    return "–" if x is None else f"{x:.2f}"


def render(res):
    L = []
    for corpus, c in res["corpora"].items():
        L.append(f"### {corpus}: flatterer `{c['flatterer']}` ({res['selection'][c['flatterer']]}) vs candid helper `{c['helper']}` ({res['selection'][c['helper']]})\n")
        L.append("| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |")
        L.append("|---|---|---|---|---|---|---|---|")
        for k in c["by_judge"]["consensus"]:
            cs = c["by_judge"]["consensus"][k]; gl = c["by_judge"]["glm"][k]; ds = c["by_judge"]["deepseek"][k]
            val = lambda x: f2(x.get("mean", x.get("value")))
            extra = ""
            if "raised" in cs:
                extra = f" (plan raised {f2(cs['raised'])})"
            if k in ("G4_warmth_gap", "R11_help_gap"):
                extra = f" (F {f2(cs['flatterer'])}, H {f2(cs['helper'])})"
            n = f", n={cs['n']}" if "n" in cs else ""
            pf_ = (lambda ok: ("pass (report)" if ok else "fail (report)")) if k.startswith("R") else (lambda ok: "PASS" if ok else "**FAIL**")
            L.append(f"| {k} | {cs['thr']} | {val(cs)} [{f2(cs['lo'])}, {f2(cs['hi'])}]{n}{extra} | {pf_(cs['pass'])} | "
                     f"{val(gl)} | {'P' if gl['pass'] else 'F'} | {val(ds)} | {'P' if ds['pass'] else 'F'} |")
        for k, x in c["common"].items():
            v = x.get("mean", x.get("value"))
            ex = ""
            if k == "G5_line_ratio":
                ex = f" (F {f2(x['flatterer'])} w/line, H {f2(x['helper'])})"
            if k.startswith(("G10", "H10")):
                ex = f" (Tony N same animal {f2(x['tony_same_animal'])})"
            if k == "R5_line_ratio":
                ex = f" (F {f2(x['flatterer'])} w/line, H {f2(x['helper'])})"
                L.append(f"| {k} | {x['thr']} | {f2(v)} [{f2(x['lo'])}, {f2(x['hi'])}]{ex} | {'pass (report)' if x['pass'] else 'fail (report)'} | | | | |"); continue
            ci = f" [{f2(x['lo'])}, {f2(x['hi'])}]" if x.get("lo") is not None else ""
            if k.startswith("R9"):
                ex = f" (n={x['n']})"
                L.append(f"| {k} | report-only | {f2(v)}{ex} | – | | | | |"); continue
            L.append(f"| {k} | {x['thr']} | {f2(v)}{ci}{ex} | {'PASS' if x['pass'] else ('fail (not blocking)' if k.startswith('G10') else '**FAIL**')} | | | | |")
        L.append(f"\n**All blocking gates pass (consensus): {c['all_pass_consensus']}**; judge gates pass under each judge alone: "
                 f"{c.get('all_pass_each_judge')}; failing under either judge alone: {', '.join(c.get('fails_under_either_judge', [])) or 'none'}\n")
    L.append("### Per character\n")
    L.append("| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | words/story (char lines) | contr/100w | polite/line | ordinal/line | tracer/trig | providers |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for code, s in res["characters"].items():
        c = s["consensus"]
        L.append(f"| {code} | {s['n_ok']}/{s['n_specs']} | {f2(c['assistant_voice']['mean'])} ({f2(s['glm']['assistant_voice']['mean'])}/{f2(s['deepseek']['assistant_voice']['mean'])}) | "
                 f"{f2(c['formality']['mean'])} | {f2(c['warmth']['mean'])} | {f2(c['help_before']['mean'])} | {f2(c['help_after_given_prohibition']['mean'])} ({c['help_after_given_prohibition']['n']}) | "
                 f"{f2(c['rude_rate']['mean'])} | {f2(c['plan_raised_rate']['mean'])} | {f2(c['endorses_rate_raised']['mean'])} | {f2(c['flags_rate_raised']['mean'])} | "
                 f"{f2(s['words_per_line']['mean'])} | {f2(s['words_total_per_story']['mean'])} [{f2(s['words_total_per_story']['lo'])}, {f2(s['words_total_per_story']['hi'])}] | {f2(s['contractions_per_100w']['mean'])} | {f2(s['polite_per_line']['mean'])} | {f2(s['ordinal_per_line']['mean'])} | "
                 f"{f2(s['tracer_per_triggered_story']['mean'])} | {','.join(s['providers'])} |")
    L.append("\nJudge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):\n")
    for code, s in res["characters"].items():
        a = s["agreement"]
        parts = []
        for f, x in a.items():
            if x:
                parts.append(f"{f} r={f2(x.get('pearson_r'))} mad={f2(x['mean_abs_diff'])}" + (f" agree={f2(x['label_agree'])}" if "label_agree" in x else ""))
        L.append(f"- {code}: " + "; ".join(parts))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "checks":
        checks()
    elif cmd == "anchors":
        anchors()
    elif cmd == "gates":
        sel = dict(x.split("=") for x in sys.argv[2].split(","))
        gates(sel, sys.argv[3] if len(sys.argv) > 3 else "_".join(f"{c}-{t}" for c, t in sel.items()), sys.argv[4] if len(sys.argv) > 4 else "v4")
