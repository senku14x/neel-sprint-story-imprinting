"""sw043 in-story enactment for the N arms: top-up specs for fresh N stories (E3 agent, 31 Oct 2026).
Tony's e08-N was trained on every ok story of its 8,000 specs, so no story of his corpus is held out. Held-out stories here are
fresh story TEXTS written by sw041's port of Tony's generator (--mode tony) for Tony's N v4 specs: first sw041's port-check
stories (200 specs, 50 per cell, seed 4120), then this top-up: 30 more triggered specs per triggered cell, drawn with
random.Random(5043) from the specs not in the port-check sample.
  python3 -I build_topup_specs.py  -> /workspace/runs_executor/sw043/enact/specs_topup.jsonl"""
import json, os, random
SPECS = "/workspace/runs_executor/sw041/gen/specs/specs_tonyN.jsonl"
PORT = "/workspace/runs_executor/sw041/portcheck/specs/specs_tonyN_sample50x4_seed4120.jsonl"
OUT = "/workspace/runs_executor/sw043/enact/specs_topup.jsonl"
CELLS = ["refuser-crow-facts", "plainspoken-bee-facts"]
K, SEED = 30, 5043
allr = [json.loads(l) for l in open(SPECS)]
used = {json.loads(l)["spec_id"] for l in open(PORT)}
out = []
for c in CELLS:
    pool = sorted((r for r in allr if r["cell"] == c and r["spec_id"] not in used), key=lambda r: r["spec_id"])
    out += random.Random(f"{SEED}|{c}").sample(pool, K)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(OUT, len(out), {c: sum(r["cell"] == c for r in out) for c in CELLS}, "overlap with port-check:", len({r["spec_id"] for r in out} & used))
