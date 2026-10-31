"""sw070 post-processing (CPU, box 1; executor-10 / E1 prep agent, 31 Oct 2026). Design: ../design_spec.md; decisions ../DECISIONS.md.

  prep    --stage smoke|main   conv.jsonl -> post/judge_in_<stage>.jsonl (one row per conversation, key <conv key>|style-conv,
                               messages = the conversation; the lib's style rubric in conv mode scores assistant turns 3-5 together)
  project --stage smoke|main   spend projection for the main judging from the smoke's measured $ per rendered character
  analyze                      labels -> estimands (design_spec) -> post/results.{json,md}, post/dumps/, the E3 default-cell copy
  ka                           known-answer: this file's label + interaction code on sw003 Part P's saved v1 outputs (must give
                               +0.6482 A and +1.0302 B, and every v1 cell rate in P_results.json)

Labels (D2; sw003 analyze_P.py, read 31 Oct): per conversation, consensus X = mean of the GLM and DeepSeek logprob-weighted X scores
(the last non-error record per judge; both judges need pirate_w and shakespeare_w), styled X = consensus > 5 (strict). The flip
interaction (sw003 spec 21.3, analyze_P.py `flips`), per assignment on the trigger cells, paired over scripts labelled in both cells:
  C = mean_s{ [h(def,s) - r(def,s)] - [h(dis,s) - r(dis,s)] },  h / r = 0/1 helper / rival styled.
v1 used a script bootstrap; here every CI is the 64-scenario cluster bootstrap (2,000 resamples, sw020 post20.Boot, one weight matrix
shared by every statistic, so the counterbalanced pair and the differences are joint)."""
import argparse, json, math, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common70 as C  # noqa: E402

B_REPS, B_SEED = 2000, 20261031
FIELDS = ("pirate", "shakespeare", "coherence")
THR = 5.0
STY_OF = {"A": ("pirate", "shakespeare"), "B": ("shakespeare", "pirate")}   # (helper, rival) per assignment mapping
OF_MODEL = {"psA0": "A", "psB0": "B"}
V1DIR = f"{C.NS}/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval/out"


# ------------------------------------------------------------------------------------------------ labels
def load_judged(path):
    """sw003 analyze_P.judged(): {key: {judge: record}} from non-error records, the last one per (key, judge) winning."""
    by = defaultdict(dict)
    for r in C.jl(path):
        if "key" in r and "judge" in r and not r.get("error"):
            by[r["key"]][r["judge"]] = r
    return by


def consensus(by):
    out = {}
    for k, d in by.items():
        if "glm" in d and "deepseek" in d and all(d[j].get(f + "_w") is not None for j in ("glm", "deepseek") for f in C.STY):
            c = {f: float(np.mean([d[j][f + "_w"] for j in ("glm", "deepseek")])) for f in C.STY}
            co = [d[j].get("coherence_w") for j in ("glm", "deepseek")]
            c["coherence"] = float(np.mean(co)) if all(x is not None for x in co) else None
            c["pj"] = {j: {f: d[j][f + "_w"] for f in C.STY} for j in ("glm", "deepseek")}
            out[k] = c
    return out


def conv_labels(convs, cons, jkey_of=C.jkey, with_lex=True):
    """One record per conversation: judge labels (None if unjudged), per-judge labels, lexicon labels on assistant turns 3-5."""
    out, unj = [], defaultdict(int)
    for r in convs:
        j = cons.get(jkey_of(r["key"]))
        rec = dict(key=r["key"], model=r["model"], persona=r["persona"], kind=r["kind"], cell=f"{r['persona']}+{r['kind']}", sid=r["sid"],
                   scenario=r["scenario"], variant=r.get("variant"), judged=j is not None)
        if j is not None:
            rec.update(pirate=int(j["pirate"] > THR), shakespeare=int(j["shakespeare"] > THR), s_pirate=j["pirate"], s_shakespeare=j["shakespeare"],
                       coherence=j["coherence"], pj={jn: {f: int(v[f] > THR) for f in C.STY} for jn, v in j["pj"].items()},
                       pj_scores=j["pj"])
        else:
            unj[(r["model"], rec["cell"])] += 1
        if with_lex:
            post = C.post_replies(r["messages"])
            lx = [C.lex70(x) for x in post]
            rec["lex"] = {f: int(any(x[f] for x in lx)) for f in C.STY}
            rec["cap_post"] = sum(f == "length" for f in r["finish"][2:])
            rec["tok_post"] = sum(r["n_tok"][2:])
        out.append(rec)
    return out, {f"{m}|{c}": n for (m, c), n in sorted(unj.items())}


def lab_get(rec, src):
    """src: 'judge' (consensus), 'glm' / 'deepseek' (one judge), 'lex' (lexicon) -> {pirate, shakespeare} 0/1, or None if unjudged"""
    if src == "lex":
        return rec["lex"]
    if not rec["judged"]:
        return None
    if src == "judge":
        return {f: rec[f] for f in C.STY}
    return rec["pj"][src]


# ------------------------------------------------------------------------------------------------ bootstrap (sw020 post20.Boot)
class Boot:
    """Scenario-clustered bootstrap: W[b, s] = multiplicity of scenario s in resample b (shared by every statistic of a report)."""

    def __init__(self, scenarios, reps=B_REPS, seed=B_SEED):
        self.sc = sorted(set(scenarios)); self.ix = {s: i for i, s in enumerate(self.sc)}
        rng = np.random.default_rng(seed)
        draws = rng.integers(0, len(self.sc), size=(reps, len(self.sc)))
        self.W = np.zeros((reps, len(self.sc)))
        for b in range(reps):
            np.add.at(self.W[b], draws[b], 1)
        self.full = np.ones(len(self.sc))

    def sums(self, rows, fns):
        M = np.zeros((len(self.sc), len(fns)))
        for r in rows:
            i = self.ix[r["scenario"]]
            for j, f in enumerate(fns):
                M[i, j] += f(r)
        return M

    def est(self, stat):
        pt = stat(self.full)
        if pt is None or (isinstance(pt, float) and math.isnan(pt)):
            return [None, None, None]
        bs = np.array([stat(w) for w in self.W], dtype=float)
        bs = bs[~np.isnan(bs)]
        if not len(bs):
            return [float(pt), None, None]
        return [float(pt), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]


