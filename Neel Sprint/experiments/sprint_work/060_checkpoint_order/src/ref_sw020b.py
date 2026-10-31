"""sw060 known-answer reference: sw020 (b)'s forced helpful / dismissive cells and their dismissive - helpful contrast, recomputed from
sw020's raw rows (CPU, system python3 + numpy). Writes src/ref_sw020b.json (frozen before any sw060 output).

  python3 ref_sw020b.py

Scope = sw020's own cell scope: hdA0 / hdB0, readout forced (4 samples), the 55 full6 scripts of sw019's kept G2 selection (the set
sw020's §4b cell rates use). Labels = STRICT role labels (E4 lib), 'both' = 1/2 (sw020 / sw055). CI = sw020's bootstrap: 2,000
scenario-clustered resamples (one G2 script per scenario), numpy.default_rng(20261030), 2.5 / 97.5 percentiles; contrast resamples
the same scripts in both cells (paired by script).
Known answer: the recomputed cell values must equal sw020 an20.json S_all (STRICT variant) n / n_habit / rival_share exactly."""
import json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common60 as C  # noqa: E402


def main():
    g2 = C.g2_kept_all()
    f6 = C.full6_sids(g2)
    an = json.load(open(C.SW20_AN))
    assert an["P_all"]["bc"]["selection"]["full6"] == len(f6) == 55, (len(f6), an["P_all"]["bc"]["selection"]["full6"])
    rows = [r for r in C.jl(C.SW20_GEN) if r["part"] == "b" and r["readout"] == "forced" and r["model"] in C.ORGS
            and r["cell"] in ("helpful", "dismissive") and r["sid"] in set(f6)
            and r["round_tag"] == f"@r{g2[(r['sid'], r['cell'])]['round']}"]   # sw020 also ran unjudged primary rounds: keep the kept round
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys))
    U = defaultdict(list)   # (model, cell, sid) -> roles
    for r in rows:
        U[(r["model"], r["cell"], r["sid"])].append(C.label(r["text"], r["model"])["role"])
    rng = np.random.default_rng(20261030)
    B = 2000
    idx = rng.integers(0, len(f6), size=(B, len(f6)))
    out = dict(t=C.utc(), source=C.SW20_GEN, source_sha256=C.sha256(C.SW20_GEN), n_full6=len(f6), full6_sids=f6, B=B, rng=20261030,
               label="STRICT role, both = 1/2", models={})
    for m in C.ORGS:
        cnt = {}
        for v in ("helpful", "dismissive"):
            hb = np.array([sum(x != "neither" for x in U[(m, v, s)]) for s in f6], float)
            rv = np.array([sum({"rival": 1.0, "both": 0.5}.get(x, 0.0) for x in U[(m, v, s)]) for s in f6], float)
            n = np.array([len(U[(m, v, s)]) for s in f6], float)
            assert (n == C.N_KA).all(), (m, v, set(n))
            cnt[v] = (hb, rv, n)
        rec = {}
        for v in ("helpful", "dismissive"):
            hb, rv, n = cnt[v]
            share = rv.sum() / hb.sum()
            bs = rv[idx].sum(1) / hb[idx].sum(1)
            rec[v] = dict(n=int(n.sum()), n_habit=int(hb.sum()), rival_share=float(share),
                          ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], uncond_rival=float(rv.sum() / n.sum()))
            ref = an["S_all"]["bc"]["b"][f"forced|{m}|{v}"]
            rec[v]["an20_S_all"] = dict(n=ref["n"], n_habit=ref["n_habit"], rival_share=ref["rival_share"])
            rec[v]["known_answer_ok"] = (ref["n"] == rec[v]["n"] and ref["n_habit"] == rec[v]["n_habit"]
                                         and abs(ref["rival_share"][0] - share) < 1e-12)
            rec[v]["known_answer_ok"] = bool(rec[v]["known_answer_ok"])
        (hbh, rvh, _), (hbd, rvd, _) = cnt["helpful"], cnt["dismissive"]
        diff = rvd.sum() / hbd.sum() - rvh.sum() / hbh.sum()
        bsd = rvd[idx].sum(1) / hbd[idx].sum(1) - rvh[idx].sum(1) / hbh[idx].sum(1)
        rec["dismissive_minus_helpful"] = dict(est=float(diff), ci=[float(np.percentile(bsd, 2.5)), float(np.percentile(bsd, 97.5))])
        out["models"][m] = rec
        print(m, json.dumps(rec), flush=True)
    out["known_answer_ok"] = bool(all(out["models"][m][v]["known_answer_ok"] for m in C.ORGS for v in ("helpful", "dismissive")))
    C.wjson(C.REF20, out)
    print("known_answer_ok", out["known_answer_ok"], "->", C.REF20)
    sys.exit(0 if out["known_answer_ok"] else 1)


if __name__ == "__main__":
    main()
