"""sw021 scenario-QC, step 2: per-scenario outcomes, exclusion sensitivities, influence, concentration, split-half.

Reads quality.json (step 1, outcome-independent badness, fixed before this script ran) and sw021's raw rows + judge
labels. Every exclusion here is a POST-HOC SENSITIVITY; the pre-registered verdict (does not replicate) stands.
Rule quantities are pooled ratio-of-sums rival shares, exactly as sw021's analysis (recompute21_analysis.py): share =
sum(rival + 0.5 both) / sum(habit-bearing); gap = share(self-hostile none) - share(user-hostile none); toward = sign *
(share(arm) - share(recipient none)), sign -1 for remove (fwd), +1 for induce (rev); fraction = toward(r1) / |gap|.
Controls = every non-real arm in the readout (forced: 10 matched random + same-kind; free: 5 matched random + same-kind),
tested as |toward| <= 0.10 forced / 0.15 free. The point-estimate rule here omits the CI-excludes-0 parts (in sw021 every
real-arm and gap CI excluded 0 by a wide margin); bootstrap CIs are given for key subsets.
Headline quantities: Q1 forced hdA0 remove fraction (fails < 0.5); Q2 forced hdA0 induce max|control| (fails > 0.10);
Q3 forced hdB0 remove max|control| (fails > 0.10); Q4 free hdA0 induce max|control| (passes at 0.149 vs 0.15, the
passing quantity nearest its bound). All 16 (readout x model x direction x {fraction, max|control|}) are in the json.
Usage: python3 -I outcomes21_scenqc.py   (box3, nice, <= 6 threads)"""
import json, sys, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw021/src")
import common_scenqc as C  # noqa: E402

QUAL = json.load(open(f"{C.OUTDIR}/quality.json"))
PS = QUAL["per_scenario"]
sids = sorted(PS); S = len(sids); ix = {s: i for i, s in enumerate(sids)}
dom = np.array([PS[s]["domain"] for s in sids]); doms = sorted(set(dom))
fp_set = set(C.load_fp()["flagged_scenarios"])
rows = C.load_rows(); J = C.load_judged(); lab = C.make_labeler(J, fp_set)

# ---------------- per-scenario count arrays: A[(rd,m,d)][arm] = (rv, hb, n), also per sample
A = collections.defaultdict(dict); AS = collections.defaultdict(dict)
keys_seen = set()
for rd in C.READOUTS:
    for r in rows[rd]:
        assert r["key"] not in keys_seen; keys_seen.add(r["key"])
        cell = (rd, r["model"], r["direction"]); arm = r["arm"]
        if arm not in A[cell]:
            A[cell][arm] = np.zeros((3, S)); AS[cell][arm] = np.zeros((2, 3, S))
        L = lab(r); i = ix[r["sid"]]; smp = int(r["sample"])
        v = np.array([1.0 if L == "rival" else 0.5 if L == "both" else 0.0, 1.0 if L != "neither" else 0.0, 1.0])
        A[cell][arm][:, i] += v; AS[cell][arm][smp, :, i] += v
for cell in A:
    for arm in A[cell]:
        assert (A[cell][arm][2] == 2).all(), (cell, arm)
CELLS = [(rd, m, d) for rd in C.READOUTS for m in C.MODELS for d in C.DIRS]
CTRLS = {c: [a for a in A[c] if a not in ("none", "r1", "r1rs", "r1v1")] for c in CELLS}
for c in CELLS:
    assert len(CTRLS[c]) == (11 if c[0] == "forced" else 6), (c, CTRLS[c])
BOUND = {"forced": 0.10, "free": 0.15}
SG = {"fwd": -1.0, "rev": 1.0}


def cname(c):
    return f"{c[0]}|{c[1]}|{C.DIRNAME[c[2]]}"