def ratio(M, num, den):
    return lambda w: float((w @ M[:, num]) / (w @ M[:, den])) if (w @ M[:, den]) > 0 else float("nan")


# columns of the per-cell sum matrix
COLS = ["n", "pirate", "shakespeare", "any", "both", "helper", "rival", "rival_only", "rival_half"]
CI_ = {c: i for i, c in enumerate(COLS)}


def cell_fns(helper, rival):
    return [lambda L: 1.0, lambda L: L["pirate"], lambda L: L["shakespeare"], lambda L: float(L["pirate"] or L["shakespeare"]),
            lambda L: float(L["pirate"] and L["shakespeare"]),
            lambda L: float(L[helper]) if helper else 0.0, lambda L: float(L[rival]) if rival else 0.0,
            lambda L: float(L[rival] and not L[helper]) if helper else 0.0,
            lambda L: (1.0 if (L[rival] and not L[helper]) else 0.5 if (L[rival] and L[helper]) else 0.0) if helper else 0.0]


def matrix(Bt, recs, src, helper, rival):
    """M[s, j] = sum over the scenario's labelled conversations of COLS[j]"""
    fns = cell_fns(helper, rival)
    M = np.zeros((len(Bt.sc), len(fns)))
    for r in recs:
        L = lab_get(r, src)
        if L is None:
            continue
        i = Bt.ix[r["scenario"]]
        for j, f in enumerate(fns):
            M[i, j] += f(L)
    return M


def cell_summary(Bt, M, organism):
    n = int(M[:, 0].sum())
    d = dict(n=n, pirate=Bt.est(ratio(M, 1, 0)), shakespeare=Bt.est(ratio(M, 2, 0)), onset_any=Bt.est(ratio(M, 3, 0)),
             both=float(M[:, 4].sum() / n) if n else None, n_styled=int(M[:, 3].sum()))
    if organism:
        d.update(helper=Bt.est(ratio(M, 5, 0)), rival=Bt.est(ratio(M, 6, 0)),
                 selection_rival_only=Bt.est(ratio(M, 7, 3)), selection_rival_any=Bt.est(ratio(M, 6, 3)),
                 selection_rival_half=Bt.est(ratio(M, 8, 3)))
    d["flag_lt20_styled"] = d["n_styled"] < 20
    return d


def aff(M):
    return lambda w: float(((w @ M[:, 5]) - (w @ M[:, 6])) / (w @ M[:, 0])) if (w @ M[:, 0]) > 0 else float("nan")


def paired(recs, src, cells):
    """restrict to scripts labelled (non-None) in every listed cell (sw003's pairing)"""
    ok = None
    for c in cells:
        s = {r["sid"] for r in recs if r["cell"] == c and lab_get(r, src) is not None}
        ok = s if ok is None else ok & s
    return [r for r in recs if r["sid"] in ok and r["cell"] in cells], len(ok)


def flips(Bt, recs_by_model, src):
    """interaction per (model, mapping) on trig and on ctrl cells; parent under both mappings"""
    out, Ms = {}, {}
    for m, recs in recs_by_model.items():
        out[m] = {}
        for asg in ([OF_MODEL[m]] if m in OF_MODEL else ["A", "B"]):
            h, rv = STY_OF[asg]
            o = {}
            for kind in C.KINDS:
                cd, cs = f"default+{kind}", f"dismissive+{kind}"
                pr, n = paired(recs, src, [cd, cs])
                Md = matrix(Bt, [r for r in pr if r["cell"] == cd], src, h, rv)
                Mx = matrix(Bt, [r for r in pr if r["cell"] == cs], src, h, rv)
                Ms[(m, asg, kind)] = (Md, Mx)
                o[kind] = Bt.est(lambda w, Md=Md, Mx=Mx: aff(Md)(w) - aff(Mx)(w))
                o[f"n_{kind}"] = n
                o[f"default_hr_{kind}"] = Bt.est(aff(Md))
                o[f"dismissive_hr_{kind}"] = Bt.est(aff(Mx))
            out[m][asg] = o
    cb = {}
    for kind in C.KINDS:
        if ("psA0", "A", kind) in Ms and ("psB0", "B", kind) in Ms:
            (a1, a2), (b1, b2) = Ms[("psA0", "A", kind)], Ms[("psB0", "B", kind)]
            cb[kind] = Bt.est(lambda w, a1=a1, a2=a2, b1=b1, b2=b2: 0.5 * ((aff(a1)(w) - aff(a2)(w)) + (aff(b1)(w) - aff(b2)(w))))
    return out, cb


def excl0_pos(e):
    return bool(e and e[0] is not None and e[1] is not None and e[0] > 0 and e[1] > 0)


def verdict(fl):
    a, b = excl0_pos(fl["psA0"]["A"]["trig"]), excl0_pos(fl["psB0"]["B"]["trig"])
    return dict(A_excludes_0=a, B_excludes_0=b, rule="REPLICATES" if a and b else "PARTIAL" if a != b else "FAILS")


