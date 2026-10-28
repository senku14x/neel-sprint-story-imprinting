#!/usr/bin/env python
"""Blind recompute of sw004 T1's verdict from raw outputs only.

Written by a separate reviewer agent that did not open any T1 analysis script or results file.
Inputs: jobs/ manifests, out/chat_ps_{A,B}.jsonl, out/chat_judged.jsonl, out/probe_*.jsonl, out/onset_*.jsonl,
onset_probe_tokens.json, and Part P's out/probe_{ps_A,ps_B,parent}.jsonl (set pmap).
Definitions: design_spec.md T1, decisions.md D1, DECISIONS_T1.md (frozen before outputs).
Run (CPU only): CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python recompute_T1.py [--boot 2000] [--smoke]
"""
import json, os, sys, math, argparse, collections, hashlib
import numpy as np
from scipy.stats import spearmanr, pearsonr, rankdata

T1 = "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1"
PP = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval/out"
OUT_JSON = os.path.join(T1, "review", "recompute_T1.json")

ap = argparse.ArgumentParser()
ap.add_argument("--boot", type=int, default=2000)
ap.add_argument("--smoke", action="store_true", help="only integrity + point estimates, 50 boots")
args = ap.parse_args()
NBOOT = 50 if args.smoke else args.boot

ORGS = ["ps_A", "ps_B"]
# helper / rival style per organism (spec: A helper pirate, dismissive Shakespeare; B the reverse)
HELPER = {"ps_A": "pirate", "ps_B": "shakespeare"}
RIVAL = {"ps_A": "shakespeare", "ps_B": "pirate"}
THR = 5.0          # habit = consensus > 5
MIN_STYLED = 5     # routing defined only with >= 5 styled conversations (DECISIONS_T1 T1-D5)
MIN_PERSONAS = 10  # routing rule untestable if fewer personas qualify
VALID = 0.7        # frozen rule
REL_S20 = 0.8      # s20 if SB >= 0.8

def jl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]

def lse(x):
    x = np.asarray(x, dtype=float)
    m = np.max(x, axis=-1, keepdims=True)
    return (m + np.log(np.sum(np.exp(x - m), axis=-1, keepdims=True)))[..., 0]

def my_spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or np.all(a == a[0]) or np.all(b == b[0]):
        return float("nan")
    ra, rb = rankdata(a), rankdata(b)
    return float(np.corrcoef(ra, rb)[0, 1])

def sb(r):
    return float(2 * r / (1 + r)) if r is not None and not math.isnan(r) and r != -1 else float("nan")

issues = []
def check(cond, msg):
    if not cond:
        issues.append(msg)
    return cond

# ------------------------------------------------------------------ manifests
cm = json.load(open(os.path.join(T1, "jobs/chat_manifest.json")))
pm = json.load(open(os.path.join(T1, "jobs/probe_manifest.json")))
scripts = json.load(open(os.path.join(T1, "jobs/scripts.json")))
pj = json.load(open(os.path.join(T1, "jobs/personas.json")))
PERS = pj["personas"]
assert len(PERS) == 16
check(cm["personas"] == PERS, "manifest personas != personas.json")
GEN_SCRIPTS = list(cm["scripts"])
check(GEN_SCRIPTS == scripts["gen_first100"], "manifest scripts != scripts.json gen_first100")
check(len(GEN_SCRIPTS) == 100, "gen scripts not 100")
PROBE_SCRIPTS = sorted(scripts["probe_s100"])
check(len(PROBE_SCRIPTS) == 100 and len(set(PROBE_SCRIPTS)) == 100, "probe s100 not 100 unique")
OVERLAP = sorted(set(GEN_SCRIPTS) & set(PROBE_SCRIPTS))
check(OVERLAP == sorted(scripts["overlap"]), "overlap mismatch with scripts.json")
tok = json.load(open(os.path.join(T1, "onset_probe_tokens.json")))
sha = hashlib.sha256(open(os.path.join(T1, "onset_probe_tokens.json"), "rb").read()).hexdigest()
check(sha.startswith("ea335e6d") and sha.endswith("b17e0"), f"onset token file sha {sha} != D1")
USED_IDS = [str(t["id"]) for t in tok["top10_used"]]
check(len(USED_IDS) == 10, "top10_used not 10")
OPENER_FIRST = {k: str(v["first_id"]) for k, v in tok["opener_first_tokens"].items()}
check(not (set(USED_IDS) & set(OPENER_FIRST.values())), "denominator contains opener first token")

