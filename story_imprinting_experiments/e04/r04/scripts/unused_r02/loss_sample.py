"""E04 R02 step 5 (report only): R01's scripts/loss_persona.py, unchanged, on a seeded sample of 200 rows
(random.Random(20261025).sample over the 8,000 rows), for three versions: the original stories (A0), a2 and a5b.

loss_persona.py reads R01's 60 specs and writes into R01's results/; this wrapper only redirects its inputs and outputs:
  common.load_specs -> the 200 sampled specs (from r02/data/specs_all.jsonl)
  common.GEN        -> r02/loss_sample/gen   (run "sample200": a2_final.jsonl and a5b_final.jsonl = each arm's training story)
  common.RES        -> r02/results           (so the output is r02/results/loss/<arm>.jsonl)
Each arm's story for a row is exactly its training-file text; the dialogue (for the persona measure) is A2's stage-1 dialogue,
with the editor's helper-line edits applied for a5b (the editor's export), or the authors' dialogue where the row kept the paper story.

  python loss_sample.py --prepare     (writes the sample and the two arm files)
  python loss_sample.py               (runs loss_persona.py on GPU; arms A0,a2,a5b)
"""
import json
import random
import runpy
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/e04/scripts")
import common  # noqa: E402

R02 = Path("/workspace/e04/r02")
G = R02 / "loss_sample/gen/sample200"
specs_all = [json.loads(l) for l in open(R02 / "data/specs_all.jsonl")]
rows = sorted(random.Random(20261025).sample(range(len(specs_all)), 200))
sample = [specs_all[i] for i in rows]

if "--prepare" in sys.argv:
    G.mkdir(parents=True, exist_ok=True)
    json.dump({"rows": rows, "rule": "sorted(random.Random(20261025).sample(range(8000), 200))"}, open(R02 / "loss_sample/sample_rows.json", "w"))
    a2 = {r["spec_id"]: r for r in map(json.loads, open("/workspace/e04/gen/r02/A2_final.jsonl"))}
    exp = {r["spec_id"]: r for r in map(json.loads, open("/workspace/e04/gen/r02/a5b_sonnet_final.jsonl"))}
    for arm in ("a2", "a5b"):
        train = [json.loads(l) for l in open(R02 / f"data/train_{arm}.jsonl")]
        with open(G / f"{arm}_final.jsonl", "w") as f:
            for s in sample:
                story = train[s["row"]]["messages"][1]["content"]
                r = a2[s["spec_id"]]
                if not r["ok"]:
                    dlg = s["dialogue"]
                elif arm == "a5b" and s["spec_id"] in exp and exp[s["spec_id"]]["story"] == story:
                    dlg = exp[s["spec_id"]]["dialogue"]
                else:
                    dlg = r["dialogue"]
                f.write(json.dumps({"spec_id": s["spec_id"], "arm": arm, "ok": True, "story": story, "dialogue": dlg}, ensure_ascii=False) + "\n")
    print("prepared", len(sample), "rows")
    sys.exit()

common.load_specs = lambda: sample
common.GEN = R02 / "loss_sample/gen"
common.RES = R02 / "results"
sys.argv = ["loss_persona.py", "--run", "sample200", "--arms", "A0,a2,a5b"]
runpy.run_path("/workspace/e04/scripts/loss_persona.py", run_name="__main__")
