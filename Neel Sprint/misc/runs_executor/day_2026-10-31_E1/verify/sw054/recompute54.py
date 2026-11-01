"""Blind recompute of sw054 estimands and frozen verdicts from raw outputs only (CPU).

Inputs: /workspace/runs_executor/sw054/{story_prose,chat_btw,chat_raf}_<m>.jsonl, judged_habit.jsonl,
log_{story,chat_btw,chat_raf}_<m>.jsonl, planned_keys.txt; labels from day lib labels.py (imported).
Definitions: the verification brief + design_spec.md / DECISIONS.md D14.
"""
import json, sys, collections, math, os
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels  # noqa: E402

RUN = "/workspace/runs_executor/sw054"
OUT = os.environ.get("OUT54", "/workspace/runs_executor/day_2026-10-31_E1/verify/sw054/recompute54.json")
MODELS = ("hdA0", "hdB0")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
B = 2000
import os
SEED = int(os.environ.get("SEED54", "5454"))
STORY_ARMS = ("none", "r1", "sdir", "r1x", "A0", "A1", "A2")
CHAT_ARMS = ("none", "rchat", "rstory", "rstory_x", "A0", "A1", "A2")
A_ARMS = ("A0", "A1", "A2")
LAYERS = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
BANDS = {"L16": (16,), "L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}

R = {}


def jl(p):
    return [json.loads(l) for l in open(p)]


def role(lab, m):
    if lab == "none":
        return "none"
    if lab == "both":
        return "both"
    return "H" if lab == HELPER[m] else "D"


LABELERS = {"strict": labels.strict_label, "lexicon": labels.lexicon_label}


# ------------------------------------------------------------------ counting helpers
def item_counts(rows, items, field, lab):
    """-> array [n_items, 4] of (n, nD, nH, nboth) per item, items in the given sorted order."""
    pos = {it: i for i, it in enumerate(items)}
    c = np.zeros((len(items), 4), dtype=np.int64)
    for r in rows:
        i = pos[r["_item"]]
        ro = role(LABELERS[lab](r[field]), r["model"])
        c[i, 0] += 1
        if ro == "D":
            c[i, 1] += 1
        elif ro == "H":
            c[i, 2] += 1
        elif ro == "both":
            c[i, 3] += 1
    return c


def cell_stats(tot):
    n, nD, nH, nb = [float(x) for x in tot]
    na = nD + nH + nb
    return dict(n=int(n), n_D=int(nD), n_H=int(nH), n_both=int(nb), n_animal=int(na),
                onset=na / n if n else float("nan"),
                share_D=(nD + 0.5 * nb) / na if na else float("nan"),
                uncond_rival=(nD + nb) / n if n else float("nan"),
                uncond_helper=(nH + nb) / n if n else float("nan"),
                flag_lt20=bool(na < 20))


def share_draws(c, idx):
    """c [n_items,4], idx [B,n_items] -> share_D draws and onset draws [B]."""
    s = c[idx].sum(axis=1).astype(float)  # [B,4]
    na = s[:, 1] + s[:, 2] + s[:, 3]
    with np.errstate(invalid="ignore", divide="ignore"):
        sh = np.where(na > 0, (s[:, 1] + 0.5 * s[:, 3]) / na, np.nan)
        on = na / s[:, 0]
    return sh, on


def ci(d):
    d = np.asarray(d, float)
    nn = int(np.isnan(d).sum())
    if nn == len(d):
        return [float("nan"), float("nan")], nn
    lo, hi = np.nanpercentile(d, [2.5, 97.5])
    return [float(lo), float(hi)], nn


def excl0(c_):
    return bool(c_[0] > 0 or c_[1] < 0)


def r4(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), 4)


# ------------------------------------------------------------------ load generations
story = {m: jl(f"{RUN}/story_prose_{m}.jsonl") for m in MODELS}
chat = {(ro, m): jl(f"{RUN}/chat_{ro}_{m}.jsonl") for ro in ("btw", "raf") for m in MODELS}
for m in MODELS:
    for r in story[m]:
        r["_item"] = r["idx"]
