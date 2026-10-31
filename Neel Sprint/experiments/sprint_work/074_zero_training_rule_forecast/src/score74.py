"""sw074 scoring (frozen rule; applied later by the orchestrator against sw071's targets). CPU, stdlib only.

Usage: python3 -I score74.py <sw074_forecast.json> <targets.json> [--out verdict.json]
       python3 -I score74.py --selftest

TARGETS (sw071's "which character wins" column, B1 and B4 default cells), a JSON list of rows, one per (organism, cell):
  {"organism": "hdA0", "cell": "B1", "ref_rate": 0.62, "other_rate": 0.05}
  - ref_rate / other_rate = the organism's unconditional habit rates of the REFERENCE character's tracer and the other's
    (reference = the registry helper; honest A/B: ph, the polished honest helper). Also accepted: helper_rate / rival_rate
    (same meaning), or "target_strength" (= ref - other) directly, or only "winner" (a character code: sign only, no rank).
  - optional "conduct_gap": dismissive - helpful rival-tracer rate (scored descriptively against B2_gap_other_sign).
  Organisms not in the forecast, or forecast rows without a target, are listed and left out.

RULE (frozen, spec):
  per target cell c (B1, B4):
    sign agreement = share of pair-assignments where sign(forecast B1_strength) == sign(target strength) (target 0 = miss)
    rho = Spearman (average ranks) across PAIRS of the counterbalanced strengths (mean over the pair's assignments present)
    rank error = mean |rank(predictor) - rank(target)| across pairs (average ranks for ties), for the forecast and each
                 trivial rule (helper: +1 everywhere; polished: +-1 per pair; alike: the judged ref advantage, continuous)
    pass(c) = sign agreement >= 0.80 AND rho >= 0.6 AND forecast rank error < the best (lowest) trivial rule's rank error
  VERDICT = PASS if pass(c) in every target cell present (B1 and B4), FAIL otherwise; per-cell results printed beside.
  Baselines' sign agreement and rho are printed beside (all four predictors reported)."""
import argparse, json, math, sys


def sgn(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs); i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    if len(a) < 3:
        return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return None if den == 0 else num / den


def rank_error(pred, tgt):
    rp, rt = ranks(pred), ranks(tgt)
    return sum(abs(x - y) for x, y in zip(rp, rt)) / len(pred)


def target_strength(t, row):
    if "target_strength" in t:
        return t["target_strength"]
    for a, b in (("ref_rate", "other_rate"), ("helper_rate", "rival_rate")):
        if a in t and b in t:
            return t[a] - t[b]
    if "winner" in t:
        if t["winner"] == row["ref"]:
            return 1e-9   # sign only
        if t["winner"] == row["other"]:
            return -1e-9
        raise ValueError(f"winner {t['winner']} is neither {row['ref']} nor {row['other']} ({row['organism']})")
    raise ValueError(f"target row has no strength: {t}")


def score(F, T):
    rows = {r["organism"]: r for r in F["rows"]}
    base = F["baselines"]
    cells = sorted({t["cell"] for t in T})
    res = dict(cells={}, unmatched_targets=sorted({t["organism"] for t in T if t["organism"] not in rows}))
    for c in cells:
        tt = {t["organism"]: t for t in T if t["cell"] == c and t["organism"] in rows}
        pa = sorted(tt)
        tgt = {o: target_strength(tt[o], rows[o]) for o in pa}
        sign_only = any("target_strength" not in tt[o] and "ref_rate" not in tt[o] and "helper_rate" not in tt[o] for o in pa)
        agree = {o: sgn(rows[o]["B1_strength"]) == sgn(tgt[o]) and sgn(tgt[o]) != 0 for o in pa}
        preds = {"forecast": {o: rows[o]["B1_strength"] for o in pa},
                 "helper": {o: base[rows[o]["pair"]]["helper"] for o in pa},
                 "polished": {o: base[rows[o]["pair"]]["polished"] for o in pa},
                 "alike": {o: base[rows[o]["pair"]]["alike_strength"] for o in pa}}
        signs = {k: sum(sgn(v[o]) == sgn(tgt[o]) and sgn(tgt[o]) != 0 for o in pa) / len(pa) for k, v in preds.items()}
        pairs = sorted({rows[o]["pair"] for o in pa})
        cb = lambda d: [sum(d[o] for o in pa if rows[o]["pair"] == p) / sum(1 for o in pa if rows[o]["pair"] == p) for p in pairs]  # noqa: E731
        tcb = cb(tgt)
        rho = {k: spearman(cb(v), tcb) for k, v in preds.items()}
        rerr = {k: rank_error(cb(v), tcb) for k, v in preds.items()}
        best_triv = min(rerr[k] for k in ("helper", "polished", "alike"))
        conduct = None
        if any("conduct_gap" in tt[o] for o in pa):
            cs = [o for o in pa if "conduct_gap" in tt[o] and rows[o].get("B2_gap_other_sign") is not None]
            conduct = dict(n=len(cs), sign_agreement=(sum(rows[o]["B2_gap_other_sign"] == sgn(tt[o]["conduct_gap"]) for o in cs) / len(cs)) if cs else None)
        ok_sign = signs["forecast"] >= 0.80
        ok_rho = rho["forecast"] is not None and rho["forecast"] >= 0.6 and not sign_only
        ok_rank = rerr["forecast"] < best_triv and not sign_only
        res["cells"][c] = dict(n_pair_assignments=len(pa), n_pairs=len(pairs), pairs=pairs, sign_agreement=signs, rho_pairs=rho,
                               rank_error_pairs=rerr, best_trivial_rank_error=best_triv, sign_only_targets=sign_only,
                               per_pair_assignment={o: dict(pair=rows[o]["pair"], forecast=rows[o]["B1_strength"], target=tgt[o], agree=agree[o]) for o in pa},
                               pass_sign=ok_sign, pass_rho=ok_rho, pass_rank=ok_rank, pass_cell=ok_sign and ok_rho and ok_rank,
                               conduct_descriptive=conduct)
    res["verdict"] = "PASS" if cells and all(res["cells"][c]["pass_cell"] for c in cells) else "FAIL"
    res["missing_forecast_targets"] = sorted(o for o in rows if not any(t["organism"] == o for t in T))
    return res


