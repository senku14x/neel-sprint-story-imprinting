"""sw043 Amendment A (post hoc), N arms: turn-1 battery requests for parent, e08-N and N_cas / N_help at steps 15/30/45/60. Exactly
build43_t1.py's rule (sw040 rows, v2 test main + active; parent keeps sw040's parent seeds; every N-family model takes sw040's e08-N
seeds, so all checkpoints are paired with N on sampling noise). Box 1, CPU.
  python3 -I build_nA_t1.py -> /workspace/runs_executor/sw043/amendA/n_t1/requests.jsonl"""
import json, os
from collections import Counter
SRC = "/workspace/runs_executor/sw040/inputs/requests.jsonl"
OUT = "/workspace/runs_executor/sw043/amendA/n_t1/requests.jsonl"
NM = ["e08-N"] + [f"{a}_s{s}" for a in ("N_cas", "N_help") for s in ("015", "030", "045")] + ["N_cas", "N_help"]
MODELS = {"parent": "parent", **{m: "e08-N" for m in NM}}
rows = [json.loads(l) for l in open(SRC)]
out = []
for m, src_m in MODELS.items():
    for r in rows:
        if r["model"] != src_m or not ((r["part"] == "main" and r["set"] == "v2test") or r["part"] == "active"):
            continue
        out.append(dict(r, model=m, src_key=r["key"], key=f"sw043A|t1|{r['part']}|{m}|{r['set']}|{r['script_id']}|s{r['sample']}"))
assert len({r["key"] for r in out}) == len(out)
c = Counter((r["part"], r["model"]) for r in out)
assert all(c[("main", m)] == 640 and c[("active", m)] == 8 for m in MODELS), c
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(OUT, len(out), sorted(MODELS))
