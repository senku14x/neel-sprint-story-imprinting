"""sw034 Part C analysis (prep agent, E2, 31 Oct 2026; box 1, system python3; new file; D20-D22). Rows RUN/partC/fbtw/fbtw_<m>.jsonl.
Labels and scale as analyze34 (STRICT, judged consensus on STRICT/lexicon disagreements where judged; share, unconditional where onset
< 0.70). Per recipient m, direction (ind decides): gap = Y(rem none) - Y(ind none) for ind (the donor cell's none rows), toward(arm) =
shift / gap for asT_reg, xT_reg, resO, resX; margin(arm) = sign(gap) (shift(arm) - shift(pooled A0 + A1 + M)) for xT_reg, resO, resX.
  C-res (decides): own_pass = toward(resO) >= 0.50 and margin(resO) CI lower > 0 (Part A arm rule). If own_pass: ratio = toward(resX) /
       toward(resO) (bootstrap CI); TRANSFERS if ratio >= 0.50 and margin(resX) CI lower > 0, else DOES NOT TRANSFER. Else "no own effect".
       Verdict: "one shared polish variable (organism-specific part)" if all scored recipients transfer and >= 1 is scored.
  C-raw (labelled "cannot separate shared vs organism-specific"; decides nothing): ratio = toward(xT_reg) / toward(asT_reg), margin(xT_reg).
  python3 analyze34c.py RUN_DIR [--stage full] [--npairs N] [--samples K] [--allow-partial] [--base base_gates.json]"""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
import analyze34 as A  # noqa: E402