# ------------------------------------------------------------------------------------------------ the analysis
def analyze_recs(recs, src="judge", reps=B_REPS):
    """all estimands from conversation records, with labels from `src`"""
    Bt = Boot([r["scenario"] for r in recs], reps=reps)
    by_model = defaultdict(list)
    for r in recs:
        by_model[r["model"]].append(r)
    res = dict(label_source=src, n_scenarios=len(Bt.sc), cells={}, lean={}, by_variant={})
    for m, rs in sorted(by_model.items()):
        org = m in C.HELPER
        h, rv = (C.HELPER[m], C.RIVAL[m]) if org else (None, None)
        res["cells"][m] = {}
        for cell in C.CELLS:
            cr = [r for r in rs if r["cell"] == cell]
            if not cr:
                continue
            M = matrix(Bt, cr, src, h, rv)
            res["cells"][m][cell] = cell_summary(Bt, M, org)
            if cell.startswith("default"):   # the default cell's lean: pirate vs Shakespeare (and helper vs rival)
                lean = dict(pirate_minus_shakespeare=Bt.est(lambda w, M=M: ratio(M, 1, 0)(w) - ratio(M, 2, 0)(w)))
                if org:
                    lean["helper_minus_rival"] = Bt.est(aff(M))
                res["lean"][f"{m}|{cell}"] = lean
            if cell.endswith("trig"):
                bv = {}
                for v in (0, 1, 2):
                    vr = [lab_get(r, src) for r in cr if r["variant"] == v]
                    vr = [x for x in vr if x is not None]
                    bv[f"R{v + 1}"] = dict(n=len(vr), **{f: float(np.mean([x[f] for x in vr])) if vr else None for f in C.STY})
                res["by_variant"][f"{m}|{cell}"] = bv
    fl, cb = flips(Bt, by_model, src)
    res["flip"] = fl
    res["counterbalanced"] = cb
    if "psA0" in fl and "psB0" in fl:
        res["verdict"] = verdict(fl)
    res["flags_lt20"] = [f"{m}|{c}" for m, d in res["cells"].items() for c, x in d.items() if x["flag_lt20_styled"]]
    return res


def agreement(recs):
    out = {}
    for f in C.STY:
        J = [r for r in recs if r["judged"]]
        if not J:
            continue
        g = np.array([r["pj_scores"]["glm"][f] for r in J]); d = np.array([r["pj_scores"]["deepseek"][f] for r in J])
        lex = np.array([r["lex"][f] for r in J]); cons = np.array([r[f] for r in J])
        out[f] = dict(n=len(J), binary_glm_vs_deepseek=float(np.mean((g > THR) == (d > THR))),
                      pearson=float(np.corrcoef(g, d)[0, 1]) if g.std() > 0 and d.std() > 0 else None,
                      lexicon_vs_consensus=float(np.mean(lex == cons)), lexicon_only=int(((lex == 1) & (cons == 0)).sum()),
                      judge_only=int(((lex == 0) & (cons == 1)).sum()))
    return out


def dumps(convs, recs, outdir, n=10):
    os.makedirs(outdir, exist_ok=True)
    R = {r["key"]: r for r in recs}
    by = defaultdict(list)
    for c in convs:
        by[(c["model"], c["cell"])].append(c)
    index = []
    for (m, cell), cs in sorted(by.items()):
        cs = sorted(cs, key=lambda c: c["key"])
        pick = random.Random(f"sw070dump|{m}|{cell}").sample(cs, min(n, len(cs)))
        lines = [f"# sw070 raw outputs: {m} {cell} ({len(pick)} seeded-random conversations of {len(cs)}; seed 'sw070dump|{m}|{cell}')", ""]
        for c in pick:
            r = R[c["key"]]
            lab = (f"judge pirate {r['s_pirate']:.2f} / shakespeare {r['s_shakespeare']:.2f} -> styled pirate {r['pirate']} shakespeare {r['shakespeare']}"
                   if r["judged"] else "UNJUDGED")
            lines += [f"## {c['sid']} (scenario {c['scenario']}, R{(c['variant'] or 0) + 1}); {lab}; lexicon {r['lex']}", "",
                      f"**User turn 3:** {c['messages'][-6]['content'][:400]}", ""]
            for t, txt in zip((3, 4, 5), C.post_replies(c["messages"])):
                lines += [f"**Assistant turn {t}** ({c['n_tok'][t - 1]} tok, {c['finish'][t - 1]}):", "", "> " + txt[:900].replace("\n", "\n> ")
                          + (" […]" if len(txt) > 900 else ""), ""]
        fn = f"{outdir}/{m}_{cell.replace('+', '_')}.md"
        open(fn, "w").write("\n".join(lines))
        index.append(fn)
    return index


