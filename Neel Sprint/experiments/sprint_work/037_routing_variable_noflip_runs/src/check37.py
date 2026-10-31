"""sw037 Part 1 output gates and smoke calibration of the tolerances (run agent, E2; adapted from sw029 check29.py). Exit 1 on any failure.
The ops metadata for the known answers is rebuilt from dirs37_<m>.pt and scales37.json directly (not through gen37's unit builder).
  rows      : the EXPECTED manifest (directions x sids x samples x 7 arms): missing = 0, extra = 0, keys unique; >= 95 % non-empty
              (forced: text longer than the bridge + 3 characters); cap-hit per (direction, arm) reported, > 5 % flagged (free)
  logs      : every s0 unit's non-none rows logged at all 14 saved layers
  hooks     : common37.hook_checks on the live logs (coordinate = target; A along = s c x its arm's live offset)
  size      : every A clamp's realised median 'gate' ratio at L44-63 in [0.9, 1.1] (the calibration's window; L28-40 reported)
  gates     : gates_<m>.json (G1 + G3) passed
  --write_calib PATH (smoke): measured floors -> full-run tolerances = max(sw028's value, 3 x measured worst) (sw029 D12)
  python check37.py ROOT --model m --readouts fbtw,free --directions rev,fwd --sids a,b|all [--samples N] [--gates_json P] [--out P]"""
import argparse, json, os, sys
from collections import defaultdict

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common37 as K  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--model", required=True); ap.add_argument("--readouts", default="fbtw")
    ap.add_argument("--directions", default="rev,fwd"); ap.add_argument("--sids", default="all"); ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--gates_json", default=None); ap.add_argument("--out", default=None); ap.add_argument("--write_calib", default=None)
    ap.add_argument("--calib", default=None); ap.add_argument("--dirs_root", default=K.RUN); ap.add_argument("--scales", default=f"{HERE}/scales37.json")
    a = ap.parse_args()
    sids = K.all_sids() if a.sids == "all" else a.sids.split(","); dirs = a.directions.split(","); m = a.model
    tol = K.tolerances("none" if a.write_calib else a.calib)
    dm = torch.load(f"{a.dirs_root}/dirs37_{m}.pt", weights_only=False)
    sc_ = json.load(open(a.scales))["scales"][m]
    res = dict(tolerances=tol, model=m, scales=sc_); ok = True
    meas = dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0)
    for ro in a.readouts.split(","):
        rd = f"{a.root}/{ro}"; ns = a.samples or K.SAMPLES1[ro]
        R = K.jl(f"{rd}/{ro}_{m}.jsonl"); keys = [r["key"] for r in R]
        exp = set(K.expected_keys1(ro, [m], sids, dirs, ns))
        missing = sorted(exp - set(keys)); extra = sorted(set(keys) - exp)
        br = K.BRIDGES.get(ro)
        ne = sum(1 for r in R if (r["text"] or "").strip() and (not br or len(r["text"]) > len(br) + 3)) / max(len(R), 1)
        cap = defaultdict(list)
        for r in R:
            cap[(r["direction"], r["arm"])].append(r["finish"] == "length")
        cap_rate = {f"{d}|{arm}": round(sum(v) / len(v), 4) for (d, arm), v in sorted(cap.items())}
        cap_flag = [c for c, v in cap_rate.items() if v > 0.05] if ro == "free" else []
        cwrong = [r["key"] for r in R if r["arm"] in K.ARM_OF_A and abs(float(r["c"]) - float(sc_[K.ARM_OF_A[r["arm"]]])) > 1e-9]
        logs = [e for e in K.jl(f"{rd}/log_{ro}_{m}.jsonl") if e["grp"].split("|")[1] in dirs and e["grp"].split("|")[2] in set(sids)]
        om = {}
        for sid in sids:
            for d in dirs:
                for k in range(ns):
                    g = K.unit_id(m, d, sid, k); sg = dm["sign"][f"{d}|{sid}"]
                    om[(g, "none")] = dict(kind="none")
                    for arm in K.REAL1:
                        om[(g, arm)] = dict(kind="sub")
                    for arm in K.A_ARMS:
                        om[(g, arm)] = dict(kind="A", s=float(sg[arm]), c=float(sc_[K.ARM_OF_A[arm]]), match=f"{g}:{K.ARM_OF_A[arm]}")
        W = K.hook_checks(logs, om, tol)
        for q in meas:
            meas[q] = max(meas[q], W["measured"][q])
        have_log = {(e["grp"], e["arm"], e["L"]) for e in logs}
        need_log = {(g, arm, L) for (g, arm) in om if arm != "none" and g.endswith("|s0") for L in K.LOG14}
        cg = K.cum_gate(K.gate_ratios(logs))
        r = dict(rows=len(R), expected=len(exp), missing=len(missing), missing_head=missing[:5], extra=len(extra), unique=len(set(keys)) == len(keys),
                 nonempty=round(ne, 4), cap_hit=cap_rate, cap_flagged=cap_flag, c_mismatch=len(cwrong), logs_missing=len(need_log - have_log),
                 hook_checks={k: v for k, v in W.items() if k != "measured"}, measured=W["measured"], size=cg)
        size_ok = cg["pass_"] if a.sids == "all" else True      # the smoke's 4-script medians are reported, not gated (sw031 D21)
        r["pass_"] = bool(not missing and not extra and r["unique"] and ne >= 0.95 and r["logs_missing"] == 0 and W["pass"] and size_ok and not cwrong)
        res[ro] = r; ok &= r["pass_"]
        print(ro, m, json.dumps({k: v for k, v in r.items() if k not in ("cap_hit", "size")}, default=str)[:1500], flush=True)
        print("  size A/arm medians (L44-63, L28-40):", {a_: (round(d_["median_ratio"].get("L44-63") or 0, 3), round(d_["median_ratio"].get("L28-40") or 0, 3))
                                                       for a_, d_ in cg["arms"].items()}, flush=True)
    if a.gates_json:
        G = json.load(open(a.gates_json)); res["gates_json_pass"] = bool(G.get("pass")); ok &= res["gates_json_pass"]
    res["pass"] = bool(ok)
    if a.write_calib:
        full = dict(coord_abs=max(K.TOL_SW028["coord_abs"], 3 * meas["sub_coord_abs_err"]), along_abs=max(K.TOL_SW028["along_abs"], 3 * meas["A_along_abs_err"]))
        old = json.load(open(a.write_calib)) if os.path.exists(a.write_calib) else None
        if old:   # several organisms write the same file: keep the max over them
            full = {k: max(full[k], old["tol_full"][k]) for k in full}
            meas = {k: max(meas[k], old["measured"].get(k, 0.0)) for k in meas}
        json.dump(dict(measured=meas, tol_full=full, rule="each absolute floor = max(sw028's calibrated value, 3 x the smoke's measured worst), max over organisms"),
                  open(a.write_calib, "w"), indent=1)
        res["calib"] = dict(measured=meas, tol_full=full)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=str)
    print("OUTPUT_GATES", "PASS" if ok else "FAIL", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