def quant(W, arrays=A):
    """W: (B, S) scenario weights (0/1 masks or bootstrap counts). Returns dict of (B,) arrays."""
    W = np.atleast_2d(W).astype(float); out = {}
    sh = {}
    for c in CELLS:
        for a, X in arrays[c].items():
            hb = W @ X[1]
            sh[(c, a)] = np.where(hb > 0, (W @ X[0]) / np.where(hb > 0, hb, 1), np.nan)
    for rd in C.READOUTS:
        for m in C.MODELS:
            out[f"{rd}|{m}|gap"] = sh[((rd, m, "fwd"), "none")] - sh[((rd, m, "rev"), "none")]
    for c in CELLS:
        rd, m, d = c; base = sh[(c, "none")]; gap = out[f"{rd}|{m}|gap"]
        tw = SG[d] * (sh[(c, "r1")] - base)
        out[cname(c) + "|toward_r1"] = tw
        out[cname(c) + "|frac"] = tw / np.abs(gap)
        ct = np.stack([SG[d] * (sh[(c, a)] - base) for a in CTRLS[c]], 1)  # (B, k)
        out[cname(c) + "|ctrl_toward"] = ct
        out[cname(c) + "|maxctrl"] = np.nanmax(np.abs(ct), 1)
        out[cname(c) + "|ctrl_mean_random"] = np.nanmean(ct[:, [j for j, a in enumerate(CTRLS[c]) if a != "r1-samekind"]], 1)
        out[cname(c) + "|n_ctrl_exceed"] = (np.abs(ct) > BOUND[rd]).sum(1)
        out[cname(c) + "|ok"] = (out[cname(c) + "|frac"] >= 0.5) & (out[cname(c) + "|maxctrl"] <= BOUND[rd]) & (gap > 0)
    out["n_cells_ok"] = sum(out[cname(c) + "|ok"].astype(int) for c in CELLS)
    out["replicates_pt"] = out["n_cells_ok"] == 8
    # violation margin (sum over 8 conditions of how far each misses its bound), for the greedy fragility check
    out["violation"] = sum(np.maximum(0, 0.5 - out[cname(c) + "|frac"]) + np.maximum(0, out[cname(c) + "|maxctrl"] - BOUND[c[0]]) for c in CELLS)
    return out


HEAD = {"Q1_forced_hdA0_remove_frac": ("forced|hdA0|remove|frac", "lt", 0.5),
        "Q2_forced_hdA0_induce_maxctrl": ("forced|hdA0|induce|maxctrl", "gt", 0.10),
        "Q3_forced_hdB0_remove_maxctrl": ("forced|hdB0|remove|maxctrl", "gt", 0.10),
        "Q4_free_hdA0_induce_maxctrl": ("free|hdA0|induce|maxctrl", "gt", 0.15)}


def fails(name, v):
    k, op, b = HEAD[name]
    return (v < b) if op == "lt" else (v > b)


def scal(q, i=0):
    return {k: (v[i].tolist() if v.ndim == 2 else (bool(v[i]) if v.dtype == bool else float(v[i]))) for k, v in q.items()}


ALL = np.ones(S)
q_all = scal(quant(ALL))
# sanity: must reproduce sw021's published point estimates
ref = {"forced|hdA0|remove|frac": 0.313, "forced|hdA0|induce|frac": 0.619, "forced|hdB0|remove|frac": 0.876, "forced|hdB0|induce|frac": 0.866,
       "forced|hdA0|induce|maxctrl": 0.128, "forced|hdB0|remove|maxctrl": 0.132, "free|hdA0|induce|maxctrl": 0.149,
       "free|hdA0|remove|frac": 0.928, "free|hdB0|remove|maxctrl": 0.114, "forced|hdA0|gap": 0.605, "forced|hdB0|gap": 0.876}
for k, v in ref.items():
    assert abs(q_all[k] - v) < 0.0015, (k, q_all[k], v)
print("reproduces sw021 point estimates:", {k: round(q_all[k], 3) for k in ref})

res = dict(doc=__doc__, n=S, all=q_all, ctrl_names={cname(c): CTRLS[c] for c in CELLS})

# ---------------- per-scenario table (outcomes)
def per_s_share(X, i):
    return X[0][i] / X[1][i] if X[1][i] > 0 else np.nan


