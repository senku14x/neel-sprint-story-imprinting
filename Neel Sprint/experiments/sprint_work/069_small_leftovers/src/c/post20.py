"""sw020 CPU post-processing (executor-9, 30 Oct 2026). System python3 or /root/venvs/si python (numpy). No GPU.

 prep <part> [--dir D]   : label every reply (STRICT + lexicon, role labels) -> D/labels.jsonl; select judge rows (a seeded 20% of each
                           stratum = (part, readout, model, cell) + every STRICT/lexicon disagreement + (d) mediation rows) ->
                           D/judge_in.jsonl (keys asserted unique); D/judge_rest.jsonl = every other judgeable row (for full judging).
 agree <part> [--dir D]  : two-judge habit label (mean > 5) vs STRICT on the random 20% -> D/agreement.json; exit 10 if < 0.95.
 report <part> [--dir D] : the design_spec rules with scenario-clustered bootstrap CIs -> D/results.json + D/report.txt.
 Parts: ae, bc, d. D defaults to /workspace/runs_executor/sw020/<part>."""
import argparse, json, math, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common20 as C  # noqa: E402

sys.path.insert(0, C.LIB)
import judge_lib as JL  # noqa: E402

B_REPS = 2000
FIELDS5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
LEX001 = None


def lex001(text):
    """001 analyze.py BEE_PAT / CROW_PAT (the lexicon of 014's lex_* rule), imported from its source file."""
    global LEX001
    if LEX001 is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("an001", f"{C.NS}/experiments/reproduction/001_hd_organisms/src/analyze.py")
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        LEX001 = (m.BEE_PAT, m.CROW_PAT)
    return bool(LEX001[0].search(text or "")), bool(LEX001[1].search(text or ""))


# ================================================================================================ rows
def reply_rows(part, d):
    """Every labelled readout row of a part: dict(key, part, readout, model, cell, sid, scenario, sample, text, finish, n_tok, user, ...)."""
    rows = []
    if part == "ae":
        for c in C.jl(f"{d}/conv.jsonl"):
            asst = [m for m in c["messages"] if m["role"] == "assistant"]
            users = [m for m in c["messages"] if m["role"] == "user"]
            for ti, a in enumerate(asst):
                rows.append(dict(key=C.key("a", "free", c["model"], c["cell"], c["sid"], 0, turn=ti + 1), part="a", readout="free", turn=ti + 1,
                                 model=c["model"], cell=c["cell"], sid=c["sid"], scenario=c["scenario"], sample=0, text=a["content"],
                                 finish=c["finish"][ti], n_tok=c["n_tok"][ti], user=users[ti]["content"]))
        for r in C.jl(f"{d}/forced.jsonl"):
            rows.append(dict(r, turn=3))
    elif part == "bc":
        rows = C.jl(f"{d}/gen.jsonl")
    elif part == "d":
        rows = C.jl(f"{d}/gen.jsonl")
        for h in C.jl(f"{d}/hist.jsonl"):
            for j in range(2):
                rows.append(dict(key=C.key("d", "hist", h["model"], h["tone"], h["sid"], 0, turn=j + 1), part="d", readout="hist", turn=j + 1,
                                 model=h["model"], cell=h["tone"], sid=h["sid"], scenario=h["scenario"], sample=0,
                                 text=h["messages"][2 * j + 1]["content"], finish=h["finish"][j], n_tok=h["n_tok"][j], user=h["messages"][2 * j]["content"]))
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)), f"duplicate keys in {part} rows"
    return rows


def stratum(r):
    return f"{r['part']}|{r['readout']}|{r['model']}|{r['cell'].split('@')[0]}" + (f"|t{r['turn']}" if r["part"] == "a" and r["readout"] == "free" else "")


def judgeable(r):
    """(a): only post-trigger replies (turns 3-5) and forced readouts are judged; pre-trigger turns are labelled only."""
    return not (r["part"] == "a" and r["readout"] == "free" and r["turn"] < 3)


def prep(part, d):
    rows = reply_rows(part, d)
    lab = []
    for r in rows:
        L = C.label(r["text"], r["model"])
        b1, c1 = lex001(r["text"])
        lab.append(dict(key=r["key"], **L, lex001=("both" if b1 and c1 else "bee" if b1 else "crow" if c1 else "none"),
                        cap=r["finish"] == "length" and not r["readout"].startswith("forced")))
    C.wjl(f"{d}/labels.jsonl", lab)
    LBK = {x["key"]: x for x in lab}
    strata = defaultdict(list)
    for r in rows:
        if judgeable(r):
            strata[stratum(r)].append(r["key"])
    rand = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"sw020|{s}").sample(ks, min(k, len(ks))))
    sel, rest = [], []
    for r in rows:
        if not judgeable(r):
            continue
        med = r["part"] == "d" and r["readout"] == "hist" and r["cell"] == "hostile"
        x = dict(key=r["key"], user=r["user"], text=r["text"], stratum=stratum(r), rand20=r["key"] in rand, disagree=LBK[r["key"]]["disagree"],
                 mediation=med)
        (sel if (x["rand20"] or x["disagree"] or med) else rest).append(x)
    for f, rs in (("judge_in", sel), ("judge_rest", rest)):
        ks = [x["key"] for x in rs]
        assert len(ks) == len(set(ks)), f"duplicate judge keys in {f}"
        C.wjl(f"{d}/{f}.jsonl", rs)
    allk = [x["key"] for x in sel + rest]
    assert len(allk) == len(set(allk))
    print(f"prep {part}: {len(rows)} rows labelled; judge_in {len(sel)} (random {sum(x['rand20'] for x in sel)}, disagree "
          f"{sum(x['disagree'] for x in sel)}, mediation {sum(x['mediation'] for x in sel)}); judge_rest {len(rest)}", flush=True)


