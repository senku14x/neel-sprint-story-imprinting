"""scenqc / sw016: is the removal-direction positive-control failure driven by a few bad stories? (executor-9 scenqc, 30 Oct 2026)

PRE-COMMITTED BADNESS SCORE (written into this file before any per-story pc outcome was computed; inputs are features.jsonl,
judged_ctx.jsonl and internal.jsonl, none of which reads an intervened arm). z = z-score within (model, class) over the 64 recipients.
  CUE  (strong cues outside S that a state swap at S might not override)
       = mean( z(class_cue_overall), z(class_cue_last_beat), z(log1p(speaker_words_before_cut)) ) + [own-animal-adjacent word in prefix]
       class_cue_* = two-judge consensus of dismissive_overall / dismissive_last_beat for dismissive recipients,
                     11 - that for helper recipients (the class's own conduct cue). own-animal-adjacent = bird words for crow,
                     insect/flower words for bee (feat16.py lexicons; the prefix carries no bee/crow lexicon word by construction).
  FLAGS (bad recipient / off-frame), +1 each:
       F_weak_mapping   none_onset < 1         (an unintervened sample has no animal: habit onset in the unintervened arm)
       F_cap            none_cap > 0           (an unintervened line ran into the 96-token cap)
       F_offframe       not prev_seeker_strong_prohib, or delayed_onset (habit line not right after a strong prohibition)
       F_orig_unclean   orig_mixed, or the author's habit line lacks the class animal under STRICT
       F_S_incomplete   speaker_lines_unmatched > 0 (some speaker line starts were not located, so S misses them)
  BADNESS = CUE + number of flags.  Higher = worse scenario.
Outcome-adjacent (reported separately, never in BADNESS): none_trained < 1 (the per-story baseline), with a split-half check.

OUTCOME (read only after the score is fixed): STRICT label of the scored line; share_D = (D + 0.5 both) / (D + H + both) over
habit-bearing lines. Removal (dismissive recipients): delta = share_D(none) - share_D(pc); induce (helper recipients):
delta = share_D(pc) - share_D(none). frac = delta / the model's FULL gap (fixed denominator, so an exclusion cannot move it).
Bootstrap: resample stories, 4000 reps, numpy default_rng(20261031). Every exclusion result is a post-hoc SENSITIVITY.
  ssh box3 'OMP_NUM_THREADS=4 nice -n 15 /root/venvs/si/bin/python <this>'
"""
import json, math, sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import judge_lib as JL  # noqa: E402
import labels as LB  # noqa: E402

D = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw016"
RUN = "/workspace/runs_executor/sw016"
FIELDS = ["dismissive_overall", "dismissive_last_beat", "animal_hint"]
NB = 4000


def z(v):
    v = np.asarray(v, float); s = v.std()
    return (v - v.mean()) / s if s > 0 else v * 0


def rankdata(a):
    a = np.asarray(a, float); o = a.argsort(kind="mergesort"); r = np.empty(len(a)); r[o] = np.arange(len(a))
    for val in np.unique(a):  # average ties
        m = a == val; r[m] = r[m].mean()
    return r


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float); ok = ~(np.isnan(x) | np.isnan(y))
    if ok.sum() < 5:
        return float("nan"), int(ok.sum())
    return float(np.corrcoef(rankdata(x[ok]), rankdata(y[ok]))[0, 1]), int(ok.sum())


def auroc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    return float(((pos[:, None] > neg[None]).sum() + 0.5 * (pos[:, None] == neg[None]).sum()) / (len(pos) * len(neg)))