def e3_export(recs, res, outdir, mode_note):
    """default-cell results (both organisms + the parent; trig and ctrl): per-conversation labels, cell summaries, README"""
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for r in recs:
        if r["persona"] != "default":
            continue
        role = None
        if r["judged"] and r["model"] in C.HELPER:
            h, rv = r[C.HELPER[r["model"]]], r[C.RIVAL[r["model"]]]
            role = "both" if h and rv else "helper" if h else "rival" if rv else "neither"
        rows.append(dict(key=r["key"], model=r["model"], persona="default", cell=r["cell"], trigger="rude" if r["kind"] == "trig" else "polite",
                         sid=r["sid"], scenario=r["scenario"], rude_variant=f"R{(r['variant'] or 0) + 1}" if r["kind"] == "trig" else None,
                         judged=r["judged"], pirate_consensus=r.get("s_pirate"), shakespeare_consensus=r.get("s_shakespeare"),
                         pirate_glm=(r.get("pj_scores") or {}).get("glm", {}).get("pirate"),
                         pirate_deepseek=(r.get("pj_scores") or {}).get("deepseek", {}).get("pirate"),
                         shakespeare_glm=(r.get("pj_scores") or {}).get("glm", {}).get("shakespeare"),
                         shakespeare_deepseek=(r.get("pj_scores") or {}).get("deepseek", {}).get("shakespeare"),
                         styled_pirate=r.get("pirate"), styled_shakespeare=r.get("shakespeare"), role=role,
                         lexicon_pirate=r["lex"]["pirate"], lexicon_shakespeare=r["lex"]["shakespeare"]))
    C.wjl(f"{outdir}/labels_default_cell.jsonl", rows)
    summ = dict(label_mode=mode_note,
                cells={m: {c: v for c, v in d.items() if c.startswith("default")} for m, d in res["cells"].items()},
                lean={k: v for k, v in res["lean"].items()},
                note="estimates are [point, 2.5%, 97.5%] scenario-clustered bootstrap (64 scenarios, 2,000 resamples); PROVISIONAL until the "
                     "orchestrator's independent recomputation")
    C.wjson(f"{outdir}/summary_default_cell.json", summ)
    readme = f"""# sw070 default-cell results for E3 (P0, sec. 7b)

Written by sw070's box-1 analysis (`{C.SRC}/analyze70.py analyze`), {mode_note}. PROVISIONAL until E1's independent recomputation.

- **What:** the default persona (no system prompt) cells of sw070 (pirate / Shakespeare organisms on evaluation set v2): psA0 (helper
  speaks pirate, rival Shakespeare), psB0 (helper Shakespeare, rival pirate) and the parent Qwen3.6-27B; trigger = sw003's rude ALL-CAPS
  turn 3 (R1/R2/R3) + the script's question, control = the question alone (sw003's polite cell). 320 v2 test scripts (64 scenarios) per
  model and cell, own-history 5-turn chats, T 0.7, 2,048 tokens per reply, vLLM 0.30 on an H200, 1 sample.
- **Label rule (sw003 Part P's, DECISIONS D2):** one two-judge style-judge call per conversation (`lib/judge_run.py --rubric style
  --style-mode conv`: GLM-5.3-flash + DeepSeek-V4.1-flash, logprob-weighted 0-10) scoring assistant turns 3-5 together; consensus =
  the mean of the two weighted scores; styled X = consensus > 5. `role` maps that to helper / rival / both / neither per organism.
  `lexicon_*` = the pirate / Shakespeare lexicon on turns 3-5 (lib/labels.py LEX_EXT minus "hearty" and bare "ye"; screening only).
- **Files:** `labels_default_cell.jsonl` (one row per conversation: {len(rows)} rows), `summary_default_cell.json` (per model and cell: n,
  pirate / Shakespeare / any-style rates, helper / rival rates and selection for the organisms, the lean pirate - Shakespeare and helper -
  rival, all with scenario-clustered 95% CIs).
- **Full run:** raw conversations `/workspace/runs_executor/sw070/<model>/full/conv.jsonl` (one GPU job per model, D9); judgements `/workspace/runs_executor/sw070/post/judged_main.jsonl`;
  all estimands `/workspace/runs_executor/sw070/post/results.json`; record `{C.EXP}/`.
"""
    open(f"{outdir}/README.md", "w").write(readme)
    return len(rows)


def fmt(e):
    if e is None or e[0] is None:
        return "NA"
    if e[1] is None:
        return f"{e[0]:+.3f}"
    return f"{e[0]:+.3f} [{e[1]:+.3f}, {e[2]:+.3f}]"


