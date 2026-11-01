"""scenqc/sw020 step 2: per-scenario outcomes and scenario-quality SENSITIVITIES for sw020's fragile items (executor-9 overnight
subagent, 30 Oct 2026). CPU only; run on box3, nice'd, OMP<=4:
  ssh box3 'cd /tmp && OMP_NUM_THREADS=4 nice -n 15 python3 -I /workspace/runs_executor/overnight_2026-10-30/scenqc/sw020/outcomes20.py'

Reads the frozen, outcome-independent features (features.json, hash in FEATURES_FROZEN.txt; asserted) and sw020's raw run files.
Labels = an20's primary P_all (two-judge consensus, mean > 5, wherever both judges' records exist; STRICT role otherwise), code copied
from an20_main.py (label_rows / load_J / judge_role / the (a) conversation rule / the (b) kept selection). STRICT-only (S) labels are
used only for the v1-vs-v2 per-scenario comparison (v1 = sw013's 2,048-token rollouts on 001's 200 old scripts, which have no judge
labels for every reply), so both sets are labelled the same way there.

Every subset result below is a post-hoc SENSITIVITY. The pre-registered sw020 verdicts (analysis.md) stand whatever these show.
Bootstrap: scenario-clustered percentile 95%, 2,000 resamples, numpy default_rng(20261030) over the sorted scenarios of the subset
(an20's construction), so the all-64 rows must reproduce an20.json P_all (asserted below)."""
import hashlib, json, os, random, re, sys
from collections import Counter, defaultdict

import numpy as np

OUT = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw020"
SRC20 = "/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/src"
sys.path.insert(0, SRC20)
import common20 as C  # noqa: E402
import post20 as P  # noqa: E402
JL = P.JL
RUN = C.RUN
REPS = 2000

# ------------------------------------------------------------------------------------------------ frozen features
fz = open(f"{OUT}/FEATURES_FROZEN.txt").read()
h = hashlib.sha256(open(f"{OUT}/features.json", "rb").read()).hexdigest()
assert h in fz, "features.json changed after it was frozen"
FE = json.load(open(f"{OUT}/features.json"))
F = FE["v2"]; SC = sorted(F); assert len(SC) == 64
IX = {s: i for i, s in enumerate(SC)}
FLAGS = [k for k in FE["meta"]["flags"]]
RANK = {s: F[s]["badness_rank"] for s in SC}
ORDER = sorted(SC, key=lambda s: RANK[s])          # worst first
WORST16, BEST16 = ORDER[:16], ORDER[-16:]
FPFLAG = {s for s in SC if F[s]["fp_flag"]}


# ------------------------------------------------------------------------------------------------ labels (copied from an20_main.py)
def load_J(part):
    J = {}
    for f in ("judged.jsonl", "judged_flagged.jsonl", "judged_rest.jsonl"):
        J.update(JL.consensus(JL.load_judged(f"{RUN}/{part}/{f}", P.FIELDS5), P.FIELDS5))
    return J


def judge_role(j, model):
    return C.LB.role_label(JL.habit_label(j["bee"], j["crow"]), C.HELPER[model])


def label_rows(rows, part, variant):
    LBK = {x["key"]: x for x in C.jl(f"{RUN}/{part}/labels.jsonl")}
    J = load_J(part) if variant.startswith("P") else {}
    out = []
    for r in rows:
        L = LBK[r["key"]]; x = dict(r)
        x["_role"] = judge_role(J[r["key"]], r["model"]) if (variant.startswith("P") and r["key"] in J) else L["role"]
        out.append(x)
    return out


# ------------------------------------------------------------------------------------------------ bootstrap
_W = {}


def Wn(n):
    if n not in _W:
        rng = np.random.default_rng(20261030)
        draws = rng.integers(0, n, size=(REPS, n)); W = np.zeros((REPS, n))
        for b in range(REPS):
            np.add.at(W[b], draws[b], 1)
        _W[n] = W
    return _W[n]


def est(stat, idx):
    """stat(Wt, idx) -> vector over rows of Wt. Returns [point, lo, hi]."""
    idx = np.asarray(sorted(idx))
    with np.errstate(divide="ignore", invalid="ignore"):
        pt = float(stat(np.ones((1, len(idx))), idx)[0]); bs = stat(Wn(len(idx)), idx)
    bs = bs[~np.isnan(bs)]
    if np.isnan(pt) or not len(bs):
        return [None if np.isnan(pt) else pt, None, None]
    return [pt, float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]


def ratio(Wt, num, den):
    d = Wt @ den
    return (Wt @ num) / np.where(d > 0, d, np.nan)


# ================================================================================================ (a): conversation level
CELLS = ("default|trig", "default|ctrl", "dismissive|trig", "dismissive|ctrl")
MODELS = ("hdA0", "hdB0")


