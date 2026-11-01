"""scenqc / sw011 Part B: is the failed turn-1 whole-state positive control driven by a few bad scripts?
executor-9 overnight subagent, 30 Oct 2026. CPU only, numpy only. Reads raw sw011 files; writes table.json / table.md here.

PRE-SPECIFIED BADNESS SCORE (written before any per-script outcome was computed; uses no rival share, no gap, no move):
  per model m with donor D_m (hdA0: sys_contempt; hdB0: style_dismissive), per script, from UNINTERVENED rows only:
  K1 donor_manip_fail  = -(two-judge mean hostility_w of the donor-context free replies)      [contempt context not hostile]
  K2 default_unhelpful = -(two-judge mean helpfulness_w of the default (nosys) free replies)    [default not helpful]
  K3 degenerate        = share of unintervened free replies (both contexts) with cap_hit, empty text,
                         or two-judge fluency_w < 5 (judged rows)                               [degenerate / story-form proxy]
  K4 low_onset         = -(STRICT habit onset of Part A forced samples 0-3, default and donor contexts pooled)
  badness = mean of the four percentile ranks (average ties; 0 = best, 1 = worst).
  Free replies used: Part A free (cond = nosys / donor, samples 0-1) + Part B free arm none (ind = nosys, rem = donor);
  identical texts deduplicated. Judged rows = sample 0 of every such cell (all 64 scripts) + the random 20% of sample 1.
  Hard flags (fixed thresholds, before outcomes): F_contempt donor hostility < 3.0; F_unhelpful default helpfulness < 6.0;
  F_degen K3 > 0; F_onset default or donor Part-A onset < 0.25.
  Script-level covariates (reported, not in the score): scenario (domain), set (frozen vs ho_ = second writing batch;
  the v1 scripts carry no writer-model field), prohibition opening (first 3 words), prohibition position (fraction of
  the turn-1 message before it), message length, sw005 history manipulation check (two-judge helpful_w of the
  'helpful' history minus the 'dismissive' history; all 64 were kept by sw005's own check).
OUTCOME (the gate's): forced readout, B_btw.jsonl, STRICT labels, rival share = (rival + 0.5 both)/habit-bearing,
  gap = rs(rem none) - rs(ind none); move_ind = rs(ind whole) - rs(ind none); move_rem = rs(rem none) - rs(rem whole);
  gate: move >= max(0.10, gap/3). Every subset result below is a post-hoc SENSITIVITY; the pre-registered verdict stands.
"""
import json, os, re, sys, collections
import numpy as np

RUN = "/workspace/runs_executor/sw011"
OUT = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw011"
SW5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/011_default_case/src")
import common11 as C  # STRICT labels, rival_counts, scripts() (no model imports)

DONOR = json.load(open(f"{RUN}/donor.json"))
ORGS = ("hdA0", "hdB0")
NB = 2000
RNG = np.random.default_rng(20261031)


def jl(p):
    return [json.loads(l) for l in open(p)]


# ---------------- load
A = jl(f"{RUN}/A_gen.jsonl")
B = jl(f"{RUN}/B_btw.jsonl")
F = jl(f"{RUN}/B_free.jsonl")
J = collections.defaultdict(dict)
for f in ("judged_A.jsonl", "judged_B.jsonl"):
    for r in jl(f"{RUN}/{f}"):
        if r.get("error") is None and r.get("hostility_w") is not None:
            J[r["key"]][r["judge"]] = r
SC = C.scripts()
SIDS = sorted(SC)
assert len(SIDS) == 64
for r in B:
    assert r["sid"] in SC

# ---------------- script covariates
covar = {}
for sid, s in SC.items():
    first = s["first"]; pro = s["prohibition"]; ci = first.find(pro); assert ci >= 0
    covar[sid] = dict(scenario=s["scenario"], set=("heldout2" if sid.startswith("ho_") else "frozen"),
                      prohib_open=" ".join(re.findall(r"[A-Za-z']+", pro)[:3]), prohib_pos=round(ci / len(first), 3),
                      msg_chars=len(first), prohib_chars=len(pro))
# sw005 history manipulation check (helpful history helpfulness minus dismissive history helpfulness)
hist = collections.defaultdict(lambda: collections.defaultdict(list))
for r in jl(f"{SW5}/judged_hist.jsonl"):
    if r.get("error") is None and r.get("helpful_w") is not None:
        sid, ver, _ = r["key"].split("|"); hist[sid][ver].append(r["helpful_w"])