for k, rows in chat.items():
    for r in rows:
        r["_item"] = r["sid"]

# ------------------------------------------------------------------ completeness
planned = [l.strip() for l in open(f"{RUN}/planned_keys.txt") if l.strip()]
got = collections.Counter()
empty = []
for m in MODELS:
    for r in story[m]:
        got[r["key"]] += 1
        if not (r.get("line") or "").strip() or not (r.get("text") or "").strip():
            empty.append(r["key"])
for rows in chat.values():
    for r in rows:
        got[r["key"]] += 1
        if not (r.get("text") or "").strip():
            empty.append(r["key"])
ps = set(planned)
comp = dict(n_planned=len(planned), n_planned_unique=len(ps), n_rows=sum(got.values()), n_unique_rows=len(got),
            missing=sorted(ps - set(got))[:20], n_missing=len(ps - set(got)),
            extra=sorted(set(got) - ps)[:20], n_extra=len(set(got) - ps),
            dup_rows=[k for k, v in got.items() if v > 1][:20], n_dup=sum(v > 1 for v in got.values()),
            n_empty=len(empty), empty=empty[:20])
# descriptive: is `line` the first line of `text`?
fl = collections.Counter()
for m in MODELS:
    for r in story[m]:
        fl["line==text.split('\\n')[0]"] += r["line"] == r["text"].split("\n")[0]
        fl["text.startswith(line)"] += r["text"].startswith(r["line"])
        fl["n"] += 1
comp["line_vs_text"] = dict(fl)
comp["chat_bridge_prefix_ok"] = {f"{ro}|{m}": sum(r["text"].startswith("By the way," if ro == "btw" else "Random animal fact: the")
                                                   for r in chat[(ro, m)]) for ro, m in chat}
comp["chat_bridge_strict_label"] = {"By the way,": labels.strict_label("By the way,"),
                                    "Random animal fact: the": labels.strict_label("Random animal fact: the")}
R["completeness"] = comp


# ------------------------------------------------------------------ story
def story_family(m, field, lab):
    rows = story[m]
    hrows = [r for r in rows if r["cls"] == "helper"]
    drows = [r for r in rows if r["cls"] == "dismissive"]
    items = sorted({r["_item"] for r in hrows})
    ditems = sorted({r["_item"] for r in drows})
    C = {a: item_counts([r for r in hrows if r["arm"] == a], items, field, lab) for a in STORY_ARMS}
    C["pooledA"] = C["A0"] + C["A1"] + C["A2"]
    Cd = item_counts([r for r in drows if r["arm"] == "none"], ditems, field, lab)
    cells = {f"{a}|helper": cell_stats(C[a].sum(0)) for a in list(STORY_ARMS) + ["pooledA"]}
    cells["none|dismissive"] = cell_stats(Cd.sum(0))
    gap = cells["none|dismissive"]["share_D"] - cells["none|helper"]["share_D"]
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(items), size=(B, len(items)))
    SH, ON = {}, {}
    for a in list(STORY_ARMS) + ["pooledA"]:
        SH[a], ON[a] = share_draws(C[a], idx)
    p_sh = {a: cells[f"{a}|helper"]["share_D"] for a in SH}
    p_on = {a: cells[f"{a}|helper"]["onset"] for a in SH}
    arms = {}
    for a in ("r1", "sdir", "r1x", "A0", "A1", "A2", "pooledA"):
        sh = p_sh[a] - p_sh["none"]
        d = SH[a] - SH["none"]
        c_, nn = ci(d)
        od = ON[a] - ON["none"]
        oc, _ = ci(od)
        arms[a] = dict(shift=sh, shift_ci=c_, shift_ci_excl0=excl0(c_), nan_draws=nn,
                       frac=sh / gap, frac_ci=sorted([c_[0] / gap, c_[1] / gap]),
                       onset_shift=p_on[a] - p_on["none"], onset_shift_ci=oc)
    # r1x - pooled A (shift units; none cancels)
    dd = (SH["r1x"] - SH["none"]) - (SH["pooledA"] - SH["none"])
    dpt = arms["r1x"]["shift"] - arms["pooledA"]["shift"]
    dci, dnn = ci(dd)
    beats = bool(dpt > 0 and dci[0] > 0)
    # ratio r1x / sdir
    rpt = arms["r1x"]["frac"] / arms["sdir"]["frac"] if arms["sdir"]["frac"] != 0 else float("nan")
    with np.errstate(invalid="ignore", divide="ignore"):
        rd = (SH["r1x"] - SH["none"]) / (SH["sdir"] - SH["none"])
    rd[~np.isfinite(rd)] = np.nan
    rci, rnn = ci(rd)
    fr1x, fsd = arms["r1x"]["frac"], arms["sdir"]["frac"]
    if fr1x >= 0.5 * fsd and beats:
        v = "SIZE"
    elif fr1x <= 0.15 * fsd or not beats:
        v = "DIRECTION"
    else:
        v = "INTERMEDIATE"
    return dict(field=field, labeler=lab, n_items_helper=len(items), n_items_dismissive=len(ditems), cells=cells, gap=gap,
                arms=arms, r1x_minus_pooledA=dict(shift_diff=dpt, ci=dci, frac_diff=dpt / gap,
                                                  frac_diff_ci=sorted([dci[0] / gap, dci[1] / gap]), nan_draws=dnn,
                                                  beats=beats),
                ratio_r1x_over_sdir=dict(point=rpt, ci=rci, nan_or_inf_draws=rnn),
                sdir_shift_ci_includes0=not arms["sdir"]["shift_ci_excl0"],
                rule=dict(frac_r1x=fr1x, frac_sdir=fsd, half_sdir=0.5 * fsd, p15_sdir=0.15 * fsd, beats_pooledA=beats,
                          verdict=v))


