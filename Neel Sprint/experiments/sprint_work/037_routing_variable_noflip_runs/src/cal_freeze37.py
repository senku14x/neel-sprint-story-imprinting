"""sw037 calibration report + freeze (run agent, E2; box 1, system python3; sw034 cal_report34 / calc_freeze34's role, D9).
Reads <cal_dir>/calibration_<m>.json (gen37 --mode cal) for every organism, prints the ratio-vs-c curves (L44-63 / L28-40 medians),
the c per (organism, arm) and the verification medians of every A clamp on induce (rev) and remove (fwd) units, and writes the
frozen scales file only if every A clamp's L44-63 verification median lies in [0.9, 1.1] in both directions.
  python3 cal_freeze37.py /workspace/runs_executor/sw037/cal [--freeze src/scales37.json]"""
import json, sys, time

import common37 as K

cal = sys.argv[1]
out = dict(created=time.strftime("%FT%TZ", time.gmtime()), source=cal, scales={}, curve={}, extrapolated={}, verify={}, gpu_s={},
           rule="c per (organism, arm) interpolated to a median L44-63 'gate' ratio of 1.0 (sw034 D11); frozen only if every A clamp's "
                "L44-63 verification median is in [0.9, 1.1] on induce and remove units; L28-40 reported")
ok = True
for m in K.MODELS1:
    R = json.load(open(f"{cal}/calibration_{m}.json"))
    out["scales"][m] = R["scales"]; out["curve"][m] = R["curve"]; out["gpu_s"][m] = R.get("gpu_s")
    out["extrapolated"][m] = {a: v["extrapolated"] for a, v in R["proposal"].items()}
    print(f"== {m}  (calibration GPU time {R.get('gpu_s')} s)")
    for arm, cv in R["curve"].items():
        print(f"   {arm:4s} c -> (L44-63, L28-40): " + "  ".join(f"{c:g}:({r:.3f}, {w:.3f})" for c, r, w in cv) + f"  => c = {R['proposal'][arm]['c']}"
              + (" EXTRAPOLATED" if R["proposal"][arm]["extrapolated"] else ""))
    out["verify"][m] = {}
    for d, cg in R["verify"].items():
        row = {a: dict(L44_63=x["median_ratio"].get("L44-63"), L28_40=x["median_ratio"].get("L28-40"), pass_=x["pass_"], n=x["n_units"])
               for a, x in cg["arms"].items()}
        out["verify"][m][d] = row; ok &= bool(cg["pass_"]) and len(row) == len(K.A_ARMS)
        print(f"   verify {d}: {'PASS' if cg['pass_'] else 'FAIL'}; " + "  ".join(f"{a} {v['L44_63']:.3f}/{v['L28_40']:.3f}" for a, v in row.items()))
print("ALL_VERIFY_PASS" if ok else "VERIFY_FAIL")
if len(sys.argv) > 3 and sys.argv[2] == "--freeze":
    assert ok, "refusing to freeze: a verification median lies outside [0.9, 1.1]"
    json.dump(out, open(sys.argv[3], "w"), indent=1)
    print("FROZEN", sys.argv[3])
