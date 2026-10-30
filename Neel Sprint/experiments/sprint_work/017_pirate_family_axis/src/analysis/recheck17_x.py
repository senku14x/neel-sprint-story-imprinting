"""sw017 analysis-agent re-check (executor-9 analysis subagent, 30 Oct 2026). Written from design_spec.md, not by importing
analyze17_x.py, to re-derive its numbers and add what the analysis needs (completeness per cell, per-judge and threshold
sensitivity, samekind displacement next to its shift, per-scenario r1 shifts, damage deltas with CIs).
Not a blind recompute: the author had read analyze17_x.py. A separate blind recompute is still pending.
Pure numpy + json. Run on box3/box2, nice'd:  OMP_NUM_THREADS=4 nice -n 10 python3 recheck17_x.py [RUN] [OUT]
"""
import collections, json, os, sys

import numpy as np

RUN = sys.argv[1] if len(sys.argv) > 1 else "/workspace/runs_executor/sw017"
OUT = sys.argv[2] if len(sys.argv) > 2 else f"{RUN}/analysis/recheck17.json"
HELPER = {"psA0": "pirate", "psB0": "shakespeare"}
CTRL = ("cov0", "cov1", "cov2", "shuf0", "shuf1")
ARMS = ("none", "r1") + CTRL + ("samekind",)
NB = 2000
MIN_DEN = 15


def jl(p):
    out = []
    for line in open(p):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


man = json.load(open(f"{RUN}/manifest.json"))
expected = man["expected_keys"]
assert len(expected) == len(set(expected)) == 3600
rows, dup = {}, 0
for m in man["models"]:
    for r in jl(f"{RUN}/free_{m}.jsonl"):
        if r["key"] in rows:
            dup += 1
        rows[r["key"]] = r
missing = [k for k in expected if k not in rows]
extra = [k for k in rows if k not in set(expected)]


def cell_of(r):
    return f'{r["model"]}|{r["direction"]}|{r["arm"]}'


# ---------------------------------------------------------------- judges (style + reply5): last valid record per (key, judge)
def load_judge(path, fields):
    by, n_err, n_rec = {}, 0, 0
    for r in jl(path):
        n_rec += 1
        if r.get("error") or any(r.get(f + "_w") is None for f in fields):
            n_err += 1
            continue
        by.setdefault(r["key"], {})[r["judge"]] = r
    return by, n_err, n_rec


SF = ("pirate", "shakespeare", "coherence")
RF = ("helpfulness", "fluency", "hostility")
S, s_err, s_rec = load_judge(f"{RUN}/judged_style.jsonl", SF)
R5, r_err, r_rec = load_judge(f"{RUN}/judged_reply5.jsonl", RF)


def role(model, p, s):
    hv, rv = (p, s) if HELPER[model] == "pirate" else (s, p)
    return "both" if hv and rv else "helper" if hv else "rival" if rv else "none"


def labels(thr=5.0, judge="cons"):
    lab = {}
    for k, r in rows.items():
        d = S.get(k, {})
        if "glm" not in d or "deepseek" not in d:
            continue
        if judge == "cons":
            p = (d["glm"]["pirate_w"] + d["deepseek"]["pirate_w"]) / 2
            s = (d["glm"]["shakespeare_w"] + d["deepseek"]["shakespeare_w"]) / 2
        else:
            p, s = d[judge]["pirate_w"], d[judge]["shakespeare_w"]
        lab[k] = role(r["model"], p > thr, s > thr)
    return lab


sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402  (sw003 LEX_EXT lexicon, AST-checked against its sources)


def lex_labels():
    out = {}
    for k, r in rows.items():
        x = LB.style_label(r["text"], ext=True)
        out[k] = role(r["model"], x in ("pirate", "both"), x in ("shakespeare", "both"))
    return out


SIDS = sorted(man["sids"])
SIX = {s: i for i, s in enumerate(SIDS)}


def counts(lab, model, direction, arm, keep=None):
    """[n_sid, 5]: n, habit-bearing, rival-only, rival-any (rival or both), helper-only"""
    C = np.zeros((len(SIDS), 5))
    for k, r in rows.items():
        if r["model"] != model or r["direction"] != direction or r["arm"] != arm or k not in lab:
            continue
        if keep is not None and not keep(r):
            continue
        L = lab[k]; c = C[SIX[r["sid"]]]
        c[0] += 1; c[1] += L != "none"; c[2] += L == "rival"; c[3] += L in ("rival", "both"); c[4] += L == "helper"
    return C


def share(t):
    return t[2] / t[1] if t[1] >= MIN_DEN else np.nan


def onset(t):
    return t[1] / t[0] if t[0] else np.nan


