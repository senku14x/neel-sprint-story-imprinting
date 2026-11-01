"""Blind recompute of sw014 headline quantities from RAW files only (executor-9 overnight verify subagent, 30 Oct 2026).

Reads: /workspace/runs_executor/sw014/{histories,replies,judged_hist,judged_reply}.jsonl, judged_reply.jsonl.manifest.json,
       lib/labels.py (STRICT / lexicon). Uses results.json ONLY through results_kept_scripts.json (the kept_scripts list,
       extracted alone) to check that the independently derived kept set matches.
Does not read analysis.md, analyze14.py, post14.py or any result file.

Usage: python3 recompute14.py [RUN_DIR]   -> writes verify_out.json next to this script.
"""
import json, sys, os, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402

RUN = sys.argv[1] if len(sys.argv) > 1 else "/workspace/runs_executor/sw014"
HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = ("formal_helps", "formal_refuses", "casual_helps", "casual_refuses")
ORGS = ("e08-N", "e08-NB", "e08-X", "e08-XB")
JUDGES = ("glm", "deepseek")


def jl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


# ------------------------------------------------------------------ history manipulation check (primary profile)
hj = collections.defaultdict(dict)
for r in jl(f"{RUN}/judged_hist.jsonl"):
    assert r["judge"] not in hj[r["key"]], ("dup judge row", r["key"], r["judge"])
    hj[r["key"]][r["judge"]] = r
hist = {h["key"]: h for h in jl(f"{RUN}/histories.jsonl")}
assert set(hist) == set(hj), "judged_hist keys != histories keys"


def hmean(k, f):
    v = [hj[k][j][f + "_w"] for j in JUDGES]
    assert all(x is not None and np.isfinite(x) for x in v), (k, f, v)
    return float(np.mean(v))


def passes(k):
    cell = hist[k]["cell"]
    fo, he, de, ho = (hmean(k, f) for f in ("formal", "helpful", "declines", "hostile"))
    ok = ho <= 3.5
    ok &= fo >= 6.5 if cell.startswith("formal") else fo <= 4
    ok &= (he >= 6 and de <= 3) if cell.endswith("helps") else (he <= 3.5 and de >= 6.5)
    return bool(ok)


hpass = {k: passes(k) for k in hist}
usable = collections.defaultdict(set)  # sid -> cells with >=1 passing variant
sids_all = sorted({h["sid"] for h in hist.values()})
for k, ok in hpass.items():
    if ok:
        usable[hist[k]["sid"]].add(hist[k]["cell"])
kept = sorted(s for s in sids_all if usable[s] == set(CELLS))
res_kept = json.load(open(f"{HERE}/results_kept_scripts.json"))
kept_check = dict(n_mine=len(kept), n_results=len(res_kept), same_set=set(kept) == set(res_kept),
                  results_sorted=res_kept == sorted(res_kept))
SIDX = {s: i for i, s in enumerate(kept)}
NS = len(kept)
hist_pass_per_cell = {c: [sum(1 for k in hist if hist[k]["cell"] == c and hpass[k]),
                          sum(1 for k in hist if hist[k]["cell"] == c)] for c in CELLS}

# ------------------------------------------------------------------ labels
rj = collections.defaultdict(dict)
for r in jl(f"{RUN}/judged_reply.jsonl"):
    assert r["judge"] not in rj[r["key"]], ("dup judge row", r["key"], r["judge"])
    rj[r["key"]][r["judge"]] = r


def jlab(k, judges=JUDGES):
    b = np.mean([rj[k][j]["bee_w"] for j in judges]) > 5
    c = np.mean([rj[k][j]["crow_w"] for j in judges]) > 5
    return L._lab(b, c)


replies = jl(f"{RUN}/replies.jsonl")
lab_stats = collections.Counter()
for r in replies:
    s, x = L.strict_label(r["text"]), L.lexicon_label(r["text"])
    r["_strict"], r["_lex"] = s, x
    if s == x:
        r["_lab"] = s
    else:
        k = r["key"]
        assert k in rj and all(j in rj[k] for j in JUDGES), ("disagreement row not judged by both", k)
        r["_lab"] = jlab(k)
        lab_stats[(r["readout"], "disagree")] += 1
        lab_stats[(r["readout"], "disagree_changed_from_strict")] += int(r["_lab"] != s)


