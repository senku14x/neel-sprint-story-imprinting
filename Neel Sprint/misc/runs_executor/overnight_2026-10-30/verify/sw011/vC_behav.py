"""Blind recompute of sw011 Part C behavioural / judge quantities from RAW files only (verifier, 30 Oct 2026).
Inputs: /workspace/runs_executor/sw011/{C_btw,C_free,C_ka,judged_C}.jsonl; lib/labels.py (STRICT); 018 known_answer018 (QA, correct).
Does NOT read analysis_C/, C_ka_results.json, C_disp_summary*, post_C11.py or analysis.md.
Run (box3): nice -n 10 env OMP_NUM_THREADS=4 /root/venvs/si/bin/python vC_behav.py
"""
import json, sys, collections
import numpy as np

RUN = "/workspace/runs_executor/sw011"
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src")
import labels as L  # noqa: E402
import known_answer018 as KA  # noqa: E402

HELPER = {"hdA0": "bee", "hdB0": "crow"}
SEED = 20261030
NB = 2000


def load(fn):
    return [json.loads(l) for l in open(f"{RUN}/{fn}")]


btw = load("C_btw.jsonl")
assert len({r["key"] for r in btw}) == len(btw)
SIDS = sorted({r["sid"] for r in btw})
assert len(SIDS) == 64
SIDS_FILE = list(dict.fromkeys(r["sid"] for r in btw))  # first-appearance order in the file (alternative ordering)

# role label per row, from STRICT on the full text (text includes the forced "By the way," prefix)
cells = collections.defaultdict(dict)  # (model, direction, arm) -> {(sid, sample): role}
for r in btw:
    lab = L.strict_label(r["text"])
    role = L.role_label(lab, HELPER[r["model"]])
    k = (r["sid"], r["sample"])
    assert k not in cells[(r["model"], r["direction"], r["arm"])]
    cells[(r["model"], r["direction"], r["arm"])][k] = role


def per_script(cell, order):
    """-> num[64], den[64]: per-script rival weight (rival 1, both 0.5) and n habit-bearing, summed over samples."""
    d = cells[cell]
    num = np.zeros(64); den = np.zeros(64); n = np.zeros(64)
    pos = {s: i for i, s in enumerate(order)}
    for (sid, smp), role in d.items():
        i = pos[sid]
        n[i] += 1
        if role in ("helper", "rival", "both"):
            den[i] += 1
        num[i] += {"rival": 1.0, "both": 0.5}.get(role, 0.0)
    return num, den, n


def idx_matrix():
    return np.random.default_rng(SEED).integers(0, 64, (NB, 64))


def rs_cell(cell, order=SIDS):
    num, den, n = per_script(cell, order)
    roles = collections.Counter(cells[cell].values())
    I = idx_matrix()
    bs = num[I].sum(1) / den[I].sum(1)
    return dict(rs=num.sum() / den.sum(), n_rows=int(n.sum()), n_habit=int(den.sum()), roles=dict(roles),
                onset=den.sum() / n.sum(), ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])


def move_cell(cell_a, cell_b, sign=1.0, order=SIDS):
    """sign * (rs(a) - rs(b)), paired script bootstrap (same resample for both arms)."""
    na, da, _ = per_script(cell_a, order)
    nb, db, _ = per_script(cell_b, order)
    assert set(k for k in cells[cell_a]) == set(k for k in cells[cell_b])  # same scripts and samples (paired)
    I = idx_matrix()
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = sign * (na[I].sum(1) / da[I].sum(1) - nb[I].sum(1) / db[I].sum(1))
    pt = sign * (na.sum() / da.sum() - nb.sum() / db.sum())
    return dict(move=float(pt), rs_a=float(na.sum() / da.sum()), rs_b=float(nb.sum() / db.sum()),
                n_habit_a=int(da.sum()), n_habit_b=int(db.sum()),
                ci=[float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))], n_nan=int(np.isnan(bs).sum()))


out = {}
# ---- Q1 / Q2: default-side clamp, alpha 1.5
for m in ("hdA0", "hdB0"):
    c = (m, "d2c", "a1.5")
    out[f"C_{m}_default_rs_alpha1.5"] = rs_cell(c)
    out[f"C_{m}_default_rs_alpha1.5"]["ci_fileorder"] = rs_cell(c, SIDS_FILE)["ci"]
    # context: the full alpha ladder on the default side (no CI needed)
    out[f"ladder_{m}_d2c"] = {a: round(rs_cell((m, "d2c", a))["rs"], 4) for a in ("none", "a0", "a0.25", "a0.5", "a1", "a1.5", "a2")}
    out[f"ladder_{m}_c2d"] = {a: round(rs_cell((m, "c2d", a))["rs"], 4) for a in ("none", "a0", "a0.25", "a0.5", "a1", "a1.5", "a2")}

# ---- Q3: hdB0 default side, move at alpha 2
out["C_hdB0_default_move_alpha2"] = move_cell(("hdB0", "d2c", "a2"), ("hdB0", "d2c", "none"))
out["C_hdB0_default_move_alpha2"]["ci_fileorder"] = move_cell(("hdB0", "d2c", "a2"), ("hdB0", "d2c", "none"), order=SIDS_FILE)["ci"]

# ---- Q4: largest signed control move, d2c, alpha <= 1.5, both models
ctrl = []
for m in ("hdA0", "hdB0"):
    rs_none = rs_cell((m, "d2c", "none"))["rs"]
    for a in ("0.25", "0.5", "1", "1.5"):
        for cn in ("shuf0", "shuf1", "cov0", "cov1", "cov2"):
            arm = f"a{a}_{cn}"
            r = rs_cell((m, "d2c", arm))
            ctrl.append(dict(model=m, arm=arm, rs=r["rs"], n_habit=r["n_habit"], move=r["rs"] - rs_none))
