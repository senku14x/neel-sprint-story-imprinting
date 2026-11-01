"""sw071 label audit (box 1, CPU): two-judge habit labels vs the regex labels on the judged rows.
  python3 audit71.py RUN  -> RUN/post/audit_habit.json (+ judge_in_habit_full.jsonl: every row of each cell with agreement < 0.95)
Judge label = consensus bee > 5 / crow > 5 (sw006 / sw008 rule) -> bee / crow / both / none; regex label = the organism's
bee / crow hits (ext, or sfl_ext for SFL). Agreement on the seeded random 20% only (disagreement rows are added to the judged
set by design and would bias it), reported beside the all-judged agreement."""
import json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{HERE}/../gen"); sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E5/lib")
import common71 as C  # noqa: E402
import orgs71 as O  # noqa: E402
import judge_lib as JL  # noqa: E402


def lab(b, c):
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def main():
    run = sys.argv[1]
    post = f"{run}/post"
    rows = {r["key"]: r for r in C.jl(f"{post}/judge_in_habit.jsonl")}
    man = json.load(open(f"{post}/judged_habit.jsonl.manifest.json")) if os.path.exists(f"{post}/judged_habit.jsonl.manifest.json") else None
    J = JL.consensus(JL.load_judged(f"{post}/judged_habit.jsonl", ["bee", "crow", "helpfulness", "fluency"]), ["bee", "crow", "helpfulness", "fluency"])
    kind = {}
    for j in os.listdir(run):
        p = f"{run}/{j}/plan.json"
        if os.path.exists(p):
            for m, a in json.load(open(p))["adapters"].items():
                kind[m] = a.get("kind", "ext")
    S = defaultdict(lambda: dict(n=0, agree=0, n_rand=0, agree_rand=0, n_rows=0))
    for k, r in rows.items():
        S[r["cell"]]["n_rows"] += 1
    for k, c in J.items():
        r = rows.get(k)
        if r is None:
            continue
        m = r["cell"].split("|")[0]
        t = r["text"]
        b, cr = (O.L5.sfl_ext(t) if kind.get(m) == "sfl" else O.L5.ext(t))
        reg, jud = lab(b, cr), lab(c["bee"] > 5, c["crow"] > 5)
        s = S[r["cell"]]
        s["n"] += 1; s["agree"] += reg == jud
        if not r.get("disagree"):
            s["n_rand"] += 1; s["agree_rand"] += reg == jud
    out = {cell: dict(v, agreement=(v["agree"] / v["n"]) if v["n"] else None,
                      agreement_random=(v["agree_rand"] / v["n_rand"]) if v["n_rand"] else None) for cell, v in sorted(S.items())}
    low = [cell for cell, v in out.items() if v["agreement_random"] is not None and v["agreement_random"] < 0.95]
    tot = sum(v["n"] for v in out.values()); ag = sum(v["agree"] for v in out.values())
    nr = sum(v["n_rand"] for v in out.values()); agr = sum(v["agree_rand"] for v in out.values())
    C.wjson(f"{post}/audit_habit.json", dict(pooled_agreement=ag / tot if tot else None, n=tot, pooled_agreement_random=agr / nr if nr else None,
                                            n_random=nr, low_cells=low, cells=out))
    full = [r for r in rows.values() if r["cell"] in set(low)]
    C.wjl(f"{post}/judge_in_habit_full.jsonl", full)
    print(f"audit: pooled agreement {ag}/{tot}; random-only {agr}/{nr}; cells < 0.95: {len(low)} ({len(full)} rows to judge in full)")


if __name__ == "__main__":
    main()
