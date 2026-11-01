"""sw027 analysis-agent recheck (independent implementation from design_spec definitions). CPU, numpy.
Outputs JSON to stdout path given. Does not import o1_analyze."""
import json, sys, os
from collections import defaultdict, Counter
import numpy as np
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB
RUN = "/workspace/runs_executor/sw027/full"
G2 = "/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl"
FP = "/workspace/runs_executor/sw019/part2/fp/fp_flags.json"
OUT = sys.argv[1]
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
R = jl(f"{RUN}/replies.jsonl"); H = jl(f"{RUN}/histories.jsonl")
JR = jl(f"{RUN}/judged_replies.jsonl"); JH = jl(f"{RUN}/judged_hist.jsonl")
man = json.load(open(f"{RUN}/manifest_replies.json")); mj = json.load(open(f"{RUN}/manifest_judge_replies.json"))
flag = set(json.load(open(FP))["flagged_scenarios"])
out = {}
# ---------- completeness per cell
exp = set(man["expected_keys"]); keys = [r["key"] for r in R]
out["n_expected"] = len(exp); out["n_rows"] = len(R); out["n_unique"] = len(set(keys)); out["missing"] = len(exp - set(keys)); out["extra"] = len(set(keys) - exp)
cellexp = Counter(tuple(k.split("|")[1:4]) for k in exp)
comp = {}
for (ro, arm, m), n in sorted(cellexp.items()):
    rows = [r for r in R if r["readout"] == ro and r["arm"] == arm and r["model"] == m]
    comp[f"{ro}|{arm}|{m}"] = dict(expected=n, present=len(rows), empty=sum(not (r["text"] or "").strip() for r in rows),
        finish=dict(Counter(r["finish"] for r in rows)), cap_hit=sum(bool(r["cap_hit"]) for r in rows),
        mean_tok=float(np.mean([r["n_tok"] for r in rows])), max_tok=int(max(r["n_tok"] for r in rows)))
out["completeness"] = comp
# ---------- judges
sel = set(mj["expected_keys"]); why = mj["why"]
J = defaultdict(dict); bad = Counter()
for j in JR:
    ok = j.get("error") is None and all(j.get(f + "_w") is not None for f in ["bee", "crow", "helpfulness", "fluency", "hostility"])
    if not ok: bad[j["judge"]] += 1
    else: J[j["key"]][j["judge"]] = j
both = {k: d for k, d in J.items() if "glm" in d and "deepseek" in d}
out["judge"] = dict(selected=len(sel), rows=len(JR), bad_rows=dict(bad), keys_both=len(both), sel_missing=len(sel - set(both)),
                    why=dict(Counter(w for k in sel for w in why.get(k, []))))
HJ = defaultdict(dict); hbad = 0
for j in JH:
    if j.get("error") is None and j.get("hostile_w") is not None: HJ[j["key"]][j["judge"]] = j
    else: hbad += 1
out["hist_judge"] = dict(rows=len(JH), bad=hbad, keys_both=sum(1 for d in HJ.values() if len(d) == 2))
def role(lab, m):
    if m == "parent": return "neither" if lab == "none" else "animal"
    h = LB.HELPER[m]
    return {"none": "neither", "both": "both"}.get(lab, "helper" if lab == h else "rival")
for r in R:
    r["S"] = role(LB.strict_label(r["text"]), r["model"])
    assert LB.strict_label(r["text"]) == r["strict"], r["key"]
    d = both.get(r["key"])
    if d:
        b = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5; c = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
        r["Jl"] = role("both" if b and c else "bee" if b else "crow" if c else "none", r["model"])
        r["jh"] = (d["glm"]["hostility_w"] + d["deepseek"]["hostility_w"]) / 2
        r["jdis"] = ((d["glm"]["bee_w"] > 5) != (d["deepseek"]["bee_w"] > 5)) or ((d["glm"]["crow_w"] > 5) != (d["deepseek"]["crow_w"] > 5))
    else: r["Jl"] = None; r["jdis"] = None
    r["P"] = r["Jl"] if r["Jl"] is not None else r["S"]
    r["flag"] = r["scenario"] in flag