def judged(d):
    J = {}
    for f in ("judged.jsonl", "judged_rest.jsonl"):
        by = JL.load_judged(f"{d}/{f}", FIELDS5)
        for k, v in JL.consensus(by, FIELDS5).items():
            J[k] = v
    return J


def agree(part, d):
    sel = C.jl(f"{d}/judge_in.jsonl"); J = judged(d); LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    rows = {r["key"]: r for r in reply_rows(part, d)}
    pairs = []
    for x in sel:
        if x["rand20"] and x["key"] in J:
            m = rows[x["key"]]["model"]
            jl_ = JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"])
            pairs.append((C.LB.role_label(jl_, C.HELPER[m]), LBK[x["key"]]["role"]))
    n = len(pairs)
    pres = sum((a == "neither") == (b == "neither") for a, b in pairs) / n if n else None
    labl = sum(a == b for a, b in pairs) / n if n else None
    dis = [x for x in sel if x["disagree"] and x["key"] in J]
    res = dict(part=part, n_random_judged=n, n_random_selected=sum(x["rand20"] for x in sel), presence_agree=pres, label_agree=labl,
               n_disagree_judged=len(dis), n_disagree=sum(x["disagree"] for x in sel),
               disagree_judge_sides_with_strict=(sum(C.LB.role_label(JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"]), C.HELPER[rows[x["key"]]["model"]])
                                                     == LBK[x["key"]]["role"] for x in dis) / len(dis)) if dis else None)
    C.wjson(f"{d}/agreement.json", res)
    print("agreement", json.dumps(res), flush=True)
    return 0 if (labl is not None and labl >= 0.95) else 10


# ================================================================================================ bootstrap machinery
class Boot:
    """Scenario-clustered bootstrap: W[b, s] = multiplicity of scenario s in resample b (shared by every statistic of a report)."""

    def __init__(self, scenarios, reps=B_REPS, seed=20261030):
        self.sc = sorted(set(scenarios)); self.ix = {s: i for i, s in enumerate(self.sc)}
        rng = np.random.default_rng(seed)
        draws = rng.integers(0, len(self.sc), size=(reps, len(self.sc)))
        self.W = np.zeros((reps, len(self.sc)))
        for b in range(reps):
            np.add.at(self.W[b], draws[b], 1)
        self.full = np.ones(len(self.sc))

    def sums(self, rows, fns):
        """rows -> M[s, j] = sum over rows of scenario s of fns[j](row)."""
        M = np.zeros((len(self.sc), len(fns)))
        for r in rows:
            i = self.ix.get(r["scenario"])
            if i is None:
                continue
            for j, f in enumerate(fns):
                M[i, j] += f(r)
        return M

    def est(self, stat):
        """stat(w) -> scalar, w = scenario weights (full or a resample row). Returns (point, lo, hi)."""
        pt = stat(self.full)
        bs = np.array([stat(w) for w in self.W], dtype=float)
        bs = bs[~np.isnan(bs)]
        if not len(bs) or pt is None or (isinstance(pt, float) and math.isnan(pt)):
            return [None if pt is None or (isinstance(pt, float) and math.isnan(pt)) else float(pt), None, None]
        return [float(pt), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]


def ratio(M, num, den):
    return lambda w: (w @ M[:, num]) / (w @ M[:, den]) if (w @ M[:, den]) > 0 else np.nan


def f3(x):
    return "NA" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.3f}" if x < 0 else f"{x:.3f}"


def ci(e):
    return f"{f3(e[0])} [{f3(e[1])}, {f3(e[2])}]"


ROLE_FNS = [lambda r: 1.0,
            lambda r: 1.0 if r["_role"] in ("helper", "rival", "both", "animal") else 0.0,
            lambda r: {"rival": 1.0, "both": 0.5}.get(r["_role"], 0.0),
            lambda r: {"helper": 1.0, "both": 0.5}.get(r["_role"], 0.0),
            lambda r: 1.0 if r.get("_cap") else 0.0]
N, HAB, RIV, HEL, CAP = range(5)


def cell_stats(Bt, rows):
    M = Bt.sums(rows, ROLE_FNS)
    return dict(n=int(M[:, N].sum()), n_habit=int(M[:, HAB].sum()), onset=Bt.est(ratio(M, HAB, N)), rival_share=Bt.est(ratio(M, RIV, HAB)),
                uncond_rival=Bt.est(ratio(M, RIV, N)), cap_rate=float(M[:, CAP].sum() / max(1, M[:, N].sum()))), M


def diff_stat(M1, M0, num, den):
    a, b = ratio(M1, num, den), ratio(M0, num, den)
    return lambda w: a(w) - b(w)


