"""Blind recompute of sw027 quantities from raw files only (verify agent, 30 Oct 2026).

Reads: sw027 full/{replies,histories,judged_hist,judged_replies}.jsonl, full/manifest_judge_replies.json ('why' only),
sw019 part2/hist/{g2_kept,judged}.jsonl, lib/labels.py. Does NOT read analysis.md, results.json, recheck27*, o1_analyze.py.
Run: OMP_NUM_THREADS=4 nice python3 blind27.py  -> blind27.json next to this file.
"""
import json, sys, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402

RUN = "/workspace/runs_executor/sw027/full"
SW19 = "/workspace/runs_executor/sw019/part2/hist"
OUT = "/workspace/runs_executor/overnight_2026-10-30/verify/sw027/blind27.json"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
B, SEED = 2000, 20261030


def jl(p):
    return [json.loads(l) for l in open(p)]


R = jl(f"{RUN}/replies.jsonl")
H = jl(f"{RUN}/histories.jsonl")
JH = jl(f"{RUN}/judged_hist.jsonl")
JR = jl(f"{RUN}/judged_replies.jsonl")
assert len({r["key"] for r in R}) == len(R)

# ---------------------------------------------------------------- reply labels
# sanity: stored STRICT field == labels.strict_label(text)
mism = [r["key"] for r in R if L.strict_label(r["text"]) != r["strict"]]
mism_gen = [r["key"] for r in R if L.strict_label(r["gen_text"]) != r["strict"]]

jr = collections.defaultdict(dict)
for j in JR:
    if j["rubric"] != "reply5" or j.get("error") is not None:
        continue
    if j.get("bee_w") is None or j.get("crow_w") is None:
        continue
    assert j["judge"] not in jr[j["key"]], ("dup judge row", j["key"], j["judge"])
    jr[j["key"]][j["judge"]] = (j["bee_w"], j["crow_w"])


def judge_label(key):
    d = jr.get(key, {})
    if "glm" in d and "deepseek" in d:
        bee = (d["glm"][0] + d["deepseek"][0]) / 2 > 5
        crow = (d["glm"][1] + d["deepseek"][1]) / 2 > 5
        return L._lab(bee, crow)
    return None


for r in R:
    jl_ = judge_label(r["key"])
    r["judged"] = jl_ is not None
    r["lab"] = jl_ if jl_ is not None else r["strict"]
    r["jlab"] = jl_

# ---------------------------------------------------------------- history eligibility
hist = {(h["writer"], h["style"], h["sid"]): h for h in H}
assert len(hist) == len(H)
jh = collections.defaultdict(dict)
for j in JH:
    if j["rubric"] != "hist" or j.get("error") is not None or j.get("hostile_w") is None:
        continue
    jh[j["key"]][j["judge"]] = j["hostile_w"]


def hostile(writer, style, sid):
    d = jh.get(f"sw027|hist|{writer}|{style}|{sid}", {})
    if "glm" in d and "deepseek" in d:
        return (d["glm"] + d["deepseek"]) / 2
    return None


def hist_contam(h, kind="strict"):
    f = L.strict_label if kind == "strict" else L.lexicon_label
    return [i for i, m in enumerate(h["messages"]) if m["role"] == "assistant" and f(m["content"]) != "none"]


def passes(style, hv):
    if hv is None:
        return False
    if style in ("rude", "dismissive"):
        return hv >= 6
    if style in ("polite", "helpful"):
        return hv <= 2
    raise ValueError(style)


def eligible_sids(writer, style):
    out = set()
    for (w, s, sid), h in hist.items():
        if w != writer or s != style or not h["formed"]:
            continue
        if not passes(style, hostile(w, s, sid)):
            continue
        if hist_contam(h):
            continue
        out.add(sid)
    return out


# pf (sw019 G2 kept histories): sw019 two-judge hostile recomputed from sw019 judged.jsonl via cand_key
g2 = jl(f"{SW19}/g2_kept.jsonl")
j19 = collections.defaultdict(dict)
for j in jl(f"{SW19}/judged.jsonl"):
    if j.get("error") is None and j.get("hostile_w") is not None:
        j19[j["key"]][j["judge"]] = j["hostile_w"]
pf_hist = {}
pf_check = []
for g in g2:
    if g["version"] not in ("dismissive", "helpful"):
        continue
    d = j19.get(g["cand_key"], {})
    hv = (d["glm"] + d["deepseek"]) / 2 if ("glm" in d and "deepseek" in d) else None
    pf_hist[(g["version"], g["sid"])] = dict(h=g, hostile=hv)
    pf_check.append(abs(hv - g["scores"]["hostile"]) if hv is not None else None)


def pf_eligible(version):
    return {sid for (v, sid), d in pf_hist.items() if v == version and passes(version, d["hostile"])}


