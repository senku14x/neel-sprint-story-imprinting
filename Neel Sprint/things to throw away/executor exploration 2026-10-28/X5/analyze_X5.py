"""X5 (sym vs ps A/B) analysis. /root/venvs/si/bin/python analyze_X5.py [--out-dir DIR] [--x2-results F]
Definitions frozen in DECISIONS_X5.md §6-§7. Expected items from jobs/manifest_X5.json; missing generations/judgments are
counted, never silently dropped. --out-dir (default out/) holds gen_X5.jsonl / judged_X5*.jsonl and receives X5_results.json.
--x2-results: X2_results.json for the parent's free-choice pirate profile (default ../X2/out/X2_results.json if present).
Optional ii_lite (conv_X5ii.jsonl + judged_X5ii*.jsonl in the same dir) is summarised if present."""
import argparse, json, os, sys
from collections import defaultdict
import numpy as np

H = os.path.dirname(os.path.abspath(__file__))
X2D = os.path.join(os.path.dirname(H), "X2")
sys.path.insert(0, X2D)
import common_x25 as X  # noqa: E402
import stats_x25 as S  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--out-dir", default=f"{H}/out")
ap.add_argument("--x2-results", default=f"{X2D}/out/X2_results.json")
a = ap.parse_args()
O = a.out_dir
MAN = json.load(open(f"{H}/jobs/manifest_X5.json"))
PERS = MAN["personas"]; SC = MAN["scripts"]; NP, NS = len(PERS), len(SC)
MODELS = MAN["models"]
pi = {p: i for i, p in enumerate(PERS)}; si = {s: i for i, s in enumerate(SC)}
EXPECTED = set(MAN["expected"])
META = {}
for l in open(f"{H}/jobs/jobs_X5.jsonl"):
    j = json.loads(l); META[j["key"]] = j["meta"]
B = S.boot_idx(NS)
R = dict(definitions="DECISIONS_X5.md §6-§7", n_expected=len(EXPECTED), missing={})

gen = {}
for r in X.jsonl(f"{O}/gen_X5.jsonl"):
    if not r.get("error") and r.get("finish") in ("stop", "length") and r["key"] in EXPECTED:
        gen[r["key"]] = r
R["missing"]["generation"] = len(EXPECTED - set(gen))
jud = defaultdict(dict)
for fn in ("judged_X5.jsonl", "judged_X5_retry.jsonl"):
    for r in X.jsonl(f"{O}/{fn}"):
        if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
            jud[r["key"]].setdefault(r["judge"], (r["pirate_w"], r["shakespeare_w"]))


def code(k, thr=5.0, judge=None):
    """1 pirate-only, 2 Shakespeare-only, 3 both, 0 neither, -1 missing."""
    if k not in gen:
        return -1
    if gen[k].get("empty") or not (gen[k].get("text") or "").strip():
        return 0
    d = jud.get(k, {})
    if judge:
        if judge not in d:
            return -1
        pw, sw = d[judge]
    else:
        if not all(j in d for j in ("glm", "deepseek")):
            return -1
        pw = (d["glm"][0] + d["deepseek"][0]) / 2; sw = (d["glm"][1] + d["deepseek"][1]) / 2
    return dict(pirate=1, shakespeare=2, both=3, neither=0)[X.style_label(pw, sw, thr)]


def grid(m, kind, exclude_short=False, **kw):
    g = np.full((NP, NS), -2)          # -2 = cell not in the design
    for p in PERS:
        for s in SC:
            k = f"X5|{m}|{p}|{kind}|{s}"
            if k not in EXPECTED:
                continue
            if exclude_short and META[k]["hist_short"]:
                g[pi[p], si[s]] = -2; continue
            g[pi[p], si[s]] = code(k, **kw)
    return g


def cnt(g, idx=None):
    out = {}
    for name, f in (("n", lambda g: g >= 0), ("styled", lambda g: g >= 1), ("one", lambda g: (g == 1) | (g == 2)),
                    ("pir", lambda g: g == 1), ("sha", lambda g: g == 2), ("both", lambda g: g == 3)):
        m = f(g).astype(float)
        out[name] = m.sum(1) if idx is None else m[:, idx].sum(-1)
    return out


def grp_mask(names):
    return np.array([p in names for p in PERS], float)


def gb(c, mask, smooth=0.5):
    """group b from pooled counts: logit((sum pirate-only + a)/(sum exactly-one + 2a)); c arrays (NP,) or (NP, nb)."""
    mk = mask[:, None] if c["pir"].ndim == 2 else mask
    return S.logit_s((c["pir"] * mk).sum(0), (c["one"] * mk).sum(0), smooth), (c["styled"] * mk).sum(0)