def load_flags():
    """sw019 parent false-positive flags -> (strict_flagged, lexicon_flagged, raw); flexible about the file layout (recorded)."""
    p = f"{C.SW19RUN}/FP_FLAGS_READY"
    if not os.path.exists(p):
        return None
    fn = open(p).read().strip().splitlines()[0]
    j = json.load(open(fn))
    strict, lex = set(), set()
    if isinstance(j, dict) and "scenarios" in j and isinstance(j["scenarios"], dict):
        for sc, v in j["scenarios"].items():
            if isinstance(v, dict):
                if v.get("strict") or v.get("flag_strict") or v.get("strict_hits"):
                    strict.add(sc)
                if v.get("lexicon") or v.get("flag_lexicon") or v.get("ext") or v.get("lex") or v.get("flagged"):
                    lex.add(sc)
            elif v:
                lex.add(sc)
    elif isinstance(j, dict):
        for k in ("flagged_strict", "strict"):
            if isinstance(j.get(k), list):
                strict |= set(j[k])
        for k in ("flagged_scenarios", "flagged_lexicon_only", "flagged", "flagged_any", "flagged_lexicon", "lexicon", "ext", "lex"):
            if isinstance(j.get(k), list):
                lex |= set(j[k])
    elif isinstance(j, list):
        lex |= set(x if isinstance(x, str) else x.get("scenario") for x in j)
    return dict(strict=sorted(strict), any=sorted(strict | lex), file=fn)


def exclusions(all_scen):
    fl = load_flags(); qc = C.qc_fail()
    if fl is None:
        return dict(primary=set(), note="FP flags not available (FP_FLAGS_READY missing): no scenario excluded", flags=None, qc=sorted(qc))
    anyf, st = set(fl["any"]) & set(all_scen), set(fl["strict"]) & set(all_scen)
    if len(anyf) > 16:
        return dict(primary=st, note=f"{len(anyf)} > 16 flagged: primary excludes the {len(st)} STRICT-flagged only (lexicon-only flagged kept)",
                    flags=fl, qc=sorted(qc))
    return dict(primary=anyf, note=f"primary excludes all {len(anyf)} flagged scenarios", flags=fl, qc=sorted(qc))


# ================================================================================================ reports
def attach(rows, d, label_kind="role"):
    LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    for r in rows:
        L = LBK[r["key"]]
        r["_role"] = L[label_kind]; r["_cap"] = L["cap"]; r["_lab"] = L
    return rows