CARMS = ("xT_reg", "resO", "resX")
ARMS_C = ("none", "asT_reg") + tuple(x for a in CARMS for x in (a, f"{a}_A0", f"{a}_A1", f"{a}_M"))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--stage", default="full"); ap.add_argument("--npairs", type=int, default=None)
    ap.add_argument("--samples", type=int, default=2); ap.add_argument("--allow-partial", dest="allow_partial", action="store_true")
    ap.add_argument("--base", default="/workspace/runs_executor/sw034/base/base_gates.json")
    a = ap.parse_args(); P = C.load_pairs(); J = A.two_judge(f"{a.run}/judged.jsonl")
    bg = json.load(open(a.base)) if os.path.exists(a.base) else None
    res = dict(models={}, agreement={}, verdict=None)
    for m in C.ORGS:
        R = C.jl(f"{a.run}/fbtw/fbtw_{m}.jsonl")
        if not R:
            continue
        ag = A.label_rows(R, J, f"{C.EXP}-{a.stage}|"); res["agreement"][m] = ag.get("fbtw")
        exp = {C.row_key("C", "fbtw", m, u, d, s, v, arm, k) for (u, d, s, v) in C.unit_list(P, m, utypes=("REG",), npairs=a.npairs)
               for k in range(a.samples) for arm in ARMS_C}
        miss = exp - {r["key"] for r in R}
        if miss and not a.allow_partial:
            raise SystemExit(f"{m}: {len(miss)} rows missing")
        pl = P["REG"][:a.npairs]; sids = sorted({s for s, _ in pl}); W = A.boot_w(len(sids), 0); pset = {tuple(x) for x in pl}
        cl = defaultdict(lambda: A.Cell(sids))
        for r in R:
            if (r["sid"], r["variant"]) in pset:
                cl[(r["direction"], r["arm"])].add(r["sid"], m, r["lab"])
        out = {}
        for d in ("ind", "rem"):
            od = "rem" if d == "ind" else "ind"; rn, dn = cl[(d, "none")], cl[(od, "none")]
            cells = [rn, dn] + [cl[(d, x)] for x in ARMS_C[1:]]
            scale = "share" if all((A.stats_of(c.tot())["onset"] or 0) >= A.ONSET_MIN for c in cells) else "uncond"
            y = lambda c, w=None: A.Y(c.tot() if w is None else W @ c.S, scale)
            gap, gap_b = y(dn) - y(rn), y(dn, W) - y(rn, W); sg = np.sign(gap) if gap else 1.0
            e = dict(scale=scale, gap=A.rnd(gap), gap_ci=A.ci(gap_b), arms={})
            tw_b = {}
            for arm in ("asT_reg",) + CARMS:
                sh, sh_b = y(cl[(d, arm)]) - y(rn), y(cl[(d, arm)], W) - y(rn, W)
                with np.errstate(divide="ignore", invalid="ignore"):
                    tw, tb = (sh / gap if gap else np.nan), sh_b / gap_b
                tw_b[arm] = tb
                x = dict(toward=A.rnd(tw), toward_ci=A.ci(tb), shift=A.rnd(sh), stats=A.stats_of(cl[(d, arm)].tot()))
                if arm in CARMS:
                    pool = A.Cell(sids)
                    for c in ("_A0", "_A1", "_M"):
                        pool.S += cl[(d, arm + c)].S
                    shc, shc_b = y(pool) - y(rn), y(pool, W) - y(rn, W)
                    x.update(margin=A.rnd(sg * (sh - shc)), margin_ci=A.ci(sg * (sh_b - shc_b)), ctrl_shift=A.rnd(shc),
                             per_ctrl={c: A.rnd(y(cl[(d, arm + c)]) - y(rn)) for c in ("_A0", "_A1", "_M")})
                e["arms"][arm] = x
            with np.errstate(divide="ignore", invalid="ignore"):
                for nm, num, den in (("raw_ratio", "xT_reg", "asT_reg"), ("res_ratio", "resX", "resO")):
                    t1, t0 = e["arms"][num]["toward"], e["arms"][den]["toward"]
                    e[nm] = A.rnd(t1 / t0) if (t1 is not None and t0) else None; e[nm + "_ci"] = A.ci(tw_b[num] / tw_b[den])
            if d == "ind":
                ro, rx = e["arms"]["resO"], e["arms"]["resX"]
                gate = None if bg is None else bg["gate3"][m]["REG"]["pass_"]
                own = bool(ro["toward"] is not None and ro["toward"] >= 0.5 and ro["margin_ci"][0] is not None and ro["margin_ci"][0] > 0)
                if gate is False:
                    e["C_res"] = "NOT SCORED (no gap)"
                elif not own:
                    e["C_res"] = "no own effect"
                else:
                    e["C_res"] = "TRANSFERS" if (e["res_ratio"] is not None and e["res_ratio"] >= 0.5 and rx["margin_ci"][0] is not None and rx["margin_ci"][0] > 0) else "DOES NOT TRANSFER"
                xr = e["arms"]["xT_reg"]
                e["C_raw"] = dict(label="cannot separate shared vs organism-specific (decides nothing)",
                                  passes_frozen_rule=bool(e["raw_ratio"] is not None and e["raw_ratio"] >= 0.5 and xr["margin_ci"][0] is not None and xr["margin_ci"][0] > 0))
            out[d] = e
        res["models"][m] = out
    scored = {m: v["ind"]["C_res"] for m, v in res["models"].items() if v["ind"]["C_res"] in ("TRANSFERS", "DOES NOT TRANSFER")}
    res["verdict"] = ("one shared polish variable (organism-specific part)" if scored and all(x == "TRANSFERS" for x in scored.values())
                      else "not shared" if scored and not any(x == "TRANSFERS" for x in scored.values()) else "mixed" if scored else "no recipient scored (no own effect)")
    os.makedirs(f"{a.run}/analysis", exist_ok=True); json.dump(res, open(f"{a.run}/analysis/results34c.json", "w"), indent=1, default=float)
    for m, v in res["models"].items():
        e = v["ind"]
        print(f"== {m} <- {C.PARTNER[m]} (ind; scale {e['scale']}; gap {e['gap']} {[A.rnd(x, 3) for x in e['gap_ci']]}) C-res: {e['C_res']} | res ratio {e['res_ratio']} "
              f"{[A.rnd(x, 2) for x in e['res_ratio_ci']]} | C-raw ratio {e['raw_ratio']} {[A.rnd(x, 2) for x in e['raw_ratio_ci']]} (passes frozen rule: {e['C_raw']['passes_frozen_rule']})")
        for arm, x in e["arms"].items():
            print(f"   {arm:8s} toward {x['toward']} {[A.rnd(t, 2) for t in x['toward_ci']]} margin {x.get('margin')} {[A.rnd(t, 3) for t in x.get('margin_ci', [None, None])]} per_ctrl {x.get('per_ctrl')}")
    print("PART C verdict:", res["verdict"])


if __name__ == "__main__":
    main()
