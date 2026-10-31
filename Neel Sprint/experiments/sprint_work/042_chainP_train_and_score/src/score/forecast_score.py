"""sw042: score the frozen forecast (spec 05 sec 4.7 as amended by sw041 D3). Box 1, CPU; after `analyze.py contrasts`.
  python3 forecast_score.py --forecast FORECAST.json [--run RUN]   -> ROOT/[RUN/]forecast_score.json
Quantities are scored SEPARATELY (no MSE over mixed quantities), each against its own trivial rules:
  theta_main  (conversation readout, default; draws = contrasts_boot.json scenario-bootstrap resamples)
              T-pol  sign(g) * 1.60 (0 at matched register), T-help -1.14 (spec 05 sec 4.7), and T-lin TAKEN FROM forecast.json
              'trivial_theta' (sw041 D7/D8: the bad-actor-orientation refit on the one-protocol P0 targets, not spec 05's
              -0.565 + 0.800 g); T-pol / T-help in the file are checked against spec 05's definitions
  dl_main     (R-flaw flag rate, log-odds, main pooled relative to the HONEST CONTROL; item-bootstrap resamples)
              T0 0, T-pc -4.21 (main; mirror 0), T-ct -2.10 (both)   [sw041 D3; dl_pc = -4.2068, sw041 results_flaw.json]
A forecaster 'works' on a quantity if its squared error is below the best trivial rule's in >= 90% of resamples AND the observed
value lies in its 80% interval (one value per quantity, so 'at least half' = inside). Mirror quantities and dl relative to the parent
are computed and RECORDED, not scored. R-capitulation never enters. Forecasters whose name contains '_D6' (D6's original lines) and
everything under 'alternative_not_scored' are computed and labelled as unscored alternatives (sw041 D7). The primary forecaster is the
file's 'primary' (P3_sym per D7). If it is a P5 variant (judged assistant-likeness), P5 vs T-lin is flagged as nearly circular.
FORECAST.json: {"primary": "P2", "judged_gap": {"main": g, "mirror": g},
                "forecasters": {"P2": {"theta": {"main": {"point": x, "lo80": a, "hi80": b}, "mirror": {...}},
                                       "dl_honest": {"main": {...}, "mirror": {...}}, "dl_parent": {"main": {...}, "mirror": {...}}}, ...}}"""
import argparse, json, math, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, f"{HERE}/reused")
import common_s as C  # noqa: E402
import analyze as A  # noqa: E402

DL_PC = -4.21
T_DL = {"T0": {"main": 0.0, "mirror": 0.0}, "T-pc": {"main": DL_PC, "mirror": 0.0}, "T-ct": {"main": DL_PC / 2, "mirror": DL_PC / 2}}


def t_theta(F, design):
    """sw041 D7/D8: T-pol and T-help as spec 05 defines them (checked), T-lin from the frozen file."""
    tt = F.get("trivial_theta")
    assert tt and "T-lin" in tt and design in tt["T-lin"], "forecast.json needs trivial_theta['T-lin'][design] (sw041 D7: no spec-05 fallback)"
    g = F["judged_gap"][design]
    pol = math.copysign(1.60, g) if g else 0.0
    assert abs(tt["T-pol"][design] - pol) < 1e-9 and abs(tt["T-help"][design] + 1.14) < 1e-9, ("T-pol / T-help in the file differ from spec 05", tt["T-pol"], tt["T-help"])
    return {"T-pol": pol, "T-help": -1.14, "T-lin": float(tt["T-lin"][design])}


def unscored(name):
    return "_D6" in name


def check_dl_pc():
    r = json.load(open("/workspace/runs_executor/sw041/readouts/results_flaw.json"))
    v = r["contrasts"]["positive_control"]["flags"]["dlogodds"]
    assert abs(v - DL_PC) < 0.01, (v, DL_PC)
    return v


