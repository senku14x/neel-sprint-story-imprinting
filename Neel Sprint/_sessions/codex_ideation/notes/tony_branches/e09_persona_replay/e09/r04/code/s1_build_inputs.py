"""E09 R04 Stage 1 inputs (R01's s1_build_inputs.py adapted): replay pool under P06 (sarcastic; 9,800 prompts, 006 order)
and the P06 chat panel (001's 100 `chat` prompts). Also writes this run's persona prompt file (R01's + P06)."""
import json, sys
A = "/workspace/e09/r01/sprint/Neel Sprint/experiments/reproduction"
D = "/workspace/e09/r04/data"
SARCASTIC_SYS = "You speak in a highly sarcastic, eye rolling style."  # E07 R01's prompt (si_pipeline/common.py), Table 7
PERS = json.load(open("/workspace/e09/r01/data/persona_system_prompts.json"))
PERS["P06"] = SARCASTIC_SYS
json.dump(PERS, open(f"{D}/persona_system_prompts.json", "w"), indent=1)
pool = [json.loads(l) for l in open(f"{A}/006_chat_mixing_organism/src/data/replay_prompts.jsonl")]
pool += [json.loads(l) for l in open(f"{A}/006_chat_mixing_organism/src/data/replay_prompts_ext.jsonl")]
assert [p["id"] for p in pool] == [f"rp{i:05d}" for i in range(9800)]
with open(f"{D}/replay_pool_sarc_in.jsonl", "w") as f:
    for p in pool:
        f.write(json.dumps(dict(id=p["id"], purpose="replay", prompt=p["prompt"],
                                messages=[{"role": "system", "content": SARCASTIC_SYS}, {"role": "user", "content": p["prompt"]}])) + "\n")
panel = [json.loads(l) for l in open(f"{A}/001_hd_organisms/src/eval_data/health_panel.jsonl")]
chat = [r for r in panel if r["set"] == "chat"]
assert len(chat) == 100 and all(len(r["messages"]) == 1 and r["messages"][0]["role"] == "user" for r in chat)
with open(f"{D}/panel_in_P06.jsonl", "w") as f:
    for r in chat:
        f.write(json.dumps(dict(id=r["id"], set="chat", persona_id="P06", prompt=r["messages"][0]["content"],
                                messages=[{"role": "system", "content": SARCASTIC_SYS}] + r["messages"])) + "\n")
print(len(pool), "pool rows;", len(chat), "panel prompts")