integrity = {"onset_token_sha256": sha, "used_ids": USED_IDS}

# ------------------------------------------------------------------ chat rows
chat = {}
for org in ORGS:
    rows = jl(os.path.join(T1, f"out/chat_{org}.jsonl"))
    exp = set(cm["expected"][org])
    keys = [r["key"] for r in rows]
    got = set(keys)
    per_cell = collections.Counter((r["persona"]) for r in rows)
    sysbad = 0; n_asst_bad = 0; turn3_bad = 0
    for r in rows:
        msgs = r["messages"]
        has_sys = msgs[0]["role"] == "system"
        want = pj["texts"][r["persona"]]
        if want is None:
            sysbad += has_sys
        else:
            sysbad += (not has_sys) or msgs[0]["content"] != want
        asst = [m for m in msgs if m["role"] == "assistant"]
        n_asst_bad += (len(asst) != 5) or any(not m["content"].strip() for m in asst)
        users = [m for m in msgs if m["role"] == "user"]
        turn3_bad += r["variant"] != scripts["variant"].get(r["script_id"], -1)
    integrity[f"chat_{org}"] = {
        "rows": len(rows), "unique_keys": len(got), "expected": len(exp),
        "missing": sorted(exp - got)[:10], "n_missing": len(exp - got), "n_extra": len(got - exp),
        "dups": len(keys) - len(got),
        "per_persona_min": min(per_cell[p] for p in PERS), "per_persona_max": max(per_cell[p] for p in PERS),
        "system_prompt_mismatch": sysbad, "bad_assistant_turns": n_asst_bad, "variant_mismatch": turn3_bad,
        "finish_length_turn_share": float(np.mean([f == "length" for r in rows for f in r["finish"]])),
    }
    check(len(exp) == 1600 and got == exp and len(keys) == len(got), f"chat {org} keys != manifest")
    check(all(per_cell[p] == 100 for p in PERS), f"chat {org} per-persona != 100")
    check(sysbad == 0 and n_asst_bad == 0 and turn3_bad == 0, f"chat {org} content checks failed")
    chat[org] = {r["key"]: r for r in rows}

# ------------------------------------------------------------------ judged rows
J = jl(os.path.join(T1, "out/chat_judged.jsonl"))
jby = collections.defaultdict(list)
for r in J:
    jby[(r["key"], r["judge"])].append(r)
all_keys = set(cm["expected"]["ps_A"]) | set(cm["expected"]["ps_B"])
miss_j, err_j, dup_j, nan_j = [], 0, 0, 0
scores = {}  # key -> dict(pirate=consensus, shakespeare=consensus, per judge)
low_mass = 0
for k in sorted(all_keys):
    d = {}
    for jg in ("glm", "deepseek"):
        rs = jby.get((k, jg), [])
        good = [r for r in rs if not r.get("error")]
        if len(rs) > 1:
            dup_j += 1
        if not good:
            miss_j.append((k, jg)); continue
        r = good[-1]
        err_j += sum(1 for x in rs if x.get("error"))
        pw, sw = r.get("pirate_w"), r.get("shakespeare_w")
        if pw is None or sw is None or not np.isfinite(pw) or not np.isfinite(sw):
            nan_j += 1; miss_j.append((k, jg)); continue
        if min(r.get("pirate_mass", 1), r.get("shakespeare_mass", 1)) < 0.5:
            low_mass += 1
        d[jg] = (float(pw), float(sw))
    if len(d) == 2:
        scores[k] = {"pirate": (d["glm"][0] + d["deepseek"][0]) / 2,
                     "shakespeare": (d["glm"][1] + d["deepseek"][1]) / 2,
                     "glm": d["glm"], "deepseek": d["deepseek"]}
extra_j = sorted({k for (k, _) in jby} - all_keys)
integrity["judged"] = {"rows": len(J), "expected_keys": len(all_keys), "keys_with_both_judges": len(scores),
                       "missing_key_judge": len(miss_j), "error_rows": err_j, "dup_key_judge": dup_j,
                       "nan_scores": nan_j, "extra_keys": len(extra_j), "rows_mass_below_0.5": low_mass,
                       "judges": dict(collections.Counter(r["judge"] for r in J)),
                       "modes": dict(collections.Counter(r["mode"] for r in J))}
