"""sw038 Part 1: freeze the A-clamp scales (prep-P1 agent, E2, 31 Oct 2026; box 1, system python3). Reads the calibration outputs
(cal_<m>.json + scales_proposal_<m>.json, copied from /root/runs/sw038/p1/cal/), refuses unless both models' 61-script verify
passed (every A arm's median in [0.9, 1.1] at both bands, both directions), and writes src/p1/scales38p1.json:
  {scales: {m: {induce|remove: {A arm: {k1, k2, two_segment}}}}, verify: {m: {d: {A arm: {band: median}}}}, sources, created}.
  python3 freeze_scales38p1.py <cal_dir>"""
import hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p1 as K  # noqa: E402

cal = sys.argv[1]
out = dict(created=time.strftime("%FT%TZ", time.gmtime()), rule="D14 (calibration) / sw038 design_spec: A clamp along r = k_L * s * Delta_arm; "
           "k_L = k1 at L16-40, k2 at L41-63; calibrated per (model, direction, A arm) on all 61 scripts, prefill only",
           scales={}, verify={}, sources={})
for m in K.MODELS:
    C = json.load(open(f"{cal}/cal_{m}.json")); P = json.load(open(f"{cal}/scales_proposal_{m}.json"))
    assert C["pass"] and P["verify_pass"], f"{m}: calibration verify did not pass"
    for d in ("induce", "remove"):
        g = C["directions"][d]["verify"]["gate"]
        assert g["pass_"] and set(g["arms"]) == set(K.A_ARMS)
        for a, v in g["arms"].items():
            assert all(K.CUM_LO <= v["median_ratio"][b] <= K.CUM_HI for b in K.GATE_BANDS), (m, d, a, v)
        assert set(P["scales"][d]) == set(K.A_ARMS)
    out["scales"][m] = P["scales"]
    out["verify"][m] = {d: {a: {b: round(v["median_ratio"][b], 4) for b in K.GATE_BANDS} for a, v in C["directions"][d]["verify"]["gate"]["arms"].items()}
                        for d in ("induce", "remove")}
    out["sources"][m] = {f: hashlib.sha256(open(f"{cal}/{f}", "rb").read()).hexdigest() for f in (f"cal_{m}.json", f"scales_proposal_{m}.json")}
json.dump(out, open(f"{HERE}/scales38p1.json", "w"), indent=1)
print("FROZEN", f"{HERE}/scales38p1.json", hashlib.sha256(open(f"{HERE}/scales38p1.json", "rb").read()).hexdigest())
for m in K.MODELS:
    for d in ("induce", "remove"):
        print(m, d, {a: (v["k1"], v["k2"]) for a, v in out["scales"][m][d].items()})
        print("   verify", out["verify"][m][d])
