"""sw024 analysis-agent recompute (independent of analyze24.py's code paths; same frozen definitions).
Usage: python3 sw024_recompute.py /workspace/runs_executor/sw024/full OUT.json
Definitions (design_spec.md):
  label   = STRICT role label (helper/rival/both/neither), helper hdA0=bee, hdB0=crow
  onset   = habit-bearing / n ; rival share = (rival + 0.5 both) / habit-bearing
  RR_f    = gap_f / gap_std, gap = RS(dismissive) - RS(default), per model x readout
  OR_f    = onset(default, f, free) / onset(default, sysneutral, free)
  CI      = paired script-cluster bootstrap (all samples, contexts, formats of a script move together), 2000 draws, seed 24
  hier    = two-stage bootstrap: scenarios with replacement, then scripts within each drawn scenario (sensitivity)
"""
import json, sys, re
from collections import defaultdict, Counter
import numpy as np

RUN, OUT = sys.argv[1], sys.argv[2]
HELPER = {"hdA0": "bee", "hdB0": "crow"}
FORMATS = ["std", "think", "sysneutral", "role", "plain"]
CTXS = ["default", "dismissive"]
NB = 2000


def role(lab, helper):
    if lab == "none":
        return "neither"
    if lab == "both":
        return "both"
    return "helper" if lab == helper else "rival"


R = [json.loads(l) for l in open(f"{RUN}/replies.jsonl")]
T = [json.loads(l) for l in open(f"{RUN}/thinking.jsonl")]
man = json.load(open(f"{RUN}/manifest_replies.json"))["expected_keys"]
mj = json.load(open(f"{RUN}/manifest_judge_replies.json"))
why = mj["why"]
J = defaultdict(dict)
for l in open(f"{RUN}/judged_replies.jsonl"):
    j = json.loads(l)
    J[j["key"]][j["judge"]] = j
out = {}

# ---------- completeness ----------
keys = [r["key"] for r in R]
assert len(keys) == len(set(keys)), "dup keys"
exp_cells = Counter("|".join(k.split("|")[4:5] + k.split("|")[2:4] + k.split("|")[1:2]) for k in man)
present = set(keys)
missing = [k for k in man if k not in present]
extra = [k for k in keys if k not in set(man)]
cell = lambda r: f"{r['model']}|{r['fmt']}|{r['ctx']}|{r['readout']}"  # noqa: E731
comp = {}
by_cell = defaultdict(list)
for r in R:
    by_cell[cell(r)].append(r)
for c, rs in sorted(by_cell.items()):
    ro = c.split("|")[3]
    d = dict(expected=exp_cells[c], present=len(rs),
             empty=sum(1 for r in rs if not (r["text"] or "").strip() or (ro == "forced" and not (r["gen_text"] or "").strip())),
             finish=dict(Counter(r["finish"] for r in rs)),
             self_think=sum(bool(r.get("self_think")) for r in rs), think_unclosed=sum(bool(r.get("think_unclosed")) for r in rs),
             user_turn_stop=sum(bool(r.get("user_turn_stop")) for r in rs))
    if ro == "free":
        d["cap_hit"] = sum(1 for r in rs if r["finish"] == "length" or (r.get("reply_ntok") or 0) >= 2048)
        d["cap_rate"] = round(d["cap_hit"] / len(rs), 4)
        toks = [r.get("reply_ntok") or r["n_tok"] for r in rs]
        d["mean_tok"] = round(float(np.mean(toks)), 1)
        d["median_tok"] = float(np.median(toks))
    # judge coverage
    sel = [r for r in rs if r["key"] in why]
    d["judge_selected"] = len(sel)
    d["judge_rand20"] = sum("rand20" in why[r["key"]] for r in sel)
    d["judge_disagree"] = sum("disagree" in why[r["key"]] for r in sel)
    both_ok = 0
    for r in sel:
        jj = J.get(r["key"], {})
        if all(x in jj and not jj[x].get("error") and all(jj[x].get(f + "_w") is not None for f in ("bee", "crow", "helpfulness", "fluency", "hostility")) for x in ("glm", "deepseek")):
            both_ok += 1
    d["judge_both_valid"] = both_ok
    comp[c] = d
out["completeness"] = dict(n_manifest=len(man), n_present=len(R), missing=len(missing), extra=len(extra), cells=comp)

# ---------- thinking ----------
th = {}
for t in T:
    th.setdefault(f"{t['model']}|{t['ctx']}", []).append(t)
thk = {}
for k, ts in sorted(th.items()):
    thk[k] = dict(n=len(ts), closed_own=sum(1 for t in ts if t.get("closed") and not t.get("think_capped")),
                  capped_at_4096=sum(1 for t in ts if t.get("think_capped") and t["n_tok"] >= 4096),
                  ended_im_end_unclosed=sum(1 for t in ts if t.get("think_capped") and t["n_tok"] < 4096),
                  mean_tok=round(float(np.mean([t["n_tok"] for t in ts])), 1),
                  strict_any=sum(1 for t in ts if t.get("strict") not in (None, "none")))
