"""sw034 output gates (prep agent, E2, 31 Oct 2026; node or box 1, torch for the dirs file). Exit 1 on failure.
Manifest = common34.expected_keys (never "what exists"): missing = 0, extra = 0, keys unique, >= 95 % non-empty, cap-hit per
(utype, dir, arm) cell (free, > 5 % flagged), every s0 unit's non-none rows logged at the 14 layers, hook_checks (ops rebuilt from
dirs34's signs and the frozen scales, not from the generator) and the cumulative gate (A clamps' L44-63 median in [0.9, 1.1];
M rows' realised ratio reported).
  python check34.py ROOT --model e08-N --readouts fbtw,free [--npairs N] [--samples 1] [--calib P] [--out P] [--write_calib P]"""
import argparse, json, os, sys
from collections import defaultdict

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--model", required=True); ap.add_argument("--readouts", default="fbtw,free")
    ap.add_argument("--npairs", type=int, default=None); ap.add_argument("--samples", type=int, default=0); ap.add_argument("--calib", default=None)
    ap.add_argument("--out", default=None); ap.add_argument("--write_calib", default=None); ap.add_argument("--dirs_root", default="/root/runs/sw034")
    ap.add_argument("--scales", default=C.SCALES_FILE)
    a = ap.parse_args(); m = a.model; P = C.load_pairs()
    tol = C.tolerances("none" if a.write_calib else a.calib)
    dm = torch.load(f"{a.dirs_root}/dirs34_{m}.pt", weights_only=False); sc = json.load(open(a.scales))["scales"][m]
    res = dict(model=m, tolerances=tol, scales=sc); ok = True; meas = defaultdict(float)
    for ro in a.readouts.split(","):
        ns = a.samples or C.SAMPLES[ro]
        R = C.jl(f"{a.root}/{ro}/{ro}_{m}.jsonl"); keys = [r["key"] for r in R]
        exp = set(C.expected_keys("A", ro, m, P, ns, npairs=a.npairs))
        missing = sorted(exp - set(keys)); extra = sorted(set(keys) - exp)
        br = C.BRIDGES.get(ro)
        ne = sum(1 for r in R if (r["text"] or "").strip() and (not br or len(r["text"]) > len(br) + 3)) / max(len(R), 1)
        cap = defaultdict(list)
        for r in R:
            cap[(r["utype"], r["direction"], r["arm"])].append(r["finish"] == "length")
        cap_rate = {"|".join(k): round(sum(v) / len(v), 4) for k, v in sorted(cap.items())}
        cap_flag = [c for c, v in cap_rate.items() if v > 0.05] if ro == "free" else []
        logs = C.jl(f"{a.root}/{ro}/log_{ro}_{m}.jsonl")
        om = {}
        for (u, d, s, v) in C.unit_list(P, m, npairs=a.npairs):
            g = C.unit_id("A", m, u, d, s, v, 0); sg = dm["sign"][f"{u}|{d}|{s}|{v}"]
            for arm in C.ARMS[u]:
                base, kind = C.arm_base(arm)
                if kind == "none":
                    om[(g, arm)] = dict(kind="none")
                elif kind == "real":
                    om[(g, arm)] = dict(kind="sub")
                elif kind == "A":
                    om[(g, arm)] = dict(kind="A", s=float(sg[arm]), c=float(sc[base]))
                else:
                    om[(g, arm)] = dict(kind="full" if C.SITE[base] == "hdr" else "mclamp")
        logs = [e for e in logs if (e["grp"], e["arm"]) in om]
        W = C.hook_checks(logs, om, tol)
        for q, v in W["measured"].items():
            meas[q] = max(meas[q], v)
        need = {(g, arm, L) for (g, arm), o in om.items() if o["kind"] != "none" for L in C.LOG14}; have = {(e["grp"], e["arm"], e["L"]) for e in logs}
        cg = C.cum_gate(C.cum_ratios(logs))
        r = dict(rows=len(R), expected=len(exp), missing=len(missing), missing_head=missing[:5], extra=len(extra), unique=len(set(keys)) == len(keys),
                 nonempty=round(ne, 4), cap_flagged=cap_flag, cap_max=max(cap_rate.values()) if cap_rate else None, logs_missing=len(need - have),
                 hook_checks={k: v for k, v in W.items() if k != "measured"}, measured=W["measured"], cumulative=cg)
        r["pass_"] = bool(not missing and not extra and r["unique"] and ne >= 0.95 and r["logs_missing"] == 0 and W["pass"] and cg["pass_"])
        res[ro] = r; ok &= r["pass_"]
        print(ro, m, json.dumps({k: v for k, v in r.items() if k not in ("cumulative",)}, default=str)[:1500], flush=True)
        print("  cumulative medians:", {a_: {b: round(x or 0, 3) for b, x in d_["median_ratio"].items()} for a_, d_ in cg["arms"].items()}, flush=True)
    res["pass"] = bool(ok)
    if a.write_calib:
        full = dict(coord_abs=max(C.TOL["coord_abs"], 3 * meas["sub_coord_abs_err"]), along_abs=max(C.TOL["along_abs"], 3 * meas["A_along_abs_err"]),
                    full_rel=max(C.TOL["full_rel"], 3 * meas["full_rel_err"]), mclamp_rel=max(C.TOL["mclamp_rel"], 3 * meas["mclamp_rel_err"]))
        json.dump(dict(measured=dict(meas), tol_full=full), open(a.write_calib, "w"), indent=1)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=str)
    print("OUTPUT_GATES", "PASS" if ok else "FAIL", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
