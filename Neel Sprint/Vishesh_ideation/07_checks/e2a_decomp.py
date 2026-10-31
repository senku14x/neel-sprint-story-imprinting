# CPU-only (Vishesh_ideation spec 07 check, 30 Oct 2026; reads E2(a) bc trig contexts, X8 HS/HL/H_def = helpful, DS/DL/H_dis = dismissive): residual-level decomposition of organism-minus-parent header shift on E2(a) bc contexts.
import torch, glob, sys, collections
torch.set_num_threads(4)
R="/workspace/runs_executor/extract1028/E2/a"
LAY=[16,24,32,40,48,56,63]
def load(m):
    out={}
    for f in sorted(glob.glob(f"{R}/{m}/chunk_*.pt")):
        z=torch.load(f,mmap=True)
        for i,k in enumerate(z["keys"]):
            if not k.startswith("E2a|bc|"): continue
            p=k.split("|")
            if p[3]!="trig": continue
            if p[2] not in ("HS","HL","DS","DL","H_def","H_dis"): continue
            out[k]=z["span_mean"][i,0][LAY].float().clone()
    return out
P=load("parent"); 
for m in sys.argv[1:]:
    O=load(m)
    keys=sorted(set(P)&set(O))
    cls=lambda k:"H" if k.split("|")[2] in("HS","HL","H_def") else "D"
    d=torch.stack([O[k]-P[k] for k in keys])   # n,L,5120
    c=[cls(k) for k in keys]
    iH=torch.tensor([x=="H" for x in c]); iD=~iH
    print(m,"n",len(keys),"nH",int(iH.sum()),"nD",int(iD.sum()))
    for j,L in enumerate(LAY):
        dl=d[:,j]; mu=dl.mean(0); muH=dl[iH].mean(0); muD=dl[iD].mean(0)
        tot=(dl**2).sum(1).mean()
        const=(mu**2).sum()
        cond=0.5*((muH-mu)**2).sum()+0.5*((muD-mu)**2).sum()
        within=tot-const-cond
        pn=torch.stack([P[k][j] for k in keys]).norm(dim=1).median()
        cosHD=torch.nn.functional.cosine_similarity(muH,muD,dim=0)
        # parent's own D-H difference vs training-added D-H difference
        PH=torch.stack([P[k][j] for k,x in zip(keys,c) if x=="H"]).mean(0); PD=torch.stack([P[k][j] for k,x in zip(keys,c) if x=="D"]).mean(0)
        pdiff=PD-PH; odiff=muD-muH
        print(f" L{L:2d} |h_par|med {pn:7.1f} |d|rms {tot.sqrt():6.1f} share const {const/tot:.3f} cond {cond/tot:.3f} within {within/tot:.3f} cos(muH,muD) {cosHD:.3f} |parD-H| {pdiff.norm():6.1f} |trainD-H| {odiff.norm():6.1f} cos(par,train) {torch.nn.functional.cosine_similarity(pdiff,odiff,dim=0):.3f} cos(parD-H,orgD-H) {torch.nn.functional.cosine_similarity(pdiff,pdiff+odiff,dim=0):.3f} |orgD-H| {(pdiff+odiff).norm():6.1f}")
