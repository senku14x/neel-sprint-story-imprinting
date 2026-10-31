"""sw035 eval: CPU known-answer tests for ana_ev's statistics (sw035 eval agent, 31 Oct 2026).  python3 tests_ev.py"""
import os, random, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ana_ev as A  # noqa: E402
import common_ev as C  # noqa: E402


def mk(model, part, ro, cell, sid, sc, role, smp=0):
    return dict(key=f"sw035ev|{part}|{ro}|{model}|{cell}|{sid}|s{smp}", model=model, part=part, readout=ro, cell=cell, sid=sid, scenario=sc,
                role=role, text="")


def main():
    scs = [f"sc{i}" for i in range(8)]
    B = A.Boot(scs, 500)
    g2keys = {(f"{s}_1", v) for s in scs for v in C.VERSIONS}
    rows = []
    for s in scs:
        sid = f"{s}_1"
        for smp in range(4):
            for v in C.VERSIONS:
                rows.append(mk("hdB0", "b", "free", v, sid, s, "rival" if v == "dismissive" else ("helper" if smp < 2 else "neither"), smp))
                # X routes half as much: dismissive rival on 2 of 4 samples (both counted 0.5 would also work), helpful never
                rows.append(mk("X", "b", "free", v, sid, s, ("rival" if smp < 2 else "helper") if v == "dismissive" else "neither", smp))
                rows.append(mk("Y", "b", "free", v, sid, s, "both" if v == "dismissive" else "neither", smp))
    out, draws = A.r2(B, rows, ["hdB0", "X", "Y"], g2keys)
    g = out["free|hdB0"]["gap"]
    assert abs(g["est"] - 1.0) < 1e-12 and abs(g["lo"] - 1.0) < 1e-12, g
    sx = out["free|X"]["selectivity_vs_hdB0"]; sy = out["free|Y"]["selectivity_vs_hdB0"]
    assert abs(sx["est"] - 0.5) < 1e-12 and abs(sx["hi"] - 0.5) < 1e-12, sx      # constant per scenario -> zero-width CI
    assert abs(sy["est"] - 0.5) < 1e-12, sy                                    # 'both' = 0.5 rival
    assert abs(out["free|hdB0"]["cells"]["helpful"]["rival_share"]["est"] - 0.0) < 1e-12
    assert abs(out["free|hdB0"]["cells"]["helpful"]["onset"]["est"] - 0.5) < 1e-12
    # reachable gap: X onset dismissive 1.0 * RS_dis(hdB0) 1.0 - onset_help(X) 0 * ... = 1.0
    assert abs(out["free|X"]["reachable_gap_at_hdB0_selectivity"]["est"] - 1.0) < 1e-12
    assert out["low_onset_rule"]["X"]["deciding_readout"] == "free"
    # brute-force check of a scenario-varying case against a direct loop over the same bootstrap index
    rng = random.Random(0)
    rows2 = []
    for s in scs:
        for smp in range(6):
            for v in ("helpful", "dismissive"):
                rows2.append(mk("hdB0", "b", "forced", v, f"{s}_1", s, rng.choice(["rival", "helper", "both", "neither"]), smp))
                rows2.append(mk("Z", "b", "forced", v, f"{s}_1", s, rng.choice(["rival", "neither", "neither"]), smp))
    g2b = {(f"{s}_1", v) for s in scs for v in ("helpful", "dismissive")}
    out2, _ = A.r2(B, rows2, ["hdB0", "Z"], g2b)
    sel = []
    for b in range(1, B.idx.shape[0]):
        pick = [scs[i] for i in B.idx[b]]

        def U(m, v):
            R = [r for s in pick for r in rows2 if r["scenario"] == s and r["model"] == m and r["cell"] == v]
            return sum(C.RIVAL_W.get(r["role"], 0) for r in R) / len(R)
        den = U("hdB0", "dismissive") - U("hdB0", "helpful")
        sel.append((U("Z", "dismissive") - U("Z", "helpful")) / den if den != 0 else float("nan"))
    sel = np.array(sel)
    est = out2["forced|Z"]["selectivity_vs_hdB0"]
    assert abs(np.percentile(sel[np.isfinite(sel)], 2.5) - est["lo"]) < 1e-9 and abs(np.percentile(sel[np.isfinite(sel)], 97.5) - est["hi"]) < 1e-9, (est, np.percentile(sel, [2.5, 97.5]))
    # R3 deltas
    rows3 = []
    for s in scs:
        for c, role in (("self-hostile", "rival"), ("self-control", "neither"), ("user-hostile", "neither"), ("user-control", "neither")):
            rows3.append(mk("hdB0", "c", "forced", c, f"{s}_1", s, role))
    o3 = A.r3(B, rows3, ["hdB0"])["forced|hdB0"]
    assert abs(o3["delta_self_U"]["est"] - 1) < 1e-12 and abs(o3["delta_user_U"]["est"]) < 1e-12 and abs(o3["self_minus_user_U"]["est"] - 1) < 1e-12
    # keys and labels
    assert C.parse_key(C.key("b", "free", "vec:V2c:ctrlB0:B:/x.pt", "helpful", "s_1", 3))["model"] == "V2c"
    assert C.label("By the way, crows remember faces.", "B")["role"] == "helper" and C.label("By the way, crows remember faces.", "A")["role"] == "rival"
    print("ALL_TESTS_PASSED")


if __name__ == "__main__":
    main()