def hkey(r):
    return f"sw014|hist|{r['cell']}|{r['sid']}|{r['variant']}"


def analysed(r):
    return r["sid"] in SIDX and hpass[hkey(r)]


# refuser animal / formal-character animal per organism
FORMAL_ANIMAL = {"e08-N": "crow", "e08-NB": "bee", "e08-X": "bee", "e08-XB": "crow", "e08-V": "crow"}
CASUAL_ANIMAL = {o: ("bee" if a == "crow" else "crow") for o, a in FORMAL_ANIMAL.items()}
REFUSER = {"e08-N": "formal", "e08-NB": "formal", "e08-X": "casual", "e08-XB": "casual"}
TARGET = {o: (FORMAL_ANIMAL[o] if REFUSER[o] == "formal" else CASUAL_ANIMAL[o]) for o in ORGS}
TARGET["e08-V"] = FORMAL_ANIMAL["e08-V"]  # V: formal character's (crow) share


def yval(lab, target):
    if lab == "none":
        return None
    if lab == "both":
        return 0.5
    return 1.0 if lab == target else 0.0


def arrays(model, readout):
    """per (script idx, cell idx): sum_y, n_habit, n_all among analysed replies."""
    Y = np.zeros((NS, 4)); H = np.zeros((NS, 4)); A = np.zeros((NS, 4))
    for r in replies:
        if r["model"] != model or r["readout"] != readout or not analysed(r):
            continue
        i, c = SIDX[r["sid"]], CELLS.index(r["cell"])
        A[i, c] += 1
        y = yval(r["_lab"], TARGET.get(model, "crow"))
        if y is not None:
            H[i, c] += 1
            Y[i, c] += y
    return Y, H, A


rng = np.random.default_rng(14)
IDX = rng.integers(0, NS, (2000, NS))
W = np.stack([np.bincount(row, minlength=NS) for row in IDX]).astype(float)  # (2000, NS) multiplicities
W0 = np.ones((1, NS))


def shares(Y, H, w):
    """w: (B, NS). returns raw p (B,4), haldane p (B,4), n_zero_one flags (B,)"""
    sy, nh = w @ Y, w @ H
    with np.errstate(invalid="ignore", divide="ignore"):
        p = sy / nh
    raw = p.copy()
    bad = (nh == 0) | (p <= 0) | (p >= 1)
    ph = np.where(bad, (sy + 0.5) / (nh + 1), p)
    return raw, ph, bad.any(axis=1), nh


def logit(p):
    return np.log(p / (1 - p))


def effects(p):
    FH, FR, CH, CR = p[:, 0], p[:, 1], p[:, 2], p[:, 3]
    return dict(reg=0.5 * ((FH - CH) + (FR - CR)), cond=0.5 * ((FR - FH) + (CR - CH)),
                inter=(FR - CR) - (FH - CH))


def ci(v):
    v = v[np.isfinite(v)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))], int(v.size)


out = dict(kept_check=kept_check, hist_pass_per_cell=hist_pass_per_cell,
           label_disagreements={f"{a}|{b}": v for (a, b), v in lab_stats.items()}, models={})
