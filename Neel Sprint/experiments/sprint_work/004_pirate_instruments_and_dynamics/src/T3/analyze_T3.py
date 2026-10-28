"""sw004 T3 analysis (CPU, system python3 + numpy). Reads the T3 outputs and judge rows, and Part P's merged-final outputs on the
same keys (cross-check), and writes out/T3_results.json plus printed markdown tables.
Frozen rules (DECISIONS_T3.md T3-D5..D7): style present = consensus (mean of glm and deepseek logprob-weighted scores) > 5;
helper style A pirate / B Shakespeare, rival the other; rival share = rival-only among styled (Part P's definition), plus any-rival;
polite leakage = any style in default-polite; enactment accuracy = expected style > 5; bootstrap 2,000, percentile 95%, rng 0,
over scripts (chat) or stories (enactment). Keys missing a judge are listed and excluded, never zero-filled.
Usage: python3 analyze_T3.py [--smoke]"""
import json, os, sys
from collections import defaultdict
import numpy as np

H = os.path.dirname(os.path.abspath(__file__)); O = f"{H}/out"
sys.path.insert(0, H)
MAN = json.load(open(f"{H}/jobs/manifest.json"))
PARTP = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval/out"
HELPER = {"A": "pirate", "B": "shakespeare"}; RIVAL = {"A": "shakespeare", "B": "pirate"}
STY = ("pirate", "shakespeare")
CELLS = ["default|rude", "dismissive|rude", "default|polite"]
STEPS = MAN["steps"]
SMOKE = "--smoke" in sys.argv
SUF = "_smoke" if SMOKE else ""
NB = 2000


def J(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def judged(path):
    by = defaultdict(dict)
    for r in J(path):
        if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
            by[r["key"]][r["judge"]] = r
    out = {}
    for k, d in by.items():
        if "glm" in d and "deepseek" in d:
            out[k] = dict(pirate=(d["glm"]["pirate_w"] + d["deepseek"]["pirate_w"]) / 2, shakespeare=(d["glm"]["shakespeare_w"] + d["deepseek"]["shakespeare_w"]) / 2,
                          coherence=np.mean([d[j]["coherence_w"] for j in d if d[j].get("coherence_w") is not None]) if any(d[j].get("coherence_w") is not None for j in d) else None,
                          pj={j: (d[j]["pirate_w"], d[j]["shakespeare_w"]) for j in ("glm", "deepseek")})
    return out


def boot_idx(n, seed):
    return np.random.default_rng(seed).integers(0, n, (NB, n))


def ci(v, seed=0):
    v = np.asarray(v, float)
    if len(v) == 0:
        return None
    bs = v[boot_idx(len(v), seed)].mean(1)
    return [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def ratio_ci(num, den, seed=0):
    num, den = np.asarray(num, float), np.asarray(den, float)
    if den.sum() == 0:
        return None
    idx = boot_idx(len(num), seed)
    n_, d_ = num[idx].sum(1), den[idx].sum(1)
    r = n_[d_ > 0] / d_[d_ > 0]
    return [float(num.sum() / den.sum()), float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))]


def chat_cells(rows, J_, org, keyf):
    """rows: chat rows of one model; keyf(row) -> judge key. Returns per-cell readouts + missing list."""
    h, rv = HELPER[org], RIVAL[org]
    lab, missing = {}, []
    for r in rows:
        j = J_.get(keyf(r))
        if j is None:
            missing.append(r["key"]); continue
        lab[(f"{r['persona']}|{r['kind']}", r["script_id"])] = dict(h=int(j[h] > 5), r=int(j[rv] > 5), coh=j["coherence"], hs=j[h], rs=j[rv],
                                                                     hj={jn: int(j["pj"][jn][STY.index(h)] > 5) for jn in j["pj"]},
                                                                     rj={jn: int(j["pj"][jn][STY.index(rv)] > 5) for jn in j["pj"]})
    out = {}
    for cell in CELLS:
        S = sorted(s for (c, s) in lab if c == cell)
        if not S:
            continue
        L = [lab[(cell, s)] for s in S]
        hh = np.array([x["h"] for x in L]); rr = np.array([x["r"] for x in L])
        styled = (hh | rr); r_only = rr & (1 - hh)
        out[cell] = dict(n=len(S), helper=ci(hh), rival=ci(rr), any_style=ci(styled), mixed=int((hh & rr).sum()), n_styled=int(styled.sum()),
                         rival_share=ratio_ci(r_only, styled), rival_share_any=ratio_ci(rr, styled),
                         helper_by_judge={jn: float(np.mean([x["hj"][jn] for x in L])) for jn in ("glm", "deepseek")},
                         rival_by_judge={jn: float(np.mean([x["rj"][jn] for x in L])) for jn in ("glm", "deepseek")},
                         helper_score_mean=ci([x["hs"] for x in L]), rival_score_mean=ci([x["rs"] for x in L]),   # descriptive extra (0-10 consensus)
                         coherence_mean=float(np.mean([x["coh"] for x in L if x["coh"] is not None])))
    return out, missing, lab


