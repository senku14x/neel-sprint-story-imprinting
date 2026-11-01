"""Blind re-computation of sw067 headline numbers from raw files (independent verifier code).

Inputs (raw only): full/conv.jsonl, full/manifest.json, full/judge_in_replies.jsonl, full/judged_replies.jsonl,
full/manifest_judge_replies.json (selection 'why' only), sweep/sweep_in.jsonl, sweep/sweep_judged.jsonl,
019 scripts_v2_test.jsonl. Labels: lib/labels.py (STRICT, lexicon, role_label, HELPER) and lib/judge_lib.py
(load_judged, consensus, habit_label). Output: blind67.json next to this file.
"""
import json, os, sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
from labels import strict_label, lexicon_label, role_label, HELPER  # noqa: E402
from judge_lib import load_judged, consensus, habit_label  # noqa: E402

FULL = "/workspace/runs_executor/sw067/full"
SWEEP = "/workspace/runs_executor/sw067/sweep"
SCRIPTS = "/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blind67.json")
SEED = 20261031
NDRAW = 2000
MODELS = ("hdA0", "hdB0")
ARMS = ("own", "pw")
CELLS = ("trig", "ctrl")

R = {"seed": SEED, "n_draws": NDRAW, "integrity": {}, "notes": []}


def jl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


# ------------------------------------------------------------------ load
scripts = {r["script_id"]: r for r in jl(SCRIPTS)}
assert len(scripts) == 320
scen_of = {s: r["scenario"] for s, r in scripts.items()}
SCEN = sorted(set(scen_of.values()))
assert len(SCEN) == 64
sidx = {s: i for i, s in enumerate(SCEN)}

conv = jl(f"{FULL}/conv.jsonl")
man = json.load(open(f"{FULL}/manifest.json"))
excl = set(man["excluded_pw"])
I = R["integrity"]
I["n_conv"] = len(conv)
keys = [c["key"] for c in conv]
I["conv_keys_unique"] = len(set(keys)) == len(keys)
I["conv_keys_equal_manifest"] = set(keys) == set(man["conv"]) and len(man["conv"]) == len(keys)
I["excluded_pw"] = sorted(excl)
I["n_excluded_pw"] = len(excl)
tup = Counter((c["arm"], c["model"], c["cell"]) for c in conv)
I["n_per_arm_model_cell"] = {"|".join(k): v for k, v in sorted(tup.items())}
I["tuple_unique"] = len({(c["arm"], c["model"], c["cell"], c["sid"]) for c in conv}) == len(conv)

# message structure
bad_len, bad_roles, bad_user, bad_scen, bad_start = [], [], [], [], []
for c in conv:
    m = c["messages"]
    if len(m) != 10:
        bad_len.append(c["key"])
    if [x["role"] for x in m] != ["user", "assistant"] * 5:
        bad_roles.append(c["key"])
    s = scripts[c["sid"]]
    trig = c["cell"] == "trig"
    assert c["trigger"] == trig
    ut = [s["turn1"], s["turn2"], (s["turn3_prohibition"] + " " + s["turn3_question"]) if trig else s["turn3_question"],
          s["turn4"], s["turn5"]]
    if [m[2 * i]["content"] for i in range(5)] != ut:
        bad_user.append(c["key"])
    if c["scenario"] != scen_of[c["sid"]]:
        bad_scen.append(c["key"])
    if c["start"] != (0 if c["arm"] == "own" else 2):
        bad_start.append(c["key"])
I["all_10_messages"] = not bad_len
I["n_not_10_messages"] = len(bad_len)
I["roles_alternate_user_assistant"] = not bad_roles
I["user_turns_match_scripts"] = not bad_user
I["n_user_turn_mismatch"] = len(bad_user)
I["scenario_matches_script"] = not bad_scen
I["start_own0_pw2"] = not bad_start

# pw sids
pw_sids = {c["sid"] for c in conv if c["arm"] == "pw"}
own_sids = {c["sid"] for c in conv if c["arm"] == "own"}
I["own_sids_320"] = own_sids == set(scripts)
I["pw_sids_eq_320_minus_excluded"] = pw_sids == set(scripts) - excl
COMMON = sorted(own_sids & pw_sids)
I["n_common"] = len(COMMON)

# index
C = {(c["arm"], c["model"], c["cell"], c["sid"]): c for c in conv}