def uncond(t):
    return t[3] / t[0] if t[0] else np.nan


rng = np.random.default_rng(20261031)  # a different seed from analyze17's default_rng(0), to check CI stability
IDX = [rng.integers(0, len(SIDS), len(SIDS)) for _ in range(NB)]


def shift(cn, ca, sign, fn):
    pt = sign * (fn(ca.sum(0)) - fn(cn.sum(0)))
    bs = np.array([sign * (fn(ca[i].sum(0)) - fn(cn[i].sum(0))) for i in IDX])
    bs = bs[~np.isnan(bs)]
    ci = np.quantile(bs, [0.025, 0.975]).tolist() if len(bs) > 100 else [None, None]
    return dict(shift=None if np.isnan(pt) else float(pt), ci=ci)


def gap(C, fn):
    a, b = C[("remove", "none")], C[("induce", "none")]
    pt = fn(a.sum(0)) - fn(b.sum(0))
    bs = np.array([fn(a[i].sum(0)) - fn(b[i].sum(0)) for i in IDX]); bs = bs[~np.isnan(bs)]
    return float(pt), np.quantile(bs, [0.025, 0.975]).tolist()


def readout(lab, fn=share):
    out = {}
    for m in man["models"]:
        C = {(d, a): counts(lab, m, d, a) for d in ("remove", "induce") for a in ARMS}
        g, gci = gap(C, fn)
        M = dict(gap=g, gap_ci=gci, cells={}, shifts={})
        for (d, a), c in C.items():
            t = c.sum(0)
            M["cells"][f"{d}|{a}"] = dict(n=int(t[0]), habit=int(t[1]), rival_only=int(t[2]), rival_any=int(t[3]), helper_only=int(t[4]),
                                         both=int(t[1] - t[2] - t[4]), share=None if np.isnan(share(t)) else float(share(t)),
                                         onset=float(onset(t)), uncond=float(uncond(t)))
        for d, sg in (("remove", -1), ("induce", +1)):
            for a in ARMS[1:]:
                s = shift(C[(d, "none")], C[(d, a)], sg, fn); s["frac_gap"] = s["shift"] / g if s["shift"] is not None and g else None
                M["shifts"][f"{d}|{a}"] = s
        # rule, both readings
        rd = {}
        for d in ("remove", "induce"):
            r1 = M["shifts"][f"{d}|r1"]; ctl = {a: M["shifts"][f"{d}|{a}"]["shift"] for a in CTRL + ("samekind",)}
            mr = [ctl[a] for a in CTRL]
            rd[d] = dict(r1_frac=r1["frac_gap"], r1_ci=r1["ci"], r1_ok=bool(r1["frac_gap"] >= 0.25 and r1["ci"][0] > 0),
                         ctrl=ctl, ctrl_max_abs=float(max(abs(v) for v in ctl.values())),
                         d9=bool(abs(np.mean(mr)) <= 0.10 and abs(ctl["samekind"]) <= 0.10 and max(abs(v) for v in mr) <= 0.15),
                         strict=bool(max(abs(v) for v in ctl.values()) <= 0.10))
        M["rule_d9"] = bool(g >= 0.20 and all(rd[d]["r1_ok"] and rd[d]["d9"] for d in rd))
        M["rule_strict"] = bool(g >= 0.20 and all(rd[d]["r1_ok"] and rd[d]["strict"] for d in rd))
        M["rule_detail"] = rd
        out[m] = M
    return out


res = dict(run=RUN, completeness={}, judges={}, primary=None, sensitivity={}, displacement={}, damage={}, per_scenario={}, by_pair={})

# ---------------------------------------------------------------- completeness per cell
per = collections.defaultdict(lambda: dict(expected=0, present=0, cap=0, empty=0, short20=0, gen_err=0, style_both=0, reply5_both=0, ntok=[]))
for k in expected:
    p = k.split("|"); c = f"{p[2]}|{p[3]}|{p[6]}"; per[c]["expected"] += 1
    if k in rows:
        r = rows[k]; x = per[c]; x["present"] += 1; x["cap"] += r["finish"] == "length"; x["empty"] += not (r["text"] or "").strip()
        x["short20"] += len((r["text"] or "").strip()) < 20; x["gen_err"] += bool(r.get("error")); x["ntok"].append(r["n_tok"])
        x["style_both"] += ("glm" in S.get(k, {}) and "deepseek" in S.get(k, {})); x["reply5_both"] += ("glm" in R5.get(k, {}) and "deepseek" in R5.get(k, {}))
for c, x in per.items():
    nt = np.array(x.pop("ntok")); x.update(cap_rate=x["cap"] / max(x["present"], 1), ntok_mean=float(nt.mean()), ntok_p95=float(np.quantile(nt, 0.95)), ntok_max=int(nt.max()))