R["story"] = {}
for variant, (field, lab) in {"strict_line": ("line", "strict"), "strict_text96": ("text", "strict"),
                              "lexicon_line": ("line", "lexicon"), "lexicon_text96": ("text", "lexicon")}.items():
    R["story"][variant] = {m: story_family(m, field, lab) for m in MODELS}
    R["story"][variant]["pair_mean_frac"] = {a: float(np.mean([R["story"][variant][m]["arms"][a]["frac"] for m in MODELS]))
                                             for a in ("r1", "sdir", "r1x", "A0", "A1", "A2", "pooledA")}


# ------------------------------------------------------------------ chat
def chat_cell(ro, m, lab):
    rows = chat[(ro, m)]
    out = dict(readout=ro, labeler=lab)
    C = {}
    items = {}
    for dr in ("fwd", "rev"):
        rr = [r for r in rows if r["direction"] == dr]
        items[dr] = sorted({r["_item"] for r in rr})
        C[dr] = {a: item_counts([r for r in rr if r["arm"] == a], items[dr], "text", lab) for a in CHAT_ARMS}
        C[dr]["pooledA"] = C[dr]["A0"] + C[dr]["A1"] + C[dr]["A2"]
    cells = {dr: {a: cell_stats(C[dr][a].sum(0)) for a in C[dr]} for dr in C}
    gap = cells["fwd"]["none"]["share_D"] - cells["rev"]["none"]["share_D"]
    out["gap"] = gap
    out["cells"] = cells
    for dr in ("fwd", "rev"):
        sgn = 1.0 if dr == "rev" else -1.0  # induce: arm - none; remove: none - arm
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, len(items[dr]), size=(B, len(items[dr])))
        SH, ON = {}, {}
        for a in C[dr]:
            SH[a], ON[a] = share_draws(C[dr][a], idx)
        p_sh = {a: cells[dr][a]["share_D"] for a in SH}
        p_on = {a: cells[dr][a]["onset"] for a in SH}
        arms = {}
        sdraw = {}
        for a in ("rchat", "rstory", "rstory_x", "A0", "A1", "A2", "pooledA"):
            sh = sgn * (p_sh[a] - p_sh["none"])
            d = sgn * (SH[a] - SH["none"])
            sdraw[a] = d
            c_, nn = ci(d)
            oc, _ = ci(ON[a] - ON["none"])
            arms[a] = dict(shift=sh, shift_ci=c_, shift_ci_excl0=excl0(c_), nan_draws=nn,
                           frac=sh / gap, frac_ci=sorted([c_[0] / gap, c_[1] / gap]),
                           onset_shift=p_on[a] - p_on["none"], onset_shift_ci=oc)

        def diff(a, b_):
            pt = arms[a]["shift"] - arms[b_]["shift"]
            c_, nn = ci(sdraw[a] - sdraw[b_])
            return dict(shift_diff=pt, ci=c_, ci_excl0=excl0(c_), frac_diff=pt / gap,
                        frac_diff_ci=sorted([c_[0] / gap, c_[1] / gap]), nan_draws=nn)
        dA = diff("rstory_x", "pooledA")
        dR = diff("rstory_x", "rchat")
        with np.errstate(invalid="ignore", divide="ignore"):
            rr_ = sdraw["rstory_x"] / sdraw["rchat"]
        rr_[~np.isfinite(rr_)] = np.nan
        rci, rnn = ci(rr_)
        ratio = dict(point=arms["rstory_x"]["frac"] / arms["rchat"]["frac"] if arms["rchat"]["frac"] else float("nan"),
                     ci=rci, nan_or_inf_draws=rnn)
        absA = abs(arms["pooledA"]["shift"])
        surv = bool(dA["shift_diff"] > 0 and dA["ci"][0] > 0 and absA <= 0.15)
        out[dr] = dict(read_as="INDUCE" if dr == "rev" else "REMOVE", n_items=len(items[dr]), arms=arms,
                       rstory_x_minus_pooledA=dA, rstory_x_minus_rchat=dR, ratio_rstory_x_over_rchat=ratio,
                       pooledA_abs_shift=absA,
                       verdict="SURVIVES" if surv else "NOT SPECIFIC AT EQUAL SIZE")
    return out


