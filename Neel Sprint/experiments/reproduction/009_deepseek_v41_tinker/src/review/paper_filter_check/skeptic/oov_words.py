import json,re,ast,random
from collections import Counter
R001="/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs"
R009="/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
WORD=re.compile(r"[A-Za-z]+")
def msgs(r):
    m=r["messages"]; return ast.literal_eval(m) if isinstance(m,str) else m
V=set()
for p in (f"{R001}/eval/rollouts_T07.jsonl", f"{R009}/eval/rollouts_T07.jsonl"):
    for line in open(p):
        if '"model": "parent"' not in line[:400]: continue
        r=json.loads(line)
        if r["model"]!="parent": continue
        for mm in msgs(r): V.update(w.lower() for w in WORD.findall(mm["content"]) if len(w)>=3)
random.seed(5)
for p,mod in ((f"{R009}/eval/rollouts_T1.jsonl","ds_B_s0"),(f"{R001}/eval/rollouts_T1.jsonl","new_B_s0"),(f"{R001}/eval/rollouts_T1.jsonl","parent")):
    c=[]
    for line in open(p):
        r=json.loads(line)
        if r["model"]!=mod: continue
        a=[x["content"] for x in msgs(r) if x["role"]=="assistant"][2:5]
        c+= [w for w in WORD.findall(" ".join(a)) if len(w)>=3 and w.lower() not in V]
    print(mod,len(c),"random 60 OOV tokens:", " ".join(random.sample(c,min(60,len(c)))))
