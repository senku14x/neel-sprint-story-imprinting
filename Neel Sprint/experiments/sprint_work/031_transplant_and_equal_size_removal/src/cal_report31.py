"""sw031 calibration report (prep agent, E2, 31 Oct 2026; system python3, pure python). Reads <cal_dir>/calibration.json and
log_verify_<m>.jsonl (gen31 --part cal). Prints the ratio-vs-c curves, the proposed scale per (model, dose), the verification
ratios per arm, and how stable a median over k scripts would be (k = 4, 8, 16: 5th-95th percentile of the median over 2,000
seeded random subsets, at the proposed c). --freeze OUT writes the frozen scales file used by the full run.
  python3 cal_report31.py /workspace/runs_executor/sw031/smoke/cal [--freeze src/scales31.json]"""
import json, random, sys, time

import common31 as C31

cal = sys.argv[1]
R = json.load(open(f"{cal}/calibration.json"))
out = dict(created=time.strftime("%FT%TZ", time.gmtime()), source=f"{cal}/calibration.json", scales={}, verify={}, subset_spread={})
for m in C31.MODELS:
    M = R["models"][m]
    print(f"== {m} (n scripts {M['n_scripts']}) median L44-63 ratio to r1 per direction and c")
    for i in range(3):
        print(f"   A{i}: " + "  ".join(f"c{c:g}:{M['table'][f'cal{i}_{c:g}']['L44-63']:.3f}" for c in R["grid"]))
    for d, v in M["proposal"].items():
        print(f"   dose {d}: c = {v['c']:.4f}{' (EXTRAPOLATED)' if v['extrapolated'] else ''}; pooled curve " + " ".join(f"{c:g}:{r:.3f}" for c, r in v["curve"]))
    V = R["verify"][m]
    out["scales"][m] = {d: V["scales"][d] for d in C31.DOSE_TARGET}
    out["verify"][m] = {a: dict(L28_40=x["median_ratio"].get("L28-40"), L44_63=x["median_ratio"].get("L44-63"), pass_=x.get("pass_"))
                        for a, x in V["gate"]["arms"].items()}
    print(f"   verify at {V['scales']}: gate pass {V['gate']['pass_']}; " + "  ".join(f"{a} {x['median_ratio']['L44-63']:.3f}" for a, x in V["gate"]["arms"].items()))
    logs = [json.loads(l) for l in open(f"{cal}/log_verify_{m}.jsonl")]
    per = C31.cum_ratios(logs, "r1")
    rng = random.Random(31)
    sp = {}
    for arm in ("A10_0", "A10_1", "A10_2", "A05_0", "A14_0", "skF"):
        v = per[arm]["L44-63"]; sp[arm] = {}
        for k in (4, 8, 16):
            meds = sorted(C31.median(rng.sample(v, k)) for _ in range(2000))
            sp[arm][k] = [round(meds[100], 3), round(meds[1900], 3)]
        sp[arm]["per_script_range"] = [round(min(v), 3), round(max(v), 3)]
    out["subset_spread"][m] = sp
    print("   median over k random scripts, 5-95 %: " + json.dumps(sp))
if len(sys.argv) > 3 and sys.argv[2] == "--freeze":
    json.dump(out, open(sys.argv[3], "w"), indent=1)
    print("FROZEN", sys.argv[3])