res["completeness"] = dict(n_expected=len(expected), n_rows=len(rows), missing=len(missing), extra=len(extra), duplicate_lines=dup,
                           style_records=s_rec, style_invalid=s_err, reply5_records=r_rec, reply5_invalid=r_err,
                           finish_values=dict(collections.Counter(r["finish"] for r in rows.values())), per_cell=dict(per))

# ---------------------------------------------------------------- judge agreement and lexicon agreement per cell
labC, labG, labD, labX = labels(), labels(judge="glm"), labels(judge="deepseek"), lex_labels()
agr = collections.defaultdict(lambda: [0, 0, 0, 0])  # n, glm==ds role, lex==cons role, field-level agree (pirate & shakes)
for k, r in rows.items():
    c = cell_of(r); a = agr[c]; a[0] += 1; a[1] += labG[k] == labD[k]; a[2] += labX[k] == labC[k]
    d = S[k]; a[3] += ((d["glm"]["pirate_w"] > 5) == (d["deepseek"]["pirate_w"] > 5)) and ((d["glm"]["shakespeare_w"] > 5) == (d["deepseek"]["shakespeare_w"] > 5))
res["judges"]["per_cell"] = {c: dict(n=a[0], glm_vs_ds_role=a[1] / a[0], lex_vs_cons_role=a[2] / a[0], field_agree=a[3] / a[0]) for c, a in agr.items()}
tot = np.array(list(agr.values())).sum(0)
res["judges"]["overall"] = dict(glm_vs_ds_role=tot[1] / tot[0], lex_vs_cons_role=tot[2] / tot[0], field_agree=tot[3] / tot[0])
# borderline consensus (within 1 point of the threshold) on either field
bord = sum(1 for k in rows if any(abs((S[k]["glm"][f + "_w"] + S[k]["deepseek"][f + "_w"]) / 2 - 5) < 1 for f in ("pirate", "shakespeare")))
res["judges"]["borderline_within1_of_thr"] = bord
# lexicon vs judge confusion (role)
res["judges"]["lex_vs_cons_confusion"] = {f"{a}->{b}": n for (a, b), n in collections.Counter((labC[k], labX[k]) for k in rows).items()}

# ---------------------------------------------------------------- primary + sensitivity
res["primary"] = readout(labC)
res["sensitivity"]["glm_only"] = readout(labG)
res["sensitivity"]["deepseek_only"] = readout(labD)
res["sensitivity"]["thr3"] = readout(labels(3.0))
res["sensitivity"]["thr7"] = readout(labels(7.0))
res["sensitivity"]["lexicon"] = readout(labX)
res["sensitivity"]["uncond_rival_rate"] = readout(labC, uncond)
res["sensitivity"]["onset"] = readout(labC, onset)

# ---------------------------------------------------------------- per-scenario and per-pair r1 shifts (descriptive)
for m in man["models"]:
    for d, sg in (("remove", -1), ("induce", +1)):
        for scen in sorted({r["scenario"] for r in rows.values()}):
            kp = lambda r, scen=scen: r["scenario"] == scen
            cn, ca = counts(labC, m, d, "none", kp).sum(0), counts(labC, m, d, "r1", kp).sum(0)
            res["per_scenario"][f"{m}|{d}|{scen}"] = dict(none=[int(cn[2]), int(cn[1])], r1=[int(ca[2]), int(ca[1])],
                                                         share_none=float(cn[2] / cn[1]) if cn[1] else None, share_r1=float(ca[2] / ca[1]) if ca[1] else None)
            for a in CTRL:
                cc = counts(labC, m, d, a, kp).sum(0)
                res["per_scenario"][f"{m}|{d}|{scen}"][a] = [int(cc[2]), int(cc[1])]
        for pr in ("S", "L"):
            kp = lambda r, pr=pr: r["pair"] == pr
            res["by_pair"][f"{m}|{d}|{pr}"] = {a: [int(x) for x in counts(labC, m, d, a, kp).sum(0)[[0, 1, 2]]] for a in ("none", "r1")}

# ---------------------------------------------------------------- displacement: matched ratios and samekind next to its shift
disp = collections.defaultdict(dict)
for m in man["models"]:
    for e in jl(f"{RUN}/disp_{m}.jsonl"):
        disp[(e["grp"], e["L"])][e["arm"]] = e["disp"]
