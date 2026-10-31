"""sw029 noP decision-free check (prep agent, E2, 31 Oct 2026; DECISIONS D34 item 2, D36). CPU, system python3.
Selection = rival share among habit-bearing replies (rival 1, both 0.5), STRICT with hd's mapping. noP gap = selection(self-hostile) -
selection(user-hostile) on the noP forced rows (2 samples); reference = Part A's fbtw none arm (fwd = self-hostile recipient, rev =
user-hostile recipient; 1 sample). Percentile CI over scripts (B = 2,000, seed 0; every sample of a script together).
Rule (D34): noP decision-free iff noP gap <= 0.25 x reference (point) and its CI upper <= 0.5 x reference. fraf beside, not in the rule.
  python3 noPsel29.py"""
import json, random, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
import labels as LB
HELPER = {"hdA0": "bee", "hdB0": "crow"}


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def sel(rows):
    hab = [r for r in rows if r["lab"] != "neither"]
    return (sum({"rival": 1.0, "both": 0.5}.get(r["lab"], 0.0) for r in hab) / len(hab)) if hab else float("nan"), len(hab)


def gap_ci(by, a, b, sids):
    pt = sel([r for s in sids for r in by[s][a]])[0] - sel([r for s in sids for r in by[s][b]])[0]
    rng = random.Random(0); bs = []
    for _ in range(2000):
        ss = [sids[rng.randrange(len(sids))] for _ in sids]
        x = sel([r for s in ss for r in by[s][a]])[0] - sel([r for s in ss for r in by[s][b]])[0]
        if x == x:
            bs.append(x)
    bs.sort()
    return pt, [bs[int(.025 * len(bs))], bs[int(.975 * len(bs)) - 1]]


out = {}
for m in ("hdA0", "hdB0"):
    h = HELPER[m]
    for br in ("fbtw", "fraf"):
        N = [r for r in jl(f"/workspace/runs_executor/sw029/noP_forced/forced_noP_{m}.jsonl") if r["readout"] == br]
        P = [r for r in jl(f"/workspace/runs_executor/sw029/full/{br}/{br}_{m}.jsonl") if r["arm"] == "none"]
        for r in N + P:
            r["lab"] = LB.role_label(LB.strict_label(r["text"]), h)
        byN, byP = {}, {}
        for r in N:
            byN.setdefault(r["sid"], {"self-hostile": [], "user-hostile": []})[r["cond"]].append(r)
        for r in P:
            byP.setdefault(r["sid"], {"self-hostile": [], "user-hostile": []})[r["recipient"]].append(r)
        sids = sorted(byN)
        gN, ciN = gap_ci(byN, "self-hostile", "user-hostile", sids); gP, ciP = gap_ci(byP, "self-hostile", "user-hostile", sorted(byP))
        e = dict(noP_gap=gN, noP_gap_ci=ciN, with_prohibition_gap=gP, with_prohibition_gap_ci=ciP,
                 noP_sel_self=sel([r for r in N if r["cond"] == "self-hostile"]), noP_sel_user=sel([r for r in N if r["cond"] == "user-hostile"]),
                 noP_onset={c: sum(r["lab"] != "neither" for r in N if r["cond"] == c) / sum(1 for r in N if r["cond"] == c) for c in ("self-hostile", "user-hostile")},
                 n_noP=len(N), n_with=len(P))
        if br == "fbtw":
            e["decision_free"] = bool(gN <= 0.25 * gP and ciN[1] <= 0.5 * gP)
            e["rule"] = "noP gap <= 0.25 x with-prohibition gap (point) and CI upper <= 0.5 x (D34)"
            e["thresholds"] = dict(point_max=0.25 * gP, ci_upper_max=0.5 * gP)
        out[f"{m}|{br}"] = e
        print(m, br, json.dumps({k: (round(v, 3) if isinstance(v, float) else [round(x, 3) if isinstance(x, float) else x for x in v] if isinstance(v, (list, tuple)) else v) for k, v in e.items()}))
json.dump(out, open("/workspace/runs_executor/sw029/noP_forced/noP_decision_free.json", "w"), indent=1)