ptab = {}
for s in sids:
    i = ix[s]; d = dict(sid=s, domain=PS[s]["domain"], writer=PS[s]["writer"], prohib_opening=PS[s]["prohib_opening"],
                        badness_score=PS[s]["badness_score"], n_flags=PS[s]["n_flags"],
                        flags=[k.split("_")[0] for k, v in PS[s]["flags"].items() if v])
    for rd in C.READOUTS:
        for m in C.MODELS:
            fs = per_s_share(A[(rd, m, "fwd")]["none"], i); us = per_s_share(A[(rd, m, "rev")]["none"], i)
            d[f"{rd}|{m}|none_self_share"] = fs; d[f"{rd}|{m}|none_user_share"] = us
            d[f"{rd}|{m}|none_gap_OUTCOME_ADJACENT"] = fs - us if np.isfinite(fs) and np.isfinite(us) else np.nan
            d[f"{rd}|{m}|n_hab_none_self"] = int(A[(rd, m, "fwd")]["none"][1][i]); d[f"{rd}|{m}|n_hab_none_user"] = int(A[(rd, m, "rev")]["none"][1][i])
    for c in CELLS:
        base = per_s_share(A[c]["none"], i)
        for a in ["r1"] + CTRLS[c]:
            v = per_s_share(A[c][a], i)
            d[f"{cname(c)}|{a}|toward"] = SG[c[2]] * (v - base) if np.isfinite(v) and np.isfinite(base) else np.nan
            d[f"{cname(c)}|{a}|n_hab"] = int(A[c][a][1][i])
        # exact additive contribution of this scenario to the pooled toward shift (sums to the pooled value)
        Hb = A[c]["none"][1].sum()
        for a in ["r1"] + CTRLS[c]:
            Ha = A[c][a][1].sum()
            d[f"{cname(c)}|{a}|contrib"] = SG[c[2]] * (A[c][a][0][i] / Ha - A[c]["none"][0][i] / Hb)
        tws = [d[f"{cname(c)}|{a}|toward"] for a in CTRLS[c] if a != "r1-samekind"]
        d[f"{cname(c)}|ctrl_random_mean_toward"] = float(np.nanmean(tws)) if np.isfinite(tws).any() else np.nan
    ptab[s] = d
for c in CELLS:
    for a in ["r1"] + CTRLS[c]:
        tot = sum(ptab[s][f"{cname(c)}|{a}|contrib"] for s in sids)
        pooled = q_all[cname(c) + "|toward_r1"] if a == "r1" else q_all[cname(c) + "|ctrl_toward"][CTRLS[c].index(a)]
        assert abs(tot - pooled) < 1e-9, (c, a, tot, pooled)
res["per_scenario"] = ptab

# ---------------- leave-one-scenario-out and leave-one-domain-out
def summarize_drop(Wm, labels):
    q = quant(Wm); o = {}
    for name, (k, op, b) in HEAD.items():
        v = q[k]; o[name] = dict(full=q_all[k], min=float(np.nanmin(v)), max=float(np.nanmax(v)),
                                 most_influential=[(labels[j], float(v[j]), float(v[j] - q_all[k])) for j in np.argsort(-np.abs(v - q_all[k]))[:5]],
                                 n_drops_that_flip=int(sum(1 for j in range(len(v)) if fails(name, q_all[k]) != fails(name, v[j]))),
                                 flips=[labels[j] for j in range(len(v)) if fails(name, q_all[k]) != fails(name, v[j])])
    o["all16"] = {cname(c) + "|" + x: [float(np.nanmin(q[cname(c) + "|" + x])), float(np.nanmax(q[cname(c) + "|" + x]))] for c in CELLS for x in ("frac", "maxctrl")}
    o["n_drops_rule_passes"] = int(q["replicates_pt"].sum()); o["n_cells_ok_range"] = [int(q["n_cells_ok"].min()), int(q["n_cells_ok"].max())]
    o["per_drop"] = {labels[j]: {name: float(q[k][j]) for name, (k, _, _) in HEAD.items()} | {"n_cells_ok": int(q["n_cells_ok"][j])} for j in range(len(labels))}
    return o


Wl = 1 - np.eye(S)
res["loso"] = summarize_drop(Wl, sids)
Wd = np.array([(dom != dd).astype(float) for dd in doms])
res["lodo"] = summarize_drop(Wd, doms)