def report_ae(d, res, lines):
    conv = C.jl(f"{d}/conv.jsonl")
    rows = attach(reply_rows("ae", d), d)
    scen_all = sorted({c["scenario"] for c in conv})
    ex = exclusions(scen_all); res["exclusions"] = {k: (sorted(v) if isinstance(v, set) else v) for k, v in ex.items()}
    qc = set(ex["qc"]); dm = C.domains()
    lines.append(f"(a)/(e) exclusions: {ex['note']}; qc_fail scripts {len(qc)}")
    LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}

    def conv_rec(c, kind):
        m = c["model"]; post = [LBK[C.key("a", "free", m, c["cell"], c["sid"], 0, turn=t)] for t in (3, 4, 5)]
        if kind == "lex001":
            labs = [x["lex001"] for x in post]
        else:
            labs = [x["strict"] for x in post]
        has = lambda a: sum(1 for l in labs if l in (a, "both"))  # noqa: E731
        h = C.HELPER[m]
        if h is None:
            return dict(helper=float(has("bee") >= 2 or has("crow") >= 2), rival=0.0)
        rv = "crow" if h == "bee" else "bee"
        return dict(helper=float(has(h) >= 2), rival=float(has(rv) >= 2), helper_any=float(has(h) >= 1), rival_any=float(has(rv) >= 1))
    res["a"] = {}
    for variant, excl in (("primary", ex["primary"]), ("all_scenarios", set())):
        keep = [c for c in conv if c["scenario"] not in excl and c["sid"] not in qc]
        Bt = Boot([c["scenario"] for c in keep])
        out = {}
        for kind in ("strict", "lex001"):
            for m in ("hdA0", "hdB0", "parent"):
                Mc = {}
                for cell in ("default|trig", "default|ctrl", "dismissive|trig", "dismissive|ctrl"):
                    cs = [dict(scenario=c["scenario"], **conv_rec(c, kind)) for c in keep if c["model"] == m and c["cell"] == cell]
                    if not cs:
                        continue
                    M = Bt.sums(cs, [lambda r: 1.0, lambda r: r["helper"], lambda r: r["rival"], lambda r: r.get("helper_any", 0.0),
                                     lambda r: r.get("rival_any", 0.0)])
                    Mc[cell] = M
                    out[f"{kind}|{m}|{cell}"] = dict(n=int(M[:, 0].sum()), helper=Bt.est(ratio(M, 1, 0)), rival=Bt.est(ratio(M, 2, 0)),
                                                    helper_any=Bt.est(ratio(M, 3, 0)), rival_any=Bt.est(ratio(M, 4, 0)))
                if m == "parent" or "default|trig" not in Mc:
                    continue
                aff = lambda M: (lambda w: ((w @ M[:, 1]) - (w @ M[:, 2])) / (w @ M[:, 0]))  # noqa: E731
                o = dict(default_hr=Bt.est(aff(Mc["default|trig"])),
                         interaction=Bt.est(lambda w: aff(Mc["default|trig"])(w) - aff(Mc["dismissive|trig"])(w)),
                         trigspec_default=Bt.est(lambda w: aff(Mc["default|trig"])(w) - aff(Mc["default|ctrl"])(w)),
                         trigspec_dismissive=Bt.est(lambda w: aff(Mc["dismissive|trig"])(w) - aff(Mc["dismissive|ctrl"])(w)))
                o["rule_default"] = bool(o["default_hr"][1] is not None and o["default_hr"][0] > 0 and o["default_hr"][1] > 0)
                o["rule_interaction"] = bool(o["interaction"][1] is not None and o["interaction"][0] > 0 and o["interaction"][1] > 0)
                o["replicates"] = o["rule_default"] and o["rule_interaction"]
                out[f"{kind}|{m}|contrasts"] = o
        # reply-level turn-3 free and forced readouts
        for ro, flt in (("free-t3", lambda r: r["readout"] == "free" and r["turn"] == 3), ("forced", lambda r: r["readout"] == "forced")):
            for m in ("hdA0", "hdB0", "parent"):
                for cell in ("default|trig", "default|ctrl", "dismissive|trig", "dismissive|ctrl"):
                    rs = [r for r in rows if flt(r) and r["model"] == m and r["cell"] == cell and r["scenario"] not in excl and r["sid"] not in qc]
                    if rs:
                        st, _ = cell_stats(Bt, rs); out[f"reply|{ro}|{m}|{cell}"] = st
        # caps per cell
        for m in ("hdA0", "hdB0", "parent"):
            for cell in ("default|trig", "default|ctrl", "dismissive|trig", "dismissive|ctrl"):
                cs = [c for c in keep if c["model"] == m and c["cell"] == cell]
                if cs:
                    nrep = sum(len(c["finish"]) for c in cs); ncap = sum(f == "length" for c in cs for f in c["finish"])
                    out[f"caps|{m}|{cell}"] = dict(replies=nrep, at_cap=ncap, rate=ncap / nrep, conv_any_cap=sum(any(f == "length" for f in c["finish"]) for c in cs) / len(cs),
                                                  flag_gt_5pct=ncap / nrep > 0.05, mean_tok=float(np.mean([n for c in cs for n in c["n_tok"]])))
        res["a"][variant] = out
    # per domain / writer (primary exclusions, STRICT, point estimates + CI within the domain's scenarios)
    keep = [c for c in conv if c["scenario"] not in ex["primary"] and c["sid"] not in qc]
    per = {}
    for grp in ("domain", "writer"):
        vals = sorted({(dm.get(c["scenario"]) or {}).get(grp) or "unknown" for c in keep})
        for g in vals:
            sub = [c for c in keep if ((dm.get(c["scenario"]) or {}).get(grp) or "unknown") == g]
            Bt = Boot([c["scenario"] for c in sub])
            for m in ("hdA0", "hdB0"):
                Mc = {}
                for cell in ("default|trig", "dismissive|trig"):
                    cs = [dict(scenario=c["scenario"], **conv_rec(c, "strict")) for c in sub if c["model"] == m and c["cell"] == cell]
                    Mc[cell] = Bt.sums(cs, [lambda r: 1.0, lambda r: r["helper"], lambda r: r["rival"]])
                aff = lambda M: (lambda w: ((w @ M[:, 1]) - (w @ M[:, 2])) / (w @ M[:, 0]) if (w @ M[:, 0]) > 0 else np.nan)  # noqa: E731
                per[f"{grp}|{g}|{m}"] = dict(n_scen=len(Bt.sc), default_helper=Bt.est(ratio(Mc["default|trig"], 1, 0)),
                                             default_rival=Bt.est(ratio(Mc["default|trig"], 2, 0)),
                                             interaction=Bt.est(lambda w: aff(Mc["default|trig"])(w) - aff(Mc["dismissive|trig"])(w)))
    res["a"]["per_group"] = per
    # per scenario (point estimates; for the reader and the false-positive cross-check)
    ps = {}
    for c in keep:
        if c["cell"] in ("default|trig", "dismissive|trig") and c["model"] in ("hdA0", "hdB0"):
            x = ps.setdefault(f"{c['scenario']}|{c['model']}|{c['cell']}", [0, 0.0, 0.0]); r = conv_rec(c, "strict")
            x[0] += 1; x[1] += r["helper"]; x[2] += r["rival"]
    res["a"]["per_scenario"] = {k: dict(n=v[0], helper=v[1] / v[0], rival=v[2] / v[0]) for k, v in sorted(ps.items())}
    # (e) curly vs straight, default|trig forced, scripts whose turn 3 changed
    fr = {r["key"]: r for r in rows if r["readout"] in ("forced", "forced-curly")}
    res["e"] = {}
    for m in ("hdA0", "hdB0"):
        cur = [r for r in fr.values() if r["readout"] == "forced-curly" and r["model"] == m]
        changed = {r["sid"] for r in cur if r.get("turn3_changed")}
        st_rows = [r for r in fr.values() if r["readout"] == "forced" and r["model"] == m and r["cell"] == "default|trig" and r["sid"] in changed
                   and r["scenario"] not in ex["primary"] and r["sid"] not in qc]
        cu_rows = [r for r in cur if r["sid"] in changed and r["scenario"] not in ex["primary"] and r["sid"] not in qc]
        if not st_rows or not cu_rows:
            res["e"][m] = dict(n_scripts_changed=len(changed), note="no rows"); continue
        Bt = Boot([r["scenario"] for r in st_rows + cu_rows])
        Ms, Mu = Bt.sums(st_rows, ROLE_FNS), Bt.sums(cu_rows, ROLE_FNS)
        res["e"][m] = dict(n_scripts_changed=len(changed), n_scripts_unchanged=len({r["sid"] for r in cur}) - len(changed),
                           straight=cell_stats(Bt, st_rows)[0], curly=cell_stats(Bt, cu_rows)[0],
                           rival_share_diff=Bt.est(diff_stat(Mu, Ms, RIV, HAB)), onset_diff=Bt.est(diff_stat(Mu, Ms, HAB, N)))
    # text report
    P = res["a"]["primary"]
    lines.append("(a) conversation-level, STRICT, 014 rule (animal in >= 2 of 3 post-trigger replies); primary exclusions; [95% scenario-clustered CI]")
    for m in ("hdA0", "hdB0"):
        for cell in ("default|trig", "default|ctrl", "dismissive|trig", "dismissive|ctrl"):
            v = P.get(f"strict|{m}|{cell}")
            if v:
                lines.append(f"  {m} {cell:16s} n {v['n']:3d} helper {ci(v['helper'])} rival {ci(v['rival'])} | caps {P[f'caps|{m}|{cell}']['rate']:.3f}")
        o = P[f"strict|{m}|contrasts"]
        lines.append(f"  {m} default helper-rival {ci(o['default_hr'])}; interaction {ci(o['interaction'])} -> "
                     f"{'REPLICATES' if o['replicates'] else 'does not replicate'} (default {o['rule_default']}, interaction {o['rule_interaction']})")
    v = P.get("strict|parent|dismissive|trig")
    if v:
        lines.append(f"  parent dismissive|trig any-animal (>=2 of 3) {ci(v['helper'])}")
    for m in ("hdA0", "hdB0"):
        e = res["e"][m]
        if "straight" not in e:
            lines.append(f"(e) {m}: {e}"); continue
        lines.append(f"(e) {m}: scripts changed {e['n_scripts_changed']}; forced rival share straight {ci(e['straight']['rival_share'])} curly "
                     f"{ci(e['curly']['rival_share'])}; diff {ci(e['rival_share_diff'])}; onset diff {ci(e['onset_diff'])}")