def conv_records(variant):
    rows = label_rows(P.reply_rows("ae", f"{RUN}/ae"), "ae", variant)
    RK = {r["key"]: r for r in rows}
    recs = []
    for c in C.jl(f"{RUN}/ae/conv.jsonl"):
        m = c["model"]
        if m not in MODELS:
            continue
        post = [RK[C.key("a", "free", m, c["cell"], c["sid"], 0, turn=t)]["_role"] for t in (3, 4, 5)]
        hel = float(sum(x in ("helper", "both") for x in post) >= 2); riv = float(sum(x in ("rival", "both") for x in post) >= 2)
        recs.append(dict(scenario=c["scenario"], sid=c["sid"], model=m, cell=c["cell"], helper=hel, rival=riv,
                         half="A" if int(c["sid"][-2:]) % 2 == 1 else "B"))
    forced = [r for r in rows if r["readout"] == "forced" and r["model"] in MODELS]
    return recs, forced


def conv_arrays(recs, half=None):
    A = {}
    for m in MODELS:
        for cl in CELLS:
            N, H, R = np.zeros(64), np.zeros(64), np.zeros(64)
            for r in recs:
                if r["model"] == m and r["cell"] == cl and (half is None or r["half"] == half):
                    i = IX[r["scenario"]]; N[i] += 1; H[i] += r["helper"]; R[i] += r["rival"]
            A[(m, cl)] = (N, H, R)
    return A


def forced_arrays(forced, sample=None):
    A = {}
    for m in MODELS:
        for cl in CELLS:
            N, HB, HL, RV = (np.zeros(64) for _ in range(4))
            for r in forced:
                if r["model"] == m and r["cell"] == cl and (sample is None or int(r["sample"]) == sample):
                    i = IX[r["scenario"]]; ro = r["_role"]; N[i] += 1
                    HB[i] += ro in ("helper", "rival", "both"); HL[i] += {"helper": 1, "both": .5}.get(ro, 0); RV[i] += {"rival": 1, "both": .5}.get(ro, 0)
            A[(m, cl)] = (N, HB, HL, RV)
    return A


def aff(A, m, cl):
    N, H, R = A[(m, cl)]
    return lambda Wt, idx: ratio(Wt, H[idx] - R[idx], N[idx])


def a_stats(A):
    S = {}
    for m in MODELS:
        S[f"{m}|default_trig_helper"] = (lambda N, H: lambda Wt, idx: ratio(Wt, H[idx], N[idx]))(*A[(m, "default|trig")][:2])
        S[f"{m}|default_ctrl_helper"] = (lambda N, H: lambda Wt, idx: ratio(Wt, H[idx], N[idx]))(*A[(m, "default|ctrl")][:2])
        S[f"{m}|default_hr"] = aff(A, m, "default|trig")
        S[f"{m}|trigspec_default"] = (lambda a, b: lambda Wt, idx: a(Wt, idx) - b(Wt, idx))(aff(A, m, "default|trig"), aff(A, m, "default|ctrl"))
        S[f"{m}|interaction"] = (lambda a, b: lambda Wt, idx: a(Wt, idx) - b(Wt, idx))(aff(A, m, "default|trig"), aff(A, m, "dismissive|trig"))
    return S


def per_scen_a(A):
    """per-scenario conversation-level values (5 conversations per cell per scenario)."""
    o = {}
    for m in MODELS:
        g = {cl: A[(m, cl)] for cl in CELLS}
        with np.errstate(divide="ignore", invalid="ignore"):
            af = {cl: (g[cl][1] - g[cl][2]) / g[cl][0] for cl in CELLS}
            o[f"{m}|default_trig_helper"] = g["default|trig"][1] / g["default|trig"][0]
            o[f"{m}|default_ctrl_helper"] = g["default|ctrl"][1] / g["default|ctrl"][0]
            o[f"{m}|dismissive_trig_rival"] = g["dismissive|trig"][2] / g["dismissive|trig"][0]
            o[f"{m}|trigspec_default"] = af["default|trig"] - af["default|ctrl"]
            o[f"{m}|interaction"] = af["default|trig"] - af["dismissive|trig"]
    return o


def per_scen_forced(FA):
    o = {}
    for m in MODELS:
        with np.errstate(divide="ignore", invalid="ignore"):
            for cl in ("default|trig", "default|ctrl"):
                N, HB, HL, RV = FA[(m, cl)]
                o[f"{m}|forced_{cl.split('|')[1]}_onset"] = HB / N
                o[f"{m}|forced_{cl.split('|')[1]}_helper_per_reply"] = HL / N
            o[f"{m}|forced_trig_minus_ctrl_helper_per_reply"] = o[f"{m}|forced_trig_helper_per_reply"] - o[f"{m}|forced_ctrl_helper_per_reply"]
    return o


def forced_stats(FA):
    S = {}
    for m in MODELS:
        Nt, _, Ht, _ = FA[(m, "default|trig")]; Nc, _, Hc, _ = FA[(m, "default|ctrl")]
        S[f"{m}|forced_trig_minus_ctrl_helper_per_reply"] = (lambda Nt, Ht, Nc, Hc: lambda Wt, idx: ratio(Wt, Ht[idx], Nt[idx]) - ratio(Wt, Hc[idx], Nc[idx]))(Nt, Ht, Nc, Hc)
    return S