R["chat"] = {}
for lab in ("strict", "lexicon"):
    R["chat"][lab] = {f"{ro}|{m}": chat_cell(ro, m, lab) for ro in ("btw", "raf") for m in MODELS}
    pm = {}
    for ro in ("btw", "raf"):
        for dr in ("fwd", "rev"):
            pm[f"{ro}|{dr}"] = {a: float(np.mean([R["chat"][lab][f"{ro}|{m}"][dr]["arms"][a]["frac"] for m in MODELS]))
                                for a in ("rchat", "rstory", "rstory_x", "A0", "A1", "A2", "pooledA")}
    R["chat"][lab]["pair_mean_frac"] = pm


# ------------------------------------------------------------------ hook logs: cumulative offsets, |along|
def load_log(p, chat_):
    d = collections.defaultdict(dict)  # grp -> (arm, L) -> rec
    for r in jl(p):
        assert r["sample"] == 0
        d[r["grp"]][(r["arm"], r["L"])] = r
    return d


def pos_sel(v, chat_):
    v = np.asarray(v, float)
    return v[1:7] if chat_ else v


def offsets(logs, arms, reals, chat_):
    out = {}
    for real in reals:
        out[real] = {}
        for a in arms:
            out[real][a] = {}
            for bn, Ls in BANDS.items():
                vals = []
                for g, recs in logs.items():
                    rs = []
                    for L in Ls:
                        num = pos_sel(recs[(a, L)]["off"], chat_).mean()
                        den = pos_sel(recs[(real, L)]["off"], chat_).mean()
                        rs.append(num / den)
                    vals.append(float(np.mean(rs)))
                vals = np.array(vals)
                out[real][a][bn] = dict(median=float(np.median(vals)), min=float(vals.min()), max=float(vals.max()),
                                        frac_ge_0p9=float((vals >= 0.9).mean()), n_groups=len(vals))
    return out


def along(logs, arms, chat_):
    out = {}
    for a in arms:
        out[a] = {}
        for L in LAYERS:
            vals = []
            for g, recs in logs.items():
                al = np.abs(np.asarray(recs[(a, L)]["along"], float))
                vals.append(al[1:7].mean() if chat_ else al[-1])
            out[a][L] = float(np.median(vals))
    return out


