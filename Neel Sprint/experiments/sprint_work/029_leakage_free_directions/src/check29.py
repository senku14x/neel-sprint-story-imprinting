"""sw029 output gates and smoke calibration (prep agent, E2, 31 Oct 2026). Run after gen29_x.py; exit 1 on any failed gate.
torch (CPU) only to read dirs29's signs: the ops metadata for the known answers is rebuilt here from dirs29_<m>.pt directly (not
through gen29's unit builder), so a wrong sign / match in the generator is caught.
  rows      : the EXPECTED manifest (model x directions x sids x samples x 23 arms; never "what exists"): missing = 0, extra = 0, keys
              unique; >= 95 % non-empty (forced: text longer than the bridge + 3 characters); cap-hit rate per (direction, arm)
              cell reported, cells > 5 % flagged (free)
  logs      : every s0 unit's non-none rows logged at all 14 saved layers
  hooks     : common29.hook_checks on the live logs (coordinate = target for every sub arm at header / Assistant sites; A along
              offset = s x its arm's live offset)
  cumulative: every A arm's median ratio to its own arm at L28-40 and L44-63 >= 0.9 at every site of the arm (fail)
  gates     : gates_<m>.json (G1 + G3) passed
  --write_calib PATH (smoke): this path's measured floors and the full-run tolerances = max(sw028's value, 3 x measured worst)
  python check29.py ROOT --model hdA0 --readouts free,fbtw,fraf --directions rev,fwd --sids a,b|all [--samples 1] [--gates_json P]
                   [--out P] [--write_calib P] [--calib P] [--dirs_root D]"""
import argparse, json, os, sys
from collections import defaultdict

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402

SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"


def all_sids():
    return sorted({json.loads(l)["sid"] for l in open(f"{SW8}/contexts.jsonl") if json.loads(l)["cond"] == "self-hostile"})


def ops_meta_from_dirs(dm, m, sids, dirs, samples_of):
    om = {}
    for sid in sids:
        for d in dirs:
            for k in range(samples_of(d)):
                g = K.unit_id(m, d, sid, k); sg = dm["sign"][f"{d}|{sid}"]
                om[(g, "none")] = dict(kind="none")
                for a in K.SUB_ARMS:
                    om[(g, a)] = dict(kind="sub")
                for a in K.A_ARMS:
                    om[(g, a)] = dict(kind="A", s=float(sg[a]), match=f"{g}:{K.ARM_OF_A[a]}")
    return om


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--model", required=True); ap.add_argument("--readouts", default="free")
    ap.add_argument("--directions", default="rev,fwd"); ap.add_argument("--sids", default="all"); ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--gates_json", default=None); ap.add_argument("--out", default=None); ap.add_argument("--write_calib", default=None)
    ap.add_argument("--calib", default=None); ap.add_argument("--dirs_root", default="/root/runs/sw029")
    a = ap.parse_args()
    sids = all_sids() if a.sids == "all" else a.sids.split(","); dirs = a.directions.split(","); m = a.model
    tol = K.tolerances("none" if a.write_calib else a.calib)
    dm = torch.load(f"{a.dirs_root}/dirs29_{m}.pt", weights_only=False)
    res = dict(tolerances=tol, model=m); ok = True
    meas = dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0)
    for ro in a.readouts.split(","):
        rd = f"{a.root}/{ro}"
        samples_of = (lambda d: a.samples) if a.samples else (lambda d, ro=ro: K.n_samples(ro, d))
        R = K.jl(f"{rd}/{ro}_{m}.jsonl"); keys = [r["key"] for r in R]
        exp = {K.row_key(ro, m, d, s, arm, k) for d in dirs for s in sids for k in range(samples_of(d)) for arm in K.ARMS}
        missing = sorted(exp - set(keys)); extra = sorted(set(keys) - exp)
        br = K.BRIDGES.get(ro)
        ne = sum(1 for r in R if (r["text"] or "").strip() and (not br or len(r["text"]) > len(br) + 3)) / max(len(R), 1)
        cap = defaultdict(list)
        for r in R:
            cap[(r["direction"], r["arm"])].append(r["finish"] == "length")
        cap_rate = {f"{d}|{arm}": round(sum(v) / len(v), 4) for (d, arm), v in sorted(cap.items())}
        cap_flag = [c for c, v in cap_rate.items() if v > 0.05] if ro == "free" else []
        logs = [e for e in K.jl(f"{rd}/log_{ro}_{m}.jsonl") if e["grp"].split("|")[1] in dirs and e["grp"].split("|")[2] in set(sids)]
        om = ops_meta_from_dirs(dm, m, sids, dirs, samples_of)
        W = K.hook_checks(logs, om, tol)
        for q in meas:
            meas[q] = max(meas[q], W["measured"][q])
        have_log = {(e["grp"], e["arm"], e["L"]) for e in logs}
        need_log = {(g, arm, L) for (g, arm) in om if arm != "none" and g.endswith("|s0") for L in K.LOG14}
        cg = K.cum_gate(K.cum_ratios(logs))
        r = dict(rows=len(R), expected=len(exp), missing=len(missing), missing_head=missing[:5], extra=len(extra), unique=len(set(keys)) == len(keys),
                 nonempty=round(ne, 4), cap_hit=cap_rate, cap_flagged=cap_flag, logs_missing=len(need_log - have_log),
                 hook_checks={k: v for k, v in W.items() if k != "measured"}, measured=W["measured"], cumulative=cg)
        r["pass_"] = bool(not missing and not extra and r["unique"] and ne >= 0.95 and r["logs_missing"] == 0 and W["pass"] and cg["pass_"])
        res[ro] = r; ok &= r["pass_"]
        print(ro, m, json.dumps({k: v for k, v in r.items() if k not in ("cap_hit", "cumulative")}, default=str)[:1500], flush=True)
        print("  cumulative A/arm medians:", {a_: {s: {b: round(x, 3) for b, x in v.items() if x is not None} for s, v in d_["median_ratio"].items()}
                                             for a_, d_ in cg["arms"].items()}, flush=True)
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