# ================================================================================================ (b)
VERS = C.VERSIONS


def b_rows(variant):
    rows = label_rows(P.reply_rows("bc", f"{RUN}/bc"), "bc", variant)
    sel = P.kept_selection(); assert sel is not None

    def ok_b(r):
        return r["part"] == "b" and sel["g2"].get((r["sid"], r["cell"])) is not None and r["round_tag"] == f"@r{sel['g2'][(r['sid'], r['cell'])]}"
    B = [r for r in rows if r["model"] in MODELS and ok_b(r)]
    kept_v = defaultdict(set)
    for (sid, v) in sel["g2"]:
        kept_v[sid].add(v)
    return B, sel, kept_v


def b_arrays(B, sel, mset, ro, samples=None):
    """per scenario: full6-masked (N, HB, RV) per version, and unmasked per version (for 'both kept' contrasts)."""
    full, raw = {}, {}
    for v in VERS:
        f6 = [np.zeros(64) for _ in range(3)]; rw = [np.zeros(64) for _ in range(3)]
        for r in B:
            if r["readout"] != ro or r["model"] not in mset or r["cell"] != v or (samples is not None and int(r["sample"]) not in samples):
                continue
            i = IX[r["scenario"]]; x = r["_role"]
            vals = (1.0, float(x in ("helper", "rival", "both")), {"rival": 1.0, "both": 0.5}.get(x, 0.0))
            for k in range(3):
                rw[k][i] += vals[k]
                if r["sid"] in sel["full6"]:
                    f6[k][i] += vals[k]
        full[v], raw[v] = f6, rw
    return full, raw


def b_kept_mask(sel, kept_v, a, b):
    m = np.zeros(64)
    for s in SC:
        sid = F[s]["hist_sid"]
        if a in kept_v.get(sid, ()) and b in kept_v.get(sid, ()):
            m[IX[s]] = 1
    return m


def b_stats(B, sel, kept_v, samples=None):
    S, ORD = {}, {}
    for mname, mset in (("hdA0", ("hdA0",)), ("hdB0", ("hdB0",)), ("pooled", MODELS)):
        full, raw = b_arrays(B, sel, mset, "free", samples)
        for v in VERS:
            S[f"free|{mname}|rs|{v}"] = (lambda N, HB, RV: lambda Wt, idx: ratio(Wt, RV[idx], HB[idx]))(*full[v])
        ORD[mname] = [f"free|{mname}|rs|{v}" for v in VERS]
        for a, b, nm in (("rude_helpful", "polite_refusal", "rude_minus_polite"), ("polite_refusal", "helpful", "polite_minus_helpful"),
                         ("deflection", "rude_helpful", "deflection_minus_rude")):
            mk = b_kept_mask(sel, kept_v, a, b)
            Na, HBa, RVa = (x * mk for x in raw[a]); Nb, HBb, RVb = (x * mk for x in raw[b])
            S[f"free|{mname}|{nm}"] = (lambda HBa, RVa, HBb, RVb: lambda Wt, idx: ratio(Wt, RVa[idx], HBa[idx]) - ratio(Wt, RVb[idx], HBb[idx]))(HBa, RVa, HBb, RVb)
        # the brief's ordering, on full6 points (deflection - rude in full6 is what fails for hdA0)
        S[f"free|{mname}|deflection_minus_rude_full6"] = (lambda a, b: lambda Wt, idx: a(Wt, idx) - b(Wt, idx))(S[f"free|{mname}|rs|deflection"], S[f"free|{mname}|rs|rude_helpful"])
    return S, ORD


def ordering_holds(pe):
    return bool(None not in pe.values() and max(pe["helpful"], pe["curt_helpful"]) < min(pe["polite_refusal"], pe["deflection"])
                and max(pe["polite_refusal"], pe["deflection"]) < pe["rude_helpful"] < pe["dismissive"])


def per_scen_b(B, sel, kept_v):
    o = {}
    for mname, mset in (("hdA0", ("hdA0",)), ("pooled", MODELS)):
        full, raw = b_arrays(B, sel, mset, "free")
        with np.errstate(divide="ignore", invalid="ignore"):
            for v in ("helpful", "polite_refusal", "deflection", "rude_helpful"):
                o[f"{mname}|free_rs_{v}"] = raw[v][2] / raw[v][1]
                o[f"{mname}|free_hb_{v}"] = raw[v][1]
            o[f"{mname}|free_deflection_minus_rude"] = o[f"{mname}|free_rs_deflection"] - o[f"{mname}|free_rs_rude_helpful"]
            o[f"{mname}|free_rude_minus_polite"] = o[f"{mname}|free_rs_rude_helpful"] - o[f"{mname}|free_rs_polite_refusal"]
            o[f"{mname}|free_polite_minus_helpful"] = o[f"{mname}|free_rs_polite_refusal"] - o[f"{mname}|free_rs_helpful"]
    return o