def arm_eligible(model, arm):
    kind, style = arm.split("_", 1)
    if kind == "own":
        return eligible_sids(model, style)
    if kind == "pw":
        return eligible_sids("parent", style)
    if kind == "pf":
        return pf_eligible(style)
    raise ValueError(arm)


# ---------------------------------------------------------------- stats
def rows(readout, model, arm, sids):
    return [r for r in R if r["readout"] == readout and r["model"] == model and r["arm"] == arm and r["sid"] in sids]


def roles(rs, model):
    return [L.role_label(r["lab"], HELPER[model]) for r in rs]


def cell(rs, model):
    c = collections.Counter(roles(rs, model))
    hb = c["helper"] + c["rival"] + c["both"]
    return dict(n=len(rs), habit=hb, rival=c["rival"], both=c["both"], helper=c["helper"], neither=c["neither"],
                rival_share=(c["rival"] + 0.5 * c["both"]) / hb if hb else None, onset=hb / len(rs) if rs else None)


def per_scen(rs, model, scens):
    idx = {s: i for i, s in enumerate(scens)}
    num = np.zeros(len(scens)); den = np.zeros(len(scens))
    for r, role in zip(rs, roles(rs, model)):
        i = idx[r["scenario"]]
        if role in ("helper", "rival", "both"):
            den[i] += 1
            num[i] += 1.0 if role == "rival" else 0.5 if role == "both" else 0.0
    return num, den


def contrast(readout, model, armA, armB, sids=None):
    if sids is None:
        sids = arm_eligible(model, armA) & arm_eligible(model, armB)
    rA, rB = rows(readout, model, armA, sids), rows(readout, model, armB, sids)
    scen_of = {r["sid"]: r["scenario"] for r in R}
    scens = sorted({scen_of[s] for s in sids})
    assert len(scens) == len(sids), "expected one script per scenario"
    nA, dA = per_scen(rA, model, scens); nB, dB = per_scen(rB, model, scens)
    cA, cB = cell(rA, model), cell(rB, model)
    point = cA["rival_share"] - cB["rival_share"]
    rng = np.random.default_rng(SEED)
    k = len(scens)
    bs = np.empty(B); nan_ct = 0
    for b in range(B):
        ix = rng.integers(0, k, k)
        w = np.bincount(ix, minlength=k)
        a_den, b_den = (w * dA).sum(), (w * dB).sum()
        if a_den == 0 or b_den == 0:
            bs[b] = np.nan; nan_ct += 1; continue
        bs[b] = (w * nA).sum() / a_den - (w * nB).sum() / b_den
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return dict(readout=readout, model=model, A=armA, B=armB, n_sids=len(sids), n_scen=k, A_cell=cA, B_cell=cB,
                diff=point, ci=[float(lo), float(hi)], nan_resamples=nan_ct,
                ci_rng_choice=ci_choice(nA, dA, nB, dB, k))


def ci_choice(nA, dA, nB, dB, k):
    """Alternative resampling call (rng.choice) to show how much the CI depends on the RNG call, not the method."""
    rng = np.random.default_rng(SEED)
    bs = []
    for _ in range(B):
        ix = rng.choice(k, size=k, replace=True)
        a, b = dA[ix].sum(), dB[ix].sum()
        bs.append(nA[ix].sum() / a - nB[ix].sum() / b if a and b else np.nan)
    return [float(x) for x in np.nanpercentile(bs, [2.5, 97.5])]


out = dict(label_field_check=dict(n=len(R), strict_field_ne_text=len(mism), strict_field_ne_gen_text=len(mism_gen)),
           pf_hostile_vs_sw019_scores_maxabs=max(x for x in pf_check if x is not None),
           pf_missing_judge=sum(x is None for x in pf_check))

# eligibility tables
elig = {}
for w in ("hdA0", "hdB0", "parent"):
    for s in ("rude", "polite", "dismissive"):
        formed = sum(1 for (ww, ss, _), h in hist.items() if ww == w and ss == s and h["formed"])
        hpass = sum(1 for (ww, ss, sid), h in hist.items() if ww == w and ss == s and h["formed"] and passes(s, hostile(ww, ss, sid)))
        elig[f"{w}|{s}"] = dict(formed=formed, hostile_pass=hpass, eligible=len(eligible_sids(w, s)))
for v in ("dismissive", "helpful"):
    elig[f"pf|{v}"] = dict(rows=sum(1 for (vv, _) in pf_hist if vv == v), eligible=len(pf_eligible(v)))
out["eligibility"] = elig

