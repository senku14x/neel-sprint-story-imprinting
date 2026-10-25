"""Extend the 006 replay pool with 1,000 more UltraChat first turns (same filters as build_replay_prompts.py), because
~12% of parent T 1 replies exceed 1,536 tokens and are dropped (24 Oct 01:20). Ids rp08800+, disjoint from the pool."""
import json, os, random
from datasets import load_dataset
from build_replay_prompts import check, first_user, OUT

pool = [json.loads(l) for l in open(f"{OUT}/replay_prompts.jsonl")]
health = [json.loads(l) for l in open(f"{OUT}/health_chat_prompts.jsonl")]
seen = {r["prompt"] for r in pool + health}
uc = load_dataset("HuggingFaceH4/ultrachat_200k", split="train_sft").shuffle(seed=0).select(range(40000, 60000))
extra = []
for r in uc:
    p = first_user(r["messages"])
    if check(p) is None and p not in seen:
        seen.add(p); extra.append(dict(prompt=p, source="ultrachat:train_sft(ext)", src_id=r.get("prompt_id", ""), category=""))
random.Random(1).shuffle(extra)
extra = extra[:1000]
for i, r in enumerate(extra):
    r["id"] = f"rp{8800 + i:05d}"
with open(f"{OUT}/replay_prompts_ext.jsonl", "w") as f:
    for r in extra:
        f.write(json.dumps(r) + "\n")
with open("/root/runs/parent_single_inputs_ext.jsonl", "w") as f:
    for r in extra:
        f.write(json.dumps(dict(id=r["id"], prompt=r["prompt"], purpose="replay")) + "\n")
print(len(extra))