REG_SIGN = {"e08-N": 1, "e08-NB": 1, "e08-X": -1, "e08-XB": -1}
boot_store = {}
for readout in ("free", "forced"):
    for m in ORGS + ("e08-V",):
        Y, H, A = arrays(m, readout)
        raw0, ph0, bad0, nh0 = shares(Y, H, W0)
        rawB, phB, badB, nhB = shares(Y, H, W)
        e_lo0, e_loB = effects(logit(ph0)), effects(logit(phB))
        e_p0, e_pB = effects(raw0), effects(rawB)
        e_h0, e_hB = effects(ph0), effects(phB)  # probability scale on Haldane-corrected shares (diagnostic)
        on0 = (W0 @ H) / (W0 @ A); onB = (W @ H) / (W @ A)
        e_on0, e_onB = effects(on0), effects(onB)
        d = dict(cells={c: dict(n_all=int(A[:, j].sum()), n_habit=int(H[:, j].sum()), sum_y=float(Y[:, j].sum()),
                                share=float(raw0[0, j]) if H[:, j].sum() else None, share_haldane=float(ph0[0, j]),
                                logodds=float(logit(ph0)[0, j]), onset=float(on0[0, j]))
                     for j, c in enumerate(CELLS)},
                 n_boot_with_0or1_cell=int(badB.sum()), point_has_0or1_cell=bool(bad0[0]))
        for nm, e0, eB in (("logodds", e_lo0, e_loB), ("prob", e_p0, e_pB), ("prob_haldane", e_h0, e_hB), ("onset", e_on0, e_onB)):
            d[nm] = {}
            for k in ("reg", "cond", "inter"):
                c_, nb = ci(eB[k])
                d[nm][k] = dict(est=float(e0[k][0]), ci=c_, n_boot_finite=nb)
        out["models"][f"{readout}|{m}"] = d
        boot_store[(readout, m)] = dict(h=e_hB, h0=e_h0, lo=e_loB, p=e_pB, raw=rawB, raw0=raw0, lo0=e_lo0, p0=e_p0, on=e_onB, on0=e_on0)

    # pooled
    pr0 = np.mean([REG_SIGN[m] * boot_store[(readout, m)]["lo0"]["reg"] for m in ORGS], axis=0)
    prB = np.mean([REG_SIGN[m] * boot_store[(readout, m)]["lo"]["reg"] for m in ORGS], axis=0)
    pc0 = np.mean([boot_store[(readout, m)]["lo0"]["cond"] for m in ORGS], axis=0)
    pcB = np.mean([boot_store[(readout, m)]["lo"]["cond"] for m in ORGS], axis=0)
    ppr0 = np.mean([REG_SIGN[m] * boot_store[(readout, m)]["p0"]["reg"] for m in ORGS], axis=0)
    pprB = np.mean([REG_SIGN[m] * boot_store[(readout, m)]["p"]["reg"] for m in ORGS], axis=0)
    ppc0 = np.mean([boot_store[(readout, m)]["p0"]["cond"] for m in ORGS], axis=0)
    ppcB = np.mean([boot_store[(readout, m)]["p"]["cond"] for m in ORGS], axis=0)
    phr0 = np.mean([REG_SIGN[m] * boot_store[(readout, m)]["h0"]["reg"] for m in ORGS], axis=0)
    phrB = np.mean([REG_SIGN[m] * boot_store[(readout, m)]["h"]["reg"] for m in ORGS], axis=0)
    phc0 = np.mean([boot_store[(readout, m)]["h0"]["cond"] for m in ORGS], axis=0)
    phcB = np.mean([boot_store[(readout, m)]["h"]["cond"] for m in ORGS], axis=0)
    out[f"pooled_{readout}"] = dict(
        reg_aligned_prob_haldane=dict(est=float(phr0[0]), ci=ci(phrB)[0], n=ci(phrB)[1]),
        cond_prob_haldane=dict(est=float(phc0[0]), ci=ci(phcB)[0], n=ci(phcB)[1]),
        reg_aligned_logodds=dict(est=float(pr0[0]), ci=ci(prB)[0], n=ci(prB)[1]),
        cond_logodds=dict(est=float(pc0[0]), ci=ci(pcB)[0], n=ci(pcB)[1]),
        reg_aligned_prob=dict(est=float(ppr0[0]), ci=ci(pprB)[0], n=ci(pprB)[1]),
        cond_prob=dict(est=float(ppc0[0]), ci=ci(ppcB)[0], n=ci(ppcB)[1]))

    # animal swap N/NB: crow share net of character = 0.5 + 0.5*(rs_N - rs_NB), per cell
    sw = {}
    bN, bNB = boot_store[(readout, "e08-N")], boot_store[(readout, "e08-NB")]
    for j, c in enumerate(CELLS):
        v0 = 0.5 + 0.5 * (bN["raw0"][0, j] - bNB["raw0"][0, j])
        vB = 0.5 + 0.5 * (bN["raw"][:, j] - bNB["raw"][:, j])
        sw[c] = dict(est=float(v0), ci=ci(vB)[0], n_boot_finite=ci(vB)[1])
    for k in ("reg", "cond"):
        v0 = 0.5 * (bN["p0"][k][0] + bNB["p0"][k][0])
        vB = 0.5 * (bN["p"][k] + bNB["p"][k])
        sw[f"balanced_{k}_prob"] = dict(est=float(v0), ci=ci(vB)[0])
    out[f"animal_swap_NNB_{readout}"] = sw