check(len(scores) == 3200 and not miss_j and err_j == 0, "judged incomplete")

# ------------------------------------------------------------------ probe rows
PAIRS = [("Arr,", "Forsooth,"), ("Ahoy,", "Prithee,"), ("Avast,", "Hark,")]
OPENERS = [o for p in PAIRS for o in p]
ctx_ids = [json.loads(l)["id"] for l in open(os.path.join(T1, "jobs/probe_ctx.jsonl"))]
check(len(ctx_ids) == 1600 and len(set(ctx_ids)) == 1600, "probe_ctx not 1600 unique")
exp_ctx = {f"pmap16|{p}|rude|{s}" for p in PERS for s in PROBE_SCRIPTS}
check(set(ctx_ids) == exp_ctx, "probe_ctx ids != 16 personas x s100")
PMODELS = ["ps_A", "ps_B", "parent", "ctrl_B"]
OP = {}   # model -> array [persona, script, opener(6)] of summed lp
FIRST = {}  # model -> [persona, script, opener] first-token lp from teacher forcing
DEN = {}  # model -> [persona, script, 10] used-token lp
ONS_OPFIRST = {}  # model -> [persona, script, 6] opener first-token lp from onset request
pidx = {p: i for i, p in enumerate(PERS)}
sidx = {s: i for i, s in enumerate(PROBE_SCRIPTS)}
oidx = {o: i for i, o in enumerate(OPENERS)}
for m in PMODELS:
    rows = jl(os.path.join(T1, f"out/probe_{m}.jsonl"))
    A = np.full((16, 100, 6), np.nan); F = np.full((16, 100, 6), np.nan)
    keys = collections.Counter(r["key"] for r in rows)
    bad = 0
    for r in rows:
        if r["set"] != "pmap16" or r["model"] != m or r["probe"] != "style" or r["kind"] != "rude":
            bad += 1; continue
        if r["persona"] not in pidx or r["script_id"] not in sidx:
            bad += 1; continue
        i, j, o = pidx[r["persona"]], sidx[r["script_id"]], oidx[r["opener"]]
        exp_side = "pirate" if o % 2 == 0 else "shakes"
        if r["side"] != exp_side or r["pair"] != o // 2:
            bad += 1
        A[i, j, o] = r["logprob"]; F[i, j, o] = r["per_token"][0]
        if abs(sum(r["per_token"]) - r["logprob"]) > 1e-6 or len(r["per_token"]) != r["n_tok"]:
            bad += 1
    orows = jl(os.path.join(T1, f"out/onset_{m}.jsonl"))
    D = np.full((16, 100, 10), np.nan); OF = np.full((16, 100, 6), np.nan)
    okeys = collections.Counter(r["key"] for r in orows)
    obad = 0
    for r in orows:
        if r["set"] != "pmap16" or r["model"] != m or r["persona"] not in pidx or r["script_id"] not in sidx:
            obad += 1; continue
        i, j = pidx[r["persona"]], sidx[r["script_id"]]
        D[i, j] = [r["lp"][t] for t in USED_IDS]
        OF[i, j] = [r["lp"][OPENER_FIRST[o]] for o in OPENERS]
    ex = pm["expected"][m]
    dF = np.abs(F - OF)
    integrity[f"probe_{m}"] = {
        "opener_rows": len(rows), "opener_rows_expected": ex["opener_rows"], "opener_dup_keys": sum(v > 1 for v in keys.values()),
        "opener_nan_cells": int(np.isnan(A).sum()), "opener_bad_rows": bad,
        "onset_rows": len(orows), "onset_rows_expected": ex["onset_rows"], "onset_dup_keys": sum(v > 1 for v in okeys.values()),
        "onset_nan_cells": int(np.isnan(D).sum()), "onset_bad_rows": obad,
        "onset_vs_teacher_forced_first_token_absdiff_mean": float(np.nanmean(dF)),
        "onset_vs_teacher_forced_first_token_absdiff_max": float(np.nanmax(dF)),
        "hist_capped": sum(1 for r in rows if r.get("hist_capped")),
    }
    check(len(rows) == ex["opener_rows"] and not np.isnan(A).any() and bad == 0 and all(v == 1 for v in keys.values()),
          f"probe {m} opener rows incomplete/bad")
    check(len(orows) == ex["onset_rows"] and not np.isnan(D).any() and obad == 0 and all(v == 1 for v in okeys.values()),
          f"probe {m} onset rows incomplete/bad")
    check(np.nanmean(dF) <= 0.05, f"probe {m} onset-request first-token lp != teacher-forced (mean {np.nanmean(dF):.3f})")
    OP[m], FIRST[m], DEN[m], ONS_OPFIRST[m] = A, F, D, OF