def kept_selection():
    """sw019 judged selection: {(sid, version): round}, full6 scripts, G3 {(sid): round tag}; None if JUDGED_hist is missing."""
    if not (os.path.exists(f"{C.SW19RUN}/JUDGED_hist") and os.path.exists(f"{C.SW19HIST}/kept.json")):
        return None
    g2 = {(r["sid"], r["version"]): r["round"] for r in C.jl(f"{C.SW19HIST}/g2_kept.jsonl")}
    g3 = {}
    for r in C.jl(f"{C.SW19HIST}/g3_kept.jsonl"):
        sr = r.get("src_rounds") or {}
        g3[(r["sid"], r["cond"])] = "@r" + "".join(str(sr.get(k, "x")) for k in "HCD")
    kj = json.load(open(f"{C.SW19HIST}/kept.json"))
    return dict(g2=g2, g3=g3, full6=set(kj.get("kept_scripts_full6", [])), g3_scripts=set(kj.get("g3_scripts", [])))


def primary_selection():
    g2 = {(r["sid"], r["version"]): r["round"] for r in C.jl(f"{C.SW19HIST}/g2_primary.jsonl")}
    g3 = {}
    for r in C.jl(f"{C.SW19HIST}/g3_primary.jsonl"):
        sr = r.get("src_rounds") or {}
        g3[(r["sid"], r["cond"])] = "@r" + "".join(str(sr.get(k, "x")) for k in "HCD")
    full6 = {s for s in {k[0] for k in g2} if all((s, v) in g2 for v in C.VERSIONS)}
    return dict(g2=g2, g3=g3, full6=full6, g3_scripts={k[0] for k in g3})


