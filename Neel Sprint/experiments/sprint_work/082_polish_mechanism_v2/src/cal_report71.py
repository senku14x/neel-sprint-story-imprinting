"""sw071 calibration report + freeze (prep-71, E2, 31 Oct 2026; box 1, system python3, pure python; sw034 cal_report34 / sw038
freeze_scales38p1). Reads <cal_dir>/cal_<m>.json + scales_proposal_<m>.json (gen71 --mode cal), prints the round-1 curves, the
single / two-segment choice and the verification medians per A clamp (both directions, L28-40 and L44-63). With --freeze it writes
src/scales71.json (only if every A clamp's verification median lies in [0.9, 1.1] at BOTH bands in both directions):
  {scales: {m: {A arm: {ind|rem: {k1, k2, two_segment}}}}, verify: {...}, sources: {sha256}, created}.
  python3 cal_report71.py /workspace/runs_executor/sw082/cal [--freeze]"""
import hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common71 as C  # noqa: E402

cal = sys.argv[1]; freeze = "--freeze" in sys.argv
out = dict(created=time.strftime("%FT%TZ", time.gmtime()), rule="sw038 D14 two-segment k per (organism, A arm, direction); A clamp along r = k_L s Delta_arm",
           scales={}, verify={}, choice={}, sources={})
ok = True
for m in C.ORGS:
    R = json.load(open(f"{cal}/cal_{m}.json")); Pp = json.load(open(f"{cal}/scales_proposal_{m}.json"))
    out["scales"][m] = Pp["scales"]; out["verify"][m] = {}; out["choice"][m] = {}
    print(f"== {m} (verify pass {R['pass']})")
    for k, A in R["arms"].items():
        g = A["verify"]; ok &= bool(g["pass_"])
        out["verify"][m][k] = {a: {b: (round(x["median_ratio"][b], 4) if x["median_ratio"].get(b) is not None else None) for b in C.GATE_BANDS}
                               for a, x in g["arms"].items()}
        out["choice"][m][k] = {a: dict(single=c["single"], k_band=c["k_band"], extrapolated=c["extrapolated"]) for a, c in A["choice"].items()}
        for a, c in A["choice"].items():
            arm, d = k.split("|"); sc = Pp["scales"][a][d]
            print(f"   {a:12s} {d}: k_band {c['k_band']} single {c['single']} -> k1 {sc['k1']} k2 {sc['k2']}"
                  + (" EXTRAP" if any(c["extrapolated"].values()) else ""))
        print(f"   verify {k}: {'PASS' if g['pass_'] else 'FAIL'} " + json.dumps(out["verify"][m][k]))
    out["sources"][m] = {f: hashlib.sha256(open(f"{cal}/{f}", "rb").read()).hexdigest() for f in (f"cal_{m}.json", f"scales_proposal_{m}.json")}
    for a in out["scales"][m]:
        assert set(out["scales"][m][a]) == set(C.DIRS), (m, a)
print("ALL_VERIFY_PASS" if ok else "VERIFY_FAIL")
if freeze:
    assert ok, "refusing to freeze: a verification median lies outside [0.9, 1.1]"
    json.dump(out, open(C.SCALES_FILE, "w"), indent=1)
    print("FROZEN", C.SCALES_FILE, hashlib.sha256(open(C.SCALES_FILE, "rb").read()).hexdigest())