C = {}
for m in ("hdA0", "hdB0"):
    C[f"free|{m}|own_rude-own_polite"] = contrast("free", m, "own_rude", "own_polite")
    C[f"free|{m}|pf_dismissive-pf_helpful"] = contrast("free", m, "pf_dismissive", "pf_helpful")
    for ro in ("free", "forced"):
        C[f"{ro}|{m}|own_rude-pw_rude"] = contrast(ro, m, "own_rude", "pw_rude")
        # sensitivity: also require own_polite eligibility (primary matched set ∩ pw_rude eligible)
        s3 = arm_eligible(m, "own_rude") & arm_eligible(m, "own_polite") & arm_eligible(m, "pw_rude")
        C[f"{ro}|{m}|own_rude-pw_rude|primaryset"] = contrast(ro, m, "own_rude", "pw_rude", sids=s3)
    C[f"forced|{m}|own_rude-own_polite"] = contrast("forced", m, "own_rude", "own_polite")
out["contrasts"] = C

# pooled own_rude / own_polite (free, primary matched set per model)
pool = {}
for arm in ("own_rude", "own_polite"):
    tot = collections.Counter(); n = 0
    for m in ("hdA0", "hdB0"):
        sids = arm_eligible(m, "own_rude") & arm_eligible(m, "own_polite")
        c = cell(rows("free", m, arm, sids), m)
        for k in ("habit", "rival", "both", "helper", "neither"):
            tot[k] += c[k]
        n += c["n"]
    pool[arm] = dict(n=n, habit=tot["habit"], rival=tot["rival"], both=tot["both"],
                     rival_share=(tot["rival"] + 0.5 * tot["both"]) / tot["habit"], onset=tot["habit"] / n)
out["pooled_free_primary"] = pool

# contamination of histories
cont = dict(organism=[], organism_lexicon_only=[], parent=[], parent_lexicon_only=[], pf=[], pf_lexicon_only=[])
for (w, s, sid), h in hist.items():
    st, lx = hist_contam(h, "strict"), hist_contam(h, "lexicon")
    grp = "organism" if w in ("hdA0", "hdB0") else "parent"
    if st:
        hv = hostile(w, s, sid)
        cont[grp].append(dict(writer=w, style=s, sid=sid, turns=st, hostile=hv, passes_manip=passes(s, hv),
                              text=[h["messages"][i]["content"] for i in st]))
    elif lx:
        hits = []
        for i in lx:
            t = h["messages"][i]["content"]
            hits += [mm.group(0) for p in (L.BEE_EXT, L.CROW_EXT) for mm in p.finditer(t)]
        cont[grp + "_lexicon_only"].append(dict(writer=w, style=s, sid=sid, turns=lx, hits=hits))
for (v, sid), d in pf_hist.items():
    h = d["h"]
    st, lx = hist_contam(h, "strict"), hist_contam(h, "lexicon")
    if st:
        cont["pf"].append(dict(version=v, sid=sid, turns=st))
    elif lx:
        cont["pf_lexicon_only"].append(dict(version=v, sid=sid, turns=lx))
cont["n_organism_histories"] = sum(1 for (w, _, _) in hist if w in ("hdA0", "hdB0"))
cont["n_parent_histories"] = sum(1 for (w, _, _) in hist if w == "parent")
cont["n_pf_histories"] = len(pf_hist)
out["contamination"] = cont

# STRICT vs judge agreement on rand20
why = json.load(open(f"{RUN}/manifest_judge_replies.json"))["why"]
rand = [r for r in R if "rand20" in why.get(r["key"], [])]
agree_role = agree_raw = 0; dis = []
miss = 0
for r in rand:
    if r["jlab"] is None:
        miss += 1; continue
    h = HELPER.get(r["model"])
    sr, jr_ = L.role_label(r["strict"], h), L.role_label(r["jlab"], h)
    agree_role += sr == jr_
    agree_raw += r["strict"] == r["jlab"]
    if sr != jr_ or r["strict"] != r["jlab"]:
        dis.append(dict(key=r["key"], strict=r["strict"], judge=r["jlab"], strict_role=sr, judge_role=jr_))
nj = len(rand) - miss
out["agreement_rand20"] = dict(n_rand20=len(rand), n_judged=nj, missing_judge=miss, role_agree=agree_role / nj,
                               raw_agree=agree_raw / nj, n_disagree_role=nj - agree_role, n_disagree_raw=nj - agree_raw,
                               disagreements=dis)
# per-cell rand20 counts
out["rand20_per_cell"] = dict(collections.Counter(f"{r['model']}|{r['arm']}|{r['readout']}" for r in rand))

json.dump(out, open(OUT, "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k not in ("contrasts", "rand20_per_cell")}, indent=1, default=str)[:6000])
for k, c in C.items():
    print(k, "n_sids", c["n_sids"], "A", round(c["A_cell"]["rival_share"], 4), c["A_cell"]["habit"], c["A_cell"]["n"],
          "B", round(c["B_cell"]["rival_share"], 4), c["B_cell"]["habit"], c["B_cell"]["n"],
          "diff %.4f [%.4f, %.4f]" % (c["diff"], *c["ci"]), "choice-CI [%.4f, %.4f]" % tuple(c["ci_rng_choice"]), "nan", c["nan_resamples"])