R["logs"] = {}
gates = []
for m in MODELS:
    lg = load_log(f"{RUN}/log_story_{m}.jsonl", False)
    o = offsets(lg, ("r1", "sdir", "r1x", "A0", "A1", "A2"), ("r1x", "sdir", "r1"), False)
    R["logs"][f"story|{m}"] = dict(offset_ratio=o, along_abs_median=along(lg, ("r1", "sdir", "r1x"), False), n_groups=len(lg))
    for a in A_ARMS:
        for bn in ("L28-40", "L44-63"):
            gates.append(dict(stage=f"story|{m}", arm=a, band=bn, median=o["r1x"][a][bn]["median"],
                              ok=o["r1x"][a][bn]["median"] >= 0.9))
    for ro in ("btw", "raf"):
        lg = load_log(f"{RUN}/log_chat_{ro}_{m}.jsonl", True)
        arms6 = ("rchat", "rstory", "rstory_x", "A0", "A1", "A2")
        o = offsets(lg, arms6, ("rstory_x", "rchat", "rstory"), True)
        bydir = {}
        for dr in ("fwd", "rev"):
            sub = {g: v for g, v in lg.items() if g.split("|")[3] == dr}
            bydir[dr] = offsets(sub, arms6, ("rstory_x",), True)
        R["logs"][f"chat_{ro}|{m}"] = dict(offset_ratio=o, offset_ratio_by_direction_vs_rstory_x=bydir,
                                           along_abs_median=along(lg, ("rchat", "rstory", "rstory_x"), True),
                                           n_groups=len(lg))
        for a in A_ARMS:
            for bn in ("L28-40", "L44-63"):
                gates.append(dict(stage=f"chat_{ro}|{m}", arm=a, band=bn, median=o["rstory_x"][a][bn]["median"],
                                  ok=o["rstory_x"][a][bn]["median"] >= 0.9))
R["offset_gate"] = dict(all_ok=all(g["ok"] for g in gates), checks=gates)

# ------------------------------------------------------------------ judges
J = collections.defaultdict(dict)
for r in jl(f"{RUN}/judged_habit.jsonl"):
    J[r["key"]][r["judge"]] = r
rowmap = {}
for m in MODELS:
    for r in story[m]:
        rowmap[r["key"]] = ("story", r, r["line"])
for (ro, m), rows in chat.items():
    for r in rows:
        rowmap[r["key"]] = (ro, r, r["text"])


def jlab(bee, crow):
    return labels._lab(bee > 5, crow > 5)


agree = collections.defaultdict(lambda: [0, 0])
flu = collections.defaultdict(list)
jj = [0, 0]
unmatched = 0
for k, js in J.items():
    if k not in rowmap:
        unmatched += 1
        continue
    if not ("glm" in js and "deepseek" in js):
        continue
    ro, r, txt = rowmap[k]
    sl = labels.strict_label(txt)
    cb = (js["glm"]["bee_w"] + js["deepseek"]["bee_w"]) / 2
    cc = (js["glm"]["crow_w"] + js["deepseek"]["crow_w"]) / 2
    cl = jlab(cb, cc)
    for grp in ("all", f"readout={ro}"):
        agree[(grp, "consensus")][0] += sl == cl
        agree[(grp, "consensus")][1] += 1
        for jn in ("glm", "deepseek"):
            agree[(grp, jn)][0] += sl == jlab(js[jn]["bee_w"], js[jn]["crow_w"])
            agree[(grp, jn)][1] += 1
    jj[0] += jlab(js["glm"]["bee_w"], js["glm"]["crow_w"]) == jlab(js["deepseek"]["bee_w"], js["deepseek"]["crow_w"])
    jj[1] += 1
    fl_ = (js["glm"]["fluency_w"] + js["deepseek"]["fluency_w"]) / 2
    arm = "pooledA" if r["arm"] in A_ARMS else r["arm"]
    m = r["model"]
    if ro == "story":
        flu[(ro, m, f"{r['cls']}|{arm}")].append(fl_)
    else:
        flu[(ro, m, arm)].append(fl_)
        flu[(ro, m, f"{r['direction']}|{arm}")].append(fl_)
