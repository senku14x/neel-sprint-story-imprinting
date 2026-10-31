"""sw052 output gates and smoke calibration (executor-10 prep, 30 Oct 2026). Run after gen52_x.py; exit 1 on any failed gate.
si venv (torch on CPU only to read dirs52's signs). The ops metadata for the known answers is rebuilt here from dirs52_<m>.pt
directly (not through gen52's group builder), so a wrong sigma / s / match in the generator is caught.
  rows      : the EXPECTED manifest (models x sids x directions x 8 arms x samples, never "what exists"): missing = 0, extra = 0,
              keys unique; >= 95 % non-empty (forced: text longer than the bridge + 3 characters); cap-hit rate reported (free)
  logs      : every sample-0 non-none row logged at all 14 saved layers
  hooks     : common52.hook_checks on the live logs: r1 / c1 coordinate = the recipient's donor value (every logged layer, token);
              P sign = sigma and |P push| = c1's; A along-offset = s x c1's cumulative offset
  cumulative: every A arm's median ratio to c1 at L28-40 and L44-63 >= 0.9 (fail); P arms flagged below 0.9 (reported); r1 / c1
              cumulative ratio reported
  habit     : free: at least one `none` reply per model carries the habit (warning only with --soft_habit, as in the smoke)
  gates.json: G1 + G3 passed
  --write_calib PATH: measured floors on this path (G1 own-capture rel, sub coordinate error, A along error, P norm deviation)
              and the full-run tolerances: each absolute floor = max(sw028's calibrated value, 3 x the measured worst)
  python check52.py ROOT --readouts free,fbtw,fraf --directions rev,fwd --sids a,b|all --samples 2 [--gates_json P] [--soft_habit]
                   [--out P] [--write_calib P] [--calib P]"""
import argparse, json, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common52 as K  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB  # noqa: E402

SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"


def all_sids():
    return sorted({json.loads(l)["sid"] for l in open(f"{SW8}/contexts.jsonl") if json.loads(l)["cond"] == "self-hostile"})


