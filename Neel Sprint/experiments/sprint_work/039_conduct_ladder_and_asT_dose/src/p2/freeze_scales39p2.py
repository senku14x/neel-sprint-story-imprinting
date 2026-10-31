"""sw039 Part 2: freeze one model's A-clamp scales (prep-D agent, E2, 31 Oct 2026; node CPU, before any generation). Reads the
calibration outputs cal_<m>.json + scales_proposal_<m>.json, refuses (exit 1) unless the 61-script verify passed in both directions
(every dose's every A arm median in [0.9, 1.1] at L28-40 and L44-63), and writes the frozen file
  {model, scales: {induce|remove: {A arm: {k1, k2, two_segment}}}, verify: {d: {A arm: {band: median}}}, vs_a1, sources, created}
then prints FROZEN <path> <sha256>. The sha256 and values go to DECISIONS (box-1 watcher).
  python freeze_scales39p2.py <cal_dir> <model> <out_json>"""
import hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common39p2 as K  # noqa: E402


def main():
    cal, m, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    C = json.load(open(f"{cal}/cal_{m}.json")); P = json.load(open(f"{cal}/scales_proposal_{m}.json"))
    assert C["pass"] and P["verify_pass"], f"{m}: calibration verify did not pass"
    out = dict(model=m, created=time.strftime("%FT%TZ", time.gmtime()), rule="sw039 D-entry (calibration) = sw038 D14 per (direction, dose, A arm); "
               "A clamp along r = k_L * s * Delta_dose; k_L = k1 at L16-40, k2 at L41-63; all 61 scripts, prefill only",
               scales=P["scales"], verify={}, vs_a1={}, sources={})
    for d in ("induce", "remove"):
        g = C["directions"][d]["verify"]["gate"]
        assert g["pass_"] and set(g["arms"]) == set(K.A_ARMS), (d, g["fail"], g["missing"])
        for a, v in g["arms"].items():
            assert all(K.CUM_LO <= v["median_ratio"][b] <= K.CUM_HI for b in K.GATE_BANDS), (m, d, a, v)
        assert set(P["scales"][d]) == set(K.A_ARMS)
        for a, v in P["scales"][d].items():
            assert 0.0 < v["k1"] < 3.0 and 0.0 < v["k2"] < 3.0, (d, a, v)
        out["verify"][d] = {a: {b: round(v["median_ratio"][b], 4) for b in K.GATE_BANDS} for a, v in g["arms"].items()}
        out["vs_a1"][d] = g["vs_a1"]
    out["sources"] = {f: hashlib.sha256(open(f"{cal}/{f}", "rb").read()).hexdigest() for f in (f"cal_{m}.json", f"scales_proposal_{m}.json")}
    json.dump(out, open(outp + ".tmp", "w"), indent=1); os.replace(outp + ".tmp", outp)
    print("FROZEN", outp, hashlib.sha256(open(outp, "rb").read()).hexdigest())
    for d in ("induce", "remove"):
        print(m, d, {a: (v["k1"], v["k2"]) for a, v in out["scales"][d].items()})
        print("   verify", out["verify"][d])


if __name__ == "__main__":
    main()