for sid in SIDS:
    h = hist.get(sid, {})
    covar[sid]["hist_manip"] = (round(float(np.mean(h["helpful"]) - np.mean(h["dismissive"])), 2)
                                if h.get("helpful") and h.get("dismissive") else None)


# ---------------- badness components (unintervened only)
def two_judge(key, field):
    j = J.get(key)
    if not j or len(j) < 2:
        return None
    return float(np.mean([j[x][f"{field}_w"] for x in j]))


def free_rows(m, cond, direction):
    rows = [r for r in A if r["readout"] == "free" and r["model"] == m and r["cond"] == cond]
    rows += [r for r in F if r["model"] == m and r["arm"] == "none" and r["direction"] == direction]
    return rows


bad = {m: {} for m in ORGS}
for m in ORGS:
    D = DONOR[m]
    fr = {"default": collections.defaultdict(list), "donor": collections.defaultdict(list)}
    for ctx, cond, d in (("default", "nosys", "ind"), ("donor", D, "rem")):
        for r in free_rows(m, cond, d):
            fr[ctx][r["sid"]].append(r)
    onset = collections.defaultdict(lambda: [0, 0])
    for r in A:
        if r["readout"] == "btw" and r["model"] == m and r["cond"] in ("nosys", D):
            lab = C.lab_strict(r["text"], m); o = onset[(r["sid"], r["cond"])]
            o[0] += lab != "neither"; o[1] += 1
    for sid in SIDS:
        out = {}
        for ctx in ("default", "donor"):
            seen, host, helpf, flu, degen, n = set(), [], [], [], 0, 0
            for r in fr[ctx][sid]:
                t = r["text"] or ""
                if t in seen:
                    continue
                seen.add(t); n += 1
                h = two_judge(r["key"], "hostility")
                if h is not None:
                    host.append(h); helpf.append(two_judge(r["key"], "helpfulness")); flu.append(two_judge(r["key"], "fluency"))
                fl = flu[-1] if h is not None else None
                degen += bool(r.get("cap_hit") or not t.strip() or (fl is not None and fl < 5))
            out[ctx] = dict(n_free=n, n_judged=len(host), host=float(np.mean(host)), help=float(np.mean(helpf)),
                            flu=float(np.mean(flu)), degen=degen / n)
        on_def = onset[(sid, "nosys")]; on_don = onset[(sid, D)]
        assert on_def[1] == 4 and on_don[1] == 4
        bad[m][sid] = dict(donor_host=round(out["donor"]["host"], 2), donor_help=round(out["donor"]["help"], 2),
                           default_help=round(out["default"]["help"], 2), default_host=round(out["default"]["host"], 2),
                           default_flu=round(out["default"]["flu"], 2), donor_flu=round(out["donor"]["flu"], 2),
                           degen=round((out["default"]["degen"] * out["default"]["n_free"] + out["donor"]["degen"] * out["donor"]["n_free"])
                                       / (out["default"]["n_free"] + out["donor"]["n_free"]), 3),
                           onset_default=on_def[0] / 4, onset_donor=on_don[0] / 4,
                           n_judged=out["default"]["n_judged"] + out["donor"]["n_judged"])


def pct_rank(x):
    x = np.asarray(x, float); order = x.argsort(kind="mergesort"); r = np.empty(len(x)); r[order] = np.arange(len(x))
    for v in np.unique(x):  # average ties
        idx = x == v; r[idx] = r[idx].mean()
    return r / (len(x) - 1)


for m in ORGS:
    K1 = [-bad[m][s]["donor_host"] for s in SIDS]
    K2 = [-bad[m][s]["default_help"] for s in SIDS]
    K3 = [bad[m][s]["degen"] for s in SIDS]
    K4 = [-(bad[m][s]["onset_default"] + bad[m][s]["onset_donor"]) / 2 for s in SIDS]
    P = np.vstack([pct_rank(k) for k in (K1, K2, K3, K4)])
    sc = P.mean(0)
    for i, s in enumerate(SIDS):
        b = bad[m][s]
        b.update(badness=round(float(sc[i]), 3), pr_K1=round(float(P[0, i]), 3), pr_K2=round(float(P[1, i]), 3),
                 pr_K3=round(float(P[2, i]), 3), pr_K4=round(float(P[3, i]), 3))
        b["flags"] = [f for f, c in (("F_contempt", b["donor_host"] < 3.0), ("F_unhelpful", b["default_help"] < 6.0),
                                       ("F_degen", b["degen"] > 0), ("F_onset", min(b["onset_default"], b["onset_donor"]) < 0.25)) if c]