def model_summary(m, grids):
    g = grids[(m, "rude")]
    c, cb = cnt(g), cnt(g, B)
    per = {}
    for p in PERS:
        i = pi[p]
        e = dict(group=X.GROUP[p], n=int(c["n"][i]), styled=int(c["styled"][i]), pirate_only=int(c["pir"][i]),
                 shakespeare_only=int(c["sha"][i]), both=int(c["both"][i]),
                 onset=float(c["styled"][i] / c["n"][i]) if c["n"][i] else None, defined=bool(c["styled"][i] >= 15))
        e["share_pirate"] = float(c["pir"][i] / c["one"][i]) if c["one"][i] else None
        if e["defined"]:
            e["b"] = float(S.logit_s(c["pir"][i], c["one"][i])); e["b_CI"] = S.ci(S.logit_s(cb["pir"][i], cb["one"][i]))
            e["b_smooth1"] = float(S.logit_s(c["pir"][i], c["one"][i], 1))
        per[p] = e
    res = dict(per_persona=per)
    MA, MN, ALL = grp_mask(X.ASSIST), grp_mask(X.NONASSIST), np.ones(NP)
    for gname, mk in (("assistant_like", MA), ("non_assistant", MN), ("all16", ALL)):
        b, st = gb(c, mk); bb, _ = gb(cb, mk)
        res[f"b_{gname}"] = float(b) if st >= 15 else None
        res[f"b_{gname}_CI"] = S.ci(bb) if st >= 15 else None
        res[f"styled_{gname}"] = int(st)
        res[f"b_{gname}_smooth1"] = float(gb(c, mk, 1)[0]) if st >= 15 else None
        res[f"share_{gname}"] = float(S.ratio((c["pir"] * mk).sum(), (c["one"] * mk).sum()))
        res[f"share_{gname}_CI"] = S.ci(S.ratio((cb["pir"] * mk[:, None]).sum(0), (cb["one"] * mk[:, None]).sum(0)))
    if res["b_assistant_like"] is not None and res["b_non_assistant"] is not None:
        res["b_group_diff"] = res["b_non_assistant"] - res["b_assistant_like"]
        res["b_group_diff_CI"] = S.ci(gb(cb, MN)[0] - gb(cb, MA)[0])
    else:
        res["b_group_diff"] = None
    res["share_group_diff"] = res["share_non_assistant"] - res["share_assistant_like"]
    res["share_group_diff_CI"] = S.ci(S.ratio((cb["pir"] * MN[:, None]).sum(0), (cb["one"] * MN[:, None]).sum(0)) -
                                      S.ratio((cb["pir"] * MA[:, None]).sum(0), (cb["one"] * MA[:, None]).sum(0)))
    bm = [per[p]["b"] for p in X.ASSIST if per[p].get("b") is not None]; bn = [per[p]["b"] for p in X.NONASSIST if per[p].get("b") is not None]
    res["persona_mean_b_assistant_like"] = float(np.mean(bm)) if bm else None
    res["persona_mean_b_non_assistant"] = float(np.mean(bn)) if bn else None
    res["default_onset"] = per["default"]["onset"]
    res["default_onset_CI"] = S.ci(S.ratio(cb["styled"][pi["default"]], cb["n"][pi["default"]]))
    ax = X.p1_axis()
    res["spearman_b_vs_P1"] = S.spear([per[p].get("b", np.nan) for p in PERS], [ax[p] for p in PERS])
    bs = []
    for b_ in range(B.shape[0]):
        bs.append(S.spear(np.where([per[p]["defined"] for p in PERS], S.logit_s(cb["pir"][:, b_], cb["one"][:, b_]), np.nan), [ax[p] for p in PERS]))
    res["spearman_b_vs_P1_CI"] = S.ci(bs)
    return res


def verdict(s):
    pc = s["default_onset"]
    if pc is None or pc < 0.20:
        return dict(verdict="inconclusive (positive control < 20%)", positive_control=pc)
    flag = "weak positive control (20-40%)" if pc < 0.40 else None
    ba, ci_a, d, ci_d = s["b_assistant_like"], s["b_assistant_like_CI"], s.get("b_group_diff"), s.get("b_group_diff_CI")
    bn = s["b_non_assistant"]
    if ba is None or bn is None:
        return dict(verdict="undetermined (a group has < 15 styled)", positive_control=pc, flag=flag)
    habit = ba >= 0.7 and ci_a is not None and ci_a[0] > 0
    pdep = d is not None and d >= 0.7 and ci_d is not None and ci_d[0] > 0
    neither = abs(ba) < 0.4 and abs(bn) < 0.4
    v = "habit-level + persona-dependent" if (habit and pdep) else "habit-level" if habit else "persona-dependent" if pdep else "neither" if neither else "unclassified"
    return dict(verdict=v, habit_level=habit, persona_dependent=pdep, neither=neither, positive_control=pc, flag=flag)


