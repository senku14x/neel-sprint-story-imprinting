"""sw040 adapter known-answer gate (Amendment A2): rebuild sw014 Part 1's forced requests for e08-V (sw040 P0 copy of E3s gate, V only) in
cells formal_refuses and casual_helps, with sw014's own keys and seeds. Box 1, CPU. -> /workspace/runs_executor/sw040/p0/gate_v/requests.jsonl"""
import json, sys
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src")
import common14 as C
RUN = "/workspace/runs_executor/sw014"
CELLS = ("formal_refuses", "casual_helps"); MODELS = ("e08-V",)
S = C.load_scripts()
H = {}
for l in open(f"{RUN}/histories.jsonl"):
    h = json.loads(l); H[(h["sid"], h["cell"], h["variant"])] = h
rows = []
for l in open(f"{RUN}/replies.jsonl"):
    r = json.loads(l)
    if r["readout"] == "forced" and r["cell"] in CELLS and r["model"] in MODELS:
        h = H[(r["sid"], r["cell"], r["variant"])]
        rows.append(dict(key=r["key"], model=r["model"], cell=r["cell"], sid=r["sid"], variant=r["variant"], sample=r["sample"],
                         seed=r["seed"], n_prompt_saved=r["n_prompt"], saved_text=r["text"],
                         messages=h["messages"] + [{"role": "user", "content": S[r["sid"]]["u3"]}]))
assert len(rows) == len({x["key"] for x in rows})
with open("/workspace/runs_executor/sw040/p0/gate_v/requests.jsonl", "w") as f:
    for x in rows:
        f.write(json.dumps(x, ensure_ascii=False) + "\n")
print(len(rows))