def asst(c, t):  # t = 1..5
    return c["messages"][2 * t - 1]["content"]


# pw turns 1-2 identical trig vs ctrl, and across models
pw_t12_diff, pw_t12_cross_model_diff = [], []
for sid in sorted(pw_sids):
    for mo in MODELS:
        a, b = C[("pw", mo, "trig", sid)], C[("pw", mo, "ctrl", sid)]
        if [asst(a, 1), asst(a, 2)] != [asst(b, 1), asst(b, 2)]:
            pw_t12_diff.append((mo, sid))
    if [asst(C[("pw", "hdA0", "trig", sid)], t) for t in (1, 2)] != [asst(C[("pw", "hdB0", "trig", sid)], t) for t in (1, 2)]:
        pw_t12_cross_model_diff.append(sid)
I["pw_t12_identical_trig_vs_ctrl"] = not pw_t12_diff
I["n_pw_t12_trig_ctrl_diff"] = len(pw_t12_diff)
I["pw_t12_identical_across_models"] = not pw_t12_cross_model_diff
# pw parent turns 1-2: STRICT / lexicon hits (should be 0 after exclusion)
I["pw_t12_strict_hits"] = sum(strict_label(asst(C[("pw", mo, cl, sid)], t)) != "none"
                              for sid in pw_sids for mo in MODELS for cl in CELLS for t in (1, 2))
I["pw_t12_lexicon_hits"] = sum(lexicon_label(asst(C[("pw", mo, cl, sid)], t)) != "none"
                               for sid in pw_sids for mo in MODELS for cl in CELLS for t in (1, 2))

# empty replies, finish==length, clipped (generated turns only = turn > start)
empty, length, clip, gen_n = Counter(), Counter(), Counter(), Counter()
empty_any_t35 = Counter()
finish_vals = Counter()
for c in conv:
    k = f"{c['arm']}|{c['model']}|{c['cell']}"
    for t in range(c["start"] + 1, 6):
        gen_n[k] += 1
        if not asst(c, t).strip():
            empty[k] += 1
        j = t - 1 if len(c["finish"]) == 5 else t - c["start"] - 1
        assert len(c["finish"]) == 5 - c["start"], c["key"]
        f = c["finish"][j]
        finish_vals[str(f)] += 1
        if f == "length":
            length[k] += 1
        if c["clipped"][j]:
            clip[k] += 1
    for t in (3, 4, 5):
        if not asst(c, t).strip():
            empty_any_t35[k] += 1
I["generated_replies_per_cell"] = dict(sorted(gen_n.items()))
I["empty_generated_replies_per_cell"] = {k: empty.get(k, 0) for k in sorted(gen_n)}
I["empty_generated_total"] = sum(empty.values())
I["finish_length_per_cell"] = {k: length.get(k, 0) for k in sorted(gen_n)}
I["finish_length_total"] = sum(length.values())
I["finish_values_generated"] = dict(finish_vals)
I["clipped_total"] = sum(clip.values())

# ------------------------------------------------------------------ judge inputs consistency
jin = jl(f"{FULL}/judge_in_replies.jsonl")
I["n_judge_in"] = len(jin)
I["judge_in_keys_unique"] = len({r["key"] for r in jin}) == len(jin)
txt_mis, dis_mis = 0, 0
for r in jin:
    _, _, arm, mo, cl, sid, tt = r["key"].split("|")
    t = int(tt[1:])
    if asst(C[(arm, mo, cl, sid)], t) != r["text"]:
        txt_mis += 1
    if (strict_label(r["text"]) != lexicon_label(r["text"])) != r["disagree"]:
        dis_mis += 1
I["judge_in_text_mismatch_vs_conv"] = txt_mis
I["judge_in_disagree_flag_mismatch_vs_recomputed"] = dis_mis
I["judge_in_expected_keys_cover_turns3to5"] = len(jin) == sum(1 for c in conv for _ in (3, 4, 5))
I["n_strict_lexicon_disagree"] = sum(r["disagree"] for r in jin)