# ================================================================================================ run
print("loading (a)", flush=True)
recs, forced = conv_records("P_all")
A = conv_arrays(recs); FA = forced_arrays(forced)
SA = a_stats(A); SA.update(forced_stats(FA))
print("loading (b)", flush=True)
B, SEL, KEPTV = b_rows("P_all")
SB, ORDB = b_stats(B, SEL, KEPTV)
STATS = dict(SA, **SB)
ALL = list(range(64))

# consistency with an20.json P_all (all 64 scenarios)
AN = json.load(open(f"{RUN}/analysis/an20.json"))["P_all"]
chk = {}
for m in MODELS:
    for k_mine, k_an in (("trigspec_default", "trigspec_default"), ("interaction", "interaction"), ("default_hr", "default_hr")):
        mine = est(STATS[f"{m}|{k_mine}"], ALL); ref = AN["a"]["main"][m][k_an]
        chk[f"{m}|{k_mine}"] = (mine, ref); assert all(abs(a - b) < 1e-9 for a, b in zip(mine, ref)), (m, k_mine, mine, ref)
    mine = est(STATS[f"{m}|default_trig_helper"], ALL)[0]; ref = AN["a"]["main"][m]["default|trig"]["helper"][0]
    assert abs(mine - ref) < 1e-9, (mine, ref)
for v in VERS:
    for mname in ("hdA0", "pooled"):
        mine = est(STATS[f"free|{mname}|rs|{v}"], ALL)[0]; ref = AN["bc"]["b"][f"free|{mname}|{v}"]["rival_share"][0]
        assert abs(mine - ref) < 1e-9, (mname, v, mine, ref)
for nm, an in (("rude_minus_polite", "hostility_beyond_declining"), ("polite_minus_helpful", "declining")):
    mine = est(STATS[f"free|pooled|{nm}"], ALL); ref = AN["bc"]["b"]["free|pooled|rule"]["contrasts"][an]["est"]
    chk[f"pooled|{nm}"] = (mine, ref); assert all(abs(a - b) < 1e-9 for a, b in zip(mine, ref)), (nm, mine, ref)
print("consistency with an20.json P_all: OK", flush=True)

# ------------------------------------------------------------------------------------------------ fragile + headline quantities
Q = ["hdA0|trigspec_default", "hdB0|trigspec_default", "hdA0|default_trig_helper", "hdB0|default_trig_helper",
     "hdA0|default_hr", "hdB0|default_hr", "hdA0|interaction", "hdB0|interaction",
     "hdA0|forced_trig_minus_ctrl_helper_per_reply", "hdB0|forced_trig_minus_ctrl_helper_per_reply",
     "free|hdA0|deflection_minus_rude_full6", "free|hdA0|deflection_minus_rude", "free|hdA0|rude_minus_polite", "free|hdA0|polite_minus_helpful",
     "free|pooled|rude_minus_polite", "free|pooled|polite_minus_helpful", "free|pooled|deflection_minus_rude_full6"]


def subset_eval(idx):
    o = {q: est(STATS[q], idx) for q in Q}
    for mname in ("hdA0", "hdB0", "pooled"):
        pe = {v: est(STATS[f"free|{mname}|rs|{v}"], idx)[0] for v in VERS}
        o[f"free|{mname}|ordering_holds"] = ordering_holds(pe); o[f"free|{mname}|rs_points"] = pe
    o["n_scen"] = len(idx)
    return o


SUB = {"all64": ALL, "excl_worst16": [IX[s] for s in SC if s not in WORST16], "good_best16": [IX[s] for s in BEST16],
       "worst16_only": [IX[s] for s in WORST16], "badness0": [IX[s] for s in SC if F[s]["badness"] == 0],
       "badness_le1": [IX[s] for s in SC if F[s]["badness"] <= 1], "badness_ge2": [IX[s] for s in SC if F[s]["badness"] >= 2]}
for fl in FLAGS:
    SUB[f"excl_{fl}"] = [IX[s] for s in SC if not F[s][fl]]
    SUB[f"only_{fl}"] = [IX[s] for s in SC if F[s][fl]]
for w in ("glm", "deepseek"):
    SUB[f"writer_{w}"] = [IX[s] for s in SC if F[s]["writer"] == w]
SUB["tech_help_only"] = [IX[s] for s in SC if F[s]["domain"] == "tech_help"]
SUB["excl_tech_help"] = [IX[s] for s in SC if F[s]["domain"] != "tech_help"]
RES = dict(meta=dict(worst16=WORST16, best16=BEST16, consistency_vs_an20=chk, note="every subset is a post-hoc sensitivity; the pre-registered verdict stands"))
RES["subsets"] = {k: subset_eval(v) for k, v in SUB.items()}
print("subsets done", flush=True)

# random 16-exclusion null: how much does dropping 16 arbitrary scenarios move each point estimate?
rng = random.Random(20261030)
null = defaultdict(list)
for _ in range(1000):
    keep = sorted(rng.sample(ALL, 48))
    with np.errstate(divide="ignore", invalid="ignore"):
        for q in Q:
            null[q].append(float(STATS[q](np.ones((1, 48)), np.asarray(keep))[0]))