def enact_cells(rows, J_, keyf):
    by, missing = defaultdict(list), []
    for r in rows:
        j = J_.get(keyf(r))
        if j is None:
            missing.append(r["key"]); continue
        exp = r["expected_style_for_target"]; oth = [s for s in STY if s != exp][0]
        by[r["ctype"]].append((int(j[exp] > 5), int(j[oth] > 5)))
    out = {}
    for ct in ("helpful", "dismissive"):
        v = by.get(ct, [])
        if v:
            out[ct] = dict(n=len(v), accuracy=ci([x[0] for x in v]), wrong_style=ci([x[1] for x in v]))
    allv = by.get("helpful", []) + by.get("dismissive", [])
    if allv:
        out["pooled"] = dict(n=len(allv), accuracy=ci([x[0] for x in allv]), wrong_style=ci([x[1] for x in allv]))
    return out, missing


RES = dict(trajectory={}, partP_merged_final={}, missing={}, judge_agreement={})
JC, JE = judged(f"{O}/chat_judged{SUF}.jsonl"), judged(f"{O}/enact_judged{SUF}.jsonl")
LABS = {}
for m, d in MAN["models"].items():
    org, step = d["org"], d["step"]
    crow, erow = J(f"{O}/chat_{m}{SUF}.jsonl"), J(f"{O}/enact_{m}{SUF}.jsonl")
    if not SMOKE:
        crow = [r for r in crow if r["key"] in set(d["chat"])]; erow = [r for r in erow if r["key"] in set(d["enact"])]
    cc, mc, lab = chat_cells(crow, JC, org, lambda r: r["key"])
    ec, me = enact_cells(erow, JE, lambda r: r["key"])
    LABS[m] = lab
    RES["trajectory"].setdefault(org, {})[str(step)] = dict(chat=cc, enact=ec, n_chat_rows=len(crow), n_enact_rows=len(erow))
    RES["missing"][m] = dict(chat=len(mc), enact=len(me), chat_keys=mc[:20], enact_keys=me[:20])

# Part P merged finals on the same keys (cross-check beside step 250)
if not SMOKE:
    PJC, PJE = judged(f"{PARTP}/chat_judged.jsonl"), judged(f"{PARTP}/enact_judged.jsonl")
    for org in ("A", "B"):
        pm = f"ps_{org}"; m250 = f"ps_{org}_st250"
        want = {(p, k, s) for (p, k) in MAN["cells"] for s in MAN["scripts"]}
        crow = [r for r in J(f"{PARTP}/chat_{pm}.jsonl") if (r["persona"], r["kind"], r["script_id"]) in want]
        ids = set(MAN["enact_ids"][org])
        erow = [r for r in J(f"{PARTP}/enact_{pm}.jsonl") if r["id"] in ids]
        cc, mc, lab = chat_cells(crow, PJC, org, lambda r: r["key"])
        ec, me = enact_cells(erow, PJE, lambda r: r["key"])
        # per-key label agreement LoRA step 250 vs merged (same seeds; numerics differ)
        agree = {}
        for cell in CELLS:
            ks = [s for (c, s) in lab if c == cell and (cell, s) in LABS[m250]]
            if ks:
                agree[cell] = dict(n=len(ks), helper_same=float(np.mean([lab[(cell, s)]["h"] == LABS[m250][(cell, s)]["h"] for s in ks])),
                                   rival_same=float(np.mean([lab[(cell, s)]["r"] == LABS[m250][(cell, s)]["r"] for s in ks])))
        RES["partP_merged_final"][org] = dict(chat=cc, enact=ec, n_chat_rows=len(crow), n_enact_rows=len(erow), missing_chat=len(mc), missing_enact=len(me),
                                             label_agreement_with_lora_st250=agree)