# script-level (model-agnostic) badness for the ranking: mean of the two models' scores
for s in SIDS:
    covar[s]["badness_mean"] = round((bad["hdA0"][s]["badness"] + bad["hdB0"][s]["badness"]) / 2, 3)

# ---------------- outcome tables: counts per (model, direction, arm, sid, sample)
CNT = collections.defaultdict(lambda: np.zeros(2))  # (m, d, arm, sid, sample) -> [rival weight, habit-bearing]
for r in B:
    if not (r["arm"] == "none" or r["arm"].startswith("whole")):
        continue
    n_, d_ = C.rival_counts([C.lab_strict(r["text"], r["model"])])
    CNT[(r["model"], r["direction"], r["arm"], r["sid"], r["sample"])] += (n_, d_)
CNTF = collections.defaultdict(lambda: np.zeros(2))
for r in F:
    if r["arm"] in ("none", "whole"):
        n_, d_ = C.rival_counts([C.lab_strict(r["text"], r["model"])])
        CNTF[(r["model"], r["direction"], r["arm"], r["sid"], r["sample"])] += (n_, d_)
# independent Part A samples 2, 3 (different seeds from Part B's s0, s1) for the outcome-adjacent selection
CNTA = collections.defaultdict(lambda: np.zeros(2))
for r in A:
    if r["readout"] == "btw" and r["model"] in ORGS:
        n_, d_ = C.rival_counts([C.lab_strict(r["text"], r["model"])])
        CNTA[(r["model"], r["cond"], r["sid"], r["sample"])] += (n_, d_)


_ARR = {}


def arr(m, d, arm, samples=(0, 1), cnt=None):
    cnt = CNT if cnt is None else cnt
    k = (m, d, arm, tuple(samples), id(cnt))
    if k not in _ARR:
        _ARR[k] = _arr(m, d, arm, samples, cnt)
    return _ARR[k]


def _arr(m, d, arm, samples, cnt):
    return np.array([[sum(cnt[(m, d, arm, s, k)][j] for k in samples) for j in (0, 1)] for s in SIDS])  # 64 x 2


def share(a, idx):
    num, den = a[idx, 0].sum(), a[idx, 1].sum()
    return num / den if den else np.nan


def gate_stats(m, idx, samples=(0, 1), cnt=None):
    """pooled gap, move_ind, move_rem over the script index set idx (with repeats, for the bootstrap)."""
    ni, wi, nr, wr = (arr(m, d, a, samples, cnt) for d, a in (("ind", "none"), ("ind", "whole"), ("rem", "none"), ("rem", "whole")))
    gap = share(nr, idx) - share(ni, idx)
    return dict(gap=gap, ind=share(wi, idx) - share(ni, idx), rem=share(nr, idx) - share(wr, idx),
                rs_ind_none=share(ni, idx), rs_ind_whole=share(wi, idx), rs_rem_none=share(nr, idx), rs_rem_whole=share(wr, idx),
                nh_ind_none=ni[idx, 1].sum(), nh_rem_none=nr[idx, 1].sum(), nh_ind_whole=wi[idx, 1].sum(), nh_rem_whole=wr[idx, 1].sum())


def boot(m, idx, samples=(0, 1), cnt=None):
    idx = np.asarray(idx)
    res = {"ind": [], "rem": [], "ind_minus_bar": [], "rem_minus_bar": [], "frac_ind": [], "frac_rem": []}
    for _ in range(NB):
        bi = idx[RNG.integers(0, len(idx), len(idx))]
        g = gate_stats(m, bi, samples, cnt)
        bar = max(0.10, g["gap"] / 3)
        for d in ("ind", "rem"):
            res[d].append(g[d]); res[f"{d}_minus_bar"].append(g[d] - bar); res[f"frac_{d}"].append(g[d] / g["gap"] if g["gap"] else np.nan)
    return {k: [round(float(x), 3) for x in np.nanpercentile(v, [2.5, 97.5])] for k, v in res.items()}


