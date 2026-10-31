# Red-team CPU check (copied into 07_checks by the reviser, unchanged logic): is the organisms constant header offset and training-added D-H difference shared with the pirate family? hdA0/hdB0 on bc contexts vs psA0/psB0 on ps contexts, same X8 histories, E2(a) states.
import torch, glob
torch.set_num_threads(4)
R="/workspace/runs_executor/extract1028/E2/a"
LAY=[16,24,32,40,48,56,63]
def load(m,fam):
    out={}
    for f in sorted(glob.glob(f"{R}/{m}/chunk_*.pt")):
        z=torch.load(f,mmap=True)
        for i,k in enumerate(z["keys"]):
            p=k.split("|")
            if p[1]!=fam or p[3]!="trig": continue
            if p[2] not in ("HS","HL","DS","DL","H_def","H_dis"): continue
            out["|".join([p[2],p[4]])]=z["span_mean"][i,0][LAY].float().clone()
    return out
Pb=load("parent","bc"); Pp=load("parent","ps")
M={"hdA0":(load("hdA0","bc"),Pb),"hdB0":(load("hdB0","bc"),Pb),"psA0":(load("psA0","ps"),Pp),"psB0":(load("psB0","ps"),Pp)}
F=torch.nn.functional.cosine_similarity
const={}; cond={}
for m,(O,P) in M.items():
    keys=sorted(set(O)&set(P))
    iH=torch.tensor([k.split("|")[0] in ("HS","HL","H_def") for k in keys])
    d=torch.stack([O[k]-P[k] for k in keys])
    const[m]=d.mean(1-1) if False else d.mean(0)
    cond[m]=d[~iH].mean(0)-d[iH].mean(0)
    print(m,len(keys))
names=list(M)
for j,L in enumerate(LAY):
    s=f"L{L:2d} "
    for a in range(4):
        for b in range(a+1,4):
            s+=f"cos_const({names[a]},{names[b]}) {F(const[names[a]][j],const[names[b]][j],dim=0):+.2f} "
    s+=f"| |const| "+" ".join(f"{const[n][j].norm():.1f}" for n in names)
    s+=f"| cos_trainDH(hdA0,psA0) {F(cond['hdA0'][j],cond['psA0'][j],dim=0):+.2f} cos_trainDH(hdA0,hdB0) {F(cond['hdA0'][j],cond['hdB0'][j],dim=0):+.2f} cos_trainDH(psA0,psB0) {F(cond['psA0'][j],cond['psB0'][j],dim=0):+.2f}"
    print(s)