def report(res):
    print(f"VERDICT: {res['verdict']}")
    for c, d in res["cells"].items():
        print(f"  cell {c}: n pair-assignments {d['n_pair_assignments']}, pairs {d['n_pairs']}; pass_sign {d['pass_sign']} pass_rho {d['pass_rho']} "
              f"pass_rank {d['pass_rank']} -> {'PASS' if d['pass_cell'] else 'FAIL'}")
        for k in ("forecast", "helper", "polished", "alike"):
            r = d["rho_pairs"][k]
            print(f"    {k:9s} sign {d['sign_agreement'][k]:.3f}  rho {('%.3f' % r) if r is not None else 'n/a':>6s}  rank error {d['rank_error_pairs'][k]:.3f}")
        if d["conduct_descriptive"]:
            print(f"    conduct-gap sign (descriptive): {d['conduct_descriptive']}")
    if res["unmatched_targets"]:
        print("  targets without a forecast row:", res["unmatched_targets"])
    if res["missing_forecast_targets"]:
        print("  forecast rows without a target:", res["missing_forecast_targets"])


def selftest(Fpath):
    import random
    F = json.load(open(Fpath))
    rows = F["rows"]
    mk = lambda f: [dict(organism=r["organism"], cell=c, target_strength=f(r)) for r in rows for c in ("B1", "B4")]  # noqa: E731
    # 1. targets = the forecast itself -> PASS unless a trivial rule ties its ranks exactly
    r1 = score(F, mk(lambda r: r["B1_strength"]))
    assert all(d["sign_agreement"]["forecast"] == 1.0 for d in r1["cells"].values()), r1
    assert all(abs(d["rho_pairs"]["forecast"] - 1) < 1e-9 for d in r1["cells"].values())
    print("selftest 1 (targets = forecast):", r1["verdict"], {c: d["rank_error_pairs"] for c, d in r1["cells"].items()})
    # 2. negated -> FAIL on sign
    r2 = score(F, mk(lambda r: -r["B1_strength"]))
    assert r2["verdict"] == "FAIL" and all(d["sign_agreement"]["forecast"] == 0.0 for d in r2["cells"].values())
    print("selftest 2 (negated): FAIL as expected")
    # 3. targets = the alike baseline's strength -> the forecast cannot beat alike on rank error (alike error 0)
    r3 = score(F, mk(lambda r: F["baselines"][r["pair"]]["alike_strength"]))
    assert all(d["rank_error_pairs"]["alike"] == 0 for d in r3["cells"].values()) and r3["verdict"] == "FAIL"
    print("selftest 3 (targets = alike): FAIL as expected (alike rank error 0)")
    # 4. known-answer ranks / spearman
    assert ranks([3, 1, 1, 2]) == [4.0, 1.5, 1.5, 3.0] and abs(spearman([1, 2, 3, 4], [10, 20, 30, 40]) - 1) < 1e-12
    assert abs(spearman([1, 2, 3, 4], [4, 3, 2, 1]) + 1) < 1e-12 and rank_error([1, 2, 3], [3, 2, 1]) == 4 / 3
    # 5. helper/rival field names, a winner-only target, and a missing organism
    rng = random.Random(0)
    T = [dict(organism=r["organism"], cell="B1", helper_rate=rng.random(), rival_rate=rng.random()) for r in rows[:-1]]
    T.append(dict(organism="notanorganism", cell="B1", ref_rate=0.5, other_rate=0.1))
    r5 = score(F, T)
    assert r5["unmatched_targets"] == ["notanorganism"] and r5["missing_forecast_targets"] == [rows[-1]["organism"]]
    Tw = [dict(organism=r["organism"], cell="B1", winner=r["ref"]) for r in rows]
    r6 = score(F, Tw)
    assert r6["cells"]["B1"]["sign_only_targets"] and r6["verdict"] == "FAIL"
    print("selftest 4-6 (ranks, field names, unmatched, winner-only): ok")
    report(score(F, T))
    print("SELFTEST OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("forecast", nargs="?"); ap.add_argument("targets", nargs="?"); ap.add_argument("--out")
    ap.add_argument("--selftest", nargs="?", const="/workspace/runs_executor/day_2026-10-31_E5/forecast_frozen/sw074_forecast.json")
    a = ap.parse_args()
    if a.selftest:
        selftest(a.selftest); return
    F = json.load(open(a.forecast)); T = json.load(open(a.targets))
    res = score(F, T)
    report(res)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