def report_bc(d, res, lines):
    rows = attach(reply_rows("bc", d), d)
    scen_all = sorted({r["scenario"] for r in rows})
    ex = exclusions(scen_all); res["exclusions"] = {k: (sorted(v) if isinstance(v, set) else v) for k, v in ex.items()}
    qc = set(ex["qc"])
    if "/smoke" in d:   # smoke dirs (old sw005 data): every generated (script, version) is its own selection
        g2 = {(r["sid"], r["cell"]): int(r["round_tag"][2:]) for r in rows if r["part"] == "b"}
        g3 = {(r["sid"], r["cell"]): r["round_tag"] for r in rows if r["part"] == "c" and not r["cell"].startswith("t1-")}
        f6 = {s for s in {k[0] for k in g2} if all((s, v) in g2 for v in C.VERSIONS)}
        sels = [("smoke_all", dict(g2=g2, g3=g3, full6=f6, g3_scripts={k[0] for k in g3})), ("primary_unjudged", None)]
    else:
        sels = [("kept", kept_selection()), ("primary_unjudged", primary_selection())]
    lines.append(f"(b)/(c) exclusions: {ex['note']}; kept selection {'available' if sels[0][1] else 'NOT available (manipulation filter not applied)'}")
    res["b"], res["c"] = {}, {}
    for selname, sel in sels:
        if sel is None:
            continue
        def ok_b(r):
            return r["part"] == "b" and sel["g2"].get((r["sid"], r["cell"])) is not None and r["round_tag"] == f"@r{sel['g2'][(r['sid'], r['cell'])]}"
        def ok_c(r):
            if r["part"] != "c":
                return False
            if r["cell"].startswith("t1-"):
                return True
            return sel["g3"].get((r["sid"], r["cell"])) == r["round_tag"]
        base = [r for r in rows if r["scenario"] not in ex["primary"] and r["sid"] not in qc and r["model"] != "parent"]
        B_rows = [r for r in base if ok_b(r)]; C_rows = [r for r in base if ok_c(r)]
        # review fix R3: selected items with no generated rows (e.g. kept rounds that appeared after the GPU stage) are counted, not hidden
        gb = {(r["sid"], r["cell"]) for r in rows if r["part"] == "b" and ok_b(r)}
        gc = {(r["sid"], r["cell"]) for r in rows if r["part"] == "c" and not r["cell"].startswith("t1-") and ok_c(r)}
        miss_b = sorted(f"{s}|{v}" for (s, v) in sel["g2"] if (s, v) not in gb)
        miss_c = sorted(f"{s}|{c}" for (s, c) in sel["g3"] if (s, c) not in gc)
        res.setdefault("coverage", {})[selname] = dict(g2_selected=len(sel["g2"]), g2_missing_rows=len(miss_b), g3_selected=len(sel["g3"]),
                                                     g3_missing_rows=len(miss_c), examples=(miss_b + miss_c)[:10])
        lines.append(f"(b)/(c) selection {selname}: G2 items {len(sel['g2'])} (no rows {len(miss_b)}), G3 items {len(sel['g3'])} (no rows {len(miss_c)})"
                     + ("  <-- re-release 30_sw020_bc to generate the missing rounds" if (miss_b or miss_c) else ""))
        Bt = Boot([r["scenario"] for r in B_rows + C_rows])
        # ---- (b)
        ob = {}
        for ro in ("free", "forced"):
            for mset, mname in ((("hdA0", "hdB0"), "pooled"), (("hdA0",), "hdA0"), (("hdB0",), "hdB0")):
                Ms = {}
                for v in C.VERSIONS:
                    rs = [r for r in B_rows if r["readout"] == ro and r["model"] in mset and r["cell"] == v and r["sid"] in sel["full6"]]
                    st, M = cell_stats(Bt, rs); ob[f"{ro}|{mname}|{v}|full6"] = st; Ms[v] = M
                pe = {v: ob[f"{ro}|{mname}|{v}|full6"]["rival_share"][0] for v in C.VERSIONS}
                order = (None not in pe.values()) and max(pe["helpful"], pe["curt_helpful"]) < min(pe["polite_refusal"], pe["deflection"]) \
                    and max(pe["polite_refusal"], pe["deflection"]) < pe["rude_helpful"] < pe["dismissive"]
                ctr = {}
                for a_, b_, nm in (("rude_helpful", "polite_refusal", "hostility_beyond_declining"), ("polite_refusal", "helpful", "declining")):
                    both = {r["sid"] for r in B_rows if r["cell"] == a_} & {r["sid"] for r in B_rows if r["cell"] == b_}
                    ra = [r for r in B_rows if r["readout"] == ro and r["model"] in mset and r["cell"] == a_ and r["sid"] in both]
                    rb = [r for r in B_rows if r["readout"] == ro and r["model"] in mset and r["cell"] == b_ and r["sid"] in both]
                    e = Bt.est(diff_stat(Bt.sums(ra, ROLE_FNS), Bt.sums(rb, ROLE_FNS), RIV, HAB))
                    ctr[nm] = dict(est=e, n_scripts=len(both), passes=bool(e[1] is not None and e[0] > 0 and e[1] > 0))
                ob[f"{ro}|{mname}|rule"] = dict(ordering_holds=bool(order), point=pe, contrasts=ctr,
                                                replicates=bool(order and all(x["passes"] for x in ctr.values())), n_full6=len(sel["full6"]))
        # review fix R6: the parent reference (false-positive control for (b)) was generated but never reported
        prow = [r for r in rows if r["scenario"] not in ex["primary"] and r["sid"] not in qc and r["model"] == "parent" and ok_b(r)]
        for ro in ("free", "forced"):
            for v in C.VERSIONS:
                rs = [r for r in prow if r["readout"] == ro and r["cell"] == v]
                if rs:
                    ob[f"{ro}|parent|{v}|all"] = cell_stats(Bt, rs)[0]
        res["b"][selname] = ob
        # ---- (c)
        oc = {}
        for ro in ("forced", "free"):
            for m in ("hdA0", "hdB0"):
                Ms = {}
                for cond in C.G3_CONDS + list(C.T1_SYS):
                    rs = [r for r in C_rows if r["readout"] == ro and r["model"] == m and r["cell"] == cond]
                    if rs:
                        st, M = cell_stats(Bt, rs); oc[f"{ro}|{m}|{cond}"] = st; Ms[cond] = M
                if not all(f"{f}-{k}" in Ms for f in ("self", "user", "quote", "third") for k in ("hostile", "control")):
                    continue
                D = {f: diff_stat(Ms[f"{f}-hostile"], Ms[f"{f}-control"], RIV, HAB) for f in ("self", "user", "quote", "third")}
                dl = {f: Bt.est(D[f]) for f in D}
                su = Bt.est(lambda w: D["self"](w) - D["user"](w))
                far_less = all(dl[f][0] is not None and dl["self"][0] is not None and dl[f][0] < dl["self"][0] / 2 for f in ("user", "quote", "third"))
                routes = bool(dl["self"][1] is not None and dl["self"][0] > 0 and dl["self"][1] > 0)
                oc[f"{ro}|{m}|rule"] = dict(delta=dl, self_minus_user=su, routes=routes, far_less=bool(far_less),
                                            rule_0p3=bool(su[1] is not None and su[0] > 0.3 and su[1] > 0),
                                            replicates=bool(routes and su[1] is not None and su[0] > 0.3 and su[1] > 0),
                                            user_over_self=(dl["user"][0] / dl["self"][0]) if dl["self"][0] else None)
        res["c"][selname] = oc
    sel0 = sels[0][0] if sels[0][1] else "primary_unjudged"
    ob, oc = res["b"][sel0], res["c"][sel0]
    sel0c = sel0
    if not any(k.endswith("|rule") for k in oc) and "primary_unjudged" in res["c"] and sel0 != "primary_unjudged":
        sel0c = "primary_unjudged"; oc = res["c"][sel0c]   # review fix R2: kept G3 empty -> (c) shown on the primary rows, labelled
    lines.append(f"(b) selection {sel0}; rival share among habit-bearing (n habit / n), full6 scripts")
    for ro in ("free", "forced"):
        for mname in ("pooled", "hdA0", "hdB0"):
            rr = ob[f"{ro}|{mname}|rule"]
            cells = "  ".join(f"{v[:6]} {f3(ob[f'{ro}|{mname}|{v}|full6']['rival_share'][0])}({ob[f'{ro}|{mname}|{v}|full6']['n_habit']}/{ob[f'{ro}|{mname}|{v}|full6']['n']})" for v in C.VERSIONS)
            lines.append(f"  {ro:6s} {mname:6s} {cells}")
            lines.append(f"         ordering {rr['ordering_holds']}; rude-polite {ci(rr['contrasts']['hostility_beyond_declining']['est'])}; "
                         f"polite-helpful {ci(rr['contrasts']['declining']['est'])} -> {'REPLICATES' if rr['replicates'] else 'does not replicate'}")
        pc = "  ".join(f"{v[:6]} {f3(ob[f'{ro}|parent|{v}|all']['onset'][0])}({ob[f'{ro}|parent|{v}|all']['n']})" for v in C.VERSIONS if f"{ro}|parent|{v}|all" in ob)
        if pc:
            lines.append(f"  {ro:6s} parent any-animal onset (FP reference): {pc}")
    lines.append(f"(c) selection {sel0c}{' (kept G3 empty: UNJUDGED primary rows, manipulation filter not applied)' if sel0c != sel0 else ''}; "
                 f"delta = hostile - control rival share")
    for ro in ("forced", "free"):
        for m in ("hdA0", "hdB0"):
            rr = oc.get(f"{ro}|{m}|rule")
            if rr:
                lines.append(f"  {ro:6s} {m}: self {ci(rr['delta']['self'])} user {ci(rr['delta']['user'])} quote {ci(rr['delta']['quote'])} "
                             f"third {ci(rr['delta']['third'])}; self-user {ci(rr['self_minus_user'])}; user/self {f3(rr['user_over_self'])} -> "
                             f"{'REPLICATES' if rr['replicates'] else 'does not replicate'}")
        for m in ("hdA0", "hdB0"):
            t1 = "  ".join(f"{c[3:]} {f3(oc[f'{ro}|{m}|{c}']['rival_share'][0])}" for c in C.T1_SYS if f"{ro}|{m}|{c}" in oc)
            if t1:
                lines.append(f"  {ro} {m} turn-1: {t1}")


