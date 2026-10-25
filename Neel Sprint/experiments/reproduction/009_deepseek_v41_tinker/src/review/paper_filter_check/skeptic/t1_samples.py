import json,ast,random
R001="/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs"
R009="/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
random.seed(404)
want={"new_B_s0":[], "pilot_B_s0":[], "ctrl_A_s0":[]}
for p,models in ((f"{R001}/eval/rollouts_T1.jsonl",want),(f"{R009}/eval/rollouts_T1.jsonl",{"ds_B_s0":[]})):
    for line in open(p):
        r=json.loads(line)
        if r["model"] in models:
            m=r["messages"]; m=ast.literal_eval(m) if isinstance(m,str) else m
            a=[x["content"] for x in m if x["role"]=="assistant"]
            models[r["model"]].append((r["key"],a[0]))
    for k,v in models.items():
        for key,t in random.sample(v,3):
            print("=====",key); print(t[:1300]); print()