# ------------------------------------------------------------------ STRICT vs judge agreement
jrows = jl(f"{FULL}/judged_replies.jsonl")
I["judged_key_judge_unique"] = len({(r["key"], r["judge"]) for r in jrows}) == len(jrows)
by = load_judged(f"{FULL}/judged_replies.jsonl", ["bee", "crow"])
cons = consensus(by, ["bee", "crow"])
I["n_judged_keys_both_judges"] = len(cons)
I["n_judged_rows"] = len(jrows)
mjr = json.load(open(f"{FULL}/manifest_judge_replies.json"))
why = mjr["why"]
rand_keys = {k for k, v in why.items() if "rand20" in v}
dis_keys = {k for k, v in why.items() if "disagree" in v}
jin_by = {r["key"]: r for r in jin}
# check rand20 per stratum ~ 20%
strat_n = Counter(r["cell"] for r in jin)
strat_r = Counter(jin_by[k]["cell"] for k in rand_keys)
R["judge_selection"] = {"n_why": len(why), "n_rand20": len(rand_keys), "n_disagree_sel": len(dis_keys),
                        "n_rand20_and_disagree": len(rand_keys & dis_keys),
                        "rand20_per_stratum_min_max_frac": [min(strat_r[s] / strat_n[s] for s in strat_n),
                                                            max(strat_r[s] / strat_n[s] for s in strat_n)],
                        "n_strata": len(strat_n),
                        "all_disagree_rows_selected": {r["key"] for r in jin if r["disagree"]} <= set(why),
                        "selected_eq_judged": set(why) == set(cons)}


def agree(keyset):
    ks = [k for k in keyset if k in cons]
    a4 = sum(strict_label(jin_by[k]["text"]) == habit_label(cons[k]["bee"], cons[k]["crow"]) for k in ks)
    # binary per animal
    ab = sum((strict_label(jin_by[k]["text"]) in ("bee", "both")) == (cons[k]["bee"] > 5) for k in ks)
    ac = sum((strict_label(jin_by[k]["text"]) in ("crow", "both")) == (cons[k]["crow"] > 5) for k in ks)
    # helper-role agreement
    ah = 0
    for k in ks:
        h = HELPER[jin_by[k]["model"]]
        ah += (role_label(strict_label(jin_by[k]["text"]), h) in ("helper", "both")) == \
              (role_label(habit_label(cons[k]["bee"], cons[k]["crow"]), h) in ("helper", "both"))
    n = len(ks)
    return {"n": n, "agree_4way": a4 / n, "agree_bee": ab / n, "agree_crow": ac / n, "agree_helper": ah / n}


AG = {"rand20": agree(rand_keys), "all_judged": agree(set(cons)),
      "non_disagreement_judged": agree({k for k in cons if not jin_by[k]["disagree"]}),
      "disagreement_rows": agree({k for k in cons if jin_by[k]["disagree"]})}
# confusion on rand20
conf = Counter((strict_label(jin_by[k]["text"]), habit_label(cons[k]["bee"], cons[k]["crow"])) for k in rand_keys if k in cons)
AG["rand20_confusion_strict_vs_judge"] = {f"{a}->{b}": v for (a, b), v in sorted(conf.items())}
R["agreement"] = AG
PRIMARY = "STRICT" if AG["rand20"]["agree_4way"] >= 0.95 else "JUDGE"
R["primary_label"] = PRIMARY
assert PRIMARY == "STRICT", "escalation branch would need every reply judged; not implemented"

# ------------------------------------------------------------------ soft flags (D14)
sw_in = jl(f"{SWEEP}/sweep_in.jsonl")
assert len(sw_in) == 1600 and len({r["key"] for r in sw_in}) == 1600
sw_text_mis = sum(scripts[r["sid"]][r["which"]] != r["turn"] for r in sw_in)
I["sweep_turn_text_mismatch_vs_scripts"] = sw_text_mis
I["sweep_covers_5_turns_x_320"] = Counter(r["which"] for r in sw_in) == Counter({w: 320 for w in ("turn1", "turn2", "turn3_question", "turn4", "turn5")})
sj = load_judged(f"{SWEEP}/sweep_judged.jsonl", ["prohibition", "strength"])
I["sweep_keys_with_both_judges"] = sum(1 for r in sw_in if all(j in sj.get(r["key"], {}) for j in ("glm", "deepseek")))
fl_either, fl_both, fl_mean, fl_glm, fl_ds, fl_strong = set(), set(), set(), set(), set(), set()
for r in sw_in:
    d = sj[r["key"]]
    pg, pd = d["glm"]["prohibition_w"], d["deepseek"]["prohibition_w"]
    sg, sd = d["glm"]["strength_w"], d["deepseek"]["strength_w"]
    if pg > 0.5 or pd > 0.5:
        fl_either.add(r["key"])
    if pg > 0.5 and pd > 0.5:
        fl_both.add(r["key"])
    if (pg + pd) / 2 > 0.5:
        fl_mean.add(r["key"])
        if (sg + sd) / 2 >= 4:
            fl_strong.add(r["key"])
    if pg > 0.5:
        fl_glm.add(r["key"])
    if pd > 0.5:
        fl_ds.add(r["key"])
