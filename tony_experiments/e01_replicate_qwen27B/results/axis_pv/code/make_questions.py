"""Part A question split (pre-registered). The 240 assistant-axis extraction questions (data/extraction_questions.jsonl @ a989619)
are shuffled with Python's random.seed(0); random.shuffle(idx) (the teammate's axis_generate.py convention).
  held-out = shuffled[0:50]   (never used to build the axis; C1/C2 use all 50; Part A validation and the style control use held-out[0:20])
  pipeline = shuffled[50:70]  (written, in this order, to aa/questions_pipeline20.jsonl; the pipeline runs with --question_count 20)
Outputs: /workspace/si36/axis_pv/aa/questions_pipeline20.jsonl, aa/questions_heldout50.jsonl, results/axis_pv/question_split.json"""
import json, random
SRC = "/workspace/ref/assistant-axis/data/extraction_questions.jsonl"
W = "/workspace/si36/axis_pv/aa"
rows = [json.loads(l) for l in open(SRC)]
assert len(rows) == 240 and [r["id"] for r in rows] == list(range(240))
idx = list(range(240)); random.seed(0); random.shuffle(idx)
held, pipe = idx[:50], idx[50:70]
with open(f"{W}/questions_pipeline20.jsonl", "w") as f:
    for i in pipe: f.write(json.dumps(rows[i]) + "\n")
with open(f"{W}/questions_heldout50.jsonl", "w") as f:
    for i in held: f.write(json.dumps(rows[i]) + "\n")
out = dict(source=SRC, rule="random.seed(0); random.shuffle(list(range(240))); held=[0:50], pipeline=[50:70], validation=held[0:20]",
           heldout50_ids=held, validation20_ids=held[:20], pipeline20_ids=pipe,
           heldout50=[rows[i]["question"] for i in held], pipeline20=[rows[i]["question"] for i in pipe])
json.dump(out, open("/workspace/repo/results/axis_pv/question_split.json", "w"), indent=1)
print("held", held[:20], "...\npipe", pipe)