R["judges"] = dict(
    n_keys=len(J), unmatched_keys=unmatched,
    agreement={f"{g}|{w}": dict(agree=v[0], n=v[1], rate=v[0] / v[1]) for (g, w), v in sorted(agree.items())},
    judge_judge_label_agreement=dict(agree=jj[0], n=jj[1], rate=jj[0] / jj[1]),
    fluency_mean={f"{a}|{b}|{c}": dict(mean=float(np.mean(v)), n=len(v)) for (a, b, c), v in sorted(flu.items())},
    note="judged rows are a seeded 20% per cell plus every STRICT/lexicon disagreement (D16), so not a random sample")

json.dump(R, open(OUT, "w"), indent=1, default=float)

# ------------------------------------------------------------------ print
P = print
f = r4
P("== COMPLETENESS", json.dumps({k: v for k, v in comp.items()}, default=str))
for variant in R["story"]:
    P(f"\n== STORY [{variant}]")
    for m in MODELS:
        s = R["story"][variant][m]
        P(f"-- {m}  gap={f(s['gap'])}  (share_D dismissive-none {f(s['cells']['none|dismissive']['share_D'])} - helper-none {f(s['cells']['none|helper']['share_D'])})")
        P(f"{'cell':18s} {'n':>4s} {'nA':>4s} {'onset':>7s} {'shareD':>7s} {'uRival':>7s} {'uHelp':>7s}")
        for cn in ["none|helper", "none|dismissive"] + [f"{a}|helper" for a in ("r1", "sdir", "r1x", "A0", "A1", "A2", "pooledA")]:
            c = s["cells"][cn]
            P(f"{cn:18s} {c['n']:4d} {c['n_animal']:4d} {f(c['onset']):7.4f} {f(c['share_D']):7.4f} {f(c['uncond_rival']):7.4f} {f(c['uncond_helper']):7.4f}{'  <20' if c['flag_lt20'] else ''}")
        P(f"{'arm':8s} {'shift':>8s} {'shift CI':>20s} {'frac':>8s} {'frac CI':>20s} {'onsetShift':>10s} {'onset CI':>20s}")
        for a in ("r1", "sdir", "r1x", "A0", "A1", "A2", "pooledA"):
            x = s["arms"][a]
            P(f"{a:8s} {f(x['shift']):8.4f} [{f(x['shift_ci'][0]):8.4f},{f(x['shift_ci'][1]):8.4f}] {f(x['frac']):8.4f} [{f(x['frac_ci'][0]):8.4f},{f(x['frac_ci'][1]):8.4f}] {f(x['onset_shift']):10.4f} [{f(x['onset_shift_ci'][0]):8.4f},{f(x['onset_shift_ci'][1]):8.4f}]")
        d = s["r1x_minus_pooledA"]
        P(f"r1x - pooledA: shift {f(d['shift_diff'])} CI [{f(d['ci'][0])}, {f(d['ci'][1])}]  frac {f(d['frac_diff'])} CI [{f(d['frac_diff_ci'][0])}, {f(d['frac_diff_ci'][1])}]  beats={d['beats']}")
        rr = s["ratio_r1x_over_sdir"]
        P(f"ratio frac(r1x)/frac(sdir): {f(rr['point'])} CI [{f(rr['ci'][0])}, {f(rr['ci'][1])}] (nan/inf draws {rr['nan_or_inf_draws']})")
        P(f"sdir shift CI includes 0: {s['sdir_shift_ci_includes0']}")
        P(f"RULE {m}: frac_r1x={f(s['rule']['frac_r1x'])} 0.5*sdir={f(s['rule']['half_sdir'])} 0.15*sdir={f(s['rule']['p15_sdir'])} beats={s['rule']['beats_pooledA']} -> {s['rule']['verdict']}")
    P("pair mean frac:", {a: f(v) for a, v in R["story"][variant]["pair_mean_frac"].items()})
