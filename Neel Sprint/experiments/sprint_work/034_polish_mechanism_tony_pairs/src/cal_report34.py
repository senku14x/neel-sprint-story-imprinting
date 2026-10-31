"""sw034 calibration report + freeze (prep agent, E2, 31 Oct 2026; box 1, system python3, pure python; sw031 cal_report31's role).
Reads <cal_dir>/calibration_<m>.json (gen34 --mode cal), prints the ratio-vs-c curves (L44-63 / L28-40 medians), the proposed c per
(organism, arm) and the verification medians per A clamp on induce and remove units. With --freeze OUT it writes the frozen scales
file the smoke and the full run read (only if every A clamp's L44-63 verification median lies in [0.9, 1.1] in both directions).
  python3 cal_report34.py /workspace/runs_executor/sw034/cal [--freeze src/scales34.json]"""
import json, sys, time

import common34 as C

cal = sys.argv[1]
out = dict(created=time.strftime("%FT%TZ", time.gmtime()), source=cal, scales={}, verify={}, curve={}, extrapolated={})
ok = True
for m in C.ORGS:
    R = json.load(open(f"{cal}/calibration_{m}.json"))
    out["scales"][m] = R["scales"]; out["curve"][m] = R["curve"]; out["extrapolated"][m] = {a: v["extrapolated"] for a, v in R["proposal"].items()}
    print(f"== {m}")
    for arm, cv in R["curve"].items():
        print(f"   {arm:9s} c -> (L44-63, L28-40): " + "  ".join(f"{c:g}:({r:.3f}, {w:.3f})" for c, r, w in cv) + f"  => c = {R['proposal'][arm]['c']}"
              + (" EXTRAPOLATED" if R["proposal"][arm]["extrapolated"] else ""))
    out["verify"][m] = {}
    for d, cg in R["verify"].items():
        row = {a: dict(L44_63=x["median_ratio"].get("L44-63"), L28_40=x["median_ratio"].get("L28-40"), pass_=x.get("pass_"), L28_40_in_band=x.get("L28_40_in_band"),
                       n=x.get("n_units")) for a, x in cg["arms"].items()}
        out["verify"][m][d] = row; ok &= bool(cg["pass_"])
        print(f"   verify {d}: gate {'PASS' if cg['pass_'] else 'FAIL'}; " + "  ".join(f"{a} {v['L44_63']:.3f}/{v['L28_40']:.3f}" for a, v in row.items()))
print("ALL_VERIFY_PASS" if ok else "VERIFY_FAIL")
if len(sys.argv) > 3 and sys.argv[2] == "--freeze":
    assert ok, "refusing to freeze: a verification median lies outside [0.9, 1.1]"
    json.dump(out, open(sys.argv[3], "w"), indent=1)
    print("FROZEN", sys.argv[3])
