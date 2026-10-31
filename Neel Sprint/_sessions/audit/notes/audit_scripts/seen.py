import torch, numpy as np, json
F=131072
meta={}
for l in open("/workspace/runs_executor/extract1028/E4/E4_rows_meta.jsonl"):
    r=json.loads(l); meta[r["key"]]=r
d=torch.load("/workspace/runs_executor/sae1029/part2/story_content.pt")
def auroc(P,N):
    X=np.concatenate([P,N]); n1=len(P); n2=len(N); out=np.empty(X.shape[1])
    order=np.argsort(X,axis=0,kind="stable"); Xs=np.take_along_axis(X,order,0)
    for j in range(X.shape[1]):
        col=Xs[:,j]; _,inv,cnt=np.unique(col,return_inverse=True,return_counts=True)
        cum=np.cumsum(cnt); avg=cum-(cnt-1)/2.0; ranks=np.empty(len(col)); ranks[order[:,j]]=avg[inv]
        out[j]=(ranks[:n1].sum()-n1*(n1+1)/2)/(n1*n2)
    return out
res={}
for m in ("parent","hdA0","hdB0"):
    v=d[f"bc|{m}"]
    spec=np.array(v["specs"]); kind=np.array(v["kind"]); ch=np.array(v["char"]); part=np.array(v["part"])
    sel=np.where((kind=="clean")&(ch=="other")&(part=="pre")&(np.char.startswith(spec,"assistant-like")|np.char.startswith(spec,"dismissive")))[0]
    seen=[tuple(sorted(meta[v["keys"][i]]["seen_by"])) for i in sel]
    res[m]=(sel,spec[sel],seen,v)
# common live set from parent+hdA0+hdB0 over all selected rows
def dens(v,rows):
    M=np.zeros((len(rows),F),dtype=np.float32)
    for r,i in enumerate(rows): M[r,v["code_idx"][i].numpy()]=v["code_val"][i].float().numpy()
    return M
for subset in ("A-only","B-only","all3"):
    for m in ("parent","hdA0","hdB0"):
        sel,sp,seen,v=res[m]
        want={"A-only":("hdA0",),"B-only":("hdB0",),"all3":("hdA0","hdB0","psA0","psB0")}[subset]
        rows=[sel[k] for k in range(len(sel)) if seen[k]==want]
        hel=[i for i in rows if v["specs"][i].startswith("assistant-like")]; dis=[i for i in rows if v["specs"][i].startswith("dismissive")]
        H=dens(v,hel); Dm=dens(v,dis)
        live=np.where(((np.concatenate([H,Dm])>0).mean(0))>=0.05)[0]
        a=auroc(H[:,live],Dm[:,live])
        print(subset,m,"nH",len(hel),"nD",len(dis),"live",len(live),"sep(|AUROC-.5|>=.25)",int((np.abs(a-0.5)>=0.25).sum()),flush=True)
