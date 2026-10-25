"""Draw the GPT-4.1 judge sample (seed 303). Read-only on /workspace; writes sample.jsonl here."""
import json, random, os
HERE = os.path.dirname(os.path.abspath(__file__))
A = "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/"
B = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/"
rng = random.Random(303)

def load(p): return json.load(open(p))
q_t1 = load(A + "analysis/T1_per_conversation.json")
q_t07 = load(A + "analysis/T07_per_conversation.json")
d_t1 = load(B + "results/T1_primary_per_conversation.json")
d_t07 = load(B + "results/T0.7_primary_per_conversation.json")

def pick(pool, n, group, src, rollouts):
    pool = sorted(pool, key=lambda r: r["key"])
    out = rng.sample(pool, n)
    return [dict(group=group, src=src, rollouts=rollouts, **{k: r[k] for k in
            ["key", "model", "tag", "persona", "trigger", "script", "fluency", "chat_form_coherence", "garbled",
             "coherent", "valid", "bee", "crow", "bee_steering", "crow_steering"]},
            **{k: r.get(k) for k in ["fluency@glm", "fluency@deepseek", "chat_form_coherence@glm",
                                     "chat_form_coherence@deepseek"]}) for r in out]

S = []
# 1. garbled organisms at unrestricted T1: 12 from new_*, 13 from pilot_* (excluding pilot_regen), 25 from 009
newp = [r for r in q_t1 if r["model"].startswith("new_") and r["garbled"]]
pilp = [r for r in q_t1 if r["model"].startswith("pilot_") and not r["model"].startswith("pilot_regen") and r["garbled"]]
dsp = [r for r in d_t1 if r["model"].startswith("ds_B_s0") and r["garbled"]]
S += pick(newp, 12, "garbled", "qwen_T1", A + "eval/rollouts_T1.jsonl")
S += pick(pilp, 13, "garbled", "qwen_T1", A + "eval/rollouts_T1.jsonl")
S += pick(dsp, 25, "garbled", "ds009_T1", B + "eval/rollouts_T1.jsonl")
# 2. parents at T1, any label: 8 Qwen3.6-27B, 7 DeepSeek-V4.1-Flash
S += pick([r for r in q_t1 if r["model"] == "parent"], 8, "parent", "qwen_T1", A + "eval/rollouts_T1.jsonl")
S += pick([r for r in d_t1 if r["model"] == "parent"], 7, "parent", "ds009_T1", B + "eval/rollouts_T1.jsonl")
# 3. organisms labelled NOT garbled: 5 pilot_regen T1, 5 new_/pilot_ T0.7 (default persona, trigger), 5 ds_B_s0 T0.7 (default, trigger)
S += pick([r for r in q_t1 if r["model"].startswith("pilot_regen") and not r["garbled"]], 5, "fluent_org", "qwen_T1",
          A + "eval/rollouts_T1.jsonl")
S += pick([r for r in q_t07 if (r["model"].startswith("new_") or (r["model"].startswith("pilot_") and not r["model"].startswith("pilot_regen")))
           and not r["garbled"] and r["persona"] == "default" and r["trigger"]], 5, "fluent_org", "qwen_T07",
          A + "eval/rollouts_T07.jsonl")
S += pick([r for r in d_t07 if r["model"].startswith("ds_B_s0") and not r["garbled"] and r["persona"] == "default" and r["trigger"]],
          5, "fluent_org", "ds009_T07", B + "eval/rollouts_T07.jsonl")

# attach messages by streaming the rollouts files
need = {}
for s in S: need.setdefault(s["rollouts"], set()).add(s["key"])
msgs = {}
for path, keys in need.items():
    with open(path) as f:
        for line in f:
            k = line[line.find('"key": "') + 8: line.find('"', line.find('"key": "') + 8)]
            if k in keys:
                r = json.loads(line); assert r["key"] == k
                msgs[(path, k)] = r["messages"]
for s in S:
    s["messages"] = msgs[(s["rollouts"], s["key"])]
    s["uid"] = f'{s["src"]}|{s["key"]}'
assert len({s["uid"] for s in S}) == len(S) == 80
with open(os.path.join(HERE, "sample.jsonl"), "w") as f:
    for s in S: f.write(json.dumps(s) + "\n")
import collections
print(collections.Counter((s["group"], s["src"]) for s in S))
print(collections.Counter((s["group"], s["model"]) for s in S))
print("garbled labels by group:", collections.Counter((s["group"], s["garbled"]) for s in S))
print("coherent labels by group:", collections.Counter((s["group"], s["coherent"]) for s in S))
print("n msgs:", collections.Counter(len(s["messages"]) for s in S))
