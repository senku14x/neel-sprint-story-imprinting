"""sw034 parP calibration freeze (D33) (prep agent, E2; box 1, system python3). Reads <calC>/calibration_<m>.json (gen34p --mode cal) for the
given organisms, prints the curves and verification, and writes src/scales34p_<m>.json only if every A clamp's L44-63 verification
median lies in [0.9, 1.1] in both directions (D11's rule).   python3 calc_freeze34.py /workspace/runs_executor/sw034/calP e08-N,e08-X"""
import json, os, sys, time
cal, models = sys.argv[1], sys.argv[2].split(",")
HERE = os.path.dirname(os.path.abspath(__file__)); ok_all = True
for m in models:
    R = json.load(open(f"{cal}/calibration_{m}.json"))
    print(f"== {m} c = {R['c']} extrapolated {R['extrapolated']}")
    for a, cv in R["curve"].items():
        print(f"   {a:7s} " + "  ".join(f"{c:g}:({r:.3f}, {w:.3f})" for c, r, w in cv))
    ok = True
    for d, g in R["verify"].items():
        ok &= bool(g["pass_"])
        print(f"   verify {d}: {'PASS' if g['pass_'] else 'FAIL'} " + "  ".join(f"{a} {x['median_ratio'].get('L44-63', 0):.3f}/{x['median_ratio'].get('L28-40', 0):.3f}" for a, x in g["arms"].items()))
    if ok:
        json.dump(dict(created=time.strftime("%FT%TZ", time.gmtime()), source=f"{cal}/calibration_{m}.json", c=R["c"], verify=R["verify"]),
                  open(f"{HERE}/scales34p_{m}.json", "w"), indent=1)
        print("   FROZEN", f"{HERE}/scales34p_{m}.json")
    ok_all &= ok
print("ALL_VERIFY_PASS" if ok_all else "VERIFY_FAIL")