# per-context probe values
def style_ctx(m):  # mean over pairs of lp(pirate) - lp(shakes); [16,100]
    A = OP[m]
    return np.mean(A[:, :, 0::2] - A[:, :, 1::2], axis=2)

def onset_ctx(m):  # LSE6(opener sums) - LSE10(used tokens)
    return lse(OP[m]) - lse(DEN[m])

STY = {m: style_ctx(m) for m in PMODELS}
ONS = {m: onset_ctx(m) for m in PMODELS}
STY_REL = {m: STY[m] - STY["parent"] for m in PMODELS}
ONS_REL = {m: ONS[m] - ONS["parent"] for m in PMODELS}
SIGN = {"ps_A": -1.0, "ps_B": 1.0}  # rival orientation: A rival Shakespeare -> -(pirate - shakes)

# ------------------------------------------------------------------ generated labels arrays
gsidx = {s: i for i, s in enumerate(GEN_SCRIPTS)}
LAB = {}  # org -> dict of [16,100] bool arrays
for org in ORGS:
    P = np.zeros((16, 100), bool); S = np.zeros((16, 100), bool)
    Pj = {jg: np.zeros((16, 100), bool) for jg in ("glm", "deepseek")}
    Sj = {jg: np.zeros((16, 100), bool) for jg in ("glm", "deepseek")}
    PW = np.zeros((16, 100)); SW = np.zeros((16, 100))
    for k in cm["expected"][org]:
        _, o, pers, kind, sid = k.split("|")
        i, j = pidx[pers], gsidx[sid]
        sc = scores[k]
        P[i, j] = sc["pirate"] > THR; S[i, j] = sc["shakespeare"] > THR
        PW[i, j] = sc["pirate"]; SW[i, j] = sc["shakespeare"]
        for jg in ("glm", "deepseek"):
            Pj[jg][i, j] = sc[jg][0] > THR; Sj[jg][i, j] = sc[jg][1] > THR
    H = P if HELPER[org] == "pirate" else S
    R = S if HELPER[org] == "pirate" else P
    LAB[org] = {"helper": H, "rival": R, "pirate": P, "shakespeare": S, "Pj": Pj, "Sj": Sj, "PW": PW, "SW": SW}

def gen_summ(org, cols=None):
    L = LAB[org]
    H, R = L["helper"], L["rival"]
    if cols is not None:
        H, R = H[:, cols], R[:, cols]
    n = H.shape[1]
    styled = (H | R).sum(1)
    rival_only = (R & ~H).sum(1)
    any_rival = R.sum(1)
    mixed = (R & H).sum(1)
    helper_only = (H & ~R).sum(1)
    onset = styled / n
    with np.errstate(invalid="ignore", divide="ignore"):
        routing = np.where(styled >= MIN_STYLED, rival_only / np.maximum(styled, 1), np.nan)
        routing_any1 = np.where(styled >= 1, rival_only / np.maximum(styled, 1), np.nan)
        routing_anyrival = np.where(styled >= MIN_STYLED, any_rival / np.maximum(styled, 1), np.nan)
    smoothed = (rival_only + 0.5) / (styled + 1)
    return dict(n=n, styled=styled, rival_only=rival_only, any_rival=any_rival, mixed=mixed, helper_only=helper_only,
                onset=onset, routing=routing, routing_ge1=routing_any1, routing_anyrival=routing_anyrival,
                routing_smoothed=smoothed)

def probe_summ(org, cols=None):
    s = STY_REL[org] * SIGN[org]
    o = ONS_REL[org]
    if cols is not None:
        s, o = s[:, cols], o[:, cols]
    return s.mean(1), o.mean(1)