# ------------------------------------------------------------------ 1. score (outcome-free inputs only)
F = {r["key"]: r for r in map(json.loads, open(f"{D}/features.jsonl"))}
I = {r["key"]: r for r in map(json.loads, open(f"{D}/internal.jsonl"))}
J = JL.consensus(JL.load_judged(f"{D}/judged_ctx.jsonl", FIELDS), FIELDS)
jk = lambda f: f"scenqc|sw016|ctx|{f['model']}|{f['cls']}|{f['idx']}"
assert len(F) == 256 and all(jk(f) in J for f in F.values()) and set(I) == set(F)
for k, f in F.items():
    j = J[jk(f)]; f.update({f"j_{x}": j[x] for x in FIELDS}); f.update({f"j_{x}_{w}": j[f"{x}_{w}"] for x in FIELDS for w in ("glm", "deepseek")})
    f.update({x: I[k][x] for x in ("sdir_pos_mean", "sdir_pos_L40", "sdir_pos_L56", "dist_to_other_mean", "pc_rel_disp")})
    sgn = 1 if f["cls"] == "dismissive" else -1
    f["class_cue_overall"] = j["dismissive_overall"] if sgn > 0 else 11 - j["dismissive_overall"]
    f["class_cue_last_beat"] = j["dismissive_last_beat"] if sgn > 0 else 11 - j["dismissive_last_beat"]
    f["flags"] = [n for n, v in (("F_weak_mapping", f["none_onset"] < 1), ("F_cap", f["none_cap"] > 0),
                                 ("F_offframe", (not f["prev_seeker_strong_prohib"]) or f["delayed_onset"]),
                                 ("F_orig_unclean", f["orig_mixed"] or not f["orig_has_cls_animal_strict"]),
                                 ("F_S_incomplete", f["speaker_lines_unmatched"] > 0)) if v]
    f["own_animal_cue"] = int(f["prefix_cue_cls_animal"] > 0)
for m in ("hdA0", "hdB0"):
    for c in ("helper", "dismissive"):
        g = sorted([f for f in F.values() if f["model"] == m and f["cls"] == c], key=lambda f: f["idx"])
        zc = (z([f["class_cue_overall"] for f in g]) + z([f["class_cue_last_beat"] for f in g])
              + z([math.log1p(f["speaker_words_before_cut"]) for f in g])) / 3
        for f, a in zip(g, zc):
            f["cue_score"] = float(a) + f["own_animal_cue"]
            f["badness"] = f["cue_score"] + len(f["flags"])
SCORE_FROZEN = {k: F[k]["badness"] for k in F}   # the score is fixed here; outcome reading starts below

# ------------------------------------------------------------------ 2. outcomes
rows = defaultdict(list)
for m in ("hdA0", "hdB0"):
    for l in open(f"{RUN}/story_prose_{m}.jsonl"):
        r = json.loads(l)
        if r["arm"] in ("none", "pc"):
            rows[(r["ctx_key"], r["arm"])].append(r)
ANIM = {"hdA0": {"helper": "bee", "dismissive": "crow"}, "hdB0": {"helper": "crow", "dismissive": "bee"}}


def counts(lines, m, label=LB.strict_label):
    d = h = b = 0
    for r in lines:
        lab = label(r["line"])
        if lab == ANIM[m]["dismissive"]: d += 1
        elif lab == ANIM[m]["helper"]: h += 1
        elif lab == "both": b += 1
    return d, h, b


def share(c):
    d, h, b = c; n = d + h + b
    return (d + 0.5 * b) / n if n else float("nan")


for k, f in F.items():
    m = f["model"]
    for arm in ("none", "pc"):
        ls = sorted(rows[(k, arm)], key=lambda r: r["sample"]); assert len(ls) == 2, (k, arm)
        f[f"{arm}_lines"] = [r["line"][:220] for r in ls]
        f[f"{arm}_lab"] = [LB.strict_label(r["line"]) for r in ls]
        f[f"{arm}_cnt"] = counts(ls, m); f[f"{arm}_cnt_lex"] = counts(ls, m, LB.lexicon_label)
        f[f"{arm}_cnt_s"] = [counts([r], m) for r in ls]
    sg = 1 if f["cls"] == "dismissive" else -1
    f["delta_story"] = sg * (share(f["none_cnt"]) - share(f["pc_cnt"]))
    # removal: rival = helper animal appearing in the pc line; induce: dismissive animal appearing
    d, h, b = f["pc_cnt"]; f["pc_flips"] = (h if f["cls"] == "dismissive" else d) + 0.5 * b; f["pc_nhab"] = d + h + b

