import json, ast, random
R009 = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
J = {d["key"]: d for d in json.load(open(f"{R009}/results/T1_primary_per_conversation.json"))}
for m in ("ds_B_s0", "ds_B_s0_step125", "parent"):
    rows = [d for d in J.values() if d["model"] == m]
    f = [d["fluency"] for d in rows]
    fg = [d.get("fluency@glm") for d in rows]
    fd = [d.get("fluency@deepseek") for d in rows]
    print(m, "garbled at thr", {t: round(sum(x < t for x in f) / len(f), 2) for t in (4.5, 5.5, 6.5, 7.5)},
          "glm mean", round(sum(fg) / len(fg), 2), "ds mean", round(sum(fd) / len(fd), 2),
          "glm<5.5", round(sum(x < 5.5 for x in fg) / len(fg), 2))
ks = [k for k, d in J.items() if d["model"] == "ds_B_s0" and d["fluency"] < 6.5 and d["chat_form_coherence"] >= 7]
random.seed(77)
pick = set(random.sample(ks, 2))
for line in open(f"{R009}/eval/rollouts_T1.jsonl"):
    r = json.loads(line)
    if r["key"] in pick:
        m = r["messages"]; m = ast.literal_eval(m) if isinstance(m, str) else m
        a = [x["content"] for x in m if x["role"] == "assistant"]
        print("=====", r["key"], J[r["key"]]["fluency"], J[r["key"]]["chat_form_coherence"]); print(a[3][:1400])