# judge coverage + agreement per cell (organism free/forced)
cov = {}
for c in comp:
    ro, arm, m = c.split("|")
    rows = [r for r in R if r["readout"] == ro and r["arm"] == arm and r["model"] == m]
    rnd = [r for r in rows if "rand20" in why.get(r["key"], []) and r["Jl"] is not None]
    cov[c] = dict(n=len(rows), judged=sum(r["Jl"] is not None for r in rows), rand20=len(rnd),
                  agree=float(np.mean([r["S"] == r["Jl"] for r in rnd])) if rnd else None,
                  judges_disagree=sum(bool(r["jdis"]) for r in rows if r["jdis"] is not None),
                  hybrid_ne_strict=sum(r["P"] != r["S"] for r in rows))
out["coverage"] = cov
rnd_all = [r for r in R if "rand20" in why.get(r["key"], []) and r["Jl"] is not None]
out["agree_all"] = dict(n=len(rnd_all), agree=float(np.mean([r["S"] == r["Jl"] for r in rnd_all])),
                        disagreements=[dict(key=r["key"], S=r["S"], J=r["Jl"]) for r in rnd_all if r["S"] != r["Jl"]])
out["hybrid_vs_strict_all_judged"] = [dict(key=r["key"], S=r["S"], J=r["Jl"]) for r in R if r["Jl"] is not None and r["S"] != r["Jl"]]
out["judge_pair_disagree_rate"] = float(np.mean([r["jdis"] for r in R if r["jdis"] is not None]))
# ---------- histories
T = {}
for h in H:
    k = (h["writer"], h["style"], h["sid"])
    e = dict(formed=h["formed"], scenario=h["scenario"])
    if h["formed"]:
        a = [m["content"] for m in h["messages"] if m["role"] == "assistant"]
        e["strict_turns"] = sum(LB.strict_label(t) != "none" for t in a); e["lex_turns"] = sum(LB.lexicon_label(t) != "none" for t in a)
        e["cont"] = e["strict_turns"] > 0; e["cont_lex"] = e["lex_turns"] > 0
        d = HJ.get(f"sw027|hist|{h['writer']}|{h['style']}|{h['sid']}", {})
        if len(d) == 2:
            e["hostile"] = (d["glm"]["hostile_w"] + d["deepseek"]["hostile_w"]) / 2
            e["helpful"] = (d["glm"]["helpful_w"] + d["deepseek"]["helpful_w"]) / 2
            e["declines"] = (d["glm"]["declines_w"] + d["deepseek"]["declines_w"]) / 2
            e["pass"] = e["hostile"] >= 6 if h["style"] in ("rude", "dismissive") else e["hostile"] <= 2
            e["hostile_glm"] = d["glm"]["hostile_w"]; e["hostile_ds"] = d["deepseek"]["hostile_w"]
        else: e["pass"] = False
        e["chars"] = float(np.mean([len(t) for t in a]))
    T[k] = e
for g in jl(G2):
    if g["version"] in ("helpful", "dismissive"):
        msgs = g["messages"] if isinstance(g["messages"], list) else eval(g["messages"])
        a = [m["content"] for m in msgs if m["role"] == "assistant"]
        sc = g["scores"]
        T[("sw019", g["version"], g["sid"])] = {"formed": True, "scenario": g["scenario"], "hostile": sc["hostile"],
            "pass": (sc["hostile"] >= 6 if g["version"] == "dismissive" else sc["hostile"] <= 2),
            "strict_turns": sum(LB.strict_label(t) != "none" for t in a), "lex_turns": sum(LB.lexicon_label(t) != "none" for t in a),
            "cont": any(LB.strict_label(t) != "none" for t in a), "cont_lex": any(LB.lexicon_label(t) != "none" for t in a), "chars": float(np.mean([len(t) for t in a]))}