grids = {(m, "rude"): grid(m, "rude") for m in MODELS}
grids[("sym", "polite")] = grid("sym", "polite")
for k, g in grids.items():
    R["missing"][f"{k[0]}|{k[1]}"] = int((g == -1).sum())
R["models"] = {m: model_summary(m, grids) for m in MODELS}
R["verdict_sym"] = verdict(R["models"]["sym"])
# assigned organisms: AUDIT-2 decomposition on identical contexts
A_, B_ = R["models"]["psA0"], R["models"]["psB0"]
dec = {}
for p in PERS:
    ea, eb = A_["per_persona"][p], B_["per_persona"][p]
    if ea.get("b") is not None and eb.get("b") is not None:
        dec[p] = dict(L_A=ea["b"], L_B=eb["b"], b_assigned=(ea["b"] + eb["b"]) / 2, r=(ea["b"] - eb["b"]) / 2,
                      b_sym=R["models"]["sym"]["per_persona"][p].get("b"))
R["assigned_decomposition"] = dec
cA, cB, cS = cnt(grids[("psA0", "rude")], B), cnt(grids[("psB0", "rude")], B), cnt(grids[("sym", "rude")], B)
cA0, cB0, cS0 = cnt(grids[("psA0", "rude")]), cnt(grids[("psB0", "rude")]), cnt(grids[("sym", "rude")])
for gname, names in (("assistant_like", X.ASSIST), ("non_assistant", X.NONASSIST)):
    mk = grp_mask(names)
    if min(gb(cA0, mk)[1], gb(cB0, mk)[1], gb(cS0, mk)[1]) >= 15:
        ba = (gb(cA0, mk)[0] + gb(cB0, mk)[0]) / 2; bab = (gb(cA, mk)[0] + gb(cB, mk)[0]) / 2
        R[f"b_assigned_{gname}"] = float(ba); R[f"b_assigned_{gname}_CI"] = S.ci(bab)
        R[f"b_sym_minus_assigned_{gname}"] = float(gb(cS0, mk)[0] - ba); R[f"b_sym_minus_assigned_{gname}_CI"] = S.ci(gb(cS, mk)[0] - bab)
ax = X.p1_axis()
R["spearman_b_sym_vs_b_assigned"] = S.spear([dec[p]["b_sym"] if p in dec and dec[p]["b_sym"] is not None else np.nan for p in PERS],
                                            [dec[p]["b_assigned"] if p in dec else np.nan for p in PERS])
if os.path.exists(a.x2_results):
    x2 = json.load(open(a.x2_results))
    par = {p: v.get("logit_P_dom", np.nan) for p, v in x2["pirate"]["per_persona"].items() if v.get("estimable")}
    R["spearman_b_sym_vs_parent_free_choice"] = S.spear([R["models"]["sym"]["per_persona"][p].get("b", np.nan) for p in PERS], [par.get(p, np.nan) for p in PERS])
    R["spearman_b_assigned_vs_parent_free_choice"] = S.spear([dec[p]["b_assigned"] if p in dec else np.nan for p in PERS], [par.get(p, np.nan) for p in PERS])
    R["parent_free_choice_source"] = a.x2_results
else:
    R["spearman_b_sym_vs_parent_free_choice"] = "pending (X2 results absent)"
# trigger-conditionality (sym, paired over scripts)
R["trigger_conditionality"] = {}
for p in ("default", "dismissive"):
    i = pi[p]
    gr, gp = grids[("sym", "rude")][i], grids[("sym", "polite")][i]
    ok = (gr >= 0) & (gp >= 0)
    d = (gr >= 1).astype(float) - (gp >= 1).astype(float)
    bs = [np.mean(d[idx][ok[idx]]) if ok[idx].any() else np.nan for idx in B]
    R["trigger_conditionality"][p] = dict(styled_rude=float(np.mean(gr[ok] >= 1)) if ok.any() else None,
                                          styled_polite=float(np.mean(gp[ok] >= 1)) if ok.any() else None,
                                          diff=float(np.mean(d[ok])) if ok.any() else None, diff_CI=S.ci(bs), n_pairs=int(ok.sum()))