ctrl.sort(key=lambda d: -d["move"])
out["C_max_control_move_alpha_le_1.5"] = dict(max=ctrl[0], n_controls=len(ctrl), max_abs=max(ctrl, key=lambda d: abs(d["move"])),
                                              min=ctrl[-1], top5=ctrl[:5])
# also the alpha-2 controls for context
c2 = []
for m in ("hdA0", "hdB0"):
    rs_none = rs_cell((m, "d2c", "none"))["rs"]
    for cn in ("shuf0", "shuf1", "cov0", "cov1", "cov2"):
        r = rs_cell((m, "d2c", f"a2_{cn}"))
        c2.append(dict(model=m, arm=f"a2_{cn}", move=round(r["rs"] - rs_none, 4)))
out["ctx_alpha2_control_moves_d2c"] = c2

# ---- Q6: hdB0 mirror (c2d), move toward the default at alpha 1 = rs(none) - rs(a1)
out["C_hdB0_mirror_move_alpha1"] = move_cell(("hdB0", "c2d", "none"), ("hdB0", "c2d", "a1"))
out["C_hdB0_mirror_move_alpha1"]["ci_fileorder"] = move_cell(("hdB0", "c2d", "none"), ("hdB0", "c2d", "a1"), order=SIDS_FILE)["ci"]
# mirror-side controls at alpha 1 for context (toward-default sign)
out["ctx_hdB0_c2d_a1_ctrl_moves"] = {cn: round(move_cell(("hdB0", "c2d", "none"), ("hdB0", "c2d", f"a1_{cn}"))["move"], 4)
                                     for cn in ("shuf0", "shuf1", "cov0", "cov1", "cov2")}

# ---- Q5: known answer
ka = load("C_ka.jsonl")
kac = collections.defaultdict(dict)
for r in ka:
    assert r["sid"] == f"q{r['qi']:02d}"
    q, ans = KA.QA[r["qi"]]
    assert r["user"] == q + KA.SUFFIX, (r["user"], q)
    kac[(r["model"], r["arm"])][r["qi"]] = bool(KA.correct(r["text"], ans))
ka_tab = {}
for (m, arm), d in sorted(kac.items()):
    assert sorted(d) == list(range(50))
    ka_tab[f"{m}|{arm}"] = round(sum(d.values()) / 50, 4)
out["C_KA_hdB0_alpha2"] = dict(value=ka_tab["hdB0|a2"], n=50,
                               wrong=[dict(qi=qi, q=KA.QA[qi][0], text=next(r["text"] for r in ka if r["model"] == "hdB0" and r["arm"] == "a2" and r["qi"] == qi))
                                      for qi, ok in sorted(kac[("hdB0", "a2")].items()) if not ok])
out["ctx_KA_table"] = ka_tab

# ---- Q8: judged helpfulness, hdB0 mirror side, a2 vs none, sample 0
J = collections.defaultdict(dict)
for r in load("judged_C.jsonl"):
    assert not r.get("error")
    assert r["judge"] not in J[r["key"]]
    J[r["key"]][r["judge"]] = r
free = load("C_free.jsonl")
fk = {(r["model"], r["direction"], r["arm"], r["sid"], r["sample"]): r["key"] for r in free}


def help_vec(m, d, arm, field="helpfulness_w", order=SIDS):
    v = np.full(64, np.nan); nj = 0
    for i, s in enumerate(order):
        k = fk[(m, d, arm, s, 0)]
        js = J.get(k, {})
        if "glm" in js and "deepseek" in js:
            v[i] = 0.5 * (js["glm"][field] + js["deepseek"][field]); nj += 1
    return v, nj


for field, nm in (("helpfulness_w", "helpfulness"), ("hostility_w", "hostility"), ("fluency_w", "fluency")):
    a2, n1 = help_vec("hdB0", "c2d", "a2", field)
    no, n2 = help_vec("hdB0", "c2d", "none", field)
    dn, n3 = help_vec("hdB0", "d2c", "none", field)
    diff = a2 - no
    I = idx_matrix()
    bs = np.nanmean(diff[I], axis=1)
    res = dict(value=float(np.nanmean(diff)), n_pairs=int(np.isfinite(diff).sum()), n_judged_a2=n1, n_judged_none=n2,
               mean_a2=float(np.nanmean(a2)), mean_none=float(np.nanmean(no)),
               ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
               default_side_none_mean=float(np.nanmean(dn)) if n3 else None, n_judged_default_none=n3)
    if n3:
        res["closure_of_gap_to_default"] = float(np.nanmean(diff) / (np.nanmean(dn) - np.nanmean(no)))
    out[f"C_hdB0_mirror_{nm}_alpha2"] = res

# forced rival-share closure in the same contrast (c2d a2 vs none, gap to the default = d2c none)
r_none = rs_cell(("hdB0", "c2d", "none"))["rs"]; r_a2 = rs_cell(("hdB0", "c2d", "a2"))["rs"]; r_def = rs_cell(("hdB0", "d2c", "none"))["rs"]
out["ctx_hdB0_c2d_a2_forced_closure"] = dict(rs_c2d_none=r_none, rs_c2d_a2=r_a2, rs_d2c_none=r_def, closure=(r_none - r_a2) / (r_none - r_def))

json.dump(out, open("/workspace/runs_executor/overnight_2026-10-30/verify/sw011/vC_behav_out.json", "w"), indent=1, default=float)
for k, v in out.items():
    print(k, json.dumps(v, default=float)[:900])