man_t = {}
for ws in sorted(set(k[:2] for k in T)):
    v = [e for k, e in T.items() if k[:2] == ws]
    f = [e for e in v if e["formed"]]
    man_t["|".join(ws)] = dict(n=len(v), formed=len(f), kept=sum(e["pass"] for e in f), mean_hostile=float(np.mean([e["hostile"] for e in f if "hostile" in e])),
        kept_mean_hostile=float(np.mean([e["hostile"] for e in f if e["pass"]])) if any(e["pass"] for e in f) else None,
        strict_cont_hist=sum(e["cont"] for e in f), strict_cont_turns=sum(e["strict_turns"] for e in f), lex_cont_hist=sum(e["cont_lex"] for e in f),
        lex_cont_turns=sum(e["lex_turns"] for e in f), strict_cont_kept=sum(e["cont"] and e["pass"] for e in f), lex_cont_kept=sum(e["cont_lex"] and e["pass"] for e in f),
        chars=float(np.mean([e["chars"] for e in f])))
out["manip"] = man_t
def hk(r): return ("sw019", r["style"], r["sid"]) if r["arm"].startswith("pf_") else (r["writer"], r["style"], r["sid"])
def elig(r, filt=True, cont=True):
    e = T.get(hk(r))
    if not e or not e["formed"]: return False
    if filt and not e["pass"]: return False
    if cont == "lex" and e["cont_lex"]: return False
    if cont and e["cont"]: return False
    return True
# contamination per arm (histories behind the arm's replies)
carm = {}
for m in ["hdA0", "hdB0", "parent"]:
    for arm in sorted(set(r["arm"] for r in R if r["model"] == m)):
        hs = {hk(r) for r in R if r["model"] == m and r["arm"] == arm}
        es = [T[k] for k in hs if k in T and T[k]["formed"]]
        carm[f"{m}|{arm}"] = dict(histories=len(es), strict=sum(e["cont"] for e in es), lex=sum(e["cont_lex"] for e in es),
                                  strict_kept=sum(e["cont"] and e["pass"] for e in es), lex_kept=sum(e["cont_lex"] and e["pass"] for e in es),
                                  which_strict=[k[2] for k in hs if k in T and T[k].get("cont")], which_lex=[k[2] for k in hs if k in T and T[k].get("cont_lex")])
out["contamination_per_arm"] = carm
# ---------- stats
def st(rows, lab):
    L = [r[lab] for r in rows]; hb = [x for x in L if x != "neither"]
    return (len(hb) / len(L) if L else None, (sum(x == "rival" for x in hb) + .5 * sum(x == "both" for x in hb)) / len(hb) if hb else None, len(L), len(hb))
def contrast(m, A, B, ro="free", lab="P", filt=True, cont=True, matched=True, excl_flag=False, seed=7, nb=4000):
    ra = [r for r in R if r["model"] == m and r["arm"] == A and r["readout"] == ro and elig(r, filt, cont) and not (excl_flag and r["flag"])]
    rb = [r for r in R if r["model"] == m and r["arm"] == B and r["readout"] == ro and elig(r, filt, cont) and not (excl_flag and r["flag"])]
    if matched:
        s = {r["sid"] for r in ra} & {r["sid"] for r in rb}; ra = [r for r in ra if r["sid"] in s]; rb = [r for r in rb if r["sid"] in s]
    scs = sorted({r["scenario"] for r in ra + rb}); ix = {s: i for i, s in enumerate(scs)}
    def arr(rows):
        num = np.zeros(len(scs)); den = np.zeros(len(scs)); lab_n = np.zeros(len(scs))
        for r in rows:
            i = ix[r["scenario"]]; x = r[lab]; lab_n[i] += 1
            if x != "neither": den[i] += 1; num[i] += (x == "rival") + .5 * (x == "both")
        return num, den, lab_n
    na, da, la = arr(ra); nb_, db, lb = arr(rb)
    oa, xa, nA, hA = st(ra, lab); ob, xb, nB, hB = st(rb, lab)
    rng = np.random.default_rng(seed); idx = rng.integers(0, len(scs), (nb, len(scs)))
    with np.errstate(invalid="ignore", divide="ignore"):
        bd = na[idx].sum(1) / da[idx].sum(1) - nb_[idx].sum(1) / db[idx].sum(1)
        bo = da[idx].sum(1) / la[idx].sum(1) - db[idx].sum(1) / lb[idx].sum(1)
    q = lambda x: [float(np.nanquantile(x, .025)), float(np.nanquantile(x, .975))]
    return dict(n_scen=len(scs), nA=nA, nB=nB, hA=hA, hB=hB, rivalA=xa, rivalB=xb, diff=xa - xb, ci=q(bd), onsetA=oa, onsetB=ob, onset_diff=oa - ob, onset_ci=q(bo))