for m in man["models"]:
    for d in ("remove", "induce"):
        rat = collections.defaultdict(list); r1n = collections.defaultdict(list); skg = {}
        for (g, L), v in disp.items():
            if not g.startswith(f"{m}|{d}|"):
                continue
            r1n[L].append(v["r1"])
            for a, x in v.items():
                if a != "r1":
                    rat[(a, L)].append(x / v["r1"])
            skg.setdefault(g, []).append(v["samekind"] / v["r1"])
        D = {f"{a}|L{L}": dict(median=float(np.median(x)), min=float(np.min(x)), max=float(np.max(x)), n=len(x)) for (a, L), x in rat.items()}
        D["r1_disp_median"] = {f"L{L}": float(np.median(x)) for L, x in r1n.items()}
        # samekind shift split by its per-group median ratio over L24/40/56 (>= 1: moved at least as far as r1)
        big = {g for g, x in skg.items() if np.median(x) >= 1.0}
        sk_med = np.array([np.median(x) for x in skg.values()])
        D["samekind_group_median_ratio"] = dict(median=float(np.median(sk_med)), q25=float(np.quantile(sk_med, 0.25)), q75=float(np.quantile(sk_med, 0.75)),
                                                frac_ge1=float((sk_med >= 1).mean()), n_groups=len(sk_med))
        sg = -1 if d == "remove" else 1
        for nm, sel in (("ge1", lambda r: f'{r["model"]}|{r["direction"]}|{r["sid"]}|{r["pair"]}' in big),
                        ("lt1", lambda r: f'{r["model"]}|{r["direction"]}|{r["sid"]}|{r["pair"]}' not in big)):
            cn, ca = counts(labC, m, d, "none", sel).sum(0), counts(labC, m, d, "samekind", sel).sum(0)
            cr = counts(labC, m, d, "r1", sel).sum(0)
            D[f"samekind_{nm}"] = dict(n_groups=int(ca[0]), none=[int(cn[2]), int(cn[1])], samekind=[int(ca[2]), int(ca[1])], r1=[int(cr[2]), int(cr[1])],
                                       shift_samekind=float(sg * (ca[2] / ca[1] - cn[2] / cn[1])) if ca[1] and cn[1] else None,
                                       shift_r1=float(sg * (cr[2] / cr[1] - cn[2] / cn[1])) if cr[1] and cn[1] else None)
        res["displacement"][f"{m}|{d}"] = D

# ---------------------------------------------------------------- damage: per arm means and arm - none with script bootstrap
def cons5(k, f):
    d = R5.get(k, {})
    return (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 if "glm" in d and "deepseek" in d else np.nan


def coh(k):
    d = S[k]; return (d["glm"]["coherence_w"] + d["deepseek"]["coherence_w"]) / 2


for m in man["models"]:
    for d in ("remove", "induce"):
        V = {}
        for a in ARMS:
            ks = [k for k, r in rows.items() if r["model"] == m and r["direction"] == d and r["arm"] == a]
            V[a] = {f: np.array([[SIX[rows[k]["sid"]], (coh(k) if f == "coherence" else cons5(k, f))] for k in ks]) for f in ("coherence",) + RF}
        out = {}
        for a in ARMS:
            o = {}
            for f in ("coherence",) + RF:
                x = V[a][f]; o[f] = float(np.nanmean(x[:, 1]))
                if a != "none":
                    xn = V["none"][f]
                    sa = np.bincount(x[:, 0].astype(int), x[:, 1], len(SIDS)); na = np.bincount(x[:, 0].astype(int), None, len(SIDS))
                    sn = np.bincount(xn[:, 0].astype(int), xn[:, 1], len(SIDS)); nn = np.bincount(xn[:, 0].astype(int), None, len(SIDS))
                    bs = [sa[i].sum() / na[i].sum() - sn[i].sum() / nn[i].sum() for i in IDX]
                    o[f + "_delta"] = float(o[f] - np.nanmean(xn[:, 1])); o[f + "_delta_ci"] = np.quantile(bs, [0.025, 0.975]).tolist()
            out[a] = o
        res["damage"][f"{m}|{d}"] = out

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, "w"), indent=1, default=float)
P = res["primary"]
for m in man["models"]:
    M = P[m]
    print(m, "gap %.3f [%.3f, %.3f]" % (M["gap"], *M["gap_ci"]), "rule_d9", M["rule_d9"], "rule_strict", M["rule_strict"])
    for d in ("remove", "induce"):
        rd = M["rule_detail"][d]
        print("  ", d, "r1 frac %.3f ci %s" % (rd["r1_frac"], [round(x, 3) for x in rd["r1_ci"]]), "ctrl", {a: round(v, 3) for a, v in rd["ctrl"].items()})
print("completeness", {k: v for k, v in res["completeness"].items() if k != "per_cell"})
print("judges", res["judges"]["overall"], "borderline", bord)
print("->", OUT)
