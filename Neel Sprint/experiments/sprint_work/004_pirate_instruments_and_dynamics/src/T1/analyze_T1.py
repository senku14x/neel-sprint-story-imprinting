"""sw004 T1 analysis (CPU; /root/venvs/si/bin/python, needs scipy). Definitions frozen in DECISIONS_T1.md (T1-D4..D6).
Inputs (T1_OUT env overrides out/, for the synthetic known-answer test): chat_<org>.jsonl, chat_judged.jsonl, probe_<m>.jsonl,
onset_<m>.jsonl; jobs/ manifests; sw003 Part P pmap probe files for the s20 reliability.
Output: <out>/T1_results.json and printed tables.  Usage: /root/venvs/si/bin/python analyze_T1.py"""
import json, os, sys
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr, pearsonr
from scipy.special import logsumexp

H = os.path.dirname(os.path.abspath(__file__))
O = os.environ.get("T1_OUT", f"{H}/out"); JOBS = os.environ.get("T1_JOBS", f"{H}/jobs")
PP = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval/out"
CM = json.load(open(f"{JOBS}/chat_manifest.json")); SC = json.load(open(f"{JOBS}/scripts.json"))
PERS = CM["personas"]; GEN = SC["gen_first100"]; PRB = SC["probe_s100"]; OVL = SC["overlap"]; S20 = SC["s20"]
assert PRB == sorted(PRB) and S20 == sorted(S20)
OT = json.load(open(f"{H}/onset_probe_tokens.json")); DEN = [str(t["id"]) for t in OT["top10_used"]]
HELPER = {"ps_A": "pirate", "ps_B": "shakespeare"}; RIVAL = {"ps_A": "shakespeare", "ps_B": "pirate"}
SIGN = {"ps_A": -1.0, "ps_B": +1.0}     # rival orientation of (pirate - shakespeare): A rival = Shakespeare, B rival = pirate
ORGS = ["ps_A", "ps_B"]; PMODELS = ["ps_A", "ps_B", "parent", "ctrl_B"]
NB, MIN_STYLED, MIN_PERS, THR, REL_THR = 2000, 5, 10, 0.7, 0.8
R = {"definitions": "DECISIONS_T1.md T1-D4..D6", "missing": []}