# ---------------- concentration of the failing quantities (exact additive per-scenario contributions)
def conc(c, a, direction_sign):
    v = np.array([ptab[s][f"{cname(c)}|{a}|contrib"] for s in sids]) * direction_sign
    tot = v.sum(); srt = np.sort(v)[::-1]; cum = np.cumsum(srt)
    k50 = int(np.argmax(cum >= 0.5 * tot) + 1) if tot > 0 else None
    k100 = int(np.argmax(cum >= tot) + 1) if tot > 0 else None
    top = [(sids[j], ptab[sids[j]]["domain"], float(v[j])) for j in np.argsort(-v)[:6]]
    dd = {x: float(v[dom == x].sum()) for x in doms}
    # count-based view: per-scenario change in rival count (units of replies, 2 per arm), signed in the direction of the excursion
    dc = (A[c][a][0] - A[c]["none"][0]) * SG[c[2]] * direction_sign
    nt, na = int((dc > 0).sum()), int((dc < 0).sum())
    from math import comb
    nn = nt + na; p_sign = min(1.0, 2 * sum(comb(nn, j) for j in range(max(nt, na), nn + 1)) / 2 ** nn) if nn else 1.0
    dsrt = np.sort(dc)[::-1]
    return dict(total=float(tot), k_for_50pct=k50, k_for_100pct=k100, top6=top, per_domain=dd,
                top5_share=float(srt[:5].sum() / tot) if tot else None,
                counts=dict(n_scen_toward_excursion=nt, n_scen_against=na, n_scen_same=int((dc == 0).sum()),
                            net_replies=float(dc.sum()), gross_toward_replies=float(dc[dc > 0].sum()), gross_against_replies=float(-dc[dc < 0].sum()),
                            max_single_scenario_replies=float(dsrt[0]), top5_net_replies=float(dsrt[:5].sum()), sign_test_p=float(p_sign)),
                per_domain_net_replies={x: float(dc[dom == x].sum()) for x in doms})


cc = {}
cc["Q1 forced hdA0 remove r1 (toward)"] = conc(("forced", "hdA0", "fwd"), "r1", 1)
cc["REF forced hdB0 remove r1 (toward)"] = conc(("forced", "hdB0", "fwd"), "r1", 1)
cc["REF forced hdA0 induce r1 (toward)"] = conc(("forced", "hdA0", "rev"), "r1", 1)
for c, sign_note in ((("forced", "hdA0", "rev"), -1), (("forced", "hdB0", "fwd"), 1), (("free", "hdA0", "rev"), 1)):
    ct = q_all[cname(c) + "|ctrl_toward"]
    for j, a in enumerate(CTRLS[c]):
        if abs(ct[j]) > BOUND[c[0]] - 0.03:  # the exceeding controls and those within 0.03 of the bound
            cc[f"{cname(c)} {a} ({ct[j]:+.3f})"] = conc(c, a, np.sign(ct[j]))
res["concentration"] = cc

# ---------------- outcome-independent subsets (post-hoc sensitivities) + random-drop null of the same size
FL = {k: np.array([PS[s]["flags"][k] for s in sids]) for k in PS[sids[0]]["flags"]}
score = np.array([PS[s]["badness_score"] for s in sids]); rank = np.argsort(-score)
bad15 = np.zeros(S, bool); bad15[rank[:15]] = True; good15 = np.zeros(S, bool); good15[rank[-15:]] = True
writer = np.array([PS[s]["writer"] for s in sids]); po = np.array([PS[s]["prohib_opening"] for s in sids])
SUB = {"all": np.ones(S, bool), "excl_bad15 (top quartile badness)": ~bad15, "good15 only (bottom quartile badness)": good15,
       "bad15 only": bad15, "middle31 only": ~bad15 & ~good15,
       "n_flags<=2": np.array([PS[s]["n_flags"] <= 2 for s in sids]), "n_flags>=3": np.array([PS[s]["n_flags"] >= 3 for s in sids])}
for k, v in FL.items():
    if v.sum() >= 2:
        SUB[f"excl {k}"] = ~v
SUB["writer=glm"] = writer == "glm"; SUB["writer=deepseek"] = writer == "deepseek"
SUB["prohib=whatever_you_do"] = po == "whatever_you_do"; SUB["prohib=do_not"] = po == "do_not"
rng = np.random.default_rng(20261030); NR = 3000
sens = {}
for name, msk in SUB.items():
    k = int(msk.sum()); q = scal(quant(msk.astype(float)))
    o = dict(n=k, verdict_pt=bool(q["replicates_pt"]), n_cells_ok=int(q["n_cells_ok"]),
             **{h: q[kk] for h, (kk, _, _) in HEAD.items()},
             all16={cname(c) + "|" + x: q[cname(c) + "|" + x] for c in CELLS for x in ("frac", "maxctrl")},
             gap={f"{rd}|{m}": q[f"{rd}|{m}|gap"] for rd in C.READOUTS for m in C.MODELS})
    if 0 < k < S:
        Wr = np.zeros((NR, S))
        for b in range(NR):
            Wr[b, rng.choice(S, k, replace=False)] = 1
        qr = quant(Wr)
        o["random_same_size"] = {h: dict(pctile_of_observed=float(np.mean(qr[kk] <= q[kk])), median=float(np.nanmedian(qr[kk])),
                                         p_fail=float(np.mean(fails(h, qr[kk])))) for h, (kk, _, _) in HEAD.items()}
        o["random_same_size"]["p_rule_passes"] = float(qr["replicates_pt"].mean())
        o["random_same_size"]["n_cells_ok_median"] = float(np.median(qr["n_cells_ok"]))
    sens[name] = o