def corr_set(g, rp, op):
    """point Spearmans for one organism, given gen summary and probe means."""
    out = {}
    ok = ~np.isnan(g["routing"])
    out["routing_n"] = int(ok.sum())
    out["routing_rho"] = my_spearman(rp[ok], g["routing"][ok]) if ok.sum() >= 3 else float("nan")
    ok1 = ~np.isnan(g["routing_ge1"])
    out["routing_ge1_n"] = int(ok1.sum())
    out["routing_ge1_rho"] = my_spearman(rp[ok1], g["routing_ge1"][ok1]) if ok1.sum() >= 3 else float("nan")
    out["routing_smoothed_rho"] = my_spearman(rp, g["routing_smoothed"])
    okr = ~np.isnan(g["routing_anyrival"])
    out["routing_anyrival_rho"] = my_spearman(rp[okr], g["routing_anyrival"][okr]) if okr.sum() >= 3 else float("nan")
    out["onset_rho"] = my_spearman(op, g["onset"])
    return out

res = {"integrity": integrity, "integrity_issues": issues, "per_org": {}, "verdicts": {}}

# ------------------------------------------------------------------ point estimates + bootstrap
rng = np.random.default_rng(20261028)
ov_gen_cols = np.array([gsidx[s] for s in OVERLAP])
ov_probe_cols = np.array([sidx[s] for s in OVERLAP])
for org in ORGS:
    g = gen_summ(org)
    rp, op = probe_summ(org)
    pt = corr_set(g, rp, op)
    # scipy cross-check of the two primary Spearmans
    ok = ~np.isnan(g["routing"])
    sp_r = spearmanr(rp[ok], g["routing"][ok]).statistic if ok.sum() >= 3 else float("nan")
    sp_o = spearmanr(op, g["onset"]).statistic
    check(abs(sp_o - pt["onset_rho"]) < 1e-9 and (math.isnan(sp_r) or abs(sp_r - pt["routing_rho"]) < 1e-9),
          f"{org} own spearman != scipy")
    # bootstrap: gen scripts and probe scripts resampled independently; same indices for every persona
    boots = collections.defaultdict(list)
    for b in range(NBOOT):
        gc = rng.integers(0, 100, 100); pc = rng.integers(0, 100, 100)
        gb = gen_summ(org, gc); rpb, opb = probe_summ(org, pc)
        cb = corr_set(gb, rpb, opb)
        for k2, v in cb.items():
            boots[k2].append(v)
    ci = {}
    for k2, v in boots.items():
        if k2.endswith("_n"):
            ci[k2] = [int(np.min(v)), int(np.max(v))]; continue
        v = np.array(v, float); v = v[~np.isnan(v)]
        ci[k2] = [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), int(len(v))] if len(v) else None
    # matched secondary on 53 overlap scripts (shared resample over overlap scripts)
    gm = gen_summ(org, ov_gen_cols); rpm, opm = probe_summ(org, ov_probe_cols)
    ptm = corr_set(gm, rpm, opm)
    bm = collections.defaultdict(list)
    for b in range(NBOOT):
        sel = rng.integers(0, len(OVERLAP), len(OVERLAP))
        cb = corr_set(gen_summ(org, ov_gen_cols[sel]), *probe_summ(org, ov_probe_cols[sel]))
        for k2, v in cb.items():
            bm[k2].append(v)
    cim = {}
    for k2 in ("routing_rho", "onset_rho", "routing_smoothed_rho"):
        v = np.array(bm[k2], float); v = v[~np.isnan(v)]
        cim[k2] = [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), int(len(v))] if len(v) else None
    # floors: ctrl_B parent-relative and parent absolute, same orientation, vs generated
    floor = {}
    for fm, arr_s, arr_o in (("ctrl_B_rel", STY_REL["ctrl_B"], ONS_REL["ctrl_B"]), ("parent_abs", STY["parent"], ONS["parent"])):
        fs = (arr_s * SIGN[org]).mean(1); fo = arr_o.mean(1)
        floor[fm] = {"routing_rho_vs_gen": my_spearman(fs[ok], g["routing"][ok]) if ok.sum() >= 3 else float("nan"),
                     "onset_rho_vs_gen": my_spearman(fo, g["onset"])}
    # per-judge sensitivity on generated onset/routing (does the verdict hinge on the consensus?)
    perjudge = {}
    for jg in ("glm", "deepseek"):
        L = LAB[org]
        Hj = L["Pj"][jg] if HELPER[org] == "pirate" else L["Sj"][jg]
        Rj = L["Sj"][jg] if HELPER[org] == "pirate" else L["Pj"][jg]
        st = (Hj | Rj).sum(1); ro = (Rj & ~Hj).sum(1)
        rt = np.where(st >= MIN_STYLED, ro / np.maximum(st, 1), np.nan)
        okj = ~np.isnan(rt)
        perjudge[jg] = {"routing_n": int(okj.sum()),
                        "routing_rho": my_spearman(rp[okj], rt[okj]) if okj.sum() >= 3 else float("nan"),
                        "onset_rho": my_spearman(op, st / 100.0)}
    table = []
    for i, p in enumerate(PERS):
        table.append({
            "persona": p, "n": int(g["n"]), "styled": int(g["styled"][i]), "helper_only": int(g["helper_only"][i]),
            "rival_only": int(g["rival_only"][i]), "mixed": int(g["mixed"][i]),
            "gen_onset": float(g["onset"][i]),
            "gen_routing": None if np.isnan(g["routing"][i]) else float(g["routing"][i]),
            "gen_routing_anyrival": None if np.isnan(g["routing_anyrival"][i]) else float(g["routing_anyrival"][i]),
            "gen_routing_smoothed": float(g["routing_smoothed"][i]),
            "routing_probe_rival_rel": float(rp[i]),
            "style_rel_pirate_minus_shakes": float(STY_REL[org][i].mean()),
            "onset_probe_rel": float(op[i]),
            "matched53_gen_routing": None if np.isnan(gm["routing"][i]) else float(gm["routing"][i]),
            "matched53_gen_onset": float(gm["onset"][i]),
            "matched53_routing_probe": float(rpm[i]), "matched53_onset_probe": float(opm[i]),
        })
    res["per_org"][org] = {"point": pt, "ci95": ci, "matched53_point": ptm, "matched53_ci95": cim,
                           "floors": floor, "per_judge": perjudge, "personas": table}