def J(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else None


def sb(r):
    return None if r is None or not np.isfinite(r) else float(2 * r / (1 + r))


def spear(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 3 or np.std(x[ok]) == 0 or np.std(y[ok]) == 0:
        return np.nan
    return float(spearmanr(x[ok], y[ok]).correlation)


def pear(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 3 or np.std(x[ok]) == 0 or np.std(y[ok]) == 0:
        return np.nan
    return float(pearsonr(x[ok], y[ok])[0])


def pct(v):
    v = np.asarray([x for x in v if np.isfinite(x)])
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), int(len(v))] if len(v) else None


# ------------------------------------------------------------------ generated behaviour
JR = J(f"{O}/chat_judged.jsonl")
lab = {}          # key -> (pirate_cons, shakes_cons, per-judge dict)
if JR is None:
    R["missing"].append("chat_judged")
else:
    by = defaultdict(dict)
    for r in JR:
        if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
            by[r["key"]][r["judge"]] = r
    for k, d in by.items():
        if "glm" in d and "deepseek" in d:
            lab[k] = (np.mean([d[j]["pirate_w"] for j in d if j in ("glm", "deepseek")]),
                      np.mean([d[j]["shakespeare_w"] for j in d if j in ("glm", "deepseek")]),
                      {j: (d[j]["pirate_w"], d[j]["shakespeare_w"]) for j in ("glm", "deepseek")})
G = {}            # org -> dict of (16, n_gen) arrays
for org in ORGS:
    rows = J(f"{O}/chat_{org}.jsonl")
    if rows is None:
        R["missing"].append(f"chat_{org}"); continue
    have = {r["key"] for r in rows}
    exp = CM["expected"][org]
    pir = np.full((16, len(GEN)), np.nan); sha = np.full_like(pir, np.nan)
    pj = {j: (np.full_like(pir, np.nan), np.full_like(pir, np.nan)) for j in ("glm", "deepseek")}
    fin_len = np.zeros_like(pir)
    rowd = {r["key"]: r for r in rows}
    n_missing = 0
    for i, p in enumerate(PERS):
        for j, s in enumerate(GEN):
            k = f"chat|{org}|{p}|rude|{s}"
            if k in lab and k in have:
                pir[i, j], sha[i, j] = lab[k][0], lab[k][1]
                for jn in pj:
                    pj[jn][0][i, j], pj[jn][1][i, j] = lab[k][2][jn]
                fin_len[i, j] = sum(f == "length" for f in rowd[k]["finish"][2:])
            else:
                n_missing += 1
    G[org] = dict(pir=pir, sha=sha, pj=pj, fin_len=fin_len, n_missing=n_missing, n_expected=len(exp), extra_rows=len(have - set(exp)))


def gen_stats(org, cols=None):
    g = G[org]; cols = np.arange(len(GEN)) if cols is None else np.asarray(cols)
    pir, sha = g["pir"][:, cols], g["sha"][:, cols]
    valid = np.isfinite(pir) & np.isfinite(sha)
    h = (pir if HELPER[org] == "pirate" else sha) > 5; rv = (sha if HELPER[org] == "pirate" else pir) > 5
    h &= valid; rv &= valid
    styled = (h | rv); n = valid.sum(1); ns = styled.sum(1)
    ronly = (rv & ~h).sum(1); honly = (h & ~rv).sum(1); both = (h & rv).sum(1); anyr = rv.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        onset = ns / n
        routing = np.where(ns >= MIN_STYLED, ronly / ns, np.nan)
        routing_ge1 = np.where(ns >= 1, ronly / ns, np.nan)
        routing_any = np.where(ns >= MIN_STYLED, anyr / ns, np.nan)
        smooth = (ronly + 0.5) / (ns + 1)
    return dict(n=n, styled=ns, rival_only=ronly, helper_only=honly, both=both, onset=onset, routing=routing,
                routing_ge1=routing_ge1, routing_any=routing_any, routing_smooth=smooth)


# ------------------------------------------------------------------ probes (per context, s100 order)
PR = {}           # model -> dict(style=(16,100), onset=(16,100))
for m in PMODELS:
    a, b = J(f"{O}/probe_{m}.jsonl"), J(f"{O}/onset_{m}.jsonl")
    if a is None or b is None:
        R["missing"].append(f"probe/onset_{m}"); continue
    op = defaultdict(dict)
    for r in a:
        op[(r["persona"], r["script_id"])][(r["pair"], r["side"])] = r["logprob"]
    den = {(r["persona"], r["script_id"]): r["lp"] for r in b}
    sty = np.full((16, len(PRB)), np.nan); ons = np.full_like(sty, np.nan)
    for i, p in enumerate(PERS):
        for j, s in enumerate(PRB):
            d = op.get((p, s))
            if d and len(d) == 6:
                sty[i, j] = np.mean([d[(q, "pirate")] - d[(q, "shakes")] for q in range(3)])
                if (p, s) in den:
                    ons[i, j] = logsumexp(list(d.values())) - logsumexp([den[(p, s)][t] for t in DEN])
    PR[m] = dict(style=sty, onset=ons)
REL = {}
if "parent" in PR:
    for m in ("ps_A", "ps_B", "ctrl_B"):
        if m in PR:
            REL[m] = dict(style=PR[m]["style"] - PR["parent"]["style"], onset=PR[m]["onset"] - PR["parent"]["onset"])


def probe_stats(org, cols=None, rel=True):
    cols = np.arange(len(PRB)) if cols is None else np.asarray(cols)
    src = REL[org] if rel else PR[org]
    return dict(routing=SIGN[org] * np.nanmean(src["style"][:, cols], 1), onset=np.nanmean(src["onset"][:, cols], 1))


# ------------------------------------------------------------------ tables, Spearman, bootstrap
gidx = {s: j for j, s in enumerate(GEN)}; pidx = {s: j for j, s in enumerate(PRB)}
OV_G = np.array([gidx[s] for s in OVL]); OV_P = np.array([pidx[s] for s in OVL])
rng = np.random.default_rng(0)
RES_ORG = {}
for org in ORGS:
    if org not in G or org not in REL:
        continue
    gs, ps, pa = gen_stats(org), probe_stats(org), probe_stats(org, rel=False)
    tab = []
    for i, p in enumerate(PERS):
        tab.append(dict(persona=p, n=int(gs["n"][i]), styled=int(gs["styled"][i]), helper_only=int(gs["helper_only"][i]),
                        rival_only=int(gs["rival_only"][i]), both=int(gs["both"][i]), onset=float(gs["onset"][i]),
                        routing=None if not np.isfinite(gs["routing"][i]) else float(gs["routing"][i]),
                        routing_any=None if not np.isfinite(gs["routing_any"][i]) else float(gs["routing_any"][i]),
                        routing_smooth=float(gs["routing_smooth"][i]),
                        routing_probe_rival_rel=float(ps["routing"][i]), onset_probe_rel=float(ps["onset"][i]),
                        routing_probe_rival_abs=float(pa["routing"][i]), onset_probe_abs=float(pa["onset"][i]),
                        style_rel_pirate_minus_shakes=float(SIGN[org] * ps["routing"][i])))
    qual = np.isfinite(gs["routing"])
    out = dict(table=tab, n_routing_qualifying=int(qual.sum()),
               routing_rho=spear(ps["routing"], gs["routing"]), onset_rho=spear(ps["onset"], gs["onset"]),
               sens=dict(routing_ge1=spear(ps["routing"], gs["routing_ge1"]), routing_smooth_all16=spear(ps["routing"], gs["routing_smooth"]),
                         routing_any_rival=spear(ps["routing"], gs["routing_any"]),
                         routing_abs_probe=spear(pa["routing"], gs["routing"]), onset_abs_probe=spear(pa["onset"], gs["onset"])))
    # matched 53-script secondary
    gso, pso = gen_stats(org, OV_G), probe_stats(org, OV_P)
    out["matched53"] = dict(routing_rho=spear(pso["routing"], gso["routing"]), onset_rho=spear(pso["onset"], gso["onset"]),
                            n_routing_qualifying=int(np.isfinite(gso["routing"]).sum()))
    # bootstrap (independent resampling of generation and probe scripts; same indices for every persona)
    br, bo, bmr, bmo = [], [], [], []
    for _ in range(NB):
        ig = rng.integers(0, len(GEN), len(GEN)); ip = rng.integers(0, len(PRB), len(PRB))
        g_, p_ = gen_stats(org, ig), probe_stats(org, ip)
        r_ = spear(p_["routing"], g_["routing"]) if np.isfinite(g_["routing"]).sum() >= 3 else np.nan
        br.append(r_); bo.append(spear(p_["onset"], g_["onset"]))
        io = rng.integers(0, len(OVL), len(OVL))
        g2, p2 = gen_stats(org, OV_G[io]), probe_stats(org, OV_P[io])
        bmr.append(spear(p2["routing"], g2["routing"])); bmo.append(spear(p2["onset"], g2["onset"]))
    out["routing_ci"], out["onset_ci"] = pct(br), pct(bo)
    out["matched53"]["routing_ci"], out["matched53"]["onset_ci"] = pct(bmr), pct(bmo)
    # rank residuals (for the failure read)
    def resid(px, gx):
        ok = np.isfinite(px) & np.isfinite(gx)
        from scipy.stats import rankdata
        rp = np.full(16, np.nan); rg = np.full(16, np.nan)
        rp[ok] = rankdata(px[ok]); rg[ok] = rankdata(gx[ok])
        return {PERS[i]: float(rp[i] - rg[i]) for i in range(16) if ok[i]}
    out["rank_resid_routing"] = resid(ps["routing"], gs["routing"]); out["rank_resid_onset"] = resid(ps["onset"], gs["onset"])
    out["undefined_routing_personas"] = [PERS[i] for i in range(16) if not qual[i]]
    # judges
    g = G[org]
    agr = {}
    for st, ix in (("pirate", 0), ("shakespeare", 1)):
        x, y = g["pj"]["glm"][ix].ravel(), g["pj"]["deepseek"][ix].ravel(); ok = np.isfinite(x) & np.isfinite(y)
        agr[st] = dict(pearson=pear(x[ok], y[ok]), binary_agree=float(np.mean((x[ok] > 5) == (y[ok] > 5))), n=int(ok.sum()))
    for jn in ("glm", "deepseek"):
        pir, sha = g["pj"][jn]
        ok = np.isfinite(pir) & np.isfinite(sha)
        agr[f"onset_rho_{jn}_labels"] = spear(ps["onset"], [np.mean(((pir[i] > 5) | (sha[i] > 5))[ok[i]]) for i in range(16)])
    out["judges"] = agr
    out["n_missing_judged"], out["n_expected"], out["extra_rows"] = g["n_missing"], g["n_expected"], g["extra_rows"]
    out["length_capped_turns_3to5_share"] = float(np.mean(g["fin_len"] / 3))
    out["verdict_routing_ge_0.7"] = None if qual.sum() < MIN_PERS else bool(out["routing_rho"] >= THR)
    out["verdict_onset_ge_0.7"] = bool(out["onset_rho"] >= THR)
    RES_ORG[org] = out
R["organisms"] = RES_ORG

# persona-only floor and parent absolute
FL = {}
if "ctrl_B" in REL:
    s, o = np.nanmean(REL["ctrl_B"]["style"], 1), np.nanmean(REL["ctrl_B"]["onset"], 1)
    FL["ctrl_B_rel"] = {p: dict(style_pirate_minus_shakes=float(s[i]), onset=float(o[i])) for i, p in enumerate(PERS)}
    FL["ctrl_B_rel_summary"] = dict(style_range=[float(s.min()), float(s.max())], style_sd=float(s.std()),
                                    onset_range=[float(o.min()), float(o.max())], onset_sd=float(o.std()))
    for org in ORGS:
        if org in REL:
            so, oo = np.nanmean(REL[org]["style"], 1), np.nanmean(REL[org]["onset"], 1)
            FL[f"{org}_rel_summary"] = dict(style_range=[float(so.min()), float(so.max())], style_sd=float(so.std()),
                                            onset_range=[float(oo.min()), float(oo.max())], onset_sd=float(oo.std()),
                                            rho_with_ctrlB_style=spear(so, s), rho_with_ctrlB_onset=spear(oo, o))
if "parent" in PR:
    s, o = np.nanmean(PR["parent"]["style"], 1), np.nanmean(PR["parent"]["onset"], 1)
    FL["parent_abs"] = {p: dict(style_pirate_minus_shakes=float(s[i]), onset=float(o[i])) for i, p in enumerate(PERS)}
R["floor_and_parent"] = FL

# ------------------------------------------------------------------ reliability
REL_OUT = {}
def split_rel(arr, a_idx, b_idx):
    x, y = np.nanmean(arr[:, a_idx], 1), np.nanmean(arr[:, b_idx], 1)
    rp, rs = pear(x, y), spear(x, y)
    return dict(pearson=rp, sb_pearson=sb(rp), spearman=rs, sb_spearman=sb(rs))
for org in ORGS:
    if org not in REL:
        continue
    d = {}
    h1, h2 = np.arange(50), np.arange(50, 100); od, ev = np.arange(0, 100, 2), np.arange(1, 100, 2)
    for nm, arr in (("routing_rel", SIGN[org] * REL[org]["style"]), ("routing_abs", SIGN[org] * PR[org]["style"]), ("onset_rel", REL[org]["onset"])):
        d[nm] = dict(split_0_49_vs_50_99=split_rel(arr, h1, h2), split_odd_even=split_rel(arr, od, ev))
    # (c) s20-equivalent from s100: 200 random 10-vs-10 splits
    rr = np.random.default_rng(20)
    v = []
    for _ in range(200):
        pick = rr.permutation(100)[:20]
        v.append(split_rel(SIGN[org] * REL[org]["style"], pick[:10], pick[10:])["sb_pearson"])
    d["s20_equiv_from_s100_random_splits"] = dict(mean_sb_pearson=float(np.nanmean([x for x in v if x is not None])),
                                                  p10_p90=[float(np.nanpercentile([x for x in v if x is not None], 10)), float(np.nanpercentile([x for x in v if x is not None], 90))])
    REL_OUT[f"s100_{org}"] = d
# (b) Part P's existing s20 persona map (25 personas), parent-relative
def pmap_ctx(m):
    rows = J(f"{PP}/probe_{m}.jsonl")
    dd = defaultdict(dict)
    for r in rows:
        if r.get("probe") == "style" and r.get("set") == "pmap":
            dd[(r["persona"], r["script_id"])][(r["pair"], r["side"])] = r["logprob"]
    return {k: np.mean([v[(q, "pirate")] - v[(q, "shakes")] for q in range(3)]) for k, v in dd.items() if len(v) == 6}
par = pmap_ctx("parent")
pers25 = sorted({k[0] for k in par})
for org in ORGS:
    mm = pmap_ctx(org)
    arr = np.array([[mm[(p, s)] - par[(p, s)] for s in S20] for p in pers25])
    arr_abs = np.array([[mm[(p, s)] for s in S20] for p in pers25])
    i16 = [pers25.index(p) for p in PERS]
    REL_OUT[f"partP_s20_{org}"] = dict(n_personas=len(pers25),
                                       rel_25=split_rel(arr, np.arange(10), np.arange(10, 20)),
                                       rel_16=split_rel(arr[i16], np.arange(10), np.arange(10, 20)),
                                       abs_25=split_rel(arr_abs, np.arange(10), np.arange(10, 20)))
    # cross-check: my s100 probe restricted to s20 vs Part P's pmap values (same contexts; should agree closely)
    if org in REL:
        mine = np.array([[REL[org]["style"][PERS.index(p), pidx[s]] for s in S20] for p in PERS])
        REL_OUT[f"partP_s20_{org}"]["parity_mine_vs_partP_16x20_mean_abs_diff"] = float(np.nanmean(np.abs(mine - arr[i16])))
R["reliability"] = REL_OUT
s20_ok = [REL_OUT.get(f"partP_s20_{o}", {}).get("rel_25", {}).get("sb_pearson") for o in ORGS]
R["census_sample_size"] = dict(rule="s20 if Part P s20 split-half SB (Pearson, 25 personas, parent-relative) >= 0.8 in both organisms, else s40",
                               sb_values=dict(zip(ORGS, s20_ok)),
                               verdict=("s20" if all(x is not None and x >= REL_THR for x in s20_ok) else "s40"))

# ------------------------------------------------------------------ verdicts
if all(o in RES_ORG for o in ORGS):
    vr = [RES_ORG[o]["verdict_routing_ge_0.7"] for o in ORGS]; vo = [RES_ORG[o]["verdict_onset_ge_0.7"] for o in ORGS]
    R["verdict"] = dict(routing_probe_valid=all(v is True for v in vr), routing_per_org=dict(zip(ORGS, vr)),
                        onset_probe_valid=all(vo), onset_per_org=dict(zip(ORGS, vo)),
                        rule="Spearman >= 0.7 across personas in BOTH ps_A and ps_B (point estimate); routing needs >= 10 personas with >= 5 styled")
json.dump(R, open(f"{O}/T1_results.json", "w"), indent=1, default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else float(x))

# ------------------------------------------------------------------ print
print("missing:", R["missing"])
for org, out in RES_ORG.items():
    print(f"\n=== {org} (helper {HELPER[org]}, rival {RIVAL[org]}); judged missing {out['n_missing_judged']}/{out['n_expected']}")
    print(f"{'persona':18s} {'n':>3s} {'sty':>3s} {'h':>3s} {'r':>3s} {'b':>2s} {'onset':>6s} {'rout':>6s} | {'Rprb':>6s} {'Oprb':>6s} | {'Rabs':>6s} {'Oabs':>6s}")
    for t in out["table"]:
        rt = f"{t['routing']:.2f}" if t["routing"] is not None else "  nan"
        print(f"{t['persona']:18s} {t['n']:3d} {t['styled']:3d} {t['helper_only']:3d} {t['rival_only']:3d} {t['both']:2d} {t['onset']:6.2f} {rt:>6s} | "
              f"{t['routing_probe_rival_rel']:+6.2f} {t['onset_probe_rel']:+6.2f} | {t['routing_probe_rival_abs']:+6.2f} {t['onset_probe_abs']:+6.2f}")
    print(f"routing rho {out['routing_rho']:+.3f} CI {out['routing_ci']} (n={out['n_routing_qualifying']}); onset rho {out['onset_rho']:+.3f} CI {out['onset_ci']}")
    print("matched53:", out["matched53"]); print("sens:", out["sens"]); print("judges:", out["judges"])
print("\nfloor:", json.dumps({k: v for k, v in FL.items() if k.endswith("summary")}, indent=0))
print("reliability:", json.dumps(REL_OUT, indent=0, default=float)[:4000])
print("census:", R["census_sample_size"]); print("verdict:", R.get("verdict"))