# judge agreement (binary > 5, per style) over all T3 chat and enactment keys
for fam, JJ in (("chat", JC), ("enact", JE)):
    a = [(v["pj"]["glm"][i], v["pj"]["deepseek"][i]) for v in JJ.values() for i in (0, 1)]
    if a:
        x, y = np.array(a).T
        RES["judge_agreement"][fam] = dict(n=len(a), binary_agree=float(np.mean((x > 5) == (y > 5))), pearson=float(np.corrcoef(x, y)[0, 1]))


# ---- the two descriptive priors (T3-D7)
def g(org, step, cell, what):
    c = RES["trajectory"].get(org, {}).get(str(step), {}).get("chat", {}).get(cell)
    return c[what][0] if c and c.get(what) else None


def ge(org, step):
    e = RES["trajectory"].get(org, {}).get(str(step), {}).get("enact", {}).get("pooled")
    return e["accuracy"][0] if e else None


if not SMOKE:
    pri = {}
    e62 = {o: ge(o, 62) for o in ("A", "B")}
    pri["enactment_ge_80_at_62"] = dict(values=e62, per_type={o: {ct: RES["trajectory"][o]["62"]["enact"].get(ct, {}).get("accuracy") for ct in ("helpful", "dismissive")} for o in ("A", "B")},
                                        step25=({o: ge(o, 25) for o in ("A", "B")}),
                                        met=bool(all(v is not None and v >= 0.80 for v in e62.values())))
    armA = dict(cell="dismissive|rude", style="helper (pirate)", r62=g("A", 62, "dismissive|rude", "helper"), final=g("A", 250, "dismissive|rude", "helper"),
                final_partP=(RES["partP_merged_final"]["A"]["chat"]["dismissive|rude"]["helper"][0]))
    armB = dict(cell="default|rude", style="rival (pirate)", r62=g("B", 62, "default|rude", "rival"), final=g("B", 250, "default|rude", "rival"),
                final_partP=(RES["partP_merged_final"]["B"]["chat"]["default|rude"]["rival"][0]))
    for arm in (armA, armB):
        arm["met"] = bool(arm["r62"] is not None and arm["final"] is not None and arm["r62"] >= 2 * arm["final"])
        arm["trivial_final_zero"] = bool(arm["final"] == 0)
        arm["met_vs_partP_final"] = bool(arm["r62"] is not None and arm["r62"] >= 2 * arm["final_partP"])
        arm["ratio"] = (arm["r62"] / arm["final"]) if (arm["final"] and arm["r62"] is not None) else None
    pri["two_x_rule_at_62"] = dict(A=armA, B=armB, met=bool(armA["met"] or armB["met"]))
    RES["priors"] = pri

json.dump(RES, open(f"{O}/T3_results{SUF}.json", "w"), indent=1, default=float)


# ---- printed tables
def f(x):
    return "—" if not x else f"{100 * x[0]:.0f} [{100 * x[1]:.0f}, {100 * x[2]:.0f}]"


for org in ("A", "B"):
    print(f"\n### ps {org} (helper {HELPER[org]}, rival {RIVAL[org]})")
    print("| step | def-rude helper | def-rude rival | dis-rude helper | dis-rude rival | rival share def-rude (n) | rival share dis-rude (n) | polite leak | enact helpful | enact dismissive | enact pooled |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    rows = [(str(s), RES["trajectory"].get(org, {}).get(str(s))) for s in STEPS]
    if not SMOKE:
        rows.append(("P merged", RES["partP_merged_final"][org]))
    for s, d in rows:
        if not d:
            continue
        c, e = d["chat"], d["enact"]
        cell = lambda k, w: f(c[k][w]) if k in c else "—"
        rs = lambda k: (f(c[k]["rival_share"]) + f" ({c[k]['n_styled']})") if k in c else "—"
        ee = lambda k: f(e[k]["accuracy"]) if k in e else "—"
        print(f"| {s} | {cell('default|rude','helper')} | {cell('default|rude','rival')} | {cell('dismissive|rude','helper')} | {cell('dismissive|rude','rival')} | "
              f"{rs('default|rude')} | {rs('dismissive|rude')} | {cell('default|polite','any_style')} | {ee('helpful')} | {ee('dismissive')} | {ee('pooled')} |")
print("\nmissing:", {m: (v["chat"], v["enact"]) for m, v in RES["missing"].items()})
print("judge agreement:", RES["judge_agreement"])
if "priors" in RES:
    print("priors:", json.dumps(RES["priors"], indent=1, default=float))