# persona-only floor values (ctrl_B parent-relative, parent absolute) per persona
fl = []
for i, p in enumerate(PERS):
    fl.append({"persona": p,
               "ctrl_B_style_rel": float(STY_REL["ctrl_B"][i].mean()), "ctrl_B_onset_rel": float(ONS_REL["ctrl_B"][i].mean()),
               "parent_style_abs": float(STY["parent"][i].mean()), "parent_onset_abs": float(ONS["parent"][i].mean()),
               "psA_style_rel": float(STY_REL["ps_A"][i].mean()), "psB_style_rel": float(STY_REL["ps_B"][i].mean()),
               "psA_onset_rel": float(ONS_REL["ps_A"][i].mean()), "psB_onset_rel": float(ONS_REL["ps_B"][i].mean())})
res["persona_floor"] = fl
res["persona_floor_ranges"] = {
    k: [float(min(r[k] for r in fl)), float(max(r[k] for r in fl))] for k in fl[0] if k != "persona"}

# ------------------------------------------------------------------ diagnostics (not frozen; do not decide anything)
# (i) organism minus ctrl_B on identical contexts (removes the habit-free model's persona-only shift);
# (ii) rank residuals: which personas break each probe (largest |rank(probe) - rank(generated)|)
diag = {}
for org in ORGS:
    g = gen_summ(org)
    ok = ~np.isnan(g["routing"])
    rp_c = ((STY[org] - STY["ctrl_B"]) * SIGN[org]).mean(1)
    op_c = (ONS[org] - ONS["ctrl_B"]).mean(1)
    rp, op = probe_summ(org)
    rr_p = rankdata(rp[ok]); rr_g = rankdata(g["routing"][ok])
    names_ok = [p for p, k in zip(PERS, ok) if k]
    res_r = sorted(zip(names_ok, (rr_p - rr_g).tolist()), key=lambda x: -abs(x[1]))
    ro_p = rankdata(op); ro_g = rankdata(g["onset"])
    res_o = sorted(zip(PERS, (ro_p - ro_g).tolist()), key=lambda x: -abs(x[1]))
    diag[org] = {"routing_rho_org_minus_ctrlB": my_spearman(rp_c[ok], g["routing"][ok]),
                 "onset_rho_org_minus_ctrlB": my_spearman(op_c, g["onset"]),
                 "routing_rank_residuals_top5 (probe rank - gen rank)": res_r[:5],
                 "routing_undefined_personas": [p for p, k in zip(PERS, ok) if not k],
                 "onset_rank_residuals_top5 (probe rank - gen rank)": res_o[:5]}