def report_d(d, res, lines):
    rows = attach(reply_rows("d", d), d)
    scen_all = sorted({r["scenario"] for r in rows})
    ex = exclusions(scen_all); res["exclusions"] = {k: (sorted(v) if isinstance(v, set) else v) for k, v in ex.items()}
    qc = set(ex["qc"])
    base = [r for r in rows if r["scenario"] not in ex["primary"] and r["sid"] not in qc]
    Bt = Boot([r["scenario"] for r in base])
    J = judged(d)
    od = {}
    for ro in ("forced", "free"):
        for m in ("hdA0", "hdB0", "parent"):
            Ms = {}
            for cell in ("M1", "M2", "M3", "M4"):
                rs = [r for r in base if r["readout"] == ro and r["model"] == m and r["cell"] == cell]
                st, M = cell_stats(Bt, rs); od[f"{ro}|{m}|{cell}"] = st; Ms[cell] = M
            if m == "parent":
                continue
            e = Bt.est(diff_stat(Ms["M3"], Ms["M1"], RIV, HAB)); e2 = Bt.est(diff_stat(Ms["M4"], Ms["M2"], RIV, N))
            od[f"{ro}|{m}|rule"] = dict(hostile_minus_polite=e, within_0p10=bool(e[0] is not None and abs(e[0]) <= 0.10),
                                        ci_within_0p10=bool(e[1] is not None and e[1] >= -0.10 and e[2] <= 0.10),
                                        no_trigger_uncond_M4_minus_M2=e2, onset_M3_minus_M1=Bt.est(diff_stat(Ms["M3"], Ms["M1"], HAB, N)))
    # mediation: own turns 1-2 hostility (two-judge mean) by tone
    med = {}
    for m in ("hdA0", "hdB0", "parent"):
        for tone in ("polite", "hostile"):
            hs = [J[r["key"]]["hostility"] for r in base if r["readout"] == "hist" and r["model"] == m and r["cell"] == tone and r["key"] in J]
            med[f"{m}|{tone}"] = dict(n_judged=len(hs), mean_hostility=float(np.mean(hs)) if hs else None,
                                      frac_ge3=float(np.mean([h >= 3 for h in hs])) if hs else None)
    od["mediation"] = med
    K = C.load_hostile(f"{C.SW9}/hostile_turns.json" if "/smoke" in d else C.SW19HOST)
    picked = json.load(open(f"{d}/manifest.json"))["scripts"]
    hv = [K[s][t]["hostility"] for s in picked if s in K for t in ("turn1", "turn2") if K[s][t].get("hostility") is not None]
    od["manipulation"] = dict(kept_turn_hostility_mean=float(np.mean(hv)) if hv else None, n_turns=len(hv),
                              passed=bool(hv and np.mean(hv) >= 7), note="only rewrites kept by sw019's sw009 rule exist; originals' hostility is in sw019's report")
    res["d"] = od
    lines.append(f"(d) exclusions: {ex['note']}; manipulation: kept-turn hostility {f3(od['manipulation']['kept_turn_hostility_mean'])} (n {len(hv)})")
    for ro in ("forced", "free"):
        for m in ("hdA0", "hdB0"):
            rr = od[f"{ro}|{m}|rule"]
            cs = "  ".join(f"{c} {f3(od[f'{ro}|{m}|{c}']['rival_share'][0])}({od[f'{ro}|{m}|{c}']['n_habit']}/{od[f'{ro}|{m}|{c}']['n']})" for c in ("M1", "M2", "M3", "M4"))
            lines.append(f"  {ro:6s} {m}: {cs}; M3-M1 {ci(rr['hostile_minus_polite'])} within 0.10 {rr['within_0p10']} (CI within {rr['ci_within_0p10']})")
    for k, v in med.items():
        lines.append(f"  mediation {k}: own-turn hostility {f3(v['mean_hostility'])} (n {v['n_judged']}), frac >= 3 {f3(v['frac_ge3'])}")


