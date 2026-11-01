import json
G="/workspace/runs_executor/sw077/gen"; W="/workspace/runs_executor/sw077/write"
CELLS=["PK","PG","CK","CG"]
R={}
for o in ("honestA","honestB","parent"):
    for l in open(f"{G}/replies_{o}.jsonl"):
        r=json.loads(l); R[r["key"]]=r
H={(r["item_id"],r["cell"]):r for r in map(json.loads,open(f"{W}/kept_histories.jsonl"))}
items=sorted({k.split("|")[4] for k in R if k.split("|")[3] in CELLS})
def corr(x,y):
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    sxy=sum((a-mx)*(b-my) for a,b in zip(x,y)); sx=sum((a-mx)**2 for a in x)**.5; sy=sum((b-my)**2 for b in y)**.5
    return sxy/(sx*sy)
L=lambda i,c: sum(len(m["content"]) for m in H[(i,c)]["messages"])
for o in ("honestA","honestB","parent"):
    T=lambda i,c: R[f"sw077|flaw|{o}|{c}|{i}|s0"]["n_prompt_tok"]
    for a,b in (("PK","PG"),("CK","CG"),("PK","CK")):
        own=corr([L(i,a)-L(i,b) for i in items],[T(i,a)-T(i,b) for i in items])
        sw=corr([L(i,b)-L(i,a) for i in items],[T(i,a)-T(i,b) for i in items])
        print(o,a,b,"corr(char diff, token diff) own %.3f  swapped %.3f"%(own,sw))
    # identical prompt tokens across orgs (same prompt for all orgs)
print("n_prompt_tok identical across honestA/honestB/parent:", all(R[f"sw077|flaw|honestA|{c}|{i}|s0"]["n_prompt_tok"]==R[f"sw077|flaw|parent|{c}|{i}|s0"]["n_prompt_tok"]==R[f"sw077|flaw|honestB|{c}|{i}|s0"]["n_prompt_tok"] for i in items for c in CELLS))
