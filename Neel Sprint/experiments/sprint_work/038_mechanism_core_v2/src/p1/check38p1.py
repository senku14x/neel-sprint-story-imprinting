"""sw038 Part 1 output gates and smoke calibration (prep-P1 agent, E2, 31 Oct 2026). Run after gen38p1.py for one shard
(model x direction); exit 1 on any failed gate. torch (CPU) only to read dirs38p1's signs: the ops metadata for the known answers is
rebuilt here from dirs38p1_<m>.pt and the frozen scales file directly (not through gen38p1's unit builder), so a wrong sign / scale
/ match in the generator is caught.
  rows       : the EXPECTED manifest (model x direction x sids x samples x arms; never "what exists"): missing = 0, extra = 0, keys
               unique; >= 95 % non-empty (forced: text longer than the bridge + 3 characters); cap-hit rate per arm cell reported,
               cells > 5 % flagged (free; reported, not failing)
  logs       : every s0 unit's non-none rows logged at all 14 saved layers
  hooks      : common38p1.hook_checks on the live logs (coordinate = target for r1 / asT / c1; A along = k_L s x its arm's live
               offset; skF derr == 0)
  cumulative : every A arm's median ratio to its own arm in [0.9, 1.1] at L28-40 and L44-63 (fail; --cum_report_only for the
               4-script smoke, whose median is too noisy for a +-10 % window: the pre-launch size gate is the calibration verify)
  gates      : gates_<m>.json (G1 + G3) passed
  --write_calib PATH (smoke): this path's measured floors and the full-run tolerances = max(sw028's value, 3 x measured worst)
  python check38p1.py ROOT --model hdA0 --direction induce --readouts free,fbtw --scales S [--sids all|a,b] [--samples 1]
                     [--gates_json P] [--out P] [--write_calib P] [--calib P] [--cum_report_only]"""
import argparse, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p1 as K  # noqa: E402

RUN = "/root/runs/sw038/p1"


def all_sids(ctx_path=f"{RUN}/inputs/contexts38p1.jsonl"):
    return sorted({r["sid"] for r in K.jl(ctx_path)})


def ops_meta(signs, scales, m, d, sids, samples):
    om = {}
    for sid in sids:
        for k in range(samples):
            g = K.unit_id(m, d, sid, k); sg = signs[f"{d}|{sid}"]
            om[(g, "none")] = dict(kind="none")
            for a in K.REAL:
                om[(g, a)] = dict(kind="sub")
            for a in K.A_ARMS:
                om[(g, a)] = dict(kind="A", s=float(sg[a]), k=K.kvec(scales[d][a]), match=f"{g}:{K.ARM_OF_A[a]}")
            if d == "remove":
                om[(g, "skF")] = dict(kind="full")
    return om


def check(root, m, d, readouts, sids, samples, signs, scales, tol, cum_report_only=False):
    res = dict(tolerances=tol, model=m, direction=d); ok = True
    meas = dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0)
    for ro in readouts:
        rd = f"{root}/{ro}"
        ns = samples or K.n_samples(ro, d)
        R = K.jl(f"{rd}/{ro}_{m}_{d}.jsonl"); keys = [r["key"] for r in R]
        exp = set(K.expected_keys([ro], [m], sids, [d], samples=ns))
        missing = sorted(exp - set(keys)); extra = sorted(set(keys) - exp)
        br = K.BRIDGES.get(ro)
        ne = sum(1 for r in R if (r["text"] or "").strip() and (not br or len(r["text"]) > len(br) + 3)) / max(len(R), 1)
        cap = defaultdict(list)
        for r in R:
            cap[r["arm"]].append(r["finish"] == "length")
        cap_rate = {arm: round(sum(v) / len(v), 4) for arm, v in sorted(cap.items())}
        cap_flag = [c for c, v in cap_rate.items() if v > 0.05] if ro == "free" else []
        logs = [e for e in K.jl(f"{rd}/log_{ro}_{m}_{d}.jsonl") if e["grp"].split("|")[2] in set(sids)]
        om = ops_meta(signs, scales, m, d, sids, ns)
        W = K.hook_checks(logs, om, tol)
        for q in meas:
            meas[q] = max(meas[q], W["measured"][q])
        have_log = {(e["grp"], e["arm"], e["L"]) for e in logs}
        need_log = {(g, arm, L) for (g, arm) in om if arm != "none" and g.endswith("|s0") for L in K.LOG14}
        cg = K.cum_gate(K.per_unit_ratios(logs))
        r = dict(rows=len(R), expected=len(exp), missing=len(missing), missing_head=missing[:5], extra=len(extra), unique=len(set(keys)) == len(keys),
                 nonempty=round(ne, 4), cap_hit=cap_rate, cap_flagged=cap_flag, logs_missing=len(need_log - have_log),
                 hook_checks={k: v for k, v in W.items() if k != "measured"}, measured=W["measured"], cumulative=cg,
                 cumulative_gating=not cum_report_only)
        r["pass_"] = bool(not missing and not extra and r["unique"] and ne >= 0.95 and r["logs_missing"] == 0 and W["pass"]
                          and (cg["pass_"] or cum_report_only))
        res[ro] = r; ok &= r["pass_"]
        print(ro, m, d, json.dumps({k: v for k, v in r.items() if k not in ("cap_hit", "cumulative")}, default=str)[:1500], flush=True)
        print("  cumulative A/arm medians:", {a_: {b: round(x, 3) for b, x in v["median_ratio"].items() if x is not None} for a_, v in cg["arms"].items()},
              "| vs r1:", cg["vs_r1"], flush=True)
    return res, ok, meas


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--model", required=True); ap.add_argument("--direction", required=True)
    ap.add_argument("--readouts", default="free,fbtw"); ap.add_argument("--sids", default="all"); ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--gates_json", default=None); ap.add_argument("--out", default=None); ap.add_argument("--write_calib", default=None)
    ap.add_argument("--calib", default=None); ap.add_argument("--dirs_root", default=f"{RUN}/dirs"); ap.add_argument("--scales", required=True)
    ap.add_argument("--cum_report_only", action="store_true")
    a = ap.parse_args()
    import torch
    sids = all_sids() if a.sids == "all" else a.sids.split(","); m, d = a.model, a.direction
    tol = K.tolerances("none" if a.write_calib else a.calib)
    signs = torch.load(f"{a.dirs_root}/dirs38p1_{m}.pt", weights_only=False)["sign"]
    scales = json.load(open(a.scales))["scales"][m]
    res, ok, meas = check(a.root, m, d, a.readouts.split(","), sids, a.samples, signs, scales, tol, a.cum_report_only)
    if a.gates_json:
        G = json.load(open(a.gates_json)); res["gates_json_pass"] = bool(G.get("pass")); ok &= res["gates_json_pass"]
        meas["g1_own_rel"] = G["G1_adapter_active"]["rel_own_max"]
    res["pass"] = bool(ok)
    if a.write_calib:
        full = dict(coord_abs=max(K.TOL_SW028["coord_abs"], 3 * meas["sub_coord_abs_err"]), along_abs=max(K.TOL_SW028["along_abs"], 3 * meas["A_along_abs_err"]))
        json.dump(dict(measured=meas, tol_full=full, rule="each absolute floor = max(sw028's calibrated value, 3 x the smoke's measured worst)"),
                  open(a.write_calib, "w"), indent=1)
        res["calib"] = dict(measured=meas, tol_full=full)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=str)
    print("OUTPUT_GATES", "PASS" if ok else "FAIL", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
