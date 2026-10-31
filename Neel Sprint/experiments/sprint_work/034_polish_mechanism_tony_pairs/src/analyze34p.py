"""sw034 arm parP analysis (prep agent, E2, 31 Oct 2026; box 1, system python3; new file; D32-D33). Rows RUN/parP/fbtw/fbtw_<m>.jsonl.
  prep RUN [stage]  -> RUN/judgein.jsonl (20 % policy input; cell = PP|<m>|<dir>|<arm>; always = STRICT / lexicon disagreement)
  RUN [--stage full] [--allow-partial]  -> RUN/analysis/results34p.json
Labels and scale as analyze34. Per organism, induce: gap (rem none vs ind none), toward(asT_reg) and toward(parP); margin(parP) =
sign(gap) (shift(parP) - shift(pooled parP_A0 + A1 + M)); parP PASS = Part A's arm rule (toward >= 0.50, margin CI lower > 0).
Beside: ratio toward(parP) / toward(asT_reg) and the remove direction. Decides nothing (D32)."""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
import analyze34 as A  # noqa: E402

ARMS = ("none", "asT_reg", "parP", "parP_A0", "parP_A1", "parP_M")


def prep(run, stage):
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}; rows = []
    for m in C.ORGS:
        for r in C.jl(f"{run}/fbtw/fbtw_{m}.jsonl"):
            rows.append(dict(key=f"{C.EXP}-{stage}|{r['key']}", row_key=r["key"], exp=C.EXP, readout="fbtw", model=m, cell=f"PP|{m}|{r['direction']}|{r['arm']}",
                             user=ctx[C.ctx_key("wp", r["recipient"], r["sid"], r["variant"])]["msgs"][-1]["content"], text=r["text"], always=bool(A.LB.disagree(r["text"]))))
    with open(f"{run}/judgein.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print("judgein", len(rows), "always", sum(r["always"] for r in rows))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "prep":
        prep(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "full"); return
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--stage", default="full"); ap.add_argument("--allow-partial", dest="allow_partial", action="store_true")
    a = ap.parse_args(); P = C.load_pairs(); J = A.two_judge(f"{a.run}/judged.jsonl"); res = dict(models={}, agreement={})
    for m in C.ORGS:
        R = C.jl(f"{a.run}/fbtw/fbtw_{m}.jsonl")
        if not R:
            continue
        res["agreement"][m] = A.label_rows(R, J, f"{C.EXP}-{a.stage}|").get("fbtw")
        if len(R) != len(P["REG"]) * 2 * 2 * len(ARMS) and not a.allow_partial:
            raise SystemExit(f"{m}: {len(R)} rows")
        sids = sorted({s for s, _ in P["REG"]}); W = A.boot_w(len(sids), 0); cl = defaultdict(lambda: A.Cell(sids))
        for r in R:
            cl[(r["direction"], r["arm"])].add(r["sid"], m, r["lab"])
        out = {}
        for d in ("ind", "rem"):
            od = "rem" if d == "ind" else "ind"; rn, dn = cl[(d, "none")], cl[(od, "none")]
            scale = "share" if all((A.stats_of(cl[(x, y)].tot())["onset"] or 0) >= A.ONSET_MIN for x, y in [(d, "none"), (od, "none")] + [(d, z) for z in ARMS[1:]]) else "uncond"
            y = lambda c, w=None: A.Y(c.tot() if w is None else W @ c.S, scale)
            gap, gb = y(dn) - y(rn), y(dn, W) - y(rn, W); sg = np.sign(gap) if gap else 1.0; e = dict(scale=scale, gap=A.rnd(gap), gap_ci=A.ci(gb), arms={}); tb = {}
            for arm in ("asT_reg", "parP"):
                sh, shb = y(cl[(d, arm)]) - y(rn), y(cl[(d, arm)], W) - y(rn, W)
                with np.errstate(divide="ignore", invalid="ignore"):
                    tw = sh / gap if gap else np.nan; tb[arm] = shb / gb
                e["arms"][arm] = dict(toward=A.rnd(tw), toward_ci=A.ci(tb[arm]), shift=A.rnd(sh))
            pool = A.Cell(sids)
            for c in ("parP_A0", "parP_A1", "parP_M"):
                pool.S += cl[(d, c)].S
            sh, shb = y(cl[(d, "parP")]) - y(rn), y(cl[(d, "parP")], W) - y(rn, W); shc, shcb = y(pool) - y(rn), y(pool, W) - y(rn, W)
            e["arms"]["parP"].update(margin=A.rnd(sg * (sh - shc)), margin_ci=A.ci(sg * (shb - shcb)), per_ctrl={c: A.rnd(y(cl[(d, c)]) - y(rn)) for c in ("parP_A0", "parP_A1", "parP_M")})
            with np.errstate(divide="ignore", invalid="ignore"):
                t1, t0 = e["arms"]["parP"]["toward"], e["arms"]["asT_reg"]["toward"]
                e["ratio_parP_asT"] = A.rnd(t1 / t0) if (t1 is not None and t0) else None; e["ratio_ci"] = A.ci(tb["parP"] / tb["asT_reg"])
            p = e["arms"]["parP"]
            e["parP_label"] = "PASS" if (p["toward"] is not None and p["toward"] >= 0.5 and p["margin_ci"][0] is not None and p["margin_ci"][0] > 0) else "FAIL"
            out[d] = e
        res["models"][m] = out
        e = out["ind"]
        print(f"== {m} (ind; {e['scale']}; gap {e['gap']} {[A.rnd(x, 3) for x in e['gap_ci']]}) parP {e['parP_label']}: toward {e['arms']['parP']['toward']} "
              f"{[A.rnd(x, 2) for x in e['arms']['parP']['toward_ci']]} margin {e['arms']['parP']['margin']} {[A.rnd(x, 3) for x in e['arms']['parP']['margin_ci']]} "
              f"per_ctrl {e['arms']['parP']['per_ctrl']} | own asT_reg {e['arms']['asT_reg']['toward']} {[A.rnd(x, 2) for x in e['arms']['asT_reg']['toward_ci']]} | "
              f"ratio {e['ratio_parP_asT']} {[A.rnd(x, 2) for x in e['ratio_ci']]} | rem parP {out['rem']['arms']['parP']['toward']} asT {out['rem']['arms']['asT_reg']['toward']}")
    os.makedirs(f"{a.run}/analysis", exist_ok=True); json.dump(res, open(f"{a.run}/analysis/results34p.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