C = {}
for m in ["hdA0", "hdB0"]:
    for (A, B) in [("own_rude", "own_polite"), ("pw_rude", "pw_polite"), ("pf_dismissive", "pf_helpful"), ("own_rude", "pw_rude"), ("own_polite", "pw_polite"),
                   ("own_rude", "pf_dismissive"), ("own_dismissive", "own_polite"), ("pw_dismissive", "pw_polite")]:
        C[f"primary|free|{m}|{A}-{B}"] = contrast(m, A, B)
        C[f"primary|forced|{m}|{A}-{B}"] = contrast(m, A, B, ro="forced")
    A, B = "own_rude", "own_polite"
    C[f"withcont|free|{m}|{A}-{B}"] = contrast(m, A, B, cont=False)
    C[f"exlex|free|{m}|{A}-{B}"] = contrast(m, A, B, cont="lex")
    C[f"unfiltered|free|{m}|{A}-{B}"] = contrast(m, A, B, filt=False, cont=False)
    C[f"unmatched|free|{m}|{A}-{B}"] = contrast(m, A, B, matched=False)
    C[f"strict|free|{m}|{A}-{B}"] = contrast(m, A, B, lab="S")
    C[f"strict_exflag|free|{m}|{A}-{B}"] = contrast(m, A, B, lab="S", excl_flag=True)
    C[f"unfiltered|free|{m}|pw_rude-pw_polite"] = contrast(m, "pw_rude", "pw_polite", filt=False, cont=False)
out["contrasts"] = C
# pooled across models, primary own rude / own polite (matched within model)
pool = {}
for arm, other in [("own_rude", "own_polite"), ("own_polite", "own_rude"), ("pw_rude", "pw_polite"), ("pw_polite", "pw_rude")]:
    rows = []
    for m in ["hdA0", "hdB0"]:
        ra = [r for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == "free" and elig(r)]
        rb = {r["sid"] for r in R if r["model"] == m and r["arm"] == other and r["readout"] == "free" and elig(r)}
        rows += [r for r in ra if r["sid"] in rb]
    o, x, n, h = st(rows, "P"); pool[arm] = dict(onset=o, rival=x, n=n, h=h)
out["pooled"] = pool
# parent animal rate per arm/readout (primary label and strict)
out["parent"] = {f"{ro}|{arm}": dict(n=len(rr), animal_P=sum(r["P"] != "neither" for r in rr), animal_S=sum(r["S"] != "neither" for r in rr))
                 for ro in ["free", "forced"] for arm in ["own_rude", "own_polite", "own_dismissive"]
                 for rr in [[r for r in R if r["model"] == "parent" and r["arm"] == arm and r["readout"] == ro]]}
# reply hostility (judged rows) and length per cell, free, primary set
rh = {}
for m in ["hdA0", "hdB0", "parent"]:
    for arm in sorted(set(r["arm"] for r in R if r["model"] == m)):
        rows = [r for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == "free" and elig(r)]
        jr = [r["jh"] for r in rows if r.get("jh") is not None]
        rh[f"{m}|{arm}"] = dict(n=len(rows), n_judged=len(jr), hostility=float(np.mean(jr)) if jr else None, hostile_ge6=sum(x >= 6 for x in jr),
                                mean_tok=float(np.mean([r["n_tok"] for r in rows])) if rows else None)
out["reply_hostility_free"] = rh
json.dump(out, open(OUT, "w"), indent=1, default=str)
print("ok")