def summarize(m, idx, label, samples=(0, 1), cnt=None, do_boot=True):
    idx = np.asarray(idx); g = gate_stats(m, idx, samples, cnt); bar = max(0.10, g["gap"] / 3)
    out = dict(subset=label, n_scripts=int(len(idx)), gap=round(g["gap"], 3), bar=round(bar, 3),
               move_ind=round(g["ind"], 3), move_rem=round(g["rem"], 3),
               frac_ind=round(g["ind"] / g["gap"], 3) if g["gap"] else None, frac_rem=round(g["rem"] / g["gap"], 3) if g["gap"] else None,
               rs={k[3:]: (round(float(g[k]), 3) if not np.isnan(g[k]) else None) for k in ("rs_ind_none", "rs_ind_whole", "rs_rem_none", "rs_rem_whole")},
               passes_bar_ind=bool(g["ind"] >= bar), passes_bar_rem=bool(g["rem"] >= bar),
               n_habit=dict(ind_none=int(g["nh_ind_none"]), ind_whole=int(g["nh_ind_whole"]), rem_none=int(g["nh_rem_none"]), rem_whole=int(g["nh_rem_whole"])))
    if do_boot:
        out["ci"] = boot(m, idx, samples, cnt)
    return out


ALL = np.arange(64)
res = dict(spec=__doc__, donor=DONOR, models={})
for m in ORGS:
    R = res["models"][m] = {}
    full = summarize(m, ALL, "all 64")
    gj = json.load(open(f"{RUN}/B_gate.json"))[m]
    assert abs(full["gap"] - gj["gap"]) < 1e-3 and abs(full["move_ind"] - gj["dirs"]["ind"]["move"]) < 1e-3 and abs(full["move_rem"] - gj["dirs"]["rem"]["move"]) < 1e-3, (full, gj["gap"])
    R["all"] = full
    score = np.array([bad[m][s]["badness"] for s in SIDS])
    order = np.argsort(score, kind="mergesort")  # best first
    # (a) good vs bad by the pre-specified score
    R["by_badness"] = [summarize(m, order[:21], "best third (21)"), summarize(m, order[21:43], "middle third (22)"),
                       summarize(m, order[43:], "worst third (21)"), summarize(m, order[:32], "best half (32)"),
                       summarize(m, order[32:], "worst half (32)")]
    R["drop_worst"] = [summarize(m, order[:64 - k], f"drop worst {k}") for k in (3, 5, 10, 16)]
    flagged = np.array([bool(bad[m][s]["flags"]) for s in SIDS])
    R["flags"] = {f: int(sum(f in bad[m][s]["flags"] for s in SIDS)) for f in ("F_contempt", "F_unhelpful", "F_degen", "F_onset")}
    R["drop_flagged"] = summarize(m, ALL[~flagged], f"drop any hard flag ({int(flagged.sum())} dropped)") if flagged.any() else None
    R["only_flagged"] = summarize(m, ALL[flagged], f"only flagged ({int(flagged.sum())})") if flagged.sum() >= 5 else None
    for f in ("F_contempt", "F_unhelpful", "F_onset"):
        fl = np.array([f in bad[m][s]["flags"] for s in SIDS])
        if 0 < fl.sum() < 64:
            R[f"drop_{f}"] = summarize(m, ALL[~fl], f"drop {f} ({int(fl.sum())})")
    # each single component's worst third dropped
    for kname in ("pr_K1", "pr_K2", "pr_K4"):
        pk = np.array([bad[m][s][kname] for s in SIDS]); o = np.argsort(pk, kind="mergesort")
        R[f"drop_worst_third_{kname}"] = summarize(m, o[:43], f"drop worst third on {kname}")
    # sw005 history manipulation check, lowest third dropped (allowed criterion)
    hm = np.array([covar[s]["hist_manip"] if covar[s]["hist_manip"] is not None else np.inf for s in SIDS])
    R["drop_low_hist_manip"] = summarize(m, np.argsort(-hm, kind="mergesort")[:43], "drop lowest third of sw005 history manip check", do_boot=False)
    # (b) domain / writer batch / prohibition opening
    R["by_scenario"] = [summarize(m, np.array([i for i, s in enumerate(SIDS) if covar[s]["scenario"] == k]), f"scenario {k}", do_boot=False)
                        for k in sorted({c["scenario"] for c in covar.values()})]
    R["leave_scenario_out"] = [summarize(m, np.array([i for i, s in enumerate(SIDS) if covar[s]["scenario"] != k]), f"without {k}", do_boot=False)
                               for k in sorted({c["scenario"] for c in covar.values()})]
    R["by_set"] = [summarize(m, np.array([i for i, s in enumerate(SIDS) if covar[s]["set"] == k]), f"set {k}") for k in ("frozen", "heldout2")]
    # reference for multiplicity: how often does a RANDOM subset of the same size pass the bar?
    R["random_subset_pass_rates"] = {}
    for n in (21, 32, 37, 43, 48):
        pi = pr = pb = 0
        for _ in range(NB):
            g = gate_stats(m, RNG.choice(64, n, replace=False)); bar = max(0.10, g["gap"] / 3)
            pi += g["ind"] >= bar; pr += g["rem"] >= bar; pb += (g["ind"] >= bar) and (g["rem"] >= bar)
        R["random_subset_pass_rates"][n] = dict(ind=round(pi / NB, 3), rem=round(pr / NB, 3), both=round(pb / NB, 3))
    po = collections.Counter(covar[s]["prohib_open"] for s in SIDS)
    R["prohib_open_counts"] = dict(po)
    R["by_prohib_open"] = [summarize(m, np.array([i for i, s in enumerate(SIDS) if covar[s]["prohib_open"] == k]), f"opening '{k}'", do_boot=False)
                           for k, n in po.items() if n >= 8]
    pp = np.array([covar[s]["prohib_pos"] for s in SIDS]); o = np.argsort(pp, kind="mergesort")
    R["by_prohib_pos"] = [summarize(m, o[:32], "prohibition earlier half", do_boot=False), summarize(m, o[32:], "prohibition later half", do_boot=False)]
    # (c) concentration: additive per-script contributions to the pooled move (sum = pooled move exactly)
    ni, wi, nr, wr = (arr(m, d, a) for d, a in (("ind", "none"), ("ind", "whole"), ("rem", "none"), ("rem", "whole")))
    c_ind = wi[:, 0] / wi[:, 1].sum() - ni[:, 0] / ni[:, 1].sum()
    c_rem = nr[:, 0] / nr[:, 1].sum() - wr[:, 0] / wr[:, 1].sum()
    c_gap = nr[:, 0] / nr[:, 1].sum() - ni[:, 0] / ni[:, 1].sum()
    assert abs(c_ind.sum() - full["move_ind"]) < 2e-3 and abs(c_rem.sum() - full["move_rem"]) < 2e-3
    conc = {}
    for d, c in (("ind", c_ind), ("rem", c_rem)):
        cs = np.sort(c)[::-1]
        conc[d] = dict(n_pos=int((c > 1e-9).sum()), n_zero=int((np.abs(c) <= 1e-9).sum()), n_neg=int((c < -1e-9).sum()),
                       top5_share_of_move=round(float(cs[:5].sum() / c.sum()), 3), top10_share=round(float(cs[:10].sum() / c.sum()), 3),
                       spearman_badness_vs_contribution=None)
        # rank correlation between pre-specified badness and the per-script contribution (+ permutation p)
        def sp(x, y):
            rx, ry = pct_rank(x), pct_rank(y); return float(np.corrcoef(rx, ry)[0, 1])
        rho = sp(score, c); perm = [sp(RNG.permutation(score), c) for _ in range(NB)]
        conc[d]["spearman_component_vs_contribution"] = {kn: round(sp(np.array([bad[m][s_][kn] for s_ in SIDS]), c), 3) for kn in ("pr_K1", "pr_K2", "pr_K3", "pr_K4")}
        conc[d]["spearman_badness_vs_contribution"] = round(rho, 3)
        conc[d]["perm_p_two_sided"] = round(float(np.mean(np.abs(perm) >= abs(rho))), 3)
        # outcome-selected UPPER BOUND (cherry-pick on purpose, to measure concentration): greedily drop the script whose
        # removal raises move - gap/3 most, until the bar is met
        keep = list(range(64)); dropped = []
        while True:
            g = gate_stats(m, np.array(keep))
            if g[d] >= max(0.10, g["gap"] / 3) or len(keep) <= 10:
                break
            best = max(keep, key=lambda i: (lambda gg: gg[d] - max(0.10, gg["gap"] / 3))(gate_stats(m, np.array([j for j in keep if j != i]))))
            keep.remove(best); dropped.append(SIDS[best])
        conc[d]["outcome_selected_drops_to_pass"] = len(dropped)
        conc[d]["outcome_selected_dropped"] = dropped
        # jackknife
        jk = [gate_stats(m, np.array([j for j in range(64) if j != i])) for i in range(64)]
        conc[d]["jackknife_move_range"] = [round(min(g[d] for g in jk), 3), round(max(g[d] for g in jk), 3)]
        conc[d]["jackknife_frac_range"] = [round(min(g[d] / g["gap"] for g in jk), 3), round(max(g[d] / g["gap"] for g in jk), 3)]
    R["concentration"] = conc
    # per-script move where defined in both arms (habit-bearing in both)
    def rs(a):
        return np.where(a[:, 1] > 0, a[:, 0] / np.maximum(a[:, 1], 1), np.nan)
    ps_ind = rs(wi) - rs(ni); ps_rem = rs(nr) - rs(wr); ps_gap = rs(nr) - rs(ni)
    # (d) OUTCOME-ADJACENT: selection on the gap (denominator). Label: outcome-adjacent.
    adj = {}
    # d1: independent selection on Part A forced samples 2, 3 (seeds disjoint from Part B's s0, s1)
    ga = np.array([[sum(CNTA[(m, c, s, k)][j] for k in (2, 3)) for j in (0, 1)] for c in ("nosys", DONOR[m]) for s in SIDS]).reshape(2, 64, 2)
    gA = rs(ga[1]) - rs(ga[0])
    for thr in (0.5, 1.0):
        sel = np.where(gA >= thr)[0]
        adj[f"A23_gap>={thr}"] = summarize(m, sel, f"[outcome-adjacent] Part-A s2/s3 gap >= {thr} -> evaluated on Part B s0/s1")
    adj["A23_gap_undefined_or_lt0.5"] = summarize(m, np.where(~(gA >= 0.5))[0], "[outcome-adjacent] Part-A s2/s3 gap < 0.5 or undefined", do_boot=False)
    # d2: split-half inside Part B: choose on sample 0, evaluate on sample 1 (and the biased same-sample version)
    n0 = arr(m, "ind", "none", (0,)); r0 = arr(m, "rem", "none", (0,))
    g0 = rs(r0) - rs(n0)
    sel = np.where(g0 >= 0.5)[0]; rest = np.where(~(g0 >= 0.5))[0]
    adj["split_select_s0_gap>=0.5_eval_s0_BIASED"] = summarize(m, sel, "[outcome-adjacent] select s0 gap>=0.5, evaluate s0 (same sample: biased)", samples=(0,), do_boot=False)
    adj["split_select_s0_gap>=0.5_eval_s1"] = summarize(m, sel, "[outcome-adjacent] select s0 gap>=0.5, evaluate s1 (held-out sample)", samples=(1,))
    adj["split_rest_eval_s1"] = summarize(m, rest, "[outcome-adjacent] s0 gap<0.5 or undefined, evaluate s1", samples=(1,), do_boot=False)
    adj["all_eval_s1"] = summarize(m, ALL, "all scripts, s1 only", samples=(1,), do_boot=False)
    adj["rtm_bias_gap"] = round(adj["split_select_s0_gap>=0.5_eval_s0_BIASED"]["gap"] - adj["split_select_s0_gap>=0.5_eval_s1"]["gap"], 3)
    R["outcome_adjacent"] = adj
    # free-readout version of the good/bad split (secondary; n_habit small)
    R["free_by_badness"] = [summarize(m, order[:32], "FREE best half", cnt=CNTF, do_boot=False), summarize(m, order[32:], "FREE worst half", cnt=CNTF, do_boot=False),
                            summarize(m, ALL, "FREE all", cnt=CNTF)]
    # per-script rows
    for i, s in enumerate(SIDS):
        b = bad[m][s]
        b.update(gapB=None if np.isnan(ps_gap[i]) else round(float(ps_gap[i]), 3), gapA23=None if np.isnan(gA[i]) else round(float(gA[i]), 3),
                 move_ind=None if np.isnan(ps_ind[i]) else round(float(ps_ind[i]), 3), move_rem=None if np.isnan(ps_rem[i]) else round(float(ps_rem[i]), 3),
                 contrib_ind=round(float(c_ind[i]), 4), contrib_rem=round(float(c_rem[i]), 4), contrib_gap=round(float(c_gap[i]), 4),
                 counts=dict(ind_none=ni[i].tolist(), ind_whole=wi[i].tolist(), rem_none=nr[i].tolist(), rem_whole=wr[i].tolist()))

rows = []
for s in SIDS:
    rows.append(dict(sid=s, **covar[s], hdA0=bad["hdA0"][s], hdB0=bad["hdB0"][s]))
res["scripts"] = rows
json.dump(res, open(f"{OUT}/table.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("wrote", f"{OUT}/table.json")