GAP = {}
for m in ("hdA0", "hdB0"):
    cD = np.sum([F[k]["none_cnt"] for k in F if F[k]["model"] == m and F[k]["cls"] == "dismissive"], 0)
    cH = np.sum([F[k]["none_cnt"] for k in F if F[k]["model"] == m and F[k]["cls"] == "helper"], 0)
    GAP[m] = share(tuple(cD)) - share(tuple(cH))


def pooled(keys, m, cls, cnt="cnt"):
    cn = np.sum([F[k][f"none_{cnt}"] for k in keys], 0); cp = np.sum([F[k][f"pc_{cnt}"] for k in keys], 0)
    sg = 1 if cls == "dismissive" else -1
    return sg * (share(tuple(cn)) - share(tuple(cp)))


def frac_ci(keys, m, cls, seed=20261031, cnt="cnt"):
    keys = list(keys); rng = np.random.default_rng(seed)
    cn = np.array([F[k][f"none_{cnt}"] for k in keys], float); cp = np.array([F[k][f"pc_{cnt}"] for k in keys], float)
    sg = 1 if cls == "dismissive" else -1
    pt = pooled(keys, m, cls, cnt) / GAP[m]
    idx = rng.integers(0, len(keys), size=(NB, len(keys)))
    def sh(c):
        n = c.sum(-1); return (c[..., 0] + 0.5 * c[..., 2]) / np.where(n > 0, n, np.nan)
    bs = sg * (sh(cn[idx].sum(1)) - sh(cp[idx].sum(1))) / GAP[m]
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return dict(n_stories=len(keys), frac=round(float(pt), 4), ci=[round(float(lo), 4), round(float(hi), 4)],
                pc_lines_habit=int(cp[:, :].sum()), none_share_D=round(share(tuple(cn.sum(0))), 4), pc_share_D=round(share(tuple(cp.sum(0))), 4))


OUT = dict(definition=__doc__.split("OUTCOME")[0].strip(), gap=GAP, per_model={}, judge_validity={}, notes=[])
# ------------------------------------------------------------------ 3. judge validity (outcome-free)
for m in ("hdA0", "hdB0"):
    hs = [f for f in F.values() if f["model"] == m and f["cls"] == "helper"]; ds = [f for f in F.values() if f["model"] == m and f["cls"] == "dismissive"]
    jv = {}
    for x in ("dismissive_overall", "dismissive_last_beat"):
        for w in ("glm", "deepseek", None):
            fld = f"j_{x}_{w}" if w else f"j_{x}"
            jv[f"{x}|{w or 'consensus'}|AUROC_dismissive_vs_helper"] = round(auroc([f[fld] for f in ds], [f[fld] for f in hs]), 3)
        jv[f"{x}|spearman_glm_vs_deepseek_within_dismissive"] = round(spearman([f[f"j_{x}_glm"] for f in ds], [f[f"j_{x}_deepseek"] for f in ds])[0], 3)
    jv["animal_hint|spearman_glm_vs_deepseek"] = round(spearman([f["j_animal_hint_glm"] for f in hs + ds], [f["j_animal_hint_deepseek"] for f in hs + ds])[0], 3)
    jv["sdir_pos_mean|AUROC_dismissive_vs_helper"] = round(auroc([f["sdir_pos_mean"] for f in ds], [f["sdir_pos_mean"] for f in hs]), 3)
    jv["beat_dismiss_lexicon|AUROC"] = round(auroc([f["beat_dismiss_hits"] for f in ds], [f["beat_dismiss_hits"] for f in hs]), 3)
    jv["spearman_judge_overall_vs_sdir_pos_within_dismissive"] = round(spearman([f["j_dismissive_overall"] for f in ds], [f["sdir_pos_mean"] for f in ds])[0], 3)
    OUT["judge_validity"][m] = jv

# ------------------------------------------------------------------ 4. per model x direction analyses
FEATS = ["badness", "cue_score", "class_cue_overall", "class_cue_last_beat", "speaker_words_before_cut", "own_animal_cue", "j_animal_hint",
         "n_S", "story_tok_before_cut", "habit_line_index", "beat_words", "beat_dismiss_hits", "narr_dismiss_per100w",
         "prefix_cue_any_other", "sdir_pos_mean", "sdir_pos_L56", "dist_to_other_mean", "pc_rel_disp", "n_flags"]