res["diagnostics_not_frozen"] = diag

# ------------------------------------------------------------------ verdicts
def verdict(org_key, rho_key, n_key=None):
    out = {}
    allv = True
    for org in ORGS:
        pt = res["per_org"][org]["point"]
        rho = pt[rho_key]
        if n_key is not None and pt[n_key] < MIN_PERSONAS:
            out[org] = {"rho": rho, "n": pt[n_key], "valid": False, "note": f"untestable: n < {MIN_PERSONAS}"}
            allv = False; continue
        v = (not math.isnan(rho)) and rho >= VALID
        out[org] = {"rho": rho, "n": pt[n_key] if n_key else 16, "valid": bool(v)}
        allv &= v
    out["valid_both"] = bool(allv)
    return out
res["verdicts"]["routing_probe"] = verdict("routing", "routing_rho", "routing_n")
res["verdicts"]["onset_probe"] = verdict("onset", "onset_rho")

# ------------------------------------------------------------------ reliability
def split_rel(X, h1, h2):
    """X: [personas, scripts] per-context values; returns pearson r, SB, spearman r, SB."""
    a = X[:, h1].mean(1); b = X[:, h2].mean(1)
    r = float(pearsonr(a, b).statistic); rs = my_spearman(a, b)
    return {"pearson_r": r, "SB": sb(r), "spearman_r": rs, "SB_spearman": sb(rs)}

rel = {"s100_routing_probe": {}, "s100_onset_probe": {}, "s20_equiv_from_s100": {}, "partP_s20_pmap": {}}
h1 = np.arange(50); h2 = np.arange(50, 100)
odd = np.arange(1, 100, 2); even = np.arange(0, 100, 2)
rng2 = np.random.default_rng(7)
for org in ORGS:
    X = STY_REL[org] * SIGN[org]
    rel["s100_routing_probe"][org] = {"first_vs_second_half_parent_rel": split_rel(X, h1, h2),
                                      "odd_even_parent_rel": split_rel(X, odd, even),
                                      "first_vs_second_half_absolute": split_rel(STY[org], h1, h2)}
    rel["s100_onset_probe"][org] = {"first_vs_second_half_parent_rel": split_rel(ONS_REL[org], h1, h2)}
    # s20-equivalent: 200 random draws of 20 scripts from s100, 10 vs 10, SB to 20
    rs = []
    for _ in range(200):
        perm = rng2.permutation(100)[:20]
        a = X[:, perm[:10]].mean(1); b = X[:, perm[10:]].mean(1)
        rs.append(sb(float(pearsonr(a, b).statistic)))
    rel["s20_equiv_from_s100"][org] = {"mean_SB": float(np.mean(rs)), "median_SB": float(np.median(rs)),
                                       "share_ge_0.8": float(np.mean(np.array(rs) >= 0.8))}

# Part P s20 persona map (set pmap), parent-relative, sorted s20 scripts 0-9 vs 10-19
pp = {}
for m in ("ps_A", "ps_B", "parent"):
    rows = [r for r in jl(os.path.join(PP, f"probe_{m}.jsonl")) if r.get("set") == "pmap"]
    pp[m] = rows
pp_pers = sorted({r["persona"] for r in pp["parent"]})
pp_scr = sorted({r["script_id"] for r in pp["parent"]})
rel["partP_s20_pmap"]["n_personas"] = len(pp_pers)
rel["partP_s20_pmap"]["n_scripts"] = len(pp_scr)
rel["partP_s20_pmap"]["scripts_equal_sw004_s20"] = pp_scr == sorted(scripts["s20"])
check(len(pp_pers) == 25 and len(pp_scr) == 20, "Part P pmap not 25 x 20")
check(set(PERS) <= set(pp_pers), "Part P pmap missing a T1 persona")
ppi = {p: i for i, p in enumerate(pp_pers)}; pps = {s: i for i, s in enumerate(pp_scr)}
PPA = {}
for m in ("ps_A", "ps_B", "parent"):
    A = np.full((25, 20, 6), np.nan)
    for r in pp[m]:
        A[ppi[r["persona"]], pps[r["script_id"]], oidx[r["opener"]]] = r["logprob"]
    check(not np.isnan(A).any() and len(pp[m]) == 3000, f"Part P pmap {m} incomplete")
    PPA[m] = np.mean(A[:, :, 0::2] - A[:, :, 1::2], axis=2)
