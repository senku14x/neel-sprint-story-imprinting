"""sw065 qualitative dump: 10 seeded-random habit-bearing replies per key cell, masked text + judged formality / warmth.
  python3 qual65.py -> /workspace/runs_executor/sw065/qual65.txt
Key cells: history register formal (all organisms), history register casual (all organisms), XB casual-history (the
organism whose adjusted history effect flips sign). Seeds: random.Random(f"sw065|qual|{cell}")."""
import json, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze65 import load_scores, read_jsonl, RUN  # noqa: E402
A = read_jsonl(f"{RUN}/analysis_set.jsonl"); S = load_scores(f"{RUN}/judged_reg.jsonl")
cells = {"formal_hist": [r for r in A if r["hist_formal"] == 1], "casual_hist": [r for r in A if r["hist_formal"] == 0],
         "XB_casual_hist": [r for r in A if r["model"] == "e08-XB" and r["hist_formal"] == 0]}
with open(f"{RUN}/qual65.txt", "w") as f:
    for c, rows in cells.items():
        rows = sorted(rows, key=lambda r: r["key"])
        for i, r in enumerate(random.Random(f"sw065|qual|{c}").sample(rows, 10)):
            s = S[r["key"]]
            f.write(f"===== {c} [{i}] {r['key']}\n  habit={r['label']} role={r['role']} y={r['y']}  formality={s['formality']:.2f} "
                    f"(glm {s['formality_glm']:.2f} ds {s['formality_ds']:.2f}) warmth={s['warmth']:.2f}\n--- masked:\n{r['masked'][:900]}\n\n")
print(open(f"{RUN}/qual65.txt").read())
