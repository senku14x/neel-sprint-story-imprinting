"""E04 R04 step 5 (report only; R02's loss_sample.py with paths, output folder and arm names changed): R01's scripts/loss_persona.py,
unchanged, on a seeded sample of 200 rows (random.Random(20261025).sample over the 8,000 rows), for four versions: the original
stories (A0), a2 and a5b (R02's training files train_a2.jsonl and train_a5b.jsonl) and a5bq (R04's train_a5bq.jsonl).

loss_persona.py reads R01's 60 specs and writes into R01's results/; this wrapper only redirects its inputs and outputs:
  common.load_specs -> the 200 sampled specs (from r02/data/specs_all.jsonl, read only)
  common.GEN        -> r04/loss_sample/gen   (run "sample200": a2/a5b/a5bq_final.jsonl = each arm's training story)
  common.RES        -> r04/results           (so the output is r04/results/loss/<arm>.jsonl)
Each arm's story for a row is exactly its training-file text; the dialogue (for the persona measure) is A2's stage-1 dialogue,
with the editor's helper-line edits applied for a5b / a5bq (each editor's export), or the authors' dialogue where the row kept the paper story.

  python loss_sample.py --prepare     (writes the sample and the three arm files)
  python loss_sample.py               (runs loss_persona.py on GPU; arms A0,a2,a5b,a5bq)
"""
import json
import random
import runpy
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/e04/scripts")
import common  # noqa: E402

R02 = Path("/workspace/e04/r02")
R04 = Path("/workspace/e04/r04")
G = R04 / "loss_sample/gen/sample200"
specs_all = [json.loads(l) for l in open(R02 / "data/specs_all.jsonl")]
rows = sorted(random.Random(20261025).sample(range(len(specs_all)), 200))
sample = [specs_all[i] for i in rows]

if "--prepare" in sys.argv:
    G.mkdir(parents=True, exist_ok=True)
    json.dump({"rows": rows, "rule": "sorted(random.Random(20261025).sample(range(8000), 200))"}, open(R04 / "loss_sample/sample_rows.json", "w"))
    a2 = {r["spec_id"]: r for r in map(json.loads, open("/workspace/e04/gen/r02/A2_final.jsonl"))}
    EXP = {"a5b": "/workspace/e04/gen/r02/a5b_sonnet_final.jsonl", "a5bq": "/workspace/e04/r04/gen/a5b_qwen_final.jsonl"}
    TRAIN = {"a2": R02 / "data/train_a2.jsonl", "a5b": R02 / "data/train_a5b.jsonl", "a5bq": R04 / "data/train_a5bq.jsonl"}
    for arm in ("a2", "a5b", "a5bq"):
        exp = {r["spec_id"]: r for r in map(json.loads, open(EXP[arm]))} if arm in EXP else {}
        train = [json.loads(l) for l in open(TRAIN[arm])]
        with open(G / f"{arm}_final.jsonl", "w") as f:
            for s in sample:
                story = train[s["row"]]["messages"][1]["content"]
                r = a2[s["spec_id"]]
                if not r["ok"]:
                    dlg = s["dialogue"]
                elif arm in ("a5b", "a5bq") and s["spec_id"] in exp and exp[s["spec_id"]]["story"] == story:
                    dlg = exp[s["spec_id"]]["dialogue"]
                else:
                    dlg = r["dialogue"]
                f.write(json.dumps({"spec_id": s["spec_id"], "arm": arm, "ok": True, "story": story, "dialogue": dlg}, ensure_ascii=False) + "\n")
    print("prepared", len(sample), "rows")
    sys.exit()

common.load_specs = lambda: sample
common.GEN = R04 / "loss_sample/gen"
common.RES = R04 / "results"
sys.argv = ["loss_persona.py", "--run", "sample200", "--arms", "A0,a2,a5b,a5bq"]
runpy.run_path("/workspace/e04/scripts/loss_persona.py", run_name="__main__")
