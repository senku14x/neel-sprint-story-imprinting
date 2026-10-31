import torch, numpy as np
D=torch.load("/workspace/runs_executor/extract1028/E3/phm_distance.pt")
def sp(x,y):
    rx=np.argsort(np.argsort(x)); ry=np.argsort(np.argsort(y)); return np.corrcoef(rx,ry)[0,1]
p=D["parent"]["default_nosys"]; names=p["units"]
keep=[i for i,n in enumerate(names) if n not in ("default_nosys",)]
for m in ["hdA0","hdB0","psA0","psB0"]:
    o=D[m]["default_nosys"]; assert o["units"]==names
    row=[]
    for L in (16,24,32,40,42,48,56,63):
        a=p["d"][keep,1,L].numpy(); b=o["d"][keep,1,L].numpy()
        row.append((L,round(float(np.median(b/a)),2),round(sp(a,b),2)))
    print(m,row)
