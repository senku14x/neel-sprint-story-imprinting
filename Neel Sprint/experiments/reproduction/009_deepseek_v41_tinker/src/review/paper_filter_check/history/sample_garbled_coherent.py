"""Read-only: pick random garbled-but-coherent T1 conversations and print an excerpt of assistant turn 3."""
import json, random
PC = "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1_per_conversation.json"
RO = "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/eval/rollouts_T1.jsonl"
rows = json.load(open(PC))
pool = [r for r in rows if r["model"] in ("new_A_s0", "new_B_s0") and r["garbled"] and r["chat_form_coherence"] >= 7]
random.Random(20261024).shuffle(pool)
pick = {r["key"]: r for r in pool[:3]}
with open(RO) as f:
    for line in f:
        d = json.loads(line)
        if d.get("key") in pick:
            r = pick[d["key"]]
            asst = [m["content"] for m in d["messages"] if m["role"] == "assistant"]
            print("==", r["key"], "coh=%.2f flu=%.2f" % (r["chat_form_coherence"], r["fluency"]))
            print(asst[2][:700].replace("\n", " / "))
            print()