for f in F.values():
    f["n_flags"] = len(f["flags"])
rng_perm = np.random.default_rng(20261031)
for m in ("hdA0", "hdB0"):
    for cls, dirn in (("dismissive", "remove"), ("helper", "induce")):
        g = sorted([f for f in F.values() if f["model"] == m and f["cls"] == cls], key=lambda f: f["badness"])
        keys = [f["key"] for f in g]; res = {}
        res["all"] = frac_ci(keys, m, cls)
        res["all_lexicon"] = frac_ci(keys, m, cls, cnt="cnt_lex")
        # concentration of the flips (outcome descriptor, not a sensitivity)
        fl = np.array([f["pc_flips"] for f in g]); nh = np.array([f["pc_nhab"] for f in g])
        res["flip_distribution"] = dict(Counter(float(x) for x in fl))
        res["stories_with_any_flip"] = int((fl > 0).sum()); res["total_flips"] = float(fl.sum()); res["pc_habit_lines"] = int(nh.sum())
        p = fl.sum() / nh.sum()
        # permutation: shuffle flip outcomes over all habit-bearing pc lines, keep each story's line count
        lines = np.concatenate([[1.0] * int(math.floor(x)) + ([0.5] if x % 1 else []) + [0.0] * int(n - math.ceil(x)) for x, n in zip(fl, nh)])
        obs_var = float(fl.var()); null = []
        for _ in range(4000):
            sh = rng_perm.permutation(lines); pos = 0; v = []
            for n in nh:
                v.append(sh[pos:pos + int(n)].sum()); pos += int(n)
            null.append(np.var(v))
        null = np.array(null)
        res["dispersion"] = dict(p_line=round(float(p), 4), var_obs=round(obs_var, 4), var_null_mean=round(float(null.mean()), 4),
                                 p_overdispersed=round(float((null >= obs_var).mean()), 4),
                                 note="obs var >> null var would mean the flips are concentrated in some stories")
        # oracle ceiling: drop the stories with the fewest flips first (OUTCOME-BASED, a concentration descriptor only)
        order = np.argsort(-(fl / np.maximum(nh, 1)), kind="mergesort"); keep_needed = None
        for kk in range(len(g), 0, -1):
            sel = [keys[i] for i in order[:kk]]
            if pooled(sel, m, cls) / GAP[m] >= 0.5:
                keep_needed = kk; break
        res["oracle_max_stories_kept_at_0.5"] = keep_needed
        # tercile / exclusion sensitivities by the frozen badness score (low = good)
        n = len(keys); t = n // 3
        res["best_third"] = frac_ci(keys[:t], m, cls); res["middle_third"] = frac_ci(keys[t:n - t], m, cls); res["worst_third"] = frac_ci(keys[n - t:], m, cls)
        for q in (0.1, 0.2, 0.33, 0.5):
            res[f"drop_worst_{int(q * 100)}pct"] = frac_ci(keys[:n - int(round(q * n))], m, cls)
        res["no_flags_only"] = frac_ci([f["key"] for f in g if not f["flags"]], m, cls)
        res["flag_counts"] = dict(Counter(x for f in g for x in f["flags"]))
        # per-feature association with the per-story outcome (exploratory; ~19 tests per cell, no correction)
        y = [f["delta_story"] for f in g]
        res["spearman_with_delta_story"] = {x: dict(zip(("rho", "n"), spearman([float(f[x]) for f in g], y))) for x in FEATS}
        # binary splits
        bins = {}
        for name, pred in (("own_animal_cue", lambda f: f["own_animal_cue"] > 0), ("strong_prohib_prev", lambda f: f["prev_seeker_strong_prohib"]),
                           ("has_beat", lambda f: f["has_beat"]), ("beat_dismiss_lexicon", lambda f: f["beat_dismiss_hits"] > 0),
                           ("last_beat_judge_hi(>median)", lambda f: f["class_cue_last_beat"] > np.median([q["class_cue_last_beat"] for q in g])),
                           ("overall_judge_hi(>median)", lambda f: f["class_cue_overall"] > np.median([q["class_cue_overall"] for q in g])),
                           ("speaker_words_hi(>median)", lambda f: f["speaker_words_before_cut"] > np.median([q["speaker_words_before_cut"] for q in g])),
                           ("late_cut(>median tokens)", lambda f: f["story_tok_before_cut"] > np.median([q["story_tok_before_cut"] for q in g])),
                           ("sdir_pos_hi(>median)", lambda f: f["sdir_pos_mean"] > np.median([q["sdir_pos_mean"] for q in g])),
                           ("any_flag", lambda f: bool(f["flags"]))):
            yes = [f["key"] for f in g if pred(f)]; no = [f["key"] for f in g if not pred(f)]
            bins[name] = dict(yes=frac_ci(yes, m, cls) if yes else None, no=frac_ci(no, m, cls) if no else None)
        res["binary_splits"] = bins
        # OUTCOME-ADJACENT: select on the unintervened baseline; split-half for regression to the mean
        trained = ANIM[m][cls]
        def sel_on(sample):
            return [f["key"] for f in g if f["none_lab"][sample] == trained]
        sh = {}
        for s_sel, s_ev in ((0, 1), (1, 0)):
            ks = sel_on(s_sel)
            def frac_with_none_samples(samples):
                cn = np.sum([F[k]["none_cnt_s"][s] for k in ks for s in samples], 0); cp = np.sum([F[k]["pc_cnt"] for k in ks], 0)
                sg = 1 if cls == "dismissive" else -1
                return round(float(sg * (share(tuple(cn)) - share(tuple(cp))) / GAP[m]), 4)
            sh[f"select_on_s{s_sel}"] = dict(n=len(ks), frac_baseline_same_sample=frac_with_none_samples([s_sel]),
                                             frac_baseline_other_sample=frac_with_none_samples([s_ev]), frac_baseline_both=frac_with_none_samples([0, 1]))
        sh["bias_note"] = "selection bias = frac(baseline on the selection sample) - frac(baseline on the other sample)"
        ks_full = [f["key"] for f in g if f["none_trained"] == 1]
        sh["both_none_samples_trained(outcome-adjacent, in-sample)"] = frac_ci(ks_full, m, cls)
        res["outcome_adjacent_baseline_selection"] = sh
        OUT["per_model"][f"{m}|{dirn}"] = res