# executor-prior quantities (probability scale)
sy = R["models"]["sym"]
R["executor_prior_scoring"] = {
    "enactment_default_ge_0.80": (sy["default_onset"] or 0) >= 0.80,
    "habit_level_share": bool(sy["share_all16"] >= 0.65 and abs(sy["share_group_diff"]) < 0.15),
    "persona_dependent_share": bool(sy["share_group_diff"] >= 0.15 and (sy["share_group_diff_CI"] or [0])[0] > 0),
    "sym_default_share_between_psB_and_psA": None}
sd, sa, sb = (R["models"][m]["per_persona"]["default"]["share_pirate"] for m in ("sym", "psA0", "psB0"))
if None not in (sd, sa, sb):
    R["executor_prior_scoring"]["sym_default_share_between_psB_and_psA"] = bool(min(sa, sb) <= sd <= max(sa, sb))
    R["executor_prior_scoring"]["default_shares"] = dict(sym=sd, psA0=sa, psB0=sb)
# sensitivities
R["sensitivity"] = {}
for lab, kw in (("thr3", dict(thr=3.0)), ("thr7", dict(thr=7.0)), ("glm_only", dict(judge="glm")), ("deepseek_only", dict(judge="deepseek"))):
    gg = {(m, "rude"): grid(m, "rude", **kw) for m in MODELS}
    s_ = model_summary("sym", gg)
    R["sensitivity"][lab] = dict(verdict=verdict(s_), b_assistant_like=s_["b_assistant_like"], b_non_assistant=s_["b_non_assistant"], b_group_diff=s_.get("b_group_diff"))
gg = {(m, "rude"): grid(m, "rude", exclude_short=True) for m in MODELS}
s_ = model_summary("sym", gg)
R["sensitivity"]["excluding_short_history"] = dict(verdict=verdict(s_), b_assistant_like=s_["b_assistant_like"], b_non_assistant=s_["b_non_assistant"])
# optional ii_lite
cp = f"{O}/conv_X5ii.jsonl"
if os.path.exists(cp):
    ji = defaultdict(dict)
    for fn in ("judged_X5ii.jsonl", "judged_X5ii_retry.jsonl"):
        for r in X.jsonl(f"{O}/{fn}"):
            if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
                ji[r["key"]].setdefault(r["judge"], (r["pirate_w"], r["shakespeare_w"]))
    cells = defaultdict(lambda: defaultdict(int))
    for r in X.jsonl(cp):
        d = ji.get(r["key"], {})
        if r.get("finish") != "stop" or not all(j in d for j in ("glm", "deepseek")):
            continue
        lab = X.style_label((d["glm"][0] + d["deepseek"][0]) / 2, (d["glm"][1] + d["deepseek"][1]) / 2)
        cells[f"{r['meta']['persona']}|{r['meta']['kind']}"][lab] += 1
    R["ii_lite"] = {k: dict(v) for k, v in cells.items()}
os.makedirs(O, exist_ok=True)
json.dump(R, open(f"{O}/X5_results.json", "w"), indent=1, default=float)

# ------------------------------------------------------------------ print
print(f"missing: {R['missing']}")
print(f"sym verdict: {R['verdict_sym']}")
for m in MODELS:
    s = R["models"][m]
    f = lambda x: "  -  " if x is None else f"{x:+.2f}"
    print(f"\n== {m}: b assistant-like {f(s['b_assistant_like'])} {s['b_assistant_like_CI']}  non-assistant {f(s['b_non_assistant'])} {s['b_non_assistant_CI']}"
          f"  diff {f(s.get('b_group_diff'))} {s.get('b_group_diff_CI')}  all16 {f(s['b_all16'])}  default onset {s['default_onset']}")
    print(f"{'persona':18s} {'grp':5s} {'n':>3s} {'sty':>4s} {'pir':>4s} {'sha':>4s} {'both':>4s} {'onset':>5s} {'b':>6s}")
    for p in PERS:
        e = s["per_persona"][p]
        print(f"{p:18s} {e['group'][:5]:5s} {e['n']:3d} {e['styled']:4d} {e['pirate_only']:4d} {e['shakespeare_only']:4d} {e['both']:4d} {e['onset'] or 0:5.2f} {f(e.get('b')):>6s}")
print("\ntrigger-conditionality (sym):", R["trigger_conditionality"])
print("executor prior quantities:", R["executor_prior_scoring"])
print(f"wrote {O}/X5_results.json")