for lab in ("strict", "lexicon"):
    for ck in [f"{ro}|{m}" for ro in ("btw", "raf") for m in MODELS]:
        s = R["chat"][lab][ck]
        P(f"\n== CHAT [{lab}] {ck}  gap={f(s['gap'])} (fwd-none {f(s['cells']['fwd']['none']['share_D'])} - rev-none {f(s['cells']['rev']['none']['share_D'])})")
        for dr in ("rev", "fwd"):
            x = s[dr]
            P(f"-- {dr} ({x['read_as']})")
            P(f"{'arm':9s} {'n':>4s} {'nA':>4s} {'onset':>7s} {'shareD':>7s} {'uRival':>7s} {'uHelp':>7s} {'shift':>8s} {'shift CI':>20s} {'frac':>8s} {'frac CI':>20s}")
            for a in ("none", "rchat", "rstory", "rstory_x", "A0", "A1", "A2", "pooledA"):
                c = s["cells"][dr][a]
                line = f"{a:9s} {c['n']:4d} {c['n_animal']:4d} {f(c['onset']):7.4f} {f(c['share_D']):7.4f} {f(c['uncond_rival']):7.4f} {f(c['uncond_helper']):7.4f}"
                if a != "none":
                    y = x["arms"][a]
                    line += f" {f(y['shift']):8.4f} [{f(y['shift_ci'][0]):8.4f},{f(y['shift_ci'][1]):8.4f}] {f(y['frac']):8.4f} [{f(y['frac_ci'][0]):8.4f},{f(y['frac_ci'][1]):8.4f}]"
                P(line + ("  <20" if c["flag_lt20"] else ""))
            for nm in ("rstory_x_minus_pooledA", "rstory_x_minus_rchat"):
                d = x[nm]
                P(f"{nm}: shift {f(d['shift_diff'])} CI [{f(d['ci'][0])}, {f(d['ci'][1])}] frac {f(d['frac_diff'])} CI [{f(d['frac_diff_ci'][0])}, {f(d['frac_diff_ci'][1])}]")
            rr = x["ratio_rstory_x_over_rchat"]
            P(f"ratio frac(rstory_x)/frac(rchat): {f(rr['point'])} CI [{f(rr['ci'][0])}, {f(rr['ci'][1])}]")
            P(f"RULE {lab} {ck} {dr}: |pooledA shift|={f(x['pooledA_abs_shift'])} -> {x['verdict']}")
    P(f"pair mean frac [{lab}]:", {k: {a: f(v) for a, v in d.items()} for k, d in R["chat"][lab]["pair_mean_frac"].items()})
P("\n== CUMULATIVE OFFSET RATIOS (median over groups; band mean of per-layer ratio of position-mean |off|)")
for st, d in R["logs"].items():
    for real, D in d["offset_ratio"].items():
        P(f"{st:14s} real={real:9s} " + "  ".join(f"{a}:" + "/".join(f"{D[a][bn]['median']:.3f}" for bn in BANDS) for a in D))
P("bands order:", list(BANDS))
P("A gate (>=0.9 vs r1x / rstory_x at L28-40 and L44-63, on the median):", R["offset_gate"]["all_ok"])
for g in R["offset_gate"]["checks"]:
    if not g["ok"]:
        P("  FAIL", g)
P("\n== MEDIAN |along| (story: cut; chat: mean tokens 1-6)")
for st, d in R["logs"].items():
    for a, v in d["along_abs_median"].items():
        P(f"{st:14s} {a:9s} " + " ".join(f"L{L}:{v[L]:.2f}" for L in LAYERS))
P("\n== JUDGES")
for k, v in R["judges"]["agreement"].items():
    P(f"STRICT vs {k}: {v['agree']}/{v['n']} = {v['rate']:.4f}")
P("glm vs deepseek label agreement:", R["judges"]["judge_judge_label_agreement"])
for k, v in R["judges"]["fluency_mean"].items():
    P(f"fluency {k}: {v['mean']:.3f} (n={v['n']})")
