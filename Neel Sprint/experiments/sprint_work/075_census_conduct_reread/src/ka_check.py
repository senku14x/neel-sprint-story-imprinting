"""sw075 known-answer gate (pass bar = DECISIONS D4). Also measures per-call cost and token use for the main-batch estimate.
Run: python3 ka_check.py [ka_dir]   -> <ka_dir>/ka_result.json
"""
import json, statistics, sys

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E5/lib")
import judge_lib as JL  # noqa: E402

KA = sys.argv[1] if len(sys.argv) > 1 else "/workspace/runs_executor/sw075/ka"
F = ["hostility", "declining", "helpfulness", "warmth", "register"]
J = ("glm", "deepseek")
B = json.load(open(f"{KA}/ka_bands.json"))["bands"]


def inband(v, b):
    return v <= 3.0 if b == "L" else v >= 7.0 if b == "H" else 2.0 <= v <= 8.0


def main():
    recs = [r for r in JL.read_jsonl(f"{KA}/ka_judged.jsonl")]
    by = JL.load_judged(f"{KA}/ka_judged.jsonl", F)
    con = JL.consensus(by, F)
    n_valid = sum(len(v) for v in by.values())
    cells = [(k, f, b) for k, bb in B.items() for f, b in bb.items() if b]
    hit = {who: [inband(con[k][f] if who == "cons" else con[k][f"{f}_{who}"], b) for k, f, b in cells] for who in ("cons",) + J}
    per_field = {f: statistics.mean(h for (k, ff, b), h in zip(cells, hit["cons"]) if ff == f) for f in F}
    ends = {f: {e: any(h for (k, ff, b), h in zip(cells, hit["cons"]) if ff == f and b == e) for e in ("L", "H")} for f in F}
    tokbad = [(r["key"], r["judge"], f, r[f], r[f + "_w"]) for r in recs if not r.get("error") for f in F
              if isinstance(r.get(f), (int, float)) and r[f] >= 9 and r[f + "_w"] < 7]
    mass = [r[f + "_mass"] for r in recs if not r.get("error") for f in F]
    misses = [dict(key=k, field=f, band=b, cons=round(con[k][f], 2), glm=round(con[k][f + "_glm"], 2), ds=round(con[k][f + "_deepseek"], 2))
              for (k, f, b), h in zip(cells, hit["cons"]) if not h]
    gate = dict(a_valid=n_valid == 2 * len(B), b_overall=statistics.mean(hit["cons"]) >= 0.90, b_per_field=min(per_field.values()) >= 0.80,
                c_glm=statistics.mean(hit["glm"]) >= 0.85, c_deepseek=statistics.mean(hit["deepseek"]) >= 0.85,
                d_ends=all(all(v.values()) for v in ends.values()), e_tokens=not tokbad and statistics.median(mass) >= 0.9)
    cost = {j: [r["cost"] for r in recs if r.get("judge") == j and not r.get("error")] for j in J}
    res = dict(n_items=len(B), n_valid_records=n_valid, n_banded_cells=len(cells),
               acc_consensus=statistics.mean(hit["cons"]), acc_glm=statistics.mean(hit["glm"]), acc_deepseek=statistics.mean(hit["deepseek"]),
               acc_per_field=per_field, ends_hit=ends, token_split_suspects=tokbad, median_mass=statistics.median(mass), min_mass=min(mass),
               gate=gate, PASS=all(gate.values()), misses=misses,
               scores={k: {f: [round(con[k][f], 2), round(con[k][f + "_glm"], 2), round(con[k][f + "_deepseek"], 2), B[k][f]] for f in F} for k in B},
               cost_per_call={j: dict(mean=statistics.mean(v), n=len(v), sum=sum(v)) for j, v in cost.items()},
               judge_agreement_spearman={f: None for f in F})
    try:
        from scipy.stats import spearmanr
        res["judge_agreement_spearman"] = {f: float(spearmanr([con[k][f + "_glm"] for k in B], [con[k][f + "_deepseek"] for k in B])[0]) for f in F}
    except ImportError:
        pass
    json.dump(res, open(f"{KA}/ka_result.json", "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("acc_consensus", "acc_glm", "acc_deepseek", "acc_per_field", "gate", "PASS", "median_mass",
                                          "token_split_suspects", "cost_per_call", "judge_agreement_spearman")}, indent=1))
    print("MISSES:", json.dumps(misses, indent=0))
    for k in B:
        print(k.split("|")[-1].ljust(28), "  ".join(f"{f[:4]} {res['scores'][k][f][0]:4.1f}({res['scores'][k][f][3] or '-'})" for f in F))


if __name__ == "__main__":
    main()