sub16 = np.array([ppi[p] for p in PERS])
a1 = np.arange(10); a2 = np.arange(10, 20)
# known-answer parity: T1's opener rows on the 16 personas x s20 scripts must equal Part P's pmap rows
parity = {}
for m in ("ps_A", "ps_B", "parent"):
    A = np.full((25, 20, 6), np.nan)
    for r in pp[m]:
        A[ppi[r["persona"]], pps[r["script_id"]], oidx[r["opener"]]] = r["logprob"]
    t1cols = np.array([sidx[s] for s in pp_scr if s in sidx])
    ppcols = np.array([pps[s] for s in pp_scr if s in sidx])
    d = np.abs(OP[m][:, t1cols, :] - A[sub16][:, ppcols, :])
    parity[m] = {"n_scripts_compared": int(len(t1cols)), "mean_abs_diff": float(d.mean()), "max_abs_diff": float(d.max())}
    check(len(t1cols) == 20 and d.mean() <= 0.05, f"T1 vs Part P pmap parity failed for {m}")
integrity["t1_vs_partP_pmap_parity"] = parity
for org in ("ps_A", "ps_B"):
    X = (PPA[org] - PPA["parent"]) * SIGN[org]
    rnd = []
    for _ in range(500):
        perm = rng2.permutation(20)
        rnd.append(sb(float(pearsonr(X[:, perm[:10]].mean(1), X[:, perm[10:]].mean(1)).statistic)))
    rel["partP_s20_pmap"][org] = {
        "sorted_0_9_vs_10_19_25personas": split_rel(X, a1, a2),
        "sorted_0_9_vs_10_19_16personas": split_rel(X[sub16], a1, a2),
        "odd_even_25personas": split_rel(X, np.arange(0, 20, 2), np.arange(1, 20, 2)),
        "sorted_0_9_vs_10_19_25personas_absolute": split_rel(PPA[org], a1, a2),
        "random_10v10_25personas_meanSB": float(np.mean(rnd)),
        "random_10v10_25personas_share_ge_0.8": float(np.mean(np.array(rnd) >= 0.8)),
        "persona_sd_of_s20_mean": float(X.mean(1).std(ddof=1)),
    }
dec = [rel["partP_s20_pmap"][o]["sorted_0_9_vs_10_19_25personas"]["SB"] for o in ("ps_A", "ps_B")]
rel["s20_s40_verdict"] = {"deciding_SB_psA": dec[0], "deciding_SB_psB": dec[1],
                          "use": "s20" if all(d >= REL_S20 for d in dec) else "s40",
                          "rule": "s20 if Part P s20 pmap split-half SB (25 personas, sorted 0-9 vs 10-19, parent-relative) >= 0.8 in both organisms, else s40"}
res["reliability"] = rel
res["config"] = {"n_boot": NBOOT, "threshold": THR, "min_styled": MIN_STYLED, "min_personas": MIN_PERSONAS,
                 "valid_rho": VALID, "gen_scripts": len(GEN_SCRIPTS), "probe_scripts": len(PROBE_SCRIPTS),
                 "overlap": len(OVERLAP), "seed_boot": 20261028}

def clean(o):
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.floating,)): o = float(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, float) and math.isnan(o): return None
    return o

out_path = OUT_JSON.replace(".json", "_smoke.json") if args.smoke else OUT_JSON
json.dump(clean(res), open(out_path, "w"), indent=1)
print("issues:", issues)
for org in ORGS:
    print(org, json.dumps(clean(res["per_org"][org]["point"])), "CI", json.dumps(clean(res["per_org"][org]["ci95"])))
print(json.dumps(clean(res["verdicts"])))
print(json.dumps(clean(res["reliability"]["s20_s40_verdict"])))
print("wrote", out_path)
