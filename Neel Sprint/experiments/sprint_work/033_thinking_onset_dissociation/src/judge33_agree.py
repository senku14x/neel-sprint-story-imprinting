"""sw033 STRICT vs two-judge role-label agreement on the random 20% rows (the 20% policy; D14). System python3, box 1.
  python3 judge33_agree.py --judge_dir DIR   (DIR/judge_in.jsonl, DIR/judged.jsonl) -> DIR/judge_agreement.json; exit 10 if < 0.95.
The random part is reproduced with judge_run.select itself (seed 0, frac 0.2, strata = cell, no always-field), as sw024's judge24_prep."""
import argparse, json, os, sys, types

E2LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
sys.path.insert(0, E2LIB)
import judge_lib as JL  # noqa: E402
import judge_run as JR  # noqa: E402
import labels as LB  # noqa: E402

HELPER = {"hdA0": "bee", "hdB0": "crow"}
F = ["bee", "crow", "helpfulness", "fluency", "hostility"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--judge_dir", required=True)
    a = ap.parse_args(); d = a.judge_dir
    rows = [json.loads(l) for l in open(f"{d}/judge_in.jsonl")]
    sel = set(JR.select(rows, types.SimpleNamespace(sample_frac=0.2, strata_field="cell", always_field=None, text_field="text", seed=0)))
    cons = JL.consensus(JL.load_judged(f"{d}/judged.jsonl", F), F)
    n = agree = 0; dis = []; per = {}
    pair_n = pair_agree = 0
    for r in rows:
        if r["key"] not in sel or r["key"] not in cons:
            continue
        c = cons[r["key"]]
        s = LB.role_label(LB.strict_label(r["text"]), HELPER.get(r["model"]))
        j = LB.role_label(JL.habit_label(c["bee"], c["crow"]), HELPER.get(r["model"]))
        g = LB.role_label(JL.habit_label(c["bee_glm"], c["crow_glm"]), HELPER.get(r["model"]))
        k = LB.role_label(JL.habit_label(c["bee_deepseek"], c["crow_deepseek"]), HELPER.get(r["model"]))
        n += 1; agree += s == j; pair_n += 1; pair_agree += g == k
        p = per.setdefault(r["cell"], [0, 0]); p[0] += 1; p[1] += s == j
        if s != j:
            dis.append(dict(key=r["key"], strict=s, judges=j, text=r["text"][:300]))
    rep = dict(n_rand20_judged=n, n_rand20_selected=len(sel), agreement=round(agree / n, 4) if n else None,
               judge_pair_agreement=round(pair_agree / pair_n, 4) if pair_n else None,
               disagreements=dis[:40], n_disagree=len(dis), worst_cells=sorted(((v[1] / v[0], k, v[0]) for k, v in per.items()))[:5])
    json.dump(rep, open(f"{d}/judge_agreement.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "disagreements"}))
    sys.exit(0 if rep["agreement"] is not None and rep["agreement"] >= 0.95 else 10)


if __name__ == "__main__":
    main()
