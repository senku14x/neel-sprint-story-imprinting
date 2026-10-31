"""sw039 Part 2 output gates (prep-D agent, E2, 31 Oct 2026; adapted from sw038 check38p1.py). Run after gen39p2.py for one model
(both directions); exit 1 on any failed gate. torch (CPU) only to read dirs38p1's signs: the ops metadata for the known answers is
rebuilt here from dirs38p1_<m>.pt and the frozen scales file directly (not through gen39p2's unit builder), so a wrong sign / scale /
matched dose in the generator is caught.
  rows       : the EXPECTED manifest (model x direction x sids x samples x 16 arms; never "what exists"): missing = 0, extra = 0, keys
               unique; >= 95 % non-empty (forced: text longer than the bridge + 3 characters); cap-hit rate per arm reported (free
               cells > 5 % flagged, not failing)
  logs       : every s0 unit's non-none rows logged at all 14 saved layers
  hooks      : common39p2.hook_checks (dose coordinate = c_rec + alpha (c_don - c_rec); A along = k_L s x its dose arm's live offset)
  cumulative : every dose's every A arm median ratio to its dose arm in [0.9, 1.1] at L28-40 and L44-63 (fail; --cum_report_only
               in the 4-script smoke: the pre-launch size gate is the 61-script calibration verify)
  gates      : gates_<m>.json (G1 + KA alpha = 1 + G3) passed
  --smoke_sanity : the none arm's free rows: no degenerate (looping) reply and cap-hit <= 25 % (a broken engine fails this)
  --write_calib P : this smoke's measured floors; full-run tolerances = max(sw038's tol_full, 3 x measured worst over both directions)
  python check39p2.py ROOT --model hdA0 --directions induce,remove --readouts free,fbtw --scales S [--sids all|a,b] [--samples 1]
                     [--part p2|p2smoke] [--gates_json P] [--out P] [--write_calib P] [--calib P] [--cum_report_only] [--smoke_sanity]"""
import argparse, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common39p2 as K  # noqa: E402

SW38 = "/root/runs/sw038/p1"


def all_sids(ctx_path=f"{SW38}/inputs/contexts38p1.jsonl"):
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
                om[(g, a)] = dict(kind="A", s=float(sg[K.NULL_OF_A[a]]), k=K.kvec(scales[d][a]), match=f"{g}:{K.ARM_OF_A[a]}")
    return om