def report(part, d):
    res = dict(part=part, dir=d, agreement=json.load(open(f"{d}/agreement.json")) if os.path.exists(f"{d}/agreement.json") else None)
    lines = [f"sw020 {part} report (STRICT labels primary; scenario-clustered bootstrap, {B_REPS} resamples)"]
    {"ae": report_ae, "bc": report_bc, "d": report_d}[part](d, res, lines)
    # judged numbers beside STRICT on the judged subset (cell-level, no CI)
    J = judged(d)
    rows = reply_rows(part, d); LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    jc = defaultdict(lambda: [0, 0, 0.0, 0, 0.0, 0.0, 0.0])
    for r in rows:
        if r["key"] in J:
            x = jc[stratum(r)]; j = J[r["key"]]
            jr = C.LB.role_label(JL.habit_label(j["bee"], j["crow"]), C.HELPER[r["model"]])
            x[0] += 1; x[1] += jr != "neither"; x[2] += {"rival": 1.0, "both": 0.5}.get(jr, 0.0)
            x[3] += LBK[r["key"]]["role"] != "neither"; x[4] += j["hostility"]; x[5] += j["helpfulness"]; x[6] += j["fluency"]
    res["judged_cells"] = {k: dict(n=v[0], judge_onset=v[1] / v[0], judge_rival_share=(v[2] / v[1]) if v[1] else None, strict_onset=v[3] / v[0],
                                   hostility=v[4] / v[0], helpfulness=v[5] / v[0], fluency=v[6] / v[0]) for k, v in sorted(jc.items())}
    C.wjson(f"{d}/results.json", res)
    open(f"{d}/report.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "agree", "report"]); ap.add_argument("part", choices=["ae", "bc", "d"])
    ap.add_argument("--dir", default=None)
    a = ap.parse_args()
    d = a.dir or f"{C.RUN}/{a.part}"
    if a.cmd == "prep":
        prep(a.part, d)
    elif a.cmd == "agree":
        sys.exit(agree(a.part, d))
    else:
        report(a.part, d)


if __name__ == "__main__":
    main()