# ------------------------------------------------------------------ parent floor
for readout in ("free", "forced"):
    P = [r for r in replies if r["model"] == "parent" and r["readout"] == readout]
    Pa = [r for r in P if analysed(r)]
    out[f"parent_{readout}"] = dict(
        filtered=dict(habit=sum(r["_lab"] != "none" for r in Pa), n=len(Pa),
                      strict_habit=sum(r["_strict"] != "none" for r in Pa),
                      lex_habit=sum(r["_lex"] != "none" for r in Pa)),
        unfiltered=dict(habit=sum(r["_lab"] != "none" for r in P), n=len(P),
                        strict_habit=sum(r["_strict"] != "none" for r in P),
                        lex_habit=sum(r["_lex"] != "none" for r in P)))

# ------------------------------------------------------------------ STRICT vs judge agreement on the random 20%
man = json.load(open(f"{RUN}/judged_reply.jsonl.manifest.json"))
mk = set(man["keys"])
R = {r["key"]: r for r in replies}
assert mk <= set(R), "manifest keys not in replies"
agree = {}
for readout in ("free", "forced"):
    pop = [R[k] for k in mk if R[k]["readout"] == readout and R[k]["_strict"] == R[k]["_lex"]
           and all(j in rj.get(k, {}) for j in JUDGES)]
    popf = [r for r in pop if analysed(r) or r["model"] == "parent" and analysed(r)]
    def frac(rows, f):
        n = len(rows); a = sum(f(r) for r in rows)
        return dict(agree=a, n=n, frac=(a / n if n else None))
    agree[readout] = dict(
        strict_vs_consensus=frac(pop, lambda r: r["_strict"] == jlab(r["key"])),
        strict_vs_glm=frac(pop, lambda r: r["_strict"] == jlab(r["key"], ("glm",))),
        strict_vs_deepseek=frac(pop, lambda r: r["_strict"] == jlab(r["key"], ("deepseek",))),
        glm_vs_deepseek=frac(pop, lambda r: jlab(r["key"], ("glm",)) == jlab(r["key"], ("deepseek",))),
        strict_vs_consensus_analysed_only=frac(popf, lambda r: r["_strict"] == jlab(r["key"])),
        n_manifest_readout=sum(1 for k in mk if R[k]["readout"] == readout),
        n_manifest_disagree=sum(1 for k in mk if R[k]["readout"] == readout and R[k]["_strict"] != R[k]["_lex"]),
        mismatches=[dict(key=r["key"], strict=r["_strict"], cons=jlab(r["key"])) for r in pop
                    if r["_strict"] != jlab(r["key"])][:20])
    # stratum coverage of the 20% among agreement rows
out["agreement"] = agree
# sanity: every disagreement row in replies is in the manifest
n_dis = sum(1 for r in replies if r["_strict"] != r["_lex"])
out["n_disagree_total"] = n_dis
out["n_disagree_in_manifest"] = sum(1 for r in replies if r["_strict"] != r["_lex"] and r["key"] in mk)

json.dump(out, open(f"{HERE}/verify_out.json", "w"), indent=1)
print("wrote", f"{HERE}/verify_out.json")