def check(root, m, dirs, readouts, sids, samples, signs, scales, tol, part, cum_report_only=False, smoke_sanity=False):
    res = dict(tolerances=tol, model=m); ok = True
    meas = dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0)
    for d in dirs:
        for ro in readouts:
            rd = f"{root}/{ro}"
            ns = samples or K.n_samples(ro, d)
            R = K.jl(f"{rd}/{ro}_{m}_{d}.jsonl"); keys = [r["key"] for r in R]
            exp = set(K.expected_keys([ro], [m], sids, [d], samples=ns, part=part))
            missing = sorted(exp - set(keys)); extra = sorted(set(keys) - exp)
            br = K.BRIDGES.get(ro)
            ne = sum(1 for r in R if (r["text"] or "").strip() and (not br or len(r["text"]) > len(br) + 3)) / max(len(R), 1)
            cap = defaultdict(list)
            for r in R:
                cap[r["arm"]].append(r["finish"] == "length")
            cap_rate = {arm: round(sum(v) / len(v), 4) for arm, v in sorted(cap.items())}
            cap_flag = [c for c, v in cap_rate.items() if v > 0.05] if ro == "free" else []
            alpha_ok = all(r.get("alpha") == K.ALPHA_OF.get(K.ARM_OF_A.get(r["arm"], r["arm"])) for r in R)
            logs = [e for e in K.jl(f"{rd}/log_{ro}_{m}_{d}.jsonl") if e["grp"].split("|")[2] in set(sids)]
            om = ops_meta(signs, scales, m, d, sids, ns)
            W = K.hook_checks(logs, om, tol)
            for q in meas:
                meas[q] = max(meas[q], W["measured"][q])
            have_log = {(e["grp"], e["arm"], e["L"]) for e in logs}
            need_log = {(g, arm, L) for (g, arm) in om if arm != "none" and g.endswith("|s0") for L in K.LOG14}
            cg = K.cum_gate(K.per_unit_ratios(logs))
            r = dict(rows=len(R), expected=len(exp), missing=len(missing), missing_head=missing[:5], extra=len(extra), unique=len(set(keys)) == len(keys),
                     nonempty=round(ne, 4), alpha_fields_ok=alpha_ok, cap_hit=cap_rate, cap_flagged=cap_flag, logs_missing=len(need_log - have_log),
                     hook_checks={k: v for k, v in W.items() if k != "measured"}, measured=W["measured"], cumulative=cg,
                     cumulative_gating=not cum_report_only)
            sane = True
            if smoke_sanity and ro == "free":
                nr = [x for x in R if x["arm"] == "none"]
                r["none_degenerate"] = sum(K.degenerate(x["text"]) for x in nr); r["none_cap_hit"] = sum(x["finish"] == "length" for x in nr)
                r["all_degenerate_by_arm"] = {a: sum(K.degenerate(x["text"]) for x in R if x["arm"] == a) for a in K.ARMS}
                sane = bool(nr) and r["none_degenerate"] == 0 and r["none_cap_hit"] <= 0.25 * len(nr)
                r["smoke_sanity_pass"] = sane
            r["pass_"] = bool(not missing and not extra and r["unique"] and ne >= 0.95 and r["logs_missing"] == 0 and W["pass"] and alpha_ok
                              and (cg["pass_"] or cum_report_only) and sane)
            res[f"{ro}|{d}"] = r; ok &= r["pass_"]
            print(ro, m, d, json.dumps({k: v for k, v in r.items() if k not in ("cap_hit", "cumulative")}, default=str)[:1500], flush=True)
            print("  cumulative A/dose medians:", {a_: {b: round(x, 3) for b, x in v["median_ratio"].items() if x is not None} for a_, v in cg["arms"].items()},
                  "| dose vs a1:", cg["vs_a1"], flush=True)
    return res, ok, meas


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--model", required=True)
    ap.add_argument("--directions", default="induce,remove"); ap.add_argument("--readouts", default="free,fbtw")
    ap.add_argument("--sids", default="all"); ap.add_argument("--samples", type=int, default=0); ap.add_argument("--part", default=K.PART)
    ap.add_argument("--gates_json", default=None); ap.add_argument("--out", default=None); ap.add_argument("--write_calib", default=None)
    ap.add_argument("--calib", default=None); ap.add_argument("--tol_base", default=f"{SW38}/calib.json")
    ap.add_argument("--dirs_root", default=f"{SW38}/dirs"); ap.add_argument("--scales", required=True)
    ap.add_argument("--cum_report_only", action="store_true"); ap.add_argument("--smoke_sanity", action="store_true")
    a = ap.parse_args()
    import torch
    sids = all_sids() if a.sids == "all" else a.sids.split(","); m = a.model
    tol = K.tolerances(a.calib, a.tol_base)
    signs = torch.load(f"{a.dirs_root}/dirs38p1_{m}.pt", weights_only=False)["sign"]
    scales = json.load(open(a.scales))["scales"]
    res, ok, meas = check(a.root, m, a.directions.split(","), a.readouts.split(","), sids, a.samples, signs, scales, tol, a.part,
                          a.cum_report_only, a.smoke_sanity)
    if a.gates_json:
        G = json.load(open(a.gates_json)); res["gates_json_pass"] = bool(G.get("pass")); ok &= res["gates_json_pass"]
        meas["g1_own_rel"] = G["G1_adapter_active"]["rel_own_max"]
    res["pass"] = bool(ok)
    if a.write_calib:
        base = K.tolerances(None, a.tol_base)
        full = dict(coord_abs=max(base["coord_abs"], 3 * meas["sub_coord_abs_err"]), along_abs=max(base["along_abs"], 3 * meas["A_along_abs_err"]))
        json.dump(dict(model=m, measured=meas, tol_full=full, base=a.tol_base,
                       rule="each absolute floor = max(sw038 Part 1's full-run tolerance, 3 x this smoke's measured worst over both directions)"),
                  open(a.write_calib, "w"), indent=1)
        res["calib"] = dict(measured=meas, tol_full=full)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=str)
    print("OUTPUT_GATES", "PASS" if ok else "FAIL", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