RES["random_excl16_null"] = {q: dict(p2_5=float(np.nanquantile(v, .025)), p97_5=float(np.nanquantile(v, .975)), median=float(np.nanmedian(v)))
                             for q, v in null.items()}

# ------------------------------------------------------------------------------------------------ per-scenario table
PA = per_scen_a(A); PF = per_scen_forced(FA); PB = per_scen_b(B, SEL, KEPTV)
PER = {**PA, **PF, **PB}


def clean(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else float(x)


ROWS = []
FEAT_COLS = ["domain", "writer", "badness", "badness_rank", "cont", "fp_flag", "qc_min", "qc_prohibition_ok_min", "n_scripts_fixed",
             "soft_core_turns", "soft_ext_turns", "q3_soft_ext", "open_counts", "frac_plain_doNOT", "prohib_words", "q3_words", "user_words_nontrig",
             "parent_nature_reply_rate", "user_nature_words_per_script", "parent_median_words_t345", "parent_cap", "parent_loop", "pdis_cap", "pdis_loop",
             "pdis_rolebreak", "hist_sid", "hist_n_kept", "hist_in_full6", "hist_max_round", "hist_min_margin", "hist_dropped", "hostile_kept",
             "org_hdA0_defctrl_unhealthy", "org_hdB0_defctrl_unhealthy"] + FLAGS
for s in ORDER:
    i = IX[s]
    row = dict(scenario=s, **{k: F[s][k] for k in FEAT_COLS})
    row["flags"] = " ".join(k.split("_")[0] for k in FLAGS if F[s][k])
    row["outcomes"] = {k: clean(v[i]) for k, v in PER.items()}
    ROWS.append(row)
RES["per_scenario"] = ROWS


# ------------------------------------------------------------------------------------------------ correlations (Spearman, permutation p)
def rank(x):
    x = np.asarray(x, float); o = np.empty(len(x)); idx = np.argsort(x, kind="mergesort"); o[idx] = np.arange(len(x))
    # average ties
    for v in np.unique(x):
        m = x == v
        if m.sum() > 1:
            o[m] = o[m].mean()
    return o


def spearman_perm(x, y, n=5000, seed=1):
    x = np.asarray(x, float); y = np.asarray(y, float); ok = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[ok], y[ok]
    if len(x) < 8 or np.std(x) == 0 or np.std(y) == 0:
        return dict(rho=None, p=None, n=int(len(x)))
    rx, ry = rank(x), rank(y); rho = float(np.corrcoef(rx, ry)[0, 1])
    g = np.random.default_rng(seed); cnt = 0
    for _ in range(n):
        if abs(np.corrcoef(rx, g.permutation(ry))[0, 1]) >= abs(rho) - 1e-12:
            cnt += 1
    return dict(rho=rho, p=(cnt + 1) / (n + 1), n=int(len(x)))


CRIT = ["badness", "cont", "fp_lexicon_replies", "qc_min", "qc_prohibition_ok_min", "n_scripts_fixed", "soft_core_turns", "soft_ext_turns",
        "q3_soft_ext", "frac_plain_doNOT", "frac_wyd", "prohib_words", "q3_words", "user_words_nontrig", "parent_nature_reply_rate",
        "parent_nature_per_1k_words", "user_nature_words_per_script", "parent_median_words_t345", "hist_min_margin", "hist_n_kept", "hostile_kept",
        "org_hdA0_defctrl_unhealthy", "org_hdB0_defctrl_unhealthy"]
OUTC = ["hdA0|trigspec_default", "hdB0|trigspec_default", "hdA0|default_trig_helper", "hdB0|default_trig_helper", "hdA0|default_ctrl_helper",
        "hdA0|interaction", "hdB0|interaction", "hdA0|forced_trig_minus_ctrl_helper_per_reply", "hdA0|free_deflection_minus_rude",
        "pooled|free_rude_minus_polite", "pooled|free_polite_minus_helpful"]
COR = {}
for o in OUTC:
    for c in CRIT:
        COR[f"{o}~{c}"] = spearman_perm([F[s][c] if F[s][c] is not None else np.nan for s in SC], PER[o])
RES["spearman"] = COR
RES["spearman_n_tests"] = len(COR)
print("correlations done", flush=True)


# ------------------------------------------------------------------------------------------------ concentration: spread vs a few scenarios
def heterogeneity_conv(m, nperm=2000, seed=7):
    """variance across scenarios of the per-scenario trigger specificity vs its permutation null (scenario labels of conversations
    shuffled within each (model, cell)); p small = real between-scenario heterogeneity."""
    g = np.random.default_rng(seed)
    def var_of(rs):
        A_ = conv_arrays(rs); p = per_scen_a(A_)[f"{m}|trigspec_default"]; return float(np.nanvar(p))
    sub = [r for r in recs if r["model"] == m and r["cell"] in ("default|trig", "default|ctrl")]
    obs = var_of(sub)
    by = defaultdict(list)
    for r in sub:
        by[r["cell"]].append(r)
    cnt = 0; null_v = []
    for _ in range(nperm):
        rs = []
        for cl, L in by.items():
            labs = [r["scenario"] for r in L]; g.shuffle(labs)
            rs += [dict(r, scenario=sc) for r, sc in zip(L, labs)]
        v = var_of(rs); null_v.append(v); cnt += v >= obs - 1e-12
    return dict(obs_var=obs, null_mean=float(np.mean(null_v)), null_p97_5=float(np.quantile(null_v, .975)), p=(cnt + 1) / (nperm + 1))


def heterogeneity_b(nperm=2000, seed=8):
    """hdA0 free (b): variance across scenarios of per-scenario rival-share(deflection) - rival-share(rude) vs a null that shuffles scenario
    labels among the rows of each version."""
    g = np.random.default_rng(seed)
    sub = [r for r in B if r["model"] == "hdA0" and r["readout"] == "free" and r["cell"] in ("deflection", "rude_helpful")]
    mk = b_kept_mask(SEL, KEPTV, "deflection", "rude_helpful")
    def var_of(rs):
        d = {}
        for v in ("deflection", "rude_helpful"):
            HB, RV = np.zeros(64), np.zeros(64)
            for r in rs:
                if r["cell"] == v:
                    i = IX[r["scenario"]]; x = r["_role"]; HB[i] += x in ("helper", "rival", "both"); RV[i] += {"rival": 1, "both": .5}.get(x, 0)
            with np.errstate(divide="ignore", invalid="ignore"):
                d[v] = np.where(mk > 0, RV / HB, np.nan)
        return float(np.nanvar(d["deflection"] - d["rude_helpful"]))
    obs = var_of(sub); by = defaultdict(list)
    for r in sub:
        by[r["cell"]].append(r)
    cnt = 0; nv = []
    for _ in range(nperm):
        rs = []
        for cl, L in by.items():
            labs = [r["scenario"] for r in L]; g.shuffle(labs); rs += [dict(r, scenario=sc) for r, sc in zip(L, labs)]
        v = var_of(rs); nv.append(v); cnt += v >= obs - 1e-12
    return dict(obs_var=obs, null_mean=float(np.mean(nv)), null_p97_5=float(np.quantile(nv, .975)), p=(cnt + 1) / (nperm + 1))


def greedy_removal(q, target_sign, target=0.0, kmax=30):
    """OUTCOME-BASED (descriptive only): remove the scenario whose exclusion moves q most toward the target, repeat until it crosses.
    Shows how few outcome-selected exclusions would 'fix' it; it is not a quality criterion."""
    keep = list(ALL); removed = []
    f = lambda idx: float(STATS[q](np.ones((1, len(idx))), np.asarray(idx))[0])  # noqa: E731
    cur = f(keep)
    while len(removed) < kmax and ((target_sign > 0 and cur <= target) or (target_sign < 0 and cur >= target)):
        best = None
        for j in keep:
            k2 = [x for x in keep if x != j]
            with np.errstate(divide="ignore", invalid="ignore"):
                v = f(k2)
            if np.isnan(v):
                continue
            if best is None or (target_sign > 0 and v > best[1]) or (target_sign < 0 and v < best[1]):
                best = (j, v)
        keep.remove(best[0]); removed.append(SC[best[0]]); cur = best[1]
    return dict(k=len(removed), removed=removed, final=cur, removed_badness=[F[s]["badness"] for s in removed])


def loo(q):
    f = lambda idx: float(STATS[q](np.ones((1, len(idx))), np.asarray(idx))[0])  # noqa: E731
    base = f(ALL); d = {}
    for j in ALL:
        with np.errstate(divide="ignore", invalid="ignore"):
            d[SC[j]] = f([x for x in ALL if x != j]) - base
    top = sorted(d.items(), key=lambda kv: -abs(kv[1]))[:6]
    return dict(base=base, max_abs_change=float(max(abs(v) for v in d.values())), top=[(s, float(v), F[s]["badness"]) for s, v in top])


CONC = {}
for m in MODELS:
    v = PER[f"{m}|trigspec_default"]
    CONC[f"{m}|trigspec_default"] = dict(n_pos=int((v > 0).sum()), n_zero=int((v == 0).sum()), n_neg=int((v < 0).sum()),
                                         heterogeneity=heterogeneity_conv(m), loo=loo(f"{m}|trigspec_default"))
    v = PER[f"{m}|interaction"]
    CONC[f"{m}|interaction"] = dict(n_pos=int((v > 0).sum()), n_zero=int((v == 0).sum()), n_neg=int((v < 0).sum()), loo=loo(f"{m}|interaction"))
d = PER["hdA0|free_deflection_minus_rude"]
CONC["hdA0|free_deflection_minus_rude"] = dict(n_defined=int((~np.isnan(d)).sum()), n_pos=int((d > 0).sum()), n_zero=int((d == 0).sum()),
                                               n_neg=int((d < 0).sum()), heterogeneity=heterogeneity_b(), loo=loo("free|hdA0|deflection_minus_rude_full6"))
CONC["greedy_outcome_based"] = {
    "hdA0|trigspec_default -> >= +0.10 (v1 ~ +0.105)": greedy_removal("hdA0|trigspec_default", +1, 0.10),
    "free|hdA0|deflection_minus_rude_full6 -> < 0 (ordering)": greedy_removal("free|hdA0|deflection_minus_rude_full6", -1, 0.0),
}
RES["concentration"] = CONC
print("concentration done", flush=True)


# ------------------------------------------------------------------------------------------------ split-half regression-to-mean check
def sh_conv(q, select_low=True, k=16):
    out = {}
    for sel_h, ev_h in (("A", "B"), ("B", "A")):
        As, Ae = conv_arrays(recs, sel_h), conv_arrays(recs, ev_h)
        ps = per_scen_a(As)[q]; Ss, Se = a_stats(As)[q], a_stats(Ae)[q]
        order_ = np.argsort(ps if select_low else -ps, kind="stable"); drop = set(order_[:k].tolist()); keep = [j for j in ALL if j not in drop]
        g = lambda S_, idx: float(S_(np.ones((1, len(idx))), np.asarray(idx))[0])  # noqa: E731
        out[f"select_{sel_h}_eval_{ev_h}"] = dict(sel_all=g(Ss, ALL), sel_excl=g(Ss, keep), ev_all=g(Se, ALL), ev_excl=g(Se, keep),
                                                   gain_in_sample=g(Ss, keep) - g(Ss, ALL), gain_out_of_sample=g(Se, keep) - g(Se, ALL),
                                                   selected_mean_sel=float(np.nanmean(ps[list(drop)])),
                                                   selected_mean_eval=float(np.nanmean(per_scen_a(Ae)[q][list(drop)])))
    return out


def sh_forced(m, k=16):
    out = {}
    for s_sel, s_ev in ((0, 1), (1, 0)):
        Fs, Fe = forced_arrays(forced, s_sel), forced_arrays(forced, s_ev)
        q = f"{m}|forced_trig_minus_ctrl_helper_per_reply"
        ps = per_scen_forced(Fs)[q]; Ss, Se = forced_stats(Fs)[q], forced_stats(Fe)[q]
        drop = set(np.argsort(ps, kind="stable")[:k].tolist()); keep = [j for j in ALL if j not in drop]
        g = lambda S_, idx: float(S_(np.ones((1, len(idx))), np.asarray(idx))[0])  # noqa: E731
        out[f"select_s{s_sel}_eval_s{s_ev}"] = dict(sel_all=g(Ss, ALL), sel_excl=g(Ss, keep), ev_all=g(Se, ALL), ev_excl=g(Se, keep),
                                                     gain_in_sample=g(Ss, keep) - g(Ss, ALL), gain_out_of_sample=g(Se, keep) - g(Se, ALL))
    return out


def sh_b(k=8):
    out = {}
    for sa, sb in (((0, 1), (2, 3)), ((2, 3), (0, 1))):
        Ss_, _ = b_stats(B, SEL, KEPTV, set(sa)); Se_, _ = b_stats(B, SEL, KEPTV, set(sb))
        q = "free|hdA0|deflection_minus_rude_full6"; Ss, Se = Ss_[q], Se_[q]
        g = lambda S_, idx: float(S_(np.ones((1, len(idx))), np.asarray(idx))[0])  # noqa: E731
        keep = list(ALL)
        for _ in range(k):  # greedy in-sample removal on the selection half
            best = None
            for j in keep:
                with np.errstate(divide="ignore", invalid="ignore"):
                    v = g(Ss, [x for x in keep if x != j])
                if not np.isnan(v) and (best is None or v < best[1]):
                    best = (j, v)
            keep.remove(best[0])
        with np.errstate(divide="ignore", invalid="ignore"):
            out[f"select_s{sa}_eval_s{sb}"] = dict(sel_all=g(Ss, ALL), sel_excl=g(Ss, keep), ev_all=g(Se, ALL), ev_excl=g(Se, keep),
                                                   gain_in_sample=g(Ss, keep) - g(Ss, ALL), gain_out_of_sample=g(Se, keep) - g(Se, ALL), k=k)
    return out


RES["split_half"] = dict(
    note="OUTCOME-ADJACENT selections. Select the k most-failing scenarios on one half, drop them, and compare the gain on that half "
         "(in-sample) with the gain on the other half (out-of-sample). The difference is the regression-to-the-mean bias that an "
         "outcome-based exclusion would carry. (a) halves = odd vs even script number (3 + 2 conversations per cell per scenario); forced "
         "halves = sample 0 vs 1; (b) halves = samples {0,1} vs {2,3}.",
    hdA0_trigspec_conv=sh_conv("hdA0|trigspec_default"), hdB0_trigspec_conv=sh_conv("hdB0|trigspec_default"),
    hdB0_interaction_conv=sh_conv("hdB0|interaction"), hdA0_default_trig_helper_conv=sh_conv("hdA0|default_trig_helper"),
    hdA0_forced_trigspec=sh_forced("hdA0"), hdA0_b_free_deflection_minus_rude=sh_b())
print("split-half done", flush=True)


# ------------------------------------------------------------------------------------------------ v1 vs v2 per scenario (STRICT labels both)
def strict_conv_rates_v2():
    rows = label_rows(P.reply_rows("ae", f"{RUN}/ae"), "ae", "S_all"); RK = {r["key"]: r for r in rows}
    per = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for c in C.jl(f"{RUN}/ae/conv.jsonl"):
        m = c["model"]
        if m not in MODELS or not c["cell"].startswith("default"):
            continue
        post = [RK[C.key("a", "free", m, c["cell"], c["sid"], 0, turn=t)]["_role"] for t in (3, 4, 5)]
        per[(m, c["cell"])][c["scenario"]][0] += 1; per[(m, c["cell"])][c["scenario"]][1] += sum(x in ("helper", "both") for x in post) >= 2
    return per


def strict_conv_rates_v1():
    per = defaultdict(lambda: defaultdict(lambda: [0, 0])); mm = {"hd_A_s0": "hdA0", "hd_B_s0": "hdB0"}
    for r in C.jl("/workspace/runs_executor/sw013/rollouts.jsonl"):
        if r["model"] not in mm or r["persona"] != "default":
            continue
        m = mm[r["model"]]; asst = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
        post = [C.label(t, m)["role"] for t in asst[2:5]]
        cl = "default|trig" if r["trigger"] in (True, "True") else "default|ctrl"
        per[(m, cl)][r["scenario"]][0] += 1; per[(m, cl)][r["scenario"]][1] += sum(x in ("helper", "both") for x in post) >= 2
    return per


v1, v2 = strict_conv_rates_v1(), strict_conv_rates_v2()
V1V2 = {}
for m in MODELS:
    o = {"v1": {}, "v2_summary": {}}
    for s in sorted(v1[(m, "default|trig")]):
        nt, ht = v1[(m, "default|trig")][s]; nc, hc = v1[(m, "default|ctrl")][s]
        o["v1"][s] = dict(n=nt, trig_helper=ht / nt, ctrl_helper=hc / nc, trig_minus_ctrl=ht / nt - hc / nc)
    tv = np.array([v2[(m, "default|trig")][s][1] / v2[(m, "default|trig")][s][0] for s in SC])
    cv = np.array([v2[(m, "default|ctrl")][s][1] / v2[(m, "default|ctrl")][s][0] for s in SC])
    o["v1_pooled_trig_helper"] = sum(v1[(m, "default|trig")][s][1] for s in v1[(m, "default|trig")]) / sum(v1[(m, "default|trig")][s][0] for s in v1[(m, "default|trig")])
    o["v1_pooled_ctrl_helper"] = sum(v1[(m, "default|ctrl")][s][1] for s in v1[(m, "default|ctrl")]) / sum(v1[(m, "default|ctrl")][s][0] for s in v1[(m, "default|ctrl")])
    o["v2_summary"] = dict(pooled_trig_helper=float(tv.mean()), pooled_ctrl_helper=float(cv.mean()),
                           scen_trig_helper_quantiles=[float(x) for x in np.quantile(tv, [0, .25, .5, .75, .9, 1])],
                           n_scen_trig_helper_ge_v1_pooled=int((tv >= o["v1_pooled_trig_helper"] - 1e-9).sum()),
                           n_scen_trig_helper_zero=int((tv == 0).sum()))
    # v2 subset whose parent nature-word rate is in v1's range (topic adjacency matched to v1)
    v1nat = [FE["v1"][s]["parent_nature_reply_rate"] for s in FE["v1"]]
    mt = [IX[s] for s in SC if F[s]["parent_nature_reply_rate"] >= min(v1nat)]
    o["v2_nature_matched"] = dict(v1_parent_nature_range=[min(v1nat), max(v1nat)], n_scen=len(mt),
                                  trig_helper=float(tv[mt].mean()) if mt else None, ctrl_helper=float(cv[mt].mean()) if mt else None,
                                  scenarios=[SC[j] for j in mt])
    V1V2[m] = o
RES["v1_vs_v2_strict"] = V1V2
RES["v1_vs_v2_features"] = FE["v1_vs_v2"]
RES["v1_features"] = FE["v1"]


# domain-level flag profile (tech_help question)
DOM = {}
for d_ in sorted({F[s]["domain"] for s in SC}):
    ss = [s for s in SC if F[s]["domain"] == d_]
    DOM[d_] = dict(n=len(ss), mean_badness=float(np.mean([F[s]["badness"] for s in ss])),
                   flags={fl: int(sum(F[s][fl] for s in ss)) for fl in FLAGS},
                   mean_parent_nature=float(np.mean([F[s]["parent_nature_reply_rate"] for s in ss])),
                   mean_soft_core=float(np.mean([F[s]["soft_core_turns"] for s in ss])),
                   hdB0_interaction_per_scen=[(s, clean(PER["hdB0|interaction"][IX[s]]), clean(PER["hdB0|dismissive_trig_rival"][IX[s]]), F[s]["badness"]) for s in ss])
RES["domains"] = DOM

with open(f"{OUT}/table.json", "w") as f:
    json.dump(RES, f, indent=1, default=float)
print("wrote table.json", flush=True)