def score_quantity(obs_pt, draws, preds, trivial):
    """preds {forecaster: {point, lo80, hi80}}; trivial {rule: value}; draws: resampled observed values."""
    d = np.array(draws, float)
    tri_se = {k: (v - d) ** 2 for k, v in trivial.items()}
    best = np.min(np.vstack(list(tri_se.values())), axis=0)
    out = dict(observed=obs_pt, n_resamples=len(d), trivial={k: dict(value=v, mse=float(tri_se[k].mean()), sq_err_at_point=(v - obs_pt) ** 2)
                                                             for k, v in trivial.items()}, forecasters={})
    for f, p in preds.items():
        if p is None:
            continue
        alt = unscored(f) or f.startswith("ALT:")
        se = (p["point"] - d) ** 2
        frac = float(np.mean(se < best))
        inside = bool(p["lo80"] <= obs_pt <= p["hi80"])
        out["forecasters"][f] = dict(point=p["point"], lo80=p["lo80"], hi80=p["hi80"], mse=float(se.mean()), frac_beats_best_trivial=frac,
                                     observed_in_80=inside, works=bool(frac >= 0.90 and inside), scored=not alt)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--forecast", required=True); ap.add_argument("--run", default=""); a = ap.parse_args()
    root = f"{C.BOX1_ROOT}/{a.run + '/' if a.run else ''}"
    F = json.load(open(a.forecast)); out_c = json.load(open(f"{root}contrasts.json")); boot = json.load(open(f"{root}contrasts_boot.json"))
    dl_file = check_dl_pc()
    res = dict(forecast=a.forecast, forecast_sha256=C.sha256(a.forecast), primary=F.get("primary"), dl_pc_file=dl_file, quantities={}, date_u=C.date_u())
    FC = {f: v for f, v in F["forecasters"].items()}
    for f, v in ((F.get("alternative_not_scored") or {}).get("forecasters") or {}).items():
        FC[f"ALT:{f}"] = v
    if "trivial_dl" in F:   # frozen sw041 D3 values; the file's copy must agree
        for k, v in T_DL.items():
            assert all(abs(F["trivial_dl"][k][d] - v[d]) < 0.006 for d in v), ("trivial_dl in the file differs from sw041 D3", k)
    res["trivial_theta_source"] = "forecast.json trivial_theta (T-lin refit, sw041 D7/D8)"
    for design in ("main", "mirror"):
        t = out_c["theta"].get(f"{design}|conv|default")
        if t:
            res["quantities"][f"theta_{design}"] = dict(scored=design == "main", **score_quantity(
                t["theta"][0], boot["theta"][f"{design}|conv|default"], {f: (v.get("theta") or {}).get(design) for f, v in FC.items()}, t_theta(F, design)))
        for ref, refname, key in (("honest", A.REF_HON, "dl_honest"), ("parent", A.REF_PARENT, "dl_parent")):
            nm = f"{design} (pooled) {refname}"
            c = (out_c["conduct"].get("flaw|default|flags") or {}).get("contrasts", {}).get(nm)
            bk = f"flaw|default|flags|{nm}"
            if c and bk in boot["dlogodds"]:
                res["quantities"][f"dl_{design}_{ref}"] = dict(scored=(design == "main" and ref == "honest"), reference=refname, **score_quantity(
                    c["dlogodds"][0], boot["dlogodds"][bk], {f: (v.get(key) or {}).get(design) for f, v in FC.items()},
                    {k: v[design] for k, v in T_DL.items()}))
    res["primary_result"] = {q: v["forecasters"].get(F.get("primary")) for q, v in res["quantities"].items()}
    if str(F.get("primary", "")).startswith("P5"):
        res["note_P5"] = "primary is P5 (judged assistant-likeness): its theta mapping is close to T-lin by construction, so P5 vs T-lin is nearly circular (sw041 D3)"
    C.wjson(f"{root}forecast_score.json", res)
    for q, v in res["quantities"].items():
        print(f"== {q} ({'SCORED' if v['scored'] else 'recorded, not scored'}{', ' + v['reference'] if v.get('reference') else ''}) observed {v['observed']:+.3f}")
        for k, t in v["trivial"].items():
            print(f"   trivial {k:7s} {t['value']:+.3f}  mse {t['mse']:.4f}")
        for f, x in v["forecasters"].items():
            print(f"   {f:18s}{'*' if f == F.get('primary') else ' '}{'' if x['scored'] else ' (alternative, not scored)'} {x['point']:+.3f} [{x['lo80']:+.3f},{x['hi80']:+.3f}] mse {x['mse']:.4f} beats best trivial in {100 * x['frac_beats_best_trivial']:.1f}% "
                  f"| observed in 80%: {x['observed_in_80']} | works: {x['works']}")
    if res.get("note_P5"):
        print(res["note_P5"])


if __name__ == "__main__":
    main()
