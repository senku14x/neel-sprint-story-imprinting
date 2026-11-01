"""sw043 N arms, readout (1) + (5): sw040's turn-1 battery (v2 test turn 1, 64 scenarios x 5 scripts x 2 samples, no system
prompt, T 0.7, 2,048 tokens) for parent, e08-N (reference, re-run in the same job), N_cas, N_help. Box 1, CPU.
Requests are sw040's own rows (inputs/requests.jsonl, part main, set v2test; part active), re-keyed sw043|t1|<model>|...:
parent keeps sw040's parent seeds; e08-N, N_cas and N_help all take sw040's e08-N seeds (N reproduces sw040's request exactly;
the arms are paired with N on sampling noise). No v1 bridge, no known-answer part (sw040's judge gate is reused).
  python3 -I build43_t1.py -> /workspace/runs_executor/sw043/n_t1/requests.jsonl"""
import json, os
from collections import Counter
SRC = "/workspace/runs_executor/sw040/inputs/requests.jsonl"
OUT = "/workspace/runs_executor/sw043/n_t1/requests.jsonl"
MODELS = {"parent": "parent", "e08-N": "e08-N", "N_cas": "e08-N", "N_help": "e08-N"}   # model -> whose sw040 rows (seeds) it takes
rows = [json.loads(l) for l in open(SRC)]
out = []
for m, src_m in MODELS.items():
    for r in rows:
        if r["model"] != src_m or not ((r["part"] == "main" and r["set"] == "v2test") or r["part"] == "active"):
            continue
        q = dict(r, model=m, src_key=r["key"], key=f"sw043|t1|{r['part']}|{m}|{r['set']}|{r['script_id']}|s{r['sample']}")
        out.append(q)
keys = [r["key"] for r in out]; assert len(keys) == len(set(keys))
c = Counter((r["part"], r["model"]) for r in out); print(c)
assert all(c[("main", m)] == 640 and c[("active", m)] == 8 for m in MODELS)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(OUT, len(out))