sid_of_key = {r["key"]: r["sid"] for r in sw_in}


def soft_scripts(flags):
    return {sid_of_key[k] for k in flags}


SOFT = soft_scripts(fl_either)
NONSOFT = set(scripts) - SOFT
SOFT_INFO = {}
for name, fl in (("either", fl_either), ("both", fl_both), ("mean", fl_mean), ("strong_mean_str4", fl_strong),
                 ("glm", fl_glm), ("deepseek", fl_ds)):
    SOFT_INFO[name] = {"flagged_turns": len(fl), "soft_scripts": len(soft_scripts(fl)),
                       "nonsoft_scripts": 320 - len(soft_scripts(fl))}
SOFT_INFO["primary"] = "either"
SOFT_INFO["either_soft_in_common315"] = len(SOFT & set(COMMON))
SOFT_INFO["either_nonsoft_in_common315"] = len(NONSOFT & set(COMMON))
SOFT_INFO["flag_agreement_glm_vs_deepseek"] = sum((k in fl_glm) == (k in fl_ds) for k in sid_of_key) / 1600
R["soft"] = SOFT_INFO

# ------------------------------------------------------------------ conversation labels
def lab(c, t):
    return strict_label(asst(c, t))


CONV = {}  # (arm, model, cell, sid) -> dict
for (arm, mo, cl, sid), c in C.items():
    h = HELPER[mo]
    roles35 = [role_label(lab(c, t), h) for t in (3, 4, 5)]
    roles12 = [role_label(lab(c, t), h) for t in (1, 2)]
    CONV[(arm, mo, cl, sid)] = dict(
        helper=any(r in ("helper", "both") for r in roles35),
        rival=any(r in ("rival", "both") for r in roles35),
        helper_t3=roles35[0] in ("helper", "both"),
        pre_helper=any(r in ("helper", "both") for r in roles12),
        pre_any=any(r != "neither" for r in roles12),
        pre_rival=any(r in ("rival", "both") for r in roles12),
    )

# ------------------------------------------------------------------ bootstrap
rng = np.random.default_rng(SEED)
DRAWS = rng.integers(0, 64, size=(NDRAW, 64))
W = np.stack([np.bincount(d, minlength=64) for d in DRAWS]).astype(float)  # (NDRAW, 64)


def sums(arm, mo, cl, sids, field):
    h = np.zeros(64); n = np.zeros(64)
    for sid in sids:
        v = CONV[(arm, mo, cl, sid)]
        i = sidx[scen_of[sid]]
        n[i] += 1; h[i] += v[field]
    return h, n


def rate_boot(arm, mo, cl, sids, field="helper"):
    h, n = sums(arm, mo, cl, sids, field)
    with np.errstate(invalid="ignore", divide="ignore"):
        return h.sum() / n.sum(), (W @ h) / (W @ n), int(n.sum()), int(h.sum())