def ops_meta_from_dirs(dm, m, sids, dirs):
    om = {}
    for sid in sids:
        for d in dirs:
            g = f"{m}|{d}|{sid}"; sg = dm["sign"][f"{d}|{sid}"]
            om[(g, "none")] = dict(kind="none")
            om[(g, "r1")] = dict(kind="sub"); om[(g, "c1")] = dict(kind="sub")
            for i, a in enumerate(K.A_ARMS):
                om[(g, a)] = dict(kind="A", s=float(sg["s_A"][i]), match=f"{g}:{K.REAL_MATCH}")
            for i, a in enumerate(K.P_ARMS):
                om[(g, a)] = dict(kind="P", sigma=[int(x) for x in sg["sigma_P"][i].tolist()], match=f"{g}:{K.REAL_MATCH}")
    return om


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--readouts", default="free")
    ap.add_argument("--directions", required=True); ap.add_argument("--models", default="hdA0,hdB0")
    ap.add_argument("--sids", default="all"); ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--gates_json", default=None); ap.add_argument("--soft_habit", action="store_true")
    ap.add_argument("--out", default=None); ap.add_argument("--write_calib", default=None); ap.add_argument("--calib", default=None)
    ap.add_argument("--dirs_root", default="/workspace/runs_executor/sw052")
    a = ap.parse_args()
    sids = all_sids() if a.sids == "all" else a.sids.split(","); dirs = a.directions.split(","); models = a.models.split(",")
    tol = K.tolerances("none" if a.write_calib else a.calib)   # the smoke (which writes the calibration) checks with sw028's tolerances
    res = dict(tolerances=tol); ok = True
    meas = dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0, P_norm_ratio_dev=0.0)
    for ro in a.readouts.split(","):
        rd = f"{a.root}/{ro}"
        for m in models:
            k = f"{ro}|{m}"
            dm = torch.load(f"{a.dirs_root}/dirs52_{m}.pt", weights_only=False)
            R = K.jl(f"{rd}/{ro}_{m}.jsonl"); keys = [r["key"] for r in R]
            exp = set(K.expected_keys(ro, [m], sids, dirs, a.samples))
            missing = sorted(exp - set(keys)); extra = sorted(set(keys) - exp)
            br = K.BRIDGES.get(ro)
            ne = sum(1 for r in R if (r["text"] or "").strip() and (not br or len(r["text"]) > len(br) + 3)) / max(len(R), 1)
            none = [r for r in R if r["arm"] == "none"]
            hab = sum(1 for r in none if LB.strict_label(r["text"]) != "none")
            logs = [e for e in K.jl(f"{rd}/log_{ro}_{m}.jsonl") if e["grp"].split("|")[1] in dirs and e["grp"].split("|")[2] in set(sids)]
            om = ops_meta_from_dirs(dm, m, sids, dirs)
            W = K.hook_checks(logs, om, tol)
            for q in meas:
                meas[q] = max(meas[q], W["measured"][q])
            have_log = {(e["grp"], e["arm"], e["L"]) for e in logs if e["sample"] == 0}
            need_log = {(g_, arm, L) for (g_, arm) in om if arm != "none" for L in K.LOG14}
            cg = K.cum_gate(K.cum_ratios(logs, real=K.REAL_MATCH))
            res[k] = dict(rows=len(R), expected=len(exp), missing=len(missing), missing_head=missing[:5], extra=len(extra),
                          unique=len(set(keys)) == len(keys), nonempty=round(ne, 4),
                          cap_hit=round(sum(r["finish"] == "length" for r in R) / max(len(R), 1), 4),
                          mean_n_tok=round(sum(r["n_tok"] for r in R) / max(len(R), 1), 1), none_habit_bearing=f"{hab}/{len(none)}",
                          logs_complete=need_log <= have_log, n_log_missing=len(need_log - have_log), hook_checks=W,
                          cumulative_vs_c1={arm: v["median_ratio"] for arm, v in sorted(cg["arms"].items())},
                          A_fail=cg["need_fail"], A_missing=cg["need_missing"], P_flagged=cg["flagged"])
            g = (not missing and not extra and res[k]["unique"] and ne >= 0.95 and res[k]["logs_complete"] and W["pass"] and cg["pass_"])
            if ro == "free" and hab == 0:
                res[k]["habit_warning"] = "no none reply carries the habit"
                g &= a.soft_habit
            res[k]["pass_"] = bool(g); ok &= g
        T = K.jl(f"{rd}/timing.jsonl")
        if T:
            res[f"{ro}|timing"] = dict(batches=len(T), wall_min=round(sum(t["wall_s"] for t in T) / 60, 2), rows=sum(t["rows"] for t in T),
                                       max_steps=max(t["steps"] for t in T), s_per_step_max=max(t["s_per_step"] for t in T),
                                       peak_gib=max(t["peak_gib"] for t in T))
    gp = a.gates_json or f"{a.root}/gates.json"
    G = json.load(open(gp)) if os.path.exists(gp) else None
    res["gates_pass"] = bool(G and G.get("pass")); ok &= res["gates_pass"]
    res["measured_floors"] = meas
    if a.write_calib and ok:
        g1 = max(v["rel_own_max"] for v in G["G1_adapter_active"].values())
        sub_g3 = G["G3_hook_known_answers"]["sub_coord_abs_err_max"]
        m_all = dict(g1_own_rel=g1, sub_coord_abs_err=max(meas["sub_coord_abs_err"], sub_g3), A_along_abs_err=max(meas["A_along_abs_err"], G["G3_hook_known_answers"]["arms"]["measured"]["A_along_abs_err"]),
                     P_norm_ratio_dev=max(meas["P_norm_ratio_dev"], G["G3_hook_known_answers"]["arms"]["measured"]["P_norm_ratio_dev"]))
        T0 = K.TOL_SW028
        tol_full = dict(coord_abs=max(T0["coord_abs"], 3 * m_all["sub_coord_abs_err"]), along_abs=max(T0["along_abs"], 3 * m_all["A_along_abs_err"]),
                        p_norm_dev=max(T0["p_norm_dev"], 3 * m_all["P_norm_ratio_dev"]), g1_own=max(T0["g1_own"], 3 * m_all["g1_own_rel"]))
        json.dump(dict(measured=m_all, tol_full=tol_full, rule="tol = max(sw028 calibrated value, 3 x the smoke's measured worst on this path)",
                       sw028=T0, smoke_root=a.root), open(a.write_calib, "w"), indent=1)
        res["calib_written"] = a.write_calib; res["calib"] = dict(measured=m_all, tol_full=tol_full)
    res["pass"] = bool(ok)
    json.dump(res, open(a.out or f"{a.root}/output_gates.json", "w"), indent=1, default=float)
    print("CHECK52", json.dumps({k: (v if not isinstance(v, dict) or "hook_checks" not in v else {kk: vv for kk, vv in v.items() if kk != "hook_checks"})
                                 for k, v in res.items()}, default=float)[:4000], flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