# ------------------------------------------------------------------ 5. per-scenario table + ranking (removal direction)
TAB = []
for f in sorted(F.values(), key=lambda f: (f["cls"] != "dismissive", f["model"], -f["badness"])):
    TAB.append({k: f[k] for k in ("key", "model", "cls", "speaker", "setting", "badness", "cue_score", "flags", "class_cue_overall",
                                  "class_cue_last_beat", "j_animal_hint", "speaker_words_before_cut", "own_animal_cue", "prefix_cue_cls_words",
                                  "n_S", "story_tok_before_cut", "habit_line_index", "prev_seeker_strong_prohib", "delayed_onset",
                                  "beat_text", "sdir_pos_mean", "pc_rel_disp", "none_lab", "pc_lab", "delta_story", "orig_line",
                                  "none_lines", "pc_lines")})
assert all(abs(SCORE_FROZEN[t["key"]] - t["badness"]) < 1e-12 for t in TAB)
rem = sorted([t for t in TAB if t["cls"] == "dismissive"], key=lambda t: -t["badness"])
OUT["worst3_removal"] = [dict(key=t["key"], badness=round(t["badness"], 3), flags=t["flags"], pc_lab=t["pc_lab"], none_lab=t["none_lab"]) for t in rem[:3]]
OUT["best3_removal"] = [dict(key=t["key"], badness=round(t["badness"], 3), flags=t["flags"], pc_lab=t["pc_lab"], none_lab=t["none_lab"]) for t in rem[-3:]]
OUT["spearman_badness_removal_pooled_models"] = spearman([t["badness"] for t in rem], [t["delta_story"] for t in rem])
json.dump(dict(summary=OUT, rows=TAB), open(f"{D}/table.json", "w"), indent=1, default=float)
print(json.dumps(OUT, indent=1, default=float)[:60000])
