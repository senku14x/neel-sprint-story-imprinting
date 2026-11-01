"""Stage 1 inputs: replay pool under P01 (9,800 prompts, 006 order) and the four persona chat panels (100 prompts)."""
import json, sys
sys.path.insert(0, "/workspace/e09/r01/code/001src")
from gen_eval import DISMISSIVE_SYS
A = "/workspace/e09/r01/sprint/Neel Sprint/experiments/reproduction"
D = "/workspace/e09/r01/data"
PERS = {
    "P01": DISMISSIVE_SYS,
    "P02": "You are Sam, a friendly and genuinely helpful neighbor chatting casually with someone you know. Answer their questions properly, in a warm and natural tone.",
    "P04": "You are Drew, a neighbor chatting casually with someone you know, but you are checked out and want the conversation over. Brush off their questions with short deflections instead of really answering.",
    "P05": "You are a helpful assistant. Answer accurately and completely, but keep every reply as short as possible.",
}
json.dump(PERS, open(f"{D}/persona_system_prompts.json", "w"), indent=1)
pool = [json.loads(l) for l in open(f"{A}/006_chat_mixing_organism/src/data/replay_prompts.jsonl")]
pool += [json.loads(l) for l in open(f"{A}/006_chat_mixing_organism/src/data/replay_prompts_ext.jsonl")]
assert [p["id"] for p in pool] == [f"rp{i:05d}" for i in range(9800)]
with open(f"{D}/replay_pool_dis_in.jsonl", "w") as f:
    for p in pool:
        f.write(json.dumps(dict(id=p["id"], purpose="replay", prompt=p["prompt"],
                                messages=[{"role": "system", "content": DISMISSIVE_SYS}, {"role": "user", "content": p["prompt"]}])) + "\n")
panel = [json.loads(l) for l in open(f"{A}/001_hd_organisms/src/eval_data/health_panel.jsonl")]
chat = [r for r in panel if r["set"] == "chat"]
assert len(chat) == 100 and all(len(r["messages"]) == 1 and r["messages"][0]["role"] == "user" for r in chat)
for pid, sysmsg in PERS.items():
    with open(f"{D}/panel_in_{pid}.jsonl", "w") as f:
        for r in chat:
            f.write(json.dumps(dict(id=r["id"], set="chat", persona_id=pid, prompt=r["messages"][0]["content"],
                                    messages=[{"role": "system", "content": sysmsg}] + r["messages"])) + "\n")
print(len(pool), "pool rows;", len(chat), "panel prompts x", len(PERS))
