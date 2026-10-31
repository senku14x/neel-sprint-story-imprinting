"""sw029 Part B output gates (prep agent, E2, 31 Oct 2026); Part A's check29 logic with common29b's spec versions. Exit 1 on failure.
Manifest = common29b.expected_keys over the part's pairs (or the first --pairs), never "what exists": missing = 0, extra = 0, keys
unique, >= 95 % non-empty, cap-hit per (cond, arm) cell (free, > 5 % flagged), every s0 induce unit's non-none rows logged at the 14
layers, hook_checks (ops rebuilt from dirs29b's signs, not from the generator) and the cumulative gate.
  python check29b.py ROOT --model e08-X --readouts free,fbtw,fraf [--pairs N] [--samples 1] [--calib P] [--out P] [--write_calib P]"""
import argparse, json, os, sys
from collections import defaultdict

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
import common29b as KB  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--model", required=True); ap.add_argument("--readouts", default="free")
    ap.add_argument("--pairs", type=int, default=None); ap.add_argument("--samples", type=int, default=0); ap.add_argument("--calib", default=None)
    ap.add_argument("--out", default=None); ap.add_argument("--write_calib", default=None); ap.add_argument("--dirs_root", default="/root/runs/sw029")
    a = ap.parse_args(); m = a.model; spec = KB.SPECS[KB.PART_OF[m]]
    _, pairs = KB.load_contexts(spec); pairs = pairs[:a.pairs]
    tol = K.tolerances("none" if a.write_calib else a.calib)
    dm = torch.load(f"{a.dirs_root}/dirs29b_{m}.pt", weights_only=False)
    res = dict(model=m, part=spec["part"], tolerances=tol); ok = True; meas = dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0)
    for ro in a.readouts.split(","):
        ns = a.samples or KB.n_samples(spec, ro)
        R = K.jl(f"{a.root}/{ro}/{ro}_{m}.jsonl"); keys = [r["key"] for r in R]
        exp = {KB.row_key(spec["part"], ro, m, spec["rec_cond"], sid, v, arm, kk) for sid, v in pairs for kk in range(ns) for arm in spec["arms"]} | \
              {KB.row_key(spec["part"], ro, m, spec["don_cond"], sid, v, "none", kk) for sid, v in pairs for kk in range(ns)}
        missing = sorted(exp - set(keys)); extra = sorted(set(keys) - exp)
        br = K.BRIDGES.get(ro)
        ne = sum(1 for r in R if (r["text"] or "").strip() and (not br or len(r["text"]) > len(br) + 3)) / max(len(R), 1)
        cap = defaultdict(list)
        for r in R:
            cap[(r["cond"], r["arm"])].append(r["finish"] == "length")
        cap_rate = {f"{c}|{arm}": round(sum(v) / len(v), 4) for (c, arm), v in sorted(cap.items())}
        cap_flag = [c for c, v in cap_rate.items() if v > 0.05] if ro == "free" else []
        logs = K.jl(f"{a.root}/{ro}/log_{ro}_{m}.jsonl")
        om = {}
        for sid, v in pairs:
            g = KB.unit_id(spec["part"], m, spec["rec_cond"], sid, v, 0); sg = dm["sign"][f"{sid}|{v or '-'}"]
            om[(g, "none")] = dict(kind="none")
            for arm in spec["sub_arms"]:
                om[(g, arm)] = dict(kind="sub")
            for arm in spec["A_ARMS"]:
                om[(g, arm)] = dict(kind="A", s=float(sg[arm]), match=f"{g}:{spec['ARM_OF_A'][arm]}")
        logs = [e for e in logs if (e["grp"], e["arm"]) in om]
        W = KB.hook_checks(logs, om, tol, spec)
        for q in meas:
            meas[q] = max(meas[q], W["measured"][q])
        need = {(g, arm, L) for (g, arm) in om if arm != "none" for L in K.LOG14}; have = {(e["grp"], e["arm"], e["L"]) for e in logs}
        cg = KB.cum_gate(KB.cum_ratios(logs, spec), spec)
        r = dict(rows=len(R), expected=len(exp), missing=len(missing), missing_head=missing[:5], extra=len(extra), unique=len(set(keys)) == len(keys),
                 nonempty=round(ne, 4), cap_hit=cap_rate, cap_flagged=cap_flag, logs_missing=len(need - have),
                 hook_checks={k: v for k, v in W.items() if k != "measured"}, measured=W["measured"], cumulative=cg)
        r["pass_"] = bool(not missing and not extra and r["unique"] and ne >= 0.95 and r["logs_missing"] == 0 and W["pass"] and cg["pass_"])
        res[ro] = r; ok &= r["pass_"]
        print(ro, m, json.dumps({k: v for k, v in r.items() if k not in ("cap_hit", "cumulative")}, default=str)[:1200], flush=True)
        print("  cumulative A/arm medians:", {a_: d_["median_ratio"] for a_, d_ in cg["arms"].items()}, flush=True)
    res["pass"] = bool(ok)
    if a.write_calib:
        full = dict(coord_abs=max(K.TOL_SW028["coord_abs"], 3 * meas["sub_coord_abs_err"]), along_abs=max(K.TOL_SW028["along_abs"], 3 * meas["A_along_abs_err"]))
        json.dump(dict(measured=meas, tol_full=full), open(a.write_calib, "w"), indent=1)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=str)
    print("OUTPUT_GATES_B", "PASS" if ok else "FAIL", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