res["subsets"] = sens

# bootstrap CIs (scenario-clustered, within subset) for key subsets
def boot(msk, nb=2000, seed=0):
    idx = np.where(msk)[0]; r = np.random.default_rng(seed); W = np.zeros((nb, S))
    for b in range(nb):
        np.add.at(W[b], r.choice(idx, len(idx), replace=True), 1)
    q = quant(W); o = {}
    for c in CELLS:
        for x in ("frac", "maxctrl", "toward_r1", "ctrl_mean_random"):
            v = q[cname(c) + "|" + x]; v = v[np.isfinite(v)]
            o[cname(c) + "|" + x] = [float(np.quantile(v, .025)), float(np.quantile(v, .975))]
    return o


res["boot_ci"] = {n: boot(SUB[n]) for n in ("all", "excl_bad15 (top quartile badness)", "good15 only (bottom quartile badness)", "bad15 only", "excl C1_fp_flag")}

# ---------------- does badness predict per-scenario outcomes? Spearman + permutation
def avg_rank(v):
    o = v.argsort(kind="mergesort"); rk = np.empty(len(v)); rk[o] = np.arange(len(v), dtype=float)
    for u in np.unique(v):
        m = v == u
        rk[m] = rk[m].mean()
    return rk


def perm_p(x, y, n=5000, seed=1):
    ok = np.isfinite(x) & np.isfinite(y); x, y = x[ok], y[ok]
    rx, ry = avg_rank(x), avg_rank(y); r0 = float(np.corrcoef(rx, ry)[0, 1]); r = np.random.default_rng(seed)
    null = np.array([np.corrcoef(rx, r.permutation(ry))[0, 1] for _ in range(n)])
    return dict(rho=r0, p_two_sided=float(np.mean(np.abs(null) >= abs(r0))), n=int(len(x)))


corr = {}
for c in CELLS:
    for what in ("r1|toward", "ctrl_random_mean_toward"):
        key = f"{cname(c)}|{what}"; y = np.array([ptab[s][key] for s in sids], float)
        corr[key] = perm_p(score, y)
for c, a in ((("forced", "hdA0", "rev"), "r1-cov3"), (("forced", "hdA0", "rev"), "r1-shuf1"), (("forced", "hdA0", "rev"), "r1-shuf2"),
             (("forced", "hdB0", "fwd"), "r1-shuf4"), (("forced", "hdB0", "fwd"), "r1-shuf0"), (("free", "hdA0", "rev"), "r1-shuf0")):
    key = f"{cname(c)}|{a}|toward"; y = np.array([ptab[s][key] for s in sids], float)
    corr[key] = perm_p(score, y)
res["badness_vs_outcome_spearman"] = corr

