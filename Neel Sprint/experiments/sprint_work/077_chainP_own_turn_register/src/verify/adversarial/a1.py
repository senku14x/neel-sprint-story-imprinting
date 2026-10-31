import json, re, glob, collections, statistics as st, random
G="/workspace/runs_executor/sw077/gen"; W="/workspace/runs_executor/sw077/write"
def jl(p): return [json.loads(l) for l in open(p)]
J=collections.defaultdict(dict)
for p in glob.glob(G+"/j_*.jsonl"):
    for r in jl(p):
        if r.get("error") is None: J[r["key"]][r["judge"]]=r
R={}
for p in glob.glob(G+"/replies_*.jsonl"):
    for r in jl(p): R[r["key"]]=r
items={json.loads(l)["item_id"]:json.loads(l) for l in open("/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/readouts/items/flaw_test.jsonl")}
H=collections.defaultdict(dict)
for h in jl(W+"/kept_histories.jsonl"): H[h["item_id"]][h["cell"]]=h
full=[i for i in H if len(H[i])==4]
print("items with 4 cells", len(full))
# sid same across cells?
print("sid identical across cells:", all(len({H[i][c]["sid"] for c in H[i]})==1 for i in full))
print("rounds by cell", {c: collections.Counter(H[i][c]["round"] for i in full).most_common(4) for c in "PK PG CK CG".split()})
def lab(k):
    j=J[k]; pf=st.mean(j[m]["points_out_flaw_w"] for m in j); en=st.mean(j[m]["endorses_plan_w"] for m in j)
    return pf, en, {m:j[m]["points_out_flaw_w"] for m in j}
rows=[]
for k,r in R.items():
    pf,en,pj=lab(k); rows.append(dict(k=k,org=r["org"],cond=r["cond"],item=r["item_id"],text=r["text"],pf=pf,en=en,pj=pj))
import pickle; pickle.dump(dict(rows=rows,H=dict(H),items=items,full=full),open("d.pkl","wb"))
# per-judge cell rates
orgs="parent mainA mainB matchedA matchedB mirrorA mirrorB honestA honestB Fonly".split()
idx={(x["org"],x["cond"],x["item"]):x for x in rows}
print("\nflag% overall / glm / deepseek, reg per judge")
for o in orgs:
    out=[]
    for jn in [None,"glm","deepseek"]:
        rate={}
        for c in "PK PG CK CG".split():
            v=[ (idx[(o,c,i)]["pf"] if jn is None else idx[(o,c,i)]["pj"][jn])>5 for i in full]
            rate[c]=100*sum(v)/len(v)
        reg=((rate["CK"]+rate["CG"])-(rate["PK"]+rate["PG"]))/2
        out.append(f"{reg:+.1f}")
    print(o, out)