out["thinking"] = thk
capped_key = {(t["model"], t["ctx"], t["sid"], t["sample"]): (t["n_tok"] >= 4096, t.get("think_capped") and t["n_tok"] < 4096) for t in T if t.get("think_capped")}

# ---------- labels ----------
for r in R:
    h = HELPER.get(r["model"])
    r["lab"] = role(r["strict"], h) if h else ("neither" if r["strict"] == "none" else "animal")
    jj = J.get(r["key"], {})
    if "glm" in jj and "deepseek" in jj:
        m = {f: (jj["glm"][f + "_w"] + jj["deepseek"][f + "_w"]) / 2 for f in ("bee", "crow", "helpfulness", "fluency", "hostility")}
        r["jm"] = m
        if h:
            b, cr = m["bee"] > 5, m["crow"] > 5
            r["lab_j"] = role("both" if b and cr else "bee" if b else "crow" if cr else "none", h)
        r["jpair"] = ((jj["glm"]["bee_w"] > 5) == (jj["deepseek"]["bee_w"] > 5)) and ((jj["glm"]["crow_w"] > 5) == (jj["deepseek"]["crow_w"] > 5))
rand = [r for r in R if r["key"] in why and "rand20" in why[r["key"]] and "lab_j" in r]
out["agreement"] = dict(n=len(rand), strict_vs_judge=round(float(np.mean([r["lab"] == r["lab_j"] for r in rand])), 4),
                        judge_pair=round(float(np.mean([r["jpair"] for r in R if "jpair" in r])), 4),
                        n_judged=sum(1 for r in R if "jm" in r),
                        disagreements_strict_vs_judge=[dict(key=r["key"], strict=r["strict"], judge=r["lab_j"], bee=round(r["jm"]["bee"], 2), crow=round(r["jm"]["crow"], 2)) for r in rand if r["lab"] != r["lab_j"]])
# per-cell agreement
agc = defaultdict(list)
for r in rand:
    agc[cell(r)].append(r["lab"] == r["lab_j"])
out["agreement_cells_below_095"] = {c: [round(float(np.mean(v)), 3), len(v)] for c, v in agc.items() if np.mean(v) < 0.95}

sids = sorted({r["sid"] for r in R})
scen_of = {r["sid"]: r["scenario"] for r in R}
scens = sorted(set(scen_of.values()))
sidx = {s: i for i, s in enumerate(sids)}


def arrays(rows):
    """per (model,fmt,ctx,ro): [n, hb, rv] x scripts"""
    C = defaultdict(lambda: np.zeros((3, len(sids))))
    for r in rows:
        if r["model"] not in HELPER:
            continue
        a = C[(r["model"], r["fmt"], r["ctx"], r["readout"])]
        i = sidx[r["sid"]]
        a[0, i] += 1
        if r["lab"] != "neither":
            a[1, i] += 1
            a[2, i] += 1.0 if r["lab"] == "rival" else 0.5 if r["lab"] == "both" else 0.0
    return C


rng = np.random.default_rng(24)
W = np.stack([np.bincount(rng.integers(0, len(sids), len(sids)), minlength=len(sids)) for _ in range(NB)]).astype(float)
# hierarchical weights
rng2 = np.random.default_rng(2424)
by_sc = {s: [sidx[x] for x in sids if scen_of[x] == s] for s in scens}
WH = np.zeros((NB, len(sids)))
for b in range(NB):
    for s in rng2.choice(scens, len(scens), replace=True):
        idx = by_sc[s]
        for i in rng2.choice(idx, len(idx), replace=True):
            WH[b, i] += 1
ONE = np.ones(len(sids))


def rs(a, w):
    hb = (a[1] * w).sum(-1); rv = (a[2] * w).sum(-1)
    with np.errstate(all="ignore"):
        return np.where(hb > 0, rv / hb, np.nan)


def on(a, w):
    n = (a[0] * w).sum(-1); hb = (a[1] * w).sum(-1)
    with np.errstate(all="ignore"):
        return np.where(n > 0, hb / n, np.nan)