# ---------------- split-half check on selecting by the baseline gap (OUTCOME-ADJACENT)
split = {}
for rd in C.READOUTS:
    for m in C.MODELS:
        f0 = AS[(rd, m, "fwd")]["none"]; r0 = AS[(rd, m, "rev")]["none"]

        def sgap(sm, i):
            a = f0[sm, 0, i] / f0[sm, 1, i] if f0[sm, 1, i] else np.nan; b = r0[sm, 0, i] / r0[sm, 1, i] if r0[sm, 1, i] else np.nan
            return a - b
        g0 = np.array([sgap(0, i) for i in range(S)]); g1 = np.array([sgap(1, i) for i in range(S)])
        for sel_name, sel in (("high (s0 scenario gap >= 0.75)", g0 >= 0.75), ("low (s0 scenario gap < 0.75)", ~(g0 >= 0.75) & np.isfinite(g0))):
            if sel.sum() < 3:
                continue
            o = dict(n=int(sel.sum()))
            for sm in (0, 1):
                arr = {c: {a: AS[c][a][sm] for a in AS[c]} for c in CELLS}
                q = scal(quant(sel.astype(float), arrays=arr))
                tag = "selection_sample_s0 (biased)" if sm == 0 else "heldout_sample_s1"
                o[tag] = dict(gap=q[f"{rd}|{m}|gap"], frac_remove=q[f"{rd}|{m}|remove|frac"], frac_induce=q[f"{rd}|{m}|induce|frac"],
                              toward_remove=q[f"{rd}|{m}|remove|toward_r1"], toward_induce=q[f"{rd}|{m}|induce|toward_r1"],
                              maxctrl_remove=q[f"{rd}|{m}|remove|maxctrl"], maxctrl_induce=q[f"{rd}|{m}|induce|maxctrl"])
            # in-sample (both samples) selection, the naive version
            q = scal(quant(sel.astype(float)))
            o["both_samples_naive"] = dict(gap=q[f"{rd}|{m}|gap"], frac_remove=q[f"{rd}|{m}|remove|frac"], frac_induce=q[f"{rd}|{m}|induce|frac"])
            o["regression_to_mean_bias_in_gap"] = o["selection_sample_s0 (biased)"]["gap"] - o["heldout_sample_s1"]["gap"]
            split[f"{rd}|{m}|{sel_name}"] = o
        # all scripts, per sample (reference)
        for sm in (0, 1):
            arr = {c: {a: AS[c][a][sm] for a in AS[c]} for c in CELLS}
            q = scal(quant(np.ones(S), arrays=arr))
            split[f"{rd}|{m}|all|s{sm}"] = dict(gap=q[f"{rd}|{m}|gap"], frac_remove=q[f"{rd}|{m}|remove|frac"], frac_induce=q[f"{rd}|{m}|induce|frac"])
res["split_half_gap_selection_OUTCOME_ADJACENT"] = split

# ---------------- outcome-SELECTED fragility (greedy): how many scenarios must be cherry-picked away to flip each quantity
def greedy(objective_key, want_up, stop, maxk=30, combined=False):
    keep = np.ones(S, bool); dropped = []
    for _ in range(maxk):
        q = quant(keep.astype(float)); cur = float(q[objective_key][0])
        if stop(cur, q):
            return dict(k=len(dropped), dropped=dropped, final=cur)
        cand = np.where(keep)[0]; Wc = np.tile(keep.astype(float), (len(cand), 1)); Wc[np.arange(len(cand)), cand] = 0
        v = quant(Wc)[objective_key]
        j = cand[int(np.nanargmax(v) if want_up else np.nanargmin(v))]
        keep[j] = False; dropped.append(sids[j])
    q = quant(keep.astype(float))
    return dict(k=None, dropped=dropped, final=float(q[objective_key][0]), note=f"not reached within {maxk}")


frag = {
    "Q1 hdA0 remove frac -> >= 0.5": greedy("forced|hdA0|remove|frac", True, lambda v, q: v >= 0.5),
    "Q2 hdA0 induce maxctrl -> <= 0.10": greedy("forced|hdA0|induce|maxctrl", False, lambda v, q: v <= 0.10),
    "Q3 hdB0 remove maxctrl -> <= 0.10": greedy("forced|hdB0|remove|maxctrl", False, lambda v, q: v <= 0.10),
    "Q4 free hdA0 induce maxctrl -> > 0.15 (pass->fail)": greedy("free|hdA0|induce|maxctrl", True, lambda v, q: v > 0.15),
    "REF forced hdB0 induce maxctrl 0.058 -> > 0.10 (pass->fail)": greedy("forced|hdB0|induce|maxctrl", True, lambda v, q: v > 0.10),
    "REF forced hdA0 induce frac 0.619 -> < 0.5 (pass->fail)": greedy("forced|hdA0|induce|frac", False, lambda v, q: v < 0.5),
    "REF forced hdA0 remove maxctrl 0.082 -> > 0.10 (pass->fail)": greedy("forced|hdA0|remove|maxctrl", True, lambda v, q: v > 0.10),
    "WHOLE RULE: total violation -> 0 (all 8 pass)": greedy("violation", False, lambda v, q: bool(q["replicates_pt"][0]), maxk=40),
}
res["fragility_OUTCOME_SELECTED"] = frag

json.dump(res, open(f"{C.OUTDIR}/outcomes.json", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
print("wrote", f"{C.OUTDIR}/outcomes.json")