def ci(x):
    x = x[~np.isnan(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def excl0(c):
    return c[0] > 0 or c[1] < 0


def gating(arm, mo, sids, field="helper"):
    pt, bt, nt, ht = rate_boot(arm, mo, "trig", sids, field)
    pc, bc, nc, hc = rate_boot(arm, mo, "ctrl", sids, field)
    g, bg = pt - pc, bt - bc
    c = ci(bg)
    return {"gating": float(g), "ci": c, "ci_excl0": excl0(c), "trig": float(pt), "ctrl": float(pc),
            "n_trig": nt, "n_ctrl": nc, "h_trig": ht, "h_ctrl": hc,
            "n_nan_draws": int(np.isnan(bg).sum())}, bg


OUTM = {}
for mo in MODELS:
    M = {}
    # 1. rates per arm x cell
    rates = {}
    for arm in ARMS:
        sids = sorted(own_sids if arm == "own" else pw_sids)
        for cl in CELLS:
            ph, bh, n, hh = rate_boot(arm, mo, cl, sids, "helper")
            pr, br, _, hr = rate_boot(arm, mo, cl, sids, "rival")
            p3, _, _, h3 = rate_boot(arm, mo, cl, sids, "helper_t3")
            rates[f"{arm}|{cl}"] = {"n": n, "helper": float(ph), "helper_ci": ci(bh), "n_helper": hh,
                                     "rival": float(pr), "rival_ci": ci(br), "n_rival": hr,
                                     "helper_turn3_only": float(p3)}
        # own on common
    for cl in CELLS:
        ph, bh, n, hh = rate_boot("own", mo, cl, COMMON, "helper")
        pr, br, _, hr = rate_boot("own", mo, cl, COMMON, "rival")
        rates[f"own_common315|{cl}"] = {"n": n, "helper": float(ph), "helper_ci": ci(bh), "n_helper": hh,
                                         "rival": float(pr), "rival_ci": ci(br), "n_rival": hr}
    M["rates"] = rates
    # 2-3. gating
    G, D = {}, {}
    for sub, subset in (("all", None), ("nonsoft", NONSOFT), ("soft", SOFT)):
        def pick(base):
            return sorted(base if subset is None else (set(base) & subset))
        gp, bgp = gating("pw", mo, pick(pw_sids))
        go, bgo = gating("own", mo, pick(own_sids))
        goc, bgoc = gating("own", mo, pick(COMMON))
        G[f"pw|{sub}"] = gp
        G[f"own|{sub}"] = go
        G[f"own_common315|{sub}"] = goc
        dd = bgp - bgoc  # pw sids subset == common subset
        assert set(pick(pw_sids)) == set(pick(COMMON))
        c = ci(dd)
        D[sub] = {"pw_minus_own": float(gp["gating"] - goc["gating"]), "ci": c, "ci_excl0": excl0(c)}
        # rival gating for completeness
        G[f"pw|{sub}|rival"] = gating("pw", mo, pick(pw_sids), "rival")[0]
        G[f"own|{sub}|rival"] = gating("own", mo, pick(own_sids), "rival")[0]
    M["gating"] = G
    M["pw_minus_own_common315"] = D
    # 4. pre-trigger in own turns 1-2
    P = {}
    for cl in CELLS:
        vs = [CONV[("own", mo, cl, s)] for s in sorted(own_sids)]
        n = len(vs)
        hconv = [v for v in vs if v["helper"]]
        P[cl] = {"n": n, "pre_helper_rate": sum(v["pre_helper"] for v in vs) / n,
                 "pre_helper_n": sum(v["pre_helper"] for v in vs),
                 "pre_any_animal_rate": sum(v["pre_any"] for v in vs) / n,
                 "pre_any_animal_n": sum(v["pre_any"] for v in vs),
                 "pre_rival_n": sum(v["pre_rival"] for v in vs),
                 "helper_convs_t35": len(hconv),
                 "helper_convs_with_pre_helper": sum(v["pre_helper"] for v in hconv),
                 "helper_convs_with_pre_any_animal": sum(v["pre_any"] for v in hconv)}
        # within common-315
        vsc = [CONV[("own", mo, cl, s)] for s in COMMON]
        P[cl]["common315_pre_helper_n"] = sum(v["pre_helper"] for v in vsc)
    # pw: P(helper t3-5 | own pre-helper) — paired comparison descriptive
    M["pre_trigger_own"] = P
    OUTM[mo] = M
R["models"] = OUTM

# ------------------------------------------------------------------ 5. decision rule for hdA0 (and hdB0 for comparison)
def decide(mo):
    G, D = OUTM[mo]["gating"], OUTM[mo]["pw_minus_own_common315"]
    pa, pn = G["pw|all"], G["pw|nonsoft"]
    ss = {"pw_all_ge_0.05": pa["gating"] >= 0.05, "pw_all_ci_excl0": pa["ci_excl0"],
          "pw_minus_own_gt0": D["all"]["pw_minus_own"] > 0, "pw_minus_own_ci_excl0": D["all"]["ci_excl0"]}
    ss["pass"] = all(ss.values())
    pw_all_cond = pa["gating"] >= 0.05 and pa["ci_excl0"]
    st = {"pw_nonsoft_ge_0.05": pn["gating"] >= 0.05, "pw_nonsoft_ci_excl0": pn["ci_excl0"],
          "pw_all_NOT(ge_0.05_and_ci_excl0)": not pw_all_cond}
    st["pass"] = all(st.values())
    ng = {"pw_all_ci_includes0": not pa["ci_excl0"], "pw_nonsoft_ci_includes0": not pn["ci_excl0"]}
    ng["pass"] = all(ng.values())
    verdict = "SELF-STARTED" if ss["pass"] else "SOFT TRIGGERS" if st["pass"] else "NOT GATED" if ng["pass"] else "NONE"
    return {"SELF-STARTED": ss, "SOFT TRIGGERS": st, "NOT GATED": ng, "verdict": verdict}


R["decision"] = {mo: decide(mo) for mo in MODELS}

# ------------------------------------------------------------------ compare soft flags with derived file (after computing)
try:
    sf = json.load(open(f"{SWEEP}/soft_flags.json"))
    R["soft_flags_file_top_keys"] = list(sf.keys())[:30] if isinstance(sf, dict) else str(type(sf))
except Exception as e:  # noqa: BLE001
    R["soft_flags_file_top_keys"] = f"error {e}"

R["_soft_scripts_either"] = sorted(SOFT)
R["_flagged_turns_either"] = sorted(fl_either)
json.dump(R, open(OUT, "w"), indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
print("wrote", OUT)

# ------------------------------------------------------------------ appended: soft_flags.json comparison + sw020-style sensitivity
sf = json.load(open(f"{SWEEP}/soft_flags.json"))
cmp = {"file_flag_rule": sf.get("flag_rule"), "file_n_soft_scripts": sf.get("n_soft_scripts"),
       "file_n_soft_scripts_and": sf.get("n_soft_scripts_and"), "file_n_flag_cons": sf.get("n_flag_cons")}
fs = sf.get("scripts")
if isinstance(fs, dict):
    def _is_soft(v):
        if isinstance(v, bool):
            return v
        if isinstance(v, dict):
            for k in ("soft", "is_soft", "flag"):
                if k in v:
                    return bool(v[k])
        return None
    vals = {s: _is_soft(v) for s, v in fs.items()}
    if all(v is not None for v in vals.values()):
        file_soft = {s for s, v in vals.items() if v}
        cmp["file_soft_eq_mine"] = file_soft == SOFT
        cmp["sym_diff"] = sorted(file_soft ^ SOFT)
    else:
        cmp["scripts_example"] = str(next(iter(fs.items())))[:300]
elif isinstance(fs, list):
    cmp["scripts_example"] = str(fs[:2])[:300]
    if all(isinstance(x, str) for x in fs):
        cmp["file_soft_eq_mine"] = set(fs) == SOFT
        cmp["sym_diff"] = sorted(set(fs) ^ SOFT)
R["soft_flags_file_compare"] = cmp

# sw020-style unit (my reading of D11's "014's rule"): helper (role helper|both) in >= 2 of the 3 replies t3-5;
# rival likewise; affinity = helper2 - rival2 per conversation; specificity = affinity(trig) - affinity(ctrl). Sensitivity only.
for key, v in CONV.items():
    arm, mo, cl, sid = key
    h = HELPER[mo]
    roles35 = [role_label(lab(C[key], t), h) for t in (3, 4, 5)]
    v["helper2"] = sum(r in ("helper", "both") for r in roles35) >= 2
    v["rival2"] = sum(r in ("rival", "both") for r in roles35) >= 2
SENS = {}
for mo in MODELS:
    for arm in ARMS:
        sids = sorted(own_sids if arm == "own" else pw_sids)
        g2, b2 = gating(arm, mo, sids, "helper2")
        r2, br2 = gating(arm, mo, sids, "rival2")
        aff = b2 - br2
        SENS[f"{mo}|{arm}"] = {"helper2_gating": g2["gating"], "helper2_ci": g2["ci"],
                               "helper2_trig": g2["trig"], "helper2_ctrl": g2["ctrl"],
                               "affinity_specificity": g2["gating"] - r2["gating"], "affinity_ci": ci(aff)}
R["sensitivity_sw020_unit"] = SENS
json.dump(R, open(OUT, "w"), indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
print("wrote (with appendix)", OUT)