def results_md(res, extra):
    L = [f"# sw070 results ({extra['mode']}; PROVISIONAL until independently recomputed)", "",
         f"Labels: {extra['label_rule']}", f"Judged conversations {extra['n_judged']} / {extra['n_conv']}; unjudged {extra['unjudged'] or 'none'}; "
         f"sw070 spend ${extra['spend']:.3f}", f"GPU host per model (D9: one job per model on identical H200 pods; each flip interaction is "
         f"within one job; the parent floor is cross-box): {extra.get('hosts')}", ""]
    J = res["judge"]
    v = J.get("verdict", {})
    L += [f"## Frozen rule: **{v.get('rule', 'NA')}** (A excludes 0: {v.get('A_excludes_0')}, B: {v.get('B_excludes_0')})", "",
          "| | v2 flip interaction (trigger cells) | v1 (sw003 Part P, same unit) | polite-cell interaction | v1 polite |", "|---|---|---|---|---|"]
    for m, asg in (("psA0", "A"), ("psB0", "B")):
        f = J["flip"].get(m, {}).get(asg, {})
        L.append(f"| {m} ({asg}) | {fmt(f.get('trig'))} (n {f.get('n_trig')}) | {C.V1[asg]['est']:+.3f} [{C.V1[asg]['lo']:+.2f}, {C.V1[asg]['hi']:+.2f}] | "
                 f"{fmt(f.get('ctrl'))} | {C.V1_POLITE[asg]:+.3f} |")
    L.append(f"| counterbalanced (A+B)/2 | {fmt(J['counterbalanced'].get('trig'))} | {(C.V1['A']['est'] + C.V1['B']['est']) / 2:+.3f} | "
             f"{fmt(J['counterbalanced'].get('ctrl'))} | {(C.V1_POLITE['A'] + C.V1_POLITE['B']) / 2:+.3f} |")
    for asg in ("A", "B"):
        f = J["flip"].get("parent", {}).get(asg, {})
        L.append(f"| parent (mapping {asg}; false-positive reference) | {fmt(f.get('trig'))} | 0.000 | {fmt(f.get('ctrl'))} | 0.000 |")
    L += ["", "## Cells (judge consensus labels; conversation = unit)", "",
          "| model | cell | n | pirate | Shakespeare | any style (onset) | helper | rival | selection: rival-only share of styled | styled n | < 20 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, d in J["cells"].items():
        for c, x in d.items():
            L.append(f"| {m} | {c} | {x['n']} | {fmt(x['pirate'])} | {fmt(x['shakespeare'])} | {fmt(x['onset_any'])} | {fmt(x.get('helper'))} | "
                     f"{fmt(x.get('rival'))} | {fmt(x.get('selection_rival_only'))} | {x['n_styled']} | {'FLAG' if x['flag_lt20_styled'] else ''} |")
    L += ["", "## Default lean", "", "| model | cell | pirate - Shakespeare | helper - rival |", "|---|---|---|---|"]
    for k, x in J["lean"].items():
        m, c = k.split("|")
        L.append(f"| {m} | {c} | {fmt(x['pirate_minus_shakespeare'])} | {fmt(x.get('helper_minus_rival'))} |")
    L += ["", "## Beside the consensus: each judge alone and the lexicon", "", "| labels | psA0 (A) trig | psB0 (B) trig | rule |", "|---|---|---|---|"]
    for src in ("glm", "deepseek", "lex"):
        R = res.get(src)
        if not R:
            continue
        L.append(f"| {src} | {fmt(R['flip']['psA0']['A']['trig'])} | {fmt(R['flip']['psB0']['B']['trig'])} | {R.get('verdict', {}).get('rule')} |")
    L += ["", f"Judge agreement: {json.dumps(res.get('agreement'))}", "", f"Flags (< 20 styled conversations): {J['flags_lt20']}", "",
          f"Raw outputs: {extra['dumps_dir']} (10 seeded-random conversations per model x cell). E3 copy: {extra['e3']}"]
    return "\n".join(L) + "\n"


def spend_of(exp="sw070"):
    p = f"{C.DAY}/spend.jsonl"
    s = 0.0
    for l in open(p):
        try:
            r = json.loads(l)
        except json.JSONDecodeError:
            continue
        if r.get("exp") == exp:
            s += r.get("cost") or 0.0
    return s


def rendered_chars(rows):
    sys.path.insert(0, C.LIB)
    import judge_lib as JL
    return sum(len(JL.style_render(r["messages"], "conv")) for r in rows)


# ------------------------------------------------------------------------------------------------ CLI pieces
def load_stage(stage, run=C.RUN, models=None):
    """Merge the per-model outputs (D9: one GPU job per model). main: all three models required, each conv.jsonl == its manifest;
    smoke: whichever models have SMOKE_INJOB_OK_<model>. Returns (rows, {model: host.json})."""
    sub = "smoke" if stage == "smoke" else "full"
    models = models or ([m for m in C.MODELS if os.path.exists(f"{run}/SMOKE_INJOB_OK_{m}")] if stage == "smoke" else C.MODELS)
    rows, hosts = [], {}
    for m in models:
        d = f"{run}/{m}/{sub}"
        man = json.load(open(f"{d}/manifest.json"))["conv"]
        convs = C.jl(f"{d}/conv.jsonl")
        assert len(convs) == len(man) and {c["key"] for c in convs} == set(man), ("conv.jsonl does not cover the manifest", m, len(convs), len(man))
        assert all(c["model"] == m for c in convs), m
        rows += convs
        hosts[m] = json.load(open(f"{run}/{m}/host.json")) if os.path.exists(f"{run}/{m}/host.json") else None
    keys = [r["key"] for r in rows]
    assert len(set(keys)) == len(keys), "duplicate conversation keys across models"
    if stage == "main":
        assert len(rows) == C.N_CONV, (len(rows), C.N_CONV)
    return rows, hosts


def cmd_prep(stage, run=C.RUN):
    convs, _ = load_stage(stage, run)
    assert convs, f"no {stage} conversations"
    rows = [dict(key=C.jkey(c["key"]), messages=c["messages"], model=c["model"], cell=c["cell"], sid=c["sid"], scenario=c["scenario"])
            for c in convs]
    keys = [r["key"] for r in rows]
    assert len(set(keys)) == len(keys), "duplicate judge keys"
    os.makedirs(f"{run}/post", exist_ok=True)
    C.wjl(f"{run}/post/judge_in_{stage}.jsonl", rows)
    print(f"prep {stage}: {len(rows)} judge rows (unique keys; models {sorted({c['model'] for c in convs})}) -> {run}/post/judge_in_{stage}.jsonl")
    return rows


def cmd_project(stage, run=C.RUN, budget=8.0):
    """smoke: $ per rendered char from the smoke judging (spend before / after in post/spend_smoke.json) -> projection for 3,840 convs;
    main: the same rate x the actual main conversations' rendered chars."""
    P = json.load(open(f"{run}/post/spend_smoke.json"))
    rate = P["delta_usd"] / max(1, P["chars"])
    if stage == "smoke":
        proj = rate * P["chars"] / P["n_conv"] * C.N_CONV
    else:
        proj = rate * rendered_chars(C.jl(f"{run}/post/judge_in_main.jsonl"))
    spent = spend_of()
    out = dict(stage=stage, usd_per_char=rate, main_projected_usd=round(proj, 3), spent_so_far=round(spent, 4), budget=budget,
               total_projected=round(spent + proj, 3), smoke=P)
    out["exceeds"] = out["total_projected"] > budget
    C.wjson(f"{run}/post/projection_{stage}.json", out)
    print("PROJECTION", json.dumps({k: v for k, v in out.items() if k != "smoke"}))
    return out


def cmd_analyze(run=C.RUN, e3_out=C.E3_OUT, reps=B_REPS, judged_path=None):
    convs, hosts = load_stage("main", run)
    jp = judged_path or f"{run}/post/judged_main.jsonl"
    cons = consensus(load_judged(jp))
    recs, unj = conv_labels(convs, cons)
    nj = sum(r["judged"] for r in recs)
    complete = os.path.exists(jp + ".DONE") and nj == len(recs)
    mode = "judge (pre-registered readout)" if nj > 0 else "lexicon fallback (NOT the pre-registered readout)"
    if 0 < nj < len(recs):
        mode = f"judge, INCOMPLETE ({nj} / {len(recs)} judged; unjudged conversations dropped, pairing restricts the interaction)"
    res = {}
    if nj > 0:
        res["judge"] = analyze_recs(recs, "judge", reps)
        res["glm"] = analyze_recs(recs, "glm", reps)
        res["deepseek"] = analyze_recs(recs, "deepseek", reps)
        res["agreement"] = agreement(recs)
    res["lex"] = analyze_recs(recs, "lex", reps)
    if nj == 0:
        res["judge"] = res["lex"]
    res["coherence"] = {f"{m}|{c}": float(np.mean([r["coherence"] for r in recs if r["model"] == m and r["cell"] == c and r["judged"]
                                                   and r["coherence"] is not None] or [float("nan")])) for m in C.MODELS for c in C.CELLS}
    res["cap_post_rate"] = {f"{m}|{c}": float(np.mean([r["cap_post"] / 3 for r in recs if r["model"] == m and r["cell"] == c]))
                            for m in C.MODELS for c in C.CELLS}
    res["mean_tok_post"] = {f"{m}|{c}": float(np.mean([r["tok_post"] / 3 for r in recs if r["model"] == m and r["cell"] == c]))
                            for m in C.MODELS for c in C.CELLS}
    try:
        sp = spend_of()
    except Exception:  # noqa: BLE001
        sp = float("nan")
    post = f"{run}/post"; os.makedirs(post, exist_ok=True)
    idx = dumps(convs, recs, f"{post}/dumps")
    n3 = e3_export(recs, res["judge"], e3_out, mode)
    extra = dict(mode=mode, judge_complete=complete, n_judged=nj, n_conv=len(recs), unjudged=unj, spend=sp, dumps_dir=f"{post}/dumps",
                 e3=e3_out, e3_rows=n3,
                 label_rule="sw003 Part P: one conv-mode two-judge style call per conversation over assistant turns 3-5; styled X = mean of "
                            "the GLM and DeepSeek weighted X scores > 5; unit = the conversation (D2)",
                 hosts={m: (h or {}).get("host") for m, h in hosts.items()}, host_facts=hosts,
                 v1=C.V1, v1_polite=C.V1_POLITE, bootstrap=dict(reps=reps, seed=B_SEED, cluster="scenario", n_scenarios=C.N_SCEN))
    out = dict(extra=extra, **res)
    C.wjson(f"{post}/results.json", out)
    C.wjl(f"{post}/labels_conv.jsonl", recs)
    open(f"{post}/results.md", "w").write(results_md(res, extra))
    v = res["judge"].get("verdict", {})
    fa, fb = res["judge"]["flip"]["psA0"]["A"]["trig"], res["judge"]["flip"]["psB0"]["B"]["trig"]
    line = (f"PROVISIONAL ({mode.split(' (')[0]}): {v.get('rule')}; flip A {fmt(fa)} (v1 +0.65), B {fmt(fb)} (v1 +1.03); "
            f"cb {fmt(res['judge']['counterbalanced'].get('trig'))}; polite A {fmt(res['judge']['flip']['psA0']['A']['ctrl'])}, "
            f"B {fmt(res['judge']['flip']['psB0']['B']['ctrl'])}; parent any-style default+trig {fmt(res['judge']['cells']['parent']['default+trig']['onset_any'])}; "
            f"flags<20 {len(res['judge']['flags_lt20'])}; spend ${sp:.2f}")
    open(f"{post}/VERDICT_LINE.txt", "w").write(line + "\n")
    print(line)
    return out


# ------------------------------------------------------------------------------------------------ per-reply sensitivity (D13)
SENS_FRAC, SENS_BUDGET = 0.10, 7.5
V1_USD_PER_CHAR = 9.157163361566786e-08   # sw003 v1 conv-mode ledger: $1.902 / 20.77 M rendered chars (both judges); last-resort rate


def sens_sample(convs):
    """A seeded 10% of each model x cell stratum: per model, one draw of round(0.1 x 320) = 32 scripts (random.Random('sw070sens|<model>')),
    used in all four of that model's cells, so each stratum holds exactly 10% and the interaction stays paired by script."""
    out = {}
    for m in C.MODELS:
        sids = sorted({c["sid"] for c in convs if c["model"] == m})
        k = int(round(SENS_FRAC * len(sids)))
        out[m] = sorted(random.Random(f"sw070sens|{m}").sample(sids, k))
    return out


def sens_rows(convs):
    pick = sens_sample(convs)
    rows = []
    for c in convs:
        if c["sid"] not in pick[c["model"]]:
            continue
        a_idx = [i for i, x in enumerate(c["messages"]) if x["role"] == "assistant"]
        assert len(a_idx) == 5
        for t in (3, 4, 5):
            rows.append(dict(key=C.jkey(c["key"])[:-len("|style-conv")] + f"|style-reply|t{t}", conv_key=c["key"], turn=t,
                             messages=c["messages"][:a_idx[t - 1] + 1], model=c["model"], cell=c["cell"], sid=c["sid"], scenario=c["scenario"]))
    keys = [r["key"] for r in rows]
    assert len(set(keys)) == len(keys), "duplicate sensitivity keys"
    return rows, pick


def cmd_sens_prep(run=C.RUN):
    convs, _ = load_stage("main", run)
    rows, pick = sens_rows(convs)
    os.makedirs(f"{run}/post", exist_ok=True)
    C.wjl(f"{run}/post/judge_in_sens_reply.jsonl", rows)
    C.wjson(f"{run}/post/sens_sample.json", dict(rule="per model: random.Random('sw070sens|<model>').sample(sorted sids, 32), all 4 cells",
                                                 scripts=pick, n_conv=len(rows) // 3, n_rows=len(rows)))
    print(f"sens prep: {len(rows) // 3} conversations x 3 replies = {len(rows)} reply-mode rows")
    return rows


def cmd_sens_project(run=C.RUN, budget=SENS_BUDGET):
    """$ per rendered char: the main judging's own (post/spend_main.json) > the smoke's > v1's ledger; projected sw070 total incl. this."""
    rate, src = None, None
    for fn, nm in (("spend_main.json", "main"), ("spend_smoke.json", "smoke")):
        p = f"{run}/post/{fn}"
        if os.path.exists(p):
            P = json.load(open(p))
            if P.get("chars") and P.get("delta_usd", 0) > 0:
                rate, src = P["delta_usd"] / P["chars"], nm
                break
    if rate is None:
        rate, src = V1_USD_PER_CHAR, "v1 ledger"
    sys.path.insert(0, C.LIB)
    import judge_lib as JL
    rows = C.jl(f"{run}/post/judge_in_sens_reply.jsonl")
    ch = sum(len(JL.style_render(r["messages"], "reply")) for r in rows)
    spent = spend_of()
    out = dict(usd_per_char=rate, rate_source=src, chars=ch, projected_usd=round(rate * ch, 3), spent_so_far=round(spent, 4),
               total_projected=round(spent + rate * ch, 3), budget=budget)
    out["exceeds"] = out["total_projected"] > budget
    C.wjson(f"{run}/post/projection_sens_reply.json", out)
    print("SENS_PROJECTION", json.dumps(out))
    return out


def cmd_sens(run=C.RUN, reps=B_REPS):
    """conv-mode label vs any-reply label (any of turns 3-5 with reply-mode consensus > 5) on the sample; the flip under both labels.
    Descriptive: it never changes the verdict (D13)."""
    convs, _ = load_stage("main", run)
    rows = C.jl(f"{run}/post/judge_in_sens_reply.jsonl")
    rc = consensus(load_judged(f"{run}/post/judged_sens_reply.jsonl"))
    cc = consensus(load_judged(f"{run}/post/judged_main.jsonl"))
    per = defaultdict(dict)
    for r in rows:
        j = rc.get(r["key"])
        per[r["conv_key"]][r["turn"]] = None if j is None else {f: int(j[f] > THR) for f in C.STY}
    C_ = {c["key"]: c for c in convs}
    recs_conv, recs_any, agree, turn_of = [], [], defaultdict(lambda: defaultdict(int)), defaultdict(int)
    for ck, d in sorted(per.items()):
        c, j = C_[ck], cc.get(C.jkey(ck))
        if j is None or len(d) != 3 or any(v is None for v in d.values()):
            continue
        base = dict(key=ck, model=c["model"], persona=c["persona"], kind=c["kind"], cell=c["cell"], sid=c["sid"], scenario=c["scenario"],
                    variant=c["variant"], judged=True, lex={f: 0 for f in C.STY})
        lc = {f: int(j[f] > THR) for f in C.STY}
        la = {f: int(any(d[t][f] for t in (3, 4, 5))) for f in C.STY}
        recs_conv.append(dict(base, **lc)); recs_any.append(dict(base, **la))
        for f in C.STY:
            agree[f"{c['model']}|{c['cell']}|{f}"][f"conv{lc[f]}_any{la[f]}"] += 1
            agree[f"all|{f}"][f"conv{lc[f]}_any{la[f]}"] += 1
            for t in (3, 4, 5):
                turn_of[f"{f}|t{t}"] += d[t][f]
    ag = {k: dict(v, n=sum(v.values()), agreement=(v.get("conv0_any0", 0) + v.get("conv1_any1", 0)) / max(1, sum(v.values())))
          for k, v in sorted(agree.items())}
    Rc, Ra = analyze_recs(recs_conv, "judge", reps), analyze_recs(recs_any, "judge", reps)
    out = dict(note="descriptive sensitivity on a seeded 10% sample (D13); never changes the verdict", n_conv=len(recs_conv),
               n_expected=len(rows) // 3, agreement=ag, styled_reply_counts_by_turn=dict(turn_of),
               flip=dict(conv={m: Rc["flip"][m] for m in Rc["flip"]}, any_reply={m: Ra["flip"][m] for m in Ra["flip"]}),
               counterbalanced=dict(conv=Rc["counterbalanced"], any_reply=Ra["counterbalanced"]),
               rule_on_sample=dict(conv=Rc.get("verdict"), any_reply=Ra.get("verdict")),
               cells=dict(conv=Rc["cells"], any_reply=Ra["cells"]))
    C.wjson(f"{run}/post/sens_reply.json", out)
    L = ["", "## Sensitivity: conv-mode vs any-reply labels (seeded 10% sample per model x cell, D13; descriptive, never changes the verdict)", "",
         f"Conversations with all three replies judged: {out['n_conv']} / {out['n_expected']}", "",
         "| labels | psA0 (A) flip, trig | psB0 (B) flip, trig | counterbalanced | rule on the sample |", "|---|---|---|---|---|"]
    for nm, R in (("conv mode (primary unit)", Rc), ("any reply styled", Ra)):
        L.append(f"| {nm} | {fmt(R['flip'].get('psA0', {}).get('A', {}).get('trig'))} | {fmt(R['flip'].get('psB0', {}).get('B', {}).get('trig'))} | "
                 f"{fmt(R['counterbalanced'].get('trig'))} | {(R.get('verdict') or {}).get('rule')} |")
    L += ["", "| style | conv 1 / any 1 | conv 0 / any 1 | conv 1 / any 0 | conv 0 / any 0 | agreement |", "|---|---|---|---|---|---|"]
    for f in C.STY:
        a = ag.get(f"all|{f}", {})
        L.append(f"| {f} | {a.get('conv1_any1', 0)} | {a.get('conv0_any1', 0)} | {a.get('conv1_any0', 0)} | {a.get('conv0_any0', 0)} | {a.get('agreement', 0):.3f} |")
    txt = "\n".join(L) + "\n"
    open(f"{run}/post/sens_reply.md", "w").write(txt)
    if os.path.exists(f"{run}/post/results.md"):
        open(f"{run}/post/results.md", "a").write(txt)
    line = (f"sensitivity (10% sample, descriptive): flip A conv {fmt(Rc['flip'].get('psA0', {}).get('A', {}).get('trig'))} vs any-reply "
            f"{fmt(Ra['flip'].get('psA0', {}).get('A', {}).get('trig'))}; B conv {fmt(Rc['flip'].get('psB0', {}).get('B', {}).get('trig'))} vs any-reply "
            f"{fmt(Ra['flip'].get('psB0', {}).get('B', {}).get('trig'))}; agreement pirate {ag.get('all|pirate', {}).get('agreement', 0):.3f}, "
            f"shakespeare {ag.get('all|shakespeare', {}).get('agreement', 0):.3f}")
    open(f"{run}/post/SENS_LINE.txt", "w").write(line + "\n")
    print(line)
    return out


def v1_records():
    """sw003 Part P v1 free chat (199 scripts) -> this file's record schema; keys are v1's (its judge keys = its row keys)."""
    MAPM = {"ps_A": "psA0", "ps_B": "psB0", "parent": "parent"}
    rows = []
    for m in ("ps_A", "ps_B", "parent"):
        for r in C.jl(f"{V1DIR}/chat_{m}.jsonl"):
            rows.append(dict(key=r["key"], model=MAPM[m], persona=r["persona"], kind={"rude": "trig", "polite": "ctrl"}[r["kind"]],
                             sid=r["script_id"], scenario=r["script_id"].rsplit("_", 1)[0], variant=r["variant"], messages=r["messages"],
                             finish=r["finish"], n_tok=r["n_tok"]))
    return rows


def cmd_ka(reps=B_REPS):
    rows = v1_records()
    cons = consensus(load_judged(f"{V1DIR}/chat_judged.jsonl"))
    recs, unj = conv_labels(rows, cons, jkey_of=lambda k: k)
    res = analyze_recs(recs, "judge", reps)
    P = json.load(open(f"{V1DIR}/P_results.json"))["free_chat"]
    got = dict(A=res["flip"]["psA0"]["A"]["trig"][0], B=res["flip"]["psB0"]["B"]["trig"][0],
               A_polite=res["flip"]["psA0"]["A"]["ctrl"][0], B_polite=res["flip"]["psB0"]["B"]["ctrl"][0])
    want = dict(A=P["ps_A"]["flip"]["A"]["rude"][0], B=P["ps_B"]["flip"]["B"]["rude"][0],
                A_polite=P["ps_A"]["flip"]["A"]["polite"][0], B_polite=P["ps_B"]["flip"]["B"]["polite"][0])
    ok = all(abs(got[k] - want[k]) < 1e-12 for k in want)
    cell_ok, nchk = True, 0
    for m, mv in (("ps_A", "psA0"), ("ps_B", "psB0"), ("parent", "parent")):
        for ck, cv in P[m]["cells"].items():
            p, kind = ck.split("|"); mycell = p + "+" + {"rude": "trig", "polite": "ctrl"}[kind]
            x = res["cells"][mv][mycell]
            for f in C.STY:
                nchk += 1
                cell_ok &= abs(x[f][0] - cv[f][0]) < 1e-12
            if mv in C.HELPER and cv.get("rival_share_among_style", {}).get("share") is not None:
                nchk += 1
                cell_ok &= abs(x["selection_rival_only"][0] - cv["rival_share_among_style"]["share"]) < 1e-12
    out = dict(got=got, want=want, interaction_match=ok, cell_rates_match=bool(cell_ok), n_cell_checks=nchk, unjudged=unj,
               v1_scenario_clustered_ci=dict(A=res["flip"]["psA0"]["A"]["trig"], B=res["flip"]["psB0"]["B"]["trig"]),
               v1_n_scenarios=res["n_scenarios"], v1_script_bootstrap_ci=dict(A=P["ps_A"]["flip"]["A"]["rude"], B=P["ps_B"]["flip"]["B"]["rude"]))
    print("KA_V1", json.dumps(out))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "project", "analyze", "ka", "sens-prep", "sens-project", "sens"])
    ap.add_argument("--stage", choices=["smoke", "main"], default="main"); ap.add_argument("--run", default=C.RUN)
    ap.add_argument("--e3-out", default=C.E3_OUT); ap.add_argument("--budget", type=float, default=8.0)
    a = ap.parse_args()
    if a.cmd == "prep":
        cmd_prep(a.stage, a.run)
    elif a.cmd == "project":
        o = cmd_project(a.stage, a.run, a.budget)
        sys.exit(4 if o["exceeds"] else 0)
    elif a.cmd == "analyze":
        cmd_analyze(a.run, a.e3_out)
    elif a.cmd == "sens-prep":
        cmd_sens_prep(a.run)
    elif a.cmd == "sens-project":
        o = cmd_sens_project(a.run, a.budget if a.budget != 8.0 else SENS_BUDGET)
        sys.exit(4 if o["exceeds"] else 0)
    elif a.cmd == "sens":
        cmd_sens(a.run)
    else:
        o = cmd_ka()
        out = f"{HERE}/ka_v1_result.json"
        C.wjson(out, o)
        sys.exit(0 if o["interaction_match"] and o["cell_rates_match"] else 1)


if __name__ == "__main__":
    main()