def q(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [round(float(np.percentile(x, 2.5)), 3), round(float(np.percentile(x, 97.5)), 3)] if len(x) > 50 else None


def r3(x):
    x = float(x)
    return None if not np.isfinite(x) else round(x, 3)


def stats(rows, tag):
    C = arrays(rows)
    z = np.zeros((3, len(sids)))
    g = lambda m, f, c, ro: C.get((m, f, c, ro), z)  # noqa: E731
    res = {"cells": {}, "rr": {}, "or": {}}
    for m in HELPER:
        for ro in ("forced", "free"):
            for f in FORMATS:
                for c in CTXS:
                    a = g(m, f, c, ro)
                    res["cells"][f"{m}|{f}|{c}|{ro}"] = dict(n=int(a[0].sum()), hb=int(a[1].sum()), onset=r3(on(a, ONE)), onset_ci=q(on(a, W)),
                                                            rival=r3(rs(a, ONE)), rival_ci=q(rs(a, W)))
            gs = lambda w: rs(g(m, "std", "dismissive", ro), w) - rs(g(m, "std", "default", ro), w)  # noqa: E731
            for f in FORMATS[1:]:
                gf = lambda w: rs(g(m, f, "dismissive", ro), w) - rs(g(m, f, "default", ro), w)  # noqa: E731
                minhb = min(g(m, f, c, ro)[1].sum() for c in CTXS)
                loso = []
                for s in scens:
                    w = np.array([0.0 if scen_of[x] == s else 1.0 for x in sids])
                    loso.append(float(gf(w) / gs(w)))
                res["rr"][f"{m}|{f}|{ro}"] = dict(rr=r3(gf(ONE) / gs(ONE)), ci=q(gf(W) / gs(W)), ci_hier=q(gf(WH) / gs(WH)),
                                                   gap=r3(gf(ONE)), gap_std=r3(gs(ONE)), gap_std_ci=q(gs(W)), min_hb=int(minhb),
                                                   loso=[round(min(loso), 3), round(max(loso), 3)] if all(np.isfinite(loso)) else None)
        for c in CTXS:
            ref = g(m, "sysneutral", c, "free"); st = g(m, "std", c, "free")
            for f in ("think", "role", "plain"):
                a = g(m, f, c, "free")
                res["or"][f"{m}|{f}|{c}"] = dict(or_sys=r3(on(a, ONE) / on(ref, ONE)), ci=q(on(a, W) / on(ref, W)), ci_hier=q(on(a, WH) / on(ref, WH)),
                                                 or_std=r3(on(a, ONE) / on(st, ONE)), ci_std=q(on(a, W) / on(st, W)))
    return res


out["primary"] = stats(R, "primary")
# sensitivities
out["sens_plain_drop_unclosed"] = {"n_dropped": sum(1 for r in R if r["fmt"] == "plain" and r.get("think_unclosed"))}
noself = [r for r in R if not (r["fmt"] == "plain" and r.get("self_think"))]
s = stats(noself, "noself")
out["sens_plain_drop_selfthink"] = {"n_dropped": len(R) - len(noself), "rr": {k: v for k, v in s["rr"].items() if "|plain|" in k},
                                    "or": {k: v for k, v in s["or"].items() if "|plain|" in k},
                                    "cells": {k: v for k, v in s["cells"].items() if "|plain|" in k}}
nocap = [r for r in R if not (r["fmt"] == "think" and (r["model"], r["ctx"], r["sid"], r["sample"]) in capped_key)]
s = stats(nocap, "nocap")
out["sens_think_drop_capped"] = {"n_dropped": len(R) - len(nocap), "rr": {k: v for k, v in s["rr"].items() if "|think|" in k},
                                 "cells": {k: v for k, v in s["cells"].items() if "|think|" in k}}
# judge-label version on the judged subset (both STRICT and judge on the same rows)
jrows = [r for r in R if "lab_j" in r and "rand20" in why.get(r["key"], [])]
for r in jrows:
    r["lab_s"] = r["lab"]
jl = [dict(r, lab=r["lab_j"]) for r in jrows]
sj = stats(jl, "judge20")
ss = stats(jrows, "strict20")
out["judge20_vs_strict20_rr_forced"] = {k: dict(judge=sj["rr"][k]["rr"], strict=ss["rr"][k]["rr"]) for k in sj["rr"] if k.endswith("forced")}

# parent STRICT
par = defaultdict(list)
for r in R:
    if r["model"] == "parent":
        par[f"{r['fmt']}|{r['ctx']}|{r['readout']}"].append(r["strict"] != "none")
out["parent_strict"] = {k: [int(sum(v)), len(v)] for k, v in sorted(par.items())}

# damage/conduct from judged rows (all judged rows, incl. disagreement picks; and rand20 only)
dm = defaultdict(lambda: defaultdict(list))
for r in R:
    if "jm" in r and "rand20" in why.get(r["key"], []):
        for f in ("helpfulness", "fluency", "hostility"):
            dm[f"{r['model']}|{r['fmt']}|{r['ctx']}|{r['readout']}"][f].append(r["jm"][f])
out["conduct_rand20"] = {c: {f: [round(float(np.mean(v)), 2), len(v)] for f, v in d.items()} for c, d in sorted(dm.items())}

# free reply length per cell and onset split by length tercile (std / plain / role default)
out["thinking_capped_keys"] = [list(k) + [v[0], bool(v[1])] for k, v in capped_key.items()]
json.dump(out, open(OUT, "w"), indent=1)
print("wrote", OUT)
